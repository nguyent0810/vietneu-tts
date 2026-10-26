---
{
  "id": "references_quy_trinh_ao_dien_rut_tu_research_a_so_lieu_kenh",
  "ten": "Quy trình đạo diễn (rút từ research A + số liệu kênh)",
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
    ".claude/skills/shorts-studio/references/pipeline.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "mo_ta_nguon": "| Bước | Sản phẩm | Ai | Cổng | |---|---|---|---| | 1 Brief | kênh, khán giả, câu hỏi chính, nguồn số liệu, luật kênh | agent | số liệu kiểm bằng code / nguồn | | 2 Kịch bản | 6-8 câu (`lines`) | agent | câu 1 <= 10 chữ + trả lời; câu 2 cụ thể; <= 3 tên chi/câu (FS); không câu > 35 âm tiết | | 3 Beat sheet | mục đích từng câu + năng lượng | agent | có hook, có nhịp tĩnh trước payoff, có close | | 4 Kế hoạch thiết bị | `scenes[]` | agent | luật đa dạng (studio.py) | | 5 Dựng | job + mp4 | studio.py | lint 0 lỗi, check ok | | 6 Soát mắt | qa_sheet.jpg | agent | khung 0, mỗi cảnh, seam, dấu tiếng Việt, vùng an toàn | | 7 Duyệt | gửi người dùng khi là thiết kế/thiết bị mới | người dùng | — | | 8",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---

## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/shorts-studio/references/pipeline.md:1`. | Bước | Sản phẩm | Ai | Cổng | |---|---|---|---| | 1 Brief | kênh, khán giả, câu hỏi chính, nguồn số liệu, luật kênh | agent | số liệu kiểm bằng code / nguồn | | 2 Kịch bản | 6-8 câu (`lines`) | agent | câu 1 <= 10 chữ + trả lời; câu 2 cụ thể; <= 3 tên chi/câu (FS); không câu > 35 âm tiết | | 3 Beat sheet | mục đích từng câu + năng lượng | agent | có hook, có nhịp tĩnh trước payoff, có close | | 4 Kế hoạch thiết bị | `scenes[]` | agent | luật đa dạng (studio.py) | | 5 Dựng |.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
