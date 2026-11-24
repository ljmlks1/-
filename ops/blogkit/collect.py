#!/usr/bin/env python3
"""매일 블로그 주제 후보 수집: 네이버 뉴스 랭킹/섹션 + 모아픽. 결과는 candidates.json"""
import re, html, json, sys, datetime, collections, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

def get(url, enc=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"})
    raw = urllib.request.urlopen(req, timeout=25).read()
    if enc: return raw.decode(enc, "ignore")
    m = re.search(rb'charset=["\']?([\w-]+)', raw[:2000])
    return raw.decode((m.group(1).decode() if m else "utf-8"), "ignore")

clean = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()

SECTIONS = {
    "정치": "https://news.naver.com/section/100",
    "경제": "https://news.naver.com/section/101",
    "사회": "https://news.naver.com/section/102",
    "증권(주식)": "https://news.naver.com/breakingnews/section/101/258",
    "금융(대출)": "https://news.naver.com/breakingnews/section/101/259",
    "부동산(청약)": "https://news.naver.com/breakingnews/section/101/260",
    "IT/과학": "https://news.naver.com/section/105",
    "과학 일반": "https://news.naver.com/breakingnews/section/105/228",
    "IT 일반": "https://news.naver.com/breakingnews/section/105/230",
    "모바일·빅테크": "https://news.naver.com/breakingnews/section/105/731",
}

def news_ranking():
    x = get("https://news.naver.com/main/ranking/popularDay.naver", "euc-kr")
    out = []
    for blk in re.findall(r'<div class="rankingnews_box">(.*?)</ul>', x, re.S):
        press = clean((re.search(r'rankingnews_name">(.*?)<', blk) or [None, ""])[1])
        for rank, (link, t) in enumerate(re.findall(r'<a href="([^"]+)" class="list_title[^"]*"[^>]*>(.*?)</a>', blk, re.S), 1):
            out.append({"press": press, "rank": rank, "title": clean(t), "link": link})
    return out

def section(url):
    x = get(url)
    out = []
    for m in re.finditer(r'<a href="([^"]+)" class="sa_text_title[^"]*"[^>]*>\s*<strong class="sa_text_strong"[^>]*>(.*?)</strong>', x, re.S):
        out.append({"title": clean(m.group(2)), "link": m.group(1)})
    if not out:
        out = [{"title": clean(t), "link": ""} for t in re.findall(r'class="sa_text_strong"[^>]*>(.*?)</strong>', x, re.S)]
    return out[:60]

STOP = set("""속보 단독 종합 영상 포토 오늘 내일 어제 이번 지난 올해 내년 작년 관련 위해 대한 통해 이유 결국 사실 논란 공개 발표 진행 가능 예정 확인 기자 뉴스 사진 한국 국내 정부 대통령 의혹 첫 대해 무슨 이런 그런 어떻게 왜 더 또 수 등 것 년 월 일 만 억 원 명 개 곳 중 후 전 앞 뒤 위 및 vs""".split())

def keywords(titles, n=50):
    cnt, ex = collections.Counter(), collections.defaultdict(list)
    for t in titles:
        toks = set()
        for w in re.findall(r"[가-힣A-Za-z0-9·]{2,}", re.sub(r"\[.*?\]", " ", t)):
            w = re.sub(r"(은|는|이|가|을|를|의|에|에서|으로|로|과|와|도|만|까지|부터|에게|께|이다|했다|한다|된다)$", "", w)
            if len(w) >= 2 and w not in STOP and not w.isdigit():
                toks.add(w)
        for w in toks:
            cnt[w] += 1
            if len(ex[w]) < 3: ex[w].append(t)
    return [{"kw": k, "count": c, "examples": ex[k]} for k, c in cnt.most_common(n)]

def moapick():
    x = get("https://moa-pick.com/rss")
    items = []
    for it in re.findall(r"<item>(.*?)</item>", x, re.S):
        g = lambda tag: clean((re.search(rf"<{tag}>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>", it, re.S) or [None, ""])[1])
        items.append({"title": g("title"), "link": g("link"), "desc": g("description"), "date": g("pubDate")})
    closing = []
    try:
        y = get("https://moa-pick.com/benefit/closing")
        for href, txt in re.findall(r'<a[^>]+href="(/benefit/[^"#?]+)"[^>]*>(.*?)</a>', y, re.S):
            t = clean(txt)
            if len(t) > 8 and href.count("/") >= 2 and href != "/benefit/closing":
                closing.append({"title": t[:160], "link": "https://moa-pick.com" + href})
    except Exception as e:
        closing.append({"error": str(e)})
    seen, uniq = set(), []
    for c in closing:
        k = c.get("link")
        if k not in seen: seen.add(k); uniq.append(c)
    return {"rss": items, "closing": uniq[:60]}

def main(out="candidates.json"):
    res = {"collected_at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(), "errors": []}
    try: res["ranking"] = news_ranking()
    except Exception as e: res["ranking"] = []; res["errors"].append(f"ranking: {e}")
    res["sections"] = {}
    for name, url in SECTIONS.items():
        try: res["sections"][name] = section(url)
        except Exception as e: res["sections"][name] = []; res["errors"].append(f"{name}: {e}")
    try: res["moapick"] = moapick()
    except Exception as e: res["moapick"] = {"rss": [], "closing": []}; res["errors"].append(f"moapick: {e}")
    # 랭킹 상위(언론사별 1~3위)는 가중치 2배
    weighted = [r["title"] for r in res["ranking"]] + [r["title"] for r in res["ranking"] if r["rank"] <= 3]
    res["hot_overall"] = keywords(weighted, 40)
    res["hot_by_section"] = {k: keywords([i["title"] for i in v], 15) for k, v in res["sections"].items()}
    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"ranking {len(res['ranking'])} / sections " + ", ".join(f"{k} {len(v)}" for k, v in res["sections"].items())
          + f" / moapick rss {len(res['moapick']['rss'])} closing {len(res['moapick']['closing'])} / errors {res['errors']}")
    print("HOT:", ", ".join(f"{k['kw']}({k['count']})" for k in res["hot_overall"][:25]))
    for k, v in res["hot_by_section"].items():
        print(f"[{k}]", ", ".join(f"{i['kw']}({i['count']})" for i in v[:10]))

if __name__ == "__main__":
    main(*(sys.argv[1:2]))
