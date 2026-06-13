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
Migrate hosting from Azure Storage static website to **Azure Static Web Apps (Standard tier, $9/month)**. Use SWA's built-in `/.auth/` endpoints (no server code) to enforce Microsoft sign-in before learners can access the site. A `login.html` page serves as the unauthenticated entry point. `staticwebapp.config.json` declares route rules.

### Rationale
- SWA Standard tier ($9/month) required — the `auth` block in `staticwebapp.config.json` (custom AAD provider config) is not supported on Free tier.
- Route protection is declarative in `staticwebapp.config.json`; `/*` requires `authenticated` role; 401s redirect to `/login.html`.
- `/.auth/me` returns `clientPrincipal.userDetails` (email) for the nav chip; no custom token logic needed.
- All pages call `/.auth/me` on load and fail silently when absent (local `http-server`) — zero dev workflow disruption.
- `npm run start:auth` launches the SWA CLI emulator (`localhost:4280`) for full auth testing locally.

### App registration (created via `az ad app create`, per tenant)
- Supported account types: `AzureADandPersonalMicrosoftAccount`
- Redirect URI: `https://<swa-hostname>/.auth/login/aad/callback`
- SWA app settings: `AAD_CLIENT_ID`, `AAD_CLIENT_SECRET` (set via `az staticwebapp appsettings set`)
- **Issuer must be tenant-specific** — see ADR-008 for the `common/v2.0` failure and fix

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

## ADR-008: AAD auth hardening — tenant issuer, ID token, service principal, access group

**Date:** 2026-06-12
**Status:** Accepted

### Decision
Four fixes applied after the initial AAD wiring failed silently post-password-entry:

