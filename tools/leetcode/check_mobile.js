// Usage: NODE_PATH=$(npm root -g) node tools/leetcode/check_mobile.js /leetcode /leetcode/<slug> ...
// Exits non-zero when a page scrolls sideways at 390px, throws a script error, or has an SVG
// text label that extends past its diagram's viewBox (the browser clips it).
const { chromium } = require('playwright');

const BASE = process.env.BASE_URL || 'http://localhost:8000';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  let failed = false;
  for (const path of process.argv.slice(2)) {
    const response = await page.goto(BASE + path);
    const [scroll, inner] = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
    const clipped = await page.evaluate(() => {
      const out = [];
      for (const svg of document.querySelectorAll('svg')) {
        const vb = svg.viewBox.baseVal;
        if (!vb || !vb.width) continue;
        for (const text of svg.querySelectorAll('text')) {
          const b = text.getBBox();
          if (b.x < vb.x - 0.5 || b.y < vb.y - 0.5 || b.x + b.width > vb.x + vb.width + 0.5 || b.y + b.height > vb.y + vb.height + 0.5) {
            out.push(text.textContent.trim());
          }
        }
      }
      return out;
    });
    const ok = response.status() === 200 && scroll <= inner && clipped.length === 0;
    failed ||= !ok;
    console.log(`${ok ? 'ok      ' : 'FAIL    '}${path} status=${response.status()} scrollWidth=${scroll} innerWidth=${inner}${clipped.length ? ' clipped=' + JSON.stringify(clipped) : ''}`);
  }
  if (errors.length) {
    failed = true;
    console.log('script errors:', errors);
  }
  await browser.close();
  process.exit(failed ? 1 : 0);
})();
