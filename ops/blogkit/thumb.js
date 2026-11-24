// 사용법: node thumb.js spec.json out.png
// photo 레이아웃: spec.photo = 로컬 jpg 경로 (실사 사진 + 훅 문구)
// spec: {"top":"군포 신혼부부","main":"대출이자 지원","amount":"최대 300만원","badge":"10월 30일 신청 마감","theme":"navy|green|red|purple|orange"}
const { chromium } = require('playwright');
const fs = require('fs');
const [,, specPath, out] = process.argv;
const s = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const themes = {
  navy:   ['#0B1F4D', '#1E3A8A', '#FFD43B'],
  green:  ['#064E3B', '#047857', '#FDE047'],
  red:    ['#7F1D1D', '#B91C1C', '#FFE066'],
  purple: ['#3B0764', '#6D28D9', '#FDE68A'],
  orange: ['#7C2D12', '#C2410C', '#FEF08A'],
};
const [bg1, bg2, hi] = themes[s.theme] || themes.navy;
const esc = t => String(t || '').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const photoHtml = () => {
  const img = 'data:image/jpeg;base64,' + fs.readFileSync(s.photo).toString('base64');
  const pos = s.photoPos || 'center 30%';
  return `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@900&display=swap" rel="stylesheet">
<style>
*{margin:0;box-sizing:border-box}
body{width:1080px;height:1080px;position:relative;overflow:hidden;font-family:'Noto Sans KR','WenQuanYi Zen Hei',sans-serif;background:#000}
.ph{position:absolute;inset:0;background:url('${img}') ${pos}/cover no-repeat}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 30%,rgba(0,0,0,.55) 55%,rgba(0,0,0,.92) 100%)}
.txt{position:absolute;left:0;right:0;bottom:64px;display:flex;flex-direction:column;align-items:center;gap:14px;text-align:center;padding:0 50px}
.top,.main,.amount{white-space:nowrap}
.top{background:#E11D26;color:#fff;font-weight:900;font-size:66px;padding:6px 30px 10px;transform:rotate(-2deg);box-shadow:0 8px 0 rgba(0,0,0,.35)}
.main{font-family:'Black Han Sans','Noto Sans KR',sans-serif;color:#fff;font-size:112px;line-height:1.05;letter-spacing:-2px;
  -webkit-text-stroke:10px #000;paint-order:stroke fill;text-shadow:0 8px 18px rgba(0,0,0,.6)}
.amount{font-family:'Black Han Sans','Noto Sans KR',sans-serif;color:#FFE100;font-size:104px;line-height:1.05;letter-spacing:-2px;
  -webkit-text-stroke:10px #000;paint-order:stroke fill;text-shadow:0 8px 18px rgba(0,0,0,.6)}
</style></head><body><div class="ph"></div><div class="shade"></div>
<div class="txt">${s.top?`<div class="top">${esc(s.top)}</div>`:''}<div class="main">${esc(s.main)}</div>${s.amount?`<div class="amount">${esc(s.amount)}</div>`:''}</div>
</body></html>`;
};
// card 레이아웃 (기본): 위 사진 + 아래 어두운 패널, 노란 주제 박스, 3줄 제목, {중괄호} = 연두 강조
// spec: {"tag":"주식 / 엔비디아","lines":["엔비디아 폭락에","{4,281억} 줍줍했다고?","세금 폭탄 주의"],"photo":"path.jpg","icon":"📉","theme":"navy"}
const cardHtml = () => {
  const img = s.photo ? 'data:image/jpeg;base64,' + fs.readFileSync(s.photo).toString('base64') : null;
  const pos = s.photoPos || 'center 35%';
  // overlay: 인물 사진을 배경에 은은하게 (오른쪽에서 왼쪽으로 사라짐)
  const ov = s.overlay ? 'data:image/jpeg;base64,' + fs.readFileSync(s.overlay.photo).toString('base64') : null;
  const line = t => esc(t).replace(/\{(.+?)\}/g, '<em>$1</em>');
  return `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;box-sizing:border-box}
body{width:1080px;height:1080px;position:relative;overflow:hidden;background:#121417;font-family:'Noto Sans KR','WenQuanYi Zen Hei',sans-serif}
.ph{position:absolute;left:0;right:0;top:0;height:600px;background:${img ? `url('${img}') ${pos}/cover no-repeat` : `radial-gradient(circle at 70% 40%, ${bg2} 0%, ${bg1} 60%, #121417 100%)`}}
.ph::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,20,23,0) 55%,rgba(18,20,23,.85) 92%,#121417 100%)}
.ov{position:absolute;right:0;top:0;width:${s.overlay ? (s.overlay.width||620) : 0}px;height:600px;background:${ov ? `url('${ov}') ${s.overlay.pos||'center 20%'}/cover no-repeat` : 'none'};opacity:${s.overlay ? (s.overlay.opacity||.45) : 0};-webkit-mask-image:linear-gradient(to left,#000 45%,transparent 100%),linear-gradient(to top,transparent 0%,#000 30%);-webkit-mask-composite:source-in;mask-composite:intersect}
.ic{position:absolute;right:90px;top:120px;font-size:300px;font-family:'Noto Color Emoji',sans-serif;opacity:.9;filter:drop-shadow(0 20px 30px rgba(0,0,0,.4))}
.panel{position:absolute;left:0;right:0;top:600px;bottom:0;padding:34px 84px 0;display:flex;flex-direction:column;gap:30px}
.tag{align-self:flex-start;background:#FFD43B;color:#111;font-weight:900;font-size:38px;padding:8px 22px;border-radius:6px;white-space:nowrap}
.t{color:#fff;font-weight:900;font-size:84px;line-height:1.2;letter-spacing:-2px}
.t div{white-space:nowrap}
${s.full ? `.ph{height:1080px} .ph::after{background:linear-gradient(180deg,rgba(18,20,23,0) 42%,rgba(18,20,23,.88) 70%,#121417 100%)} .panel{top:auto;bottom:70px}` : ''}
.t em{font-style:normal;color:#B4F05A}
</style></head><body><div class="ph"></div>${ov ? '<div class="ov"></div>' : ''}${!img && s.icon ? `<div class="ic">${esc(s.icon)}</div>` : ''}
<div class="panel">${s.tag ? `<div class="tag">${esc(s.tag)}</div>` : ''}<div class="t">${(s.lines||[]).map(l=>`<div>${line(l)}</div>`).join('')}</div></div>
</body></html>`;
};
const html = s.lines ? cardHtml() : s.photo ? photoHtml() : `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;box-sizing:border-box}
body{width:1080px;height:1080px;font-family:'Noto Sans KR','WenQuanYi Zen Hei',sans-serif;
 background:linear-gradient(160deg,${bg1} 0%,${bg2} 100%);color:#fff;display:flex;flex-direction:column;
 justify-content:center;align-items:center;text-align:center;padding:90px 70px;position:relative;overflow:hidden}
.ring{position:absolute;border-radius:50%;border:2px solid rgba(255,255,255,.08)}
.top,.main,.amount{white-space:nowrap}
.top{font-size:62px;font-weight:900;letter-spacing:-1px;opacity:.95;margin-bottom:22px}
.main{font-family:'Black Han Sans','Noto Sans KR',sans-serif;font-size:118px;line-height:1.08;letter-spacing:-2px;margin-bottom:26px;text-shadow:0 6px 0 rgba(0,0,0,.25)}
.amount{font-family:'Black Han Sans','Noto Sans KR',sans-serif;font-size:150px;line-height:1;color:${hi};letter-spacing:-3px;margin-bottom:56px;text-shadow:0 8px 0 rgba(0,0,0,.3)}
.badge{background:#fff;color:${bg1};font-size:54px;font-weight:900;padding:22px 54px;border-radius:999px;box-shadow:0 10px 0 rgba(0,0,0,.25)}
.src{position:absolute;bottom:34px;font-size:26px;opacity:.6;font-weight:700}
</style></head><body>
<div class="ring" style="width:900px;height:900px;left:-420px;top:-380px"></div>
<div class="ring" style="width:700px;height:700px;right:-360px;bottom:-300px"></div>
<div class="top">${esc(s.top)}</div>
<div class="main">${esc(s.main)}</div>
${s.amount ? `<div class="amount">${esc(s.amount)}</div>` : ''}
${s.badge ? `<div class="badge">${esc(s.badge)}</div>` : ''}
${s.footer ? `<div class="src">${esc(s.footer)}</div>` : ''}
</body></html>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  await p.setContent(html, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => {           // 한 줄에 들어가도록 글자 크기 자동 축소
    for (const el of document.querySelectorAll('.top,.main,.amount,.t div')) {
      let fs = parseFloat(getComputedStyle(el).fontSize);
      while (el.scrollWidth > 912 && fs > 30) { fs -= 2; el.style.fontSize = fs + 'px'; }
    }
    const ls = [...document.querySelectorAll('.t div')];  // 제목 줄 크기 통일
    if (ls.length) { const m = Math.min(...ls.map(l => parseFloat(getComputedStyle(l).fontSize))); ls.forEach(l => l.style.fontSize = m + 'px'); }
  });
  await p.screenshot({ path: out, type: 'png' });
  await b.close();
  console.log('saved', out);
})();
