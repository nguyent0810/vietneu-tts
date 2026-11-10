"""032/032b: file .mp4 hỏng không được coi là đã render; file cuối cũ không được bỏ qua.

Không gọi ffprobe, ffmpeg, df thật. Thời lượng và chỗ trống đều giả lập.
"""
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

import hf_batch_render as HBR


def _cp(cmd, code=0, out="", err=""):
    return subprocess.CompletedProcess(cmd, code, out, err)


def test_probe_doc_duration(monkeypatch):
    def run(cmd, **_k):
        assert cmd[0] == "ffprobe" and "format=duration" in cmd
        return _cp(cmd, 0, "12.5\n")
    monkeypatch.setattr(HBR.subprocess, "run", run)
    assert HBR.probe_duration_s(Path("x.mp4")) == 12.5


def test_probe_hong_va_duration_khong_duong(monkeypatch):
    monkeypatch.setattr(HBR.subprocess, "run", lambda cmd, **_k: _cp(cmd, 1, "", "Invalid data"))
    assert HBR.probe_duration_s(Path("x.mp4")) is None
    monkeypatch.setattr(HBR.subprocess, "run", lambda cmd, **_k: _cp(cmd, 0, "0.000000\n"))
    assert HBR.probe_duration_s(Path("x.mp4")) is None
    monkeypatch.setattr(HBR.subprocess, "run", lambda cmd, **_k: _cp(cmd, 0, "N/A\n"))
    assert HBR.probe_duration_s(Path("x.mp4")) is None


@pytest.mark.parametrize("raw", ["-1\n", "", "\n", "inf\n", "-inf\n", "nan\n", "Infinity\n"])
def test_probe_duration_am_rong_inf_nan(monkeypatch, raw):
    monkeypatch.setattr(HBR.subprocess, "run", lambda cmd, **_k: _cp(cmd, 0, raw))
    assert HBR.probe_duration_s(Path("x.mp4")) is None


def test_dest_free_bytes_lay_disk_usage(monkeypatch, tmp_path):
    seen = []

    class Usage:
        free = 4096

    monkeypatch.setattr(HBR.shutil, "disk_usage", lambda p: seen.append(Path(p)) or Usage)
    assert HBR.dest_free_bytes(tmp_path) == 4096
    assert seen == [tmp_path]


def test_dest_free_bytes_path_chua_ton_tai_lay_cha(monkeypatch, tmp_path):
    seen = []

    class Usage:
        free = 77

    monkeypatch.setattr(HBR.shutil, "disk_usage", lambda p: seen.append(Path(p)) or Usage)
    missing = tmp_path / "chua_co"
    assert not missing.exists()
    assert HBR.dest_free_bytes(missing) == 77
    assert seen == [tmp_path]


def test_dest_free_bytes_di_len_toi_thu_muc_co(monkeypatch, tmp_path):
    seen = []

    class Usage:
        free = 88

    monkeypatch.setattr(HBR.shutil, "disk_usage", lambda p: seen.append(Path(p)) or Usage)
    missing = tmp_path / "a" / "b" / "c"
    assert not missing.exists()
    assert HBR.dest_free_bytes(missing) == 88
    assert seen == [tmp_path]


def test_dem_xong_bo_qua_part_mp4(tmp_path):
    (tmp_path / "a.mp4").write_bytes(b"1")
    (tmp_path / "a.part.mp4").write_bytes(b"2")
    (tmp_path / "b.mp4").write_bytes(b"3")
    (tmp_path / "ghi_chu.txt").write_text("x")
    assert HBR.done_mp4_count(tmp_path) == 2


def test_mix_wav_expected_bytes_uoc_va_file_co(tmp_path):
    mix = tmp_path / "mix.wav"
    assert HBR.mix_wav_expected_bytes(4.0, mix) == 44 + int(4.0 * 48000) * 2 * 3
    mix.write_bytes(b"x" * 99)
    assert HBR.mix_wav_expected_bytes(4.0, mix) == 99


def test_disk_shortfall_dung_2_lan_va_dung_cau():
    GiB = 1024 ** 3
    assert HBR.disk_shortfall_message(3 * GiB, 5 * GiB) == "đĩa không đủ chỗ: còn 5.00 GB, cần ~6.00 GB"
    assert HBR.disk_shortfall_message(3 * GiB, 6 * GiB) is None
    assert HBR.disk_shortfall_message(3 * GiB, 6 * GiB - 1) is not None


