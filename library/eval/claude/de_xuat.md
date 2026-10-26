# Đề xuất thử thư viện — agent claude

## 1. Nơi áp và kỹ thuật

Lệnh: `.venv/bin/python library/tools/lib.py pick --channel bud --usage-root "<checkout chính>"`.
Kết quả có 5 dòng, gồm jataka (ngang), doi (ngang), phap (thua), niem (thua) và ô tn_2026-10. Cả 5 dòng đều gợi ý cùng 3 kỹ thuật: Reveal chữ (15,00), Loop animation (10,00), Texture giấy (10,00).

**Nơi áp: khuôn short `phap` (thua).**
- Nguồn: `output/cl_staging/briefs/bud.md:169`. Bảng luật dừng khuôn ghi `phap` có n=13, trung vị 647 view, sàn 905, kết luận **DỪNG (đổi khuôn, giữ chủ đề)**.
- `phap` có n=13, đủ dữ liệu, nên được chọn trước `jataka` (n=1) và `doi` (n=4), hai khuôn còn "chưa đủ bài".
- Đề xuất này giữ chủ đề Phật pháp và chỉ đổi cách dựng, đúng memory "giữ chủ đề, đổi cách dựng".
- Không chọn ô `tn_2026-10`. Ô TN4 của BUD là chuỗi Chú Đại Bi, thuộc chuỗi bảo vệ.
- Không chọn `niem`. `pick` ghi cảnh báo Chú Đại Bi ngay trên dòng `niem`, mà bài TN4 phần 3 cũng mang lane `niem` (plan_bud_tn1029.json). Chọn `niem` dễ đụng chuỗi bảo vệ.

**Kỹ thuật: `text_reveal` (Reveal chữ).** Thẻ: `library/cards/canh/text_reveal.md`. Lý do chọn:
- Điểm cao nhất trong `rank --channel bud`: 15,0 (độ hợp bud 3 × 5 nguồn / công thấp).
- `ap_dung: thu_nghiem_hoac_dang_thua`, khớp với ADR 0018 mục 7.
- Phần "Khi nào dùng" của thẻ nói đúng nhu cầu ở đây: hiện cụm giải nghĩa sau trích đoạn kinh. Khuôn `phap` đang thua nằm ở khâu nhịp. Thẻ chữ hiện cả khối bằng mờ-nhoè (`show`) không giữ được mắt theo lời đọc.
- Rủi ro thẻ đã nêu là mask cắt dấu tiếng Việt. Kho đã có lời giải: `.wd.mask` có đệm dấu ở `hyperframes_short/studio/kit.css:4`.

**Phát hiện cho Lead:** thẻ ghi `da_dung: chua_co`. Thực ra studio đã có reveal theo mask: `hyperframes_short/studio/devices/quote.js:24` (mode `rise`) và device `close` (quote.js:43-46). Plan BUD chưa dùng mode `rise` lần nào (grep `"mode": "rise"` trên `output/cl_staging/bud/plan_*.json` ra 0). Vì vậy cờ đúng hơn là `co_san`. `engine_map.json` có thể thiếu ánh xạ quote.js → `text_reveal`.

## 2. Short thử nghiệm (27–32 giây)

**Tiêu đề:** Được khen nhiều có phải là phúc?

Kiểm trùng:
```
$ .venv/bin/python hf_novelty.py check bud "Được khen nhiều có phải là phúc?"
(không in dòng "trùng" nào; exit 0)
```
Hai tiêu đề phụ đã thử cũng sạch: "Vì sao cây chuối tàn sau khi ra buồng?" và "Danh lợi đến nhiều có phải là phúc?".

Đã soát thêm bằng tay:
- AN 4.68 chưa xuất hiện trong plan short BUD nào. Nó chỉ có trong Long Đề Bà Đạt Đa (L_bud_26).
- Hai kinh tôi định dùng trước đó đều đã có short, nên bỏ: AN 8.39 (đã dùng cho "Năm giới: hôm nay bạn giữ được mấy giới?") và AN 3.100 nắm muối (đã dùng ở b37 và b46).

