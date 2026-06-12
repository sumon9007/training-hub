# AZ-104 Azure Administrator — Training Requirements

## Audience Profile
- IT professionals, sysadmins, DevOps engineers, and cloud engineers
- Most have 1–3 years of hands-on IT experience (on-prem or cloud)
- Many have already passed AZ-900 or have equivalent Azure familiarity
- Goal: hands-on administrator skills and pass the AZ-104 exam
- Expects timed practice and hands-on validation, not passive slides

---

## Module & Slide Structure

This course has **7 modules** (Module 0–6), mapped 1:1 to the official AZ-104T00 learning paths plus an exam-prep module. Generate slides in this order per module:

1. Module overview slide (title, exam weight %, key skills)
2. Per lesson: lesson header slide → content slides → diagram slide → **knowledge check slide**
3. Per lab: lab header → scenario → step slides (with CLI) → expected output → validate → cleanup → "What you achieved"
4. **Module exam simulator block** (timed, scored)
5. Module summary / key takeaways slide

---

## Knowledge Check Directive (every lesson)

- EXACTLY ONE scenario-based MCQ after every lesson — no exceptions
- AZ-104 stem style: 2–3 sentence scenario ending in "What should you do?" / "Which … should you use?"
- 4 options, all plausible — distractors must be same-category services, roles, scopes, or SKUs
- The explanation must state why the correct answer is right AND one line per wrong option explaining why it is wrong (`.quiz-why-wrong` list)
- Use the outline's per-lesson `**Quiz:**` line as the scenario seed, including its distractor hints

---

## Module Exam Simulator Directive

- Question count, time limit, and topic coverage come from each module's `**Exam-Sim:**` line in the outline
- Timed and scored client-side: start button → countdown timer → one question per slide → score summary with per-question review
- Question mix per module: ≥50% scenario questions, ≥1 command/portal-path completion question, ≥1 service-comparison question
- Module 6 hosts the 20-question weight-proportional final (identities 5, storage 3, compute 5, networking 4, monitoring 3)
- Pass mark display: 70%

---

## Lab Slide Directive

Labs come from the outline with labeled blocks (`Objective / Est-Time / Scenario / Steps / CLI / Expected-Output / Validate / Cleanup`). Slide sequence per lab:

| Slide | Content |
|-------|---------|
| **Lab header** | Official lab number + title, objective, estimated time (amber accent) |
| **Scenario** | The business scenario driving the lab |
| **Step slides** | Numbered steps, max ~5 per slide; portal paths in `code style`; CLI commands in copyable code blocks with expected output |
| **Validate** | Verification command + success criteria — how the learner proves it worked |
| **Cleanup** | Teardown commands — never skip; cost-hygiene warning callout |
| **What you achieved** | Checklist mapped to the exam skills the lab exercised |

- Every CLI block must be copy-paste runnable (placeholders in `<angle-brackets>`)
- Show `az` CLI as primary; mention Az PowerShell equivalents where the exam tests both

---

## Diagram Policy (two tiers)

1. **PNG architecture diagrams (official Azure icons)** — pre-rendered by the pipeline into `courses/az104/assets/diagrams/`, referenced by slug from the outline's `**Diagram:** png · <slug> — <description>` lines. Used for multi-service Azure topologies. Do NOT generate Mermaid for these lessons — the image slide is appended automatically.
2. **Mermaid diagrams** — for flows, decision trees, evaluation orders, comparisons, and pie charts, from `**Diagram:** mermaid · <type> — <description>` lines. Follow diagram_rules.md (max 12 nodes, Azure color tokens).

Density: 2–3 diagrams per module minimum, never two diagrams for the same concept.

---

## Style & Design Requirements

### Colors & Theme
- **Base:** Professional dark theme — navy/slate (same as AZ-900)
- **Module accent colors:**
  | Module | Accent | Hex |
  |--------|--------|-----|
  | 0 — Prerequisites & Tools | Steel blue | `#64748B` |
  | 1 — Identities & Governance | Purple | `#8B5CF6` |
  | 2 — Storage | Teal | `#14B8A6` |
  | 3 — Compute | Azure blue | `#0078D4` |
  | 4 — Networking | Emerald | `#10B981` |
  | 5 — Monitoring & Backup | Orange | `#F59E0B` |
  | 6 — Exam Prep | Gold | `#EAB308` |
- **Lab slides:** Amber/yellow accent; **exam simulator slides:** rose accent (built-in)

### Typography & Labels
- Module numbers: `MODULE 00` … `MODULE 06`; lesson numbers restart per module
- Lab numbers: use the official MicrosoftLearning lab IDs from the outline (LAB 00, 02a, 03b, 09c …)
- Exam tips prefix: `🎯 Exam tip:` · Lab tips prefix: `🔧 Lab tip:`
- Comparison advantage: `✅` / disadvantage: `❌`

### Content Standards
- Every slide must have speaker notes with talking points (2–4 sentences minimum)
- Exam tips must reference specific AZ-104 question patterns from the official study guide
- Include service-to-service comparison tables — AZ-104 heavily tests choosing the right service
- Callout boxes for gotchas — e.g. "NSGs don't filter traffic between VMs in the same subnet by default"
- Cap bullets at ~6 per column; split dense comparisons across two auto-animate slides

---

## Exam-Currency Rules (April 17, 2026 skills list)

- Current branding only: **Microsoft Entra ID** (never "Azure AD"), Azure Monitor, Microsoft Defender for Cloud
- **Built-in roles only** for RBAC — custom role authoring is no longer in the skills list (one-line awareness is fine)
- **No longer on the exam** — mention at most as a one-line "beyond the exam" callout, never a full slide: ExpressRoute, Virtual WAN, Front Door, Traffic Manager, Azure Firewall deep-dive, PIM, Entra ID Protection, Conditional Access deep-dive, Entra Connect deep-dive, Azure Blueprints (deprecated)
- **Must be covered** (recent additions/emphases): manage licenses in Entra ID, manage external users, interpret access assignments, identity-based access for Azure Files, storage account encryption, object replication, stored access policies, AzCopy + Storage Explorer, encryption at host, move VM across RG/subscription/region, Azure Container Apps sizing/scaling, App Service certificates/TLS/custom DNS/backup/networking, evaluate effective NSG rules, troubleshoot connectivity and load balancing, alert processing rules, Azure Monitor Insights (VM/storage/network), Connection monitor, **Backup vault vs Recovery Services vault distinction**, backup reports & alerts

---

## Sources & Accuracy

This course outline is grounded in:
- Official AZ-104 study guide — "Skills measured as of April 17, 2026" (https://learn.microsoft.com/credentials/certifications/resources/study-guides/az-104)
- Microsoft Learn AZ-104 learning paths (6 paths): Prerequisites · Manage identities and governance · Implement and manage storage · Deploy and manage compute · Configure and manage virtual networks · Monitor and back up resources
- Official MicrosoftLearning/AZ-104-MicrosoftAzureAdministrator lab repository (lab numbering preserved)

All service names use current Microsoft branding. Exam facts (pass mark 700, ~100 minutes, renewal policy) per the official certification pages.