def test_quarantine_hau_to_gio_va_khong_de(tmp_path, monkeypatch):
    trash = tmp_path / "trash"
    monkeypatch.setattr(HBR, "_broken_trash_dir", lambda: trash)
    monkeypatch.setattr(HBR.time, "strftime", lambda _fmt: "20261110_153045")
    src_dir = tmp_path / "work"
    src_dir.mkdir()
    src = src_dir / "a.mp4"
    src.write_bytes(b"1")
    first = HBR.quarantine_broken_mp4(src)
    assert first.name == "a.mp4.broken_20261110_153045"
    assert first.read_bytes() == b"1" and not src.exists()
    src.write_bytes(b"2")
    second = HBR.quarantine_broken_mp4(src)
    assert second.name == "a.mp4.broken_20261110_153045_2"
    assert second.read_bytes() == b"2" and first.read_bytes() == b"1"


def _short_row():
    return {"id": "s1", "series": "law", "style": "clean", "script": ["Một câu ngắn."], "badge": ""}


def test_render_one_mp4_tot_van_bo_qua(tmp_path, monkeypatch):
    monkeypatch.setattr(HBR, "_broken_trash_dir", lambda: tmp_path / "trash")
    monkeypatch.setattr(HBR, "probe_duration_s", lambda _p: 4.0)
    monkeypatch.setattr(HBR, "render_tts", lambda *_a, **_k: pytest.fail("không được TTS"))
    mp4 = tmp_path / "s1.mp4"
    mp4.write_bytes(b"GOOD")
    ok, note = HBR.render_one(_short_row(), tmp_path, "draft")
    assert ok and note == "đã có"
    assert mp4.read_bytes() == b"GOOD"
    assert not (tmp_path / "trash").exists()


def test_render_one_mp4_hong_khong_bo_qua(tmp_path, monkeypatch, capsys):
    trash = tmp_path / "trash"
    monkeypatch.setattr(HBR, "_broken_trash_dir", lambda: trash)
    monkeypatch.setattr(HBR, "probe_duration_s", lambda _p: None)
    called = []
    monkeypatch.setattr(HBR, "render_tts", lambda *_a, **_k: called.append(True) or False)
    mp4 = tmp_path / "s1.mp4"
    mp4.write_bytes(b"BROKEN")
    ok, note = HBR.render_one(_short_row(), tmp_path, "draft")
    assert not ok and note != "đã có" and "TTS" in note
    assert called == [True]
    assert not mp4.exists()
    trashed = list(trash.iterdir())
    assert len(trashed) == 1 and trashed[0].read_bytes() == b"BROKEN"
    assert re.fullmatch(r"s1\.mp4\.broken_\d{8}_\d{6}", trashed[0].name)
    logged = capsys.readouterr().out
    assert "CẢNH BÁO" in logged and "hỏng" in logged


