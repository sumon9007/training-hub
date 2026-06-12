---
name: decisions
description: Architecture and technology decisions with rationale — append-only ADR log
metadata:
  type: project
---

# Architecture Decision Records

## ADR-001: Reveal.js as the presentation engine

**Date:** 2026-06-05  
**Status:** Accepted

### Decision
Use Reveal.js (CDN, no build) as the slide presentation engine.

### Rationale
- **No build step** — loaded from CDN; the AI generator writes a single `.html` file per course, no toolchain required.
- **Static output** — output is a portable, inspectable HTML file. Deploys directly to GitHub Pages or Azure Static Web Apps with no server needed.
- **Vertical slide nesting** — native support for the `module → sub-slides` structure used in this project (outer `<section>` per module, inner `<section>` per slide).
- **Mermaid.js compatibility** — diagrams render client-side inside slides with no extra integration.
- **PDF export built-in** — `?print-pdf` URL param + browser print produces handouts; no extra tooling.
- **Speaker notes** — `S` key opens presenter view; AI-generated notes per slide work out of the box.

### Alternatives considered
- **PowerPoint/PPTX generation** — complex binary format templating, hard to inspect or diff.
- **Google Slides API** — requires OAuth, external service dependency, harder to self-host.

## ADR-002: Spec-JSON → deterministic PNG rendering for Azure-icon diagrams

**Date:** 2026-06-10
**Status:** Accepted

### Decision
Architecture diagrams with official Azure icons are produced in two stages: the LLM (haiku) emits a JSON spec (clusters/nodes/edges, `service` constrained to a ~74-key whitelist), and `src/generator/diagram_render.py` renders it deterministically with the Python `diagrams` library under `.venv`. Specs are persisted next to the PNGs (`courses/{name}/assets/diagrams/specs/`) and cached — re-render is free, hand-editing a spec is supported.

### Rationale
- No arbitrary LLM-written code execution; the spec is schema-validatable.
- Cacheable and reproducible — full course regens don't re-burn diagram calls.
- Visual standards (dark-theme colors, cluster styling) live in one audited place.
- Renders via a `.venv/bin/python` subprocess so `generate.py` keeps zero third-party deps and falls back to Mermaid when the venv is absent.
- Module is named `diagram_render.py` (NOT `diagrams.py`) — a `diagrams.py` script shadows the `diagrams` package when run directly.

## ADR-003: Engagement features are data-first, HTML-deterministic

**Date:** 2026-06-10
**Status:** Accepted

### Decision
Exam simulators and rich labs follow the same contract: the LLM generates structured DATA (`EXAM_SCHEMA` questions with per-option rationales, `LAB_SCHEMA` steps with CLI/validate/cleanup), and Python builders emit the interactive HTML. Client-side behavior (exam timer/scoring, quiz reveal, copy buttons) lives once in `base.html`. Exam options use `.exam-option` (no instant feedback) — deliberately distinct from `.quiz-option` (instant reveal).

### Rationale
- The timer/score markup contract can't be broken by model drift.
- Malformed questions (≠4 options, ≠1 correct) are filtered server-side; a module silently drops its simulator rather than shipping a broken one.
- Every feature degrades gracefully via `COURSE_META[*]["features"]`, keeping AZ-900 regens stable.

## ADR-004: Hub page — Courses/Labs tab switcher with provider grouping

**Date:** 2026-06-11
**Status:** Accepted

### Decision
`index.html` is organised into two client-side tabs — **Courses** and **Labs** — each subdivided by cloud provider (Microsoft / AWS / Google). Switching is done with a plain JS `switchTab()` function that toggles a `hidden` class; no routing library is needed.

### Rationale
- Labs warrant a distinct entry point from courses — users come to practice a specific lab without browsing the full course catalogue.
- Provider grouping mirrors how cloud professionals think (not by certification level or topic).
- Static JS toggle keeps the zero-build constraint (no React, no framework).
- Lab rows in the Labs tab are compact (number badge + title + meta) — different from the richer course cards — because labs are consumed sequentially, not browsed for overview.
- Coming-soon labs are included as placeholders so the structure is established before content is generated.

