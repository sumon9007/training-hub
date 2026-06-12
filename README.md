# Training Hub

AI-powered modular training presentation platform. Drop a course outline → Claude generates a complete Reveal.js presentation with scenario knowledge checks after every lesson, timed module exam simulators, hands-on CLI labs (copyable commands + validate/cleanup), Azure-icon architecture diagrams, Mermaid flow diagrams, and speaker notes → auto-publishes to GitHub Pages.

## Quick Start

```bash
# Preview the hub locally
npm start          # → http://localhost:8080

# One-time: venv for Azure-icon PNG diagram rendering (optional — falls back to Mermaid)
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# Generate / regenerate a course
./scripts/generate.sh azure          # uses claude sonnet (default)
./scripts/generate.sh azure haiku    # faster, less detailed
./scripts/generate.sh azure opus     # highest quality

# Regenerate all courses that have an outline
./scripts/build_all.sh

# Pipeline debugging
python3 src/generator/generate.py --course az104 --parse-only       # inspect step-1 JSON
python3 src/generator/generate.py --course az104 --skip-diagrams    # no PNG rendering
python3 src/generator/generate.py --course az104 --force-diagrams   # re-extract diagram specs
```

## Adding a New Course

1. Create `courses/{name}/input/outline.md` — course module structure
2. Create `courses/{name}/input/requirements.md` — style, diagram, audience notes
3. Run `./scripts/generate.sh {name}`
4. Add a course card to `index.html`
5. Push to `main` → GitHub Pages deploys automatically

## Project Structure

```
training-hub/
├── index.html                    # Hub landing page
├── courses/
│   └── az104/                    # (same layout for azure, ai, aws, data)
│       ├── input/
│       │   ├── outline.md        ← YOUR INPUT
│       │   └── requirements.md   ← YOUR INPUT
│       ├── assets/diagrams/      ← AI-GENERATED Azure-icon PNGs + cached specs/
│       └── presentation.html     ← AI-GENERATED
├── src/
│   ├── generator/
│   │   ├── generate.py           # Main AI pipeline
│   │   ├── diagram_render.py     # Azure-icon PNG renderer (spec JSON → diagrams lib)
│   │   ├── prompts/
│   │   │   ├── system.md         # Slide generation prompt
│   │   │   └── diagram_rules.md  # Diagram spec extraction rules
│   │   └── templates/base.html   # Reveal.js shell (quiz / exam-sim / copy-button JS)
│   └── theme/training.css        # Dark professional theme
├── scripts/
│   ├── generate.sh
│   └── build_all.sh
├── infra/
│   ├── main.bicep                # Azure Storage static-website IaC
│   └── deploy.sh                 # az group + Bicep deploy + content upload
└── .github/workflows/deploy.yml  # GitHub Pages
```

## Presentation Controls

| Key | Action |
|-----|--------|
| `→` / `Space` | Next slide |
| `↓` | Sub-slide (within module) |
| `S` | Speaker notes |
| `F` | Fullscreen |
| `O` | Slide overview |
| `?` | All shortcuts |

**PDF export:** Add `?print-pdf` to the URL, then Print → Save as PDF.

## Deployment

### GitHub Pages

1. Push this repo to GitHub (no remote is configured yet: `git remote add origin <url>`)
2. Go to Settings → Pages → Source: **GitHub Actions**
3. Push to `main` — `.github/workflows/deploy.yml` deploys to `https://{user}.github.io/training-hub/`

### Azure Storage static website (alternative)

```bash
./infra/deploy.sh [resource-group] [location]   # defaults: training-hub-rg, eastus
```

Creates the resource group, deploys `infra/main.bicep` (Storage Account), enables static-website hosting, and uploads the site. Outputs land in `.env` (`AZURE_RESOURCE_GROUP`, `AZURE_STORAGE_ACCOUNT`, `AZURE_STATIC_WEBSITE_URL`).

## Courses

| Course | Cert Track | Status |
|--------|-----------|--------|
| Azure Fundamentals | AZ-900 | ✅ Ready |
| Azure Administrator Associate | AZ-104 | ✅ Ready — official AZ-104T00 outline, exam sims + CLI labs |
| AWS Solutions Architect | SAA-C03 | 🔲 Add outline.md |
| Data & Analytics | DP-900 | 🔲 Add outline.md |
| AI & Machine Learning | AI-900 | 🔲 Add outline.md |

## Tech Stack

- **Reveal.js 5.x** — presentation engine (CDN, no build)
- **Mermaid.js 10** — flow diagrams rendered client-side
- **diagrams + Graphviz** — Azure-icon architecture PNGs (`.venv`, optional)
- **Claude CLI** — AI generation via subprocess
- **Tailwind CDN** — hub page styling
- **GitHub Pages** — zero-config static hosting
