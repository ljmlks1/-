# Codex 지시문에 추가할 내용 (복사해서 붙여넣기)

【Claude 연동 · 게시 이관】
제작한 캐러셀은 직접 게시하지 말고 vidIQ 초안으로 넘긴다. 순서는 다음과 같다.
1. 이미지를 vidiq_upload_image로 올린다.
2. vidiq_social_post_draft_create로 초안을 만든다. destinations에는 해당 채널 1개만 넣는다.
   - issue.ap: 29314331491559156
   - legendhumormeme: 29028458450154197
3. publishAt을 반드시 넣는다(희망 게시 시각, 미래 시각). 날짜가 없는 초안은 Claude가 찾지 못한다.
4. 사실 확인과 사진 사용 근거 확인이 끝난 최종본만 초안으로 만든다. 보류 항목은 초안을 만들지 않는다.
5. 수정할 때는 새 초안을 만들지 말고 vidiq_social_post_draft_update로 같은 postId를 고친다.
6. Claude가 사용자 컨펌을 받아 vidiq_social_post_publish로 게시한다. Codex는 같은 글을 게시하지 않는다.
   단, Claude를 쓸 수 없을 때는 Codex가 같은 규칙(컨펌된 정확한 revision만, 채널별 4시간 간격, 1건씩)으로 게시해도 된다.
