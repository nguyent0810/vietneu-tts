"""Test tự động cho thumbnail_generator.py + long_batch_runner.py::
_pick_thumbnail_background() (audit 9 điểm mục #6)."""
import json

from PIL import Image

import thumbnail_generator as tg
import long_batch_runner as lbr


def _make_test_background(path, size=(1920, 1080), color=(80, 90, 100)):
    Image.new("RGB", size, color).save(path)
    return path


def test_output_is_exact_youtube_thumbnail_size(tmp_path):
    bg = _make_test_background(tmp_path / "bg.jpg")
    out = tg.generate_thumbnail(str(bg), "Tiêu Đề Thử Nghiệm", str(tmp_path / "out.jpg"), domain="BUD")
    with Image.open(out) as img:
        assert img.size == (1280, 720)


def test_vietnamese_diacritics_render_without_crash(tmp_path):
    bg = _make_test_background(tmp_path / "bg.jpg")
    out = tg.generate_thumbnail(
        str(bg), "Vì Sao Nghiệp Không Phải Là Bản Án?", str(tmp_path / "out.jpg"), domain="BUD",
    )
    assert out.exists()
    assert out.stat().st_size > 1000


def test_background_aspect_ratio_is_cropped_not_stretched(tmp_path):
    """_fit_background() phải CROP (giữ tỉ lệ gốc) chứ không kéo méo ảnh --
    kiểm tra bằng cách xác nhận kích thước đầu ra đúng 16:9, không phụ
    thuộc tỉ lệ ảnh nền gốc (vuông, dọc, ngang đều)."""
    for src_size in [(1000, 1000), (1080, 1920), (3840, 1000)]:
        bg = _make_test_background(tmp_path / f"bg_{src_size[0]}x{src_size[1]}.jpg", size=src_size)
        result = tg._fit_background(bg, tg.OUT_SIZE)
        assert result.size == tg.OUT_SIZE


def test_domain_accent_colors_differ_and_cl_avoids_red_yellow():
    """CL (Hình Sự) PHẢI dùng tông trầm/trung tính, KHÔNG đỏ/vàng giật gân
    -- đúng cam kết "non-sensational" đã áp dụng xuyên suốt dự án."""
    assert set(tg.ACCENT_BY_DOMAIN.keys()) == {"BUD", "FS", "CL"}
    cl_accent = tg.ACCENT_BY_DOMAIN["CL"]["accent"]
    r, g, b = cl_accent
    # Không phải tông đỏ nổi bật (r cao, g/b thấp) hay vàng chói (r,g cao, b thấp).
    is_red_dominant = r > 180 and g < 100 and b < 100
    is_yellow_dominant = r > 200 and g > 180 and b < 100
    assert not is_red_dominant and not is_yellow_dominant


def test_unknown_domain_falls_back_to_default_accent(tmp_path):
    bg = _make_test_background(tmp_path / "bg.jpg")
    out = tg.generate_thumbnail(str(bg), "Test", str(tmp_path / "out.jpg"), domain="UNKNOWN_DOMAIN")
    assert out.exists()


def test_long_title_wraps_to_at_most_three_lines():
    """Codex review vòng 1 (bug thật): test cũ chỉ gọi _wrap_text() ở 1 cỡ
    chữ CỐ ĐỊNH, không gọi logic co-chữ/cắt-bớt thật -- không xác nhận
    được bất biến "luôn <= 3 dòng". Gọi ĐÚNG _fit_title_to_lines() (hàm
    thật sự dùng trong generate_thumbnail()) và assert kết quả CUỐI CÙNG."""
    from PIL import ImageDraw
    canvas = Image.new("RGB", tg.OUT_SIZE)
    draw = ImageDraw.Draw(canvas)
    long_title = "ĐÂY LÀ MỘT TIÊU ĐỀ RẤT DÀI DÙNG ĐỂ KIỂM TRA XUỐNG DÒNG TỰ ĐỘNG CHO THUMBNAIL YOUTUBE VỚI RẤT NHIỀU TỪ KHÔNG NGỪNG"
    font, lines = tg._fit_title_to_lines(draw, long_title, tg.OUT_SIZE[0] - 128, max_lines=3, start_size=92)
    assert len(lines) <= 3
    # Dòng cuối (nếu bị cắt) phải vừa khung hình -- không tràn ra ngoài.
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        assert bbox[2] - bbox[0] <= tg.OUT_SIZE[0] - 128


