#!/usr/bin/env python3
"""
Training Hub — AI Presentation Generator
Reads courses/{name}/input/{outline,requirements}.md
Writes courses/{name}/presentation.html

Usage:
  python3 src/generator/generate.py --course azure
  python3 src/generator/generate.py --course azure --model sonnet
  python3 src/generator/generate.py --all
"""

import argparse
import asyncio
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent  # training-hub/
GENERATOR_DIR = Path(__file__).parent
TEMPLATES_DIR = GENERATOR_DIR / "templates"
PROMPTS_DIR = GENERATOR_DIR / "prompts"

_CLAUDE = shutil.which("claude") or "/home/cloudlens/.local/bin/claude"

# Load .env at project root into os.environ (provides AZURE_MEDIA_STORAGE_* for blob upload).
# Uses setdefault so real env vars always win over .env values.
_env_file = ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# Engagement features per course. Absent keys fall back to DEFAULT_FEATURES.
# Every feature degrades gracefully: turning one off (or a generation step failing)
# falls back to the pre-feature behavior, so older courses keep regenerating cleanly.
DEFAULT_FEATURES = {
    "lesson_quizzes": True,   # scenario MCQ after every lesson
    "exam_sim": True,         # timed, scored quiz block per module
    "rich_labs": True,        # CLI commands + expected output + validate/cleanup slides
    "png_diagrams": True,     # Azure-icon PNG diagrams for architecture lessons
}

COURSE_META = {
    "azure": {
        "title": "Azure Fundamentals",
        "badge": "Microsoft Azure · Fundamentals",
        "color": "#0078D4",
        "accent": "#50E6FF",
        "cert": "AZ-900",
        # Fundamentals course stays conservative: per-lesson quizzes only.
        "features": {"lesson_quizzes": True, "exam_sim": False, "rich_labs": False, "png_diagrams": False},
    },
    "aws": {
        "title": "AWS Solutions Architect",
        "badge": "Amazon Web Services · Associate",
        "color": "#FF9900",
        "accent": "#FFD14F",
        "cert": "SAA-C03",
    },
    "data": {
        "title": "Data & Analytics",
        "badge": "Data Engineering · Microsoft Fabric",
        "color": "#14B8A6",
        "accent": "#5EEAD4",
        "cert": "DP-900",
    },
    "az104": {
        "title": "Azure Administrator Associate",
        "badge": "Microsoft Azure · Administrator",
        "color": "#6366F1",
        "accent": "#A5B4FC",
        "cert": "AZ-104",
    },
    "ai": {
        "title": "AI & Machine Learning",
        "badge": "Artificial Intelligence · Azure OpenAI",
        "color": "#A855F7",
        "accent": "#D8B4FE",
        "cert": "AI-900",
    },
}


def course_features(course: str) -> dict:
    """Effective feature flags for a course (META override → defaults)."""
    return {**DEFAULT_FEATURES, **COURSE_META.get(course, {}).get("features", {})}

# ── Claude CLI helpers ─────────────────────────────────────────────────────

CLAUDE_CALL_TIMEOUT = 600   # seconds per attempt — the big step-1 parse legitimately needs 4-6 min
CLAUDE_CALL_RETRIES = 2     # attempts after the first


async def claude_call(system_prompt: str, user_message: str, model: str = "sonnet") -> str:
    """Single Claude CLI call with timeout + retry, returns plain text result."""
    last_err = None
    for attempt in range(1 + CLAUDE_CALL_RETRIES):
        proc = await asyncio.create_subprocess_exec(
            _CLAUDE,
            "--print",
            "--output-format", "json",
            "--no-session-persistence",
            "--model", model,
            "--system-prompt", system_prompt,
            user_message,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=CLAUDE_CALL_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            last_err = f"timed out after {CLAUDE_CALL_TIMEOUT}s"
            print(f"      ⚠ Claude CLI {last_err} (attempt {attempt + 1}/{1 + CLAUDE_CALL_RETRIES})", flush=True)
            continue
        if proc.returncode != 0:
            last_err = f"exit {proc.returncode}: {stderr.decode().strip()[:200]}"
            print(f"      ⚠ Claude CLI error ({last_err}) (attempt {attempt + 1}/{1 + CLAUDE_CALL_RETRIES})", flush=True)
            await asyncio.sleep(5 * (attempt + 1))
            continue
        try:
            envelope = json.loads(stdout.decode())
            return envelope.get("result", "")
        except json.JSONDecodeError:
            return stdout.decode()
    raise RuntimeError(f"Claude CLI failed after {1 + CLAUDE_CALL_RETRIES} attempts: {last_err}")


async def claude_extract(system_prompt: str, user_message: str, schema: dict, model: str = "haiku") -> dict:
    """Extract structured JSON from Claude."""
    augmented = (
        f"{system_prompt}\n\n"
        f"Respond with ONLY valid JSON matching this schema — no markdown fences, no explanation:\n"
        f"{json.dumps(schema)}"
    )
    raw = await claude_call(augmented, user_message, model)
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Model wrapped the JSON in prose — recover the first JSON object
        start = clean.find("{")
        if start == -1:
            raise
        obj, _ = json.JSONDecoder().raw_decode(clean[start:])
        return obj


# ── Generation pipeline ────────────────────────────────────────────────────

# Lesson-based schema: the model is called once per LESSON (a small, focused unit) so it
# never has to produce a whole module in one shot. Module headers, labs, and summaries are
# built deterministically in Python — they always appear, correctly structured.
MODULE_SCHEMA = {
    "type": "object",
    "properties": {
        "course_title": {"type": "string"},
        "course_description": {"type": "string"},
        "duration_hours": {"type": "number"},
        "target_audience": {"type": "string"},
        "modules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "number": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "objectives": {"type": "array", "items": {"type": "string"}},
                    "lessons": {
                        "type": "array",
                        "description": "Lessons within the module — each becomes its own focused slide-gen call",
                        "items": {
                            "type": "object",
                            "properties": {
                                "number": {"type": "integer"},
                                "title": {"type": "string"},
                                "objectives": {"type": "array", "items": {"type": "string"}},
                                "topics": {"type": "array", "items": {"type": "string"}},
                                "diagram": {
                                    "type": "object",
                                    "description": "If this lesson warrants a diagram, its type + description; omit otherwise. An explicit 'Diagram: none' in the outline means omit.",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["architecture", "sequence", "flowchart", "comparison"]},
                                        "description": {"type": "string"},
                                        "engine": {
                                            "type": "string",
                                            "enum": ["mermaid", "azure-icons"],
                                            "description": "azure-icons ONLY for architecture diagrams showing Azure service topology (or when the outline says 'png'); mermaid for flows, sequences, decision trees, comparisons. Default: mermaid.",
                                        },
                                        "asset": {
                                            "type": "string",
                                            "description": "kebab-case slug for the rendered diagram file, e.g. 'hub-spoke-topology' (from the outline's Diagram line when given)",
                                        },
                                    },
                                },
                                "quiz_topic": {
                                    "type": "string",
                                    "description": "REQUIRED for every lesson: the scenario topic for its knowledge check. Use the outline's Quiz line when present, otherwise derive from the lesson's most exam-relevant decision point.",
                                },
                            },
                            "required": ["number", "title", "topics"]
                        }
                    },
                    "labs": {
                        "type": "array",
                        "description": "Hands-on labs belonging to this module (empty if none)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "objective": {"type": "string"},
                                "est_minutes": {"type": "integer"},
                                "steps": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["title", "steps"]
                        }
                    },
                    "exam_sim": {
                        "type": "object",
                        "description": "Module exam-simulator spec from the outline's Exam-Sim line; omit if the outline has none",
                        "properties": {
                            "question_count": {"type": "integer"},
                            "minutes": {"type": "integer"},
                            "coverage": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["question_count"]
                    },
                },
                "required": ["number", "title", "description", "lessons"]
            }
        }
    },
    "required": ["course_title", "modules"]
}


