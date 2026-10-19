// Print the book to PDF: cover (no running header) + body, merged.
// Usage: node scripts/render.js   -> dist/Multilevel_Writing_Guide.pdf
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const dist = path.resolve(__dirname, '..', 'dist');
const out = path.join(dist, 'Multilevel_Writing_Guide.pdf');

const header = `<div style="width:100%;margin:0 15mm;padding-bottom:4px;border-bottom:1.5px solid #1E90FF;
display:flex;justify-content:space-between;align-items:center;font-family:Inter,sans-serif;font-size:7.5px;
color:#0A2A5E;-webkit-print-color-adjust:exact">
<span style="letter-spacing:.14em">IMPULSE <span style="opacity:.6">LEARNING CENTER</span></span>
<span style="letter-spacing:.14em"><b style="color:#1E90FF">MULTILEVEL</b> WRITING</span></div>`;

const footer = `<div style="width:100%;margin:0 15mm;display:flex;justify-content:space-between;
align-items:center;font-family:Inter,sans-serif;font-size:7px;color:#64748B;-webkit-print-color-adjust:exact">
<span>© Impulse Learning Center</span>
<span style="background:#1E90FF;color:#fff;border-radius:4px;padding:2px 7px;font-weight:700">
Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`;

(async () => {
  const exe = fs.existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined;
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const page = await browser.newPage();

  await page.goto('file://' + path.join(dist, 'body.html'), { waitUntil: 'networkidle' });

  // Warn about any .page taller than the printable A4 box (297 - 16 - 14 mm).
  const limit = (297 - 38) * (96 / 25.4); // 8mm of slack: Chromium spills a page that only just fits
  const over = await page.evaluate((lim) => [...document.querySelectorAll('.page')]
    .map((el, i) => ({ i: i + 1, h: Math.round(el.getBoundingClientRect().height),
                       t: (el.querySelector('h2') || el).textContent.trim().slice(0, 48) }))
    .filter((p) => p.h > lim), limit);
  for (const p of over) {
    console.warn(`overflow: section ${p.i} is ${p.h}px (limit ${Math.round(limit)}px) — ${p.t}`);
  }

  await page.pdf({ path: path.join(dist, 'body.pdf'), format: 'A4', printBackground: true,
    displayHeaderFooter: true, headerTemplate: header, footerTemplate: footer,
    preferCSSPageSize: true });

  await page.goto('file://' + path.join(dist, 'cover.html'), { waitUntil: 'networkidle' });
  await page.pdf({ path: path.join(dist, 'cover.pdf'), format: 'A4', printBackground: true,
    preferCSSPageSize: true });
  await browser.close();

  execFileSync('pdfunite', [path.join(dist, 'cover.pdf'), path.join(dist, 'body.pdf'), out]);
  fs.unlinkSync(path.join(dist, 'cover.pdf'));
  fs.unlinkSync(path.join(dist, 'body.pdf'));
  const n = execFileSync('pdfinfo', [out]).toString().match(/Pages:\s+(\d+)/)[1];
  console.log(`wrote ${path.relative(process.cwd(), out)} (${n} pages${over.length ? `, ${over.length} overflowing` : ', no overflow'})`);
})();
