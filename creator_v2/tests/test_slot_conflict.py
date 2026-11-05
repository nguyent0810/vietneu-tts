"""GH-146: hai item cùng kênh không được trùng publish_at.

DB tạm. Không đụng state.sqlite thật, không gọi API YouTube.
"""
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "stier"), str(ROOT / "motion"), str(ROOT)]

from factory import store  # noqa: E402
from factory.bundle import Bundle  # noqa: E402
from factory.channel import Channel, Upload  # noqa: E402
from factory.youtube_api import PublishError  # noqa: E402
from factory.youtube_fake import FakeYouTube  # noqa: E402

WHEN = "2026-11-05T05:00:00Z"          # 05/11/2026 12:00 VN
LATER = "2026-12-01T12:00:00Z"         # 01/12/2026 19:00 VN — chắc chắn còn tương lai với upload_one
T0 = datetime(2026, 10, 5, 3, 0, tzinfo=timezone.utc)
SCRIPT = "Một câu đủ dài để kể chuyện. " * 8


def bundle(slug, channel="CK", publish_at=WHEN, **kw):
    f = dict(channel=channel, kind="short", slug=slug, script=SCRIPT, title=f"T {slug}",
             description="d", tags=["x"], thumbnail_text="", publish_at=publish_at,
             voice="Ngọc Huyền", bgm="", broll_queries=["chart"])
    f.update(kw)
    return Bundle(**f)


@pytest.fixture
def conn(tmp_path):
    with store.connect(tmp_path / "state.sqlite") as c:
        yield c


def test_same_channel_same_time_is_blocked_and_names_the_holder(conn):
    store.enqueue(bundle("ck-giu"), conn)
    with pytest.raises(store.SlotConflict, match="ck-giu") as e:
        store.enqueue(bundle("ck-moi"), conn)
    assert "05/11/2026 12:00" in str(e.value)
    assert WHEN in str(e.value)
    assert [r["slug"] for r in conn.execute("SELECT slug FROM item")] == ["ck-giu"]


def test_other_channel_same_time_is_free(conn):
    store.enqueue(bundle("ck-giu"), conn)
    assert store.enqueue(bundle("mim-khac", channel="MIM"), conn) is True
    assert store.slot_conflicts(conn, "MIM", WHEN, exclude_slug="mim-khac") == []


def test_failed_and_replaced_do_not_hold_the_slot(conn):
    hong = bundle("ck-hong")
    store.enqueue(hong, conn)
    store.mark(conn, hong.id, "failed")
    assert store.slot_conflicts(conn, "CK", WHEN) == []
    cu = bundle("ck-cu")
    store.enqueue(cu, conn)
    store.mark(conn, cu.id, "replaced")
    assert store.slot_conflicts(conn, "CK", WHEN) == []
    assert store.enqueue(bundle("ck-moi"), conn) is True


def test_same_slug_enqueue_does_not_block_itself(conn):
    b = bundle("ck-giu")
    assert store.enqueue(b, conn) is True
    assert store.enqueue(b, conn) is False
    assert store.slot_conflicts(conn, "CK", WHEN, exclude_slug="ck-giu") == []


def _ledger(conn, channel="CK"):
    Channel(channel, FakeYouTube(), conn, now=lambda: T0)


def _log(conn, slug, publish_at=WHEN, channel="CK", state="done"):
    conn.execute(
        "INSERT INTO upload_log (channel, slug, title, state, video_id, publish_at, started_at) "
        "VALUES (?, ?, 'T', ?, ?, ?, '2026-11-01T00:00:00Z')",
        (channel, slug, state, "vid-" + slug, publish_at))


def test_upload_log_blocks_even_without_an_item(conn):
    _ledger(conn)
    _log(conn, "ck-da-len")
    assert store.slot_conflicts(conn, "CK", WHEN) == ["ck-da-len"]
    with pytest.raises(store.SlotConflict, match="ck-da-len"):
        store.enqueue(bundle("ck-moi"), conn)


