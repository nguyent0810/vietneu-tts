# Kể chuyện trung thành nguồn (Tiền Thân, sử, nhân vật minh hoạ)

Nguồn/quyền kể theo [lõi §6](../../../../docs/script/audio-script.md#6-sự-thật-diễn-giải-và-phỏng-dựng) và [BUD](../../../../docs/script/profiles/bud.md). Không thêm luật phỏng dựng từ reference này. Giữ PO16/11 kể cho tai, nhãn theo adapter; ranh giới truyện kinh/lời Phật theo hồ sơ BUD và luật19.

## 1. Tra nguồn theo loại
Pali/kệ: `.venv/bin/python hf_sutta.py <uid> "<cụm>"`, Jātaka `ja<N>` (chỉ kệ). Văn xuôi: Cowell PD trong `output/cl_staging/long/research/jataka_cowell/`, bản Việt đối chiếu không chép. Sử: sách gốc như Toàn thư/Thánh đăng ngữ lục, ghi nguồn. Dân gian/truyền thuyết: ghi dị bản đã chọn và khung lời. Nhân vật minh hoạ hiện đại ghi rõ trong `seo.summary`, không lẫn nhân vật của kinh.

## 2. Gợi ý kể
Có thể chọn cảnh, nhịp, lời người kể, câu nối đời nay để giữ mạch. Bớt câu xin phép/rào nguồn lặp; giữ nhãn đúng workflow. Bản cũ “tối đa một phỏng đoán/truyện” và mặc định cho thêm gió/đêm vào truyện kinh đã bỏ; lý do [X10/X18](../../../../docs/script/conflicts-075b.md). Không biến các gợi ý này thành lint.

## 3. Mẫu một truyện (6-9 phút, ngân sách theo bảng giọng)
1. **Móc ở khủng hoảng** (3-5 câu): một cảnh cụ thể ngay trước lựa chọn; câu hỏi chưa trả. Không nêu bài học.
2. **Chuyện hiện tại** (3-6 câu): ai, ở đâu, vì sao Đức Phật kể -- nối với một câu hỏi đời thường ("Bạn đã bao giờ...").
3. **Bối cảnh quá khứ** (4-8 câu): "Thuở xưa, khi vua Phạm Dự trị vì ở Ba La Nại..." — chọn chi tiết có nghĩa theo hồ sơ.
4. **Leo thang** (8-15 câu): hai lựa chọn, hai nhân vật đối chiếu (người khôn / kẻ vội); thoại mỗi lượt một dòng (line-rules §5).
5. **Đỉnh + lặng**: câu ngắn ≤ 6 tiếng, `pause` 1,0-1,4, `tempo` 0,85-0,88; có thể `SILENCE`.
6. **Kệ** (≤ 2 câu diễn ý, `alt=True`, đã đối chiếu `ja<N>`).
7. **Nhận diện** (1-2 câu): "Người lái buôn khôn ngoan ấy, chính là Bồ Tát" -- cú lật, không nói trước.
8. **Bài học hôm nay** (1-2 câu, cụ thể, có một việc làm được) + **câu cầu nối** mở truyện sau. Không "Tóm lại".

## 4. Soát truyện trước khi giao
- Đặt cốt truyện nguồn cạnh beat sheet; đối chiếu sự thật, tách lời người kể/phỏng dựng theo hồ sơ.
- Tìm trong kịch bản các câu có "nói", "dạy", "thưa", "nghĩ" → đối chiếu câu chạm tư liệu; nhãn theo hồ sơ, không bắt thêm cho mọi câu giọng kể.
- Số (năm trăm cỗ xe, sáu mươi do tuần...) đúng nguồn; đổi đơn vị cổ ra cách hiểu nay thì nói "khoảng".
- Ví dụ thật đã bắt được: b45_b viết "tự bắn mũi tên thứ hai" trong khi SN 36.6 là "bị trúng mũi tên thứ hai" (long-video §3).
