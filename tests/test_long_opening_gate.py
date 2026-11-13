"""Test cổng mở đầu 40s (opening_gate) cho video dài (Task 026):
Luật O1–O8 theo báo cáo 025:
- O1: câu 1 có hình (không thẻ chương/thẻ chữ ở giây 0) [ERROR]
- O2: 0–40 s không chữ-trên-nền-trống > 1,5 s [ERROR]
- O3: ≥ 8 hình khác nhau trong 0–40 s [ERROR]
- O4: từ khoá chính của title được nói trước giây 15 [WARN]
- O5: cấm ảnh ref nhân vật (/refs/, REF_) làm hình [ERROR]
- O6: cảnh báo lời meta (\"video này\", \"chương N\", \"đăng ký\") trong 0–40 s [WARN]
- O7: câu hỏi hẹn/lộ trình không nằm trong 0–40 s [WARN]
- O8: xuất tờ khung 0–40 s (1 khung/2 s) ra first40.jpg
- O9: không khung đồng màu > 0,3 s trong 0–40 s của mp4 đã render [ERROR]
"""
import sys
import shutil
from pathlib import Path
from PIL import Image
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hf_batch_render as HBR
import hyperframes_bridge as HB


def _segs_from_durs(durs):
    out, t = [], 0.0
    for d in durs:
        out.append({"start": round(t, 3), "end": round(t + d - 0.05, 3)})
        t += d
    return out


def test_opening_gate_o1_sentence_1_must_have_image():
    # Câu 1 không có media -> LỖI O1
    script = [f"Câu {i} nội dung lịch sử." for i in range(1, 15)]
    durs = [2.5] * len(script)
    segs = _segs_from_durs(durs)
    media = {str(i): {"kind": "image", "src": f"img{i}.jpg"} for i in range(2, 10)}
    row = {"id": "test_o1", "title": "Lịch Sử", "script": script, "media": media, "visuals": {}}
    errs, _ = HBR.opening_gate(row, segs)
    assert any("O1: câu 1 (giây 0) không có hình" in e for e in errs)

    # Câu 1 là heading -> LỖI O1
    script_heading = ["**Mở đầu**"] + script[1:]
    media_1 = {str(i): {"kind": "image", "src": f"img{i}.jpg"} for i in range(1, 10)}
    row_heading = {"id": "test_o1_head", "title": "Lịch Sử", "script": script_heading, "media": media_1, "visuals": {}}
    errs_h, _ = HBR.opening_gate(row_heading, segs)
    assert any("O1: câu 1 (giây 0) là thẻ chương" in e for e in errs_h)

    # Câu 1 có ảnh hợp lệ -> ĐẠT O1
    row_ok = {"id": "test_o1_ok", "title": "Lịch Sử", "script": script, "media": media_1, "visuals": {}}
    errs_ok, _ = HBR.opening_gate(row_ok, segs)
    assert not any("O1:" in e for e in errs_ok)


def test_opening_gate_o2_naked_run_limit_in_first_40s():
    # 0-40s có đoạn chữ trên nền trống liên tục 2.0s > 1.5s -> LỖI O2
    script = [f"Câu {i}." for i in range(1, 15)]
    durs = [2.0, 2.0] + [2.5] * 12
    segs = _segs_from_durs(durs)
    media = {"1": {"kind": "image", "src": "img1.jpg"}}
    # Câu 2 và câu 3 không có ảnh, nhưng câu 2 là visual word 2.0s > 1.5s
    visuals = {"2": {"type": "word"}}
    row = {"id": "test_o2", "title": "Lịch Sử", "script": script, "media": media, "visuals": visuals}
    errs, _ = HBR.opening_gate(row, segs)
    assert any("O2: 0–40s có chữ trên nền trống" in e and "(> 1.5s)" in e for e in errs)

    # Nếu visual có overlay: true trên ảnh đang giữ -> không tính là naked -> ĐẠT O2
    visuals_ov = {"2": {"type": "ask", "overlay": True}}
    row_ov = {"id": "test_o2_ov", "title": "Lịch Sử", "script": script, "media": media, "visuals": visuals_ov}
    errs_ov, _ = HBR.opening_gate(row_ov, segs)
    assert not any("O2:" in e for e in errs_ov)


