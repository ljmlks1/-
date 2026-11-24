# 매일 아침 초안 작성 매뉴얼 (예약 작업이 이 문서를 따른다)

검토함 Artifact = 저장소. 스크립트·가이드는 이 Artifact의 published files, 초안은 db 컬렉션 `drafts`.
**하루 1~2개 (대표님 확정, 2026-11-19부터).** 기본 슬롯 10:30·19:00. 그날 핫이슈가 충분히 강할 때만 2개, 아니면 가장 강한 1개만 쓴다. 이 작업은 08:17 KST쯤 실행되어 **오늘 날짜** 검토본을 만든다.
네이버 자동 발행은 하지 않는다. 대표님이 검토 후 예약발행한다.

## 0. 준비
- Artifact `read`로 파일 받기: `collect.py`, `thumb.js`, `btn.js`, `photo.py`, `build_assets.py`, `contact.py`, `helpers.py`, `realphoto.py`, `STYLE.md`, `RUNBOOK.md`, `cold-verify.md`, `example_drafts.py` → 작업 폴더에 복사.
- **STYLE.md를 끝까지 읽고 그대로 따른다.**

## 1. 수집
`python3 collect.py candidates.json`
- 네이버 뉴스 많이 본 뉴스(언론사별 랭킹) + 섹션 헤드라인(정치·경제·사회·증권·금융·부동산) + 모아픽 RSS/마감임박.
- 출력의 HOT 키워드(전체, 섹션별)를 본다. 에러가 있어도 나머지로 진행하되 초안 `checks`에 적는다.

## 2. 중복·피드백 확인
- ArtifactData `list` 컬렉션 `drafts` → 최근 14일 `keyword`·`title`과 겹치는 주제는 제외.
- `notes`(대표님 수정 요청 메모)가 있으면 오늘 초안에 반영한다. 상태 `보류`인 주제는 피한다.

## 3. 주제 1~2개 고르기 (슬롯별 성격) — 10:30에 아래 1·2행 성격 중 더 강한 것, 19:00에 3행 성격
| 슬롯 | 성격 | 우선 소스 |
|---|---|---|
| 10:30 | 정책자금·지원금·소상공인·청년/신혼 지원 | 모아픽 마감임박·새 가이드 + 뉴스의 지원금 이슈 |
| 15:00 | 주식·금융·대출·금리 | 증권/금융 섹션 + 랭킹 핫키워드 |
| 19:00 | 부동산·청약·세금, 또는 정치·사회 핫이슈의 돈 문제 | 부동산 섹션 + 랭킹 1~10위 이슈 |

선정 기준(높은 순):
1. 랭킹 핫키워드 count가 높고 섹션 헤드라인에도 등장(오늘 가장 많이 검색될 주제)
2. 독자의 돈과 직접 연결(지원금 금액, 세금, 이자, 마감일)
3. 원문 근거(공고문, 기관 공지, 2개 이상 언론)를 확보할 수 있음
4. 최근 14일 미사용
연예·사건 이슈는 STYLE.md 4절처럼 돈·제도 정보로 연결될 때만 쓴다.

## 4. 사실 확인
- 기사 본문: `https://n.news.naver.com/...` (본문 `id="dic_area"`).
- 모아픽 상세: 페이지 내용을 읽고 **원 출처(기관 공고 링크)**까지 따라가서 숫자 확인. 모아픽 문장은 복사하지 않는다.
- 숫자(금액·세율·날짜·전화번호)는 출처 2곳 이상 대조. 못 맞춘 것은 `checks`에 "확인 필요"로 남긴다.

## 5. 초안 작성
- `example_drafts.py`를 복사해 오늘 날짜로 바꾸고 3개 작성(헬퍼 C/QUOTE/SUB/TABLE/BTN/PHOTO/TAGS 사용).
- 각 초안 필드: id(`YYYY-MM-DD_HHMM`), date, slot, account=`ljmlks1`, status=`검토대기`, category, keyword, hot_reason(근거 숫자 포함),
  title, thumb{tag(노란 박스 `분야 / 키워드`),lines[3](`{ }` 연두 강조),icon(사진 없을 때),query(Pexels 영어 검색어),theme}, buttons[], photos[] (헬퍼가 자동 생성), tags(8~12), sources[], checks[](2~4개), body(HTML), created_at, notes="".
- 제목은 STYLE.md 1절 훅 공식(어그로+후킹)을 반드시 쓴다. 블록 사이 빈 줄은 BODY()가 넣는다.
- 본문 길이: 태그 제외 1,800자 이상. 다른 블로그·모아픽 문장 복사 금지.
- theme은 3개가 서로 다르게.

