#!/usr/bin/env python3
"""릴스 템플릿 — 이 폼으로 고정, 절대 변형 금지 (사용자 확정 2026-11-24, 굵은 폰트 Noto Sans KR 900, 줄은 항상 한 줄 단위로 맞춤(출처는 \\n으로 줄 나눔, 줄마다 자동 축소), 실제 영상만·이모티콘 금지·캐러셀 슬라이드 사용 금지): 1080x1920 검은 배경, 위 제목 2줄(1줄 흰색 / 2줄 주황), 가운데 원본 영상(비율 유지, 원본 소리 그대로), 아래 출처 한 줄.
사용: python3 reel.py spec.json out.mp4
spec = {"src":"원본.mp4","start":22,"dur":30,"line1":"흰 줄","line2":"주황 줄","credit":"영상: NASA"}"""
import json, sys, subprocess, pathlib, base64, os, tempfile
s = json.load(open(sys.argv[1])); out = sys.argv[2]
import re
EMO = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D\u2B00-\u2BFF\u2190-\u21FF\u2300-\u23FF]")
for k in ("line1", "line2", "credit"): s[k] = EMO.sub("", s.get(k, "")).strip()  # 릴스 이모티콘 절대 금지(사용자 확정)
HERE = pathlib.Path(__file__).resolve().parent
font = lambda w: base64.b64encode((HERE / "fonts" / f"nskr-{w}.woff2").read_bytes()).decode()
esc = lambda t: str(t).replace("&", "&amp;").replace("<", "&lt;")
html = f"""<html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@900&display=swap" rel="stylesheet"><style>
@font-face{{font-family:K;font-weight:800;src:url(data:font/woff2;base64,{font(800)})}}
@font-face{{font-family:K;font-weight:500;src:url(data:font/woff2;base64,{font(500)})}}
body{{margin:0;width:1080px;height:1920px;background:transparent;font-family:'Noto Sans KR',K}}
.t{{position:absolute;bottom:TITLE_BOTTOMpx;left:30px;right:30px;text-align:center;font-weight:900;line-height:1.22;letter-spacing:-2px}}
.t div{{white-space:nowrap;font-size:108px}} .a{{color:#fff}} .b{{color:#FF8A00}}
.c{{position:absolute;top:CREDIT_TOPpx;left:40px;right:40px;text-align:center;color:#cfcfcf;font-weight:900;font-size:40px;line-height:1.35}} .c div{{white-space:nowrap}}
</style></head><body><div class=t><div class=a>{esc(s['line1'])}</div><div class=b>{esc(s['line2'])}</div></div>
<div class=c>{''.join('<div>'+esc(x)+'</div>' for x in s.get('credit','').split(chr(10)))}</div>
<script>for(const d of document.querySelectorAll('.c div')){{let f=40;while(d.scrollWidth>1000&&f>26){{f-=1;d.style.fontSize=f+'px'}}}}for(const d of document.querySelectorAll('.t div')){{let f=108;while(d.scrollWidth>1020&&f>56){{f-=2;d.style.fontSize=f+'px'}}}}</script></body></html>"""
w,h=map(int,(s["crop"].split(":")[:2] if s.get("crop") else subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","csv=p=0",s["src"]],capture_output=True,text=True).stdout.strip().split(",")[:2]))
vh=min(1220,round(1080*h/w)); vh-=vh%2; vtop=420+(1220-vh)//2; vbot=vtop+vh
html=html.replace("TITLE_BOTTOM",str(1920-vtop+60)).replace("CREDIT_TOP",str(vbot+40))
tmp = tempfile.mkdtemp(); hp = os.path.join(tmp, "o.html"); png = os.path.join(tmp, "o.png"); open(hp, "w").write(html)
subprocess.run(["node", "-e", f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});await p.goto('file://{hp}');await p.waitForLoadState('networkidle');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);await p.screenshot({{path:'{png}',omitBackground:true}});await b.close()}})()"""], check=True)
# 한글 자막(선택, 사용자 요청 2026-11-25 "영어를 못알아들음"): spec "subs": [[시작초, 끝초, "자막"], ...] (클립 기준 시각, \n 줄바꿈 가능)
subs = s.get("subs") or []
sub_pngs = []
for i, (t0, t1, txt) in enumerate(subs):
    sh = os.path.join(tmp, f"s{i}.html"); sp = os.path.join(tmp, f"s{i}.png")
    open(sh, "w").write(f"""<html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@900&display=swap" rel="stylesheet"><style>
body{{margin:0;width:1080px;height:1920px;background:transparent;font-family:'Noto Sans KR'}}
.s{{position:absolute;bottom:{1920-vbot+28}px;left:40px;right:40px;text-align:center}}
.s span{{display:inline-block;background:rgba(0,0,0,.72);color:#fff;font-weight:900;font-size:50px;line-height:1.3;padding:8px 22px;border-radius:12px}}
</style></head><body><div class=s><span>{'<br>'.join(esc(x) for x in str(txt).split(chr(10)))}</span></div></body></html>""")
    subprocess.run(["node", "-e", f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});await p.goto('file://{sh}');await p.waitForLoadState('networkidle');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);await p.screenshot({{path:'{sp}',omitBackground:true}});await b.close()}})()"""], check=True)
    sub_pngs.append((t0, t1, sp))
# 영상 영역: 제목 아래(y=420)~출처 위(y=1640), 가로 1080에 맞추고 세로 가운데
crop = ("crop=" + s["crop"] + ",") if s.get("crop") else ""
vf = (f"[0:v]{crop}scale=1080:1220:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:420+(1220-ih)/2:black,setsar=1[v];"
      "[v][1:v]overlay=0:0[b0]")
last = "b0"
for i, (t0, t1, _) in enumerate(sub_pngs):
    vf += f";[{last}][{i+2}:v]overlay=0:0:enable='between(t,{t0},{t1})'[b{i+1}]"; last = f"b{i+1}"
vf += f";[{last}]format=yuv420p[o]"
extra = sum((["-i", sp] for _, _, sp in sub_pngs), [])
cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(s.get("start", 0)), "-t", str(s.get("dur", 30)), "-i", s["src"], "-i", png, *extra,
       "-filter_complex", vf, "-map", "[o]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", "30",
       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
subprocess.run(cmd, check=True); print("saved", out)