def test_opening_gate_o3_min_8_distinct_images_in_first_40s():
    script = [f"Câu {i}." for i in range(1, 16)]
    durs = [2.5] * 15
    segs = _segs_from_durs(durs)
    # Chỉ có 4 ảnh khác nhau trong 40s đầu (câu 1-15 kéo dài 37.5s)
    media_4 = {
        "1": {"path": "a.jpg"}, "2": {"path": "b.jpg"}, "3": {"path": "c.jpg"}, "4": {"path": "d.jpg"},
        "5": {"path": "a.jpg"}, "6": {"path": "b.jpg"}, "7": {"path": "c.jpg"}, "8": {"path": "d.jpg"}
    }
    row_fail = {"id": "test_o3_f", "title": "Lịch Sử", "script": script, "media": media_4}
    errs, _ = HBR.opening_gate(row_fail, segs)
    assert any("O3: 0–40s chỉ có 4 hình khác nhau (yêu cầu ≥ 8" in e for e in errs)

    # 8 ảnh khác nhau trong 40s đầu -> ĐẠT O3
    media_8 = {str(i): {"path": f"img_{i}.jpg"} for i in range(1, 9)}
    row_pass = {"id": "test_o3_p", "title": "Lịch Sử", "script": script, "media": media_8}
    errs_p, _ = HBR.opening_gate(row_pass, segs)
    assert not any("O3:" in e for e in errs_p)


def test_opening_gate_o4_title_keywords_in_first_15s():
    script_miss = ["Trời hôm nay nhiều mây đen.", "Gió thổi mạnh qua cành cây.", "Mọi người vội vã về nhà.", "Đường phố vắng lặng."]
    durs = [4.0, 4.0, 4.0, 4.0]
    segs = _segs_from_durs(durs)
    media = {str(i): {"path": f"img_{i}.jpg"} for i in range(1, 10)}
    row_miss = {"id": "test_o4_m", "title": "Bí Ẩn Kim Tự Tháp Ai Cập", "script": script_miss, "media": media}
    _, warns = HBR.opening_gate(row_miss, segs)
    assert any("O4: Chưa thấy từ khoá chính của title" in w for w in warns)

    # Có nói từ khoá chính trước 15s (ví dụ \"16 năm\" qua từ \"mười sáu năm\") -> ĐẠT O4 (không cảnh báo)
    script_hit = ["Cỗ xe dừng lại ở bìa rừng.", "Mười sáu năm cậu chưa từng mở miệng nói.", "Hôm nay là ngày định mệnh."]
    row_hit = {"id": "test_o4_h", "title": "Hoàng Tử Temiya | 16 Năm Giả Câm", "script": script_hit, "media": media}
    _, warns_hit = HBR.opening_gate(row_hit, segs[:3])
    assert not any("O4:" in w for w in warns_hit)


def test_opening_gate_o5_ref_assets_forbidden():
    script = [f"Câu {i}." for i in range(1, 10)]
    durs = [3.0] * 9
    segs = _segs_from_durs(durs)
    # Media có chứa đường dẫn /refs/ hoặc REF_ -> LỖI O5
    media_ref = {
        "1": {"path": "research/ai_media/p2_kisa/refs/REF_KISA_R1.jpg"},
        "2": {"path": "clean_image.jpg"}
    }
    row = {"id": "test_o5", "title": "Kisa", "script": script, "media": media_ref}
    errs, _ = HBR.opening_gate(row, segs)
    assert any("O5: media câu 1 dùng ảnh ref nhân vật" in e and "cấm ảnh ref" in e for e in errs)

    # Ảnh sạch -> ĐẠT O5
    media_clean = {str(i): {"path": f"clean_{i}.jpg"} for i in range(1, 9)}
    row_clean = {"id": "test_o5_clean", "title": "Kisa", "script": script, "media": media_clean}
    errs_c, _ = HBR.opening_gate(row_clean, segs)
    assert not any("O5:" in e for e in errs_c)


def test_opening_gate_o6_meta_words_warn():
    # Lời meta trong 40s đầu: \"video này\", \"chương một\", \"đăng ký\" -> CẢNH BÁO O6
    script = ["Chào bạn đến với video này.", "Hôm nay chúng ta sẽ khám phá.", "Hãy bấm đăng ký kênh nhé."]
    durs = [3.0, 3.0, 3.0]
    segs = _segs_from_durs(durs)
    media = {str(i): {"path": f"img_{i}.jpg"} for i in range(1, 9)}
    row = {"id": "test_o6", "title": "Khám Phá", "script": script, "media": media}
    _, warns = HBR.opening_gate(row, segs)
    assert any("O6: câu 1" in w and "video này" in w for w in warns)
    assert any("O6: câu 2" in w and "chúng ta sẽ" in w for w in warns)
    assert any("O6: câu 3" in w and "đăng ký" in w for w in warns)