## ★ 냉철 검증 (대표님 확정 2026-11-20, 발행 전 필수)
초안을 db에 저장하기 직전, published file `cold-verify.md`(냉철 검증 스킬)를 읽고 6단계를 스스로 돌린다.
- 아첨 금지: 칭찬 대신 고칠 것만. 모든 숫자·날짜·인용을 [확인된 팩트]/[추측]으로 나누고 확신도 %를 매긴다.
- 확신도 60% 미만 숫자는 본문에서 UNK()로 감싸거나 지운다. 치명적 문제는 직접 고친다.
- `checks` 첫 줄에 판정: "냉철검증: 발행 가능 / 수정 후 발행 / 보류 — 이유".

## 6. 이미지 (썸네일·본문 사진·버튼) — STYLE.md 4-1 사진 원칙 먼저 읽기
- 먼저 realphoto.py로 주제의 실제 인물·기업·장소 사진을 찾고(썸네일 배경 + 중간 사진 2장 이상), 나머지만 photo.py로.
  실제 사진은 out/real/<key>/NN.jpg를 out/photos/<id>_thumb/ 또는 <id>_phN/ 폴더에 09.jpg로 복사하고 pick "09"로 지정. 출처 문구는 본문 끝 C("사진: …") 줄에 모아 쓴다.
- photo.py 검색어는 **사물·장면 영어 1~2단어**(예: `smartphone`, `stock chart`, `credit card`, `soldier`, `apartment building`, `calculator`). 감정 단어를 넣으면 엉뚱한 사진이 섞인다.
- `python3 build_assets.py drafts_<날짜>.json` 실행(사진 후보 8장씩 순서대로 받음: Pexels → 안 되면 CC0 스톡 StockSnap·WordPress).
- `python3 contact.py out/photos/<id>_*` → 각 폴더 `contact.jpg`(번호 붙은 후보 미리보기)를 Read로 **반드시 직접 보고**
  주제에 가장 맞고 사람이 보이면 더 좋은 사진 번호를 `PHOTO(desc, query, "05")`, thumb `"pick": "05"`로 지정한다.
  장난감·엉뚱한 결과뿐이면 검색어를 바꾸거나 다른 폴더의 좋은 후보를 `09.jpg`로 복사해 쓴다.
- 지정 후 build_assets.py를 다시 실행하고, 본문 사진은 1600px로 줄인다(`PIL thumbnail((1600,1600))`, quality 85).
- 완성 썸네일 3장을 한 장으로 붙여 Read로 확인(글자 넘침, 사진이 글씨를 가리지 않는지).

## 7. 업로드
1. Artifact publish `url`=검토함, `asset: true`, `file_paths`=[오늘 id의 out/assets png/jpg 전부(25개 이하씩)] → 각 `url`.
2. 초안에 `thumb_url`, `photos[n].url`, `buttons[n].img_url` 채우기.
3. checks에 "사진은 CC0 무료 스톡: 상업 이용 가능, 출처 표기 불필요"(Pexels면 "Pexels 무료 사진") 추가.
4. ArtifactData `batch`로 `drafts/<id>` `set`. 같은 id가 이미 있으면 건너뛴다(대표님이 손댄 상태 보존).

## 7-1. 보물상(bomulsang777)은 별도 검토함·별도 매뉴얼(RUNBOOK_BOMUL.md)로 분리됨 — 이 작업에서는 쓰지 않는다.

## 7-2. 비축 글 (과학·IT·우주·기업가) — 1번 계정, 하루 2~3개, 발행 시간 없음
- 별도 예약 작업(오후)이 쓴다. 대표님이 쌓인 글을 한 번에 몰아서 올린다.
- 소스: collect.py 섹션 `IT/과학`, `과학 일반`, `IT 일반`, `모바일·빅테크` + 랭킹의 IT·기업가 키워드. **최근 24시간 이내 최신 뉴스만.**
- 주제 예: 빅테크 CEO 이슈(젠슨 황, 머스크, 올트먼), AI·반도체, 대형 IT 장애, 우주 발사·탐사, 신기한 과학 연구.
- 돈 연결이 없어도 된다. 대신 훅은 더 강하게("○○이 무너졌다?", "이게 실화?", "인류 최초").
- id=`YYYY-MM-DD_X1`, `_X2`, `_X3`(X=비축), slot=`비축`, date=작성일, category=`과학·IT`, status=`검토대기`.
- 사진은 4-1 원칙대로 실제 인물·NASA 사진 우선. 썸네일 tag 예: `IT / 마이크로소프트`, `우주 / 스페이스X`.
- 이미 비축된 글과 같은 주제는 쓰지 않는다(drafts에서 slot=비축 목록 확인).

## 8. 마무리 보고
마지막 메시지(푸시 알림으로 감): "시베리안종베 오늘 초안 3개 준비 완료" + "비축 글 미발행 N개" + 슬롯별 제목 3줄 + 확인 필요 항목 개수 + 검토함 링크.