@pytest.fixture
def chap(tmp_path, monkeypatch):
    """Một video theo chương, chương đã cache. ffprobe/ffmpeg/df đều giả."""
    monkeypatch.setenv("VIENEU_LOCK_DIR", str(tmp_path / "locks"))
    monkeypatch.delenv("VIENEU_FINAL_MIX_RAM_GATE", raising=False)
    trash = tmp_path / "trash"
    monkeypatch.setattr(HBR, "_broken_trash_dir", lambda: trash)

    out = tmp_path / "out"
    rid = "L_bud_P3_ananda"
    cdir = out / f"{rid}_chapters"
    cdir.mkdir(parents=True)
    chapter = cdir / "ch00.mp4"
    chapter.write_bytes(b"CHAPTER-OK")
    (cdir / "ch00.render.json").write_text(
        json.dumps({"input_sha1": "abc", "media_credits": ["nguon"]}), encoding="utf-8")
    (out / f"{rid}.wav").write_bytes(b"RIFF")
    (out / f"{rid}.json").write_text(json.dumps({
        "duration_s": 4.0, "segments": [{"start": 0.0, "end": 4.0}],
    }), encoding="utf-8")
    txt = out / f"{rid}.txt"
    txt.write_text("Xin chào.\n", encoding="utf-8")
    wav = out / f"{rid}.wav"
    row = {
        "id": rid, "series": "bud", "style": "lacquer_long", "lane": "long",
        "script": ["Xin chào."], "chapters": True, "badge": "",
    }
    monkeypatch.setattr(HBR, "chapter_spans", lambda lines, segs, total: [(0, 1, 0.0, 4.0)])
    monkeypatch.setattr(HBR, "chapter_key", lambda *_a, **_k: "abc")
    monkeypatch.setattr(HBR, "pacing", lambda _row, _segs: ({}, []))
    monkeypatch.setattr(HBR, "long_pool", lambda _row: None)
    monkeypatch.setattr(HBR, "note_bgm", lambda _row, _mixed: [])

    import soundfile as sf
    monkeypatch.setattr(sf, "read", lambda *_a, **_k: ([0.0] * 16000, 16000))
    monkeypatch.setattr(sf, "write", lambda *_a, **_k: None)

    state = {"ffmpeg": 0, "bridge": 0, "mux_out": None, "part_bytes": b"FINAL-NEW", "final_during_mux": "unset"}

    def probe(path):
        path = Path(path)
        if not path.is_file():
            return None
        blob = path.read_bytes()
        if blob.startswith(b"BROKEN") or blob.startswith(b"PART-BAD"):
            return None
        return 9.0

    def run(cmd, **_k):
        if cmd and cmd[0] == "ffmpeg":
            state["ffmpeg"] += 1
            Path(cmd[-1]).write_bytes(b"SILENT-OK")
            return _cp(cmd, 0)
        state["bridge"] += 1
        outp = Path(cmd[cmd.index("--output") + 1])
        outp.write_bytes(b"CHAPTER-NEW")
        return _cp(cmd, 0, '{"media_credits": ["moi"]}\n')

    monkeypatch.setattr(HBR, "probe_duration_s", probe)
    monkeypatch.setattr(HBR.subprocess, "run", run)

    import hf_foley
    import hyperframes_bridge as HB

    def mux(_video, _narration, output, **_k):
        output = Path(output)
        state["mux_out"] = output
        final = out / f"{rid}.mp4"
        state["final_during_mux"] = final.read_bytes() if final.is_file() else None
        assert output.name == f"{rid}.part.mp4"
        output.write_bytes(state["part_bytes"])
        if final.is_file():
            assert final.read_bytes() == state["final_during_mux"]

    monkeypatch.setattr(HB, "build_lines", lambda *_a, **_k: [])
    monkeypatch.setattr(HB, "apply_visuals", lambda *_a, **_k: None)
    monkeypatch.setattr(HB, "mux_audio", mux)
    monkeypatch.setattr(hf_foley, "mix_long", lambda *_a, **_k: None)

    monkeypatch.setattr(HBR, "dest_free_bytes", lambda _p: 50 * 1024 ** 3)
    return {"out": out, "row": row, "rid": rid, "cdir": cdir, "trash": trash,
            "state": state, "chapter": chapter, "txt": txt, "wav": wav}


def _render(box):
    return HBR.render_chapters(box["row"], box["out"], "looks", box["txt"], box["wav"], "")


def test_file_cuoi_tot_van_bo_qua(chap):
    final = chap["out"] / f"{chap['rid']}.mp4"
    final.write_bytes(b"GOOD-VIDEO")
    ok, note = _render(chap)
    assert ok and note == "đã có"
    assert final.read_bytes() == b"GOOD-VIDEO"
    assert chap["state"]["ffmpeg"] == 0 and chap["state"]["mux_out"] is None
    assert not chap["trash"].exists()


def test_file_cuoi_hong_khong_bo_qua_roi_doi_ten_sau_khi_ghep(chap):
    final = chap["out"] / f"{chap['rid']}.mp4"
    part = chap["out"] / f"{chap['rid']}.part.mp4"
    final.write_bytes(b"BROKEN-moov")
    ok, note = _render(chap)
    assert ok and note == "xong"
    assert final.read_bytes() == b"FINAL-NEW"
    assert not part.exists()
    assert chap["state"]["mux_out"] == part
    assert chap["state"]["final_during_mux"] is None   # mux ghi vào .part, chưa có tên thật
    assert chap["state"]["ffmpeg"] == 1
    trashed = list(chap["trash"].iterdir())
    assert len(trashed) == 1 and trashed[0].read_bytes() == b"BROKEN-moov"
    assert re.fullmatch(rf"{chap['rid']}\.mp4\.broken_\d{{8}}_\d{{6}}", trashed[0].name)


def _expected_mux_bytes(chap, mix=None):
    ch = chap["chapter"].stat().st_size
    mix_path = mix if mix is not None else chap["cdir"] / "mix.wav"
    return ch + HBR.mix_wav_expected_bytes(4.0, mix_path)


