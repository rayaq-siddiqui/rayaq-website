// Usage: NODE_PATH=$(npm root -g) node tools/ml_models/check_mobile.js /ml-models /ml-models/<slug> ...
// Exits non-zero when a page scrolls sideways at 390px or throws a script error.
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
    const ok = response.status() === 200 && scroll <= inner;
    failed ||= !ok;
    console.log(`${ok ? 'ok      ' : 'FAIL    '}${path} status=${response.status()} scrollWidth=${scroll} innerWidth=${inner}`);
  }
  if (errors.length) {
    failed = true;
    console.log('script errors:', errors);
  }
  await browser.close();
  process.exit(failed ? 1 : 0);
})();
