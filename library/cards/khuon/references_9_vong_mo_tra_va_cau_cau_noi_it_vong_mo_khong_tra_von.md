---
{
  "id": "references_9_vong_mo_tra_va_cau_cau_noi_it_vong_mo_khong_tra_von",
  "ten": "9. Vòng mở / trả và câu cầu nối (it_vong_mo, khong_tra_vong, thieu_rehook, ket_chuong_tom_tat, chuong_mo_khong_moc, vong_khong_dong)",
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
    ".claude/skills/long-script/references/line-rules.md:88"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "Lint nhận diện vòng bằng cụm từ; viết rõ để người nghe (và lint) nghe ra: - Mở: \"lát nữa\", \"ở cuối video\", \"ta sẽ quay lại...\", \"hãy giữ câu hỏi này\", \"còn một điều\", \"nhưng đó chưa phải tất cả\", \"câu hỏi thứ hai\". - Trả: \"còn nhớ...\", \"hãy quay lại đêm ấy\", \"câu trả lời là...\", \"đó là lý do...\", \"giờ thì bạn đã hiểu...\". - Chương mở có một câu hỏi hoặc một câu móc (`chuong_mo_khong_moc`). - Kết chương = câu cầu nối mở sang chương sau. Câu kết không bắt đầu bằng \"Tóm lại\" hoặc \"Như vậy\" (`ket_chuong_tom_tat`; F4, F1 rơi 29-31% ở chương cuối kiểu đó). - Plan có trường `vong` thì mỗi vòng cần cụm `dong` có thật trong lời sau chương mở (`vong_khong_dong`). - Trả một vòng thì câu kế tiếp mở vòng",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/long-script/references/line-rules.md:88`. Lint nhận diện vòng bằng cụm từ; viết rõ để người nghe (và lint) nghe ra: - Mở: "lát nữa", "ở cuối video", "ta sẽ quay lại...", "hãy giữ câu hỏi này", "còn một điều", "nhưng đó chưa phải tất cả", "câu hỏi thứ hai". - Trả: "còn nhớ...", "hãy quay lại đêm ấy", "câu trả lời là...", "đó là lý do...", "giờ thì bạn đã hiểu...". - Chương mở có một câu hỏi hoặc một câu móc (`chuong_mo_khong_moc`). - Kết chương = câu cầu nối mở sang chương sau. Câu kết không bắt đầu bằng "Tóm lại" hoặ.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
