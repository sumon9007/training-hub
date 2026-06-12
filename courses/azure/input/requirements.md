# Azure Fundamentals — Training Requirements

## Audience Profile
- Mix of IT admins, developers, project managers, and business analysts
- Most have 0-2 years hands-on cloud experience
- Some have on-premises infrastructure background
- Goal: build a solid Azure foundation and pass the AZ-900 exam

## Module Structure
This course follows the **official AZ-900 exam blueprint** as THREE modules, one per skills-measured
domain. Each lesson within a module gets its own section slide + content slides. Labs are placed in
the module where the skill is first applied.

- **Module 1 — Cloud Concepts** (25–30%): 4 lessons + Lab 1, Lab 2
- **Module 2 — Azure Architecture & Services** (35–40%): 6 lessons (no labs)
- **Module 3 — Azure Management & Governance** (30–35%): 4 lessons + Lab 3, Lab 4

Generate slides in this order:
1. Course title slide
2. For each module: module overview slide → its lessons → its labs (if any) → module summary
3. Final course wrap-up / key takeaways slide

## Slide Types per Lesson
- Lesson header slide: lesson number, title, learning objectives (3-4 bullets)
- 3-5 content slides per lesson (concept cards, two-column comparisons, lists)
- Diagram slides where relevant (see Diagram Requirements below)
- 1 quiz slide per lesson where it adds value (4-option MCQ, AZ-900 exam style)

## Slide Types per Lab
- Lab header slide: "LAB 0X", lab title, objective, estimated time (~10-15 min each) — **amber accent**
- Step-by-step instructions (numbered, **max 6 steps per slide**) — use the `.steps` style
- Portal navigation paths and commands shown in `<code>` style
- Screenshot placeholder callout where applicable
- "What you achieved" summary slide at the end of each lab

## Diagram Requirements
Aim for **2–3 diagrams per module** (raise visual density — do not settle for one). Required diagrams:
- Module 1, Lesson 3: IaaS / PaaS / SaaS layered shared-responsibility model
- Module 1, Lesson 4: Public / Private / Hybrid cloud comparison
- Module 2, Lesson 1: Geography → Region → Availability Zone topology
- Module 2, Lesson 2: Azure management hierarchy (Management Groups → Subscriptions → Resource Groups → Resources)
- Module 2, Lesson 3: Compute decision flow (when to pick VM / App Service / Container / Function)
- Module 3, Lesson 1: Cost factors / cost-optimisation flow
- Module 3, Lesson 4: Monitoring stack (Azure Monitor → Log Analytics / App Insights / Advisor / Service Health)

## Style Requirements
- Professional dark theme — navy/slate
- Use lesson numbers consistently: "LESSON 01", "LESSON 02" etc.
- Use lab numbers: "LAB 01", "LAB 02" etc.
- **Lab slides use an amber/yellow accent** (`.lab-slide` / `.steps`) to distinguish them from lessons
- Step-by-step lab instructions use numbered list format with portal navigation paths in `code` style
- Every slide needs speaker notes with talking points
- Exam tips prefixed with "🎯 Exam tip:"
- Lab tips prefixed with "🔧 Lab tip:"

## Content Density
- Cap bullets at ~6 per column; if a comparison needs more, split it across two consecutive
  `data-auto-animate` slides rather than shrinking the font
- Prefer concept cards (`.cards`) and diagrams over long bullet lists
- One complete, exam-relevant fact per bullet — never a bare heading
