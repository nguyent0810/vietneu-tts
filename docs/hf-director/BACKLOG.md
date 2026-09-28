# Những chỗ có thể cải thiện — ghi trong lúc phủ 02–09/10

Danh sách này sinh ra từ một lượt chạy thật: 40 short, 200 câu, director tự
quyết toàn bộ. Phần **đã sửa** là các lỗi đủ nặng để không thể để lại (không
còn bước người duyệt, sai là ra thẳng kênh). Phần **còn nợ** là các cải thiện
thật nhưng cần đụng tới hợp đồng hoặc kiến trúc, nên tách riêng.

## Đã sửa trong lượt này

| # | Lỗi | Biểu hiện thật | Cách sửa |
|---|---|---|---|
| 1 | `một` là mạo từ, không phải số | "dùng hình ảnh của **một người**" → `stat: 1 NGƯỜI`. Xuất hiện **6 lần** | Loại mọi `stat` có `value <= 1` |
| 2 | Regex số chỉ bắt chữ cuối | "**Mười hai** năm sau" → `stat: 2 NĂM` | Dùng `_NUM_PAT` đầy đủ (chuỗi nhiều chữ số) |
| 3 | Mảnh ngày tháng thành số liệu | "Rạng sáng **11 tháng 12 năm 1978**" → `stat: 12 NĂM` | `_DATE_CTX_RE`, số nằm trong cụm ngày tháng bị bỏ |
| 4 | Lane truyện bị gắn đồ hoạ | Truyện ma có ô số liệu "2 NGƯỜI" | `series == "tale"` → luôn `none` |
| 5 | Dấu hiệu ngưỡng ở quá xa con số | "ba tấn vàng — **nhiều hơn** mọi tính toán" → `TRÊN 3 TẤN` | Dấu hiệu phải nằm trong 26 ký tự trước số |
| 6 | Ngưỡng chỉ nhận đơn vị tiền | Bỏ sót "tỷ lệ tổn thương từ **11 phần trăm** trở lên" (Điều 134) | `threshold` nhận mọi đơn vị |

Cả 6 đều có test hồi quy trong `test_hf_director.py`. Lỗi 1–3 và 5 thuộc đúng
lớp "máy chắc chắn mà sai" mà ADR-0005 nói tới: confidence cao, không bao giờ
tự nhận là mơ hồ, nên chỉ lộ ra khi **đọc lại toàn bộ output trước khi render**.

> Rút ra: sau khi bỏ người duyệt, bước "đọc lại toàn bộ figure của cả loạt
> trước khi render" là **bắt buộc**, không phải tuỳ hứng. Nó rẻ (một lệnh) và
> vừa bắt được 13 figure rác trên 200 câu.

## Đã làm nốt trong lúc chờ render

| # | Việc | Kết quả |
|---|---|---|
| 1 | `timeline` gom mốc năm từ cả kịch bản | Không đụng hợp đồng: figure vẫn thuộc về một câu, chỉ dữ liệu là gom từ cả bài. Gắn vào câu có mốc cuối **không phải câu chốt** (gắn vào câu chốt là bị ràng buộc gỡ mất trong im lặng). Được phép thay `stat` đơn vị thời gian vì timeline nói đủ hơn |
| 2 | `run_batch.py` vào repo | `hf_batch_render.py <thư mục plan>` — hết cảnh mỗi đợt một bản copy lệch nhau |
| 4 | TTS đọc lồng tự thử lại | Phát hiện segment dài quá 3× mức 13 ký tự/giây → đọc lại tối đa 3 lần rồi mới báo hỏng |
| 3 | Đổi kiểu phụ đề theo ngày | 5 skin: `karaoke` (dossier) · `pill` (interrogation) · `rgb` (vhs) · `slab` (casemap) · `glow` (night). Cùng DOM, chỉ đổi cách lớp phủ `.on` hiện ra — hiệu ứng phải dùng `box-shadow`/`text-shadow` vì `.on` là lớp phủ đè lên từ nền, đổi kích thước hộp là lệch chữ |
| 5 | Hướng dẫn viết cho director | [WRITING-FOR-THE-DIRECTOR.md](WRITING-FOR-THE-DIRECTOR.md) |
| + | **Bẫy mới phát hiện**: kịch bản đổi mà `.wav` cũ còn đó | Số câu vẫn khớp số segment nên **không lỗi nào nổ ra** — video ra đời với tiếng cũ ghép vào chữ mới. Đã ghim hash kịch bản cạnh wav để bắt |

