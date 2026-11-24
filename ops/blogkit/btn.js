// 링크 버튼 이미지 (그라데이션 + 아이콘). 사용법: node btn.js spec.json out.png
// spec: {"label":"홈택스 증여세 모의계산 하기","icon":"🧮","color":"blue|green|orange|purple|red"}
const { chromium } = require('playwright');
const fs = require('fs');
const [,, specPath, out] = process.argv;
const s = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const G = {
  green:  ['#16C784', '#0EA5A4'], blue: ['#3B82F6', '#6D5DF6'], orange: ['#FF8A00', '#FF4D4D'],
  purple: ['#8B5CF6', '#EC4899'], red: ['#F43F5E', '#F97316'],
};
const [a, b] = G[s.color] || G.green;
const esc = t => String(t || '').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const html = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@800;900&display=swap" rel="stylesheet">
<style>*{margin:0;box-sizing:border-box}
body{width:900px;height:190px;background:transparent;display:flex;align-items:center;justify-content:center;font-family:'Noto Sans KR','WenQuanYi Zen Hei',sans-serif}
.b{width:860px;height:150px;border-radius:999px;background:linear-gradient(100deg,${a},${b});display:flex;align-items:center;gap:22px;padding:0 34px 0 18px;
 box-shadow:0 10px 22px rgba(0,0,0,.18), inset 0 2px 0 rgba(255,255,255,.35);position:relative;overflow:hidden}
.b::before{content:"";position:absolute;left:-40px;top:-60px;width:420px;height:120px;background:rgba(255,255,255,.18);transform:rotate(-8deg);border-radius:50%}
.i{width:114px;height:114px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;font-size:62px;font-family:'Noto Color Emoji',sans-serif;flex:none;box-shadow:0 4px 10px rgba(0,0,0,.15)}
.t{flex:1;color:#fff;font-weight:900;font-size:46px;letter-spacing:-1px;white-space:nowrap;text-shadow:0 2px 4px rgba(0,0,0,.2)}
.ar{width:62px;height:62px;border-radius:50%;background:rgba(255,255,255,.25);display:flex;align-items:center;justify-content:center;color:#fff;font-size:40px;font-weight:900;flex:none}
</style></head><body><div class="b"><div class="i">${esc(s.icon || '👉')}</div><div class="t">${esc(s.label)}</div><div class="ar">›</div></div></body></html>`;
(async () => {
  const br = await chromium.launch();
  const p = await br.newPage({ viewport: { width: 900, height: 190 }, deviceScaleFactor: 1 });
  await p.setContent(html, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => { const t = document.querySelector('.t'); let fs = 46;
    while (t.scrollWidth > t.clientWidth && fs > 26) { fs -= 2; t.style.fontSize = fs + 'px'; } });
  await p.screenshot({ path: out, omitBackground: true });
  await br.close(); console.log('saved', out);
})();
