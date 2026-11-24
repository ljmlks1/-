#!/usr/bin/env python3
"""실사 사진 검색·다운로드. 1순위 Pexels(키 필요), 실패 시 Openverse의 CC0 스톡 사진(StockSnap·WordPress 사진, 상업 이용 가능·출처 표기 불필요).
사용법: python3 photo.py "worried man phone" out/photos/키 [개수=6]
결과: 폴더에 01.jpg… + candidates.json. 검색어는 영어 2~3단어가 잘 걸린다(없으면 단어를 줄여 재검색)."""
import sys, os, json, time, urllib.request, urllib.parse
q, out = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
os.makedirs(out, exist_ok=True)
UA = {"User-Agent": "blog-auto/1.0"}
def get(url, headers=None, timeout=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}), timeout=timeout)

def pexels(query):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": query, "per_page": n, "orientation": "landscape"})
    data = json.load(get(url, {"Authorization": os.environ.get("PEXELS_KEY", "proxy-injected")}))
    return [{"src": p["src"]["large2x"], "alt": p.get("alt"), "by": p.get("photographer"), "page": p["url"], "license": "Pexels"} for p in data.get("photos", [])]

def openverse(query):
    res, words = [], query.split()
    while words and len(res) < n:
        for src in ("stocksnap", "wordpress"):
            url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
                {"q": " ".join(words), "source": src, "license": "cc0", "page_size": 20, "category": "photograph"})
            data = None
            for wait in (0, 4, 10, 20):
                time.sleep(wait)
                try: data = json.load(get(url, timeout=40)); break
                except Exception: pass
            if not data: continue
            for r in data.get("results", []):
                if (r.get("width") or 0) >= 1000 and r["url"] not in {x["src"] for x in res}:
                    res.append({"src": r["url"], "alt": r.get("title"), "by": r.get("creator"), "page": r.get("foreign_landing_url"), "license": "CC0 " + src})
        words = words[:-1]  # 결과가 모자라면 마지막 단어를 빼고 재검색
    return res[:n]

items, err = [], None
try: items = pexels(q)
except Exception as e: err = f"pexels: {e}"
if not items: items = openverse(q)
saved = []
for i, it in enumerate(items, 1):
    f = os.path.join(out, f"{i:02d}.jpg")
    try:
        with get(it["src"], timeout=60) as r, open(f, "wb") as w: w.write(r.read())
        saved.append({**it, "file": f})
    except Exception as e: print("download fail", it["src"][:60], e)
json.dump(saved, open(os.path.join(out, "candidates.json"), "w"), ensure_ascii=False, indent=1)
print(f"{len(saved)}장 저장 → {out}" + (f" (Pexels 실패 → CC0 스톡 사용)" if err else ""))
for r in saved: print(r["file"], "|", r["license"], "|", (r["alt"] or "")[:60])
if not saved: sys.exit(1)