def test_truncate_line_to_width_adds_ellipsis_when_too_long():
    """Test trực tiếp _truncate_line_to_width() (không phụ thuộc đoán số
    từ/cỡ chữ vừa đủ tràn dòng, vốn khó tính tay chính xác) -- 1 dòng CHẮC
    CHẮN quá dài (lặp lại nhiều lần) phải được cắt + thêm '…' và kết quả
    PHẢI vừa max_width."""
    from PIL import ImageDraw
    canvas = Image.new("RGB", tg.OUT_SIZE)
    draw = ImageDraw.Draw(canvas)
    font = tg._font(92)
    max_width = 300  # cố tình rất hẹp để chắc chắn cần cắt
    too_long_line = "TỪTHỬNGHIỆMDÀIRẤTNHIỀUKÝTỰKHÔNGTHỂVỪA"
    result = tg._truncate_line_to_width(draw, too_long_line, font, max_width)
    assert "…" in result
    assert draw.textbbox((0, 0), result, font=font)[2] <= max_width


def test_fit_title_to_lines_never_exceeds_max_lines_even_with_narrow_width():
    """_fit_title_to_lines() với max_width RẤT HẸP (buộc mỗi dòng chỉ vừa
    vài ký tự) + không cho co cỡ chữ -- PHẢI vẫn <= 3 dòng bằng cách cắt
    bớt, không bao giờ trả về nhiều hơn max_lines dù input dài bao nhiêu."""
    from PIL import ImageDraw
    canvas = Image.new("RGB", tg.OUT_SIZE)
    draw = ImageDraw.Draw(canvas)
    absurdly_long = " ".join(["TỪ"] * 50)
    font, lines = tg._fit_title_to_lines(draw, absurdly_long, max_width=200, max_lines=3, start_size=92, min_size=92)
    assert len(lines) <= 3


def test_single_unbreakable_token_line_never_exceeds_max_width():
    """Codex review vòng 2 (bug thật): _wrap_text() có nhánh `or not current`
    để tránh vòng lặp vô hạn khi 1 token DUY NHẤT (VD: URL, hashtag, mã vụ
    án) rộng hơn max_width -- token đó vẫn được chấp nhận làm 1 dòng dù
    tràn khung, và vì len(lines) == 1 (không vượt max_lines) nên nhánh cắt
    dòng cũ trước đây không bao giờ chạy tới, dòng tràn được vẽ nguyên vẹn.
    Test tiêu đề chỉ gồm 1 token dài không khoảng trắng, assert dòng cuối
    PHẢI vừa max_width."""
    from PIL import ImageDraw
    canvas = Image.new("RGB", tg.OUT_SIZE)
    draw = ImageDraw.Draw(canvas)
    max_width = 300
    single_long_token = "VUANDHINHSU2026TAPMOTHATDACBIETXEMNGAYKHONGBOLO"
    font, lines = tg._fit_title_to_lines(
        draw, single_long_token, max_width=max_width, max_lines=3, start_size=92, min_size=92,
    )
    for line in lines:
        assert draw.textbbox((0, 0), line, font=font)[2] <= max_width


def test_last_line_gets_ellipsis_when_lines_dropped_even_if_it_already_fits():
    """Khi tiêu đề bị cắt bớt xuống đúng max_lines (các dòng phía sau bị bỏ
    hẳn), dòng cuối PHẢI luôn có dấu '…' để báo hiệu nội dung đã bị rút
    gọn -- kể cả khi bản thân dòng đó vốn đã vừa max_width (Codex review
    vòng 2: bản cũ trả nguyên dòng không dấu '…' trong trường hợp này,
    trông như đã hiển thị đủ toàn bộ tiêu đề)."""
    from PIL import ImageDraw
    canvas = Image.new("RGB", tg.OUT_SIZE)
    draw = ImageDraw.Draw(canvas)
    words = " ".join(["TỪ"] * 20)
    font, lines = tg._fit_title_to_lines(draw, words, max_width=220, max_lines=3, start_size=92, min_size=92)
    assert len(lines) == 3
    assert lines[-1].endswith("…")
    assert draw.textbbox((0, 0), lines[-1], font=font)[2] <= 220


