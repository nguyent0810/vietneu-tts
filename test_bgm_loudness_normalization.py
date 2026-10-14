"""Regression test cho G4 (Audio Generation remediation, finding E2):
mỗi track BGM Short giờ có gain RIÊNG tính từ loudness đo thật (EBU R128,
ffmpeg ebur128), đưa về cùng 1 mức "nền" mục tiêu với giới hạn true-peak
chống clip -- thay vì trước đây MỌI track (7 track, chênh nhau thật ~8 LU
độ to) đều bị áp CÙNG 1 hệ số 10% cố định
(``video_tool_clone/core/pipeline/bgm.py::DEFAULT_BGM_VOLUME_PCT``),
khiến độ to hiệu dụng ra video KHÔNG NHẤT QUÁN giữa các Short tuỳ track
nào rơi trúng vòng xoay.

Đo thật (không đoán mù), lưu vào bgm_tracks.py tại thời điểm remediation:
    track                      | integrated_lufs | true_peak_dbfs
    meditation_impromptu_01    | -23.3            | -2.1
    meditation_impromptu_02    | -23.0            | -2.4
    meditation_impromptu_03    | -22.5            | -1.0
    asian_drums                | -22.2            | -0.3
    comfortable_mystery_4      | -15.3            | -0.1
    deliberate_thought         | -17.7            | -2.1
    thinking_music             | -20.5            | -0.1
-> chênh lệch integrated_lufs thật giữa các track: 8.0 LU -- xác nhận
đúng quy mô bất nhất mà audit/Codex đã đo (mean_volume, thước đo khác
nhưng cùng xác nhận ~8-8.6dB chênh lệch thật)."""
import bgm_tracks
import short_batch_runner as sbr


# ─── _compute_gain_db(): logic tính gain cốt lõi ──────────────────────

def test_gain_targets_the_configured_loudness_when_no_clipping_risk():
    gain = bgm_tracks._compute_gain_db(integrated_lufs=-30.0, true_peak_dbfs=-10.0)
    assert gain == bgm_tracks.TARGET_BGM_INTEGRATED_LUFS - (-30.0)


def test_gain_is_capped_by_true_peak_ceiling_even_if_target_wants_more():
    """Track RẤT êm (LUFS thấp) nhưng có 1 đỉnh gần 0dBFS (transient) --
    nếu áp thẳng gain để đạt target loudness sẽ đẩy peak vượt ngưỡng an
    toàn -- PHẢI bị giới hạn (chấp nhận chưa đạt đúng target loudness còn
    hơn là clip)."""
    quiet_but_peaky_lufs = -45.0  # cần gain rất lớn để đạt target
    hot_peak = -0.5
    gain = bgm_tracks._compute_gain_db(quiet_but_peaky_lufs, hot_peak)
    resulting_peak = hot_peak + gain
    assert resulting_peak <= bgm_tracks.SAFE_TRUE_PEAK_CEILING_DBTP + 1e-9, (
        f"gain={gain} đẩy peak lên {resulting_peak} dBTP, VƯỢT trần an toàn "
        f"{bgm_tracks.SAFE_TRUE_PEAK_CEILING_DBTP} -- rủi ro clip"
    )
    # Gain bị giới hạn PHẢI nhỏ hơn hẳn gain "lý tưởng" nếu không giới hạn.
    unclamped_gain_for_target = bgm_tracks.TARGET_BGM_INTEGRATED_LUFS - quiet_but_peaky_lufs
    assert gain < unclamped_gain_for_target


def test_gain_never_pushes_true_peak_above_safe_ceiling_for_any_reasonable_input():
    """Quét 1 lưới input hợp lý (LUFS -50..-5, peak -20..0) -- bất biến bắt
    buộc: peak sau gain KHÔNG BAO GIỜ vượt trần an toàn."""
    for lufs in range(-50, -4, 5):
        for peak in range(-20, 1, 2):
            gain = bgm_tracks._compute_gain_db(float(lufs), float(peak))
            assert peak + gain <= bgm_tracks.SAFE_TRUE_PEAK_CEILING_DBTP + 1e-9


# ─── gain_db_to_volume_pct(): quy đổi dB -> % tuyến tính ──────────────

def test_zero_gain_db_is_100_percent():
    assert bgm_tracks.gain_db_to_volume_pct(0.0) == 100.0