def _strip_fences(text: str) -> str:
    """Remove a single leading ```html / ``` fence and a trailing ``` fence, if present."""
    text = text.strip()
    text = re.sub(r'^```[a-zA-Z]*\n', '', text)
    text = re.sub(r'\n```$', '', text)
    return text.strip()


async def step1_parse_outline(outline: str, requirements: str, course: str) -> dict:
    """Parse raw outline into a structured module → lesson → lab map."""
    meta = COURSE_META.get(course, {})
    print(f"  [Step 1] Parsing course outline with Claude haiku...")
    system = (
        "You are a technical curriculum designer. Parse the provided course outline and requirements "
        "into a structured JSON map. Preserve the module structure exactly as the outline defines it "
        "(do not merge or split modules). For each MODULE extract: title, description, 3-5 learning "
        "objectives, an ordered 'lessons' array, a 'labs' array, and an 'exam_sim' object when the "
        "module has an 'Exam-Sim:' line (question_count, minutes, coverage topics). "
        "For each LESSON extract: number, title, 3-4 objectives, key topics, an optional 'diagram', "
        "and a quiz_topic for EVERY lesson — use the lesson's 'Quiz:' line when present, otherwise "
        "pick the lesson's most exam-relevant decision point. "
        "Diagram rules: when the lesson has a 'Diagram:' line, copy its description; 'png · <slug>' "
        "means engine='azure-icons' with that asset slug, 'mermaid · <type>' means engine='mermaid' "
        "with that type, and 'none' means omit the diagram entirely. Without a Diagram line, add one "
        "only when the requirements call for it or the topic clearly benefits from a visual "
        "(engine='azure-icons' only for Azure service topology/architecture; otherwise 'mermaid'). "
        "For each LAB copy: title, objective, est_minutes, and the ordered list of steps from the "
        "outline (steps only — CLI/Validate/Cleanup blocks are enriched in a later pass). "
        "A module with no labs gets an empty labs array. "
        f"Course context: {meta.get('title', course)} — target cert: {meta.get('cert', 'n/a')}."
    )
    user = (
        f"COURSE OUTLINE:\n{outline}\n\n"
        f"REQUIREMENTS:\n{requirements}\n\n"
        f"Parse this into the module → lesson → lab structure JSON."
    )
    return await claude_extract(system, user, MODULE_SCHEMA, model="haiku")


