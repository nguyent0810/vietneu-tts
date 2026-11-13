import json
import sqlite3
import tempfile
import uuid
from pathlib import Path

import pytest
from datetime import datetime, timezone

from scripts.related_map import make_map
from webauto.studio_related import plan, save_done

@pytest.fixture
def tmp_path():
    # pytest Windows temporary directories may inherit unusable restrictive ACLs.
    path = Path(tempfile.gettempdir()) / ("gh333-" + uuid.uuid4().hex)
    path.mkdir()
    return path


NOW = datetime(2026, 11, 13, tzinfo=timezone.utc)


def fixture(tmp_path):
    db = tmp_path / "test.sqlite"
    with sqlite3.connect(db) as c:
        c.execute("CREATE TABLE item (channel TEXT, kind TEXT, slug TEXT, publish_at TEXT, video_id TEXT)")
        c.executemany("INSERT INTO item VALUES (?, ?, ?, ?, ?)", [
            ("CK", "long", "old", "2026-01-01T00:00:00Z", "oldLong0001"),
            ("CK", "long", "new", "2026-02-01T00:00:00Z", "newLong0001"),
            ("CK", "long", "future", "2027-01-01T00:00:00Z", "futureLong1"),
            ("CK", "short", "target", "2026-01-01T00:00:00Z", "short000001"),
            ("CK", "short", "keyword", "2026-01-01T00:00:00Z", "short000002"),
            ("CK", "short", "fallback", "2026-01-01T00:00:00Z", "short000003"),
            ("CK", "short", "unavailable", "2026-01-01T00:00:00Z", "short000004"),
        ])
    folder = tmp_path / "bundles" / "CK"
    folder.mkdir(parents=True)
    for slug, data in {
        "old": {"title": "Hòa Thân và triều đình"},
        "new": {"title": "Tài chính gia đình"},
        "target": {"title": "Tài chính", "long_target": "old"},
        "keyword": {"title": "Chuyện Hòa Thân"},
        "fallback": {"title": "Không long"},
        "unavailable": {"title": "Tài chính", "long_target": "future"},
    }.items():
        (folder / (slug + ".json")).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return db


def test_mapping_priorities_and_future(tmp_path):
    db = fixture(tmp_path)
    rows = {r["short_slug"]: r for r in make_map("CK", db, tmp_path, NOW)["matches"]}
    assert rows["target"]["long_slug"] == "old"
    assert rows["target"]["reason"] == "long_target"
    assert rows["keyword"]["long_slug"] == "old"
    assert rows["keyword"]["score"] >= 2
    assert rows["fallback"]["long_slug"] == "new"
    assert rows["fallback"]["fallback"] is True
    assert rows["unavailable"]["long_video_id"] is None
    assert all(r["long_slug"] != "future" for r in rows.values())


def test_spec_target_and_done_ledger(tmp_path):
    db = fixture(tmp_path)
    folder = tmp_path / "bundles" / "CK"
    (folder / "target.json").write_text(json.dumps({"render": {"spec": "spec.json"}, "long_target": "new"}), encoding="utf-8")
    (tmp_path / "spec.json").write_text(json.dumps({"long_target": "old"}), encoding="utf-8")
    mapping = make_map("CK", db, tmp_path, NOW)
    target = next(r for r in mapping["matches"] if r["short_slug"] == "target")
    assert target["long_slug"] == "old"
    path = tmp_path / "map.json"
    path.write_text(json.dumps(mapping), encoding="utf-8")
    ledger = tmp_path / "done.json"
    save_done(ledger, {"short000001": {"long_video_id": "oldLong0001"}})
    pending = plan("CK", path, ledger)
    assert all(r["short_video_id"] != "short000001" for r in pending)
    assert len(pending) == 2
    assert len(plan("CK", path, ledger, 1)) == 1
