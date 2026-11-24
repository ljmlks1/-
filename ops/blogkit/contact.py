#!/usr/bin/env python3
"""사진 후보 폴더를 번호 붙은 한 장짜리 미리보기로. 사용법: python3 contact.py 폴더 [폴더…] → 각 폴더/contact.jpg"""
import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 40) if os.path.exists("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc") else None
for d in sys.argv[1:]:
    fs = sorted(glob.glob(f"{d}/[0-9][0-9].jpg"))
    if not fs: continue
    W, H, cols = 400, 280, 4
    rows = (len(fs) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, H * rows), "white")
    for i, f in enumerate(fs):
        try: im = Image.open(f).convert("RGB")
        except Exception: continue
        im.thumbnail((W - 6, H - 6))
        x, y = (i % cols) * W, (i // cols) * H
        sheet.paste(im, (x + 3, y + 3))
        ImageDraw.Draw(sheet).text((x + 10, y + 6), os.path.basename(f)[:2], fill="yellow", font=font, stroke_width=3, stroke_fill="black")
    sheet.save(f"{d}/contact.jpg", quality=80)
    print(f"{d}/contact.jpg")