async def step2_generate_lesson_slides(lesson: dict, module: dict, course: str, model: str,
                                        requirements: str = "", features: dict | None = None) -> str:
    """Generate the vertical sub-slides for ONE lesson (focused, reliable scope)."""
    meta = COURSE_META.get(course, {})
    features = features or course_features(course)
    system_prompt = (PROMPTS_DIR / "system.md").read_text()
    diagram_rules = (PROMPTS_DIR / "diagram_rules.md").read_text()

    m_no = module["number"]
    l_no = lesson.get("number", 1)
    print(f"    [Step 2] Module {m_no} · Lesson {l_no}: {lesson['title']}...")

    diagram = lesson.get("diagram") or {}
    if diagram.get("engine") == "azure-icons":
        # The PNG architecture slide is built and appended deterministically.
        diagram_directive = (
            "  - Do NOT create a diagram slide for this lesson — an architecture image slide "
            "is appended automatically after your slides.\n"
        )
    elif diagram.get("description"):
        diagram_directive = (
            f"  - Include EXACTLY ONE diagram slide: [{diagram.get('type', 'architecture')}] "
            f"{diagram['description']}\n"
        )
    else:
        diagram_directive = "  - No diagram required for this lesson (only add one if it genuinely clarifies a concept).\n"

    if features.get("lesson_quizzes", True):
        quiz_topic = lesson.get("quiz_topic") or lesson["title"]
        quiz_directive = (
            f"  - End with EXACTLY ONE scenario-based knowledge check slide on: {quiz_topic}\n"
            f"    Exam style: a 2-3 sentence scenario stem ('A company needs to…'), 4 plausible options, "
            f"and an explanation block that states why the correct answer is right AND one line per wrong "
            f"option explaining why it is wrong (use the .quiz-why-wrong list).\n"
        )
    else:
        quiz_directive = "  - No quiz slide for this lesson.\n"

    user = (
        f"Generate the slides for ONE LESSON only. Output 3-6 vertical <section> sub-slides:\n"
        f"  lesson header → 2-4 content slides → [diagram slide if specified] → [quiz slide if specified].\n"
        f"Do NOT output a module header, a course title slide, or any other lesson's content.\n\n"
        f"CONTEXT:\n"
        f"  Course: {meta.get('title', course)} ({meta.get('cert', '')})\n"
        f"  Module {m_no}: {module['title']}\n"
        f"  Lesson {l_no}: {lesson['title']}\n"
        f"  Lesson objectives: {chr(10).join('  - ' + o for o in lesson.get('objectives', []))}\n"
        f"  Topics to cover: {chr(10).join('  - ' + t for t in lesson.get('topics', []))}\n\n"
        f"REQUIRED SLIDES:\n"
        f"  - Start with a lesson header slide: <h3>Module {m_no:02d} · {module['title']}</h3>"
        f" then <h2>Lesson {l_no:02d} · {lesson['title']}</h2> and an .objectives list.\n"
        f"{diagram_directive}"
        f"{quiz_directive}\n"
        f"STYLE & DENSITY RULES (follow exactly):\n{requirements}\n\n"
        f"DIAGRAM RULES:\n{diagram_rules}\n\n"
        f"Output ONLY the HTML <section> sub-slides for this lesson — no outer wrapper, no markdown fences."
    )

    try:
        slides = await claude_call(system_prompt, user, model=model)
    except RuntimeError as e:
        # Never let one failed lesson kill the whole course build — emit a
        # deterministic placeholder so the gap is visible and regenerable.
        print(f"      ⚠ Lesson {m_no}.{l_no} generation failed ({e}); emitting placeholder", flush=True)
        objectives = "".join(f"\n    <li>{_esc(o)}</li>" for o in lesson.get("objectives", []))
        return (
            f'<section>\n'
            f'  <h3>Module {m_no:02d} · {_esc(module["title"])}</h3>\n'
            f'  <h2>Lesson {l_no:02d} · {_esc(lesson["title"])}</h2>\n'
            f'  <ul class="objectives">{objectives}\n  </ul>\n'
            f'  <div class="callout warning">⚠ This lesson failed to generate — re-run the generator to fill it in.</div>\n'
            f'  <aside class="notes">Generation placeholder.</aside>\n'
            f'</section>'
        )
    return _strip_fences(slides)


# Azure-icon PNG diagrams: the LLM emits a spec (nodes/clusters/edges constrained
# to a service whitelist); rendering is deterministic via diagram_render.py running
# under the project venv (the only place the `diagrams` package is installed).
DIAGRAM_SPEC_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "direction": {"type": "string", "enum": ["LR", "TB"], "description": "LR strongly preferred (slides are landscape)"},
        "clusters": {
            "type": "array",
            "description": "Grouped nodes (e.g. a VNet, a region, a tier). Max 4 clusters.",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "short alphanumeric id, unique across the whole diagram"},
                                "service": {"type": "string", "description": "MUST be one of the whitelisted service keys"},
                                "label": {"type": "string"},
                            },
                            "required": ["id", "service", "label"],
                        },
                    },
                },
                "required": ["label", "nodes"],
            },
        },
        "nodes": {
            "type": "array",
            "description": "Ungrouped nodes (users, internet, on-premises)",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "service": {"type": "string"},
                    "label": {"type": "string"},
                },
                "required": ["id", "service", "label"],
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "label": {"type": "string", "description": "short, e.g. 'peering', '443'; omit when obvious"},
                },
                "required": ["from", "to"],
            },
        },
    },
    "required": ["title", "edges"],
}

_VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
_DIAGRAM_RENDERER = GENERATOR_DIR / "diagram_render.py"


def _diagram_python() -> str | None:
    """Interpreter that has the `diagrams` package, or None if unavailable."""
    if _VENV_PYTHON.exists():
        return str(_VENV_PYTHON)
    return None


def _upload_diagram_blob(storage_account: str, storage_key: str,
                          course: str, slug: str, png_path: Path) -> str | None:
    """Upload rendered PNG to the private 'diagrams' container; return 2-year SAS URL.
    Returns None (and prints a warning) if azure-storage-blob is not installed or upload fails.
    Blob path: diagrams/{course}/slides/{slug}.png
    """
    try:
        from azure.storage.blob import (  # type: ignore
            BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings,
        )
        from datetime import datetime, timezone, timedelta

        blob_name = f"{course}/slides/{slug}.png"
        conn = (
            f"DefaultEndpointsProtocol=https;AccountName={storage_account};"
            f"AccountKey={storage_key};EndpointSuffix=core.windows.net"
        )
        client = BlobServiceClient.from_connection_string(conn)
        bc = client.get_blob_client(container="diagrams", blob=blob_name)
        with open(png_path, "rb") as fh:
            bc.upload_blob(fh, overwrite=True,
                           content_settings=ContentSettings(content_type="image/png"))
        expiry = datetime.now(timezone.utc) + timedelta(days=730)
        token = generate_blob_sas(
            account_name=storage_account,
            container_name="diagrams",
            blob_name=blob_name,
            account_key=storage_key,
            permission=BlobSasPermissions(read=True),
            expiry=expiry,
        )
        return (
            f"https://{storage_account}.blob.core.windows.net/diagrams/{blob_name}?{token}"
        )
    except Exception as exc:
        print(f"      ⚠ Blob upload skipped ({exc}) — using local path")
        return None


