---
{
  "id": "references_visual_studio_mot_thiet_bi_cho_mot_cau_hoac_nhieu_cau",
  "ten": "Visual `studio` = một thiết bị cho một câu (hoặc nhiều câu với `until`)",
  "loai": "khuon",
  "dinh_dang": [],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [],
  "cam_ngach": [],
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [],
  "bang_chung_dung": [],
  "vi_du": [],
  "nguon_su_that": [
    ".claude/skills/shorts-studio/references/long.md:18"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "```json \"visuals\": { \"12\": { \"type\": \"studio\", \"device\": \"ledger\", \"until\": 14, \"title\": \"...\", \"rows\": [ { \"y\": \"1990\", \"value\": 38, \"at\": \"@1990\" }, { \"y\": \"2002\", \"value\": 26, \"at\": { \"at\": 13, \"word\": \"2002\" } } ] } } ``` - Trường giống hệt spec short (`references/devices.md`), riêng **mốc**: - `\"@từ\"` = lúc giọng đọc tới từ đó trong CHÍNH câu gắn thiết bị; - `{\"at\": n, \"word\": \"từ\", \"offset\": giây}` = câu n (số câu toàn video, bridge tự đổi sang câu trong chương). - Mốc phải nằm trong khoảng câu `n..until` (bridge kiểm như sơ đồ thường). - Thiết bị vẽ bằng `cssW` (khổ ngang): vùng nội dung x 150..1770, y 120..850; dưới là dải phụ đề (đừng đặt chữ y > 860). Toạ độ do spec đưa (vd `stamps",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/shorts-studio/references/long.md:18`. ```json "visuals": { "12": { "type": "studio", "device": "ledger", "until": 14, "title": "...", "rows": [ { "y": "1990", "value": 38, "at": "@1990" }, { "y": "2002", "value": 26, "at": { "at": 13, "word": "2002" } } ] } } ``` - Trường giống hệt spec short (`references/devices.md`), riêng **mốc**: - `"@từ"` = lúc giọng đọc tới từ đó trong CHÍNH câu gắn thiết bị; - `{"at": n, "word": "từ", "offset": giây}` = câu n (số câu toàn video, bridge tự đổi sang câu trong chương). - Mốc.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