def test_thieu_cho_dung_truoc_khi_ghep(chap, monkeypatch):
    expected = _expected_mux_bytes(chap)
    free = expected * 2 - 1
    monkeypatch.setattr(HBR, "dest_free_bytes", lambda _p: free)
    ok, note = _render(chap)
    assert not ok
    assert note == HBR.disk_shortfall_message(expected, free)
    assert note.startswith("đĩa không đủ chỗ: còn ") and "cần ~" in note and note.endswith(" GB")
    assert chap["state"]["ffmpeg"] == 0 and chap["state"]["mux_out"] is None
    assert not (chap["cdir"] / "silent.mp4").exists()
    assert not (chap["out"] / f"{chap['rid']}.part.mp4").exists()
    assert not (chap["out"] / f"{chap['rid']}.mp4").exists()


def test_nguong_cho_cong_mix_wav_da_co(chap, monkeypatch):
    mix = chap["cdir"] / "mix.wav"
    mix.write_bytes(b"M" * 1000)
    expected = _expected_mux_bytes(chap, mix)
    assert expected == chap["chapter"].stat().st_size + 1000
    free = expected * 2 - 1
    monkeypatch.setattr(HBR, "dest_free_bytes", lambda _p: free)
    ok, note = _render(chap)
    assert not ok
    assert note == HBR.disk_shortfall_message(expected, free)
    assert chap["state"]["ffmpeg"] == 0 and chap["state"]["mux_out"] is None


def test_part_hong_khong_doi_ten(chap):
    chap["state"]["part_bytes"] = b"PART-BAD"
    part = chap["out"] / f"{chap['rid']}.part.mp4"
    final = chap["out"] / f"{chap['rid']}.mp4"
    ok, note = _render(chap)
    assert not ok and "chưa đổi tên" in note
    assert not final.exists()
    assert not part.exists()
    assert chap["state"]["mux_out"] == part
    assert chap["state"]["ffmpeg"] == 1
    trashed = list(chap["trash"].iterdir())
    assert len(trashed) == 1 and trashed[0].read_bytes() == b"PART-BAD"
    assert re.fullmatch(rf"{chap['rid']}\.part\.mp4\.broken_\d{{8}}_\d{{6}}", trashed[0].name)


def test_file_cu_tot_khong_bi_ghi_de_khi_part_hong(chap, monkeypatch):
    monkeypatch.setattr(HBR, "chapter_key", lambda *_a, **_k: "khac")
    final = chap["out"] / f"{chap['rid']}.mp4"
    final.write_bytes(b"GOOD-OLD")
    chap["state"]["part_bytes"] = b"PART-BAD"
    ok, note = _render(chap)
    assert not ok and "chưa đổi tên" in note
    assert final.read_bytes() == b"GOOD-OLD"
    assert chap["state"]["final_during_mux"] == b"GOOD-OLD"
    assert chap["state"]["bridge"] == 1
    assert not (chap["out"] / f"{chap['rid']}.part.mp4").exists()
    trashed = [p for p in chap["trash"].iterdir() if p.read_bytes() == b"PART-BAD"]
    assert len(trashed) == 1


def test_chuong_hong_khong_dung_cache(chap, monkeypatch):
    chap["chapter"].write_bytes(b"BROKEN-ch")

    def run(cmd, **_k):
        if cmd and cmd[0] == "ffmpeg":
            raise AssertionError("không được ghép khi chương chưa render lại")
        chap["state"]["bridge"] += 1
        return _cp(cmd, 1, "", "render fail")

    monkeypatch.setattr(HBR.subprocess, "run", run)
    ok, note = _render(chap)
    assert not ok and "chương ch00" in note
    assert chap["state"]["bridge"] == 1
    assert not chap["chapter"].exists()
    trashed = list(chap["trash"].iterdir())
    assert len(trashed) == 1 and trashed[0].read_bytes() == b"BROKEN-ch"
    assert ".broken_" in trashed[0].name


def test_resume_chuong_doi_ghep_hong_lan_2_khong_bao_da_co(chap, monkeypatch):
    """Lần 1 chương đổi + ghép hỏng; lần 2 chương khớp nhưng file cuối cũ hơn chương → phải ghép lại."""
    final = chap["out"] / f"{chap['rid']}.mp4"
    final.write_bytes(b"GOOD-OLD")
    old = 1_700_000_000.0
    os.utime(final, (old, old))
    monkeypatch.setattr(HBR, "chapter_key", lambda *_a, **_k: "khac")
    chap["state"]["part_bytes"] = b"PART-BAD"
    ok, note = _render(chap)
    assert not ok and "chưa đổi tên" in note
    assert final.read_bytes() == b"GOOD-OLD"
    assert chap["chapter"].stat().st_mtime > final.stat().st_mtime

    chap["state"]["part_bytes"] = b"FINAL-NEW"
    chap["state"]["ffmpeg"] = 0
    chap["state"]["bridge"] = 0
    chap["state"]["mux_out"] = None
    ok, note = _render(chap)
    assert ok and note == "xong"
    assert final.read_bytes() == b"FINAL-NEW"
    assert chap["state"]["mux_out"] is not None
    assert chap["state"]["ffmpeg"] == 1


