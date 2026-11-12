# GH-270 — báo cáo Codex

## Thay đổi

- `motion/stier/build.py`: kiểm schema theo loại cảnh trước plan/SFX; trường lồng và danh sách được kiểm tra, báo cảnh, trường sai bằng tiếng Việt. `timeline.rows` thiếu `items` bị chặn với chỉ dẫn trường đúng. Khi schema sai, preflight không gọi plan để tránh lỗi KeyError che thông báo. `evidence` có `code`, `title`, `desc` được cảnh báo engine bỏ qua, không chặn riêng vì các trường đó.
- `motion/stier/README.md`: bổ sung bảng trường bắt buộc và sửa tiêu đề bảng loại cảnh.
- `tests/test_stier_preflight_schema.py`: kiểm thử preflight timeline sai/đúng, cảnh báo evidence và một số trường lồng.
- Đã đọc issue bằng `gh issue view 270 --repo nguyent0810/vietneu-tts` và đối chiếu `casefile.js`, `sfx.py`, `build.py`. Không sửa spec.

## Bảng trường bắt buộc

Mọi cảnh sau cảnh đầu cần `at` cấp cảnh. Mốc `at` cấp cảnh đầu mặc định bằng 0; các mốc được builder tự điền không cần khai báo. Các mục trong danh sách tùy chọn chỉ bắt các trường bên trong khi danh sách được khai báo.

| Loại cảnh | Trường bắt buộc; trường lồng khi dùng |
|---|---|
| `hero`, `doc`, `photo`, `evidence` | `img`; `doc.moves[]{at,x,y,z}`, `photo.circles[]{x,y,at}`, `evidence.callouts[]{x,y,text,at}` nếu có |
| `date` | `date` (builder tự điền `dayAt`, `groupAt`) |
| `counter` | `to` (builder tự điền `until`) |
| `calendar` | `n` (builder tự điền mốc và `step`) |
| `question`, `slam` | `text` |
| `quote` | `text`; riêng `mode: karaoke` cần `line`, builder lấy `text` từ câu đó |
| `kinetic` | `items` không rỗng, mỗi phần tử có `text, at` |
| `timeline` | `items` không rỗng, mỗi phần tử có `year, text, at`; không dùng `rows` |
| `split` | `a{img}`, `b{img}` (builder tự điền mốc) |
| `chart` | `points[]{v,at}` không rỗng nếu `kind: line`; còn lại `bars[]{v,at}` không rỗng |
| `cards3d` | `cards[]{k,v,at}` không rỗng |
| `table` | `cols[]`, `rows[]{k,v[]}` không rỗng; `hl[]{at}` nếu có |
| `board` | `nodes[]{text,x,y,at}`, `arrows[]{from,to,at}` nếu có |
| `ledger` | `rows[]{k,v,at}`, `total{k,v,at}` nếu có |
| `map` | `pins[]{name}`, `routes[]{from,to,at}`, `mug{img,at}` nếu có; dữ liệu bản đồ nằm ở `spec.map` |
| `mug` | `mug{img,at}` nếu có |
| `clock`, `file`, `crowd`, `source` | Không có trường đặc thù bắt buộc trong cổng này |

Các khối tùy chọn như `stamp{text,at}`, `label{text,at}`, `tape{text,at}`, `shatter{at}`, `bars{at}`, `big{text,at}`, `chart.ref{v,at}` và `chart.badge{text,at}` cần đủ trường khi được dùng.

Trong `evidence`, chữ chú thích dùng `tag` hoặc `callouts`: engine bỏ qua `code`, `title`, `desc`, nên preflight chỉ cảnh báo.

## Kiểm thử

