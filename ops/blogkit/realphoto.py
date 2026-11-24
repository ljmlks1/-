#!/usr/bin/env python3
"""실제 인물·기관·장소 사진 찾기 (출처 표기만 하면 쓸 수 있는 사진만: CC0·CC BY·CC BY-SA·공공누리·퍼블릭도메인).
언론사 사진은 출처를 밝혀도 무단 사용이 불가하므로 찾지 않는다.
사용법: python3 realphoto.py "Jensen Huang" out/real/jensen [개수=10]
결과: 폴더에 01.jpg… + candidates.json(제목, 라이선스, 작가, 원본 페이지, 출처 표기 문구). contact.py로 미리보기."""
import sys, os, json, time, urllib.request, urllib.parse
q, out = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
os.makedirs(out, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
OK = {"cc0", "pdm", "by", "by-sa"}  # 상업 이용 가능 + 변경 가능 (by-nd·nc 제외)

def get(url, timeout=40, tries=4):
    for w in (0, 5, 12, 25)[:tries]:
        time.sleep(w)
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        except Exception as e: err = e
    raise err

def wm_thumb(u, w=1280):  # 위키미디어 원본 대신 축소본(요청 제한 회피)
    if "upload.wikimedia.org/wikipedia/commons/" in u and "/thumb/" not in u:
        a, b = u.split("/wikipedia/commons/", 1)
        name = b.split("/")[-1]
        return f"{a}/wikipedia/commons/thumb/{b}/{w}px-{name}"
    return u

res = []
# 0) NASA 공개 이미지 (우주·과학 주제, 퍼블릭 도메인)
if os.environ.get("NASA", "") or any(k in q.lower() for k in ["nasa", "mars", "moon", "space", "rocket", "galaxy", "nebula", "telescope", "astronaut", "iss", "spacex", "artemis", "comet", "asteroid", "planet"]):
    try:
        d = json.loads(get("https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": q, "media_type": "image"})))
        for it in d["collection"]["items"][:15]:
            meta = it["data"][0]; link = next((l["href"] for l in it.get("links", []) if l.get("rel") == "preview"), None)
            if link:
                res.append({"src": link.replace("~thumb", "~large"), "title": meta.get("title"), "creator": "NASA", "license": "퍼블릭 도메인(NASA)",
                            "page": f"https://images.nasa.gov/details/{meta.get('nasa_id')}", "credit": "사진: NASA"})
    except Exception as e: print("NASA 실패:", e)
# 1) Openverse: 위키미디어 커먼즈·플리커의 자유 이용 사진
for src in ("wikimedia", "flickr"):
    try:
        d = json.loads(get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
            {"q": q, "source": src, "license_type": "commercial,modification", "page_size": 20})))
    except Exception as e:
        print(f"openverse {src} 실패: {e}"); continue
    for r in d.get("results", []):
        if r.get("license") in OK and (r.get("width") or 0) >= 600:
            lic = "CC0" if r["license"] == "cc0" else ("퍼블릭 도메인" if r["license"] == "pdm" else f"CC {r['license'].upper()} {r.get('license_version') or ''}".strip())
            res.append({"src": r["url"], "title": r.get("title"), "creator": r.get("creator"), "license": lic,
                        "page": r.get("foreign_landing_url"), "w": r.get("width"), "h": r.get("height"),
                        "credit": f"사진: {r.get('creator') or '작자 미상'}, {lic}" if r["license"] not in ("cc0", "pdm") else ""})
# 2) 위키백과 대표 사진(인물·기관 문서)
try:
    s = json.loads(get("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(q.replace(" ", "_")), tries=2))
    img = (s.get("originalimage") or {}).get("source")
    if img: res.insert(0, {"src": img.split("?")[0], "title": f"Wikipedia: {s.get('title')}", "creator": "위키미디어 커먼즈 (라이선스는 원본 페이지 확인)",
                           "license": "확인 필요", "page": "https://commons.wikimedia.org/wiki/File:" + img.split("/")[-1].split("?")[0], "credit": "확인 필요"})
except Exception as e:
    print("wikipedia 요약 없음:", e)

saved, seen = [], set()
for it in res:
    if len(saved) >= n or it["src"] in seen: continue
    seen.add(it["src"])
    f = os.path.join(out, f"{len(saved)+1:02d}.jpg")
    try:
        data = get(wm_thumb(it["src"]), timeout=60, tries=3)
        if len(data) < 5000: continue
        open(f, "wb").write(data); saved.append({**it, "file": f}); time.sleep(2)
    except Exception as e: print("다운로드 실패", it["src"][:70], e)
json.dump(saved, open(os.path.join(out, "candidates.json"), "w"), ensure_ascii=False, indent=1)
print(f"{len(saved)}장 → {out}")
for r in saved: print(os.path.basename(r["file"]), "|", r["license"], "|", (r["title"] or "")[:50], "|", r["credit"][:50])