**Kịch bản (6 câu):**
1. Được khen nhiều, lợi lộc nhiều, có chắc đó là phúc không? *(câu hỏi)*
2. Trong kinh Tăng Chi 4.68, Đức Phật nói **cây chuối** chết vì chính buồng quả của nó. *(chi tiết bất ngờ)*
3. Ngài nói khi Đề Bà Đạt Đa vừa rời đi: lợi lộc, danh tiếng đến với ông chỉ để ông tự hại.
4. Cây tre, cây sậy cũng vậy, **kết quả xong thì tàn**.
5. Lời khen không có lỗi; cái hại là khi ta bắt đầu sống để được khen. *(lời bình của kênh, không gán cho Phật)*
6. Điều người ta khen bạn nhiều nhất, bạn có đang sợ mất nó không? *(câu hỏi mở)*

Độ dài khoảng 89 từ. Giọng Binh đọc khoảng 3,3 từ/giây, ước theo tn4_p3: 85 từ ra dur 29,94 giây. Vậy được khoảng 27 giây lời, cộng 4 giây đệm, tổng khoảng 31 giây.

**Đối chiếu kinh** (`.venv/bin/python hf_sutta.py an4.68 "<cụm>"`, đọc từ cache `chunks_cache/suttacentral/an4.68.json`):

| Câu | uid | Nguyên văn (Sujato, CC0) |
|---|---|---|
| 2 | an4.68:6.1 | "The banana plant is destroyed by its own fruit," |
| 3 | an4.68:1.1 | "At one time the Buddha was staying near Rājagaha, on the Vulture's Peak Mountain, not long after Devadatta had left." |
| 3 | an4.68:1.3 | "Possessions, honor, and popularity came to Devadatta for his own ruin and downfall." |
| 4 | an4.68:3.1–4.1 | "or a bamboo …" / "or a reed, all of which bear fruit to their own ruin and downfall …" |

Ví dụ con la (an4.68:5.1) được bỏ có chủ ý: nó khó diễn tiếng Việt cho trang nghiêm, và không cần cho ý chính.

**Spec dựng:**
- **Thẻ kỹ thuật:** `text_reveal`, áp lên template `statue_cards` (`library/cards/template/statue_cards.md`).
- **Code dùng và mở rộng.** Không sửa file cũ. Tạo builder mới theo mẫu.
  - `output/cl_staging/grok/build_r1025.py:162`: `html_statue(rid, t, dur)` là khung ảnh tượng, shade, chip, thẻ và footer.
  - `output/cl_staging/grok/build_r1025.py:220`: `const show = ...` là chỗ thay bằng reveal chữ. Hiện tại thẻ hiện cả khối bằng opacity và blur.
  - `output/cl_staging/grok/build_r1025.py:66` và `build_r1024.py:54`: `segs(rid, delay)` lấy mốc đầu câu từ `<rid>_final.json`.
  - `hyperframes_short/studio/kit.css:4`: `.wd.mask` có đệm dấu `padding:.36em .04em .16em`. Chép quy tắc này vào CSS thẻ.
  - `hyperframes_short/studio/core.js:58`: `words(box, text, {mask})` tách từ và giữ `**nhấn**`. `core.js:65`: `waterfall` hiện nhị phân theo mốc.
  - `hyperframes_short/studio/devices/quote.js:24`: mode `rise` (`yPercent 115 → 0`) là mẫu chuyển động sẽ dùng.
  - `output/cl_staging/grok/build_r1025.py:63`: mẫu `IMG[rid] = (bank_path(...), top, bright)`. Dùng `statue_india_01` (CC0), lấy từ `output/cl_staging/bud/banks/statues.json`.
  - QA: `hf_qa.py:163` `gate_overflow` kiểm tràn chữ trước render.
- **Cách dựng tất định, seek-safe:**
  1. Trong builder Python, tách mỗi dòng `quote` thành `<span class="wd mask"><span class="in">từ</span></span>`.
  2. Mốc từng từ lấy theo kiểu `spread(T[i]+.15, T[i]+1.6, n)`. Mọi mốc là hằng số JSON nhúng sẵn, không đo layout và không dùng `Date`/`random`.
  3. Từng từ: `tl.set(in,{yPercent:115},0)`, rồi `tl.to(in,{yPercent:0,duration:.5,ease:"power3.out"},t_i)`.
  4. Dòng `gloss` (cụm giải nghĩa) wipe trái sang phải bằng `clip-path`. Tween `fromTo(gloss,{clipPath:"inset(-30% 100% -30% 0)"},{clipPath:"inset(-30% 0% -30% 0)",duration:.6,ease:"power2.out",immediateRender:false}, T[i]+1.8)`. Inset âm theo trục dọc để không cắt dấu (ả, ỗ, ặ).
  5. `tl.set(...,0)` khởi trạng thái ở frame 0. Mọi tween hữu hạn và có `immediateRender:false`, nên seek tới frame bất kỳ cho cùng kết quả. Giữ `hide` cũ ở dòng 221 để chuyển thẻ.
  6. Phụ đề và thẻ không lặp cùng chữ: thẻ chỉ hiện cụm khoá. Ảnh tượng zoom 1,00 → 1,05 tuyến tính như cũ.
