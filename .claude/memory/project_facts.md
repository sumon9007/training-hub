---
name: project-facts
description: Core facts about the training-hub project — stack, structure, course status, and infrastructure
metadata:
  type: project
---

# Training Hub — Project Facts

**Bootstrapped:** 2026-06-05  
**Location:** `/data/workbench/training-hub`  
**Type:** Static web app — AI-powered training presentation platform  
**Version:** 1.0.0 (package.json)  
**Git:** Git repo, branch `main`, remote `origin` → `https://github.com/sumon9007/training-hub` (force-pushed clean initial commit 2026-06-12)  
**Last context sync:** 2026-06-12 (session 5)
**CLAUDE.md:** ✅ exists at project root (committed in initial commit)

## Stack

| Layer | Technology |
|-------|-----------|
| Presentation engine | Reveal.js 5.x (CDN) |
| Diagrams | Mermaid.js 10 (client-side) + Azure-icon PNGs (spec-JSON → `diagrams` lib) |
| AI generation | Claude CLI subprocess (`/home/cloudlens/.local/bin/claude`) |
| Styling | Custom dark theme (`src/theme/training.css`) + Tailwind CDN (hub page) |
| Dev server | `npx http-server . -p 8080` (`npm start`) |
| Auth (SWA) | `/.auth/login/aad`, `/.auth/me`, `/.auth/logout` — built-in SWA AAD provider |
| CI/CD | GitHub Actions → Azure Static Web Apps (`azure/static-web-apps-deploy@v1`) |
| IaC | Azure Bicep (`infra/main.bicep`) — SWA + Storage Account in one template |

## Course Status

| Course | Cert | Input | Generated |
|--------|------|-------|-----------|
| azure  | AZ-900 | ✅ outline.md + requirements.md | ✅ presentation.html |
| az104  | AZ-104 | ✅ official-outline rebuild (2026-06-10) | ✅ presentation.html + assets/diagrams/ |
| ai     | AI-900 | ❌ empty input dir | ❌ |
| aws    | SAA-C03 | ❌ empty input dir | ❌ |
| data   | DP-900 | ❌ empty input dir | ❌ |

## Generation Pipeline

Async pipeline in `src/generator/generate.py` (bounded concurrency, 4 parallel Claude calls):
1. **Parse outline** — Claude haiku extracts structured module JSON (`--parse-only` to inspect)
2. **PNG diagrams (step 2d)** — haiku emits diagram spec JSON → `src/generator/diagram_render.py` renders Azure-icon PNGs via the `.venv` (`diagrams` + Graphviz); cached in `courses/{name}/assets/diagrams/` (specs + PNGs); if `AZURE_MEDIA_STORAGE_ACCOUNT`/`AZURE_MEDIA_STORAGE_KEY` are in env, generator uploads PNG to blob storage and embeds a 2-year SAS URL in `<img src>`; SAS URL cached in the spec JSON (`blob_url` field); `--force-diagrams` to re-extract, `--skip-diagrams` to fall back to Mermaid
3. **Generate slides (step 2)** — Claude sonnet generates Reveal.js `<section>` HTML per lesson, each ending in a scenario knowledge check
4. **Exam sim (step 2b)** + **rich labs (step 2c)** — sonnet generates exam questions / enriched lab JSON; HTML built deterministically (`build_exam_sim`, `build_lab_slides`)
5. **Assemble** — injects slides into `src/generator/templates/base.html` (exam timer/scoring + copy-button JS live there)

Per-course feature flags: `COURSE_META[*]["features"]` — `lesson_quizzes`, `exam_sim`, `rich_labs`, `png_diagrams` (azure/AZ-900 runs quizzes only).

Prompts: `src/generator/prompts/system.md`, `src/generator/prompts/diagram_rules.md`

## Infrastructure (Azure)

Two resources deployed by `infra/main.bicep` in one `az deployment group create` run:

| Resource | Type | Tier | Purpose |
|----------|------|------|---------|
| Azure Static Web Apps | `Microsoft.Web/staticSites` | Standard ($9/month) | Hosts site, enforces auth routes, serves `/.auth/*` |
| Storage Account | `Microsoft.Storage/storageAccounts` | Standard_LRS | Private blob containers for course assets |

**Storage containers** (all `publicAccess: None`):
- `diagrams/` — PNG diagrams uploaded by the generator; organized as `{course}/slides/{slug}.png`
- `videos/` — future course videos; `{course}/{filename}.mp4`
- `questionbanks/` — future raw question JSON; `{course}/questions.json`

**CORS** on blob service allows `https://*.azurestaticapps.net`, `http://localhost:4280`, `http://localhost:8080`.

**`.env` keys** (written by `infra/deploy.sh` + AAD setup step, never committed):
- `AZURE_RESOURCE_GROUP`, `AZURE_SWA_NAME`, `AZURE_SWA_URL`, `AZURE_SWA_DEPLOYMENT_TOKEN`
- `AZURE_MEDIA_STORAGE_ACCOUNT`, `AZURE_MEDIA_STORAGE_KEY`
- `AAD_CLIENT_ID`, `AAD_CLIENT_SECRET`, `AAD_TENANT_ID` (reference only — runtime values live in SWA app settings)

