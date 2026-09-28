"""Baseline snapshot (ticket 10): ghép registry, ledger, metrics Hub, retention/
traffic, .srt/manifest, file staged; mỗi trường thiếu có lý do; thống kê theo
Domain; script_provenance (source_only không bao giờ là script đã đăng); tập
gán nhãn theo D37. Fixture nhỏ, không kết nối Hub."""
import json

import pytest

import baseline_snapshot as bs

PR5 = """### #1 `MENH_Kim_MauSacHopMenh_01` (element_color)
1. "..." — ✗(d)
**Subtotal: 3**
"""


def _w(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def raw_dir(tmp_path):
    raw = tmp_path / "raw"
    _w(raw / "registry" / "Phong Thủy" / "registry.json", {
        "MENH_Kim_MauSacHopMenh_01": {"key": "MENH_Kim_MauSacHopMenh_01", "episode": "MENH_Kim_MauSacHopMenh",
                                      "segment_index": 1, "status": "uploaded", "video_id": "fs1",
                                      "final_script": "Script đã đăng FS1.", "hook_score": 8.0,
                                      "publish_at": "2026-07-28T01:00:00Z"},
        "THAN20260724_12ViThan_01": {"key": "THAN20260724_12ViThan_01", "episode": "THAN20260724_12ViThan",
                                     "segment_index": 1, "status": "uploaded", "video_id": "fs2"},
        "CONGIAP20260724_ConGiap_01": {"key": "CONGIAP20260724_ConGiap_01", "episode": "CONGIAP20260724_ConGiap",
                                       "segment_index": 1, "status": "uploaded", "video_id": "fs3"},
        "KINHDICH_X_01": {"key": "KINHDICH_X_01", "episode": "KINHDICH_X", "segment_index": 1, "status": "needs_review"},
    })
    _w(raw / "registry" / "Phật giáo" / "registry.json", {
        f"EP{i}_Short_01": {"key": f"EP{i}_Short_01", "episode": f"EP{i}_Short", "segment_index": 1,
                            "status": "uploaded", "video_id": f"bud{i}", "publish_at": "2026-07-28T00:00:00Z"}
        for i in range(12)
    })
    _w(raw / "rendered" / "THAN20260724_12ViThan" / "01_short.srt",
       "1\n00:00:00,000 --> 00:00:02,000\nlời đã đọc một\n\n2\n00:00:02,000 --> 00:00:04,000\nlời đã đọc hai\n")
    _w(raw / "rendered" / "THAN20260724_12ViThan" / "01_short.json", {"voice": "Sơn"})
    _w(raw / "staged" / "Phong Thủy" / "CONGIAP20260724_ConGiap_Short.txt", "*** 1\n\nĐoạn staged.\n")
    _w(raw / "hub" / "content_revisions.json", [
        {"youtube_video_id": "bud0", "audio_script": "Bản trước khi đăng.", "created_at": "2026-07-27T00:00:00Z"},
        {"youtube_video_id": "bud0", "audio_script": "Bản sửa sau khi đăng.", "created_at": "2026-07-29T00:00:00Z"},
        {"youtube_video_id": "bud1", "audio_script": "Chỉ có bản sau đăng.", "created_at": "2026-08-01T00:00:00Z"},
    ] + [{"youtube_video_id": f"bud{i}", "audio_script": f"BUD {i}.", "created_at": "2026-07-01T00:00:00Z"}
         for i in range(2, 12)])
    pcts = {"bud0": 31.2, "bud1": 24.8, **{f"bud{i}": 40.0 + i for i in range(2, 12)}, "fs1": 55.0}
    metrics = []
    for vid, pct in pcts.items():
        metrics += [{"youtube_video_id": vid, "date": "2026-07-28", "views": 100, "average_view_percentage": pct},
                    {"youtube_video_id": vid, "date": "2026-07-29", "views": 0, "average_view_percentage": None}]
    _w(raw / "hub" / "video_daily_metric.json", metrics)
    _w(raw / "youtube_analytics_phong_thuy_1.json", {"videos": [
        {"youtube_video_id": "fs1", "retention_curve": {"status": "ok", "data": [{"elapsedVideoTimeRatio": 0.01}]},
         "traffic_sources": {"status": "missing", "reason": "no_data"}}]})
    _w(raw / "known_violations.json", {"fs2": {"safety": 1, "source": "audit"}})
    ledger = tmp_path / "ledger.json"
    _w(ledger, {"items": [{"content_id": "CL_D1_luat", "youtube_video_id": "cl1", "category": "luat_hinh_su",
                           "final_publish_datetime_utc": "2026-07-28T02:00:00Z"},
                          {"content_id": "FS_D1_menh", "youtube_video_id": "fs1", "category": "element_color"}]})
    pr5 = tmp_path / "pr5.md"
    _w(pr5, PR5)
    return raw, ledger, pr5


def _snap(raw_dir):
    raw, ledger, pr5 = raw_dir
    return bs.build_snapshot(bs.load_raw(raw, ledger_path=ledger, pr5_path=pr5), created_at="t0")


def _row(snap, vid):
    return next(r for r in snap["rows"] if r["youtube_video_id"] == vid)


def test_one_row_per_published_short_including_ledger_only(raw_dir):
    snap = _snap(raw_dir)
    vids = [r["youtube_video_id"] for r in snap["rows"]]
    assert sorted(vids) == sorted(["fs1", "fs2", "fs3", "cl1"] + [f"bud{i}" for i in range(12)])
    assert _row(snap, "cl1")["domain"] == "CL" and _row(snap, "cl1")["ledger_category"] == "luat_hinh_su"
    assert snap["snapshot_version"] == bs.SNAPSHOT_VERSION and snap["created_at"] == "t0"


def test_script_provenance_hierarchy(raw_dir):
    snap = _snap(raw_dir)
    fs1, fs2, fs3 = _row(snap, "fs1"), _row(snap, "fs2"), _row(snap, "fs3")
    assert (fs1["script_provenance"], fs1["verified"], fs1["script"]) == ("exact", True, "Script đã đăng FS1.")
    assert (fs2["script_provenance"], fs2["verified"]) == ("rendered", True)
    assert fs2["script"] == "lời đã đọc một lời đã đọc hai"
    b0, b1 = _row(snap, "bud0"), _row(snap, "bud1")
    assert (b0["script_provenance"], b0["verified"], b0["script"]) == ("revision", True, "Bản trước khi đăng.")
    assert (b1["script_provenance"], b1["verified"]) == ("revision", False), "chỉ có revision sau khi đăng"
    cl1 = _row(snap, "cl1")
    assert cl1["script_provenance"] == "missing" and cl1["script"] is None and cl1["script_missing_reason"]


def test_source_only_is_never_the_published_script(raw_dir):
    fs3 = _row(_snap(raw_dir), "fs3")
    assert fs3["script_provenance"] == "source_only"
    assert fs3["script"] is None, "source_only không bao giờ ở trường script đã đăng (D79)"
    assert fs3["source_reference"]["kind"] == "source_only" and "Đoạn staged" in fs3["source_reference"]["text"]
    assert fs3["script_missing_reason"]


def test_missing_fields_carry_a_reason_never_zero(raw_dir):
    snap = _snap(raw_dir)
    fs2 = _row(snap, "fs2")
    assert bs.is_missing(fs2["views"]) and fs2["views"]["reason"]
    assert bs.is_missing(fs2["hook_score"])
    assert bs.is_missing(fs2["retention_curve"]) and "không có trong output analytics" in fs2["retention_curve"]["reason"]
    fs1 = _row(snap, "fs1")
    assert fs1["retention_curve"] == [{"elapsedVideoTimeRatio": 0.01}]
    assert bs.is_missing(fs1["traffic_sources"]) and "no_data" in fs1["traffic_sources"]["reason"]
    assert fs1["views"] == 100 and fs1["average_view_percentage"] == pytest.approx(55.0)
    cl1 = _row(snap, "cl1")
    assert bs.is_missing(cl1["domain"]) is False and bs.is_missing(cl1["generator"])


def test_known_violations_from_pr5_and_audit(raw_dir):
    snap = _snap(raw_dir)
    assert _row(snap, "fs1")["known_cr1_violations"] == 3 and _row(snap, "fs1")["violations_source"] == "PR-5"
    assert _row(snap, "fs2")["known_safety_violations"] == 1
    assert bs.is_missing(_row(snap, "fs3")["known_cr1_violations"])


def test_domain_stats_median_quantiles_provenance_and_publish_rate(raw_dir):
    stats = _snap(raw_dir)["stats"]
    bud = stats["BUD"]
    assert bud["published"] == 12 and bud["average_view_percentage"]["n"] == 12
    assert bud["average_view_percentage"]["median"] == pytest.approx(statistics_median([31.2, 24.8] + [40.0 + i for i in range(2, 12)]))
    assert bud["script_provenance"]["revision"] == 12
    fs = stats["FS"]
    assert fs["script_provenance"] == {"exact": 1, "revision": 0, "rendered": 1, "source_only": 1, "missing": 0}
    assert fs["registry_status_counts"] == {"uploaded": 3, "needs_review": 1}
    assert fs["publish_rate"] == pytest.approx(0.75)
    assert bs.is_missing(stats["CL"]["publish_rate"])


def statistics_median(v):
    import statistics
    return statistics.median(v)


def test_labeling_set_follows_d37_and_excludes_source_only(raw_dir):
    labels = bs.labeling_set(_snap(raw_dir))
    assert [i["youtube_video_id"] for i in labels["FS"]] == ["fs1"]  # PR-5 + có script đã đăng
    bud_ids = [i["youtube_video_id"] for i in labels["BUD"]]
    assert bud_ids[:2] == ["bud0", "bud1"], "2 video retention 31%/25% bắt buộc"
    assert len(bud_ids) == 10 and len(set(bud_ids)) == 10
    assert labels["CL"] == []  # cl1 không có script đã đăng
    for group in ("FS", "BUD", "CL"):
        for item in labels[group]:
            assert item["script_provenance"] in ("exact", "revision", "rendered")
            assert "views" not in item and "average_view_percentage" not in item, "gán nhãn mù"
    assert any("FS" in n for n in labels["notes"])


def test_command_writes_versioned_snapshot_to_given_dir(raw_dir, tmp_path):
    raw, ledger, pr5 = raw_dir
    out = tmp_path / "snaps"
    assert bs.main(["--raw-dir", str(raw), "--out-dir", str(out), "--ledger", str(ledger), "--pr5", str(pr5)]) == 0
    files = sorted(p.name for p in out.iterdir())
    assert any(f.startswith(f"baseline_snapshot_v{bs.SNAPSHOT_VERSION}_") for f in files)
    assert any(f.startswith("labeling_set_") for f in files)


def test_default_output_is_gitignored_baseline_dir():
    assert bs.DEFAULT_OUT_DIR.parts[-2:] == ("baseline", "snapshots")
    assert bs.DEFAULT_RAW_DIR.parts[-2:] == ("baseline", "raw")


def test_parse_pr5_reads_every_subtotal_form_of_the_committed_report():
    """Review 10: report thật có "**Subtotal (a/d): 0.**" và "**Subtotal: 3 confirmed,
    0 disputed**" -- phải đọc đúng cả 12 key, không key nào None."""
    parsed = bs.parse_pr5(bs.PR5_PATH.read_text(encoding="utf-8"))
    assert len(parsed) == 12 and all(v["cr1"] is not None for v in parsed.values())
    assert parsed["CHUYENKE_Chicgingkhinnginmlunbtan_01"]["cr1"] == 0
    assert parsed["MENH_Kim_MauSacHopMenh_01"]["cr1"] == 3  # "3 confirmed, 0 disputed"
    assert sum(v["cr1"] for v in parsed.values()) == 31, "PR-5 v4 xác nhận 31 vi phạm"


def test_unreadable_pr5_subtotal_is_missing_with_reason_not_none():
    assert bs.is_missing(bs._cr1({"cr1": None, "source": "PR-5"}, None))


def test_naive_revision_timestamp_does_not_abort_the_snapshot():
    out = bs.resolve_script({"key": "k", "episode": "e", "segment_index": 1}, "v", "2026-07-28T00:00:00Z",
                            [{"youtube_video_id": "v", "audio_script": "S.", "created_at": "2026-07-27 10:00:00"}], {}, {})
    assert out["script_provenance"] == "revision" and out["verified"] is True
