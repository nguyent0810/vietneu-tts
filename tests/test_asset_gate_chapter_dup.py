"""030: asset_gate chặn ảnh/clip trùng SHA1 trong cùng chương (luật engine)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load_asset_gate():
    gate_path = ROOT / "tools/long/asset_gate.py"
    if not gate_path.exists():
        raise AssertionError("tools/long/asset_gate.py missing")
    spec = importlib.util.spec_from_file_location("asset_gate", gate_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _write(p: Path, blob: bytes) -> str:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(blob)
    return str(p)


def _row(script: list[str], media: dict) -> dict:
    return {"id": "L_test_dup", "script": script, "media": media}


def _plan(tmp: Path, row: dict) -> Path:
    p = tmp / "plan.json"
    p.write_text(json.dumps([row], ensure_ascii=False), encoding="utf-8")
    return p


HEADING = "**Chương hai**"
SCRIPT = [
    "Câu một mở.",
    "Câu hai kể.",
    "Câu ba kể.",
    "Câu bốn kể.",
    HEADING,
    "Câu sáu sang chương.",
    "Câu bảy kể tiếp.",
    "Câu tám kết.",
]


def test_chapter_starts_match_engine_spans():
    import hf_batch_render as R

    ag = _load_asset_gate()
    lines = ["a", "b", "**Chương 1**", "c", "d", "**Chương 2**", "e"]
    segs, t = [], 0.0
    for _ in lines:
        segs.append({"start": t, "end": t + 2.0})
        t += 2.5
    spans = R.chapter_spans(lines, segs, t)
    assert ag.chapter_starts(lines) == [a for a, *_ in spans] == [0, 2, 5]
    # câu 0 in đậm không cắt; ** giữa câu không cắt
    mixed = ["**Mở**", "x", "giữa **chữ** đây", "**Chương**"]
    assert ag.chapter_starts(mixed) == [0, 3]


def test_same_chapter_same_file_blocked(tmp_path: Path):
    ag = _load_asset_gate()
    a = _write(tmp_path / "a.jpg", b"AAA-bytes")
    b = _write(tmp_path / "b.jpg", b"BBB-bytes")
    media = {
        "1": {"kind": "local", "path": a},
        "3": {"kind": "local", "path": a},
        "6": {"kind": "local", "path": b},
    }
    issues = ag.chapter_dup_issues(_row(SCRIPT, media), ROOT)
    assert issues == ["ch00: câu 3 (a.jpg) trùng hệt câu 1 (a.jpg)"]
    bad = ag.check(_plan(tmp_path, _row(SCRIPT, media)))
    assert any("trùng hệt" in x for x in bad)


def test_same_file_different_chapter_allowed(tmp_path: Path):
    ag = _load_asset_gate()
    a = _write(tmp_path / "a.jpg", b"AAA-bytes")
    b = _write(tmp_path / "b.jpg", b"BBB-bytes")
    media = {
        "1": {"kind": "local", "path": a},
        "6": {"kind": "local", "path": a},  # sang chương (câu 5 = heading)
        "7": {"kind": "local", "path": b},
    }
    issues = ag.chapter_dup_issues(_row(SCRIPT, media), ROOT)
    assert issues == []
    bad = ag.check(_plan(tmp_path, _row(SCRIPT, media)))
    assert not any("trùng hệt" in x or "trùng trong cùng chương" in x for x in bad)


def test_different_name_same_bytes_blocked(tmp_path: Path):
    ag = _load_asset_gate()
    blob = b"SAME-CONTENT-BYTES"
    a = _write(tmp_path / "one.jpg", blob)
    b = _write(tmp_path / "two.png", blob)
    media = {
        "2": {"kind": "local", "path": a},
        "4": {"kind": "local", "path": b},
    }
    issues = ag.chapter_dup_issues(_row(SCRIPT, media), ROOT)
    assert issues == ["ch00: câu 4 (two.png) trùng hệt câu 2 (one.jpg)"]


def test_same_name_different_bytes_allowed(tmp_path: Path):
    ag = _load_asset_gate()
    a = _write(tmp_path / "dir1" / "shot.jpg", b"LEFT")
    b = _write(tmp_path / "dir2" / "shot.jpg", b"RIGHT")
    media = {
        "1": {"kind": "local", "path": a},
        "3": {"kind": "local", "path": b},
    }
    assert ag.chapter_dup_issues(_row(SCRIPT, media), ROOT) == []


def test_same_source_different_crop_allowed(tmp_path: Path):
    """Engine hash sau _frame_local_image(crop) -- crop khác = byte khác."""
    ag = _load_asset_gate()
    a = _write(tmp_path / "wide.jpg", b"WIDE-SRC")
    media = {
        "1": {"kind": "local", "path": a, "crop": [0.2, 0.0, 0.72]},
        "3": {"kind": "local", "path": a, "crop": [0.8, 0.0]},  # zoom mặc định 0.72, khác fx
    }
    assert ag.chapter_dup_issues(_row(SCRIPT, media), ROOT) == []
    same_crop = {
        "1": {"kind": "local", "path": a, "crop": [0.5, 0.0]},
        "3": {"kind": "local", "path": a, "crop": [0.5, 0.0, 0.72]},
    }
    issues = ag.chapter_dup_issues(_row(SCRIPT, same_crop), ROOT)
    assert len(issues) == 1


def test_lists_all_pairs_in_one_run(tmp_path: Path):
    ag = _load_asset_gate()
    a = _write(tmp_path / "a.jpg", b"AAA")
    b = _write(tmp_path / "b.jpg", b"BBB")
    media = {
        "1": {"path": a},
        "2": {"path": a},
        "3": {"path": a},
        "6": {"path": b},
        "8": {"path": b},
    }
    issues = ag.chapter_dup_issues(_row(SCRIPT, media), ROOT)
    # ch00: 3 mốc a -> 3 cặp; ch01: 2 mốc b -> 1 cặp. File đi với đúng câu.
    assert issues == [
        "ch00: câu 2 (a.jpg) trùng hệt câu 1 (a.jpg)",
        "ch00: câu 3 (a.jpg) trùng hệt câu 1 (a.jpg)",
        "ch00: câu 3 (a.jpg) trùng hệt câu 2 (a.jpg)",
        "ch01: câu 8 (b.jpg) trùng hệt câu 6 (b.jpg)",
    ]


def test_chapter_of_nonpositive_is_ch00():
    ag = _load_asset_gate()
    starts = ag.chapter_starts(SCRIPT)
    assert ag.chapter_of(0, starts) == 0
    assert ag.chapter_of(-1, starts) == 0
    assert ag.chapter_of(1, starts) == 0


def test_media_key_zero_same_chapter_blocked(tmp_path: Path):
    ag = _load_asset_gate()
    a = _write(tmp_path / "a.jpg", b"AAA-bytes")
    media = {"0": {"path": a}, "1": {"path": a}}
    issues = ag.chapter_dup_issues(_row(SCRIPT, media), ROOT)
    assert issues == ["ch00: câu 1 (a.jpg) trùng hệt câu 0 (a.jpg)"]


def test_mp4_repeat_blocked_even_if_crop_differs(tmp_path: Path):
    """Bridge kind local + .mp4/.mov/.webm: shutil.copy2, không đọc crop."""
    ag = _load_asset_gate()
    clip = _write(tmp_path / "shot.mp4", b"MP4-BYTES-NOT-A-REAL-CONTAINER")
    media = {
        "1": {"kind": "local", "path": clip, "crop": [0.2, 0.0, 0.5]},
        "3": {"kind": "local", "path": clip, "crop": [0.8, 0.4, 0.9]},
    }
    issues = ag.chapter_dup_issues(_row(SCRIPT, media), ROOT)
    assert issues == ["ch00: câu 3 (shot.mp4) trùng hệt câu 1 (shot.mp4)"]


def test_heading_media_joins_new_chapter(tmp_path: Path):
    ag = _load_asset_gate()
    a = _write(tmp_path / "head.jpg", b"HEAD-BYTES")
    # Câu 5 là tiêu đề in đậm -> chương mới. Trùng câu 6 cùng chương thì chặn.
    same = {"5": {"path": a}, "6": {"path": a}}
    issues = ag.chapter_dup_issues(_row(SCRIPT, same), ROOT)
    assert issues == ["ch01: câu 6 (head.jpg) trùng hệt câu 5 (head.jpg)"]
    # Trùng câu 4 (chương trước) thì không chặn.
    prev = {"4": {"path": a}, "5": {"path": a}}
    assert ag.chapter_dup_issues(_row(SCRIPT, prev), ROOT) == []


def test_no_heading_script_is_all_ch00(tmp_path: Path):
    ag = _load_asset_gate()
    lines = ["Một.", "Hai.", "Ba.", "Bốn."]
    assert ag.chapter_starts(lines) == [0]
    a = _write(tmp_path / "a.jpg", b"AAA")
    issues = ag.chapter_dup_issues(_row(lines, {"1": {"path": a}, "4": {"path": a}}), ROOT)
    assert issues == ["ch00: câu 4 (a.jpg) trùng hệt câu 1 (a.jpg)"]


def test_missing_file_falls_back_to_path_key(tmp_path: Path):
    ag = _load_asset_gate()
    ghost = str(tmp_path / "absent" / "ghost.jpg")
    other = str(tmp_path / "absent" / "other.jpg")
    assert ag.resolve_file(ghost, ROOT) is None
    d1 = ag.engine_digest({"path": ghost}, ghost, ROOT)
    assert d1 == "path:" + ghost
    assert ag.engine_digest({"path": other}, other, ROOT) == "path:" + other
    assert d1 != ag.engine_digest({"path": other}, other, ROOT)
    issues = ag.chapter_dup_issues(_row(SCRIPT, {"1": {"path": ghost}, "3": {"path": ghost}}), ROOT)
    assert issues == ["ch00: câu 3 (ghost.jpg) trùng hệt câu 1 (ghost.jpg)"]


def test_bad_crop_does_not_crash(tmp_path: Path):
    ag = _load_asset_gate()
    a = _write(tmp_path / "a.jpg", b"AAA-bytes")
    omitted = ag.engine_digest({"path": a}, a, ROOT)
    assert ag.engine_digest({"path": a, "crop": []}, a, ROOT) == omitted
    assert ag.engine_digest({"path": a, "crop": {}}, a, ROOT) == omitted
    dict_crop = ag.engine_digest({"path": a, "crop": {"fx": 0.2, "fy": 0.1}}, a, ROOT)
    short = ag.engine_digest({"path": a, "crop": [0.4]}, a, ROOT)
    assert dict_crop is not None and short is not None
    assert dict_crop != omitted and short != omitted
    assert "|crop=" in dict_crop and "|crop=" in short
    media = {
        "1": {"path": a, "crop": {"fx": 0.2}},
        "2": {"path": a, "crop": []},
        "3": {"path": a, "crop": [0.2]},
        "4": {"path": a, "crop": {}},
    }
    ag.chapter_dup_issues(_row(SCRIPT, media), ROOT)


def test_omitted_crop_differs_from_explicit_default_zoom(tmp_path: Path):
    """Thiếu crop = không cắt. [fx, fy] thiếu zoom mới mặc định 0.72."""
    ag = _load_asset_gate()
    a = _write(tmp_path / "wide.jpg", b"WIDE-SRC")
    none_vs_explicit = {
        "1": {"path": a},
        "3": {"path": a, "crop": [0.5, 0.5, 0.72]},
    }
    assert ag.chapter_dup_issues(_row(SCRIPT, none_vs_explicit), ROOT) == []


def test_sha1_chunked_matches_full_file(tmp_path: Path):
    ag = _load_asset_gate()
    blob = (b"abc123" * 200_000) + b"Z"  # vượt biên khối 1 MB
    p = _write(tmp_path / "big.mp4", blob)
    assert ag.engine_digest({"path": p}, p, ROOT) == hashlib.sha1(blob).hexdigest()
    assert ag._sha1_file(Path(p)) == hashlib.sha1(Path(p).read_bytes()).hexdigest()


def test_check_prints_every_pair_and_fails(tmp_path: Path):
    ag = _load_asset_gate()
    a = _write(tmp_path / "a.jpg", b"AAA")
    b = _write(tmp_path / "b.jpg", b"BBB")
    media = {
        "1": {"path": a},
        "2": {"path": a},
        "3": {"path": a},
        "6": {"path": b},
        "8": {"path": b},
    }
    plan = _plan(tmp_path, _row(SCRIPT, media))
    bad = ag.check(plan)
    pairs = [
        "ch00: câu 2 (a.jpg) trùng hệt câu 1 (a.jpg)",
        "ch00: câu 3 (a.jpg) trùng hệt câu 1 (a.jpg)",
        "ch00: câu 3 (a.jpg) trùng hệt câu 2 (a.jpg)",
        "ch01: câu 8 (b.jpg) trùng hệt câu 6 (b.jpg)",
    ]
    for line in pairs:
        assert line in bad
    assert any("cặp ảnh/clip trùng" in x for x in bad)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools/long/asset_gate.py"), str(plan)],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert proc.returncode != 0
    for line in pairs:
        assert line in proc.stdout
    assert "  ĐẠT" not in proc.stdout