- Python brief, `python -m pytest tests/test_stier_preflight_schema.py tests/test_ck_stier.py --basetemp=tmp_pytest -p no:cacheprovider -q`: **172 passed, 1 skipped, 3 errors**. Ba lỗi ở bước setup fixture `tmp_path` của `test_gap_adds_silence_between_lines_only_and_is_part_of_the_cache_key`, `test_a_ck_bundle_carries_disclaimer_sources_music_credit_and_utc_time`, `test_a_mim_spec_is_refused_by_the_ck_enqueue`: `PermissionError: [WinError 5] Access is denied` với `tmp_pytest`. Đây là lỗi quyền thư mục tạm, không phải kết quả assertion; cần Lead chạy lại toàn bộ ngoài sandbox. Một lần thử `tmp_pytest_270` cũng gặp lỗi quyền.
- `python -m pytest tests/test_stier_preflight_schema.py -p no:cacheprovider -q`: **8 passed**.
- `python -m pytest tests/test_ck_stier.py -p no:cacheprovider -q -k 'not test_gap_adds_silence_between_lines_only_and_is_part_of_the_cache_key and not test_a_ck_bundle_carries_disclaimer_sources_music_credit_and_utc_time and not test_a_mim_spec_is_refused_by_the_ck_enqueue'`: **164 passed, 1 skipped, 3 deselected**.
- Không chạy lint lời đọc: ticket sửa code preflight, không sản xuất Short; không render.

## So sánh preflight cũ và mới

Dùng danh sách file trên đĩa, không chạy git, nên bao gồm cả file chưa theo dõi nếu có. Chạy `build.preflight(slug)` đầy đủ hai lần cho từng file `data/stier/specs/{cl,ck,mim}-*.json`; lần cũ tắt riêng `scene_schema_errors` trong bộ nhớ, mọi cổng khác giữ nguyên. Kết quả **427 spec**: 126 qua cả hai; 295 bị cổng cũ và mới chặn; **6 qua cổng cũ nhưng bị cổng mới chặn**; không có exception. Tổng 9 spec có lỗi schema mới, trong đó 3 spec đã bị cổng cũ chặn vì lý do khác. Danh sách spec bị chặn thêm:

| Spec | Lỗi schema |
|---|---|
| `cl-alger-hiss-khai-man` | cảnh 1 (photo), label: cần đối tượng chứa trường text; cảnh 1 (photo), label: cần đối tượng chứa trường at; cảnh 3 (doc), tag: thiếu trường at; cảnh 6 (photo), label: cần đối tượng chứa trường text; cảnh 6 (photo), label: cần đối tượng chứa trường at |
| `cl-black-dahlia-56-phut` | cảnh 2 (doc), tag: thiếu trường at; cảnh 6 (photo), label: cần đối tượng chứa trường text; cảnh 6 (photo), label: cần đối tượng chứa trường at |
| `cl-clifford-irving-hoi-ky` | cảnh 0 (counter), sub: thiếu trường at |
| `cl-frank-grigware-van-tay` | cảnh 2 (photo), label: cần đối tượng chứa trường text; cảnh 2 (photo), label: cần đối tượng chứa trường at; cảnh 3 (doc), tag: thiếu trường at; cảnh 6 (photo), label: cần đối tượng chứa trường text; cảnh 6 (photo), label: cần đối tượng chứa trường at |
| `cl-khoi-da-dinh-menh-1950` | cảnh 2 (counter), sub: thiếu trường at |
| `cl-ross-tien-chuoc` | cảnh 0 (photo), label: cần đối tượng chứa trường text; cảnh 0 (photo), label: cần đối tượng chứa trường at; cảnh 3 (doc), tag: thiếu trường at; cảnh 6 (photo), label: cần đối tượng chứa trường text; cảnh 6 (photo), label: cần đối tượng chứa trường at |

Không tự sửa các spec. Kết quả so sánh chi tiết còn tại `tmp_gh270_comparison.json`; thư mục tạm pytest và file này được giữ lại vì luật repo cấm xóa ngoài phạm vi topic.

## Giới hạn

Cổng mới kiểm trường và hình dạng được nêu ở bảng; không xác nhận ý nghĩa dữ kiện, ảnh, hay kết quả hình ảnh sau render. Không có khẳng định nội dung video cần fact-check trong ticket code này. Không render nên không có clip sheet hoặc thumbnail. Không đăng, commit hoặc đổi lịch.