def test_generate_thumbnail_end_to_end_respects_three_line_cap(tmp_path):
    bg = _make_test_background(tmp_path / "bg.jpg")
    long_title = "ĐÂY LÀ MỘT TIÊU ĐỀ RẤT DÀI DÙNG ĐỂ KIỂM TRA XUỐNG DÒNG TỰ ĐỘNG CHO THUMBNAIL YOUTUBE VỚI RẤT NHIỀU TỪ KHÔNG NGỪNG NGHỈ"
    out = tg.generate_thumbnail(str(bg), long_title, str(tmp_path / "out.jpg"), domain="CL")
    with Image.open(out) as img:
        assert img.size == (1280, 720)  # không bị tràn/vỡ layout


# --- _pick_thumbnail_background() ---

def test_pick_background_prefers_image_treatment(tmp_path):
    img_asset = tmp_path / "beat_image.jpg"
    _make_test_background(img_asset)
    shot_list = {
        "beats": [
            {"treatment": "video", "asset_path": None},
            {"treatment": "typography", "asset_path": None},
            {"treatment": "image", "asset_path": str(img_asset)},
        ]
    }
    shot_list_path = tmp_path / "shot_list.json"
    shot_list_path.write_text(json.dumps(shot_list), encoding="utf-8")
    result = lbr._pick_thumbnail_background(str(shot_list_path))
    assert result == img_asset


def test_pick_background_skips_missing_files(tmp_path):
    shot_list = {
        "beats": [
            {"treatment": "image", "asset_path": str(tmp_path / "does_not_exist.jpg")},
        ]
    }
    shot_list_path = tmp_path / "shot_list.json"
    shot_list_path.write_text(json.dumps(shot_list), encoding="utf-8")
    assert lbr._pick_thumbnail_background(str(shot_list_path)) is None


def test_pick_background_returns_none_when_no_image_beats(tmp_path):
    shot_list = {"beats": [{"treatment": "video", "asset_path": "/some/video.mp4"}]}
    shot_list_path = tmp_path / "shot_list.json"
    shot_list_path.write_text(json.dumps(shot_list), encoding="utf-8")
    assert lbr._pick_thumbnail_background(str(shot_list_path)) is None


def test_pick_background_falls_back_to_diagram(tmp_path):
    diagram_asset = tmp_path / "beat_diagram.jpg"
    _make_test_background(diagram_asset)
    shot_list = {"beats": [{"treatment": "diagram", "asset_path": str(diagram_asset)}]}
    shot_list_path = tmp_path / "shot_list.json"
    shot_list_path.write_text(json.dumps(shot_list), encoding="utf-8")
    assert lbr._pick_thumbnail_background(str(shot_list_path)) == diagram_asset


def test_pick_background_skips_diagram_that_became_a_video_clip(tmp_path):
    """BUG THẬT phát hiện qua Codex CLI review: beat treatment="diagram" có
    annotation có thể bị asset_generation.py THAY asset_path bằng đường
    dẫn CLIP MP4 đã render (render_annotated_diagram_clip()) -- file MP4
    này .exists()=True nhưng KHÔNG phải ảnh, PIL sẽ crash nếu dùng làm
    nền. Xác nhận _pick_thumbnail_background() tự bỏ qua case này (không
    trả về video), không chỉ dựa vào exists()."""
    fake_video = tmp_path / "diagram_clip.mp4"
    fake_video.write_bytes(b"not a real mp4, just bytes for the exists() check")
    shot_list = {"beats": [{"treatment": "diagram", "asset_path": str(fake_video)}]}
    shot_list_path = tmp_path / "shot_list.json"
    shot_list_path.write_text(json.dumps(shot_list), encoding="utf-8")
    assert lbr._pick_thumbnail_background(str(shot_list_path)) is None


def test_is_valid_image_file_rejects_non_image(tmp_path):
    fake = tmp_path / "not_an_image.mp4"
    fake.write_bytes(b"definitely not image bytes")
    assert lbr._is_valid_image_file(fake) is False


def test_is_valid_image_file_accepts_real_image(tmp_path):
    img = tmp_path / "real.jpg"
    _make_test_background(img)
    assert lbr._is_valid_image_file(img) is True


