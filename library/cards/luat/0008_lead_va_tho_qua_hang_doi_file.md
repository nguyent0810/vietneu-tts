---
{
  "id": "0008_lead_va_tho_qua_hang_doi_file",
  "ten": "Một Lead điều phối nhiều thợ qua hàng đợi file; phản biện từ ngoài chỉ để tham khảo, Lead có quyền phủ quyết bằng số liệu",
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
    "docs/adr/0008-lead-va-tho-qua-hang-doi-file.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "Trạng thái: đã chấp nhận (19–22/10/2026). Hạn mức của nhà cung cấp LLM chính (Claude) có giới hạn, và chủ kênh không muốn ngồi gửi lệnh liên tục. Mặt khác, thợ thường báo \"đạt\" mà sai: 15/16 lỗi tháng 10 đã lọt qua bước tự kiểm của thợ. Các kiểu lỗi: bịa tên file Commons, gõ tay số liệu, báo đã xem ảnh mà không mở ảnh. Mô hình được chọn: - **Lead (Claude).** Viết ticket nhỏ vào `output/cl_staging/grok/queue/*.md`; chọn đề; khoá dữ kiện; render Long; đăng; dọn; viết retro. - **Thợ.** Vòng lặp `loop_v3.sh` giao ticket cho thợ theo thứ tự ưu tiên Agy > Grok > Codex. `worker_status.py` phân biệt ba kiểu hết hạn mức chỉ bằng chữ ký lỗi trong 60 dòng log cuối: - reset: tin vào giờ reset; - hết số ",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `docs/adr/0008-lead-va-tho-qua-hang-doi-file.md:1`. Trạng thái: đã chấp nhận (19–22/10/2026). Hạn mức của nhà cung cấp LLM chính (Claude) có giới hạn, và chủ kênh không muốn ngồi gửi lệnh liên tục. Mặt khác, thợ thường báo "đạt" mà sai: 15/16 lỗi tháng 10 đã lọt qua bước tự kiểm của thợ. Các kiểu lỗi: bịa tên file Commons, gõ tay số liệu, báo đã xem ảnh mà không mở ảnh. Mô hình được chọn: - **Lead (Claude).** Viết ticket nhỏ vào `output/cl_staging/grok/queue/*.md`; chọn đề; khoá dữ kiện; render Long; đăng; dọn; viết retro. - *.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
