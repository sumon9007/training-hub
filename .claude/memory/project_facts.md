---
name: project-facts
description: Core facts about the training-hub project — stack, structure, course status, and infrastructure
metadata:
  type: project
---

# BD Cloud Academy — Project Facts

**Bootstrapped:** 2026-06-05  
**Location:** `/data/workbench/training-hub`  
**Type:** Static web app — AI-powered cloud certification training platform  
**Version:** 1.0.0 (package.json)  
**Git:** Git repo, branch `main`, remote `origin` → `https://github.com/sumon9007/training-hub`
**Last context sync:** 2026-06-14 (session 10)
**CLAUDE.md:** ✅ exists at project root

**Brand name:** BD Cloud Academy (renamed from "Training Hub" — all 32 user-facing files updated 2026-06-12)  
**Public URL:** `https://learn.bdcloudacademy.com` (custom domain on SWA, Cloudflare DNS-only / grey cloud)

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
- `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET` — app reg with Graph `User.ReadWrite.All` + `GroupMember.ReadWrite.All` (admin-consented) for self-service registration
- `LEARNERS_GROUP_ID` — object ID of `sg-training-hub-learners` security group
- `ACS_CONNECTION_STRING`, `ACS_SENDER_ADDRESS` — Azure Communication Services for welcome email
- `SITE_URL` — public site URL embedded in credential emails (no trailing slash)
- `TENANT_DOMAIN=bdcloudacademy.com` — UPN suffix for new member accounts

**AAD App Registration** (created via `az ad app create`, one-time per tenant):
- App name: `BD Cloud Academy` | Audience: `AzureADandPersonalMicrosoftAccount`
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

**`staticwebapp.config.json`** — SWA route config (three-tier):
- `/`, `/index.html`, `/signup.html` — `anonymous` + `authenticated` (public landing + registration)
- `/src/brand/*` — `anonymous` (brand assets + showcase images must load on public landing page before auth)
- `/courses/*` — requires `authenticated` role
- `/*` — requires `authenticated` role (catch-all)
- `401` response → redirects to `/login.html`
- AAD provider with tenant-specific issuer `https://login.microsoftonline.com/<tenantId>/v2.0`
- `AAD_CLIENT_ID` / `AAD_CLIENT_SECRET` stored as SWA application settings (never in code)

**Sign-out** — all sign-out links use `/.auth/logout?post_logout_redirect_uri=/login.html` (index, lab pages, presentation pages) to land on login page after sign-out, not the gated hub.

**User nav pattern** — all pages call `/.auth/me` on load via a small inline `<script>`. Fails silently on `http-server` (no `/.auth/me` endpoint locally). Same pattern in `index.html`, `base.html` (presentation pages), and `build_labs.py` template (lab pages).

## Testing

- **Framework:** Playwright (`playwright.config.js` at project root) — Chromium only, `webServer` auto-starts `http-server` on port 8080
- **Test files:**
  - `tests/lab-images.spec.js` — verifies all 17 lab pages load, architecture images present, navigation works
  - `tests/design-assessment.spec.js` — design quality suite (ADR-013): full-page screenshots (desktop/tablet/mobile), brand token presence, WCAG AA contrast checks, typography rules, layout overflow, logo/favicon, design-system page
- **Run all:** `npx playwright test --reporter=list`
- **Screenshots:** saved to `test-results/design-screenshots/` (gitignored)
- **Known failing test:** `lab-03c — no step has CLI or PowerShell badge` — the "no CLI/PS badge" check at `tests/lab-images.spec.js:142` incorrectly runs on all 17 labs including the PowerShell-specific lab-03c. Fix: skip the check for labs whose titles contain "PowerShell" or "CLI".

### Accessibility fixes applied (session 7 — 2026-06-12)

| Element | Before | After | Reason |
|---------|--------|-------|--------|
| Desktop nav `<a>` | `text-slate-600` (2.77:1) | `text-slate-700` (10.35:1) | WCAG AA fail |
| Lab card descriptions | `text-xs` (12px) | `text-sm` (14px) | Below minimum readable size |
| `.ribbon` badge | `0.6rem` (9.6px) | `0.7rem` (11.2px) | Too small for decorative text |
| `index.html` `<head>` | no `tokens.css` link | `<link href="/src/brand/tokens.css">` added | Design tokens unavailable on landing page |

## Self-Service Registration (`signup.html` + `api/register/`)

New in session 5 (2026-06-12). Allows visitors to create their own Entra ID member account.

**Flow:** `signup.html` → POST `/api/register` → Graph API creates user → adds to `sg-training-hub-learners` → ACS sends branded welcome email with temp credentials.

