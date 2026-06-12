# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: lab-images.spec.js >> Static: no CLI/PowerShell badge steps remain >> lab-03b — all steps are Portal-only
- Location: tests/lab-images.spec.js:86:5

# Error details

```
Error: lab-03b: found 1 PowerShell badge(s)

expect(received).toBe(expected) // Object.is equality

Expected: 0
Received: 1
```

# Test source

```ts
  1   | // Playwright tests — AZ-104 Lab Module
  2   | // Tests: all 17 lab pages load, architecture images are present,
  3   | // no CLI/PS badge steps remain, navigation links work.
  4   | //
  5   | // Run from project root:
  6   | //   npx playwright test tests/lab-images.spec.js --reporter=list
  7   | 
  8   | const { test, expect } = require('@playwright/test');
  9   | const path = require('path');
  10  | const fs = require('fs');
  11  | 
  12  | const BASE_URL = 'http://localhost:8080';
  13  | 
  14  | const LABS = [
  15  |   { slug: 'lab-01',  title: 'Manage Azure AD Identities' },
  16  |   { slug: 'lab-02a', title: 'Subscriptions' },
  17  |   { slug: 'lab-02b', title: 'Governance' },
  18  |   { slug: 'lab-03a', title: 'Resources via Azure Portal' },
  19  |   { slug: 'lab-03b', title: 'Resources via ARM Templates' },
  20  |   { slug: 'lab-03c', title: 'Resources via PowerShell' },
  21  |   { slug: 'lab-03d', title: 'Resources via Azure CLI' },
  22  |   { slug: 'lab-04',  title: 'Implement Virtual Networking' },
  23  |   { slug: 'lab-05',  title: 'Intersite Connectivity' },
  24  |   { slug: 'lab-06',  title: 'Traffic Management' },
  25  |   { slug: 'lab-07',  title: 'Manage Azure Storage' },
  26  |   { slug: 'lab-08',  title: 'Manage Virtual Machines' },
  27  |   { slug: 'lab-09a', title: 'Implement Web Apps' },
  28  |   { slug: 'lab-09b', title: 'Azure Container Instances' },
  29  |   { slug: 'lab-09c', title: 'Azure Kubernetes Service' },
  30  |   { slug: 'lab-10',  title: 'Implement Data Protection' },
  31  |   { slug: 'lab-11',  title: 'Implement Monitoring' },
  32  | ];
  33  | 
  34  | const DIAGRAM_DIR = path.resolve(
  35  |   __dirname, '../courses/az104/assets/diagrams/labs'
  36  | );
  37  | 
  38  | // ── Static file checks (no server needed) ────────────────────────────────────
  39  | 
  40  | test.describe('Static: diagram PNG files exist on disk', () => {
  41  |   for (const lab of LABS) {
  42  |     test(`${lab.slug} — PNG exists`, () => {
  43  |       const png = path.join(DIAGRAM_DIR, `${lab.slug}.png`);
  44  |       const exists = fs.existsSync(png);
  45  |       if (!exists) {
  46  |         console.warn(`  MISSING: ${png}`);
  47  |       }
  48  |       expect(exists, `PNG missing for ${lab.slug}: ${png}`).toBe(true);
  49  |     });
  50  | 
  51  |     test(`${lab.slug} — PNG is non-empty (> 5 KB)`, () => {
  52  |       const png = path.join(DIAGRAM_DIR, `${lab.slug}.png`);
  53  |       if (!fs.existsSync(png)) {
  54  |         test.skip();
  55  |         return;
  56  |       }
  57  |       const size = fs.statSync(png).size;
  58  |       expect(size, `PNG for ${lab.slug} is suspiciously small (${size} bytes)`).toBeGreaterThan(5120);
  59  |     });
  60  |   }
  61  | });
  62  | 
  63  | test.describe('Static: lab HTML references <img> diagram (not inline SVG)', () => {
  64  |   for (const lab of LABS) {
  65  |     test(`${lab.slug} — uses <img> for diagram`, () => {
  66  |       const htmlPath = path.resolve(
  67  |         __dirname, `../courses/az104/labs/${lab.slug}.html`
  68  |       );
  69  |       if (!fs.existsSync(htmlPath)) {
  70  |         test.skip();
  71  |         return;
  72  |       }
  73  |       const html = fs.readFileSync(htmlPath, 'utf-8');
  74  |       // Must have an img tag pointing to the labs diagram directory
  75  |       const hasImg = /src=["'][^"']*assets\/diagrams\/labs\/[^"']+\.png["']/.test(html);
  76  |       // Must NOT have an inline SVG as the diagram (the large auto-generated one)
  77  |       const hasInlineSvg = /<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg" width="520"/.test(html);
  78  |       expect(hasImg, `${lab.slug}: no <img> pointing to labs/diagrams PNG`).toBe(true);
  79  |       expect(hasInlineSvg, `${lab.slug}: still has inline SVG (should be <img>)`).toBe(false);
  80  |     });
  81  |   }
  82  | });
  83  | 
  84  | test.describe('Static: no CLI/PowerShell badge steps remain', () => {
  85  |   for (const lab of LABS) {
  86  |     test(`${lab.slug} — all steps are Portal-only`, () => {
  87  |       const htmlPath = path.resolve(
  88  |         __dirname, `../courses/az104/labs/${lab.slug}.html`
  89  |       );
  90  |       if (!fs.existsSync(htmlPath)) {
  91  |         test.skip();
  92  |         return;
  93  |       }
  94  |       const html = fs.readFileSync(htmlPath, 'utf-8');
  95  |       // CLI badge: emerald-500 color with text "CLI"
  96  |       const cliCount = (html.match(/bg-emerald-500\/20.*?CLI|CLI.*?bg-emerald-500\/20/gs) || []).length;
  97  |       // PowerShell badge: indigo-500 with "PowerShell"
  98  |       const psCount = (html.match(/bg-indigo-500\/20.*?PowerShell|PowerShell.*?bg-indigo-500\/20/gs) || []).length;
  99  |       expect(cliCount, `${lab.slug}: found ${cliCount} CLI badge(s)`).toBe(0);
> 100 |       expect(psCount, `${lab.slug}: found ${psCount} PowerShell badge(s)`).toBe(0);
      |                                                                            ^ Error: lab-03b: found 1 PowerShell badge(s)
  101 |     });
  102 |   }
  103 | });
  104 | 
  105 | // ── Browser tests (requires running server on port 8080) ─────────────────────
  106 | 
  107 | test.describe('Browser: lab pages load correctly', () => {
  108 |   for (const lab of LABS) {
  109 |     test(`${lab.slug} — page loads and title is correct`, async ({ page }) => {
  110 |       const url = `${BASE_URL}/courses/az104/labs/${lab.slug}.html`;
  111 |       const response = await page.goto(url, { waitUntil: 'domcontentloaded' });
  112 |       expect(response.status(), `HTTP status for ${url}`).toBe(200);
  113 | 
  114 |       // Page must have the lab title somewhere in <h1>
  115 |       const h1 = await page.locator('h1').first().textContent();
  116 |       expect(h1, `h1 content for ${lab.slug}`).toContain(lab.title.split(' ')[0]);
  117 |     });
  118 | 
  119 |     test(`${lab.slug} — architecture diagram image loads (HTTP 200)`, async ({ page }) => {
  120 |       const url = `${BASE_URL}/courses/az104/labs/${lab.slug}.html`;
  121 |       await page.goto(url, { waitUntil: 'networkidle' });
  122 | 
  123 |       // Find the diagram <img> tag
  124 |       const diagramImg = page.locator('img[src*="assets/diagrams/labs"]').first();
  125 |       const count = await diagramImg.count();
  126 |       expect(count, `${lab.slug}: no <img> with diagrams/labs src found`).toBeGreaterThan(0);
  127 | 
  128 |       if (count > 0) {
  129 |         // Verify the image actually loaded (naturalWidth > 0)
  130 |         const naturalWidth = await diagramImg.evaluate(img => img.naturalWidth);
  131 |         expect(naturalWidth, `${lab.slug}: diagram image failed to load (naturalWidth=0)`).toBeGreaterThan(0);
  132 |       }
  133 |     });
  134 | 
  135 |     test(`${lab.slug} — "Architecture Diagram" section is visible`, async ({ page }) => {
  136 |       await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
  137 |       // The section heading "Architecture Diagram" must be visible
  138 |       const heading = page.getByText('Architecture Diagram', { exact: true });
  139 |       await expect(heading).toBeVisible();
  140 |     });
  141 | 
  142 |     test(`${lab.slug} — no step has CLI or PowerShell badge`, async ({ page }) => {
  143 |       await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
  144 |       const cliBadge = page.locator('span:has-text("CLI")');
  145 |       const psBadge = page.locator('span:has-text("PowerShell")');
  146 |       await expect(cliBadge).toHaveCount(0);
  147 |       await expect(psBadge).toHaveCount(0);
  148 |     });
  149 | 
  150 |     test(`${lab.slug} — "Lab Steps" section has at least 3 steps`, async ({ page }) => {
  151 |       await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
  152 |       const steps = page.locator('.step-card');
  153 |       const count = await steps.count();
  154 |       expect(count, `${lab.slug}: only ${count} step cards found`).toBeGreaterThanOrEqual(3);
  155 |     });
  156 | 
  157 |     test(`${lab.slug} — breadcrumb nav links back to hub`, async ({ page }) => {
  158 |       await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
  159 |       const hubLink = page.locator('nav a:has-text("Training Hub")');
  160 |       await expect(hubLink).toBeVisible();
  161 |     });
  162 | 
  163 |     test(`${lab.slug} — Validation Checklist is present`, async ({ page }) => {
  164 |       await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
  165 |       const section = page.getByText('Validation Checklist', { exact: true });
  166 |       await expect(section).toBeVisible();
  167 |     });
  168 | 
  169 |     test(`${lab.slug} — Cleanup Resources section is present`, async ({ page }) => {
  170 |       await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
  171 |       const section = page.getByText('Cleanup Resources', { exact: true });
  172 |       await expect(section).toBeVisible();
  173 |     });
  174 |   }
  175 | });
  176 | 
  177 | test.describe('Browser: hub page Labs tab shows all labs', () => {
  178 |   test('Hub Labs tab lists at least 17 lab rows', async ({ page }) => {
  179 |     await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'domcontentloaded' });
  180 |     // Click the Labs tab
  181 |     await page.click('button:has-text("Labs")');
  182 |     // Count lab rows in the Microsoft section
  183 |     const labRows = page.locator('#view-labs .lab-row, #view-labs [href*="lab-"]');
  184 |     const count = await labRows.count();
  185 |     expect(count, `Hub page only shows ${count} lab links`).toBeGreaterThanOrEqual(17);
  186 |   });
  187 | });
  188 | 
```