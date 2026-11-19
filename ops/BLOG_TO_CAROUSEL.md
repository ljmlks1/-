# 블로그최종 → 캐러셀 변환 규칙 (2026-11-19 사용자 지시)

- 원천: claude.ai 아티팩트 '블로그최종'(시베리안종베 검토함) https://claude.ai/artifact/9A9TkJDELb6dCCz8QrWCgm
  - ArtifactData list, collection `drafts` (문서 id 예: 2026-11-19_1030, _1500, _1900, _F1, _X1…)
  - 필드: title, body(HTML), photos[{desc,url=/_blob/<id>,credit}], tags, sources, category, date, slot, status
- 매 회차: 아직 캐러셀로 만들지 않은 블로그 초안(ledger의 blog_id로 판별)을 찾아 **블로그 내용을 그대로** 캐러셀로 변환
  - 사실·수치·순서·주의 문구는 블로그 본문을 따른다(블로그 sources가 근거). 줄이기만 하고 새 주장 추가 금지
  - 장수: 표지 + 본문 6장 + 엔딩 = 8장 (블로그 소제목 순서대로)
  - 사진: 블로그 사진은 550px라 저화질 → 같은 주제의 고화질 사진(Pexels find_broll / 위키미디어)로 장마다 다르게
  - 계정: 재미·화제 중 연예/유머 성격 → @legendhumormeme, 그 외(과학·IT·경제·금융·사회·정책) → @issue.ap
  - 본문(캡션): 블로그 요약 + 질문 + 해시태그 5개, 출처 URL은 캡션에 넣지 않고 ops/evidence에 기록
- 같은 주제 충돌: 내가 네이버 랭킹에서 고른 소재와 블로그 주제가 같으면 둘 중 더 좋은(사실 풍부·최신·사진 좋은) 쪽 하나만 전달하고, 다른 쪽은 ledger에 superseded로 기록
- 게시는 사용자가 직접(또는 사용자가 명시 승인한 정확한 버전만 vidIQ로)
