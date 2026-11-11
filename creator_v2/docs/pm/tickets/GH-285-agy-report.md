# GH-285 phần 1 — báo cáo tải nhạc và giấy phép

Không commit, không sửa `music_catalog.json`, không đổi lịch, không đăng.

## Kết quả

Tải **87 bài** vào `tmp_music/`, ghi `tmp_music/proposed_catalog.json`. Mọi bài trong file đề xuất đều có `source_url`, `license`, `license_url`, `duration_s` (ffprobe), mood và channel theo brief.

Sau khi ghép 23 bài MacLeod thiếu + 64 bài nhạc sĩ mới vào danh mục hiện có (91 bài):

| Kênh | Bài dùng được | Tác giả |
| --- | ---: | --- |
| CL | 59 | Kevin MacLeod, Scott Buckley, Kai Engel |
| MIM | 51 | Kevin MacLeod, Chris Zabriskie, Kai Engel, Scott Buckley |
| CK | 47 | Kevin MacLeod, Kai Engel, Chris Zabriskie, Scott Buckley |

Mỗi kênh ≥ 40 bài, ≥ 3 tác giả.

## 1. Tải bù 23 bài MacLeod thiếu

So `motion/long/music_catalog.json` với `D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\output\music\`: **68 có file, 23 thiếu**. Cả 23 đã tải từ incompetech.com vào `tmp_music/macleod/<file>` đúng tên trong danh mục.

Nguồn từng bài: `https://incompetech.com/music/royalty-free/index.html?isrc=<ISRC>` (lấy ISRC từ `pieces.json` của incompetech). File MP3: `/music/royalty-free/mp3-royaltyfree/<filename>`.

Loạt SCP trên đĩa dùng tên ngắn `SCP-x1x.mp3` … `SCP-x7x.mp3` (không có phụ đề trong ngoặc). Đã lưu đúng slug danh mục (`scp_x1x_gateway_to_hell.mp3` …). Tiêu đề trên trang incompetech khớp `title` danh mục.

Thời lượng ffprobe khớp số liệu danh mục (ví dụ Stay the Course 272 s, SCP-x1x 352 s, Anguish 239 s).

**Giấy phép ghi trên trang incompetech** (khối credit trong `pieces.json` / UI): *Licensed under Creative Commons: By Attribution 3.0 License* — `https://creativecommons.org/licenses/by/3.0/`. Catalog hiện hành ghi CC BY 4.0. Đề xuất ghi **CC BY 3.0** đúng chữ trên trang bài. Cả 3.0 và 4.0 đều cho dùng thương mại nếu ghi công.

## 2. Nhạc sĩ mới

Mỗi người 20–22 bài, không lời, ≥ 2 phút, nguồn trang bài (không Pixabay, không YouTube Audio Library).

### Scott Buckley — 22 bài — CC BY 4.0

Trang thư viện và từng bài: `https://www.scottbuckley.com.au/library/<slug>/`. Mỗi trang có nút MP3 và dòng *Creative Commons Attribution 4.0 International License*. Chính sách chung: `https://www.scottbuckley.com.au/library/using-this-music/`.

Lưu `tmp_music/scott_buckley/<slug>.mp3`.

| Kênh | Số | Bài |
| --- | ---: | --- |
| CL | 14 | Eyes In The Void, Unraveling, Katabasis I, Anabasis I, The Long Dark, Terminus, I Walk With Ghosts, Beautiful Oblivion, Hiraeth, Filaments, Tears in Rain, Hour Of The Witch, Penumbra, What We Don’t Say |
| CK | 5 | In This Moment, Home Was You, Golden Hour, Sanctuary, Moonlight |
| MIM | 3 | With These Hands, Simplicity, Passage of Time |

### Chris Zabriskie — 20 bài — CC BY 4.0

Trang dùng nhạc: `https://chriszabriskie.com/use/` — *All of my music is free to use … Creative Commons Attribution 4.0*. Từng album ghi *Creative Commons Attribution license* trỏ về `/use/`.

File lấy từ bản FMA/Internet Archive (Cylinders, Direct to Video, Thoughtless, Music from Neptune Flux). `source_url` là trang album trên chriszabriskie.com.

Lưu `tmp_music/chris_zabriskie/<slug>.mp3`.

| Album | Trang bài | Số |
| --- | --- | ---: |
| Cylinders | https://chriszabriskie.com/cylinders/ | 8 (bỏ Cylinder Six, 1:46) |
| Direct to Video | https://chriszabriskie.com/dtv/ | 6 (bỏ *God Be With You Till We Meet Again* — hòa âm thánh ca của người khác) |
| Thoughtless | https://chriszabriskie.com/thoughtless/ | 5 |
| Music from Neptune Flux | https://chriszabriskie.com/neptuneflux/ | 1 (A New Day in a New Sector) |

16 bài MIM, 4 bài CK.

### Kai Engel — 22 bài — CC BY 3.0 hoặc CC BY 4.0

Trang nghệ sĩ FMA hiện **404**. Chỉ lấy bài có giấy phép BY (không NC, không ND) kiểm được trên trang bài/item.

| Album | Giấy phép | Bằng chứng | Số |
| --- | --- | --- | ---: |
| The Run | CC BY 3.0 | https://archive.org/details/KaiEngelTheRun (`licenseurl` = by/3.0) | 9 |
| Chapter Four / Fall | CC BY 4.0 | Wikimedia Commons (Laburnum, September, Smoldering, …) + FMA CDN | 4 |
| Sustains | CC BY 4.0 | Commons: Meekness, Holiday Gift, Slum Canto, Evermore, Cold War Echo, Mercy | 6 |
| Satin | CC BY 4.0 | Commons: Sentinel, Great Expectations, Homeroad | 3 |

