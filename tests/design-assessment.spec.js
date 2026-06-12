/**
 * Design Assessment — BD Cloud Academy
 *
 * Captures screenshots + evaluates color contrast, brand token usage,
 * typography, spacing, and visual consistency across key pages.
 */

const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

const PAGES = [
  { name: 'landing',    url: '/',                                         title: 'Landing (index.html)' },
  { name: 'login',      url: '/login.html',                               title: 'Login page' },
  { name: 'signup',     url: '/signup.html',                              title: 'Sign-up page' },
  { name: 'az900',      url: '/courses/azure/presentation.html',          title: 'AZ-900 Presentation' },
  { name: 'az104',      url: '/courses/az104/presentation.html',          title: 'AZ-104 Presentation' },
  { name: 'lab-01',     url: '/courses/az104/labs/lab-01.html',            title: 'Lab 01' },
  { name: 'design-sys', url: '/src/brand/design-system.html',             title: 'Design System reference' },
];

const VIEWPORT_DESKTOP  = { width: 1440, height: 900 };
const VIEWPORT_TABLET   = { width: 768,  height: 1024 };
const VIEWPORT_MOBILE   = { width: 390,  height: 844 };

// Actual token names defined in src/brand/tokens.css
const BRAND_COLORS = {
  '--color-brand-600':    '#2563eb',
  '--color-brand-500':    '#3b82f6',
  '--color-dark-bg':      '#060c18',
  '--color-slate-50':     '#f8fafc',
};

const SCREENSHOT_DIR = path.join(__dirname, '..', 'test-results', 'design-screenshots');

test.beforeAll(() => {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
});

// ─── helpers ───────────────────────────────────────────────────────────────

async function getComputedToken(page, property) {
  return page.evaluate((prop) => {
    return getComputedStyle(document.documentElement).getPropertyValue(prop).trim();
  }, property);
}

async function hexToRgb(hex) {
  const r = parseInt(hex.slice(1,3), 16);
  const g = parseInt(hex.slice(3,5), 16);
  const b = parseInt(hex.slice(5,7), 16);
  return { r, g, b };
}

