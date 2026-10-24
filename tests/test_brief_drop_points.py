"""Ticket 71: hf_brief ghi điểm rơi dốc nhất của short pipeline kèm câu đang đọc (không gọi mạng)."""
import json

import hf_brief as B
import hf_short_retention


def test_drop_section_chi_ra_giay_va_cau(tmp_path, monkeypatch):
    out = tmp_path / "output" / "cl_staging" / "bud" / "out"
    out.mkdir(parents=True)
    (out / "b1.json").write_text(json.dumps({"segments": [
        {"start": 0.0, "end": 2.0, "text": "Câu móc đầu."}, {"start": 2.2, "end": 6.0, "text": "Câu **thứ hai** giải thích."}]}))
    monkeypatch.setattr(B, "ROOT", tmp_path)
    monkeypatch.setattr(B, "CACHE", tmp_path / "cache")
    calls = []

    def fake(query, cred, vid, start, end):
        calls.append(vid)
        return {"steepest_drop": {"from": .2, "to": .25, "drop": .2, "drop_percentage_points": 20.0}}
    monkeypatch.setattr(hf_short_retention, "analyze_video", fake)
    rows = [{"vid": "v1", "rid": "b1", "ours": True, "rank": .05, "dur": 20, "day_pt": "2026-10-10", "title": "Bài thấp"},
            {"vid": "v2", "rid": None, "ours": True, "rank": .95, "dur": 20, "day_pt": "2026-10-10", "title": "Bài cao"},
            {"vid": "v3", "rid": None, "ours": False, "rank": .5, "dur": 20, "day_pt": "2026-10-10", "title": "Nguồn ngoài"}]
    L = B.drop_section("bud", rows, n=1)
    text = "\n".join(L)
    assert "thấp 0.05 · rơi 20 điểm ở 4.0–5.0s / 20s — Bài thấp" in text
    assert "đang đọc: _Câu thứ hai giải thích._" in text
    assert "Nguồn ngoài" not in text and "**2-5s**" in text
    B.drop_section("bud", rows, n=1)                  # lần hai đọc cache, không gọi lại
    assert calls == ["v1", "v2"]


def test_drop_section_api_loi_khong_chan_ban_tin(tmp_path, monkeypatch):
    monkeypatch.setattr(B, "ROOT", tmp_path)
    monkeypatch.setattr(B, "CACHE", tmp_path / "cache")

    def boom(*a, **k):
        raise TimeoutError
    monkeypatch.setattr(hf_short_retention, "analyze_video", boom)
    L = B.drop_section("bud", [{"vid": "v1", "rid": None, "ours": True, "rank": .1, "dur": 20,
                                "day_pt": "2026-10-10", "title": "Bài"}], n=1)
    assert "chưa lấy được đường giữ chân (TimeoutError)" in L[0]
