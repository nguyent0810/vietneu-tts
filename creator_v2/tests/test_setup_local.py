"""scripts/setup_local.py: nối media root, không ghi đè, --check chỉ đọc, không lộ YT_CREDS_DIR."""
import importlib.util
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("setup_local", ROOT / "scripts" / "setup_local.py")
sl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sl)

SECRET = "ZZ_distinct_secret_creds_dir_93817"


def _can_link(tmp: Path) -> bool:
    try:
        s, d = tmp / "_s", tmp / "_d"
        s.mkdir()
        sl.make_link(d, s)
        return sl.is_link(d)
    except Exception:
        return False


@pytest.fixture
def env(tmp_path, monkeypatch):
    probe = tmp_path / "probe"
    probe.mkdir()
    if not _can_link(probe):
        pytest.skip("môi trường không tạo được symlink/junction")
    media, root = tmp_path / "media", tmp_path / "root"
    for rel in sl.LINKS:
        (media / rel).mkdir(parents=True)
    (media / "output" / "sub").mkdir(parents=True)
    amb = media / "motion/stier/ambience"
    amb.mkdir(parents=True)
    (amb / "a.wav").write_bytes(b"RIFF")
    root.mkdir()
    monkeypatch.delenv("YT_CREDS_DIR", raising=False)
    return media, root


def test_links_created_and_wav_copied(env):
    media, root = env
    sl.run(str(media), False, False, root)
    for rel in sl.LINKS:
        assert sl.is_link(root / rel), rel
    wav = root / "motion/stier/ambience/a.wav"
    assert wav.read_bytes() == b"RIFF" and not sl.is_link(wav)


def test_existing_destination_untouched(env, capsys):
    media, root = env
    d = root / "output/music"
    d.mkdir(parents=True)
    (d / "keep.txt").write_text("x")
    (root / ".ref").write_text("file")
    (root / "motion/stier/ambience").mkdir(parents=True)
    (root / "motion/stier/ambience/a.wav").write_bytes(b"LOCAL")
    sl.run(str(media), False, False, root)
    out = capsys.readouterr().out
    assert (d / "keep.txt").read_text() == "x" and not sl.is_link(d)
    assert (root / ".ref").read_text() == "file"
    assert (root / "motion/stier/ambience/a.wav").read_bytes() == b"LOCAL"
    assert "đã có" in out


def test_link_pointing_elsewhere_warns(env, tmp_path, capsys):
    media, root = env
    other = tmp_path / "other"
    other.mkdir()
    sl.make_link(root / ".ref", other)
    sl.run(str(media), False, False, root)
    assert "link trỏ chỗ khác" in capsys.readouterr().out
    assert Path(os.path.realpath(root / ".ref")) == other.resolve()


def test_missing_source_warns_and_continues(env, capsys):
    media, root = env
    (media / "motion/hf/assets/cases").rmdir()
    sl.run(str(media), False, False, root)
    assert "không thấy nguồn" in capsys.readouterr().out
    assert sl.is_link(root / ".ref") and not (root / "motion/hf/assets/cases").exists()


def test_check_changes_nothing(env):
    media, root = env
    assert sl.run(str(media), True, False, root) == 1
    assert list(root.iterdir()) == []


def test_link_output_links_whole_output(env):
    media, root = env
    sl.run(str(media), False, True, root)
    assert sl.is_link(root / "output") and (root / "output/sub").is_dir()


def test_creds_dir_value_never_printed(env, tmp_path, monkeypatch, capsys):
    media, root = env
    cd = tmp_path / SECRET
    cd.mkdir()
    (cd / "token.json").write_text("{}")
    monkeypatch.setenv("YT_CREDS_DIR", str(cd))
    sl.run(str(media), True, False, root)
    monkeypatch.setenv("YT_CREDS_DIR", str(tmp_path / (SECRET + "_missing")))
    sl.run(str(media), True, False, root)
    cap = capsys.readouterr()
    assert SECRET not in cap.out + cap.err
    assert "đã đặt" in cap.out and "không tồn tại" in cap.out


def test_main_reads_env_media_root_check_only(env, monkeypatch):
    media, root = env
    monkeypatch.setenv("CREATOR_MEDIA_ROOT", str(media))
    monkeypatch.setattr(sl, "ROOT", root)
    assert sl.main(["--check"]) == 1
    assert list(root.iterdir()) == []


def test_real_empty_dir_is_not_ok(env, capsys):
    """Thư mục thật rỗng ở chỗ media (vd. do lệnh khác tạo) không được tính là đã nối."""
    media, root = env
    clips = root / "motion/hf/assets/clips"
    clips.mkdir(parents=True)
    rep = sl.Report()
    sl.link_one(rep, "motion/hf/assets/clips", media, root, dry=True)
    assert rep.rows[-1][2] == sl.FAIL and not rep.ok
    assert not sl.is_link(clips) and clips.is_dir()


def test_real_dir_with_data_warns_and_is_kept(env, capsys):
    media, root = env
    d = root / "motion/hf/assets/clips"
    d.mkdir(parents=True)
    (d / "a.mp4").write_bytes(b"x")
    rep = sl.Report()
    sl.link_one(rep, "motion/hf/assets/clips", media, root, dry=False)
    assert rep.rows[-1][2] == sl.WARN and rep.ok
    assert (d / "a.mp4").read_bytes() == b"x" and not sl.is_link(d)


def test_link_survives_shell_metacharacters(tmp_path):
    src, dest = tmp_path / "m&e^d%x" / "clips", tmp_path / "r&o^o%t" / "clips"
    src.mkdir(parents=True)
    (src / "f.txt").write_text("ok")
    try:
        sl.make_link(dest, src)
    except OSError as e:
        pytest.skip(f"không tạo được link: {e}")
    assert sl.is_link(dest) and (dest / "f.txt").read_text() == "ok"
