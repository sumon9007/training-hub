// Playwright tests — AZ-104 Lab Module
// Tests: all 17 lab pages load, architecture images are present,
// no CLI/PS badge steps remain, navigation links work.
//
// Run from project root:
//   npx playwright test tests/lab-images.spec.js --reporter=list

const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'http://localhost:8080';

const LABS = [
  { slug: 'lab-01',  title: 'Manage Azure AD Identities' },
  { slug: 'lab-02a', title: 'Subscriptions' },
  { slug: 'lab-02b', title: 'Governance' },
  { slug: 'lab-03a', title: 'Resources via Azure Portal' },
  { slug: 'lab-03b', title: 'Resources via ARM Templates' },
  { slug: 'lab-03c', title: 'Resources via PowerShell' },
  { slug: 'lab-03d', title: 'Resources via Azure CLI' },
  { slug: 'lab-04',  title: 'Implement Virtual Networking' },
  { slug: 'lab-05',  title: 'Intersite Connectivity' },
  { slug: 'lab-06',  title: 'Traffic Management' },
  { slug: 'lab-07',  title: 'Manage Azure Storage' },
  { slug: 'lab-08',  title: 'Manage Virtual Machines' },
  { slug: 'lab-09a', title: 'Implement Web Apps' },
  { slug: 'lab-09b', title: 'Azure Container Instances' },
  { slug: 'lab-09c', title: 'Azure Kubernetes Service' },
  { slug: 'lab-10',  title: 'Implement Data Protection' },
  { slug: 'lab-11',  title: 'Implement Monitoring' },
];

const DIAGRAM_DIR = path.resolve(
  __dirname, '../courses/az104/assets/diagrams/labs'
);

// ── Static file checks (no server needed) ────────────────────────────────────

test.describe('Static: diagram PNG files exist on disk', () => {
  for (const lab of LABS) {
    test(`${lab.slug} — PNG exists`, () => {
      const png = path.join(DIAGRAM_DIR, `${lab.slug}.png`);
      const exists = fs.existsSync(png);
      if (!exists) {
        console.warn(`  MISSING: ${png}`);
      }
      expect(exists, `PNG missing for ${lab.slug}: ${png}`).toBe(true);
    });

    test(`${lab.slug} — PNG is non-empty (> 5 KB)`, () => {
      const png = path.join(DIAGRAM_DIR, `${lab.slug}.png`);
      if (!fs.existsSync(png)) {
        test.skip();
        return;
      }
      const size = fs.statSync(png).size;
      expect(size, `PNG for ${lab.slug} is suspiciously small (${size} bytes)`).toBeGreaterThan(5120);
    });
  }
});

