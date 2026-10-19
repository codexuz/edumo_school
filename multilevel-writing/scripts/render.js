// Print the book's interior to PDF.
// Each sheet is a fixed 210x297mm box, so content that does not fit would be
// clipped — every .cols box is measured and reported before printing.
// Usage: node scripts/render.js   -> dist/Multilevel_Writing_Guide.pdf
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const dist = path.resolve(__dirname, '..', 'dist');
const out = path.join(dist, 'interior.pdf');

(async () => {
  const exe = fs.existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined;
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const page = await browser.newPage({ viewport: { width: 794, height: 1123 } });

  await page.goto('file://' + path.join(dist, 'body.html'), { waitUntil: 'networkidle', timeout: 120000 });
  await page.emulateMedia({ media: 'print' });
  await page.evaluate(() => document.fonts.ready);

  const over = await page.evaluate(() => [...document.querySelectorAll('.sheet')]
    .map((el, i) => {
      const c = el.querySelector('.cols');
      return {
        i: i + 2,
        px: Math.round(c.scrollHeight - c.clientHeight),
        t: (el.querySelector('h2') || el.querySelector('.rhead .r')).textContent.trim().slice(0, 44),
      };
    })
    .filter((p) => p.px > 1));
  for (const p of over) console.warn(`overflow: page ${p.i} clipped by ${p.px}px — ${p.t}`);

  await page.pdf({ path: out, printBackground: true, preferCSSPageSize: true });
  await browser.close();

  const n = execFileSync('pdfinfo', [out]).toString().match(/Pages:\s+(\d+)/)[1];
  console.log(`wrote ${path.relative(process.cwd(), out)} (${n} interior pages${over.length ? `, ${over.length} clipped` : ', nothing clipped'})`);
})();