**AAD App Registration** (created via `az ad app create`, one-time per tenant):
- App name: `Training Hub` | Audience: `AzureADandPersonalMicrosoftAccount`
- Redirect URI: `https://<swa-hostname>/.auth/login/aad/callback`
- **Issuer:** `https://login.microsoftonline.com/<tenantId>/v2.0` (tenant-specific — `common/v2.0` causes JWT issuer mismatch in SWA validation)
- **ID token issuance:** must be enabled (`az ad app update --enable-id-token-issuance true`) — SWA uses implicit ID token flow; it is OFF by default
- **Service principal:** must be created (`az ad sp create --id <appId>`) — not auto-created for multi-tenant apps
- **Access group:** `sg-training-hub-learners` (Entra security group) assigned to the app; `appRoleAssignmentRequired=true` — only group members can sign in
- SWA app settings: `AAD_CLIENT_ID`, `AAD_CLIENT_SECRET` (set via `az staticwebapp appsettings set`)

## Hub Page Structure (`index.html`)

The hub landing page uses a **Courses / Labs tab switcher** (client-side JS, no build). Both tabs are structured by cloud provider.

**Auth nav** — header right side: fetches `/.auth/me` on load; shows email + "Sign out" link when authenticated, "Sign in" button when not. Silently no-ops on `npm start` (no `/.auth/me` on `http-server`).

### Courses tab
Three provider sections — each with a header bar (logo + divider) and a card grid:
- **Microsoft** — AZ-900 (live), AZ-104 (live), AI-900 (coming soon), DP-900 (coming soon)
- **AWS** — SAA-C03 (coming soon), CLF-C02 (coming soon)
- **Google** — ACE (coming soon), CDL (coming soon)

### Labs tab
Same three provider groups with individual lab-row cards (number badge, title, description, time, difficulty):
- **Microsoft** — 17 live AZ-104 labs, each linking to a dedicated page at `courses/az104/labs/lab-{slug}.html`
- **AWS** — 6 placeholder labs (coming soon): EC2, S3, IAM, VPC, CloudFormation, RDS
- **Google** — 6 placeholder labs (coming soon): Compute Engine, Cloud Storage, Cloud Run, GKE, VPC, BigQuery

Tab switching: `switchTab('courses'|'labs')` toggles `hidden` on `#view-courses` / `#view-labs`.  
Nav links anchor to `#microsoft`, `#aws`, `#google` within the active courses view.

## Local Dev

- **Dev server URL:** `http://localhost:8080`
- **Azure course URL:** `http://localhost:8080/courses/azure/presentation.html`
- **No Docker** — pure static files, no containers needed
- **Python venv** — `.venv/` at repo root holds `diagrams`, `pillow`, `azure-storage-blob`, `python-dotenv` (`requirements.txt`); the generator itself runs on system Python 3 + Claude CLI and degrades gracefully if the venv or blob credentials are missing
- **Auth dev server** — `npm run start:auth` runs the SWA CLI emulator at `http://localhost:4280` (full auth mock); `npm start` at port 8080 is auth-free for local dev

## Lab Pages (`courses/az104/labs/`)

17 static HTML lab pages generated by `src/generator/build_labs.py` (standalone script, no Claude calls — all lab data is hardcoded). Run with:

```bash
python3 src/generator/build_labs.py
```

**Layout (ADR-005):** Single-column. Order: Prerequisites → Lab Steps heading → Architecture Diagram (centred, `max-height:520px; max-width:860px`, dark `#080e18` background) → Step cards → Validation checklist → Cleanup → Back to labs link. The diagram was moved from a 360px right sidebar into the main content flow so it renders at full readable size.

Diagram assets: `courses/az104/assets/diagrams/labs/{slug}.png` (inline SVG-rendered PNGs from `build_labs.py`'s own `diagram()` helper — no `.venv` needed, uses `svg` strings directly embedded in the HTML template).

**Auth nav** — each lab page nav bar fetches `/.auth/me`; shows user email + "Sign out" (right-aligned in breadcrumb bar) when authenticated, "Sign in" link otherwise.

## Auth Layer

**`login.html`** — dark-themed Microsoft sign-in page at site root. "Sign in with Microsoft" button links to `/.auth/login/aad?post_login_redirect_uri=/`. Auto-redirects to `/` if already authenticated.

**`staticwebapp.config.json`** — SWA route config:
- `/*` — requires `authenticated` role (entire site gated, not just `/courses/*`)
- `/login.html` — only page accessible to `anonymous`
- `401` response → redirects to `/login.html`
- AAD provider with tenant-specific issuer `https://login.microsoftonline.com/<tenantId>/v2.0`
- `AAD_CLIENT_ID` / `AAD_CLIENT_SECRET` stored as SWA application settings (never in code)

**Sign-out** — all sign-out links use `/.auth/logout?post_logout_redirect_uri=/login.html` (index, lab pages, presentation pages) to land on login page after sign-out, not the gated hub.

**User nav pattern** — all pages call `/.auth/me` on load via a small inline `<script>`. Fails silently on `http-server` (no `/.auth/me` endpoint locally). Same pattern in `index.html`, `base.html` (presentation pages), and `build_labs.py` template (lab pages).

## Testing

- **Framework:** Playwright (`playwright.config.js` at project root)
- **Test file:** `tests/lab-images.spec.js` — verifies all 17 lab pages load, architecture images are present, and navigation links work
- **Run:** `npx playwright test tests/lab-images.spec.js --reporter=list` (requires `npm start` running on port 8080)

## Generate Commands

```bash
./scripts/generate.sh azure          # default sonnet model
./scripts/generate.sh azure haiku    # faster
./scripts/generate.sh azure opus     # highest quality
./scripts/build_all.sh               # all courses with outlines
```
