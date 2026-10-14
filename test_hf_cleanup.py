"""Khoá các luật an toàn của hf_cleanup: chỉ dọn video YouTube xác nhận đã xử lý + công khai/hẹn giờ,
đúng id (không kéo theo id có tiền tố trùng), giữ metadata nhỏ, không đụng kênh Hình Sự."""
import os
import time

import hf_cleanup as C


def _mk(p, data=b"x"):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return p


def _setup(tmp_path, monkeypatch, status):
    st = tmp_path / "output" / "cl_staging"
    out = st / "fs" / "out"
    for name in ("f01_a.mp4", "f01_a.wav", "f01_a.json", "f01_a.srt", "f01_ab.mp4", "f02_a.mp4", "f03_a.mp4"):
        _mk(out / name)
    (st / "fs" / "uploaded.json").write_text('{"f01_a": "V1", "f02_a": "V2", "f03_a": "V3"}', encoding="utf-8")
    _mk(st / "hyperframes_oct" / "out" / "o01_a.mp4")             # kênh Hình Sự
    (st / "hyperframes_oct" / "uploaded.json").write_text('{"o01_a": "V9"}', encoding="utf-8")
    monkeypatch.setattr(C, "STAGING", st)
    monkeypatch.setattr(C, "ROOT", tmp_path)
    monkeypatch.setattr(C, "LANES", {"fs": ["x"]})
    monkeypatch.setattr(C, "youtube_status", lambda ids, creds: status)
    return out


def test_only_processed_and_scheduled_are_cleaned(tmp_path, monkeypatch):
    out = _setup(tmp_path, monkeypatch, {
        "V1": {"processed": True, "live_or_scheduled": True, "privacy": "private"},
        "V2": {"processed": False, "live_or_scheduled": True, "privacy": "private"},
        "V3": {"processed": True, "live_or_scheduled": False, "privacy": "private"}})
    todo, notes = C.published_candidates()
    names = sorted(p.name for p, _ in todo)
    assert names == ["f01_a.mp4", "f01_a.wav"]          # f01_ab (tiền tố trùng) và json/srt không bị kéo theo
    assert any("f02_a" in n for n in notes) and any("f03_a" in n for n in notes)
    assert (out / "f01_a.json").exists()


def test_unknown_on_channel_is_kept(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, {})
    todo, notes = C.published_candidates()
    assert todo == [] and len(notes) == 3


def test_stale_respects_pattern_and_age(tmp_path):
    old = time.time() - 5 * 86400
    a = _mk(tmp_path / "L_bud_06_s12.jpg"); os.utime(a, (old, old))
    b = _mk(tmp_path / "logo.png"); os.utime(b, (old, old))           # không phải file render sinh ra
    c = _mk(tmp_path / "ch01_s3.jpg")                                  # mới
    assert C.stale(tmp_path, 2, C.HF_ASSET_RE) == [a]


def test_apply_trash_moves_and_keeps_structure(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "ROOT", tmp_path)
    monkeypatch.setattr(C.Path, "home", classmethod(lambda cls: tmp_path / "home"))
    f = _mk(tmp_path / "output" / "x" / "a.mp4", b"12345")
    d = tmp_path / "output" / "x" / "a_chapters"; _mk(d / "ch00.mp4", b"123")
    freed = C.apply([(f, "t"), (d, "t")], delete=False)
    assert freed == 8 and not f.exists() and not d.exists()
    moved = list((tmp_path / "home" / ".Trash" / "vieneu_tu_don").rglob("a.mp4"))
    assert moved and moved[0].read_bytes() == b"12345"


def test_rerender_newer_than_upload_is_kept(tmp_path):
    """Bản render lại (sửa lỗi) chờ thay video cũ: mp4 mới hơn lúc video lên YouTube -> không dọn (sự cố F10/B10 04/10/2026)."""
    out = tmp_path / "out"
    mp4 = _mk(out / "L_fs_15.mp4")
    now = time.time()
    os.utime(mp4, (now, now))
    old = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - 86400))
    new = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + 60))
    assert C.rendered_after_upload(out, "L_fs_15", old) is True
    assert C.rendered_after_upload(out, "L_fs_15", new) is False
    assert C.rendered_after_upload(out, "L_fs_15", None) is False