async def _render_diagram(spec_path: Path, png_path: Path) -> bool:
    python = _diagram_python()
    if not python:
        print("      ⚠ No .venv with the `diagrams` package — run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt")
        return False
    proc = await asyncio.create_subprocess_exec(
        python, str(_DIAGRAM_RENDERER), "--spec", str(spec_path), "--out", str(png_path),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        print(f"      ⚠ Diagram render failed: {stderr.decode().strip()[:200]}")
        return False
    return png_path.exists() and png_path.stat().st_size > 0


async def _diagram_service_keys() -> list[str]:
    """Whitelist keys from diagram_render.py, via the venv interpreter."""
    python = _diagram_python()
    if not python:
        return []
    proc = await asyncio.create_subprocess_exec(
        python, "-c",
        f"import sys; sys.path.insert(0, {str(GENERATOR_DIR)!r}); "
        "from diagram_render import service_keys; print(','.join(service_keys()))",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    keys = stdout.decode().strip()
    return keys.split(",") if keys else []


async def step2d_diagram_png(lesson: dict, module: dict, course: str,
                             service_keys: list[str], force: bool = False) -> str | None:
    """Generate (or reuse cached) Azure-icon PNG for a lesson. Returns the path
    relative to the course directory, or None on failure (caller falls back to Mermaid)."""
    diagram = lesson.get("diagram") or {}
    m_no, l_no = module["number"], lesson.get("number", 1)
    slug = re.sub(r"[^a-z0-9-]", "", (diagram.get("asset") or f"m{m_no}-l{l_no}").lower()) or f"m{m_no}-l{l_no}"

    assets_dir = ROOT / "courses" / course / "assets" / "diagrams"
    spec_path = assets_dir / "specs" / f"{slug}.json"
    png_path = assets_dir / f"{slug}.png"
    rel_path = f"assets/diagrams/{slug}.png"

    if spec_path.exists() and png_path.exists() and not force:
        spec_cached = json.loads(spec_path.read_text())
        if cached_url := spec_cached.get("blob_url"):
            print(f"    [Step 2d] Diagram '{slug}' cached (blob) — skipping")
            return cached_url
        print(f"    [Step 2d] Diagram '{slug}' cached — skipping")
        return rel_path

    if spec_path.exists() and not force:
        # Spec was hand-edited or render failed previously — just re-render
        spec = json.loads(spec_path.read_text())
    else:
        print(f"    [Step 2d] Diagram spec for '{slug}'...")
        meta = COURSE_META.get(course, {})
        system = (
            "You design Azure architecture diagrams as JSON specs. "
            "Use ONLY these whitelisted service keys for the 'service' field: "
            f"{', '.join(service_keys)}. "
            "Max 12 nodes total, max 4 clusters, direction LR. Node ids must be short, "
            "alphanumeric, and unique across clusters and top-level nodes. Edge labels are "
            "short (1-3 words). Model the architecture the description asks for — no more."
        )
        user = (
            f"Course: {meta.get('title', course)} — Module {m_no}: {module['title']} — Lesson: {lesson['title']}\n"
            f"Diagram to design: {diagram.get('description', lesson['title'])}"
        )
        try:
            spec = await claude_extract(system, user, DIAGRAM_SPEC_SCHEMA, model="haiku")
        except Exception as e:
            print(f"      ⚠ Diagram spec extraction failed ({e})")
            return None
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        spec_path.write_text(json.dumps(spec, indent=2))

    if await _render_diagram(spec_path, png_path):
        sa = os.environ.get("AZURE_MEDIA_STORAGE_ACCOUNT")
        sk = os.environ.get("AZURE_MEDIA_STORAGE_KEY")
        if sa and sk:
            loop = asyncio.get_event_loop()
            blob_url = await loop.run_in_executor(
                None, _upload_diagram_blob, sa, sk, course, slug, png_path
            )
            if blob_url:
                spec["blob_url"] = blob_url
                spec_path.write_text(json.dumps(spec, indent=2))
                print(f"      ✓ {slug}.png → blob")
                return blob_url
        print(f"      ✓ {rel_path}")
        return rel_path
    return None


# Rich-lab enrichment: turns outline steps into structured steps with canonical
# CLI commands, expected output, validation, and cleanup.
LAB_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "objective": {"type": "string"},
        "scenario": {"type": "string", "description": "1-2 sentence business scenario driving the lab"},
        "est_minutes": {"type": "integer"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "What to do — portal paths in plain text like Policy → Definitions"},
                    "command": {"type": "string", "description": "Copy-paste runnable az CLI or PowerShell command, if this step has one; omit otherwise"},
                    "shell": {"type": "string", "enum": ["azurecli", "powershell"]},
                    "expected_output": {"type": "string", "description": "Trimmed sample output worth showing (1-3 lines); omit otherwise"},
                },
                "required": ["text"],
            },
        },
        "validation": {
            "type": "array",
            "description": "How the learner proves the lab worked — command + success criterion",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "command": {"type": "string"},
                    "expected_output": {"type": "string"},
                },
                "required": ["text"],
            },
        },
        "cleanup": {
            "type": "array",
            "description": "Teardown steps so the learner avoids charges",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "command": {"type": "string"},
                },
                "required": ["text"],
            },
        },
    },
    "required": ["title", "objective", "steps"],
}


async def step2c_enrich_lab(lab: dict, module: dict, course: str, model: str = "sonnet") -> dict:
    """Enrich one lab's outline steps into structured steps with CLI/validate/cleanup.

    Falls back to the original lab dict on any failure so legacy rendering still works.
    """
    meta = COURSE_META.get(course, {})
    print(f"    [Step 2c] Enriching lab: {lab.get('title', '?')}...")
    system = (
        "You are an expert Azure trainer writing a hands-on lab. Convert the outline lab into "
        "structured lab JSON. Keep the outline's steps and any CLI/Expected-Output/Validate/Cleanup "
        "content it already has — refine, don't reinvent. Every command must be copy-paste runnable "
        "current Azure CLI (or Az PowerShell where noted), with placeholders in <angle-brackets>. "
        "Portal steps keep their navigation path in the text (e.g. 'Policy → Definitions'). "
        "Include expected_output only when it teaches something (1-3 trimmed lines). "
        "validation MUST contain at least one entry with a command and its success criterion. "
        "cleanup MUST contain the teardown so the learner avoids charges. "
        f"Course: {meta.get('title', course)} ({meta.get('cert', '')}) — Module {module.get('number')}: {module.get('title')}."
    )
    user = (
        f"LAB FROM OUTLINE:\n{json.dumps(lab, indent=2)}\n\n"
        f"Produce the enriched lab JSON."
    )
    try:
        enriched = await claude_extract(system, user, LAB_SCHEMA, model=model)
        if enriched.get("steps"):
            enriched.setdefault("est_minutes", lab.get("est_minutes"))
            return enriched
    except Exception as e:
        print(f"      ⚠ Lab enrichment failed ({e}); using outline steps as-is")
    return lab