def test_opening_gate_o7_roadmap_and_ask_warn():
    # Có thẻ ask hoặc timeline trong 40s đầu -> CẢNH BÁO O7
    script = ["Đêm ở thành phố.", "Liệu ai có thể giải được bí ẩn này?", "Câu trả lời nằm ở phía trước."]
    durs = [3.0, 3.5, 3.0]
    segs = _segs_from_durs(durs)
    media = {str(i): {"path": f"img_{i}.jpg"} for i in range(1, 9)}
    visuals = {"2": {"type": "ask", "overlay": True}}
    row = {"id": "test_o7", "title": "Bí Ẩn", "script": script, "media": media, "visuals": visuals}
    _, warns = HBR.opening_gate(row, segs)
    assert any("O7: câu 2" in w and "thẻ visual \x27ask\x27" in w for w in warns)


def test_opening_gate_o8_export_first40_contact_sheet(tmp_path):
    script = [f"Câu số {i} nội dung thử nghiệm." for i in range(1, 15)]
    durs = [3.0] * 14
    segs = _segs_from_durs(durs)
    media = {str(i): {"path": f"img_{i}.jpg"} for i in range(1, 9)}
    row = {"id": "test_first40", "title": "Thử Nghiệm", "script": script, "media": media}
    out_img = tmp_path / "review_test_first40" / "first40.jpg"
    p = HBR.export_first40(row, segs, out_path=out_img)
    assert p.exists()
    assert p.stat().st_size > 0
    im = Image.open(p)
    # Lưới 5x4 với CELL 384x216 -> 1920x864
    assert im.size == (1920, 864)


def test_opening_gate_bypassed_when_off():
    # Plan vi phạm mọi luật O1, O2, O3, O5 nhưng có opening_gate: off
    row = {
        "id": "test_off",
        "title": "Bí Ẩn",
        "script": ["Câu một không có ảnh.", "Câu hai.", "Câu ba."],
        "media": {"1": {"path": "refs/REF_TEST.jpg"}},
        "opening_gate": "off"
    }
    segs = _segs_from_durs([5.0, 5.0, 5.0])
    errs, warns = HBR.opening_gate(row, segs)
    assert errs == []
    assert warns == []
    assert HBR.opening_gate_issues(row, segs) == []


