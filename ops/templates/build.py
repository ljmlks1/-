#!/usr/bin/env python3
"""이슈압축 / 유머밈어워드 캐러셀 템플릿 엔진.
설계 단위: 가로 1024. 기준 원본(4:5, 1024x1280)에서 잰 좌표를 그대로 사용한다.
3:4 출력(기본): 세로 1365 단위 → 1080x1440으로 저장. 늘어난 85단위는 사진 영역에 배분한다.
사용: python3 build.py spec.json outdir [--ratio 4:5]
spec = {"brand":"issue|humor","cover":{...},"pages":[...],"end":{...}}
"""
import json, sys, os, base64, html, subprocess, pathlib
HERE = pathlib.Path(__file__).resolve().parent
BR = {
 "issue": {"acc":"#c2f471","div":"#5f6656","logoL":"logos/issue-logo-large.png","logoS":"logos/issue-logo-small.png","logoSize":138,
           "endL1":"세상에 몰랐던","endL2":"흥미로운 <a>이슈</a>","name":"이슈압축","sub":"ISSUE COMPRESS","handle":"@issue.ap"},
 "humor": {"acc":"#fe7819","div":"#5e4f43","logoL":"logos/humor-logo-large.png","logoS":"logos/humor-logo-small.png","logoSize":171,
           "endL1":"오늘의 웃음 후보","endL2":"함께 볼 <a>한 장면</a>","name":"유머밈어워드","sub":"HUMOR MEME AWARD","handle":"@legendhumormeme"},
}
def uri(p):
    p = pathlib.Path(p); p = p if p.is_absolute() else HERE / p
    ext = p.suffix.lower().lstrip('.'); ext = 'jpeg' if ext in ('jpg','jpeg') else ext
    return f"data:image/{ext};base64," + base64.b64encode(p.read_bytes()).decode()
def fonts():
    css = ""
    for w in (400,500,700,800):
        for sub,rng in (("korean","U+AC00-D7A3,U+1100-11FF,U+3130-318F,U+3000-303F,U+FF00-FFEF"),("latin","U+0000-00FF,U+2000-206F,U+2190-21FF")):
            f = HERE/"fonts"/(f"nskr-{w}.woff2" if sub=="korean" else f"nskr-latin-{w}.woff2")
            css += f"@font-face{{font-family:NSKR;font-weight:{w};src:url(data:font/woff2;base64,{base64.b64encode(f.read_bytes()).decode()}) format('woff2');unicode-range:{rng}}}\n"
    return css
def acc(t): return t.replace("<a>","<span class=acc>").replace("</a>","</span>")
def footer(b, left, page, total):
    return f'<div class=foot><span>{left}</span><span>{page:02d}/{total:02d}</span><img src="{uri(b["logoS"])}"></div>'

