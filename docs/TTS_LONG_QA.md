# TTS video dài: QA, lexicon, ASR (hướng dẫn thử nghiệm)

Tất cả mặc định **không đổi tiếng của video đã làm**, trừ phần "Đổi ngay" dưới đây. Mọi cờ nằm trong `tts` của plan (spec của `hf_voice.py`).

## Đổi ngay (không cờ)
- Manifest `<id>.json` ghi `n_retried`, `n_failed_qa`, `qa_failed_lines` thật. Câu nghi lỗi sau mọi lần thử **vẫn vào cache**, đánh dấu `"cached": true` trong `qa_failed_lines` và tạo file `.suspect` cạnh cache để lần sau biết (chỉ đọc lại khi bật `"qa_strict"` hoặc `VIENEU_RETTS_SUSPECT=1`).
- `tts_lexicon`: tên Pali -> tên Việt, `DN 16` -> "Trường Bộ kinh số mười sáu", `1-3` -> "1 đến 3", `%`, `&`, ngoặc, `...`.
  Tắt bằng `"lexicon": false`. Sửa bảng tên ở `tts_lexicon.json`. Phụ đề giữ chữ gốc; chữ đọc nằm ở `segments[].spoken`.
- Fade 8 ms ở đầu/cuối câu khi ghép.
- Thiết bị: `VIENEU_DEVICE` hoặc tự dò mps/cuda/cpu (trước: mps cứng).

## Cờ, mặc định TẮT (Lead quyết)
| Cờ | Tác dụng | Rủi ro khi bật |
|----|----------|----------------|
| `"qa_strict": true` | `hf_voice` thoát mã 2 nếu còn câu nghi lỗi -> runner dừng, không ghép tiếng hỏng; đọc lại câu nghi lỗi từ cache | Một câu hỏng chặn cả video cho tới khi sửa |
| `"pause_ctx": true` | Nghỉ >= 0,7 s sau câu trích kinh (`alt`), >= 0,5 s sau câu kết bằng `:` hoặc `…` | Đổi nhịp / thời lượng video so với dựng cũ |
| `"level": true` | Chuẩn hoá RMS từng câu về -23 dBFS (tối đa ±4 dB) | Đổi âm lượng tương đối giữa các câu của video cũ khi dựng lại |
| `"asr_check": true` hoặc `VIENEU_ASR_CHECK=1` | Nghe lại câu rủi ro bằng faster-whisper, cờ câu lệch | Tốn thời gian ASR, cần tải model |
| `"asr_all": true` | ASR mọi câu thay vì chỉ câu rủi ro | Chậm hơn |
| `VIENEU_MODEL_TAG=...` | Đưa tag vào khoá cache -> đọc lại toàn bộ khi đổi model | Mất cache một lần |
| `VIENEU_RETTS_SUSPECT=1` | Đọc lại câu nghi lỗi đã đánh dấu `.suspect` trong cache | Tốn thời gian đọc lại |

## Cách thử
1. `pytest tests/test_hf_asr_check.py tests/test_tts_normalization_consistency.py test_tts_lexicon.py test_hf_long_v2.py tests/test_long_script_lint.py`
2. Dựng 1 video dài ngắn như thường. Xem `<id>.json`: `n_failed_qa`, `qa_failed_lines`; nghe các câu có `spoken`.
3. Đo ASR trên wav đã có, không dựng lại gì:
   `pip install faster-whisper` rồi `python hf_asr_check.py output/.../<id>.wav --report-only` (thêm `--all` để kiểm mọi câu).
   Dòng đầu in `N câu mới, X s cho Y s âm thanh (Zx thời gian thực)`; chi tiết ở `<id>.asr.json`.
   Chạy lần hai: nghe 0 câu mới (cache). Đổi model: `--model medium` hoặc đường dẫn model CT2 khác.
4. Chỉnh `THRESHOLD` / `THRESHOLD_RISKY` trong `hf_asr_check.py` theo `wer` thật của câu đúng và câu sai.

## Chưa kiểm chứng (không có model/GPU trong môi trường dựng PR)
- `hf_voice.synth` với model thật; ASR với faster-whisper thật; ngưỡng WER; thời gian ASR (xRT).
- Chưa làm: chống trùng câu mở giữa các Short; căn từ bằng Whisper thay `hf_align` (word timestamps của faster-whisper là hướng tiếp theo).