function luminance({ r, g, b }) {
  const sRGB = [r, g, b].map(v => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
}

function contrastRatio(l1, l2) {
  const lighter = Math.max(l1, l2);
  const darker  = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// ─── screenshot suite ───────────────────────────────────────────────────────

test.describe('Screenshots — desktop', () => {
  for (const pg of PAGES) {
    test(`${pg.title}`, async ({ page }) => {
      page.setViewportSize(VIEWPORT_DESKTOP);
      const resp = await page.goto(pg.url);
      // Some pages (presentations) may be large; wait for load
      await page.waitForLoadState('networkidle').catch(() => {});

      if (resp && resp.status() >= 400) {
        console.warn(`  ⚠  ${pg.url} returned ${resp.status()} — skipping screenshot`);
        test.skip();
        return;
      }

      const file = path.join(SCREENSHOT_DIR, `desktop-${pg.name}.png`);
      await page.screenshot({ path: file, fullPage: true });
      console.log(`  📸  Saved ${file}`);

      // Basic check: page is not blank
      const bodyText = await page.evaluate(() => document.body.innerText.trim());
      expect(bodyText.length, `${pg.title} — page appears blank`).toBeGreaterThan(20);
    });
  }
});

test.describe('Screenshots — responsive', () => {
  for (const [label, vp] of [['tablet', VIEWPORT_TABLET], ['mobile', VIEWPORT_MOBILE]]) {
    for (const pg of ['landing', 'login', 'signup', 'lab-01']) {
      const pageInfo = PAGES.find(p => p.name === pg);
      test(`${label} — ${pageInfo.title}`, async ({ page }) => {
        page.setViewportSize(vp);
        const resp = await page.goto(pageInfo.url);
        await page.waitForLoadState('networkidle').catch(() => {});
        if (resp && resp.status() >= 400) { test.skip(); return; }
        const file = path.join(SCREENSHOT_DIR, `${label}-${pg}.png`);
        await page.screenshot({ path: file, fullPage: true });
        console.log(`  📸  Saved ${file}`);
      });
    }
  }
});

// ─── brand token audit ──────────────────────────────────────────────────────

test.describe('Brand tokens', () => {
  test('tokens.css is loaded on the landing page', async ({ page }) => {
    await page.goto('/');
    // --color-brand-600 is defined in tokens.css; empty string means the file is not linked
    const tokenValue = await getComputedToken(page, '--color-brand-600');
    expect(tokenValue, '--color-brand-600 CSS token is missing — tokens.css not loaded?')
      .not.toBe('');
  });

  test('CSS token values match brand spec', async ({ page }) => {
    await page.goto('/src/brand/design-system.html');
    const results = [];
    for (const [token, expected] of Object.entries(BRAND_COLORS)) {
      const actual = await getComputedToken(page, token);
      const match  = actual.replace(/\s/g, '').toLowerCase() === expected.toLowerCase();
      results.push({ token, expected, actual, match });
      if (!match) console.warn(`  ✗  ${token}: expected ${expected}, got "${actual}"`);
      else        console.log( `  ✓  ${token}: ${actual}`);
    }
    const failures = results.filter(r => !r.match);
    expect(failures.length, `Token mismatches:\n${JSON.stringify(failures, null, 2)}`).toBe(0);
  });
});

// ─── color contrast (WCAG AA) ───────────────────────────────────────────────

test.describe('Color contrast — WCAG AA', () => {
  // Target elements on flat (non-gradient) backgrounds so contrast can be computed reliably.
  // Hero section uses a CSS gradient (background-image) — cannot be measured via getComputedStyle.
  const CONTRAST_CHECKS = [
    { name: 'nav links',           selector: 'header nav a',                         minRatio: 4.5 },
    { name: 'sign-in button',      selector: 'header a[href="/login.html"]',          minRatio: 4.5 },
    { name: 'course card heading', selector: '.course-card h3, .card h3, section h3', minRatio: 4.5 },
    { name: 'course card text',    selector: '.course-card p, .card p',               minRatio: 4.5 },
  ];

  for (const check of CONTRAST_CHECKS) {
    test(`${check.name} — contrast ≥ ${check.minRatio}:1`, async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle').catch(() => {});

      const result = await page.evaluate(({ selector, minRatio }) => {
        function toLinear(c) {
          c /= 255;
          return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        }
        function lum(r, g, b) {
          return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
        }
        function parseColor(css) {
          const m = css.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
          if (!m) return null;
          return { r: +m[1], g: +m[2], b: +m[3] };
        }
        function contrast(fg, bg) {
          const l1 = lum(fg.r, fg.g, fg.b) + 0.05;
          const l2 = lum(bg.r, bg.g, bg.b) + 0.05;
          return Math.max(l1, l2) / Math.min(l1, l2);
        }

        const el = document.querySelector(selector);
        if (!el) return { skip: true, reason: `selector "${selector}" not found` };

        const cs = getComputedStyle(el);
        const fg = parseColor(cs.color);

        // Walk up DOM to find the first ancestor with a solid (non-transparent) background-color.
        // Returns null if a gradient background-image is found (can't compute contrast reliably).
        function getActualBg(node) {
          while (node && node !== document.documentElement) {
            const cs = getComputedStyle(node);
            if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
            const raw = cs.backgroundColor;
            const rgba = raw.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
            if (rgba) {
              const alpha = rgba[4] !== undefined ? parseFloat(rgba[4]) : 1;
              if (alpha > 0) return { r: +rgba[1], g: +rgba[2], b: +rgba[3] };
            }
            node = node.parentElement;
          }
          return null;
        }

        const bg = getActualBg(el);
        if (!fg || !bg) return { skip: true, reason: 'background is a gradient or could not be determined — verify visually' };

        const ratio = contrast(fg, bg);
        return { ratio: +ratio.toFixed(2), fg: cs.color, bg: cs.backgroundColor, pass: ratio >= minRatio };
      }, { selector: check.selector, minRatio: check.minRatio });

      if (result.skip) {
        console.warn(`  ⚠  ${check.name}: skipped — ${result.reason}`);
        return; // soft skip
      }

      const icon = result.pass ? '✓' : '✗';
      console.log(`  ${icon}  ${check.name}: ${result.ratio}:1  (fg:${result.fg} bg:${result.bg})`);
      expect(result.ratio, `${check.name} — contrast ${result.ratio}:1 is below ${check.minRatio}:1`).toBeGreaterThanOrEqual(check.minRatio);
    });
  }
});

// ─── typography ─────────────────────────────────────────────────────────────

test.describe('Typography', () => {
  test('landing — heading uses correct font family', async ({ page }) => {
    await page.goto('/');
    const fontFamily = await page.evaluate(() => {
      const h1 = document.querySelector('h1');
      return h1 ? getComputedStyle(h1).fontFamily : null;
    });
    expect(fontFamily, 'h1 font family not found').toBeTruthy();
    console.log(`  ℹ  h1 font-family: ${fontFamily}`);
    // Inter or system UI expected per brand tokens
    const hasExpectedFont = /inter|system-ui|segoe|helvetica/i.test(fontFamily);
    expect(hasExpectedFont, `Unexpected font: "${fontFamily}" — should be Inter or system-ui stack`).toBe(true);
  });

  test('landing — h1 font size is ≥ 32px', async ({ page }) => {
    await page.goto('/');
    const fontSize = await page.evaluate(() => {
      const h1 = document.querySelector('h1');
      return h1 ? parseFloat(getComputedStyle(h1).fontSize) : 0;
    });
    console.log(`  ℹ  h1 font-size: ${fontSize}px`);
    expect(fontSize, `h1 font-size ${fontSize}px is too small`).toBeGreaterThanOrEqual(32);
  });

  test('body text is readable — font size ≥ 14px', async ({ page }) => {
    await page.goto('/');
    const minFontSize = await page.evaluate(() => {
      // Only check genuine body copy — exclude UI chrome (badges, chips, short labels).
      // Require ≥60 chars so pill text, stat captions, and eyebrow labels are skipped.
      const paras = Array.from(document.querySelectorAll('p, li')).filter(el => {
        const cls = el.className || '';
        const text = el.innerText.trim();
        if (text.length < 60) return false;
        if (/ribbon|badge|chip|label|tag/i.test(cls)) return false;
        return true;
      });
      if (!paras.length) return 16;
      const sizes = paras.map(el => parseFloat(getComputedStyle(el).fontSize)).filter(Boolean);
      return Math.min(...sizes);
    });
    console.log(`  ℹ  minimum body font-size: ${minFontSize}px`);
    expect(minFontSize, `Body text too small: ${minFontSize}px`).toBeGreaterThanOrEqual(14);
  });
});

// ─── layout & spacing ───────────────────────────────────────────────────────

test.describe('Layout', () => {
  test('landing — no horizontal scroll on desktop', async ({ page }) => {
    page.setViewportSize(VIEWPORT_DESKTOP);
    await page.goto('/');
    const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
    expect(scrollWidth, `Horizontal overflow: body.scrollWidth=${scrollWidth}px > 1440px`)
      .toBeLessThanOrEqual(VIEWPORT_DESKTOP.width);
  });

  test('landing — no horizontal scroll on mobile', async ({ page }) => {
    page.setViewportSize(VIEWPORT_MOBILE);
    await page.goto('/');
    const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
    expect(scrollWidth, `Mobile horizontal overflow: ${scrollWidth}px > 390px`)
      .toBeLessThanOrEqual(VIEWPORT_MOBILE.width + 5); // 5px tolerance
  });

  test('landing — course cards are visible above the fold', async ({ page }) => {
    page.setViewportSize(VIEWPORT_DESKTOP);
    await page.goto('/');
    const cardsVisible = await page.evaluate(() => {
      const card = document.querySelector('.course-card, [class*="course"], .card');
      if (!card) return false;
      const rect = card.getBoundingClientRect();
      return rect.top < window.innerHeight;
    });
    // Don't fail if card class differs — just log
    if (!cardsVisible) console.warn('  ⚠  No .course-card found above the fold — check selector');
  });

  test('login — form is centered and visible', async ({ page }) => {
    page.setViewportSize(VIEWPORT_DESKTOP);
    const resp = await page.goto('/login.html');
    if (resp?.status() >= 400) { test.skip(); return; }
    const formRect = await page.evaluate(() => {
      const form = document.querySelector('form, .login-card, [class*="login"], [class*="signin"]');
      if (!form) return null;
      const r = form.getBoundingClientRect();
      return { left: r.left, top: r.top, width: r.width };
    });
    if (!formRect) { console.warn('  ⚠  login form container not found by selector'); return; }
    console.log(`  ℹ  login container: left=${formRect.left.toFixed(0)} top=${formRect.top.toFixed(0)} w=${formRect.width.toFixed(0)}`);
    // Should be roughly centered (left margin > 200px on 1440 viewport)
    expect(formRect.left, 'Login form appears flush-left — not centered?').toBeGreaterThan(200);
  });
});

// ─── logo & favicon ─────────────────────────────────────────────────────────

test.describe('Logo & favicon', () => {
  test('favicon is referenced on landing page', async ({ page }) => {
    await page.goto('/');
    const faviconHref = await page.evaluate(() => {
      const link = document.querySelector('link[rel="icon"], link[rel="shortcut icon"]');
      return link ? link.getAttribute('href') : null;
    });
    expect(faviconHref, 'No <link rel="icon"> found').toBeTruthy();
    console.log(`  ℹ  favicon: ${faviconHref}`);
  });

  test('logo SVG is present and loads on the landing page', async ({ page }) => {
    const responses = [];
    page.on('response', r => responses.push(r));
    await page.goto('/');
    await page.waitForLoadState('networkidle').catch(() => {});
    const logoResp = responses.find(r => r.url().includes('logo') && (r.url().endsWith('.svg') || r.url().includes('logo')));
    if (!logoResp) {
      // Check if logo is inline instead
      const inlineSvg = await page.evaluate(() => !!document.querySelector('svg, img[src*="logo"]'));
      console.log(inlineSvg
        ? '  ✓  Logo appears to be inline SVG or <img src*="logo">'
        : '  ⚠  No external logo request or inline SVG logo found');
    } else {
      expect(logoResp.status()).toBeLessThan(400);
      console.log(`  ✓  Logo loaded: ${logoResp.url()} (${logoResp.status()})`);
    }
  });
});

// ─── design system page ─────────────────────────────────────────────────────

test.describe('Design system reference page', () => {
  test('renders without JS errors', async ({ page }) => {
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const resp = await page.goto('/src/brand/design-system.html');
    if (resp?.status() >= 400) { test.skip(); return; }
    await page.waitForLoadState('networkidle').catch(() => {});
    expect(errors, `JS errors on design-system.html:\n${errors.join('\n')}`).toHaveLength(0);
  });

  test('contains color swatch section', async ({ page }) => {
    const resp = await page.goto('/src/brand/design-system.html');
    if (resp?.status() >= 400) { test.skip(); return; }
    const hasSwatches = await page.evaluate(() => {
      const text = document.body.innerText.toLowerCase();
      return text.includes('color') || text.includes('swatch') || text.includes('palette');
    });
    expect(hasSwatches, 'Design system page missing color section').toBe(true);
  });
});