def test_negative_gain_db_reduces_volume_pct_below_100():
    assert bgm_tracks.gain_db_to_volume_pct(-10.0) < 100.0
    assert bgm_tracks.gain_db_to_volume_pct(-10.0) > 0.0


def test_gain_db_to_volume_pct_is_monotonic():
    values = [bgm_tracks.gain_db_to_volume_pct(db) for db in [-20, -15, -10, -5, 0]]
    assert values == sorted(values)


# ─── Tính tự nhất quán của BGM_BY_TOPIC (dữ liệu đo thật đã lưu) ──────

def test_every_track_gain_db_matches_recomputed_value_from_stored_measurements():
    """Bảo vệ chống lỗi gõ tay: gain_db LƯU SẴN trong mỗi entry phải khớp
    ĐÚNG với _compute_gain_db(integrated_lufs, true_peak_dbfs) của CHÍNH
    entry đó -- nếu ai sửa integrated_lufs/true_peak_dbfs (đo lại) mà quên
    tính lại gain_db, test này phải FAIL."""
    for topic, tracks in bgm_tracks.BGM_BY_TOPIC.items():
        for t in tracks:
            recomputed = bgm_tracks._compute_gain_db(t["integrated_lufs"], t["true_peak_dbfs"])
            assert t["gain_db"] == recomputed, (
                f"{topic}/{t['path'].name}: gain_db lưu ({t['gain_db']}) không khớp "
                f"giá trị tính lại từ integrated_lufs/true_peak_dbfs ({recomputed})"
            )


def test_no_track_exceeds_safe_true_peak_ceiling_after_gain():
    """Bất biến an toàn CHỐNG CLIP cho toàn bộ danh mục track thật (không
    phải input tổng hợp) -- xác nhận KHÔNG track nào trong bgm/ hiện tại
    có nguy cơ vượt ngưỡng an toàn sau khi áp gain đã lưu."""
    for topic, tracks in bgm_tracks.BGM_BY_TOPIC.items():
        for t in tracks:
            resulting_peak = t["true_peak_dbfs"] + t["gain_db"]
            assert resulting_peak <= bgm_tracks.SAFE_TRUE_PEAK_CEILING_DBTP + 1e-9, (
                f"{topic}/{t['path'].name}: peak sau gain = {resulting_peak} dBTP, "
                f"vượt trần an toàn {bgm_tracks.SAFE_TRUE_PEAK_CEILING_DBTP}"
            )


def test_gain_values_are_genuinely_per_track_not_a_single_blanket_value():
    """'Preserve intentional creative differences; do not flatten
    everything blindly' -- xác nhận gain KHÔNG phải 1 hằng số chung (như
    bug gốc E2: mọi track cùng 10%) mà thật sự khác nhau theo độ to gốc
    từng track."""
    all_gains = [t["gain_db"] for tracks in bgm_tracks.BGM_BY_TOPIC.values() for t in tracks]
    assert len(set(all_gains)) > 1, "mọi track có cùng gain_db -- nghi ngờ lại bị áp 1 hệ số chung như bug gốc"


def test_normalized_effective_loudness_is_far_more_consistent_than_raw():
    """Chênh lệch integrated_lufs GỐC giữa các track là ~8 LU (bug thật,
    xác nhận qua đo) -- sau khi áp gain riêng từng track, chênh lệch loudness
    HIỆU DỤNG (integrated_lufs + gain_db) phải giảm mạnh, gần bằng 0
    (không nhất thiết TUYỆT ĐỐI bằng 0 nếu có track bị giới hạn bởi
    true-peak ceiling -- xem test riêng cho trường hợp đó)."""
    all_tracks = [t for tracks in bgm_tracks.BGM_BY_TOPIC.values() for t in tracks]
    raw_lufs = [t["integrated_lufs"] for t in all_tracks]
    effective_lufs = [t["integrated_lufs"] + t["gain_db"] for t in all_tracks]

    raw_spread = max(raw_lufs) - min(raw_lufs)
    effective_spread = max(effective_lufs) - min(effective_lufs)

    assert raw_spread > 5.0, "test cần dữ liệu có chênh lệch gốc đáng kể để có ý nghĩa"
    assert effective_spread < 1.0, (
        f"chênh lệch loudness hiệu dụng sau normalize vẫn còn {effective_spread} LU -- "
        f"chưa nhất quán đủ (gốc chênh {raw_spread} LU)"
    )


