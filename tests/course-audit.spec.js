const { test, expect } = require('@playwright/test');
const fs = require('fs');

const DIR = 'test-results/course-audit';

test.beforeAll(() => {
  if (!fs.existsSync(DIR)) fs.mkdirSync(DIR, { recursive: true });
});

async function shot(page, name) {
  await page.screenshot({ path: `${DIR}/${name}.png`, fullPage: false });
}

async function waitForReveal(page) {
  await page.waitForFunction(() => typeof Reveal !== 'undefined' && Reveal.isReady && Reveal.isReady(), { timeout: 15000 });
  await page.waitForTimeout(800);
}

// --- Landing Page ---
test('landing hero + nav', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(600);
  await shot(page, '01-landing-hero');
  await page.evaluate(() => window.scrollTo(0, 600));
  await shot(page, '02-landing-why-section');
  await page.evaluate(() => window.scrollTo(0, 1200));
  await shot(page, '03-landing-course-cards');
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await shot(page, '04-landing-footer');
});

test('landing labs tab', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);
  const labsTab = page.locator('button', { hasText: 'Labs' }).first();
  if (await labsTab.isVisible()) {
    await labsTab.click();
    await page.waitForTimeout(300);
  }
  await shot(page, '05-landing-labs-tab');
});

test('landing mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(600);
  await shot(page, '06-landing-mobile');
});

// --- AZ-104 Presentation ---
test('az104 title slide', async ({ page }) => {
  page.setDefaultTimeout(20000);
  await page.goto('/courses/az104/presentation.html', { waitUntil: 'domcontentloaded' });
  await waitForReveal(page);
  await shot(page, '07-az104-title-slide');
});

test('az104 module intro + lesson slide', async ({ page }) => {
  page.setDefaultTimeout(20000);
  await page.goto('/courses/az104/presentation.html', { waitUntil: 'domcontentloaded' });
  await waitForReveal(page);
  await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(500);
  await shot(page, '08-az104-module-intro');
  await page.keyboard.press('ArrowDown');
  await page.waitForTimeout(500);
  await shot(page, '09-az104-lesson-slide');
  await page.keyboard.press('ArrowDown');
  await page.waitForTimeout(500);
  await shot(page, '10-az104-lesson-slide-2');
});

test('az104 keyboard shortcut overlay', async ({ page }) => {
  page.setDefaultTimeout(20000);
  await page.goto('/courses/az104/presentation.html', { waitUntil: 'domcontentloaded' });
  await waitForReveal(page);
  await page.keyboard.press('?');
  await page.waitForTimeout(600);
  await shot(page, '11-az104-keyboard-overlay');
});

test('az104 overview mode', async ({ page }) => {
  page.setDefaultTimeout(20000);
  await page.goto('/courses/az104/presentation.html', { waitUntil: 'domcontentloaded' });
  await waitForReveal(page);
  await page.keyboard.press('o');
  await page.waitForTimeout(800);
  await shot(page, '12-az104-overview-mode');
});

test('az104 quiz slide + answer', async ({ page }) => {
  page.setDefaultTimeout(20000);
  await page.goto('/courses/az104/presentation.html', { waitUntil: 'domcontentloaded' });
  await waitForReveal(page);
  const found = await page.evaluate(() => {
    const slides = Reveal.getSlides();
    for (let i = 0; i < slides.length; i++) {
      if (slides[i].querySelector && slides[i].querySelector('.quiz-option')) return i;
    }
    return -1;
  });
  if (found >= 0) {
    await page.evaluate((idx) => Reveal.slide(idx), found);
    await page.waitForTimeout(600);
    await shot(page, '13-az104-quiz-slide');
    await page.locator('.quiz-option').first().click();
    await page.waitForTimeout(400);
    await shot(page, '14-az104-quiz-answered');
  }
});

test('az104 diagram slide', async ({ page }) => {
  page.setDefaultTimeout(20000);
  await page.goto('/courses/az104/presentation.html', { waitUntil: 'domcontentloaded' });
  await waitForReveal(page);
  const found = await page.evaluate(() => {
    const slides = Reveal.getSlides();
    for (let i = 0; i < slides.length; i++) {
      if (slides[i].querySelector && slides[i].querySelector('img')) return i;
    }
    return -1;
  });
  if (found >= 0) {
    await page.evaluate((idx) => Reveal.slide(idx), found);
    await page.waitForTimeout(1000);
    await shot(page, '15-az104-diagram-slide');
  }
});

test('az104 exam sim area', async ({ page }) => {
  page.setDefaultTimeout(20000);
  await page.goto('/courses/az104/presentation.html', { waitUntil: 'domcontentloaded' });
  await waitForReveal(page);
  const total = await page.evaluate(() => Reveal.getTotalSlides());
  const target = Math.max(0, total - 5);
  await page.evaluate((t) => Reveal.slide(t), target);
  await page.waitForTimeout(800);
  await shot(page, '16-az104-near-end');
});

test('az104 mobile', async ({ page }) => {
  page.setDefaultTimeout(20000);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/courses/az104/presentation.html', { waitUntil: 'domcontentloaded' });
  await waitForReveal(page);
  await shot(page, '17-az104-mobile-title');
  await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(500);
  await shot(page, '18-az104-mobile-module');
  await page.keyboard.press('ArrowDown');
  await page.waitForTimeout(500);
  await shot(page, '19-az104-mobile-lesson');
});

// --- Lab Page ---
test('lab page', async ({ page }) => {
  await page.goto('/courses/az104/labs/lab-01.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);
  await shot(page, '20-lab-page-top');
  await page.evaluate(() => window.scrollTo(0, 600));
  await shot(page, '21-lab-page-steps');
  await page.evaluate(() => window.scrollTo(0, 1400));
  await shot(page, '22-lab-page-lower');
});

test('lab page mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/courses/az104/labs/lab-01.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);
  await shot(page, '23-lab-mobile-top');
});

// --- Signup Page ---
test('signup page', async ({ page }) => {
  await page.goto('/signup.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);
  await shot(page, '24-signup-page');
});