## ADR-005: Lab page — architecture diagram inline, not right sidebar

**Date:** 2026-06-12
**Status:** Accepted

### Decision
Lab pages use a single-column layout. The architecture diagram renders centered in the main content flow — directly after the "Lab Steps" heading and before the step cards — at up to 860px wide / 520px tall. The original two-column grid (`1fr, 360px`) with a sticky right sidebar is removed.

### Rationale
- The 360px sidebar made diagram images too small to read, especially for multi-node Azure architectures.
- Sidebar placement created a visual disconnect between the diagram and the steps it contextualises.
- Single-column flow matches the reading order: orient (diagram) → act (steps) → verify → clean up.
- `max-width: 860px` keeps the image large on wide screens while still being responsive on small viewports.

## ADR-006: Azure Static Web Apps + built-in AAD authentication

**Date:** 2026-06-12
**Status:** Accepted

### Decision
Migrate hosting from Azure Storage static website to **Azure Static Web Apps (Free tier)**. Use SWA's built-in `/.auth/` endpoints (no server code) to enforce Microsoft sign-in before learners can access `/courses/*`. A `login.html` page serves as the unauthenticated entry point. `staticwebapp.config.json` declares route rules.

### Rationale
- SWA Free tier ($0/month) includes managed OAuth2 with AAD — zero server code, zero Function App.
- Route protection is declarative in `staticwebapp.config.json`; `/courses/*` requires `authenticated` role; 401s redirect to `/login.html`.
- AAD issuer `https://login.microsoftonline.com/common/v2.0` accepts both personal Microsoft accounts and work/school accounts — appropriate for a public training platform.
- `/.auth/me` returns `clientPrincipal.userDetails` (email) for the nav chip; no custom token logic needed.
- All pages call `/.auth/me` on load and fail silently when absent (local `http-server`) — zero dev workflow disruption.
- `npm run start:auth` launches the SWA CLI emulator (`localhost:4280`) for full auth testing locally.

### App registration (manual, per tenant)
- Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
- Redirect URI: `https://<swa-hostname>/.auth/login/aad/callback`
- SWA app settings: `AAD_CLIENT_ID`, `AAD_CLIENT_SECRET` (set via `az staticwebapp appsettings set`)

## ADR-007: Blob Storage for course assets — private containers, build-time SAS tokens

**Date:** 2026-06-12
**Status:** Accepted

### Decision
Add an Azure Storage Account (Standard_LRS) alongside the SWA resource in `infra/main.bicep`. Three private containers: `diagrams`, `videos`, `questionbanks`. Diagram PNGs are uploaded by the generator immediately after rendering; a 2-year SAS URL is embedded directly in `<img src>` and cached in the spec JSON (`blob_url` field). Videos and question banks are uploaded manually via `az storage blob upload`.

### Rationale
- **Private containers** — `allowBlobPublicAccess: false`; no asset is accessible without a SAS token. Since courses require login (SWA auth), SAS-URL-bearing HTML never reaches unauthenticated users.
- **Build-time SAS** — the static site has no server API, so tokens can't be minted at runtime. 2-year SAS expiry is acceptable because: (a) HTML is regenerated regularly, (b) token rotation is free (re-run the generator), (c) SWA auth gates the HTML itself.
- **Storage key not in Bicep outputs** — `deploy.sh` fetches the key via `az storage account keys list` post-deploy to avoid the key appearing in ARM deployment history.
- **Graceful degradation** — if `AZURE_MEDIA_STORAGE_ACCOUNT`/`AZURE_MEDIA_STORAGE_KEY` are absent, the generator silently falls back to relative local file paths. Local dev (`npm start`) is unaffected.
- **CORS** on blob service: `*.azurestaticapps.net`, `localhost:4280`, `localhost:8080` — browser can load blob images from SWA pages without preflight errors.
- Blob path convention: `diagrams/{course}/slides/{slug}.png` | `videos/{course}/` | `questionbanks/{course}/questions.json`
