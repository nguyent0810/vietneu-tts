# GH-159 PR 1 — báo cáo Codex

## File đã đổi

- `library/tools/channel_profile.py`: thêm loader JSON, kiểm tra schema tối thiểu, nhận diện kênh và mapping ngược tương thích cho tên lịch sử cũ.
- `library/channels/mim.yaml`: thêm hồ sơ dữ liệu MIM.
- `library/channels/ck.yaml`: thêm hồ sơ dữ liệu CK.
- `library/channels/cl.yaml`: thêm hồ sơ dữ liệu CL.
- `library/channels/lich_su.yaml`: đổi tên nguyên nội dung từ hồ sơ lịch sử cũ.
- `library/channels/_thu_lich_su.yaml`: xoá sau migration tên tệp.
- `library/channels/vsd.yaml`: đổi `kenh` thành `vsd`, thêm tên hiển thị và alias.
- `library/channels/_external.yaml`: xoá; `kho_loc` đã nằm trong từng hồ sơ kênh.
- `library/tools/assets.py`: chỉ tải hồ sơ kênh thực; bỏ luồng đọc `_external.yaml` và cập nhật tài liệu CLI.
- `library/tools/lib.py`: dùng `channel_profile` cho registry/profile thực, vẫn hỗ trợ thư mục profile được test monkeypatch.
- `hf_sound.py`: cập nhật comment migration, không đổi hành vi.
- `library/CHO_KENH_KHAC.md`: đổi tên tệp mẫu lịch sử trong tài liệu.
- `library/schema/asset.schema.json`: bỏ tham chiếu `_external.yaml` trong mô tả `pham_vi`.
- `tests/test_assets.py`: fixture dùng các hồ sơ kênh riêng thay vì manifest ngoài.
- `tests/test_motion_picker.py`: dùng `lich_su`.
- `tests/test_prompt_builder.py`: dùng `lich_su.yaml`.
- `tests/test_kinetic_presets.py`: dùng `lich_su.yaml`.
- `tests/test_sound_director.py`: dùng `lich_su`.
- `tests/test_studio_v3turbo.py`: cập nhật assert `kenh == "vsd"`.
- `tests/test_channel_profile.py`: thêm kiểm tra JSON/schema, resolve, compatibility và đối chiếu bảng hard-code.

## Kiểm tra

`python -m pytest tests/test_channel_profile.py tests/test_sound_director.py::test_load_channel_sound_and_new_sound tests/test_sound_director.py::test_sfx_anti_clash_timing_safety tests/test_assets.py::test_code_khong_nhanh_kenh -q -p no:cacheprovider`

```text
6 passed in 1.79s
```

Đã chạy nguyên lệnh pytest theo brief (không có `tests/test_image_request.py` trong worktree): `9 failed, 39 passed, 2 skipped, 34 errors in 11.86s`. Các lỗi đều xảy ra ngoài phần migration: sandbox Windows từ chối tạo/quét thư mục tạm cho fixture (`PermissionError`), hoặc môi trường Windows thiếu `fcntl` khi import các test sound/studio. Không tắt test.

`git diff --check` không báo lỗi nội dung (nhưng `git status` in cảnh báo vì các thư mục tạm pytest bị sandbox khóa). `git grep -n "_thu_lich_su"` chỉ thấy hai tài liệu ticket đã có; vì loader mới đang untracked theo yêu cầu không commit/stage, dùng `rg` trên worktree xác nhận thêm đúng một mapping compatibility trong `library/tools/channel_profile.py`. Không còn `_external.yaml` trong code/tài liệu vận hành.

## Giá trị cần Lead duyệt

- `ngach` cho MIM/CK/CL và tên/id/trạng thái `active` của hai `khuon` mỗi kênh: code nguồn không có biểu diễn profile tương ứng.
- `upload.slot_short` của CL đặt `[]`: lưới slot hiện chỉ có MIM/CK.
- `theme.brand` của CL đặt `"Hình Sự"`: bảng Long chỉ có voice/quote của CL; đây là tên hiển thị đã có trong bảng factory.