def test_same_slug_in_upload_log_does_not_block_itself(conn):
    _ledger(conn)
    _log(conn, "ck-moi")
    assert store.slot_conflicts(conn, "CK", WHEN, exclude_slug="ck-moi") == []
    assert store.enqueue(bundle("ck-moi"), conn) is True


def test_upload_log_still_blocks_after_the_item_is_replaced(conn):
    goc = bundle("ck-goc")
    store.enqueue(goc, conn)
    store.mark(conn, goc.id, "replaced")
    _ledger(conn)
    _log(conn, "ck-goc")
    assert store.slot_conflicts(conn, "CK", WHEN, exclude_slug="ck-moi") == ["ck-goc"]


def test_published_item_with_cleared_upload_log_does_not_block(conn):
    # Gốc published, item.publish_at còn giờ, nhưng sổ đã gỡ lịch (NULL).
    _ledger(conn)
    goc = bundle("ck-p2-tra-truoc-mot-ty")
    store.enqueue(goc, conn)
    store.mark(conn, goc.id, "published", video_id="vid-goc")
    _log(conn, goc.slug, publish_at=None)
    assert store.slot_conflicts(conn, "CK", WHEN, exclude_slug="ck-p2-tra-truoc-mot-ty-r2") == []
    assert store.enqueue(bundle("ck-p2-tra-truoc-mot-ty-r2"), conn) is True


def test_published_item_whose_upload_log_still_holds_the_time_blocks(conn):
    _ledger(conn)
    goc = bundle("ck-goc")
    store.enqueue(goc, conn)
    store.mark(conn, goc.id, "published", video_id="vid-ck-goc")
    _log(conn, goc.slug, publish_at=WHEN)
    assert store.slot_conflicts(conn, "CK", WHEN, exclude_slug="ck-r2") == ["ck-goc"]
    with pytest.raises(store.SlotConflict, match="ck-goc"):
        store.enqueue(bundle("ck-r2"), conn)


@pytest.fixture
def env(tmp_path):
    video = tmp_path / "final.mp4"
    video.write_bytes(b"\0" * 64)
    with store.connect(tmp_path / "state.sqlite") as c:
        yield {"yt": FakeYouTube(), "conn": c, "video": video, "tmp": tmp_path}


def ch(env, code="FS"):
    return Channel(code, env["yt"], env["conn"], now=lambda: T0)


def up(env, slug, title, when=WHEN):
    return Upload(slug=slug, video=env["video"], title=title, description="Mô tả.",
                  tags=("x",), kind="short", publish_at=when)


def test_upload_of_another_slug_at_the_same_time_is_refused(env):
    ch(env).upload(up(env, "lich-giu", "Giữ", "2026-10-10T23:00:00Z"))
    with pytest.raises(PublishError, match="lich-giu") as e:
        ch(env).upload(up(env, "lich-moi", "Mới", "2026-10-10T23:00:00Z"))
    assert "11/10/2026 06:00" in str(e.value)
    assert env["yt"].inserts == 1
    assert env["conn"].execute("SELECT COUNT(*) FROM upload_log").fetchone()[0] == 1


def test_uploading_the_same_slug_again_is_not_a_slot_conflict(env):
    c = ch(env)
    first = c.upload(up(env, "lich-giu", "Giữ", "2026-10-10T23:00:00Z"))
    again = c.upload(up(env, "lich-giu", "Giữ", "2026-10-10T23:00:00Z"))
    assert again.video_id == first.video_id and again.reused
    assert env["yt"].inserts == 1


def test_reschedule_onto_an_item_or_an_upload_is_refused(env):
    c = ch(env)
    vid = c.upload(up(env, "lich-a", "A", "2026-10-10T23:00:00Z")).video_id
    store.enqueue(bundle("lich-b", channel="FS", publish_at=WHEN), env["conn"])
    with pytest.raises(PublishError, match="lich-b") as e:
        c.reschedule(vid, WHEN)
    assert "05/11/2026 12:00" in str(e.value)
    assert env["yt"].get_video(vid, "status")["status"]["publishAt"] == "2026-10-10T23:00:00Z"
    assert env["conn"].execute("SELECT publish_at FROM upload_log WHERE video_id = ?", (vid,)).fetchone()[0] \
        == "2026-10-10T23:00:00Z"

    # Giờ chỉ có trong sổ upload, không có hàng item thứ hai.
    c.upload(up(env, "lich-c", "C", "2026-11-20T05:00:00Z"))
    with pytest.raises(PublishError, match="lich-c"):
        c.reschedule(vid, "2026-11-20T05:00:00Z")
    assert env["yt"].get_video(vid, "status")["status"]["publishAt"] == "2026-10-10T23:00:00Z"


