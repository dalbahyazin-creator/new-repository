import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('playwright');
const base = process.argv[2];
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const out = {};
for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['phone', { width: 412, height: 915 }]]) {
  for (const opt of ['a', 'b']) {
    const page = await browser.newPage({ viewport: vp, deviceScaleFactor: name === 'phone' ? 2 : 1 });
    const errs = []; page.on('pageerror', (e) => errs.push(e.message)); page.on('console', (m) => m.type() === 'error' && errs.push(m.text()));
    const t0 = Date.now();
    await page.goto(`${base}/${opt}.html`); await page.waitForFunction('window.__ready', null, { timeout: 60000 });
    const load = Date.now() - t0;
    await page.waitForTimeout(2000);
    await page.evaluate('window.__rotate()'); await page.waitForTimeout(4000);
    const rotate = await page.evaluate('window.__fps(4000)');
    await page.evaluate('window.__stop(); window.__flyToCountry()'); await page.waitForTimeout(3500);
    const fly = await page.evaluate('window.__fps(3000)');
    await page.waitForTimeout(1500);
    const swapped = await page.evaluate('!!window.__swapped');
    await page.screenshot({ path: `shots/${opt}-${name}.png` });
    out[`${opt}-${name}`] = { loadMs: load, rotate, fly, swapped50m: swapped, errors: errs.slice(0, 3) };
    await page.close();
  }
}
console.log(JSON.stringify(out, null, 2)); await browser.close();
