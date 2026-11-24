"""초안 HTML 헬퍼 (네이버 에디터 붙여넣기용)
- 글꼴: 본문 전체 마루부리 (네이버 기본 제공 글꼴), 기본 크기 16px (인용구 19px)
- 인용구: 네이버 에디터 인용구 컴포넌트 구조(se-quotation)를 그대로 쓴다.
  소제목 SUB = '포스트잇' 스타일, 도입 훅 QUOTE = '따옴표' 스타일. 네모 표 박스는 쓰지 않는다.
"""
NB = "&nbsp;"
FONT = "font-family:'MaruBuri','마루부리','Nanum Myeongjo',serif"
P = f"text-align:center;{FONT};font-size:16px;color:#000000"  # 기본 16px, 검은색

def _span(t, size="fs16"):  # 네이버 에디터 글꼴·크기 클래스(마루부리)
    return f'<span class="se-fs-{size} se-ff-nanummaruburi" style="{FONT};font-size:{size[2:]}px;color:#000000">{t}</span>'

def C(*lines):  # 가운데 정렬 문단. "" = 빈 줄(실제 공백 문단)
    return "".join(f'<p class="se-text-paragraph se-text-paragraph-align-center" style="{P}">{_span(l) if l else NB}</p>' for l in lines)
GAP = f'<p class="se-text-paragraph se-text-paragraph-align-center" style="{P}">{NB}</p>'
B = lambda t: f"<b>{t}</b>"
HL = lambda t: f'<span style="background-color:#D9F99D"><b>{t}</b></span>'
CUR = {"btns": [], "photos": []}

def _quote(style, lines, bold):  # 네이버 인용구 컴포넌트 구조 그대로
    ps = "".join(f'<p class="se-text-paragraph se-text-paragraph-align-center" style="{P}">'
                 f'{_span(f"<b>{l}</b>" if bold else l, "fs19")}</p>' for l in lines)
    return (f'<div class="se-component se-quotation se-l-{style}" data-naver="{ "subtitle" if bold else "quote" }">'
            f'<div class="se-component-content"><div class="se-section se-section-quotation se-l-{style}">'
            f'<blockquote class="se-quotation-container"><div class="se-module se-module-text se-quote">{ps}</div>'
            f'</blockquote></div></div></div>')

def QUOTE(*lines):  # 도입부 훅: 네이버 인용구 '따옴표'(기본) 스타일, 19px
    return _quote("default", lines, False)

def SUB(t):  # 소제목: 네이버 인용구 '포스트잇' 스타일, 19px 굵게 (<br>로 줄 나눔)
    return _quote("quotation_postit", t.split("<br>"), True)

def PHOTO(desc, query, pick="01"):  # 본문 사진 자리. query = 영어 검색어(사물·장면 1~2단어), pick = 후보 번호
    CUR["photos"].append({"desc": desc, "query": query, "pick": pick})
    n = len(CUR["photos"])
    return f'<p data-naver="photo" data-ph="{n}" style="{P}">📷 사진 {n} 자리 · {desc}</p>'

def BTN(label, url, color="green", icon="👉"):  # 그라데이션 배너 이미지 + 링크. 붙여넣기 때 배너 자리에 연결할 주소를 표시
    CUR["btns"].append({"label": label, "url": url, "color": color, "icon": icon})
    n = len(CUR["btns"])
    return (f'<p data-naver="button" data-btn="{n}" data-url="{url}" style="{P}">'
            f'<a href="{url}" style="color:#000000">{_span(f"<b>{icon} {label}</b>")}</a></p>')

def TABLE(rows):
    head, *body = rows
    th = "".join(f'<td style="{P};background-color:#FDE7D3;padding:8px"><b>{h}</b></td>' for h in head)
    tb = "".join("<tr>" + "".join(f'<td style="{P};padding:8px">{c}</td>' for c in r) + "</tr>" for r in body)
    return f'<table border="1" style="border-collapse:collapse;margin:16px auto;width:100%"><tbody><tr>{th}</tr>{tb}</tbody></table>'

TAGS = lambda tags: f'<p class="se-text-paragraph se-text-paragraph-align-center" style="{P}">' + _span(" ".join("#" + t for t in tags), "fs13") + "</p>"  # 해시태그 13px

def BODY(d, blocks):  # 블록 사이마다 빈 줄을 넣어 가독성 확보, 버튼·사진 목록을 초안에 저장
    d["buttons"], d["photos"] = CUR["btns"], CUR["photos"]
    CUR["btns"], CUR["photos"] = [], []
    return GAP.join(blocks)

def UNK(t):  # 사실 확인을 못 한 부분: 노란 표시. 발행 전에 대표님이 확인하고 지운다
    return f'<span style="background-color:#FDE68A;color:#000000"><b>⚠ 확인 필요: {t}</b></span>'