# Exam-simulator content: questions are generated as data, never as HTML — the
# timer/score markup is built deterministically by build_exam_sim().
EXAM_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "stem": {"type": "string", "description": "Scenario-based question text, 2-3 sentences, real AZ exam style"},
                    "domain": {"type": "string", "description": "Exam domain/topic this question maps to"},
                    "options": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "A, B, C, or D"},
                                "text": {"type": "string"},
                                "correct": {"type": "boolean"},
                                "rationale": {"type": "string", "description": "Why this option is right or wrong, one sentence"},
                            },
                            "required": ["key", "text", "correct", "rationale"],
                        },
                    },
                    "exam_tip": {"type": "string", "description": "One-line pattern note for this question type"},
                },
                "required": ["stem", "options"],
            },
        }
    },
    "required": ["questions"],
}


async def step2b_generate_exam_questions(module: dict, course: str, model: str = "sonnet") -> list[dict]:
    """Generate the module's exam-simulator questions as structured data."""
    meta = COURSE_META.get(course, {})
    sim = module.get("exam_sim") or {}
    count = sim.get("question_count", 5)
    coverage = sim.get("coverage") or [module.get("title", "")]
    print(f"    [Step 2b] Exam simulator: {count} questions for Module {module.get('number')}...")
    system = (
        "You are a certification exam author. Write timed practice-exam questions in real "
        f"{meta.get('cert', 'Azure')} exam style: scenario stems ('A company needs to…'), "
        "exactly 4 plausible options (A-D) with EXACTLY ONE correct, and a one-sentence rationale "
        "for EVERY option (why right / why wrong). Mix: at least half scenario questions, at least "
        "one command/portal-path completion question, at least one service-comparison question. "
        "All facts must reflect current Azure (Microsoft Entra ID branding)."
    )
    lessons = "\n".join(f"- {l.get('title')}: {', '.join(l.get('topics', [])[:4])}" for l in module.get("lessons", []))
    user = (
        f"Write exactly {count} questions for Module {module.get('number')}: {module.get('title')}.\n"
        f"Topic coverage plan: {'; '.join(coverage)}\n"
        f"Module lessons:\n{lessons}\n"
    )
    try:
        data = await claude_extract(system, user, EXAM_SCHEMA, model=model)
        questions = data.get("questions", [])
        # Keep only well-formed questions: 4 options, exactly one correct
        good = [q for q in questions
                if len(q.get("options", [])) == 4
                and sum(1 for o in q["options"] if o.get("correct")) == 1]
        if good:
            return good[:count]
        print("      ⚠ Exam questions malformed; skipping simulator for this module")
    except Exception as e:
        print(f"      ⚠ Exam question generation failed ({e}); skipping simulator for this module")
    return []


# ── Deterministic slide builders (no model — guaranteed structure) ──────────

def _esc(text: str) -> str:
    """Minimal HTML escaping for text injected into templates."""
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_module_header(module: dict) -> str:
    """Module header slide — always present, always correctly structured."""
    n = module["number"]
    objectives = "".join(f"\n    <li>{_esc(o)}</li>" for o in module.get("objectives", []))
    return (
        f'<section class="module-slide" data-background-color="#080E1C">\n'
        f'  <div class="module-number">Module {n:02d}</div>\n'
        f'  <h1>{_esc(module["title"])}</h1>\n'
        f'  <p>{_esc(module.get("description", ""))}</p>\n'
        f'  <ul class="objectives">{objectives}\n  </ul>\n'
        f'  <aside class="notes">Introduce Module {n:02d}: {_esc(module["title"])}. '
        f'Set expectations for the lessons ahead and why this domain matters for the exam.</aside>\n'
        f'</section>'
    )


def _lab_step_html(step) -> tuple[str, int]:
    """Render one lab step (legacy string or enriched dict) → (li HTML, slide weight)."""
    if isinstance(step, str):
        return f"\n    <li>{_esc(step)}</li>", 1
    text = _esc(step.get("text", ""))
    weight = 1
    parts = [f"\n    <li>{text}"]
    command = step.get("command")
    if command:
        lang = "powershell" if step.get("shell") == "powershell" else "bash"
        parts.append(f'\n      <pre><code class="language-{lang}">{_esc(command)}</code></pre>')
        weight += 1
    expected = step.get("expected_output")
    if expected:
        parts.append(f'\n      <div class="expected-output fragment"><code>{_esc(expected)}</code></div>')
        weight += 1
    parts.append("</li>")
    return "".join(parts), weight


