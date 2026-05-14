const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const outPath = path.join(process.env.HOME || '', 'Documents', 'nikolajflojgaard.me', 'public', 'images', 'sigenstor-hero.png');

(async() => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
  await page.goto('https://www.sigenergy.com/us/products/sigenstor', { waitUntil: 'networkidle', timeout: 60000 });
  await page.screenshot({ path: outPath, fullPage: false });
  await browser.close();
  console.log('saved');
})();
