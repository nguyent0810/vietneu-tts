# Kho tham khảo kiểu dựng từ các thư viện Opus 5.5

Ngày kiểm tra: 26/10/2026. Mục tiêu là mượn **kỹ thuật và cấu trúc chỉ đạo**, không chép thiết kế, hình hay lời. Điểm hợp 0–3 là nhận định biên tập cho FS/BUD, không phải điểm chất lượng/hiệu quả. Chỉ kiểm README, CSV, JSON, Markdown/code và bài gốc được repo dẫn; không tải video.

## Corpus và giới hạn

| Nguồn | Quy mô/đường dẫn dữ liệu | Cách dùng và giới hạn |
|---|---|---|
| [athemeroy/awesome-opus-5-5-videos](https://github.com/athemeroy/awesome-opus-5-5-videos) | Ưu tiên chính. README ghi 424 bài nguồn, 301 nhãn Opus; CSV case `data/cases.csv`, bảng phân loại `data/domain-style.csv`, thống kê `docs/statistics.md`, atlas `docs/domain-style-atlas.md`. Snapshot phân loại đóng băng 26/09/2026. | Corpus đóng góp/tuyển chọn; bộ phân loại xem văn bản và chín khung, không xác minh tác giả, model hay toàn bộ chuyển động. Mỗi hàng ở `domain-style.csv` là một tệp; trong 1.119 tệp gắn nhãn `yes/likely`, motion graphics/UI 350, 3D render 324, hoạt hình phẳng 162, pixel art 58; lịch sử/văn hoá 49, giáo dục/khoa học 147. Đổi ngưỡng `yes` sang `yes+likely` làm nhóm nội dung lớn nhất đổi từ quảng cáo (191) sang game/tương tác (230), nên không coi thứ hạng lĩnh vực là ổn định. [README](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/README.md) · [thống kê](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/docs/statistics.md) · [CSV phân loại](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/data/domain-style.csv) |
| [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos) | README ghi 703 prompt, 418 có remake trên Skillry; có thư mục `prompts/` và `data/videos.json`. | Hữu ích đối chiếu prompt/cặp remake; “remake” không phải tái lập độc lập đã kiểm. Repo ghi thêm 285 prompt ngày 12/10; các con số là theo README tại ngày kiểm tra. [README](https://raw.githubusercontent.com/yihui-dev/awesome-opus5-5-videos/main/README.md) |
| [LeaddeOpenLab/awesome-opus-5-5-video-prompts](https://github.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts) | README hiện ghi 749 prompt; nhóm motion graphics, explainer, 3D, prompt và template. | README nói prompt cộng đồng chưa được tái tạo độc lập; mẫu Manim ghi rõ `not_tested`. Dùng để học cấu trúc brief/nhãn công cụ, không lấy đó làm bằng chứng thành phẩm chạy giống nhau. [README](https://raw.githubusercontent.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts/main/README.md) · [prompt Manim](https://raw.githubusercontent.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts/main/prompts/2103128559174971663.md) |

Các lĩnh vực gần nhu cầu giải thích văn hoá/tra cứu gồm giáo dục-khoa học (147 tệp) và lịch sử-văn hoá (49), nhưng đây là đếm tệp trong tập nhãn `yes/likely`, không phải đếm video độc lập hay riêng ngách Việt/Phật giáo. [Thống kê](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/docs/statistics.md) ghi 1.401 tệp phân loại, 1.371 post ID; một post có thể có nhiều tệp. Không suy ra độ phổ biến hay hiệu quả giữ chân từ số lượng corpus, lượt thích hoặc nhãn “viral”.

## Đối chiếu với kho của kênh

Kho Long đã có wheel 12 chi, ngũ hành, years/list/timeline/compare/stat/map, quote/word/illus, layout ảnh 2.5D và endcard; BUD short giới hạn loại visual và kho devices short đã có hook, compare, wheel, cycle, timeline, source card, ledger, list, quote, count ring, bars và các dạng khác. Vì thế bảng năm, vòng 12 con giáp, sơ đồ quan hệ, quote động, timeline thường và UI quảng cáo không phải khoảng trống. Nguồn nội bộ: [motion-library/SKILL.md](../SKILL.md), [devices.md](../../shorts-studio/references/devices.md).

Kho 234 prompt-motion đã phân loại cũng đã bao gồm Manim đạo hàm, rối bóng, giấy, timeline và nhiều kiểu tranh; `quy_uoc.md` đã xếp `shadow_theatre`/`paint_over` vào hàng đợi cảnh mới. Đây là đối chiếu kỹ thuật sẵn có, không có nghĩa các cảnh đó đã được triển khai trong engine kênh. [quy_uoc.md](./prompt_motion/quy_uoc.md) · [catalog.json](./prompt_motion/catalog.json). Dưới đây chỉ là những **biến thể còn thiếu trong các loại executable hiện nêu**, hoặc cách dàn cảnh chưa được chuẩn hoá.

## Bảng kiểu dựng đáng xem

| Kiểu / case nguồn | Kỹ thuật gốc và ý mượn | Đưa sang HyperFrames (đề xuất) | FS / BUD | Công | Rủi ro / khoảng trống |
|---|---|---|---:|---|---|
| **Manim: bài học bằng biến đổi hình học** — [LinearUncle, case 2103128559174971663](https://x.com/LinearUncle/status/2103128559174971663); [prompt và mô tả](https://raw.githubusercontent.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts/main/prompts/2103128559174971663.md) | Manim + TTS; một khái niệm đi từ trực giác → hình → ký hiệu → ví dụ → giới hạn. Case mô tả bài đạo hàm 7:36 phút; prompt gốc yêu cầu giải thích dễ hiểu, có ví dụ, khơi suy nghĩ. | Vẽ SVG/HTML paths và nhãn theo mốc câu/word trong GSAP timeline; dữ liệu/nội dung khóa trước, mỗi trạng thái suy trực tiếp từ thời gian để seek-safe. Dùng dạng scene Long, không nhúng Manim/Python renderer vào render HF. | FS 3 / BUD 2 | Vừa. Nguy cơ sai công thức/diễn giải; cần người duyệt chuyên môn. Manim style tổng thể không mới với catalog nội bộ, nhưng chuỗi “trực giác rồi biến đổi rồi kiểm tra giới hạn” chưa thành mẫu scene trong SKILL. |
| **Giấy cắt lớp / sân khấu bóng** — [Axton Liu, “breathing Xuan paper” case 2103288413969621231](https://x.com/AxtonLiu/status/2103288413969621231); [NFT Chen, giấy cắt Trung thu case 2103380404791333144](https://x.com/NFT_Chen/status/2103380404791333144) | Hai bài gốc mô tả HTML/Canvas từng nét trên giấy dó, và p5.js/p5.brush ghép tư liệu nền với lớp giấy cắt. Phần mềm/nguồn asset ở ví dụ NFT Chen do tác giả mô tả, không có source để độc lập kiểm. | Tách 3–5 lớp SVG/ảnh đã cấp phép; dùng parallax rất nhẹ và mask/reveal theo cue, không mô phỏng vật lý ngẫu nhiên. Ráp chuyển động qua GSAP timeline, giữ mọi transform là hàm của t. | FS 2 / BUD 3 | Vừa. BUD hợp tranh minh hoạ biểu tượng, không nhân cách hoá Phật; FS dùng vật/nhà/tiết khí, tránh khẳng định phong thuỷ như định mệnh. Dễ thành “AI paper texture” hoặc chật chữ dọc. Kho đã có 2.5D ảnh nên novelty là chất liệu/layer reveal, không phải parallax đơn thuần. |
| **Tranh mực hiện dần theo nét** — [Axton Liu, case 2103288413969621231](https://x.com/AxtonLiu/status/2103288413969621231); đối chiếu ranh giới chất lượng [Pradeep Kapoor, case 2102782449478668290](https://x.com/pradeepXkapoor/status/2102782449478668290) | Axton nói HTML/Canvas dựng từng nét tranh núi, tùng, thuyền, mặt trời trên nền giấy; mã nguồn chưa công khai. Case Pradeep nêu Three.js/WebGPU, cọ và mô phỏng mực nhưng tác giả đánh dấu bản phim chưa hoàn tất. Đây là tuyên bố tác giả, không phải kiểm tra source. | Không bê mô phỏng chất lỏng/WebGPU. Tiền vẽ các đường SVG/alpha-mask cố định, reveal stroke theo t; hạt mực nếu có thì cố định seed, rất ít. Seek-safe; một cảnh 4–8 giây. | FS 2 / BUD 3 | Vừa–cao nếu tự tạo artwork. Rủi ro cọ/mực giả, rung hoặc hạt thành “mùi AI”; không để hiệu ứng làm mất chữ/nguồn kinh. Kho Long đã có `ink` và style inkwash, nên chỉ cân nhắc như biến thể “nét vẽ lộ theo lời”, không thêm một hệ shader. |
| **Sơ đồ kỹ thuật xây theo lời** — [akokoi1 geography, case 2102606609574941028](https://x.com/akokoi1/status/2102606609574941028); [JoaoLi13 context window, case 2102805376466891137](https://x.com/joaoli13/status/2102805376466891137) | Explainer code/diagram: dòng khí quyển → ô áp suất → mùa; ví dụ kia chuyển dữ liệu giữa hai vùng input/output. Case ghi TTS ngoài; không có source code được xác nhận. | Khai báo node/edge và trạng thái hiển thị từ JSON; GSAP draw/reveal theo câu; snap vào bố cục ổn định và có nhãn. Dữ liệu không phụ thuộc FPS, không dùng simulation đang chạy. Tái dùng `cycle_draw`/`list_build` nếu phù hợp. | FS 3 / BUD 2 | Thấp–vừa. Có thể làm rõ nhà/cấu trúc hoặc quan hệ nhân-quả trong lời giảng; không biến suy đoán thành quy luật phong thuỷ/giáo lý. Bảng/flowchart cơ bản đã có, phần mới là sơ đồ nhiều trạng thái có node/edge được giải thích theo trình tự. |
| **Cảnh 3D procedural với camera có mục đích** — [Clearwater, case 2102786378282987591](https://x.com/Aurelien_Gz/status/2102786378282987591), [repo code được case dẫn](https://github.com/Aureliengmz/clearwater); [MengTo ship case 2103122947133309311](https://x.com/MengTo/status/2103122947133309311) | Clearwater README có WebGL2, FFT waves, ripple simulation, caustics; CSV mô tả cảnh nước realtime. Ship case nói tác giả tự chấm điểm cải thiện, điểm đó không phải đánh giá độc lập. | Rút thành một shot 2.5D/CSS hoặc scene SVG/WebGL đã cố định; camera keyframes theo timeline, seed/dữ liệu cố định, không dùng realtime FFT/physics. Mỗi thời điểm phải ra cùng khung khi seek. | FS 2 / BUD 1 | Cao. Có thể dùng cận cảnh mái/đồ vật hay địa hình khi thực sự giải thích không gian; không dùng “bay camera” trang trí. BUD dễ mất trang nghiêm, FS dễ thành quảng cáo/giật gân; kiểm GPU/headless nếu WebGL. |
| **Nhân vật/đồ vật lặp lại qua các cảnh** — [Hanif Produktif, ant colony case 2102742924148830211](https://x.com/hanifproduktif/status/2102742924148830211); [repo công khai được CSV dẫn](https://github.com/buildwithhanif/claude-animation-skill) | Repo case ghi `frame(ctx,t)`, Node Canvas/ffmpeg, rig kiến/âm thanh và kiểm deterministic; chín khung được đối chiếu với project, nhưng không khôi phục prompt/call gốc. | Mượn “hành động được chia thành trạng thái” và continuity của một hình tượng, không nhất thiết lấy nhân vật hoạt hình. Dựng SVG/pose assets; cue trạng thái qua time/word, không random. | FS 2 / BUD 2 | Vừa. Dùng vật thể trung tính (hạt gạo, lá sen, la bàn) làm chỉ dẫn; tránh hoạt hình hoá Phật hoặc biến giáo lý thành game. Kho short có loop/nhân vật theo định dạng, nên đây là khung kể chuyện Long hơn là engine mới. |

`FS/BUD` điểm 0–3 biểu thị độ hợp giọng kênh theo jugement biên tập. Các giá trị kỹ thuật trong cột “đưa sang” là phương án chuyển thể, không phải thứ tác giả nguồn đã làm bằng HyperFrames.

## Top 5 đáng thử

Thứ tự ưu tiên theo độ mới trong kho, tính giải thích và chi phí chuyển thể; Lead duyệt trước khi đưa vào backlog/coding.

### 1. Sơ đồ kỹ thuật xây theo lời — Long FS

**Vì sao:** dùng motion để giải thích quan hệ, bổ sung cho list/timeline/compare mà không đòi shader. Nguồn: [akokoi1 geography](https://x.com/akokoi1/status/2102606609574941028), [JoaoLi13 context window](https://x.com/joaoli13/status/2102805376466891137). Kỹ thuật nguồn được mô tả là code/diagram; engine cụ thể chưa kiểm.

**Dàn ý cảnh mẫu, “Vì sao hướng gió đổi theo mùa?”** (chủ đề minh hoạ; mọi số/khẳng định phải có nguồn riêng): (1) hiện bản đồ/đường chân trời tĩnh; (2) vẽ mũi tên “mặt đất nóng lên” đến node “không khí bốc lên”; (3) nối node áp suất và mũi tên chiều gió; (4) đổi nhãn mùa theo câu đọc; (5) giữ sơ đồ hoàn chỉnh kèm nguồn. Dọc short chỉ giữ tối đa 3 node; ngang Long có thể giữ toàn sơ đồ. Không tự suy diễn quan hệ phong thuỷ từ hình.

### 2. Bài học bằng biến đổi hình học — Long BUD

**Vì sao:** cấu trúc trực giác → hình → ví dụ → giới hạn có thể làm lời giáo lý trừu tượng dễ theo hơn, nhưng nội dung phải do biên tập giáo lý duyệt. Nguồn/công cụ: [prompt Manim LinearUncle](https://raw.githubusercontent.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts/main/prompts/2103128559174971663.md); bản ghi nói kết quả “not_tested” độc lập.

**Dàn ý cảnh mẫu, “Vô thường qua chiếc lá”**: (1) một chiếc lá nguyên vẹn đứng yên; (2) đổi sáng/tối và hiện dấu thời gian, không cho lá rã thành hiệu ứng; (3) cùng chiếc lá chuyển màu theo vài trạng thái minh hoạ; (4) chữ trích dẫn có nguồn chỉ xuất hiện sau lời giải thích; (5) kết bằng hình chiếc lá nằm yên và một câu hỏi chiêm nghiệm. Không gán câu diễn ý thành lời Phật; kinh văn phải có nguồn và số kinh.

### 3. Giấy cắt lớp, sân khấu bóng — short dọc BUD

**Vì sao:** silhouette/layer rõ ở màn hình nhỏ, hợp kể một tình huống đời thường trong khi giữ tông ấm. Kỹ thuật gợi ý đối chiếu từ [Axton Liu](https://x.com/AxtonLiu/status/2103288413969621231) và [NFT Chen](https://x.com/NFT_Chen/status/2103380404791333144); không có project gốc để tái lập độc lập.

**Dàn ý cảnh mẫu, “Một người ôm mãi lời trách”**: (1) bóng người ngồi trong khung cửa, một mảnh giấy tượng trưng câu nói; (2) giấy được chuyển từ tay này sang bàn, không thêm lời kết luận; (3) lớp sáng chuyển chậm từ ngoài cửa vào; (4) câu kinh đã xác minh hiện đúng lúc đọc, giữ nguồn; (5) kết khung tĩnh không CTA hoạt náo. Không vẽ Đức Phật như nhân vật hoạt hình.

### 4. Nét mực mở ra cảnh — Long BUD

**Vì sao:** một nét có thể dẫn mắt và tạo nhịp đọc chậm; kỹ thuật tham khảo từ [case Axton](https://x.com/AxtonLiu/status/2103288413969621231). Kho đã có style inkwash, nên thử dưới dạng reveal stroke thuần SVG trong scene hiện hữu, không xây engine mực mới. **Chưa kiểm** mã nguồn hay tính nhất quán của rendering Axton.

**Dàn ý cảnh mẫu, “Con đường về chùa”**: (1) một nét mái chùa kéo dài thành đường chân trời; (2) nét thứ hai tạo lối đi; (3) một bóng cây được tô dần theo câu kể; (4) giữ vùng trống an toàn cho một dòng kinh có nguồn; (5) dừng hình ít nhất đủ đọc. Nếu đường nét không truyền đạt nội dung, bỏ cảnh.

### 5. Vật thể lặp lại làm mốc kể chuyện — Long FS

**Vì sao:** continuity có thể nối các ý tra cứu mà không phải đổi sang template/UI. Nguồn quy trình có code/determinism mạnh hơn là [repo ant colony được CSV athemeroy dẫn](https://github.com/buildwithhanif/claude-animation-skill); đây là tham khảo về pipeline `frame(ctx,t)`, không mượn kiến/thiết kế.

**Dàn ý cảnh mẫu, “Dòng nước trong sơ đồ nhà”**: (1) một đường nước mảnh đi vào sơ đồ nhà; (2) mỗi câu lần lượt mở đúng một nhánh/hướng; (3) nhãn chỉ nêu dữ kiện có trong kịch bản/nguồn; (4) cùng đường nước dẫn mắt sang sơ đồ tổng kết; (5) kết bằng nhắc đây là tham khảo văn hoá, không dự báo vận hạn. Dùng SVG/HTML deterministic; không chạy mô phỏng nước realtime.

## Cấu trúc prompt nên bổ sung cho `prompt_mau.md`

Mẫu hiện có đã quy định inputs, direction, cue sheet, build, gotchas và review. Nên thêm trường vào `<inputs>` và `<structure>`, không thay prompt cốt lõi:

```text
Ý cần người xem hiểu sau cảnh: {{một câu, không phải cảm giác chung}}
Sự thật/nguồn cần giữ: {{mệnh đề + link; lời kinh kèm số kinh; nếu chưa có thì ghi CHƯA KIỂM}}
Biến thể khung: {{dọc 9:16 | ngang 16:9}}; vùng chữ/phụ đề an toàn: {{tọa độ hoặc preset}}
Vật thể/quan hệ xuyên cảnh: {{một hình tượng chính; trạng thái trước → sau}}
Giới hạn hình: {{số lớp/node tối đa; điều tuyệt đối không vẽ}}
Chất liệu tham khảo: {{medium/kỹ thuật + nguồn; chỉ mượn nguyên tắc, không chép bố cục}}
Kiểm duyệt: {{độ trang nghiêm BUD / không gieo sợ FS / người duyệt nội dung}}

Cho từng cue: lời đọc → trạng thái nhìn thấy → thuộc tính thay đổi → thời điểm bắt đầu/kết → khung giữ để đọc.
Ghi rõ khung đầu, trạng thái trung gian, khung cuối; nêu cách cùng một t cho cùng một frame khi seek ngược/xuôi.
```

Lý do: prompt Manim mẫu chỉ nêu “dễ hiểu, ví dụ, gợi suy nghĩ” và công cụ TTS; trong khi README athemeroy khuyến nghị ghi asset, voice, segment timing và yêu cầu giao hàng cùng nhau. [Prompt Manim](https://raw.githubusercontent.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts/main/prompts/2103128559174971663.md) · [athemeroy README](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/README.md). Đây là đề xuất cấu trúc prompt; hiệu quả chưa thử.

## Không nên mượn

- **Không mượn shader/physics realtime làm chuẩn mặc định.** Clearwater dùng WebGL2/FFT/ripple theo README repo được case dẫn; render headless cần cùng khung tại cùng t. Chuyển thành keyframe/mask/geometry xác định trước nếu thực sự cần. [Clearwater source](https://github.com/Aureliengmz/clearwater).
- **Không coi 3D hoặc số lượt tương tác là bằng chứng đúng.** Các case 3D/game là demo/capture; nội dung lịch sử, khoa học, giáo lý cần người duyệt riêng. [Atlas giới hạn phân loại](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/docs/domain-style-atlas.md).
- **Không bê quảng cáo UI, nhịp cắt gấp, hạt/glow/flare, camera bay hoặc prompt “go all out”.** Chúng không giúp tra cứu và một số trái luật motion hiện hành. [quy_uoc.md](./prompt_motion/quy_uoc.md).
- **Không dùng mô phỏng mực/3D cho BUD chỉ để gây choáng; không dùng nhà cửa/vật phẩm để dọa hạn cho FS.** Đây là áp dụng quy ước giọng kênh, không phải kết luận từ corpus.
- **Không lấy nhãn likes/views/remake làm kết quả dựng.** Corpus và các repo không cung cấp thử nghiệm đối chứng retention của FS/BUD; quan hệ hiệu quả chưa kiểm.

## Nguồn đối chiếu trong repo

- Kho cảnh Long và nguyên tắc nội bộ: [SKILL.md](../SKILL.md).
- Bộ 234 prompt đã phân loại: [quy_uoc.md](./prompt_motion/quy_uoc.md), [catalog.json](./prompt_motion/catalog.json).
- Thiết bị hình short: [devices.md](../../shorts-studio/references/devices.md).
- Mẫu prompt hiện tại cần cập nhật sau khi Lead duyệt: [prompt_mau.md](./prompt_motion/prompt_mau.md).

## Nhận xét Lead (Claude, 26/10/2026)

Codex làm ticket. Lead đã kiểm chéo:
- `data/domain-style.csv` có 1.401 dòng.
- Bảy mã case dẫn trong file đều có trong cả `cases.csv` và `domain-style.csv`.
- Repo `Aureliengmz/clearwater` và `buildwithhanif/claude-animation-skill` đều tồn tại.
- README của Leadde ghi 749 prompt.

Không thấy chỗ nào bịa.

**Ưu tiên của Lead:**
1. **Sơ đồ xây theo lời (top 1):** đáng làm nhất. Đây là một dạng cảnh Long mới (node/edge khai báo bằng JSON, hiện dần theo từng câu), khác list/timeline đang có. Làm theo skill `motion-scene-dev`, thử trên một chương FS.
2. **Giấy cắt lớp, sân khấu bóng (top 3):** trùng `shadow_theatre`/`paint_over` đã có trong hàng đợi của `quy_uoc.md`. Gộp lại thành một việc, ưu tiên cho BUD.
3. **Bài học bằng biến đổi hình học (top 2):** dùng được như một khuôn kịch bản cho chương BUD (trực giác → hình → ví dụ → giới hạn), không cần engine mới.
4. **Nét mực mở cảnh (top 4) và vật thể lặp lại (top 5):** để sau. Top 4 chỉ là biến thể của inkwash đang có; top 5 là khuôn kể, chưa phải thiết bị hình.

Các trường bổ sung cho `prompt_mau.md` hợp lý. Chỉ sửa `prompt_mau.md` khi bắt đầu làm cảnh mới đầu tiên trong danh sách trên.