def build_lab_slides(lab: dict, lab_no: int, weight_budget: int = 5) -> str:
    """Lab header → [scenario] → chunked step slides → [validate] → [cleanup] → 'What you achieved'.

    Accepts legacy labs (steps = list of strings) and enriched labs (steps = list of
    dicts with command/expected_output, plus validation[] and cleanup[]). Chunking is
    weight-based so command-heavy slides don't overflow.
    """
    title = _esc(lab.get("title", "Hands-on Lab"))
    objective = _esc(lab.get("objective", ""))
    scenario = _esc(lab.get("scenario", ""))
    minutes = lab.get("est_minutes") or 12
    steps = lab.get("steps", [])

    header_lines = [f'    <li>🎯 Objective: {objective}</li>']
    if scenario:
        header_lines.append(f'    <li>📋 Scenario: {scenario}</li>')
    header_lines.append(f'    <li>⏱ Estimated time: ~{minutes} minutes</li>')
    sections = [
        f'<section class="lab-slide" data-background-color="#1A1206">\n'
        f'  <div class="lab-number">LAB {lab_no:02d}</div>\n'
        f'  <h1>{title}</h1>\n'
        f'  <ul class="objectives">\n' + "\n".join(header_lines) + '\n  </ul>\n'
        f'  <aside class="notes">Lab {lab_no:02d}: {title}. Walk through this live if possible; '
        f'pause for everyone to catch up before moving on.</aside>\n'
        f'</section>'
    ]

    # Chunk steps by weight, continuing the numbering via counter-reset offset
    chunks: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    used = 0
    for i, step in enumerate(steps):
        html, weight = _lab_step_html(step)
        if current and used + weight > weight_budget:
            chunks.append(current)
            current, used = [], 0
        current.append((i, html))
        used += weight
    if current:
        chunks.append(current)

    for group in chunks:
        start, end = group[0][0], group[-1][0] + 1
        items = "".join(html for _, html in group)
        sections.append(
            f'<section class="lab-slide" data-background-color="#1A1206" data-auto-animate>\n'
            f'  <div class="lab-number">LAB {lab_no:02d} · Steps {start + 1}–{end}</div>\n'
            f'  <h2>Step-by-step</h2>\n'
            f'  <ol class="steps" style="counter-reset: step {start}">{items}\n  </ol>\n'
            f'  <aside class="notes">Demonstrate steps {start + 1} to {end}. '
            f'🔧 Lab tip: keep the Azure portal open alongside the slides.</aside>\n'
            f'</section>'
        )

    validation = lab.get("validation") or []
    if validation:
        items = []
        for v in validation:
            li = [f"\n    <li><div>{_esc(v.get('text', ''))}</div>"]
            if v.get("command"):
                li.append(f'\n      <pre><code class="language-bash">{_esc(v["command"])}</code></pre>')
            if v.get("expected_output"):
                li.append(f'\n      <div class="expected-output"><code>{_esc(v["expected_output"])}</code></div>')
            li.append("</li>")
            items.append("".join(li))
        sections.append(
            f'<section class="lab-slide" data-background-color="#1A1206">\n'
            f'  <div class="lab-number">LAB {lab_no:02d} · Validate</div>\n'
            f'  <h2>Prove It Worked</h2>\n'
            f'  <ul class="validate">{"".join(items)}\n  </ul>\n'
            f'  <aside class="notes">Have everyone run the validation before moving on — '
            f'this mirrors how the exam tests expected command output.</aside>\n'
            f'</section>'
        )

    cleanup = lab.get("cleanup") or []
    if cleanup:
        items = []
        for c in cleanup:
            li = [f"\n    <li>{_esc(c.get('text', ''))}"]
            if c.get("command"):
                li.append(f'\n      <pre><code class="language-bash">{_esc(c["command"])}</code></pre>')
            li.append("</li>")
            items.append("".join(li))
        sections.append(
            f'<section class="lab-slide" data-background-color="#1A1206">\n'
            f'  <div class="lab-number">LAB {lab_no:02d} · Cleanup</div>\n'
            f'  <h2>Tear It Down</h2>\n'
            f'  <ol class="steps">{"".join(items)}\n  </ol>\n'
            f'  <div class="callout warning">🔧 Lab tip: always clean up lab resources — '
            f'idle public IPs, gateways, and VMs keep billing until deleted.</div>\n'
            f'  <aside class="notes">Walk through the teardown together so nobody leaves billable resources running.</aside>\n'
            f'</section>'
        )

    sections.append(
        f'<section class="lab-slide" data-background-color="#1A1206">\n'
        f'  <div class="lab-number">LAB {lab_no:02d} · Done</div>\n'
        f'  <h2>What You Achieved</h2>\n'
        f'  <ul class="objectives">\n'
        f'    <li>{objective}</li>\n'
        f'  </ul>\n'
        f'  <aside class="notes">Confirm everyone completed Lab {lab_no:02d} before continuing.</aside>\n'
        f'</section>'
    )
    return "\n".join(sections)


def build_exam_sim(module: dict, questions: list[dict]) -> str:
    """Timed exam-simulator block: intro → one slide per question → results.

    Interactive behavior (timer, selection, scoring, review) lives in base.html;
    this builder only emits the data-carrying markup contract.
    """
    if not questions:
        return ""
    n = module["number"]
    exam_id = f"m{n}"
    sim = module.get("exam_sim") or {}
    total = len(questions)
    minutes = sim.get("minutes") or max(2, round(total * 1.5))
    pass_pct = 70

    sections = [
        f'<section class="exam-slide exam-intro" data-exam-id="{exam_id}" data-background-color="#160A10">\n'
        f'  <div class="exam-number">Module {n:02d} · Exam Simulator</div>\n'
        f'  <h1>Timed Knowledge Test</h1>\n'
        f'  <ul class="objectives">\n'
        f'    <li>{total} exam-style questions covering this module</li>\n'
        f'    <li>⏱ Time limit: {minutes} minutes — the timer starts when you click Start</li>\n'
        f'    <li>🎯 Target score: {pass_pct}% — review follows automatically</li>\n'
        f'    <li>Navigate with ↓ / ↑ — change answers any time before the results slide</li>\n'
        f'  </ul>\n'
        f'  <button class="exam-start" data-exam-id="{exam_id}" data-minutes="{minutes}">Start timed quiz ▸</button>\n'
        f'  <aside class="notes">Module {n:02d} exam simulator: {total} questions in {minutes} minutes. '
        f'Encourage attendees to treat it like the real exam — no notes.</aside>\n'
        f'</section>'
    ]

    for i, q in enumerate(questions):
        options = []
        for o in q.get("options", []):
            options.append(
                f'    <div class="exam-option" data-correct="{str(bool(o.get("correct"))).lower()}" '
                f'data-rationale="{_esc(o.get("rationale", ""))}">'
                f'<span class="option-key">{_esc(o.get("key", "?"))}</span> {_esc(o.get("text", ""))}</div>'
            )
        domain = f' — {_esc(q["domain"])}' if q.get("domain") else ""
        sections.append(
            f'<section class="exam-slide exam-question" data-exam-id="{exam_id}" data-q="{i}" data-background-color="#160A10">\n'
            f'  <div class="exam-number">Question {i + 1} of {total}{domain}</div>\n'
            f'  <p class="exam-stem">{_esc(q.get("stem", ""))}</p>\n'
            + "\n".join(options) + "\n"
            f'  <aside class="notes">{_esc(q.get("exam_tip", ""))}</aside>\n'
            f'</section>'
        )

    sections.append(
        f'<section class="exam-slide exam-results" data-exam-id="{exam_id}" data-total="{total}" '
        f'data-pass="{pass_pct}" data-background-color="#160A10">\n'
        f'  <div class="exam-number">Module {n:02d} · Results</div>\n'
        f'  <h2>Your Score</h2>\n'
        f'  <div class="exam-score"></div>\n'
        f'  <div class="exam-review"></div>\n'
        f'  <button class="exam-retake" data-exam-id="{exam_id}">↺ Retake</button>\n'
        f'  <aside class="notes">Review every missed question with the rationale shown. '
        f'Suggest re-reading the matching lesson for any domain below {pass_pct}%.</aside>\n'
        f'</section>'
    )
    return "\n".join(sections)