def build(spec, outdir, ratio="4:5"):
    b = BR[spec["brand"]]; H = 1365 if ratio=="3:4" else 1280; E = H-1280
    total = len(spec["pages"]) + 2
    css = fonts() + f"""
    *{{margin:0;padding:0;box-sizing:border-box}} body{{background:#000;font-family:NSKR,sans-serif}}
    .card{{width:1024px;height:{H}px;position:relative;overflow:hidden;background:#151716;color:#fff}}
    .acc{{color:{b['acc']}}}
    .foot{{position:absolute;left:95px;width:834px;top:{1186+E}px;height:51px;display:flex;justify-content:space-between;align-items:center;font-size:18px;color:#a8aaa9;font-weight:400}}
    .foot img{{width:51px;height:51px;display:block}}
    .cv-photo{{position:absolute;left:0;top:0;width:1024px;height:{880+E}px;object-fit:cover}}
    .cv-grad{{position:absolute;left:0;top:{600+E}px;width:1024px;height:280px;background:linear-gradient(rgba(21,23,22,0),rgba(21,23,22,.55))}}
    .cv-band{{position:absolute;left:0;top:{880+E}px;width:1024px;bottom:0;background:#151716}}
    .tag{{position:absolute;left:95px;top:{733+E}px;height:57px;padding:0 15px;background:#ffd83d;color:#151515;font-size:26px;font-weight:700;display:flex;align-items:center;border-radius:3px}}
    .cv-h{{position:absolute;left:95px;right:60px;top:{815+E}px;font-size:64px;font-weight:700;line-height:85px;letter-spacing:-2px}}
    .in-img{{position:absolute;left:0;top:0;width:1024px;height:{578+E}px;overflow:hidden;background:#151716}}
    .in-img img{{width:100%;height:100%;object-fit:cover}}
    .in-img.contain img{{object-fit:contain}}
    .ov{{position:absolute;left:0;top:0;width:1024px;height:{578+E}px;display:flex;align-items:center;justify-content:flex-end;padding-right:44px}}\n    .ov.center{{justify-content:center;padding:0}}\n    .ov.left{{justify-content:flex-start;padding-left:44px;padding-right:0}}
    .chat{{background:rgba(15,17,20,.78);border-radius:22px;padding:20px 22px;width:380px;display:flex;flex-direction:column;gap:12px;backdrop-filter:blur(2px)}}
    .chat .t{{font-size:20px;color:#aab;text-align:center;margin-bottom:4px}}
    .me{{align-self:flex-end;background:#ffe14d;color:#151515;font-size:25px;padding:11px 18px;border-radius:18px 18px 4px 18px;max-width:320px}}
    .you{{align-self:flex-start;background:#fff;color:#151515;font-size:25px;padding:11px 18px;border-radius:18px 18px 18px 4px;max-width:320px}}
    .mt{{font-size:16px;color:#9aa;align-self:flex-end;margin-top:-6px}} .mtl{{font-size:16px;color:#9aa;align-self:flex-start;margin-top:-6px}}
    .del{{align-self:flex-end;background:rgba(255,255,255,.15);color:#bbb;font-size:23px;padding:11px 18px;border-radius:18px;font-style:italic}}
    .cap{{position:absolute;left:95px;top:25px;background:rgba(0,0,0,.72);color:#f2f2f2;font-size:19px;padding:7px 12px;font-weight:400}}
    .in-h{{position:absolute;left:40px;right:40px;top:{638+E}px;text-align:center;font-size:44px;font-weight:700;line-height:62px}}
    .in-p{{position:absolute;left:40px;right:40px;top:{790+E}px;text-align:center;font-size:33.5px;font-weight:400;line-height:57px;color:#f2f2f2}}
    .teaser{{position:absolute;left:95px;top:{1096+E}px;font-size:25px;color:#dcdcdc}}
    .end-bg{{position:absolute;inset:-40px;background-size:cover;background-position:center;filter:grayscale(1) blur(14px) brightness(.33)}}
    .end-c{{position:absolute;left:0;right:0;top:{E//2}px;height:1280px;text-align:center}}
    .e1{{position:absolute;left:0;right:0;top:227px;font-size:39.5px;font-weight:400}}
    .e2{{position:absolute;left:0;right:0;top:299px;font-size:58px;font-weight:700}}
    .erow{{position:absolute;left:0;right:0;top:{438 if spec['brand']=='issue' else 437}px;display:flex;justify-content:center;align-items:center;gap:26px}}
    .erow img{{width:{b['logoSize']}px;height:{b['logoSize']}px;display:block}}
    .erow span{{font-size:64px;font-weight:700}}
    .esub{{position:absolute;left:0;right:0;top:{601 if spec['brand']=='issue' else 634}px;font-size:21px;letter-spacing:5.1px;color:#c9c9c9}}
    .ediv{{position:absolute;left:228px;width:568px;top:{675 if spec['brand']=='issue' else 708}px;height:1px;background:{b['div']}}}
    .ebody{{position:absolute;left:0;right:0;top:{736 if spec['brand']=='issue' else 769}px;font-size:33.6px;line-height:65px}}
    .ehandle{{position:absolute;left:0;right:0;top:{926 if spec['brand']=='issue' else 962}px;font-size:24px;color:#a9a9a9}}
    """
    cards = []
    c = spec["cover"]
    cards.append(f'<div class=card><img class=cv-photo src="{uri(c["photo"])}" style="object-position:{c.get("pos","center")}"><div class=cv-grad></div><div class=cv-band></div>'
                 f'<div class=tag>{c["tag"]}</div><div class=cv-h>{acc(c["title"])}</div>{footer(b,c["credit"],1,total)}</div>')
    for i,p in enumerate(spec["pages"], start=2):
        if p.get("figure"):
            p["overlay"] = f'<img src="{uri(p["figure"])}" style="max-height:{530+E}px;max-width:720px;background:#fff;padding:12px;border-radius:6px;box-shadow:0 10px 40px rgba(0,0,0,.5)">'
            p.setdefault("ovside","center")
        fit = " contain" if p.get("fit")=="contain" else ""
        cards.append(f'<div class=card><div class="in-img{fit}"><img src="{uri(p["photo"])}" style="object-position:{p.get("pos","center")};{p.get("imgstyle","")}"></div>'
                     + (f'<div class="ov {p.get("ovside","")}">{p["overlay"]}</div>' if p.get("overlay") else "")
                     + (f'<div class=cap>{p["cap"]}</div>' if p.get("cap") else "")
                     + f'<div class=in-h>{acc(p["title"])}</div><div class=in-p>{acc(p["body"])}</div>'
                     + (f'<div class=teaser>{p["teaser"]}</div>' if p.get("teaser") else "")
                     + footer(b,p["credit"],i,total) + '</div>')
    e = spec["end"]
    endbody = e.get("body2", "")
    cards.append(f'<div class=card><div class=end-bg style="background-image:url({uri(e.get("photo", c["photo"]))})"></div><div class=end-c>'
                 f'<div class=e1>{b["endL1"]}</div><div class=e2>{acc(b["endL2"])}</div>'
                 f'<div class=erow><img src="{uri(b["logoL"])}"><span>{b["name"]}</span></div><div class=esub>{b["sub"]}</div><div class=ediv></div>'
                 f'<div class=ebody>팔로우하고 다음 이야기도 만나보세요.<br>{acc(endbody)}</div><div class=ehandle>{b["handle"]}</div></div>'
                 f'{footer(b,b["handle"],total,total)}</div>')
    os.makedirs(outdir, exist_ok=True)
    page = f"<!doctype html><meta charset=utf-8><style>{css}</style>" + "".join(f'<div id=c{i+1}>{x}</div>' for i,x in enumerate(cards))
    hp = pathlib.Path(outdir)/"cards.html"; hp.write_text(page)
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1024,height:{H}}},deviceScaleFactor:2}});
    await p.goto('file://{hp}');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
    for(let i=1;i<={len(cards)};i++){{await p.locator('#c'+i+' .card').screenshot({{path:'{outdir}/raw-'+i+'.png'}})}}await b.close()}})();"""
    subprocess.run(["node","-e",js],check=True)
    from PIL import Image
    W,HH = (1080,1440) if ratio=="3:4" else (1080,1350)
    outs=[]
    for i in range(1,len(cards)+1):
        im = Image.open(f"{outdir}/raw-{i}.png").convert("RGB").resize((W,HH), Image.LANCZOS)
        o = f"{outdir}/{spec.get('slug','card')}-{i}.jpg"; im.save(o, quality=93); os.remove(f"{outdir}/raw-{i}.png"); outs.append(o)
    return outs
if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); ratio = "3:4" if "--ratio" in sys.argv and sys.argv[sys.argv.index("--ratio")+1]=="3:4" else "4:5"
    print("\n".join(build(spec, os.path.abspath(sys.argv[2]), ratio)))
