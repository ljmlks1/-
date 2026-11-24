#!/usr/bin/env python3
"""초안 JSON의 이미지 만들기 (모두 가로 550px): 버튼(btn.js) + 본문 사진(Pexels) + 썸네일(thumb.js, 사진 있으면 실사 레이아웃).
사용법: python3 build_assets.py drafts_YYYY-MM-DD.json   → out/assets/ 에 파일, out/assets/manifest.json
사진은 후보 1번을 기본으로 쓴다. 표정이 약하면 out/photos/<id>/ 후보를 열어보고 manifest에서 바꿔 다시 실행."""
import json, os, sys, subprocess, shutil
src = sys.argv[1]
drafts = json.load(open(src))
os.makedirs("out/assets", exist_ok=True)
env = dict(os.environ, PEXELS_KEY="proxy-injected")
man = {}
def run(*a): return subprocess.run(a, capture_output=True, text=True, env=env)
def photo(query, key, n=8, pick="01"):
    d = f"out/photos/{key}"
    if not os.path.exists(f"{d}/01.jpg"):
        r = run("python3", "photo.py", query, d, str(n))
        if r.returncode: return None, (r.stdout + r.stderr).strip().splitlines()[-1]
    f = f"{d}/{pick}.jpg"
    return (f if os.path.exists(f) else None), None
for d in drafts:
    i = d["id"]; m = man[i] = {"buttons": [], "photos": [], "thumb": None, "errors": []}
    for k, b in enumerate(d.get("buttons", []), 1):
        spec = f"out/assets/{i}_btn{k}.json"; json.dump(b, open(spec, "w"), ensure_ascii=False)
        out = f"out/assets/{i}_btn{k}.png"; r = run("node", "btn.js", spec, out)
        m["buttons"].append(out if not r.returncode else None)
        if r.returncode: m["errors"].append(r.stderr[-200:])
    for k, p in enumerate(d.get("photos", []), 1):
        f, err = photo(p["query"], f"{i}_ph{k}", pick=p.get("pick", "01"))
        if f: dst = f"out/assets/{i}_ph{k}.jpg"; shutil.copy(f, dst); m["photos"].append(dst)
        else: m["photos"].append(None); m["errors"].append(f"사진{k}: {err}")
    t = dict(d["thumb"])
    if t.get("query"):
        f, err = photo(t["query"], f"{i}_thumb", pick=t.get("pick", "01"))
        if f: t["photo"] = os.path.abspath(f)
        else: m["errors"].append(f"썸네일 사진: {err} → 사진 없는 레이아웃 사용")
    spec = f"out/assets/{i}_thumb.json"; json.dump(t, open(spec, "w"), ensure_ascii=False)
    out = f"out/assets/{i}_thumb.png"; r = run("node", "thumb.js", spec, out)
    m["thumb"] = out if not r.returncode else None
# 모든 이미지 가로 550px 고정 (세로는 비율대로) — 대표님 확정 규칙
from PIL import Image
W = 550
for i, m in man.items():
    for f in [m["thumb"], *m["photos"], *m["buttons"]]:
        if not f: continue
        im = Image.open(f)
        if im.width != W:
            im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
        if f.endswith(".jpg"): im.convert("RGB").save(f, "JPEG", quality=90)
        else: im.save(f, optimize=True)
json.dump(man, open("out/assets/manifest.json", "w"), ensure_ascii=False, indent=1)
for i, m in man.items():
    print(i, "thumb", bool(m["thumb"]), "btn", sum(map(bool, m["buttons"])), "photo", sum(map(bool, m["photos"])), "| errors:", len(m["errors"]), (m["errors"][:1] or [""])[0][:90])
