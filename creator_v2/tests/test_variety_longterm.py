import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion"))
import variety as V


def rows(count, uses):
    return [{"topic": f"old{i}", "channel": "MIM", "date": f"2026-01-{i + 1:02d}",
             "bgm": uses.get(i, []), "look": "classic"} for i in range(count)]


def setup_picker(tmp_path, monkeypatch, history, names):
    library = tmp_path / "music"
    library.mkdir()
    for name in names:
        (library / f"{name}.mp3").write_bytes(b"audio")
    monkeypatch.setattr(V, "LIB", library)
    monkeypatch.setattr(V, "ledger", lambda: history)
    monkeypatch.setattr(V, "catalog", lambda: {"tracks": {
        name: {"file": f"{name}.mp3", "mood": ["calm"], "channel": "MIM"} for name in names}})
    monkeypatch.setattr(V, "_picks_path", lambda topic: tmp_path / "picks.json")


def pick(tmp_path):
    chapters = [("ch00", {"bgm": {"mood": "calm"}})]
    V.resolve_bgm("new", {"channel": "MIM"}, chapters, tmp_path / "out")
    return chapters[0][1]["bgm"]


def test_recent_track_is_excluded(tmp_path, monkeypatch):
    setup_picker(tmp_path, monkeypatch, rows(20, {15: ["recent"]}), ["recent", "fresh"])
    assert pick(tmp_path)["file"] == "fresh.mp3"


def test_track_at_share_cap_is_excluded(tmp_path, monkeypatch):
    setup_picker(tmp_path, monkeypatch, rows(19, {0: ["over"], 5: ["over"], 10: ["over"]}), ["over", "fresh"])
    assert pick(tmp_path)["file"] == "fresh.mp3"


def test_no_eligible_candidates_warns_and_leaves_slot_unresolved(tmp_path, monkeypatch, capsys):
    setup_picker(tmp_path, monkeypatch, rows(10, {9: ["recent"]}), ["recent"])
    assert "file" not in pick(tmp_path)
    assert "WARNING variety" in capsys.readouterr().out


def test_audit_reports_both_rules_and_ignores_other_channels(monkeypatch):
    history = rows(19, {0: ["over"], 5: ["over"], 10: ["over"], 18: ["recent"]})
    history.append({"topic": "other", "channel": "CL", "bgm": ["free"], "date": "2026-02-01"})
    monkeypatch.setattr(V, "ledger", lambda: history)
    monkeypatch.setattr(V, "profile", lambda topic: {"topic": topic, "channel": "MIM", "theme": "lab",
                                                     "look": "classic", "bgm": ["over", "recent", "free"]})
    issues = V.audit("new")
    assert any("recent" in s and "5 Long" in s for s in issues)
    assert any("over" in s and "15%" in s for s in issues)
    assert not any("free" in s for s in issues)


def test_share_rounding_and_exclusion_of_current_topic(monkeypatch):
    history = rows(6, {0: ["a"], 1: ["a"]})
    history.append({"topic": "new", "channel": "MIM", "date": "2026-02-01", "bgm": ["a"]})
    monkeypatch.setattr(V, "ledger", lambda: history)
    _, counts, cap = V.longterm_limits("MIM", "new")
    assert counts["a"] == 2 and cap == 2


def test_library_reports_available_tracks_by_author_and_missing_files(tmp_path, monkeypatch, capsys):
    setup_picker(tmp_path, monkeypatch, [], ["present"])
    monkeypatch.setattr(V, "catalog", lambda: {"tracks": {
        "present": {"file": "present.mp3", "mood": ["calm"], "channel": "MIM", "author": "Author A"},
        "missing": {"file": "missing.mp3", "mood": ["calm"], "channel": "MIM", "author": "Author B"}}})
    monkeypatch.setattr(sys, "argv", ["variety.py", "library"])
    V.main()
    output = capsys.readouterr().out
    assert "1 bài có file, 1 tác giả: Author A" in output
    assert "Thiếu file: 1" in output and "missing.mp3" in output
