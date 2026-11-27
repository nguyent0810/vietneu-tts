# Khuôn prompt Gemini viết lời Long — v3 (dùng chung 5 kênh: FS, BUD, CL, MIM, CK)

Chủ kênh chốt ngày 27/11/2026, sau khi thử thật trên Long FS 1982 và 1997.

## Vì sao đổi
Khuôn cũ có nhiều luật: khối "KỂ CHO TAI", giọng mẫu, chỉ dẫn chi tiết và đích số chữ. Kết quả là Gemini viết cứng và chen câu cảnh vô nghĩa, kiểu "ngoài hành lang chung cư, tiếng thang máy…". Khi bỏ bớt luật, hành văn tự nhiên và hay hơn hẳn.

## Dùng
1. Chọn loại:
   - `khuon_long_vua.md` (khoảng 9–15 phút): thay Long ngắn 6–7 phút.
   - `khuon_long_dai.md` (≥ 30 phút): nhiều hồi, viết nhiều lượt trong cùng một chat.
2. Điền `{KENH_LUAT}`, `{GIONG}` từ `kenh_luat.md`. Chọn **một** cách triển khai trong `cach_trien_khai.md` hoặc danh sách riêng của kênh. Bài liền kề không trùng cách. `CHUONG` cũng là một lựa chọn.
3. `{DU_KIEN}`: dán thẳng dữ kiện, xoá tên file và tên ticket, vì Gemini web không đọc được file.
4. Long dài: `{DAN_HOI}` là dàn hồi **gợi ý** do Lead dựng, mỗi hồi 3–4 dòng. Gemini được phép đổi thứ tự, gộp hoặc thêm hồi.
5. Gửi bằng `creator_v2/scripts/gemini_chat.py ask <prompt> --out <file>`. Long dài thì dùng thêm `--chat <link>` cho các lượt viết tiếp.
6. Biên tập theo `bien_tap.md`: **chỉ sửa thông tin cần chính xác**, không cắt xén. Độ dài theo chất liệu, không khoá cứng.

## Tinh thần
- Ít luật. Khuôn chỉ giữ luật bắt buộc tối thiểu của kênh; luật an toàn kiểm ở khâu biên tập.
- Có kịch tính: cái giá, sóng lên xuống, đỉnh ở khoảng 3/4 bài, lặng sau đỉnh.
- Không nói về chính video. Lời rào đón chỉ nói một lần, lồng vào câu chuyện.
- `nghien_cuu.md`: kỹ thuật mở đầu, hook, reward, nối mạch, kèm ví dụ và nguồn.
