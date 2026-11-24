#!/usr/bin/env python3
"""캐러셀 슬라이드 → 릴스 가운데 영상 만들기 (슬라이드 영상형). 이후 reel.py로 제목·출처 틀을 씌운다.
사용: python3 reel_slides.py out_src.mp4 sec_per_slide slide1.jpg slide2.jpg ...  (엔딩 슬라이드는 빼고 넣는다)
각 슬라이드를 천천히 확대(줌인)하며 sec초씩, 0.5초 크로스페이드. 소리 없음(무음 트랙 포함)."""
import sys, subprocess
out, sec, imgs = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
n = len(imgs); fps = 30; fr = int(sec * fps); xf = 0.5
args = []
for f in imgs: args += ["-loop", "1", "-t", str(sec), "-i", f]
args += ["-f", "lavfi", "-t", str(n * sec - (n - 1) * xf), "-i", "anullsrc=r=44100:cl=stereo"]
fl = []
for i in range(n):
    fl.append(f"[{i}:v]scale=1080:1350,zoompan=z='min(zoom+0.0006,1.06)':d={fr}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1350:fps={fps},setsar=1,format=yuv420p[s{i}]")
last = "s0"
for i in range(1, n):
    off = i * sec - i * xf
    fl.append(f"[{last}][s{i}]xfade=transition=fade:duration={xf}:offset={off}[x{i}]"); last = f"x{i}"
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", ";".join(fl), "-map", f"[{last}]", "-map", f"{n}:a",
                "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-shortest", out], check=True)
print("saved", out)