def build_diagram_slide(lesson: dict, module: dict, png_rel_path: str, caption: str = "") -> str:
    """Architecture image slide for a pre-rendered Azure-icon PNG diagram."""
    m_no = module["number"]
    desc = (lesson.get("diagram") or {}).get("description", "")
    title = _esc(re.split(r"[:—–]", desc)[0].strip() or lesson["title"])
    return (
        f'<section>\n'
        f'  <h3>Module {m_no:02d} · {_esc(module["title"])}</h3>\n'
        f'  <h2>{title}</h2>\n'
        f'  <div class="diagram-container arch-diagram">\n'
        f'    <img src="{png_rel_path}" alt="{title}">\n'
        f'  </div>\n'
        f'  {f"<p class=\"diagram-caption\">{_esc(caption)}</p>" if caption else ""}\n'
        f'  <aside class="notes">Walk through this architecture left to right — name each Azure service '
        f'and its role before moving on. This visual maps directly to exam scenario questions.</aside>\n'
        f'</section>'
    )


def build_module_summary(module: dict) -> str:
    """Module wrap-up / key takeaways slide from the module objectives."""
    n = module["number"]
    takeaways = "".join(f"\n    <li>{_esc(o)}</li>" for o in module.get("objectives", []))
    return (
        f'<section data-background-color="#080E1C">\n'
        f'  <h3>Module {n:02d} · Wrap-up</h3>\n'
        f'  <h2>Key Takeaways</h2>\n'
        f'  <ul class="objectives">{takeaways}\n  </ul>\n'
        f'  <aside class="notes">Recap Module {n:02d}. Pause for questions before moving on.</aside>\n'
        f'</section>'
    )


async def step3_assemble(course_data: dict, module_slides: list[str], course: str) -> str:
    """Inject slides into base.html template."""
    meta = COURSE_META.get(course, COURSE_META.get("azure", {}))
    base = (TEMPLATES_DIR / "base.html").read_text()

    # Build title slide
    title_slide = f"""
    <section class="title-slide" data-background-gradient="radial-gradient(ellipse at top, #0F1E3A 0%, #0B1120 100%)">
      <div style="margin-top: 12%">
        <div class="course-badge">{meta.get('badge', course.upper())}</div>
        <h1>{course_data.get('course_title', meta['title'])}</h1>
        <p class="subtitle">{course_data.get('course_description', '')}</p>
        <p class="subtitle" style="margin-top:0.3em;font-size:0.8em;color:#475569">
          {len(module_slides)} modules · ~{course_data.get('duration_hours', len(module_slides) * 0.5):.0f} hours · {meta.get('cert', '')}
        </p>
        <div style="margin-top:2em;display:flex;gap:2em;font-size:0.45em;color:#475569">
          <span>📋 Structured curriculum</span>
          <span>📊 Interactive diagrams</span>
          <span>✅ Knowledge checks</span>
          <span>🗒️ Speaker notes</span>
        </div>
      </div>
      <aside class="notes">Welcome everyone. This presentation covers {course_data.get('course_title', meta['title'])}. We have {len(module_slides)} modules to get through. Encourage questions throughout.</aside>
    </section>"""

    all_slides = title_slide + "\n\n" + "\n\n".join(module_slides)

    # Patch theme CSS path and title
    html = base.replace("{{COURSE_TITLE}}", course_data.get("course_title", meta["title"]))
    html = html.replace("{{SLIDES_CONTENT}}", all_slides)

    # Patch accent color in theme for this course
    html = html.replace(
        "</style>",
        f"  :root {{ --course-color: {meta.get('color', '#0078D4')}; --course-accent: {meta.get('accent', '#50E6FF')}; }}\n  </style>"
    )

    return html