## Còn nợ

**1. Kịch bản hồ sơ vụ án thường chỉ có MỘT mốc năm.** Timeline giờ chạy
được, nhưng trên 8 bài lane vụ án chỉ **1 bài** có đủ hai mốc. Đây là vấn đề
biên tập chứ không phải kỹ thuật: bài nào cũng nên có **năm xảy ra** và **năm
khép lại**, nếu hồ sơ công khai có. Đã ghi vào hướng dẫn viết.

**4. TTS đọc lồng không được tự xử lý.** `d28_d` từng có một câu ngắn bị đọc
thành 32 giây (`n_failed_qa=1`); runner chỉ bỏ qua cả mục. Nên: phát hiện
segment dài bất thường → thử lại chính câu đó vài lần → vẫn hỏng mới bỏ.

**5. Viết kịch bản "cho director" nên thành hướng dẫn.** `o03_b` có 3 figure
vì câu văn nêu rõ mốc tiền, dải hình phạt và chuỗi hành vi; phần lớn câu khác
không có gì để vẽ. Đây là **cách viết**, không phải mẹo — nên ghi vào tài liệu
biên tập, nếu không người viết tiếp theo sẽ không biết.

**6. Độ phủ hiện tại: 13 figure / 200 câu (6,5%).** Lane truyện cố ý bằng 0.
Muốn dày hơn thì thêm **loại figure mới** (trích điều luật, so sánh hai điều
luật) chứ không nới ngưỡng cho rule đoán bừa — nới ngưỡng là quay lại đúng
lớp lỗi vừa sửa.

**7. `jsonschema` nằm ngoài `pyproject`.** `uv add` thất bại vì lock của repo
hỏng sẵn ở một wheel `win_amd64` không liên quan (404). Đang cài bằng
`uv pip install`, nên `uv sync` sẽ xoá. Cần sửa lock — việc riêng, không thuộc
đường ống này.

## `flow` bắt nhầm câu kể liệt kê (phát hiện 28/09, loạt BUD 01–06/10)

Ba lần trong 30 bài Phật giáo, director gắn `flow` cho câu **liệt kê song song**
chứ không phải chuỗi bước:

- "ăn thì biết mình đang ăn, đi thì biết mình đang đi" (b03_a)
- "Lúc buồn thì mua sắm, lúc vui cũng mua, rồi cuối tháng nhìn lại…" (b04_c)
- "Hẹn cà phê rồi quên, hứa gọi lại rồi thôi…" (b05_c)

Cả ba đều trùng câu đã có màn ảnh, nên bridge sẽ từ chối render. Đã ghi đè
tay (`source: human`). Hướng sửa: `flow` cần dấu hiệu **trình tự** (rồi / sau
đó / bước / trước khi…) giữa các vế, không chỉ nhiều vế cách nhau bằng dấu phẩy
-- và nên thêm ba câu trên làm test hồi quy.

## "năm tháng" bị đọc thành số 5 (phát hiện 28/09, b11_c)

"giữ lại **những năm tháng** đã qua" → `stat {value: 5, unit: "tháng"}`, độ tin
0.62, vượt ngưỡng 0.6. "năm" vừa là *year* vừa là *five*. Nếu không soi plan
trước khi render, video sẽ hiện ô số liệu "5 THÁNG" giữa bài về cha mẹ già.

Hướng sửa: coi "năm tháng", "năm này tháng nọ", "quanh năm" là thành ngữ thời
gian, không phải số; thêm câu trên làm test hồi quy. Câu hỏi rộng hơn: kênh BUD
gần như không bao giờ cần figure -- có nên để director tắt `stat`/`flow` cho
series này, thay vì vá từng trường hợp? (Quyết định cần một ADR.)