# --- Tách upload video khỏi set thumbnail (Codex review vòng 1, bug nghiêm
# trọng): video upload THÀNH CÔNG nhưng set-thumbnail LỖI không được khiến
# registry hiểu nhầm là chưa upload -- resume sau đó KHÔNG được upload
# trùng. ---

def test_thumbnail_failure_does_not_prevent_video_id_from_being_saved(tmp_path, monkeypatch):
    topic = "Test Topic Long"
    monkeypatch.setattr(lbr, "_output_dir", lambda t: tmp_path / "output" / "long" / t)

    ep_dir = tmp_path / "output" / "long" / topic / "EP_TEST"
    ep_dir.mkdir(parents=True, exist_ok=True)

    # Shot list có 1 beat ảnh hợp lệ để thumbnail generator có nền dùng.
    img_asset = ep_dir / "beat_image.jpg"
    _make_test_background(img_asset)
    shot_list_path = ep_dir / "shot_list_final.json"
    shot_list_path.write_text(json.dumps({"beats": [{"treatment": "image", "asset_path": str(img_asset)}]}), encoding="utf-8")

    video_bgm_path = ep_dir / "with_bgm.mp4"
    video_bgm_path.write_bytes(b"fake video bytes")

    registry = {
        "EP_TEST": {
            "key": "EP_TEST", "episode_dir_name": "EP_TEST", "title": "Test Episode",
            "status": "seo_ready", "shot_list_path": str(shot_list_path), "video_bgm_path": str(video_bgm_path),
            "seo": {"title": "Tiêu Đề Test", "description": "Mô tả test", "tags": ["test"]},
        }
    }
    lbr.save_registry(registry, topic)

    monkeypatch.setattr(lbr, "upload_video", lambda *a, **kw: {"id": "FAKE_VIDEO_ID_123"})
    # Bỏ qua bước kiểm tra trùng lặp thật (duplicate_check.py, gọi YouTube
    # Data API + ffprobe thật) -- test này không xoay quanh cơ chế đó (đã
    # có test_duplicate_check.py/test_long_batch_runner_duplicate_guard.py
    # riêng), chỉ cần xác nhận video_id vẫn được lưu đúng dù bước thumbnail
    # lỗi.
    monkeypatch.setattr(lbr, "check_for_possible_duplicate", lambda *a, **kw: None)

    def _boom_thumbnail(*a, **kw):
        raise RuntimeError("giả lập lỗi thumbnails.set API")
    monkeypatch.setattr("youtube_upload.upload_thumbnail", _boom_thumbnail)

    # internal_dir chỉ thật sự dùng ở các bước TRƯỚC "seo_ready" (audio/
    # shot-list/SEO) -- entry seed sẵn ở status="seo_ready" nên các bước đó
    # bị bỏ qua, giá trị dummy này không bao giờ được đọc thật.
    ep = {"episode_id": "EP_TEST", "episode_dir_name": "EP_TEST", "title": "Test Episode", "internal_dir": str(tmp_path)}
    # credentials_path trong tmp_path (không phải string tương đối trần) --
    # process_one_episode() giờ giữ channel_upload_lock() (thật, ghi file
    # khoá cạnh credentials_path) xuyên suốt bước upload; dùng path tương
    # đối trần từng làm rơi 1 file "fake_creds.json.lock" mồ côi vào chính
    # thư mục dự án (đã tự phát hiện khi review).
    credentials_path = str(tmp_path / "fake_creds.json")
    result = lbr.process_one_episode(ep, topic, credentials_path, None, "2026-08-01T13:00:00Z", dry_run=False, domain="CL")

    # Bất biến QUAN TRỌNG NHẤT: video ĐÃ upload (có video_id, status=uploaded)
    # dù thumbnail lỗi -- không được để resume sau hiểu nhầm là chưa upload.
    assert result["video_id"] == "FAKE_VIDEO_ID_123"
    assert result["status"] == "uploaded"
    assert result["thumbnail_status"] == "failed"

    # Xác nhận ĐÃ GHI xuống đĩa (không chỉ đúng trong bộ nhớ) -- đây chính
    # là trạng thái 1 lần chạy sau (resume) sẽ đọc lại.
    on_disk = lbr.load_registry(topic)
    assert on_disk["EP_TEST"]["video_id"] == "FAKE_VIDEO_ID_123"
    assert on_disk["EP_TEST"]["status"] == "uploaded"


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