`source_url`: file trên archive.org (The Run) hoặc trang Commons của đúng bài. October: URL FMA lịch sử `…/Chapter_Four__Fall/…_05_October` (trang FMA hiện 404; giấy phép album Chapter Four xác nhận CC BY 4.0 trên Commons).

17 CK, 4 MIM, 1 CL (Denouement, mood quiet/sad).

## 3. Số bài tải theo tác giả và kênh

Chỉ các bài trong `proposed_catalog.json` (bài tải bù + bài mới):

| Tác giả | Tổng | CL | MIM | CK |
| --- | ---: | ---: | ---: | ---: |
| Kevin MacLeod (bù) | 23 | 23 | 0 | 0 |
| Scott Buckley | 22 | 14 | 3 | 5 |
| Chris Zabriskie | 20 | 0 | 16 | 4 |
| Kai Engel | 22 | 1 | 4 | 17 |
| **Tổng** | **87** | **38** | **23** | **26** |

File: `tmp_music/macleod/` 23, `scott_buckley/` 22, `chris_zabriskie/` 20, `kai_engel/` 22.

## 4. Bài bỏ, kèm lý do

**MacLeod:** không bỏ bài nào trong 23 bài thiếu.

**Kai Engel — không tải vì NC / NC-SA (không phải CC BY thuần):**

- *The Scope* (kể cả Silence, Mist and Clouds) — CC BY-NC 4.0
- *Irsen's Tale* / Moonlight Reprise — CC BY-NC 3.0
- *Calls and Echoes* — CC BY-NC-SA 4.0 (archive.org SCL115)
- *Idea* — bản Jamendo ghi CC BY-NC 3.0; không lấy vì không xác nhận BY thuần
- *Chapter One / Cold*, *Chapter Two / Mild*, *Chapter Three / Warm* — Jamendo/FMA gắn NC
- *Rain Catcher*, *Paradigm Lost*, *Evening Colors*, *Deathless* — NC hoặc NC-SA

**Kai Engel — có BY nhưng không đưa vào đề xuất:**

- Thunderstorm (Pon VIII), Murmuration (Pon IX), Downpour (Pon X) — tên file FMA có khoảng trắng, CDN 404; Commons không khớp đúng tên file lúc tải
- Cobweb Morning (1:44), November (1:34) — ngắn hơn 2 phút
- Một số bài Satin/Sustains còn lại — Wikimedia 429 khi tải ogg; đã đủ 22 bài nên dừng

**Chris Zabriskie:**

- Cylinder Six — 1:46
- Itasca / We Were Never Meant to Live Here — dưới 2 phút
- *God Be With You Till We Meet Again* — hòa âm thánh ca Tomer/Rankin
- Album *Divider* trên archive.org ghi Attribution-Noncommercial 3.0, trong khi trang nghệ sĩ và Wikimedia ID3 ghi BY. **Không tải** vì mâu thuẫn metadata; đủ 20 bài từ album giấy phép rõ

**Scott Buckley:** không bỏ bài đã chọn. Không lấy Pumpkin Polka (halloween vui), không lấy bài remix dàn nhạc có chủ đề bản quyền (thư viện ghi rõ remix orchestral không thuộc CC).

Không dùng Pixabay, YouTube Audio Library, hay trang tổng hợp không rõ nguồn.

## 5. Nghi ngờ giấy phép

1. **MacLeod 3.0 vs 4.0.** incompetech vẫn in credit CC BY 3.0. Catalog và issue GH-285 ghi CC BY 4.0. filmmusic.io đôi khi ghi 4.0. Đề xuất theo chữ trên trang incompetech (3.0). Codex/lead nên thống nhất một dòng credit.
2. **FMA gỡ trang Kai Engel.** Artist/album FMA trả 404. Giấy phép The Run lấy từ metadata archive.org; Chapter Four / Sustains / Satin lấy từ Wikimedia Commons (LicenseShortName = CC BY 4.0, credit trỏ FMA). Trang FMA gốc không còn kiểm trực tiếp.
3. **October (Kai Engel).** File MP3 lấy từ FMA CDN (`Kai_Engel_-_05_-_October.mp3`); trang Commons đúng tên không thấy lúc truy vấn API. Gán CC BY 4.0 theo album Chapter Four đã kiểm. Nếu lead muốn chỉ bài có trang Commons đúng tên thì bỏ October.
4. **Divider (Zabriskie).** archive.org item ghi NC; trang `chriszabriskie.com/divider/` và `/use/` ghi mọi nhạc là CC BY 4.0. Đã bỏ Divider khỏi đề xuất.
5. **ID3 loạt SCP.** Tag gốc ghi `SCP-x1x` (không phụ đề). `SCP-x2x` ID3 bị ghi `SPC-x2x` (lỗi chính tả trên file incompetech). Tiêu đề đề xuất giữ đúng catalog.
6. **Một số MP3 Buckley** (Katabasis I, Anabasis I, Passage of Time) không có header ID3, vẫn là MPEG frame hợp lệ.

## File giao

- `tmp_music/proposed_catalog.json` — 87 mục, khuôn catalog + `license_url`, `source_url`, `duration_s`
- `tmp_music/macleod/*.mp3` — 23 bài bù
- `tmp_music/scott_buckley/*.mp3` — 22 bài
- `tmp_music/chris_zabriskie/*.mp3` — 20 bài
- `tmp_music/kai_engel/*.mp3` — 22 bài

Phần code `variety.py` / `describe.py` không làm (giao Codex). Lead nghe thử trước khi đưa vào danh mục chính.
