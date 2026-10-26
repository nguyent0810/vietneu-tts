---
{
  "id": "long_video_4_plan_mot_phan_tu_trong_plan_long_w40_json",
  "ten": "4. Plan (một phần tử trong `plan_long_w40.json`)",
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
    ".claude/skills/long-video/SKILL.md:90"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "mo_ta_nguon": "`id, day, slot (UTC, \"13:00\" = 20:00 VN), style (laban_long | inkwash_long), series (bud|fs), lane: \"long\", title, tags, script[], media{}, visuals{}, figures{} (mọi câu type none), thumbnail, playlists[{title, description?}], hold?` — cú pháp `visuals`/`media`: skill `motion-library`. Ảnh không ghi `layout` → bridge tự luân phiên bố cục. - Cảnh giữ hình > 25 giây bị runner chặn (pacing) trừ khi plan ghi lý do: `\"slow_hold\": {\"<câu đầu cảnh>\": \"đọc nguyên văn bia\"}` (ticket 65, 24/10/2026). Runner in thêm p50/p90 giây/cảnh và nhịp phút đầu/phút cuối (mục tiêu 2–4 giây, cảnh báo). - Ảnh/clip AI đã tải về: `{\"kind\": \"local\", \"path\": \"output/cl_staging/long/research/ai_media/...\"}`. Ảnh dọc (ch",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---

## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/long-video/SKILL.md:90`. `id, day, slot (UTC, "13:00" = 20:00 VN), style (laban_long | inkwash_long), series (bud|fs), lane: "long", title, tags, script[], media{}, visuals{}, figures{} (mọi câu type none), thumbnail, playlists[{title, description?}], hold?` — cú pháp `visuals`/`media`: skill `motion-library`. Ảnh không ghi `layout` → bridge tự luân phiên bố cục. - Cảnh giữ hình > 25 giây bị runner chặn (pacing) trừ khi plan ghi lý do: `"slow_hold": {"<câu đầu cảnh>": "đọc nguyên văn bia"}` (ticket 6.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