def test_file_cuoi_cu_hon_mix_phai_ghep_lai(chap):
    final = chap["out"] / f"{chap['rid']}.mp4"
    final.write_bytes(b"GOOD-OLD")
    mix = chap["cdir"] / "mix.wav"
    mix.write_bytes(b"MIX")
    silent = chap["cdir"] / "silent.mp4"
    silent.write_bytes(b"SILENT-OK")
    old = 1_700_000_000.0
    os.utime(final, (old, old))
    os.utime(chap["chapter"], (old - 10, old - 10))
    ok, note = _render(chap)
    assert ok and note == "xong"
    assert final.read_bytes() == b"FINAL-NEW"
    assert chap["state"]["mux_out"] is not None


def test_file_cuoi_moi_hon_mix_van_bo_qua(chap):
    mix = chap["cdir"] / "mix.wav"
    mix.write_bytes(b"MIX")
    silent = chap["cdir"] / "silent.mp4"
    silent.write_bytes(b"SILENT-OK")
    old = 1_700_000_000.0
    os.utime(chap["chapter"], (old, old))
    os.utime(mix, (old + 1, old + 1))
    os.utime(silent, (old + 2, old + 2))
    final = chap["out"] / f"{chap['rid']}.mp4"
    final.write_bytes(b"GOOD-VIDEO")
    os.utime(final, (old + 10, old + 10))
    ok, note = _render(chap)
    assert ok and note == "đã có"
    assert final.read_bytes() == b"GOOD-VIDEO"
    assert chap["state"]["ffmpeg"] == 0 and chap["state"]["mux_out"] is None


def test_newer_than_inputs(tmp_path):
    outp = tmp_path / "out.mp4"
    a = tmp_path / "a.mp4"
    b = tmp_path / "b.wav"
    outp.write_bytes(b"o")
    a.write_bytes(b"a")
    old = 1_700_000_000.0
    os.utime(a, (old, old))
    os.utime(outp, (old + 5, old + 5))
    assert HBR.newer_than_inputs(outp, [a, b])
    os.utime(a, (old + 6, old + 6))
    assert not HBR.newer_than_inputs(outp, [a, b])
    os.utime(a, (old + 5, old + 5))
    assert not HBR.newer_than_inputs(outp, [a, b])


def test_silent_hong_chuyen_vao_trash(chap, monkeypatch):
    def run(cmd, **_k):
        if cmd and cmd[0] == "ffmpeg":
            chap["state"]["ffmpeg"] += 1
            Path(cmd[-1]).write_bytes(b"BROKEN-SILENT")
            return _cp(cmd, 0)
        raise AssertionError("không được gọi bridge khi nối silent hỏng")

    monkeypatch.setattr(HBR.subprocess, "run", run)
    ok, note = _render(chap)
    assert not ok and "silent.mp4" in note
    assert not (chap["cdir"] / "silent.mp4").exists()
    assert chap["state"]["mux_out"] is None
    trashed = list(chap["trash"].iterdir())
    assert len(trashed) == 1 and trashed[0].read_bytes() == b"BROKEN-SILENT"
    assert "silent.mp4.broken_" in trashed[0].name


def test_silent_ffmpeg_loi_cung_chuyen_vao_trash(chap, monkeypatch):
    def run(cmd, **_k):
        if cmd and cmd[0] == "ffmpeg":
            chap["state"]["ffmpeg"] += 1
            Path(cmd[-1]).write_bytes(b"BROKEN-FF")
            return _cp(cmd, 1, "", "concat error")
        raise AssertionError("không được gọi bridge khi ffmpeg nối lỗi")

    monkeypatch.setattr(HBR.subprocess, "run", run)
    ok, note = _render(chap)
    assert not ok and "nối chương lỗi" in note
    assert not (chap["cdir"] / "silent.mp4").exists()
    trashed = list(chap["trash"].iterdir())
    assert len(trashed) == 1 and trashed[0].read_bytes() == b"BROKEN-FF"
