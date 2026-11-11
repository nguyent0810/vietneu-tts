# GH-248 — Báo cáo 12 spec series CL

12 spec mới trong `data/stier/specs/`. `publish_at` để trống. Không render, không enqueue, không commit, không đổi nhánh, không sửa spec cũ.

Preflight, không `--allow-hook`:

`PYTHONIOENCODING=utf-8 .venv\Scripts\python.exe motion/stier/build.py --preflight <slug>`

Cả 12 bài in `OK`. Preflight cảnh báo ảnh chưa có trong cache nên không tự đo độ sáng. Giấy phép và độ sáng đã kiểm trên thumbnail Commons: Public domain hoặc CC0, luma trung bình từ 101 trở lên. Mỗi bài 4 ảnh, không trùng nhau và không trùng file đã có trong spec cũ. Grep 12 file mới không thấy dấu `?`.

Series B để sau ngày 22/11, nhưng ngày đăng vẫn để Lead điền.

| Slug | Series | Tiêu đề | lines[0] | Ảnh cảnh 0 | Nguồn chính | Preflight |
|---|---|---|---|---|---|---|
| cl-bao-s2-loi-cam | A · Hồ sơ Bao Chửng | 1 lời cấm: Bao Chửng không cho con cháu tham ô về | Bao Chửng cấm con cháu tham ô về nhà. | File:Stele at Bao Zheng's Tomb (9974351526).jpg | Tống sử, quyển 316 | OK — 119 từ, 36.1s |
| cl-bao-s2-song-hue-dan | A · Hồ sơ Bao Chửng | 1057: Bao Chửng phá vườn nhà quyền lấn sông Huệ Dân | Bao Chửng phá vườn nhà quyền giữa trận lũ. | File:Qingming shanghe tu bridge.jpg | Tống sử, quyển 316; Wikipedia tiếng Trung, Bao Chửng | OK — 115 từ, 34.8s |
| cl-bao-s2-au-duong-tu | A · Hồ sơ Bao Chửng | 2 lần hặc: Âu Dương Tu chê Bao Chửng chiếm ghế | Bao Chửng hặc hai người rồi ngồi ghế ấy. | File:Ouyang Xiu.jpg | Tống sử, quyển 316 | OK — 103 từ, 31.2s |
| cl-dong-lang-min-1928 | B · Hồ sơ Đông Lăng | 1928: Tôn Điện Anh nổ mìn lăng, không ai bị án | Tôn Điện Anh nổ mìn, không ai bị án. | File:Plan of Consorts Tomb of Yuling of the Qing Dynasty.png | Wikipedia — Sun Dianying; Eastern Qing tombs | OK — 131 từ, 39.7s |
| cl-dong-lang-da-min-chau | B · Hồ sơ Đông Lăng | 133 gam: Dạ Minh Châu của Từ Hi không có giấy tờ | Một trăm ba mươi ba gam, không giấy tờ. | File:Bottle with dragon chasing a flaming pearl, China, Jingdezhen, Jiangxi province, Qing dynasty, Kangxi emperor, porcelain with underglaze red decoration - Asian Art Museum of San Francisco - DSC01404.JPG | Wikipedia — Sun Dianying; Empress Dowager Cixi; Soong Mei-ling | OK — 132 từ, 40.0s |
| cl-dong-lang-tu-1947 | B · Hồ sơ Đông Lăng | 1947: Tôn Điện Anh chết trong tù, không có án lăng | Tôn Điện Anh chết trong tù, không có án. | File:Covered ewer with figures in a landscape, China, Qing dynasty, metal core with black lacquer and mother-of-pearl inlays - Asian Art Museum of San Francisco - DSC01628.JPG | Wikipedia — Sun Dianying | OK — 118 từ, 35.8s |
| cl-a-nezumi-1831 | C · Vụ án châu Á | Hơn 100 phủ: Nezumi khai trộm mà túi gần rỗng | Nezumi khai hơn một trăm vụ, túi gần rỗng. | File:Kodanji Ichikawa IV as Nezumi-kozō Jirokichi.jpg | Wikipedia — Nezumi Kozō | OK — 124 từ, 37.6s |
| cl-a-oppert-1868 | C · Vụ án châu Á | 1868: Oppert đào mộ cha nhiếp chính, về tay không | Oppert chạm bia đá rồi về tay không. | File:Ernst Oppert 1895.jpg | Wikipedia — Ernst Oppert | OK — 127 từ, 38.5s |
| cl-a-vien-minh-vien-1860 | C · Vụ án châu Á | 1860: Viên Minh Viên sạch đồ chỉ sau vài ngày | Viên Minh Viên sạch đồ chỉ sau vài ngày. | File:Felice Beato (British, born Italy) - (Imperial Summer Palace before the of Burning Yuan Ming Yuan, October 18, 1860) - Google Art Project.jpg | Wikipedia — Old Summer Palace | OK — 102 từ, 30.9s |
| cl-a-phaulkon-1688 | C · Vụ án châu Á | 1688: Phaulkon bị kết tội phản lúc vua Narai hấp hối | Phaulkon giữ triều Xiêm, rồi bị kết tội phản. | File:Constantine Phaulkon Portrait Engraving.png | Wikipedia — Constantine Phaulkon | OK — 105 từ, 31.8s |
| cl-a-manila-1762 | C · Vụ án châu Á | 4 triệu bạc: Manila chịu chuộc thành, chỉ nộp một phần tư | Manila chịu bốn triệu, chỉ nộp một phần tư. | File:The Attack of Manilla, October 1762.png | Wikipedia — British occupation of Manila | OK — 100 từ, 30.3s |
| cl-a-mayrena-1888 | C · Vụ án châu Á | 1888: Mayréna tự xưng vua Xơ Đăng giữa đất Pháp | Mayréna đi đàm phán, rồi tự xưng vua. | File:David de Mayrena, Auguste Jean Baptiste Marie Charles.jpg | Wikipedia — Marie-Charles David de Mayréna; Kingdom of Sedang | OK — 124 từ, 37.6s |

Ghi chú cho Lead khi dựng:

- Series A và B có nhãn `HỒ SƠ BAO CHỬNG · n/3` hoặc `HỒ SƠ ĐÔNG LĂNG · n/3` trên cảnh 0. Câu cuối mời bản dài, không có lời kêu gọi đăng ký.
- Năm 1057 trên phim sông Huệ Dân là năm Bao nhận phủ Khai Phong. Tống sử không ghi ngày trận lũ.
- Ảnh Đông Lăng là sơ đồ viên tẩm phi tần Dụ Lăng và đồ bảo tàng đời Thanh. Lời đọc nói rõ đó không phải địa cung bị nổ và không phải đồ lấy từ lăng. 133 gam, 4,5 cm và giá bạc là ước tính thứ cấp. Không có giấy tờ cùng thời ghi Tống Mỹ Linh nhận ngọc.
- Tranh Nezumi là vai kabuki năm 1857, kèm tranh và bản đồ Edo. Phim dừng ở bản án tử, không kể cách thi hành.
- Ảnh Oppert chụp năm 1895. Ảnh Phaulkon là bản khắc. Ảnh Beato chụp Viên Minh Viên trước ngày đốt. Xơ Đăng là ngôi tự xưng.
