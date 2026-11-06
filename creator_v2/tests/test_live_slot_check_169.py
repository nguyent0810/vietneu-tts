"""#169: giờ hẹn kiểm với lịch THẬT trên YouTube, không chỉ sổ local. Fake client, không mạng."""
from datetime import datetime, timezone

import pytest

from factory import store
from factory.channel import Channel, Upload
from factory.youtube_api import PublishError
from factory.youtube_fake import FakeYouTube

T0 = datetime(2026, 10, 5, 3, 0, tzinfo=timezone.utc)
SLOT = "2026-10-10T23:00:00Z"


@pytest.fixture
def env(tmp_path):
    video = tmp_path / "final.mp4"
    video.write_bytes(b"\0" * 64)
    with store.connect(tmp_path / "state.sqlite") as conn:
        yield {"yt": FakeYouTube(), "conn": conn, "video": video}


def ch(env):
    return Channel("CL", env["yt"], env["conn"], now=lambda: T0)


def up(env, slug="a", when=SLOT):
    return Upload(slug=slug, video=env["video"], title=f"Tiêu đề {slug}", description="Mô tả.",
                  tags=("t",), kind="short", publish_at=when)


def foreign(env, at=SLOT, privacy="private"):
    st = {"privacyStatus": privacy}
    if at:
        st["publishAt"] = at
    return env["yt"].add_video({"title": "ngoài sổ"}, st)


def test_upload_into_slot_held_on_youtube_but_unknown_to_ledger_is_blocked(env):
    vid = foreign(env)
    with pytest.raises(PublishError, match=vid):
        ch(env).upload(up(env))
    assert env["yt"].inserts == 1                       # chỉ video ngoài sổ, không upload mới


def test_reschedule_into_such_slot_is_blocked(env):
    vid = foreign(env)
    mine = foreign(env, at="2026-10-11T23:00:00Z")
    with pytest.raises(PublishError, match=vid):
        ch(env).reschedule(mine, SLOT)
    assert env["yt"].videos[mine]["status"]["publishAt"] == "2026-10-11T23:00:00Z"


def test_video_keeping_its_own_slot_is_not_a_conflict(env):
    mine = foreign(env)
    ch(env).reschedule(mine, "2026-10-10T23:00:00+00:00")
    assert store.norm_utc(env["yt"].videos[mine]["status"]["publishAt"]) == SLOT


def test_other_formats_are_the_same_slot(env):
    vid = foreign(env, at="2026-10-10T23:00:00.000Z")
    with pytest.raises(PublishError, match=vid):
        ch(env).upload(up(env, when=SLOT))
    other = foreign(env, at="2026-10-12T23:00:00+00:00")
    with pytest.raises(PublishError, match=other):
        ch(env).upload(up(env, slug="b", when="2026-10-12T23:00:00Z"))


def test_free_slot_uploads_and_is_cached_once_per_run(env):
    foreign(env, at="2026-10-20T23:00:00Z")
    calls = []
    orig = env["yt"].list_uploads
    env["yt"].list_uploads = lambda n: calls.append(n) or orig(n)
    c = ch(env)
    c.upload(up(env))
    with pytest.raises(PublishError):                   # slot vừa đăng cũng đã vào cache
        c.upload(up(env, slug="b"))
    assert len(calls) == 1


def test_norm_utc_formats():
    for s in ("2026-10-10T23:00:00Z", "2026-10-10T23:00:00+00:00", "2026-10-10T23:00:00.000Z",
              "2026-10-11T06:00:00+07:00"):
        assert store.norm_utc(s) == SLOT
    assert store.norm_utc("rác") == "rác"