# ─── Wiring: short_batch_runner.py::run_video_render() truyền đúng
# --bgm-volume-pct qua subprocess (không cần import render_short.py --
# xem test_short_importance_marker_normalization.py về lý do render_short
# không import được trong .venv này) ───────────────────────────────────

def _fake_completed_process(stdout='{"ok": true}', returncode=0):
    return type("R", (), {"stdout": stdout, "stderr": "", "returncode": returncode})()


def test_run_video_render_passes_bgm_volume_pct_when_provided(tmp_path, monkeypatch):
    captured_cmd = []

    def fake_run(cmd, **kwargs):
        captured_cmd.extend(cmd)
        return _fake_completed_process()

    monkeypatch.setattr(sbr.subprocess, "run", fake_run)

    sbr.run_video_render(
        tmp_path / "a.wav", tmp_path / "a.json", tmp_path / "a.mp4",
        topic="Phật giáo", bgm_path="/bgm/x.mp3", bgm_volume_pct=32.7341,
    )

    assert "--bgm" in captured_cmd
    assert "/bgm/x.mp3" in captured_cmd
    assert "--bgm-volume-pct" in captured_cmd
    idx = captured_cmd.index("--bgm-volume-pct")
    assert captured_cmd[idx + 1] == "32.7341"


def test_run_video_render_omits_bgm_volume_pct_when_not_provided(tmp_path, monkeypatch):
    """Không truyền bgm_volume_pct (None) -- KHÔNG được tự thêm cờ, giữ
    hành vi cũ (render_short.py tự dùng default của BGMConfig)."""
    captured_cmd = []

    def fake_run(cmd, **kwargs):
        captured_cmd.extend(cmd)
        return _fake_completed_process()

    monkeypatch.setattr(sbr.subprocess, "run", fake_run)

    sbr.run_video_render(
        tmp_path / "a.wav", tmp_path / "a.json", tmp_path / "a.mp4",
        topic="Phật giáo", bgm_path="/bgm/x.mp3",
    )

    assert "--bgm-volume-pct" not in captured_cmd


def test_run_video_render_omits_bgm_volume_pct_when_no_bgm_path(tmp_path, monkeypatch):
    captured_cmd = []

    def fake_run(cmd, **kwargs):
        captured_cmd.extend(cmd)
        return _fake_completed_process()

    monkeypatch.setattr(sbr.subprocess, "run", fake_run)

    sbr.run_video_render(
        tmp_path / "a.wav", tmp_path / "a.json", tmp_path / "a.mp4",
        topic="Phật giáo", bgm_path=None, bgm_volume_pct=32.7341,
    )

    assert "--bgm" not in captured_cmd
    assert "--bgm-volume-pct" not in captured_cmd


# ─── resolve_gain_db_for_path() / backfill_bgm_gain_db(): fail-closed
# backfill cho entry["bgm"] ĐÃ LƯU TRƯỚC KHI G4 thêm gain_db vào catalog
# (Codex review round 1 finding High #1 -- xác nhận thật: 28 entry
# Phật giáo/Phong Thuỷ trong registry sản xuất thiếu gain_db; không backfill
# sẽ tái hiện đúng bug E2 mỗi lần resume) ─────────────────────────────

def test_resolve_gain_db_for_path_finds_exact_match():
    real_track = bgm_tracks.BGM_BY_TOPIC["Phật giáo"][0]
    result = bgm_tracks.resolve_gain_db_for_path(str(real_track["path"]), "Phật giáo")
    assert result == real_track["gain_db"]


def test_resolve_gain_db_for_path_fails_closed_for_unknown_path():
    assert bgm_tracks.resolve_gain_db_for_path("/nonexistent/track.mp3", "Phật giáo") is None


def test_resolve_gain_db_for_path_fails_closed_for_unconfigured_topic():
    real_track = bgm_tracks.BGM_BY_TOPIC["Phật giáo"][0]
    assert bgm_tracks.resolve_gain_db_for_path(str(real_track["path"]), "Chủ đề chưa cấu hình") is None