test.describe('Static: lab HTML references <img> diagram (not inline SVG)', () => {
  for (const lab of LABS) {
    test(`${lab.slug} — uses <img> for diagram`, () => {
      const htmlPath = path.resolve(
        __dirname, `../courses/az104/labs/${lab.slug}.html`
      );
      if (!fs.existsSync(htmlPath)) {
        test.skip();
        return;
      }
      const html = fs.readFileSync(htmlPath, 'utf-8');
      // Must have an img tag pointing to the labs diagram directory
      const hasImg = /src=["'][^"']*assets\/diagrams\/labs\/[^"']+\.png["']/.test(html);
      // Must NOT have an inline SVG as the diagram (the large auto-generated one)
      const hasInlineSvg = /<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg" width="520"/.test(html);
      expect(hasImg, `${lab.slug}: no <img> pointing to labs/diagrams PNG`).toBe(true);
      expect(hasInlineSvg, `${lab.slug}: still has inline SVG (should be <img>)`).toBe(false);
    });
  }
});

test.describe('Static: no CLI/PowerShell badge steps remain', () => {
  for (const lab of LABS) {
    test(`${lab.slug} — all steps are Portal-only`, () => {
      const htmlPath = path.resolve(
        __dirname, `../courses/az104/labs/${lab.slug}.html`
      );
      if (!fs.existsSync(htmlPath)) {
        test.skip();
        return;
      }
      const html = fs.readFileSync(htmlPath, 'utf-8');
      // CLI badge: emerald-500 color with text "CLI"
      const cliCount = (html.match(/bg-emerald-500\/20.*?CLI|CLI.*?bg-emerald-500\/20/gs) || []).length;
      // PowerShell badge: indigo-500 with "PowerShell"
      const psCount = (html.match(/bg-indigo-500\/20.*?PowerShell|PowerShell.*?bg-indigo-500\/20/gs) || []).length;
      expect(cliCount, `${lab.slug}: found ${cliCount} CLI badge(s)`).toBe(0);
      expect(psCount, `${lab.slug}: found ${psCount} PowerShell badge(s)`).toBe(0);
    });
  }
});

// ── Browser tests (requires running server on port 8080) ─────────────────────

test.describe('Browser: lab pages load correctly', () => {
  for (const lab of LABS) {
    test(`${lab.slug} — page loads and title is correct`, async ({ page }) => {
      const url = `${BASE_URL}/courses/az104/labs/${lab.slug}.html`;
      const response = await page.goto(url, { waitUntil: 'domcontentloaded' });
      expect(response.status(), `HTTP status for ${url}`).toBe(200);

      // Page must have the lab title somewhere in <h1>
      const h1 = await page.locator('h1').first().textContent();
      expect(h1, `h1 content for ${lab.slug}`).toContain(lab.title.split(' ')[0]);
    });

    test(`${lab.slug} — architecture diagram image loads (HTTP 200)`, async ({ page }) => {
      const url = `${BASE_URL}/courses/az104/labs/${lab.slug}.html`;
      await page.goto(url, { waitUntil: 'networkidle' });

      // Find the diagram <img> tag
      const diagramImg = page.locator('img[src*="assets/diagrams/labs"]').first();
      const count = await diagramImg.count();
      expect(count, `${lab.slug}: no <img> with diagrams/labs src found`).toBeGreaterThan(0);

      if (count > 0) {
        // Verify the image actually loaded (naturalWidth > 0)
        const naturalWidth = await diagramImg.evaluate(img => img.naturalWidth);
        expect(naturalWidth, `${lab.slug}: diagram image failed to load (naturalWidth=0)`).toBeGreaterThan(0);
      }
    });

    test(`${lab.slug} — "Architecture Diagram" section is visible`, async ({ page }) => {
      await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
      // The section heading "Architecture Diagram" must be visible
      const heading = page.getByText('Architecture Diagram', { exact: true });
      await expect(heading).toBeVisible();
    });

    test(`${lab.slug} — no step has CLI or PowerShell badge`, async ({ page }) => {
      await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
      const cliBadge = page.locator('span:has-text("CLI")');
      const psBadge = page.locator('span:has-text("PowerShell")');
      await expect(cliBadge).toHaveCount(0);
      await expect(psBadge).toHaveCount(0);
    });

    test(`${lab.slug} — "Lab Steps" section has at least 3 steps`, async ({ page }) => {
      await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
      const steps = page.locator('.step-card');
      const count = await steps.count();
      expect(count, `${lab.slug}: only ${count} step cards found`).toBeGreaterThanOrEqual(3);
    });

    test(`${lab.slug} — breadcrumb nav links back to hub`, async ({ page }) => {
      await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
      const hubLink = page.locator('nav a:has-text("BD Cloud Academy")');
      await expect(hubLink).toBeVisible();
    });

    test(`${lab.slug} — Validation Checklist is present`, async ({ page }) => {
      await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
      const section = page.getByText('Validation Checklist', { exact: true });
      await expect(section).toBeVisible();
    });

    test(`${lab.slug} — Cleanup Resources section is present`, async ({ page }) => {
      await page.goto(`${BASE_URL}/courses/az104/labs/${lab.slug}.html`, { waitUntil: 'domcontentloaded' });
      const section = page.getByText('Cleanup Resources', { exact: true });
      await expect(section).toBeVisible();
    });
  }
});

test.describe('Browser: hub page Labs tab shows all labs', () => {
  test('Hub Labs tab lists at least 17 lab rows', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`, { waitUntil: 'domcontentloaded' });
    // Click the Labs tab
    await page.click('button:has-text("Labs")');
    // Count lab rows in the Microsoft section
    const labRows = page.locator('#view-labs .lab-row, #view-labs [href*="lab-"]');
    const count = await labRows.count();
    expect(count, `Hub page only shows ${count} lab links`).toBeGreaterThanOrEqual(17);
  });
});
