---
{
  "id": "0007_dang_rieng_tu_hen_gio_dem_theo_id",
  "ten": "Luôn đăng ở chế độ riêng tư kèm hẹn giờ; đếm lịch theo ID video chứ không theo playlist; mỗi kênh tối đa 24 upload trong 24 giờ",
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
    "docs/adr/0007-dang-rieng-tu-hen-gio-dem-theo-id.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "Trạng thái: đã chấp nhận (20/10/2026). Đăng công khai ngay thì mất cơ hội soát lại và không gỡ êm được. Ta cũng từng đếm sai lịch vì tin playlist \"uploads\": - Playlist bỏ sót video riêng tư có `publishAt`. Ngày 28/09 sót 256 video. Ngày 20/10, Lead báo kênh có \"0 video đã hẹn\" trong khi thực tế là 71. - Playlist xê dịch ngay sau mỗi lần đăng, nên vừa đếm lặp vừa đếm sót. - Thông báo \"HẾT QUOTA\" ngày 20/10 thực ra là `UploadPacingHold`: trần tự đặt 24 upload trong 24 giờ cho mỗi kênh trong `youtube_upload.py`, không phải quota của API. Quyết định: - Mọi uploader mặc định chạy thử (dry-run); phải có `--confirm` mới đăng thật.",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `docs/adr/0007-dang-rieng-tu-hen-gio-dem-theo-id.md:1`. Trạng thái: đã chấp nhận (20/10/2026). Đăng công khai ngay thì mất cơ hội soát lại và không gỡ êm được. Ta cũng từng đếm sai lịch vì tin playlist "uploads": - Playlist bỏ sót video riêng tư có `publishAt`. Ngày 28/09 sót 256 video. Ngày 20/10, Lead báo kênh có "0 video đã hẹn" trong khi thực tế là 71. - Playlist xê dịch ngay sau mỗi lần đăng, nên vừa đếm lặp vừa đếm sót. - Thông báo "HẾT QUOTA" ngày 20/10 thực ra là `UploadPacingHold`: trần tự đặt 24 upload trong 24 giờ cho m.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
