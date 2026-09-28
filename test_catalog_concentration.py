"""Concentration signal (ticket 19): đọc record Script PASS gần nhất của Domain
(window theo số lượng), tỷ trọng theo fingerprint, ghi record `layer: catalog`
advisory -- không cờ đạt/không đạt, không ngưỡng, không đường nào tới Gate
status hay prompt writer."""
import inspect
import json

import pytest

import catalog_concentration as cc
import content_quality_gate as cqg
import script_quality_gate as sqg


def _pass(script, domain="FS"):
    return sqg.evaluate(script, domain=domain, identity={"content_id": script[:8]}, invariant=None,
                        content_quality_record_id="c")


def test_each_script_pass_writes_an_advisory_catalog_record_with_shares():
    _pass("Bạn có biết hôm nay tuổi Tý may mắn?\nHết.")
    _pass("Bạn có biết hôm nay tuổi Ngọ cần thận trọng?\nHết.")
    gate = _pass("Ba con giáp hợp nhau hôm nay.\nHết.")
    catalog = [r for r in cqg.read_records("FS") if r["layer"] == "catalog"]
    assert len(catalog) == 3
    last = catalog[-1]
    assert last["advisory"] is True and last["window"]["records_in_window"] == 3
    assert last["script_quality_record_id"] == gate.record["quality_record_id"]
    shares = {s["fingerprint"]: s for s in last["fingerprint_shares"]}
    assert shares["bạn có biết hôm nay"]["count"] == 2
    assert shares["bạn có biết hôm nay"]["share"] == pytest.approx(2 / 3, abs=1e-4)
    assert last["this_fingerprint_share"] == pytest.approx(1 / 3, abs=1e-4)


def test_window_is_by_count_and_only_script_pass_records_of_the_domain():
    for i in range(5):
        _pass(f"Mở đầu số {i} khác nhau hoàn toàn.\nHết.")
    _pass("Câu lặp.\nCâu lặp.")  # S8 FAIL -> không nằm trong window, không có catalog
    _pass("Mở đầu bên BUD.\nHết.", domain="BUD")
    recent = cc.recent_script_records("FS", window=3)
    assert len(recent) == 3 and all(r["gate_status"] == cqg.PASS for r in recent)
    assert [r["fingerprint"] for r in recent] == [f"mở đầu số {i} khác" for i in (2, 3, 4)]
    with pytest.raises(ValueError):
        cc.recent_script_records("FS", window=0)


def test_catalog_record_has_no_pass_fail_threshold_or_lists():
    _pass("Bạn có biết điều này?\nHết.")
    rec = [r for r in cqg.read_records("FS") if r["layer"] == "catalog"][-1]
    assert "gate_status" not in rec and "reason_codes" not in rec
    blob = json.dumps(rec).lower()
    for forbidden in ("threshold", "whitelist", "blacklist", "\"pass\"", "\"fail\""):
        assert forbidden not in blob


def test_catalog_signal_never_reaches_gate_status_or_writer_prompt(monkeypatch):
    # Signal lỗi hay bất thường cũng không đổi Gate decision.
    monkeypatch.setattr(cc, "build_record", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("hỏng")))
    gate = _pass("Câu một.\nCâu hai.")
    assert gate.publishable and gate.extra["catalog"] is None
    # Không module sinh nội dung nào đọc catalog.
    import short_judge_panel_engine
    import script_rewrite
    for mod in (short_judge_panel_engine, script_rewrite):
        assert "catalog" not in inspect.getsource(mod)
    assert "catalog" not in inspect.getsource(sqg.decide)


def test_opening_pattern_descriptions_are_kept_raw():
    gate = _pass("Bạn có biết?\nHết.")
    rec = cqg.read_records("FS")
    script_rec = [r for r in rec if r["layer"] == "script"][-1]
    script_rec["opening_pattern"] = {"description": "câu hỏi tu từ", "evidence": "Bạn có biết?"}
    catalog = cc.build_record(script_rec)
    assert catalog["opening_pattern_descriptions"] == [] or all(d["description"] for d in catalog["opening_pattern_descriptions"])
    assert gate.publishable
