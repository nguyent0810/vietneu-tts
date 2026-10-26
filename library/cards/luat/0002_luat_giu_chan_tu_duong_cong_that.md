---
{
  "id": "0002_luat_giu_chan_tu_duong_cong_that",
  "ten": "Luật viết kịch bản Long lấy từ đường giữ chân thật của kênh, mã hoá thành lint và một điểm duyệt kịch bản",
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
    "docs/adr/0002-luat-giu-chan-tu-duong-cong-that.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "Trạng thái: đã chấp nhận (14–21/10/2026). Trước đây kịch bản Long theo một checklist chữ chung (mượn từ kênh khác), và checklist này hay bị bỏ qua. Ngày 14/10 ta ghép `audienceWatchRatio` của 6 Long (B3, B5, F1, F3, F4, F6) với câu đang đọc ở từng giây. Những chỗ rơi dốc nhất trùng với các kiểu câu lặp lại được: - câu nói về chính video (\"Video này sẽ…\"): B5 mất 25 điểm ở giây 18–37; - chương định nghĩa đặt trước phần trả lời: F6 mất 52 điểm ở giây 21–42, đúng lúc vào \"lục thập hoa giáp\"; - câu dồn 5 năm sinh liền nhau, dài 40–44 tiếng đọc: F6 rơi 7 điểm; - câu kết \"Tóm lại\", hoặc đọc to bảng tổng hợp: F4 mất 31% trong 50 giây. Ta biến các chỗ rơi này thành 10 luật đầu skill `long-script`, r",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `docs/adr/0002-luat-giu-chan-tu-duong-cong-that.md:1`. Trạng thái: đã chấp nhận (14–21/10/2026). Trước đây kịch bản Long theo một checklist chữ chung (mượn từ kênh khác), và checklist này hay bị bỏ qua. Ngày 14/10 ta ghép `audienceWatchRatio` của 6 Long (B3, B5, F1, F3, F4, F6) với câu đang đọc ở từng giây. Những chỗ rơi dốc nhất trùng với các kiểu câu lặp lại được: - câu nói về chính video ("Video này sẽ…"): B5 mất 25 điểm ở giây 18–37; - chương định nghĩa đặt trước phần trả lời: F6 mất 52 điểm ở giây 21–42, đúng lúc vào "lục th.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
