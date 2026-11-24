#!/usr/bin/env python3
"""사실 확인·보강용 뉴스 검색: 네이버 뉴스에서 검색해 언론사 기사 본문(네이버뉴스 링크가 있는 것)을 읽는다.
사용법: python3 newsfind.py "양산항 프리미엄 230달러" [개수=5] → 제목·언론사·날짜·링크·본문 앞부분 출력, newsfind_last.json 저장
글에 넣는 숫자는 여기서 확인된 기사(링크)나 대표님 레퍼런스, LME 수집값에 있는 것만 쓴다."""
import re, sys, json, html, time, urllib.request, urllib.parse
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
clean = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
def get(u):
    for w in (0, 3, 8):
        time.sleep(w)
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode("utf-8", "ignore")
        except Exception as e: err = e
    raise err
x = get("https://search.naver.com/search.naver?" + urllib.parse.urlencode({"where": "news", "query": q, "sort": "1"}))
links = []
for u in re.findall(r'n\.news\.naver\.com/(?:mnews/)?article/\d+/\d+', x):
    u = "https://" + u
    if u not in links: links.append(u)
out = []
for u in links[:n]:
    try:
        y = get(u)
        t = clean((re.search(r'<h2[^>]*id="title_area"[^>]*>(.*?)</h2>', y, re.S) or re.search(r"<title>(.*?)</title>", y, re.S)).group(1))
        press = clean((re.search(r'<meta (?:property|name)="og:article:author" content="([^"|]+)', y) or re.search(r'media_end_head_top_logo_img[^>]+alt="([^"]+)"', y) or [None, ""])[1])
        date = (re.search(r'data-date-time="([^"]+)"', y) or [None, ""])[1]
        b = re.search(r'id="dic_area"[^>]*>(.*?)</article>', y, re.S)
        body = clean(re.sub(r"<br\s*/?>", "\n", b.group(1))) if b else ""
        out.append({"title": t, "press": press, "date": date, "link": u, "body": body[:3000]})
    except Exception as e: out.append({"link": u, "error": str(e)})
json.dump(out, open("newsfind_last.json", "w"), ensure_ascii=False, indent=1)
for o in out:
    print(f"■ {o.get('date','')[:16]} {o.get('press','')} | {o.get('title', o.get('error',''))[:70]}\n  {o['link']}\n  {o.get('body','')[:400]}\n")