def test_reschedule_to_the_same_time_or_another_channel_is_allowed(env):
    c = ch(env)
    vid = c.upload(up(env, "lich-a", "A", "2026-10-10T23:00:00Z")).video_id
    c.reschedule(vid, "2026-10-10T23:00:00Z")
    store.enqueue(bundle("ck-khac", publish_at=WHEN), env["conn"])
    c.reschedule(vid, WHEN)
    assert env["yt"].get_video(vid, "status")["status"]["publishAt"] == WHEN


def test_reschedule_r2_is_not_blocked_by_an_unscheduled_original(env):
    # Tình huống 8 cặp gốc/-r2: cả hai published, cùng item.publish_at.
    # Gốc đã gỡ lịch (upload_log.publish_at NULL); -r2 vẫn giữ giờ trên sổ.
    c = ch(env, "CK")
    conn = env["conn"]
    other = "2026-11-06T05:00:00Z"

    def plant(slug, item_at, log_at):
        b = bundle(slug, channel="CK", publish_at=item_at)
        store.enqueue(b, conn)
        status = {"privacyStatus": "private"}
        if log_at:
            status["publishAt"] = log_at
        vid = env["yt"].add_video({"title": slug}, status)
        store.mark(conn, b.id, "published", video_id=vid)
        _log(conn, slug, publish_at=log_at, channel="CK")
        conn.execute("UPDATE upload_log SET video_id = ? WHERE channel = ? AND slug = ?",
                     (vid, "CK", slug))
        return vid

    goc = plant("ck-p2-tra-truoc-mot-ty", WHEN, None)
    r2 = plant("ck-p2-tra-truoc-mot-ty-r2", WHEN, WHEN)
    khac = plant("ck-p2-khac", other, None)

    c.reschedule(r2, WHEN)
    assert env["yt"].get_video(r2, "status")["status"]["publishAt"] == WHEN
    c.reschedule(r2, other)
    assert env["yt"].get_video(r2, "status")["status"]["publishAt"] == other
    assert "publishAt" not in env["yt"].get_video(goc, "status")["status"]
    assert "publishAt" not in env["yt"].get_video(khac, "status")["status"]
    assert conn.execute(
        "SELECT publish_at FROM upload_log WHERE slug = ?", ("ck-p2-tra-truoc-mot-ty",)
    ).fetchone()[0] is None
    assert conn.execute(
        "SELECT publish_at FROM upload_log WHERE slug = ?", ("ck-p2-khac",)
    ).fetchone()[0] is None


def _patch_connect(monkeypatch, db):
    orig = store.connect

    @contextmanager
    def connect(db_path=None):
        with orig(db) as c:
            yield c

    monkeypatch.setattr(store, "connect", connect)
    return orig


def test_upload_one_dry_blocks_and_does_not_write(monkeypatch, tmp_path):
    import upload_one
    db = tmp_path / "state.sqlite"
    holder = bundle("ck-giu", publish_at=LATER)
    with store.connect(db) as c:
        store.enqueue(holder, c)
    _patch_connect(monkeypatch, db)
    monkeypatch.setattr(upload_one, "build_bundle",
                        lambda *a, **k: (bundle("ck-moi", publish_at=LATER), tmp_path / "f.mp4"))
    with pytest.raises(SystemExit) as e:
        upload_one.main(["ck-moi", "2026-12-01 19:00", "--channel", "CK", "--dry"])
    assert "ck-giu" in str(e.value) and "01/12/2026 19:00" in str(e.value)
    with store.connect(db) as c:
        assert [r["slug"] for r in c.execute("SELECT slug FROM item")] == ["ck-giu"]