def test_backfill_bgm_gain_db_adds_missing_gain_db_from_catalog():
    """Mô phỏng ĐÚNG hình dạng entry["bgm"] thật trong registry sản xuất
    (path+attribution, KHÔNG có gain_db) -- backfill phải tra đúng track
    và thêm gain_db, báo changed=True."""
    real_track = bgm_tracks.BGM_BY_TOPIC["Phật giáo"][0]
    legacy_bgm_choice = {"path": str(real_track["path"]), "attribution": real_track["attribution"]}

    backfilled, changed = sbr.backfill_bgm_gain_db(legacy_bgm_choice, "Phật giáo")

    assert changed is True
    assert backfilled["gain_db"] == real_track["gain_db"]
    assert backfilled["path"] == legacy_bgm_choice["path"]
    assert backfilled["attribution"] == legacy_bgm_choice["attribution"]


def test_backfill_bgm_gain_db_noop_when_gain_db_already_present():
    already_migrated = {"path": "/x/y.mp3", "attribution": "Z", "gain_db": -12.3}
    backfilled, changed = sbr.backfill_bgm_gain_db(already_migrated, "Phật giáo")
    assert changed is False
    assert backfilled == already_migrated


def test_backfill_bgm_gain_db_noop_when_bgm_choice_is_none():
    backfilled, changed = sbr.backfill_bgm_gain_db(None, "Phật giáo")
    assert changed is False
    assert backfilled is None


def test_backfill_bgm_gain_db_fails_closed_when_path_unresolvable():
    """path không khớp track nào trong catalog hiện tại (vd track đã bị
    xoá khỏi BGM_BY_TOPIC) -- KHÔNG được đoán gain_db, giữ nguyên
    bgm_choice, changed=False."""
    orphaned = {"path": "/bgm/track_da_bi_xoa.mp3", "attribution": "Z"}
    backfilled, changed = sbr.backfill_bgm_gain_db(orphaned, "Phật giáo")
    assert changed is False
    assert "gain_db" not in backfilled


def test_process_one_segment_style_flow_backfills_and_persists_before_render(tmp_path, monkeypatch):
    """Mô phỏng ĐÚNG luồng thật trong process_one_segment (không gọi
    process_one_segment() trực tiếp -- hàm đó quá lớn, kéo theo TTS/hook
    review/SEO/upload không liên quan tới G4; xem lý do tương tự
    resolve_bgm_for_attribution() được tách hàm thuần để test độc lập).
    Xác nhận: entry["bgm"] cũ (thiếu gain_db) được backfill + LƯU LẠI vào
    registry.json trên đĩa TRƯỚC khi bgm_volume_pct được tính cho
    run_video_render() -- đúng thứ tự Codex review yêu cầu."""
    registry_path = tmp_path / "registry.json"
    monkeypatch.setattr(sbr, "_registry_path", lambda t: registry_path)

    real_track = bgm_tracks.BGM_BY_TOPIC["Phật giáo"][0]
    legacy_bgm = {"path": str(real_track["path"]), "attribution": real_track["attribution"]}
    key = "ep01_seg01"
    entry = {"key": key, "status": "audio_ready", "bgm": legacy_bgm}
    registry = {key: entry}
    registry_path.write_text('{"' + key + '": ' + __import__("json").dumps(entry) + "}", encoding="utf-8")

    # Đúng logic trong process_one_segment(): backfill rồi lưu NGAY nếu đổi.
    bgm_choice, changed = sbr.backfill_bgm_gain_db(entry["bgm"], "Phật giáo")
    assert changed is True
    entry["bgm"] = bgm_choice
    registry[key] = entry
    sbr.save_registry_entry(key, entry, "Phật giáo")

    on_disk = __import__("json").loads(registry_path.read_text(encoding="utf-8"))
    assert on_disk[key]["bgm"]["gain_db"] == real_track["gain_db"], (
        "gain_db backfill PHẢI được lưu xuống registry.json thật, không chỉ trong bộ nhớ"
    )

    bgm_volume_pct = (
        bgm_tracks.gain_db_to_volume_pct(bgm_choice["gain_db"])
        if bgm_choice and "gain_db" in bgm_choice else None
    )
    assert bgm_volume_pct is not None, "sau backfill, bgm_volume_pct KHÔNG được là None (mới là bug đã sửa)"
    assert bgm_volume_pct == bgm_tracks.gain_db_to_volume_pct(real_track["gain_db"])
