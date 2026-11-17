# Ma trận engine — 075b

Chỉ mã HBR/Long lint/hook library/shortbuild được sửa theo task. Không sửa V2 stier (AGENTS yêu cầu ticket chỉ rõ từng file), pace_gate, hf_qa hay bộ kiểm độc lập. Danh mục10 nhóm audio ở lõi §9 có phạm vi HBR/shortbuild, **không phải tuyên bố toàn repo chỉ có10 cổng**.

| Đường gọi | LỖI giữ/thêm | CB/gợi ý và giới hạn |
|---|---|---|
| long_script_lint → production_gates.long_script_report | cau_dai, nhieu_chi, ten_con_vat, tts_khoa_dong, tts_van_tay_lech; mới cau_tron theo tts.pause_ctx/ngày merge, markup_leak | Bốn check lookup/tuyển tập hạ CB: giờ từ clock nháp và nghĩa/đoán chương không tất định; nguồn BUD vẫn phải review receipt, không có check sutta tự động trong lint này. |
| HBR.retention_issues | Không chặn | Giữ các finding; đếm tiếng đọc thay token để khớp cau_dai, night/tra_cuu không quota câu ngắn. |
| library.tools.hook_lint → production_gates → HBR/short_batch_runner | KHUNG_DAU_TRONG giữ kiểm hình | TRUU_TUONG hạ gợi ý; KHONG_DANH_TU_CU_THE đã gợi ý, vẫn in ra khi qua adapter; tool/dữ liệu thiếu vẫn báo lỗi kỹ thuật. |
| short_v2_issues / short_tone_issues | API tương thích trả rỗng; không còn chặn heuristic | Logic chuyển short_v2_warnings/short_tone_warnings, gọi/in trong HBR và guard. V2 token budget/định nghĩa/câu1/insight/novelty/tone là ước đoán văn phong; không khẳng định duplicate-title là lặp nguyên văn lời. |
| short_story_issues → HBR/guard | Dòng cuối phẩy, từ29/11; thiếu ngày áp mới; hiểu publish_at/effective_date | Rào nguồn >1 chuyển short_source_warnings, có thể cần khung làm rõ nghĩa; không thêm check BUD phỏng dựng. |
| shortbuild.validate | Nguồn BUD, integrity lời (nối lại cùng HBR), tên chi, câu trọn; band đo đã khai và hợp đồng chip PD cũ | short_win_9_18/daytable dùng profile, không v2 token floor; hook hình studio vẫn theo workflow. Profile chưa có dur không tự tạo timing giả. |
| HBR.integrity_issues | Markup và lặp nguyên văn Short, voices sai | Long điệp có chủ đích giữ; ký hiệu/heading đậm được gỡ như trước. |
| studio.hook_errors / strict-hook | Không sửa | Kiểm hình/độ sáng/hiện chữ; không phải lint nghĩa hook. |
| V2 stier.script_lint / build.py (chưa sửa) | Legacy vẫn có hook>14, ngưỡng9/hook_kind/title/ảnh đổi mức01/12; build hook_errors/retention_hook_lint theo rules có thể chặn trước01/12; BUD legacy có nhiều cổng riêng | Đã chỉ rõ mâu thuẫn, hồ sơ mới không làm code này tự đổi. Lead cần ticket code nêu file nếu muốn chuyển các heuristic ấy sang CB; không chạy engine/TTS ở075b. |
| V2 Long script_lines.py (chưa sửa) | Integrity/roadmap/meta legacy | RAO_NGUON/NHIP_DEU/NHAY_MOC/META_NGUOI_KE và beat30s đã CB; guide mới không nhận đây là đồng bộ mọi cổng. |

Chạy `.venv/bin/python long_script_lint.py <plan> --strict`: chỉ exit1 khi có LỖI; exit0 mặc định không chứng minh0 lỗi. Segments/manifest khớp văn bản, giọng, pause mới dùng timing cuối; bước kiểm sau TTS giữ nguyên ở workflow sản xuất.
