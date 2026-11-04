# GH-33 render 3 report

Scenes rewritten (title/lines/say/sources/description untouched). All 12 rendered with real `build.py` (preflight OK, no --draft). Contact sheets: `output/stier/<slug>/qa_sheet.png` (20 frames). No code under motion/ changed; no upload, schedule or commit.

| slug | status | dur | scene types (mode) | clips | sheet |
|---|---|---|---|---|---|
| ck-thue-xang-0-giam-1804 | rendered OK | 39.0s | kinetic(T) > timeline(D) > board(G) > table(D) > ledger(D) > kinetic(M) > cards3d(G) > kinetic(T) | pexels:39189857 | output/stier/ck-thue-xang-0-giam-1804/qa_sheet.png |
| ck-dien-giam-44-dong-20-nam | rendered OK | 33.5s | kinetic(T) > counter(D) > chart(D) > cards3d(G) > kinetic(M) > ledger(D) > board(G) > kinetic(T) | pexels:38362060 | output/stier/ck-dien-giam-44-dong-20-nam/qa_sheet.png |
| ck-vang-sjc-140-trieu-chenh-14-trieu | rendered OK | 35.2s | kinetic(T) > counter(D) > kinetic(M) > table(D) > board(G) > cards3d(G) > ledger(D) > kinetic(T) | pexels:7361127 | output/stier/ck-vang-sjc-140-trieu-chenh-14-trieu/qa_sheet.png |
| ck-ho-kinh-doanh-giam-30-thue | rendered OK | 35.1s | kinetic(T) > cards3d(G) > table(D) > board(G) > ledger(D) > kinetic(M) > board(G) > kinetic(T) | pexels:7233781 | output/stier/ck-ho-kinh-doanh-giam-30-thue/qa_sheet.png |
| ck-lai-giam-05-tien-gui-80-ngan-han | rendered OK | 33.4s | kinetic(T) > chart(D) > ledger(D) > kinetic(M) > cards3d(G) > chart(D) > kinetic(M) > kinetic(T) | pexels:6326861, pexels:35771190 | output/stier/ck-lai-giam-05-tien-gui-80-ngan-han/qa_sheet.png |
| ck-binance-63-ty-rut-36-ty | rendered OK | 35.6s | kinetic(T) > board(G) > table(D) > chart(D) > cards3d(G) > ledger(D) > kinetic(M) > kinetic(T) | pexels:26586643 | output/stier/ck-binance-63-ty-rut-36-ty/qa_sheet.png |
| mim-binance-20-phut-6-3-ty | rendered OK | 32.6s | kinetic(T) > timeline(D) > kinetic(M) > board(G) > table(D) > kinetic(M) > cards3d(G) > kinetic(T) | pexels:5377697, pexels:5377991 | output/stier/mim-binance-20-phut-6-3-ty/qa_sheet.png |
| mim-cam-nhap-dien-thoai-cu-2027 | rendered OK | 31.1s | kinetic(T) > ledger(D) > cards3d(G) > kinetic(M) > board(G) > kinetic(M) > table(D) > kinetic(T) | pexels:6755162, pexels:6755168 | output/stier/mim-cam-nhap-dien-thoai-cu-2027/qa_sheet.png |
| mim-sam-altman-ram-5-phan-tram | rendered OK | 31.1s | kinetic(M) > chart(D) > board(G) > quote(T) > kinetic(M) > cards3d(G) > ledger(D) > board(G) | pexels:10470834, pexels:6755168 | output/stier/mim-sam-altman-ram-5-phan-tram/qa_sheet.png |
| mim-android-20-tin-nhan-tu-than | rendered OK | 30.9s | kinetic(T) > cards3d(G) > kinetic(M) > board(G) > table(D) > kinetic(M) > ledger(D) > kinetic(T) | pexels:6611951, pexels:8865818 | output/stier/mim-android-20-tin-nhan-tu-than/qa_sheet.png |
| mim-9-tren-10-ai-tu-lay-otp | rendered OK | 31.0s | kinetic(T) > cards3d(G) > table(D) > board(G) > kinetic(M) > ledger(D) > cards3d(G) > kinetic(T) | pexels:33315117 | output/stier/mim-9-tren-10-ai-tu-lay-otp/qa_sheet.png |
| mim-ve-tinh-google-4-chip-tpu | rendered OK | 30.9s | kinetic(M) > board(G) > counter(D) > cards3d(G) > kinetic(M) > board(G) > ledger(D) > kinetic(M) | pexels:20349219, pexels:39433173, pexels:39433173 | output/stier/mim-ve-tinh-google-4-chip-tpu/qa_sheet.png |

## Issues found and fixed

- Original junk: narration sentences in table/ledger/board, `DU KIEN` chart labels, string lists (crash in sfx.py:366), 0.19 s first scene, ck-binance clip pexels:32365210 (3.2 s). All replaced by short labels and real numbers from beats.
- Scene 0 is a kinetic `hold` scene carrying the frame0 text from second 0 (2.5-3 s). Chart/board/counter fade in, so they cannot be scene 0.
- ck-binance clip replaced by pexels:26586643 (padlocks, 26 s, no text/brand). Other clips: existing ids kept where long enough; new: 7361127 (gold, ck-vang), 5377697/5377991 (monitors/red room, mim-binance), 6755162/6755168 (circuit board close-ups, no logos).
- Table: single wide cell highlight overlapped the row label; switched to row highlights and short cell text (2 columns or 1 column). Board first node clamped to y>=0.27 (touched the board title). Final kinetic scenes reduced to 2 items (3 stacked lines overlapped). Ledger/table keys shortened to fit.
- mim-sam-altman: Altman portrait (imgs) not used as photo scene; scene 0 stays kinetic over RAM clip to guarantee frame0 text. `imgs` left unchanged but unused. mim-ve-tinh: no haiku text in the facts, so no quote scene (counter '3 DONG HAIKU' instead). mim-binance FBI/PD image not used.
- Elon Musk quote text is taken verbatim from the beats ('Moi nguoi cung xung dang so huu RAM!'), labelled TRICH DICH.

## Remaining minor items (not blocking)
- A highlighted wide table cell still slightly covers the row label on mim-android row 2 and ck-vang (label clipped by 1-2 chars while highlighted).
- Some kinetic lines with 17+ characters render at 45-60 px (legible but small).
- Sequences differ across the 12 (checked by listing above). Mix lint passed in build for all.
- ck-lai-giam-05-tien-gui-80-ngan-han re-rendered (its earlier scenes were placeholder junk too).