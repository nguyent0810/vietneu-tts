"""Plan Long đang giữ (day = None) không làm hf_music.pool_for sập (Lead 12/11)."""
import hf_music


def test_pool_for_hold_plan_without_day(tmp_path, monkeypatch):
    ledger = {
        "L_fs_old": {"series": "fs", "day": "2026-11-01", "pool": ["bgm/a.mp3"]},
        "L_fs_undated": {"series": "fs", "day": None, "pool": ["bgm/b.mp3"]},
    }
    monkeypatch.setattr(hf_music, "ledger", lambda: ledger)
    monkeypatch.setattr(hf_music, "_save", lambda d: None)
    (tmp_path / "bgm").mkdir()
    for name, _ in hf_music.CATALOG["fs"]:
        (tmp_path / "bgm" / name).write_bytes(b"")
    row = {"id": "L_fs_new", "series": "fs", "day": None, "lane": "long"}
    pool = hf_music.pool_for(row, tmp_path)
    assert pool and all(p.startswith("bgm/") for p in pool)


def test_neighbors_skips_undated_rows():
    d = {"a": {"series": "fs", "day": "2026-11-01"}, "b": {"series": "fs", "day": None}}
    assert hf_music.neighbors(d, "x", "fs", "2026-11-02") == ["a"]