- **Ước công: thấp.** Khoảng 60–80 dòng mới trong một builder copy từ `build_r1025.py` (hàm `html_statue_reveal`). Không đụng engine chung. Rủi ro chính là chiều cao thẻ khi mask có đệm, đã có `gate_overflow` kiểm.

**Plan nháp:** xem `plan.json`. Tóm tắt:
```json
{"id":"lib1_phap_khen","title":"Được khen nhiều có phải là phúc?","script":["…6 câu như trên…"],
 "source":"https://suttacentral.net/an4.68/en/sujato — AN 4.68 … CC0","insight":"Tăng Chi 4.68: …",
 "tags_vi":["lời phật dạy","danh lợi","đề bà đạt đa","kinh tăng chi","phật pháp"],
 "lane":"phap","test_cell":"LIB1 (chờ Lead đăng ký)","technique":"text_reveal"}
```

## 3. Tự kiểm

**Đã tuân:**
- **ADR 0018 mục 7:**
  - Áp vào khuôn `phap`, đang ở trạng thái DỪNG/thua theo `briefs/bud.md:169`.
  - Không đụng `tuong` (khuôn thắng, "giữ").
  - Không đụng chuỗi Chú Đại Bi, cũng không đụng các bài nhân khuôn ở `bud.md:157-159`.
  - Bài "Phóng sinh…" (phap, 1149 view) là bài thắng lẻ trong khuôn thua. Đề xuất không sửa bài đó, chỉ thêm một bài mới.
- **Luật BUD:**
  - Không máu, không vũ khí, không bạo lực. Đề Bà Đạt Đa chỉ được nhắc là "rời đi", không kể chuyện hại Phật.
  - Không người phương Tây: chọn tượng Ấn Độ `statue_india_01`, không chọn Gandhara.
  - Không tôn giáo khác. Chữ "ascetics and brahmins" không có trong AN 4.68 và không dùng.
  - Mọi câu gán cho Phật (câu 2–4) đều có uid và nguyên văn. Câu 5 là lời bình, được ghi rõ trong `source`.
- **Công thức:** câu 1 hỏi, câu 2 bất ngờ ("cây chuối chết vì chính buồng quả"), câu 6 hỏi mở. Thời lượng ước khoảng 31 giây.
- **Không mùi AI:** câu ngắn, dùng từ đời thường ("lợi lộc", "tự hại", "sợ mất"). Không dùng "hãy cùng", "bạn có biết", cũng không có câu khẩu hiệu kiểu "Đây chính là…".

**Chỗ chưa chắc:**
- `test_cell` LIB1 chưa có trong `experiments/tn_2026-10.json`. Nếu muốn thay một slot đã hẹn, Lead phải đăng ký và chạy quy trình lô thay (dry-run, unschedule.py).
- Thời lượng 31 giây mới là ước tính, chưa chạy TTS. Nếu vượt 32 giây thì cắt "lợi lộc nhiều" ở câu 1.
- "Cây sậy" dịch từ *reed* (Pali naḷa). Có bản Việt dịch là "cây lau". Cần thống nhất với cách gọi ở L_bud_26.
- Tôi chưa xem trực tiếp ảnh `statue_india_01` để soát crop (chữ đè mặt tượng, ticket 45). Phải xem trước khi render.
- Cờ `da_dung` của thẻ `text_reveal` có thể sai (xem mục 1). Đề xuất Lead sửa `engine_map.json` thay vì sửa tay thẻ.
- Không render, không đăng, không commit. Lệnh `hf_sutta` và `hf_novelty` chạy ở checkout chính và chỉ đọc cache có sẵn, không ghi file.
