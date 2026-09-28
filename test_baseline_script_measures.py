"""S8 + chẩn đoán code trên script baseline (ticket 20): chỉ exact/revision/
rendered, không bao giờ source_only; n theo từng tiêu chí; tách theo
provenance và Domain; rendered bỏ kiểm markup; không điểm/ngưỡng."""
import json

import baseline_script_measures as bm

ROWS = [
    {"domain": "FS", "script_provenance": "exact", "script": "Hôm nay **Tuổi Tý** may.\nNgày 25/07 đẹp.\nHết."},
    {"domain": "FS", "script_provenance": "revision", "script": "Câu lặp lại nhé.\nCâu lặp lại nhé.\nKết"},
    {"domain": "FS", "script_provenance": "rendered", "script": "hôm nay tuổi tý may. ngày hai mươi lăm đẹp."},
    {"domain": "FS", "script_provenance": "source_only", "script": None,
     "source_reference": {"kind": "source_only", "text": "Đoạn trích *** 1"}},
    {"domain": "BUD", "script_provenance": "exact", "script": "Phương án A: buông bỏ.\nHết."},
    {"domain": "BUD", "script_provenance": "missing", "script": None},
]


def _report():
    return bm.build_report({"created_at": "snap", "rows": ROWS}, created_at="t")


def test_only_published_script_provenances_are_measured():
    r = _report()
    assert r["excluded_rows"] == {"source_only": 1, "missing": 1}
    assert sum(v["repeated_sentence"]["n"] for v in r["by_provenance"].values()) == 4
    assert "source_only" not in r["by_provenance"]


def test_source_only_text_is_never_measured_even_if_placed_in_script():
    rows = [{"domain": "FS", "script_provenance": "source_only", "script": "Câu lặp.\nCâu lặp."}]
    r = bm.build_report({"rows": rows})
    assert r["by_domain"] == {} and r["excluded_rows"] == {"source_only": 1}


def test_n_is_per_criterion_and_rendered_excludes_markup_with_reason():
    fs = _report()["by_domain"]["FS"]
    assert fs["repeated_sentence"]["n"] == 3
    assert fs["leftover_markup"]["n"] == 2
    assert fs["leftover_markup"]["excluded"] == {bm.RENDERED_EXCLUDED["leftover_markup"]: 1}
    assert fs["density_numbers"]["n"] == 2 and fs["density_names"]["n"] == 3
    assert fs["repeated_sentence"]["count_true"] == 1 and fs["truncated"]["count_true"] == 1


def test_split_by_domain_and_provenance():
    r = _report()
    assert set(r["by_domain_and_provenance"]) == {"FS|exact", "FS|revision", "FS|rendered", "BUD|exact"}
    assert r["by_domain"]["BUD"]["leftover_markup"]["count_true"] == 1


def test_no_score_threshold_or_pass_verdict():
    blob = json.dumps(_report()).lower()
    for forbidden in ("score", "threshold", "\"pass\"", "\"fail\"", "\"ok\""):
        assert forbidden not in blob


def test_command_writes_versioned_report_to_gitignored_dir(tmp_path):
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"created_at": "x", "rows": ROWS}, ensure_ascii=False), encoding="utf-8")
    assert bm.main(["--snapshot", str(snap), "--out-dir", str(tmp_path / "m")]) == 0
    files = list((tmp_path / "m").glob(f"baseline_script_measures_v{bm.REPORT_VERSION}_*.json"))
    assert len(files) == 1
    rep = json.loads(files[0].read_text(encoding="utf-8"))
    assert rep["report_version"] == bm.REPORT_VERSION and rep["created_at"]
    assert bm.DEFAULT_OUT_DIR.parts[-2:] == ("baseline", "measures")
