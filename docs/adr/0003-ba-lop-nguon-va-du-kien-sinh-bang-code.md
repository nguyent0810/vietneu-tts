# Mọi dữ kiện có mã và nhãn lớp nguồn; số liệu sinh bằng code; lời kinh đối chiếu bằng công cụ; bộ kiểm độc lập do Lead giữ

Trạng thái: đã chấp nhận (04–23/10/2026).

Kênh tôn giáo và phong thủy sống bằng lòng tin: một câu "kinh nói" sai, hay một ngày tốt tính sai, đủ để người xem bỏ kênh. Tháng 10 bắt được một loạt lỗi cùng kiểu:

- 04/10: short b45_b viết "tự bắn mũi tên thứ hai", trong khi kinh SN 36.6 nói "bị trúng".
- 20/10: thợ gán cho kinh những điều kinh không nói ("Địa Tạng ngày 27", "không dính bùn", "bốn màu sen").
- 20/10: ngày Tam Nương 31/10 lại ghi "NÊN: Đính hôn".
- 21/10: truyện Cakkhupāla bị thêm "đêm mưa gió, máu ứa, thuốc độc".
- Bài tv04 ghi tay "Thái Bạch" thay cho La Hầu.
- 23/10: Lead đọc nguyên văn MN 86 và *Nam Hải dị nhân*, bắt được 15 chỗ kể thêm ngoài nguồn.

Ta quyết định như sau.

- **Gói nguồn trước kịch bản.** Mỗi dữ kiện có mã (`K20`, `C07`, `D04`…) và nhãn lớp: kinh/luật, chú giải, truyền thống, truyền thuyết, sử, dân gian, code. Kịch bản ghi mã dữ kiện cuối mỗi câu. Câu không có trong gói thì bỏ.
- **Ba lớp kể phải nói rõ trên lời đọc**: kinh/luật, chú giải kể, truyện đời sau. Ví dụ "đất nuốt Đề Bà Đạt Đa" là chú giải, không phải kinh.
- **Lời Phật** chỉ dùng khi đã đối chiếu bằng `hf_sutta.py <uid> "<cụm>"` (bản Sujato/Brahmali). **Lời quẻ** chỉ lấy từ `hf_kinhdich.py`.
- **Số FS** (can chi, nạp âm, sao hạn, ngày tốt) sinh bằng code (`canchi.py`, `amlich.py`, `tuvi_year.py`) rồi đưa vào lời bằng f-string. Không gõ tay.
- **Hoàng đạo** phải qua cả bộ sinh lẫn bộ kiểm độc lập `tools/hoangdao_indep_check.py` (tính lại từ ngày Julian và trăng mới). Thợ không được sửa bộ kiểm này.
- **Truyện kinh không thêm chi tiết**; biểu tượng đời sau ghi "theo cách giải thích phổ biến".

## Các phương án đã cân nhắc

- **Để thợ tự kiểm.** Lệnh `--check` của thợ dùng chung code với bộ sinh nên không bắt được lỗi logic, chỉ bắt lỗi định dạng.
- **Dùng thư viện âm lịch có sẵn để tính trực/thần/nạp âm.** Tính sai, nên loại.
- **Tin tóm tắt nguồn của thợ.** Bị loại sau các vụ bịa chi tiết và bịa tên file ảnh.

## Hệ quả

- Viết chậm hơn, nhiều câu hay bị bỏ vì không có nguồn.
- Kinh Dịch tạm giới hạn ở 9/64 quẻ đã có lời dịch kiểm được. Nội dung Bắc tông phải trích nguyên văn có nguồn.
- Ghi công ảnh Commons lấy từ API lúc dựng, không lấy từ kho đã lưu, vì kho từng ghi sai tác giả.
- Trong sổ lỗi `defects.jsonl`, khâu "nguồn" chiếm 6/23 lỗi. Đây là khâu lỗi nhiều nhất.

## Bằng chứng

`output/cl_staging/grok/rules.md` luật 5, 9, 12–14, 19; `output/cl_staging/retro/2026-10-19_dot1.md`, `2026-10-20_hoangdao_29-10.md`, `2026-10-23_long_pilot.md`; `output/cl_staging/long/research/de_ba_dat_da_pack.json` (mẫu gói nguồn 70 dữ kiện).