**Azure Function:** `api/register/index.js` (Node.js, HTTP trigger, `authLevel: anonymous`)
- Gets Graph token via client credentials flow (`GRAPH_CLIENT_ID` / `GRAPH_CLIENT_SECRET`)
- Creates member user with `forceChangePasswordNextSignIn: true`; UPN: `firstname.lastname@bdcloudacademy.com` (checks up to 5 variants for uniqueness)
- Adds user to `sg-training-hub-learners` group
- Sends HTML welcome email via `@azure/communication-email` SDK
- Returns `{ success: true, message: "..." }` on success

**Required SWA app settings** (beyond auth ones): `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`, `LEARNERS_GROUP_ID`, `ACS_CONNECTION_STRING`, `ACS_SENDER_ADDRESS`, `TENANT_DOMAIN`, `SITE_URL`

## Design System (`src/brand/`)

Added session 6 (2026-06-12). Single source of truth for visual language.

| File | Purpose |
|------|---------|
| `src/brand/tokens.css` | CSS custom properties — colors, type scale, spacing, radius, shadows, gradients, z-index, motion |
| `src/brand/logo/logo.svg` | Horizontal lockup: geometric mark + "BD Cloud Academy" wordmark (560×120) |
| `src/brand/logo/logo-white.svg` | All-white variant for dark/hero backgrounds |
| `src/brand/logo/logo-icon.svg` | Icon mark only — graduation cap over cloud mark on blue→navy gradient (200×200); redesigned 2026-06-13 |
| `src/brand/logo/favicon.svg` | Simplified bold mark for browser tab (32×32) |
| `src/brand/design-system.html` | Interactive visual reference — colors, typography, spacing, buttons, cards, forms, alerts, motion |
| `src/brand/showcase/` | Public product visuals used by the landing page (e.g. `hub-spoke-topology.png`); served anonymously via SWA route rule so they load before login |

All HTML pages reference `/src/brand/logo/favicon.svg` as the `<link rel="icon">`.

## Hub Page — Landing Page Design

Full-dark product-first theme. Public-facing sections (no auth required):
- **Hero** — full-dark gradient, outcome-first headline, dual CTAs (Sign Up indigo / Sign In violet), provider pill row. Stats strip (2 certs / 17 labs / 7 modules / AI diagrams) is inlined at the bottom of the hero via a flex divider row — the separate stats bar section was removed (2026-06-14).
- **"Why BD Cloud Academy"** — compact 3-column feature card grid (redesigned 2026-06-14 from the earlier zigzag two-column showcase rows). Cards: Labs (CLI snippet inline), Exam Simulator, AI Diagrams. Each card has an icon, title, description, micro-demo, and CTA link.
- **Course cards** — gradient icon backgrounds, "Most Popular" ribbon on AZ-104, "Start course →" CTAs

Header shows **Sign Up** (ghost) + **Sign In** (indigo/violet CTA) when unauthenticated; collapses to email + Sign out when authenticated. Footer copyright: BD Cloud Academy.

## Presentation UI — Round 1 Polish (session 10, 2026-06-14)

Custom UI layer added to `base.html` + `training.css` replacing Reveal.js built-in controls:

| Element | ID / Class | Description |
|---------|-----------|-------------|
| Slide-type badge | `#slide-type-badge` | Top-left pill — LESSON / MODULE / EXAM / LAB / KNOWLEDGE CHECK / DIAGRAM |
| Module HUD | `#module-hud` | Top-center — module number · name · slide N/M + mini progress bar |
| Global progress | `#global-progress` | Top-right chip — overall % through the whole deck |
| Bottom nav bar | `#bottom-nav` | Fixed 44px bar — prev/next arrows + one pill per module (`bnav-module` pills); active pill highlighted |

Reveal.js `slideNumber`, `progress`, and `controls` are all disabled (`false`) — the custom layer replaces them.  
`"Back to hub"` link repositioned to `bottom: 54px` to sit above the bottom nav bar.

**AZ-104 title slide** redesigned (2026-06-14) to a two-column hero: left has eyebrow breadcrumb, AZ-104 code tag, gradient headline, meta chips (7 modules / ~18h / 65+ Qs / 5 lab suites), and "Press Space to begin" prompt; right panel holds a rotating cert badge and topic pills. Background: `#060D1A` with CSS grid lines + glow effect.

## Generate Commands

```bash
./scripts/generate.sh azure          # default sonnet model
./scripts/generate.sh azure haiku    # faster
./scripts/generate.sh azure opus     # highest quality
./scripts/build_all.sh               # all courses with outlines
```
