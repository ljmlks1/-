#!/usr/bin/env python3
"""릴스 템플릿 (사용자 확정 2026-11-24): 1080x1920 검은 배경, 위 제목 2줄(1줄 흰색 / 2줄 주황), 가운데 원본 영상(비율 유지, 원본 소리 그대로), 아래 출처 한 줄.
사용: python3 reel.py spec.json out.mp4
spec = {"src":"원본.mp4","start":22,"dur":30,"line1":"흰 줄","line2":"주황 줄","credit":"영상: NASA"}"""
import json, sys, subprocess, pathlib, base64, os, tempfile
s = json.load(open(sys.argv[1])); out = sys.argv[2]
HERE = pathlib.Path(__file__).resolve().parent
font = lambda w: base64.b64encode((HERE / "fonts" / f"nskr-{w}.woff2").read_bytes()).decode()
esc = lambda t: str(t).replace("&", "&amp;").replace("<", "&lt;")
html = f"""<html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:800;src:url(data:font/woff2;base64,{font(800)})}}
@font-face{{font-family:K;font-weight:500;src:url(data:font/woff2;base64,{font(500)})}}
body{{margin:0;width:1080px;height:1920px;background:transparent;font-family:K}}
.t{{position:absolute;top:150px;left:40px;right:40px;text-align:center;font-weight:800;line-height:1.22;letter-spacing:-2px}}
.t div{{white-space:nowrap;font-size:84px}} .a{{color:#fff}} .b{{color:#FF8A00}}
.c{{position:absolute;bottom:250px;left:40px;right:40px;text-align:center;color:#cfcfcf;font-weight:500;font-size:40px}}
</style></head><body><div class=t><div class=a>{esc(s['line1'])}</div><div class=b>{esc(s['line2'])}</div></div>
<div class=c>{esc(s.get('credit',''))}</div>
<script>for(const d of document.querySelectorAll('.t div')){{let f=84;while(d.scrollWidth>1000&&f>48){{f-=2;d.style.fontSize=f+'px'}}}}</script></body></html>"""
tmp = tempfile.mkdtemp(); hp = os.path.join(tmp, "o.html"); png = os.path.join(tmp, "o.png"); open(hp, "w").write(html)
subprocess.run(["node", "-e", f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});await p.goto('file://{hp}');await p.waitForTimeout(400);await p.screenshot({{path:'{png}',omitBackground:true}});await b.close()}})()"""], check=True)
# 영상 영역: 제목 아래(y=420)~출처 위(y=1640), 가로 1080에 맞추고 세로 가운데
vf = ("[0:v]scale=1080:1220:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:420+(1220-ih)/2:black,setsar=1[v];"
      "[v][1:v]overlay=0:0,format=yuv420p[o]")
cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(s.get("start", 0)), "-t", str(s.get("dur", 30)), "-i", s["src"], "-i", png,
       "-filter_complex", vf, "-map", "[o]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", "30",
       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
subprocess.run(cmd, check=True); print("saved", out)