1. **Tenant-specific issuer** — `openIdIssuer` changed from `https://login.microsoftonline.com/common/v2.0` to `https://login.microsoftonline.com/<tenantId>/v2.0` in `staticwebapp.config.json`.
2. **ID token issuance enabled** — `az ad app update --enable-id-token-issuance true` (off by default for new registrations; SWA's built-in auth requires it).
3. **Service principal created** — `az ad sp create --id <appId>` (not auto-provisioned for multi-tenant app registrations; required for token issuance in the home tenant).
4. **Entra access group** — security group `sg-training-hub-learners` created; `appRoleAssignmentRequired=true` on the service principal; group assigned to the app. Only members can sign in.

### Rationale
- `common/v2.0` issuer fails SWA's JWT validation because the actual `iss` claim in the token is the tenant-specific URL — they never match. Root cause found via `az rest .../auditLogs/signIns` (error code 700054).
- ID token issuance is disabled by default on new app registrations since 2023 — SWA's implicit-flow auth requires it explicitly enabled.
- Multi-tenant app registrations do not auto-create a service principal in the home tenant — must be created manually.
- `appRoleAssignmentRequired=true` + group assignment controls who can sign in without adding per-user conditional access policies.

### Current group members
- `admin@bdcloudacademy.com` (Cloud Academy)
- `suruz.ahammed@outlook.com` (external/guest user)

### Add new learners
```bash
az ad group member add --group sg-training-hub-learners --member-id <user-object-id>
```

## ADR-009: Public landing page with three-tier route auth

**Date:** 2026-06-12
**Status:** Accepted

### Decision
`index.html` and `signup.html` are accessible without authentication (`anonymous` role). `/courses/*` and the `/*` catch-all require `authenticated`. The landing page, hero, benefits section, and course card grid are visible to unauthenticated visitors; clicking a course card triggers SWA's 401 → `/login.html` redirect.

### Rationale
- Marketing funnel: visitors must see what they're signing up for before creating an account.
- SWA's route table makes this declarative — no server code, no JS guards.
- The auth nav renders two buttons (Sign Up / Sign In) when unauthenticated and an email chip + Sign out when authenticated, driven by `/.auth/me`.

## ADR-010: Self-service registration via Azure Function + Graph API + ACS

**Date:** 2026-06-12
**Status:** Accepted

### Decision
A co-located Azure Function (`api/register/index.js`, HTTP trigger) accepts a form POST from `signup.html`, creates an Entra ID member account via Microsoft Graph API (client credentials flow), adds the user to `sg-training-hub-learners`, and sends a branded HTML welcome email with temporary credentials via Azure Communication Services.

### Rationale
- Eliminates manual admin provisioning for every new learner.
- Graph client credentials flow requires no user interaction — the Function runs headlessly with app-only permissions (`User.ReadWrite.All`, `GroupMember.ReadWrite.All`).
- ACS transactional email is the recommended Azure-native path (no third-party SMTP dependency).
- The Function is co-located with SWA in `api/` — zero additional hosting cost, deployed by the same GitHub Actions workflow.
- No SDK for Graph — uses native Node.js `https` module to keep the function dependency surface minimal; only `@azure/communication-email` is an external dep.

## ADR-011: Design system in `src/brand/`

**Date:** 2026-06-12
**Status:** Accepted

### Decision
All visual tokens (colors, typography, spacing, radius, shadows, gradients, motion) live in `src/brand/tokens.css` as CSS custom properties. Logo variants are SVG files in `src/brand/logo/`. A visual reference page (`src/brand/design-system.html`) documents all components inline — no external Storybook or design tool required.

### Rationale
- CSS custom properties are the lowest-friction token system compatible with the zero-build-step constraint.
- SVG logos are infinitely scalable, editable in any text editor, and load without HTTP overhead on browsers that support `<link rel="icon" type="image/svg+xml">`.
- The self-contained reference page (single HTML file) can be opened from `npm start` without deploying — no documentation hosting needed.

## ADR-012: Site renamed from "Training Hub" to "BD Cloud Academy"

**Date:** 2026-06-12
**Status:** Accepted

### Decision
All user-facing references to "Training Hub" were replaced with "BD Cloud Academy" across 32 files (page titles, nav alt text, footer, email content, lab breadcrumbs, presentation template, logo wordmarks). The git repository slug (`training-hub`) and the Entra security group name (`sg-training-hub-learners`) are deliberately left unchanged to avoid breaking infrastructure references.

### Rationale
- The public brand is "BD Cloud Academy"; "Training Hub" was an internal project codename.
- Keeping the repo slug and group name unchanged avoids needing to update GitHub Actions secrets, SWA resource names, and Bicep templates — purely cosmetic risk with no benefit.
- Custom domain `learn.bdcloudacademy.com` reinforces the brand on the public URL.

## ADR-014: Serve `/src/brand/*` anonymously for public landing page

**Date:** 2026-06-13
**Status:** Accepted

### Decision
Add a route rule in `staticwebapp.config.json` that grants `anonymous` access to `/src/brand/*`. All other unauthenticated paths use the existing catch-all `authenticated` requirement.

### Rationale
- The public landing page (`index.html`) embeds product visuals from `src/brand/showcase/` (e.g. `hub-spoke-topology.png`) in the "Why BD Cloud Academy" zigzag section.
- Without an explicit anonymous rule, SWA's `/*` catch-all blocks image requests for unauthenticated visitors, breaking the marketing funnel before sign-in.
- Scoping the exception to `/src/brand/*` keeps all course content, labs, and API routes fully protected — only CSS tokens, logos, and showcase PNGs are public.

---

## ADR-013: Playwright design assessment suite

**Date:** 2026-06-12  
**Status:** Accepted

### Decision
A dedicated Playwright test file (`tests/design-assessment.spec.js`) runs automated design quality checks on every local build: full-page screenshots at three viewports, brand token presence, WCAG AA contrast on flat-background elements, typography minimums, horizontal overflow, and logo/favicon loading.

### Rationale
- Screenshots at 1440/768/390px give a permanent visual record per commit — reviewers can diff PNGs without spinning up the site.
- WCAG AA contrast checks caught a real failure: desktop nav links at 2.77:1 (slate-600 on white); fixed to 10.35:1 (slate-700).
- Typography minimum (14px body copy) caught lab card descriptions at 12px; bumped to `text-sm`.
- Contrast walker bails out on `background-image` (gradients) rather than producing false negatives — hero section is excluded by design, verified visually via screenshots.
- Token check verifies `tokens.css` is linked and its CSS custom properties resolve on the landing page.
- `webServer` in `playwright.config.js` auto-starts `http-server` — no manual `npm start` needed before running tests.
