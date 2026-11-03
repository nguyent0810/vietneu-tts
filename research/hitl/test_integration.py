"""Test tích hợp đầu–cuối #127 + #128 + #132 (replay, không mạng)."""
import json
from pathlib import Path

from research.hitl import reviewer, card
from research.hitl.history import history

STORES = Path(__file__).resolve().parents[1] / "fact_store" / "pilot" / "stores_fixed"


def _candidates(tmp_path):
    d = {"video_id": "vsd_fansipan_v1", "topic_id": "vsd_fansipan", "channel": "vsd", "publish_date": "2026-11-20", "series_context": None,
         "candidates": [{"candidate_id": f"c{i}", "title": f"Fansipan {i}", "thumbnail_text": "LỆCH 4 MÉT?", "first_frame_0_1s": "Bản đồ",
                         "voice_0_3s": "Fansipan cao 3.147,3 m.", "escalation_3_10s": "x", "payoff": "y",
                         "claims": [{"field": "voice_0_3s", "span": "Fansipan cao 3.147,3 m", "fact_ids": "vsd_fansipan_f01"}],
                         "tags_for_history": {"mechanism": "m", "opener_shape": "statement", "first_frame_type": "map", "title_shape": "plain"}} for i in (1, 2, 3)]}
    p = tmp_path / "vsd_fansipan.json"; p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8"); return p, d


def test_end_to_end_flags_reach_card_and_decision_is_hash_bound(tmp_path):
    cands, data = _candidates(tmp_path)
    replay = tmp_path / "replay.json"
    replay.write_text(json.dumps({"videos": [{"video_id": "vsd_fansipan_v1", "candidates": [
        {"candidate_id": "c1", "flags": [{"code": "modality_dropped", "field": "escalation_3_10s", "quote_from_package": "x", "explanation": "e", "severity": "medium",
                                         "evidence": [{"source_id": "vsd_fansipan_s1", "quote": "q"}]}], "note": ""},
        {"candidate_id": "c2", "flags": [], "note": "không thấy lỗi"}]}]}, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "review.json"
    reviewer.run(cands, STORES, out, batch=3, replay=replay)
    rev = json.loads(out.read_text(encoding="utf-8"))
    rows = rev if isinstance(rev, list) else rev.get("videos", [])
    v = [r for r in rows if r.get("video_id") == "vsd_fansipan_v1"][0]
    assert v["sources_sent"], "nguồn phải được gửi cho reviewer"
    assert v["review_status"] == "review_failed"            # c3 thiếu kết quả → cả video báo lỗi
    html = card.render_card(cands, out, tmp_path / "card.html").read_text(encoding="utf-8")   # thẻ đọc thẳng file nhiều video
    assert "modality_dropped" in html and "review_result_missing" not in html.split("c1")[0]
    assert "review_failed" in html
    dec = card.record_decision(cands, "APPROVE", "c2", reviewer="PO", note="ok", history_dir=tmp_path / "dec")
    dpath = sorted((tmp_path / "dec").glob("v*.json"))[-1]
    assert card.verify_decision(cands, dpath) == "ok"
    data["candidates"][1]["title"] = "đổi sau khi duyệt"; cands.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert card.verify_decision(cands, dpath) != "ok"        # nội dung đổi → phải duyệt lại
    hist = history.build_history(data["candidates"], "vsd", n=10)
    assert hist["n"] == 10 or len(hist["items"]) == 3
