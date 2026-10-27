---
{
  "id": "0009_nhip_hinh_la_diem_kiem_truoc_render",
  "ten": "Nhịp hình được kiểm trước khi render: phần chặn cứng giữ nhỏ, các sàn chỉ cảnh báo",
  "loai": "luat",
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
    "docs/adr/0009-nhip-hinh-la-diem-kiem-truoc-render.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "Trạng thái: đã chấp nhận (01/10/2026, bổ sung 21/10 và 24/10). Ngày 01/10 đo hai Long F1 và B1: - 68% thời lượng là ba loại sơ đồ lặp đi lặp lại; - 35% là thẻ chữ khoá trên nền trơn; - có cảnh đứng yên 64 giây. Ngày 19/10, tt03 chỉ có 36 ảnh/clip cho 758 câu nên phải dừng render và làm lại. Nếu chỉ soát bằng mắt sau khi render xong, mỗi vòng sửa tốn khoảng 1,7 lần thời lượng video. `hf_batch_render.pacing()` chạy trên spec dựng cộng mốc giây của TTS, trước khi render hình:",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `docs/adr/0009-nhip-hinh-la-diem-kiem-truoc-render.md:1`. Trạng thái: đã chấp nhận (01/10/2026, bổ sung 21/10 và 24/10). Ngày 01/10 đo hai Long F1 và B1: - 68% thời lượng là ba loại sơ đồ lặp đi lặp lại; - 35% là thẻ chữ khoá trên nền trơn; - có cảnh đứng yên 64 giây. Ngày 19/10, tt03 chỉ có 36 ảnh/clip cho 758 câu nên phải dừng render và làm lại. Nếu chỉ soát bằng mắt sau khi render xong, mỗi vòng sửa tốn khoảng 1,7 lần thời lượng video. `hf_batch_render.pacing()` chạy trên spec dựng cộng mốc giây của TTS, trước khi render hình:.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