def test_120s_chu_khoa_gate_with_kinetic_true():
    # Khi kinetic: True, trong 120s đầu chữ khoá chiếm > 15% -> LỖI cổng nhịp
    # Tổng thời lượng 10s: 3s câu 1 có ảnh, 7s còn lại là chữ khoá (70% > 15%)
    script = ["Câu có ảnh.", "Câu chữ khoá 1.", "Câu chữ khoá 2."]
    durs = [3.0, 4.0, 3.0]
    segs = _segs_from_durs(durs)
    media = {"1": {"path": "m1.jpg"}}
    # Câu 2 bị ngắt bởi visual word không overlay hoặc không có media -> chữ khoá
    visuals = {"2": {"type": "word"}}
    row = {"id": "test_kin", "script": script, "media": media, "visuals": visuals, "kinetic": True}
    errs = HBR.pace_gate_issues(row, segs)
    assert any("120s đầu: chữ khoá" in e and "(> 15%)" in e and "kinetic không miễn trừ" in e for e in errs)

    # Nếu pace_gate: off thì bỏ qua
    row["pace_gate"] = "off"
    assert not any("120s đầu: chữ khoá" in e for e in HBR.pace_gate_issues(row, segs))


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="cần ffmpeg")
def test_opening_gate_o9_solid_frame_limit_in_first_40s(tmp_path):
    import subprocess
    # 1. Tạo video vi phạm: 0-1.0s có texture, 1.0-1.5s là màu đen đồng màu (0.5s > 0.3s)
    bad_mp4 = tmp_path / "bad_solid.mp4"
    cmd_bad = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", "testsrc=duration=1:size=320x180:rate=10",
        "-f", "lavfi", "-i", "color=c=black:duration=0.5:size=320x180:rate=10",
        "-f", "lavfi", "-i", "testsrc=duration=1:size=320x180:rate=10",
        "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1[v]",
        "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(bad_mp4)
    ]
    subprocess.run(cmd_bad, check=True)

    script = [f"Câu {i}." for i in range(1, 10)]
    durs = [2.5] * 9
    segs = _segs_from_durs(durs)
    media = {str(i): {"path": f"img_{i}.jpg"} for i in range(1, 9)}
    row_bad = {"id": "test_o9_bad", "title": "Test", "script": script, "media": media}

    errs, _ = HBR.opening_gate(row_bad, segs, video_path=bad_mp4)
    assert any("O9: 0–40s có khung đồng màu" in e and "(> 0.3s)" in e for e in errs)

    # 2. Tạo video đạt: testsrc liên tục (không có đoạn đồng màu nào > 0.3s)
    good_mp4 = tmp_path / "good.mp4"
    cmd_good = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", "testsrc=duration=2.5:size=320x180:rate=10",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(good_mp4)
    ]
    subprocess.run(cmd_good, check=True)

    row_good = {"id": "test_o9_good", "title": "Test", "script": script, "media": media}
    errs_good, _ = HBR.opening_gate(row_good, segs, video_path=good_mp4)
    assert not any("O9:" in e for e in errs_good)

    # 3. Khi opening_gate: off thì bỏ qua cả O9
    row_bad["opening_gate"] = "off"
    errs_off, _ = HBR.opening_gate(row_bad, segs, video_path=bad_mp4)
    assert not any("O9:" in e for e in errs_off)


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="cần ffmpeg")
def test_opening_gate_o9_catches_blank_theme_missing_media_case(tmp_path):
    """Tái hiện đúng ca câu 2 P1 (Task 029b): khung nền theme trống (saffron) bị bỏ sót
    do std > 20 (dải chuyển màu), nhưng sim > 0.90 và low_detail_ratio >= 0.70 phải bị O9 bắt."""
    import subprocess
    import numpy as np
    from PIL import Image

    # 1. Tạo khung nền saffron tham chiếu (tương tự f_04_4s trong render_029)
    blank_png = tmp_path / "blank_saffron_ref.png"
    arr = np.zeros((180, 320, 3), dtype=np.uint8)
    arr[:, :] = [236, 230, 216]
    arr[140:, :] = [180, 175, 165]
    Image.fromarray(arr).save(blank_png)

    # 2. Tạo video mô phỏng ca lỗi câu 2:
    # 0-1.0s có ảnh/texture (câu 1 cine), 1.0-1.8s rơi về nền theme trống (câu 2 mất hình 0.8s > 0.3s), 1.8-2.8s ảnh (câu 3)
    bad_mp4 = tmp_path / "missing_media_s2.mp4"
    cmd_bad = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", "testsrc=duration=1:size=320x180:rate=10",
        "-loop", "1", "-t", "0.8", "-i", str(blank_png),
        "-f", "lavfi", "-i", "testsrc=duration=1:size=320x180:rate=10",
        "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1[v]",
        "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(bad_mp4)
    ]
    subprocess.run(cmd_bad, check=True)

    script = ["Cỗ xe dừng lại ở bìa rừng.", "Người đánh xe bước xuống.", "Ông gỡ hết vàng ngọc trên người hoàng tử."] + [f"Câu {i}." for i in range(4, 10)]
    durs = [2.0, 1.5, 2.5] + [2.0] * 6
    segs = _segs_from_durs(durs)
    media = {
        "1": {"path": "f_C1_169.png", "cine": {"cam": "dolly_parallax", "depth": True}},
        "2": {"path": "co_driver_1_897081ad_1K.jpg"},
        "3": {"path": "f_C2_1_e1c1e79a_1K.jpg", "cine": {"cam": "push_in", "depth": True}},
    }
    for i in range(4, 9):
        media[str(i)] = {"path": f"img_{i}.jpg"}

    row_bad = {
        "id": "test_ca2_bad",
        "title": "Hoàng tử câm",
        "script": script,
        "media": media,
        "theme": "saffron",
    }

    # Bắt buộc O9 phải bắt được khung nền theme trống (trước đây bỏ sót vì std=24 > 20)
    errs, _ = HBR.opening_gate(row_bad, segs, video_path=bad_mp4)
    assert any("O9: 0–40s có khung đồng màu hoặc nền theme trống" in e and "(> 0.3s)" in e for e in errs), f"Lỗi không bắt được: {errs}"

    # 3. Tạo video đạt khi câu 2 hiển thị ảnh đầy đủ (testsrc liên tục không có khoảng hở nền)
    good_mp4 = tmp_path / "fixed_media_s2.mp4"
    cmd_good = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", "testsrc=duration=2.8:size=320x180:rate=10",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(good_mp4)
    ]
    subprocess.run(cmd_good, check=True)

    row_good = dict(row_bad)
    row_good["id"] = "test_ca2_good"
    errs_good, _ = HBR.opening_gate(row_good, segs, video_path=good_mp4)
    assert not any("O9:" in e for e in errs_good), f"Không được báo lỗi O9 khi video đủ hình: {errs_good}"