def test_upload_one_dry_same_slug_is_not_blocked(monkeypatch, tmp_path):
    import upload_one
    db = tmp_path / "state.sqlite"
    with store.connect(db) as c:
        store.enqueue(bundle("ck-moi", publish_at=LATER), c)
    _patch_connect(monkeypatch, db)
    monkeypatch.setattr(upload_one, "build_bundle",
                        lambda *a, **k: (bundle("ck-moi", publish_at=LATER), tmp_path / "f.mp4"))
    upload_one.main(["ck-moi", "2026-12-01 19:00", "--channel", "CK", "--dry"])
    with store.connect(db) as c:
        assert [r["slug"] for r in c.execute("SELECT slug FROM item")] == ["ck-moi"]


@pytest.mark.parametrize("mod_name,channel", [("enqueue_ck", "CK"), ("enqueue_mim", "MIM")])
def test_enqueue_cli_blocks_and_a_repeat_of_the_same_slug_does_not(monkeypatch, tmp_path, mod_name, channel):
    import importlib
    mod = importlib.import_module(mod_name)
    db = tmp_path / "state.sqlite"
    monkeypatch.setattr(store, "BUNDLE_DIR", tmp_path / "bundles")
    holder = bundle("ck-giu" if channel == "CK" else "mim-giu", channel=channel, publish_at=LATER)
    with store.connect(db) as c:
        store.enqueue(holder, c)
    _patch_connect(monkeypatch, db)
    out = tmp_path / "out"
    (out / holder.slug).mkdir(parents=True)
    (out / holder.slug / "final.mp4").write_bytes(b"x")
    monkeypatch.setattr(mod, "OUT", out)
    monkeypatch.setattr(mod, "bundle_for", lambda slug, vn: holder)
    monkeypatch.setattr(mod.sys, "argv", [mod_name, holder.slug, "2026-12-01 19:00"])
    mod.main()          # cùng slug: không tự chặn
    new = bundle("ck-moi" if channel == "CK" else "mim-moi", channel=channel, publish_at=LATER)
    (out / new.slug).mkdir()
    (out / new.slug / "final.mp4").write_bytes(b"x")
    monkeypatch.setattr(mod, "bundle_for", lambda slug, vn: new)
    monkeypatch.setattr(mod.sys, "argv", [mod_name, new.slug, "2026-12-01 19:00"])
    with pytest.raises(SystemExit) as e:
        mod.main()
    assert holder.slug in str(e.value) and "01/12/2026 19:00" in str(e.value)
    with store.connect(db) as c:
        assert {r["slug"] for r in c.execute("SELECT slug FROM item")} == {holder.slug}


def test_publish_long_register_blocks_before_writing_the_bundle(tmp_path):
    sys.path[:0] = [str(ROOT / "motion" / "long")]
    import publish_long as pl
    sd, od = tmp_path / "data" / "long" / "kowloon", tmp_path / "out"
    sd.mkdir(parents=True)
    od.mkdir()
    (sd / "spec.json").write_text(
        '{"title":"Cửu Long","chapters":["ch00"],"youtube":{"tags":["k"],"sources":["https://example.com"]}}',
        encoding="utf-8")
    (sd / "ch00.json").write_text('{"lines":["Câu một đủ để thành lời đọc của video dài."]}', encoding="utf-8")
    (od / "description.txt").write_text("Mô tả dài.", encoding="utf-8")
    db = tmp_path / "state.sqlite"
    with store.connect(db) as conn:
        store.enqueue(bundle("cl-giu", channel="CL", publish_at=LATER), conn)
        chan = Channel("CL", FakeYouTube(), conn, now=lambda: T0)
        b = pl.long_bundle("kowloon", "CL", LATER, sd, od)
        with pytest.raises(SystemExit) as e:
            pl.register(conn, b, {}, od / "final.mp4", chan, tmp_path / "bundles")
        assert "cl-giu" in str(e.value) and "01/12/2026 19:00" in str(e.value)
        assert [r["slug"] for r in conn.execute("SELECT slug FROM item")] == ["cl-giu"]
    assert not (tmp_path / "bundles").exists()
