# Training Hub — Claude Instructions

AI-powered static training presentation platform: course outline in → Reveal.js presentation out (quizzes, exam simulators, CLI labs, Azure-icon diagrams). No build step, no server — pure static HTML.

## Context

- Project facts (stack, course status, pipeline, infra): @.claude/memory/project_facts.md
- Architecture decisions (ADR log): @.claude/memory/decisions.md

## Key rules

- **LLM calls**: the generator shells out to the `claude` CLI (`--print --output-format json`). Never add the `anthropic` SDK or require an API key.
- **Generated vs. source**: `courses/*/presentation.html` and `courses/*/assets/diagrams/` are AI-generated — regenerate via `./scripts/generate.sh {course}`, don't hand-edit. Hand-edited content belongs in `courses/*/input/` or `src/`.
- **Diagrams**: LLM emits a JSON spec; `src/generator/diagram_render.py` renders PNGs deterministically via `.venv` (`diagrams` + Graphviz). Specs are cached in `assets/diagrams/specs/` — edit a spec and re-render rather than re-extracting. Falls back to Mermaid if `.venv` is missing.
- **Engagement features** (quizzes, exam sims, labs): LLM generates data, Python builders in `generate.py` emit the HTML, client JS lives once in `src/generator/templates/base.html`. Don't let the model generate interactive markup directly (ADR-003).
- **Feature flags**: per-course in `COURSE_META[*]["features"]` in `generate.py`.

## Common commands

```bash
npm start                              # dev server → http://localhost:8080
./scripts/generate.sh {course} [model] # regenerate one course (sonnet default)
./scripts/build_all.sh                 # regenerate all courses with outlines
python3 src/generator/generate.py --course az104 --parse-only      # debug step-1 JSON
./infra/deploy.sh                      # Azure Storage static-website deploy
```

## State

- Courses ready: azure (AZ-900), az104 (AZ-104). Pending outlines: ai, aws, data.
- Git: branch `main`, no remote yet. GitHub Pages workflow exists but needs a remote + push.
- `.env` (gitignored) holds Azure deploy outputs — never commit or echo its values.
