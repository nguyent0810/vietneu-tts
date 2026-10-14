# Dựng Short kênh Hình Sự bằng HyperFrames

Nhánh dựng hình **thứ hai** của repo, song song với `video_tool_bridge.py`
(shot_list + Ken Burns + B-roll). Cùng đầu vào (`wav` + manifest `.json` do
TTS sinh ra), cùng đầu ra (1 file mp4 9:16 đã có tiếng) — khác ở chỗ hình
được **vẽ bằng HTML** rồi render qua headless Chrome, không gọi API ảnh và
không tải stock footage.

Vì sao có nhánh này: với domain CL, B-roll là chỗ tốn thời gian nhất và rủi
ro nhất (cả bộ `broll_query_sanitizer` trong `domain_creative_profiles.json`
sinh ra chỉ để chặn ảnh bạo lực lọt vào). Nội dung dạng "giải thích điều
luật / cảnh báo / kể chuyện" vốn lấy chữ làm chính, nên vẽ thẳng bằng HTML
vừa nhanh hơn vừa không có gì để kiểm duyệt ngoài chính HTML ta viết.

## Chạy

```bash
python3 hyperframes_bridge.py \
  --script kich_ban.txt --wav audio.wav \
  --series law --style dossier \
  --badge "ĐIỀU 173 · BLHS 2015" --footer "Phổ biến kiến thức pháp luật" \
  --bgm bgm/deliberate_thought.mp3 --bgm-gain 0.17 \
  --output output/cl_staging/vd.mp4 --quality looks
```

`--script` là kịch bản gốc, **mỗi câu một dòng**, cụm quan trọng bọc trong
`**...**`. Số dòng phải bằng số segment trong manifest TTS — lệch là báo lỗi
chứ không ghép mò (kịch bản đã bị sửa sau khi render audio).

## Hai trục độc lập: series và style

| Trục | Quyết định | Giá trị |
|---|---|---|
| `--series` | **làn nội dung**: nhãn kicker, footer mặc định | `law` · `scam` · `case` · `tale` |
| `--style` | **cái nhìn**: màu accent, bố cục, chuyển cảnh | `clean` · `dossier` · `interrogation` · `vhs` · `casemap` · `night` |

Lịch đang chạy: **mỗi ngày một style**, 5 short trong ngày dùng chung style
đó nên cả ngày trông như một tập phim; phân biệt làn nội dung bằng nhãn
kicker chứ không bằng màu.

| Style | Cái nhìn | Chuyển cảnh |
|---|---|---|
| `dossier` | Hồ sơ mật — đen sâu, đỏ máu, thẻ hồ sơ, bụi trôi | zoom-through + mờ |
| `interrogation` | Phòng thẩm vấn — một vũng đèn, chữ giữa khung, đèn chập chờn | focus pull |
| `vhs` | Băng ghi hình — CRT, timecode chạy, tách màu RGB, nhiễu băng | glitch |
| `casemap` | Bản đồ điều tra — lưới bản vẽ, dây nối vẽ dần, thẻ đầu mối | dạt ngang + mờ |
| `night` | Hiện trường đêm — mưa, đèn vàng hắt, chữ có bóng nước | loé sáng |

## Cấu trúc

```
hyperframes_short/
  index.html                 # style "clean"
  compositions/base.css      # layout + phụ đề dùng chung
  compositions/engine.js     # dựng scene, phụ đề karaoke, timeline, audio
  compositions/<style>.html  # CSS + 4 hook của từng style
```

Mỗi style chỉ cần khai báo `window.HF_STYLE = { buildScene, enter,
transition, ambient }` rồi gọi `HF.build()`.

## Ba cái bẫy đã gặp (đừng sửa lại theo hướng cũ)

1. **`data-duration` của root đọc ở compile time.** Gán bằng JS hay bằng
   `--variables` đều bị bỏ qua. `hyperframes_bridge.py` vì thế nướng thời
   lượng thật vào một bản sao `.render_<tên>.html` rồi mới render.
2. **Thẻ `<audio>` do script tạo ra không được tính** (`audioCount: 0`,
   video ra câm mà không báo lỗi) — compiler chỉ quét media khai báo tĩnh.
   Tiếng được ghép bằng `ffmpeg` sau khi render, tiện thể chuẩn hoá
   `loudnorm=I=-14` đúng mốc YouTube.
3. **Scene không được là `.clip`.** Composition nhiều cảnh có transition thì
   GSAP phải tự quản opacity; để framework ẩn/hiện theo `data-start` sẽ
   tranh quyền với transition. Phụ đề nằm ở lớp riêng phía trên nên chữ
   không nhoè theo cảnh.

## Yêu cầu môi trường

- **Node >= 22** (cài qua nvm; Node mặc định của máy vẫn là 20, launchd
  không bị ảnh hưởng). Bridge tự `nvm use 22` trong shell con.
- `ffmpeg` (đã có sẵn cho pipeline hiện tại).
- Thư mục `hyperframes_short/assets/` và các file `.render_*`/`.vars_*` là
  rác tạm, đã nằm trong `.gitignore` của thư mục đó.