async def generate_course(course: str, model: str = "sonnet",
                          parse_only: bool = False,
                          skip_diagrams: bool = False,
                          force_diagrams: bool = False):
    """Full pipeline for one course."""
    course_dir = ROOT / "courses" / course
    input_dir = course_dir / "input"
    out_path = course_dir / "presentation.html"

    outline_path = input_dir / "outline.md"
    requirements_path = input_dir / "requirements.md"

    if not outline_path.exists():
        print(f"  ✗ Missing: {outline_path}")
        print(f"    Create courses/{course}/input/outline.md to generate this course.")
        return False

    outline = outline_path.read_text()
    requirements = requirements_path.read_text() if requirements_path.exists() else ""

    print(f"\n{'='*60}")
    print(f"  Generating: {course.upper()} course presentation")
    print(f"  Model: {model}")
    print(f"{'='*60}")

    # Step 1: Parse outline (disk-cached on the input digest — restarts are free)
    import hashlib
    digest = hashlib.sha256((outline + "\n###\n" + requirements).encode()).hexdigest()[:16]
    parse_cache = course_dir / ".parse-cache.json"
    course_data = None
    if parse_cache.exists():
        try:
            cached = json.loads(parse_cache.read_text())
            if cached.get("digest") == digest:
                print("  [Step 1] Outline unchanged — using cached parse")
                course_data = cached["data"]
        except (json.JSONDecodeError, KeyError):
            pass
    if course_data is None:
        course_data = await step1_parse_outline(outline, requirements, course)
        parse_cache.write_text(json.dumps({"digest": digest, "data": course_data}, indent=2))
    modules = course_data.get("modules", [])
    total_lessons = sum(len(m.get("lessons", [])) for m in modules)
    total_labs = sum(len(m.get("labs", [])) for m in modules)
    print(f"  → Found {len(modules)} modules · {total_lessons} lessons · {total_labs} labs")

    if parse_only:
        print(json.dumps(course_data, indent=2))
        return True

    features = course_features(course)

    # Step 2d (pre-pass): resolve Azure-icon PNG diagrams. Failures and disabled
    # feature both downgrade the lesson to Mermaid so the deck always builds.
    png_lessons = [
        (module, lesson)
        for module in modules
        for lesson in module.get("lessons", [])
        if (lesson.get("diagram") or {}).get("engine") == "azure-icons"
    ]
    if png_lessons:
        png_enabled = features.get("png_diagrams", True) and not skip_diagrams and _diagram_python()
        keys = await _diagram_service_keys() if png_enabled else []
        for module, lesson in png_lessons:
            rel = None
            if png_enabled and keys:
                rel = await step2d_diagram_png(lesson, module, course, keys, force=force_diagrams)
            if rel:
                lesson["_png_path"] = rel
            else:
                lesson["diagram"]["engine"] = "mermaid"

    # Step 2: Build each module = deterministic header + per-lesson model calls + deterministic labs + summary.
    # Each module is one outer <section> wrapping vertical sub-slides (matches the Reveal.js structure).
    # LLM calls are independent `claude` subprocesses, so they run with bounded concurrency.
    sem = asyncio.Semaphore(4)

    async def bounded(coro):
        async with sem:
            return await coro

    lab_counter = 0
    for module in modules:
        for lab in module.get("labs", []):
            lab_counter += 1
            lab["_no"] = lab_counter

    async def build_module(module: dict) -> str:
        lessons = module.get("lessons", [])
        labs = module.get("labs", [])
        lesson_task = asyncio.gather(*[
            bounded(step2_generate_lesson_slides(lesson, module, course, model, requirements, features))
            for lesson in lessons
        ])
        if features.get("rich_labs", True) and labs:
            lab_task = asyncio.gather(*[bounded(step2c_enrich_lab(lab, module, course)) for lab in labs])
        else:
            lab_task = asyncio.gather(*[])
        if features.get("exam_sim", True) and module.get("exam_sim"):
            exam_task = bounded(step2b_generate_exam_questions(module, course))
        else:
            exam_task = None

        lesson_htmls, enriched_labs = await asyncio.gather(lesson_task, lab_task)
        questions = await exam_task if exam_task else []

        parts = [build_module_header(module)]
        for lesson, lesson_html in zip(lessons, lesson_htmls):
            if lesson.get("_png_path"):
                # Insert the architecture image slide before the lesson's knowledge check
                # (the quiz is the last <section> the model emits).
                diagram_slide = build_diagram_slide(lesson, module, lesson["_png_path"],
                                                    caption=(lesson.get("diagram") or {}).get("description", ""))
                idx = lesson_html.rfind("<section")
                if features.get("lesson_quizzes", True) and idx > 0:
                    lesson_html = lesson_html[:idx] + diagram_slide + "\n" + lesson_html[idx:]
                else:
                    lesson_html = lesson_html + "\n" + diagram_slide
            parts.append(lesson_html)
        for original, lab in zip(labs, enriched_labs if enriched_labs else labs):
            parts.append(build_lab_slides(lab, original["_no"]))
        exam_html = build_exam_sim(module, questions)
        if exam_html:
            parts.append(exam_html)
        parts.append(build_module_summary(module))
        return "<section>\n" + "\n".join(parts) + "\n</section>"

    module_slides = list(await asyncio.gather(*[build_module(m) for m in modules]))

    # Step 3: Assemble
    print(f"  [Step 3] Assembling presentation...")
    html = await step3_assemble(course_data, module_slides, course)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html)
    print(f"  ✓ Written: courses/{course}/presentation.html")
    print(f"    {len(html):,} chars · {len(modules)} modules · {sum(s.count('<section') for s in module_slides)} slides")
    return True


async def main():
    parser = argparse.ArgumentParser(description="Training Hub — AI Presentation Generator")
    parser.add_argument("--course", choices=list(COURSE_META.keys()), help="Course to generate")
    parser.add_argument("--all", action="store_true", help="Generate all courses")
    parser.add_argument("--model", default="sonnet", choices=["haiku", "sonnet", "opus"], help="Claude model for slide generation")
    parser.add_argument("--parse-only", action="store_true", help="Run only step 1 (outline parse) and print the JSON")
    parser.add_argument("--skip-diagrams", action="store_true", help="Skip Azure-icon PNG diagram generation (fall back to Mermaid)")
    parser.add_argument("--force-diagrams", action="store_true", help="Regenerate PNG diagram specs even when cached")
    args = parser.parse_args()

    if not args.course and not args.all:
        parser.print_help()
        sys.exit(1)

    if not Path(_CLAUDE).exists() and not shutil.which("claude"):
        print(f"✗ Claude CLI not found at {_CLAUDE}. Install Claude Code first.")
        sys.exit(1)

    courses = list(COURSE_META.keys()) if args.all else [args.course]
    results = []
    for course in courses:
        ok = await generate_course(
            course, args.model,
            parse_only=args.parse_only,
            skip_diagrams=args.skip_diagrams,
            force_diagrams=args.force_diagrams,
        )
        results.append((course, ok))

    print(f"\n{'='*60}")
    for course, ok in results:
        status = "✓" if ok else "✗"
        print(f"  {status} {course}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
