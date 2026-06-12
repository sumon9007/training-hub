# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: lab-images.spec.js >> Browser: lab pages load correctly >> lab-03c — no step has CLI or PowerShell badge
- Location: tests/lab-images.spec.js:142:5

# Error details

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  locator('span:has-text("PowerShell")')
Expected: 0
Received: 1
Timeout:  5000ms

Call log:
  - Expect "toHaveCount" with timeout 5000ms
  - waiting for locator('span:has-text("PowerShell")')
    14 × locator resolved to 1 element
       - unexpected value "1"

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - navigation [ref=e2]:
    - generic [ref=e3]:
      - link "Training Hub" [ref=e4] [cursor=pointer]:
        - /url: ../../../index.html#labs
        - img [ref=e5]
        - text: Training Hub
      - generic [ref=e8]: /
      - link "AZ-104 Labs" [ref=e9] [cursor=pointer]:
        - /url: ../../../index.html#labs
      - generic [ref=e10]: /
      - generic [ref=e11]: Lab 03c
  - banner [ref=e12]:
    - generic [ref=e14]:
      - generic [ref=e15]:
        - generic [ref=e16]:
          - generic [ref=e17]: Lab 03c
          - generic [ref=e18]: 🟡 Intermediate
          - generic [ref=e19]: ⏱ 30 min
        - heading "Resources via PowerShell" [level=1] [ref=e20]
        - paragraph [ref=e21]: Manage Azure resources using Azure PowerShell and Cloud Shell
        - paragraph [ref=e22]: Module 3 — Manage Azure Resources
      - generic [ref=e23]:
        - heading "Lab Objectives" [level=2] [ref=e24]
        - list [ref=e25]:
          - listitem [ref=e26]:
            - generic [ref=e27]: ✓
            - text: Open and configure Azure Cloud Shell with PowerShell
          - listitem [ref=e28]:
            - generic [ref=e29]: ✓
            - text: Create and manage resource groups with Az PowerShell module
          - listitem [ref=e30]:
            - generic [ref=e31]: ✓
            - text: Deploy a managed disk using PowerShell
          - listitem [ref=e32]:
            - generic [ref=e33]: ✓
            - text: Create a simple ARM deployment from a PowerShell template
  - main [ref=e34]:
    - generic [ref=e35]:
      - generic [ref=e36]:
        - generic [ref=e37]:
          - heading "Lab Steps" [level=2] [ref=e38]:
            - img [ref=e39]
            - text: Lab Steps
          - generic [ref=e48]:
            - generic [ref=e49]:
              - generic [ref=e51]: "1"
              - generic [ref=e52]:
                - generic [ref=e53]:
                  - heading "Open Cloud Shell (PowerShell)" [level=3] [ref=e54]
                  - generic [ref=e55]: Portal
                - paragraph [ref=e56]:
                  - text: Click the
                  - strong [ref=e57]: Cloud Shell
                  - text: icon (>_) in the portal toolbar. If prompted, select
                  - strong [ref=e58]: PowerShell
                  - text: and complete the storage setup wizard. The shell opens in an integrated terminal at the bottom of the portal.
            - generic [ref=e59]:
              - generic [ref=e61]: "2"
              - generic [ref=e62]:
                - generic [ref=e63]:
                  - heading "Create a resource group" [level=3] [ref=e64]
                  - generic [ref=e65]: Portal
                - paragraph [ref=e66]:
                  - text: Search for
                  - strong [ref=e67]: Resource groups → + Create
                  - text: . Set Subscription to your subscription, Resource group name to
                  - emphasis [ref=e68]: az104-rg1
                  - text: ", Region to"
                  - emphasis [ref=e69]: East US
                  - text: . Click
                  - strong [ref=e70]: Review + create → Create
                  - text: .
            - generic [ref=e71]:
              - generic [ref=e73]: "3"
              - generic [ref=e74]:
                - generic [ref=e75]:
                  - heading "Deploy a managed disk" [level=3] [ref=e76]
                  - generic [ref=e77]: Portal
                - paragraph [ref=e78]:
                  - text: Search for
                  - strong [ref=e79]: Disks → + Create
                  - text: . Set Resource group to
                  - emphasis [ref=e80]: az104-rg1
                  - text: ", Disk name to"
                  - emphasis [ref=e81]: az104-disk1
                  - text: ", Region to"
                  - emphasis [ref=e82]: East US
                  - text: . Under Disk SKU choose
                  - emphasis [ref=e83]: Standard SSD (locally-redundant)
                  - text: ", Size"
                  - emphasis [ref=e84]: 32 GiB
                  - text: . Click
                  - strong [ref=e85]: Review + create → Create
                  - text: .
            - generic [ref=e86]:
              - generic [ref=e88]: "4"
              - generic [ref=e89]:
                - generic [ref=e90]:
                  - heading "Resize the disk" [level=3] [ref=e91]
                  - generic [ref=e92]: Portal
                - paragraph [ref=e93]:
                  - text: Open
                  - emphasis [ref=e94]: az104-disk1
                  - text: in the portal. Click
                  - strong [ref=e95]: Size + performance
                  - text: in the sidebar. Change the disk size to
                  - emphasis [ref=e96]: 64 GiB
                  - text: (disk must be unattached). Click
                  - strong [ref=e97]: Save
                  - text: and confirm the updated size in Overview.
            - generic [ref=e98]:
              - generic [ref=e100]: "5"
              - generic [ref=e101]:
                - generic [ref=e102]:
                  - heading "List resources in the resource group" [level=3] [ref=e103]
                  - generic [ref=e104]: Portal
                - paragraph [ref=e105]:
                  - text: Open
                  - emphasis [ref=e106]: az104-rg1 → Overview
                  - text: . All resources are listed with their Name, Type, and Location. Use the
                  - strong [ref=e107]: Filter by name
                  - text: box to search within the group.
            - generic [ref=e108]:
              - generic [ref=e110]: "6"
              - generic [ref=e111]:
                - generic [ref=e112]:
                  - heading "Clean up resources" [level=3] [ref=e113]
                  - generic [ref=e114]: Portal
                - paragraph [ref=e115]:
                  - text: Open
                  - emphasis [ref=e116]: az104-rg1 → Overview → Delete resource group
                  - text: . Type the resource group name to confirm deletion. Click
                  - strong [ref=e117]: Delete
                  - text: — all resources inside are removed.
        - generic [ref=e118]:
          - heading "Validation Checklist" [level=2] [ref=e119]:
            - img [ref=e120]
            - text: Validation Checklist
          - list [ref=e122]:
            - listitem [ref=e123]:
              - generic [ref=e124]: ✓
              - generic [ref=e125]:
                - text: Cloud Shell opens in PowerShell mode and
                - code [ref=e126]: Get-AzContext
                - text: returns your subscription.
            - listitem [ref=e127]:
              - generic [ref=e128]: ✓
              - generic [ref=e129]:
                - text: Managed disk
                - emphasis [ref=e130]: az104-disk1
                - text: is visible in
                - emphasis [ref=e131]: az104-rg1
                - text: via the portal.
            - listitem [ref=e132]:
              - generic [ref=e133]: ✓
              - generic [ref=e134]: After resize, disk shows 64 GiB in the portal.
        - generic [ref=e135]:
          - heading "Cleanup Resources" [level=2] [ref=e136]:
            - img [ref=e137]
            - text: Cleanup Resources
          - paragraph [ref=e139]: Run after the lab to avoid ongoing charges.
          - generic [ref=e140]:
            - button "Copy" [ref=e141] [cursor=pointer]
            - code [ref=e143]: Remove-AzResourceGroup -Name "az104-rg1" -Force
      - generic [ref=e145]:
        - generic [ref=e146]:
          - heading "Architecture Diagram" [level=2] [ref=e147]:
            - img [ref=e148]
            - text: Architecture Diagram
          - img "Resources via PowerShell Architecture Diagram" [ref=e154]
        - generic [ref=e155]:
          - heading "Prerequisites" [level=2] [ref=e156]:
            - img [ref=e157]
            - text: Prerequisites
          - list [ref=e159]:
            - listitem [ref=e160]:
              - generic [ref=e161]: •
              - text: Azure subscription with
              - strong [ref=e162]: Contributor
              - text: role
            - listitem [ref=e163]:
              - generic [ref=e164]: •
              - text: Storage account for Cloud Shell (created automatically on first use)
        - link "All AZ-104 Labs" [ref=e165] [cursor=pointer]:
          - /url: ../../../index.html#labs
          - img [ref=e166]
          - text: All AZ-104 Labs
  - contentinfo [ref=e168]:
    - generic [ref=e169]:
      - 'link "Lab 03b: Resources via ARM Templates" [ref=e170] [cursor=pointer]':
        - /url: lab-03b.html
        - img [ref=e171]
        - text: "Lab 03b: Resources via ARM Templates"
      - generic [ref=e173]: Lab 03c of 17
      - 'link "Lab 03d: Resources via Azure CLI" [ref=e174] [cursor=pointer]':
        - /url: lab-03d.html
        - text: "Lab 03d: Resources via Azure CLI"
        - img [ref=e175]
```

# Test source

```ts
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
  100 |       expect(psCount, `${lab.slug}: found ${psCount} PowerShell badge(s)`).toBe(0);
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
> 147 |       await expect(psBadge).toHaveCount(0);
      |                             ^ Error: expect(locator).toHaveCount(expected) failed
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