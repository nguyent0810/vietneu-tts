"""O9 (12/11): khung bảng tra/sơ đồ dữ liệu không tính là "đồng màu"; phần trống ngoài sơ đồ vẫn chặn.
Trống số bảng tra chỉ quay tới năm sau vòng chờ."""
from pathlib import Path

import hf_batch_render as H

ROOT = Path(__file__).resolve().parents[1]


def _row(vtype="lookup"):
    script = [f"Câu **số {i}** ngắn gọn." for i in range(1, 21)]
    media = {str(i): {"kind": "local", "path": f"x{i}.png"} for i in range(1, 21) if i not in (5, 6)}
    spec = {"type": "lookup", "title": "T", "cols": ["A", "B"], "rows": [{"cells": ["Tý", "x"]}], "until": 6}
    if vtype == "word":
        spec = {"type": "word", "text": "chữ", "until": 6}
    visuals = {"5": spec}
    return {"id": "L_test_o9", "script": script, "media": media, "visuals": visuals}


def _segs():
    return [{"start": i * 2.0, "end": i * 2.0 + 1.8} for i in range(20)]


def _run(monkeypatch, tmp_path, viol, vtype="lookup"):
    mp4 = tmp_path / "v.mp4"; mp4.write_bytes(b"x")
    monkeypatch.setattr(H, "check_opening_solid_frames", lambda *a, **k: viol)
    errs, _ = H.opening_gate(_row(vtype), _segs(), video_path=mp4)
    return [e for e in errs if e.startswith("O9")]


def test_khung_trong_bang_tra_khong_bi_chan(monkeypatch, tmp_path):
    # câu 5–6 là bảng tra: 8.0s–12.0s
    assert _run(monkeypatch, tmp_path, [{"start": 8.2, "end": 11.0, "dur": 2.8, "std": 17.5, "sim": .1}]) == []


def test_khung_trong_ngoai_bang_van_chan(monkeypatch, tmp_path):
    assert _run(monkeypatch, tmp_path, [{"start": 2.0, "end": 3.0, "dur": 1.0, "std": 3.0, "sim": .9}])
    # tràn ra ngoài bảng > 0,3 s vẫn chặn
    assert _run(monkeypatch, tmp_path, [{"start": 11.0, "end": 12.8, "dur": 1.8, "std": 3.0, "sim": .9}])


def test_trong_so_quay_sau_vong_cho():
    js = (ROOT / "hyperframes_short/compositions/longform.js").read_text(encoding="utf-8")
    assert "Math.max(t - .4, t0 + 1.95)" in js


def test_tran_ra_ngoai_bang_khong_qua_0_3s_khong_chan(monkeypatch, tmp_path):
    assert _run(monkeypatch, tmp_path, [{"start": 11.0, "end": 12.2, "dur": 1.2, "std": 3.0, "sim": .9}]) == []


def test_hai_manh_ngan_hai_ben_bang_khong_cong_don(monkeypatch, tmp_path):
    # 7.8–8.0 trước bảng (0,2 s) + 12.0–12.2 sau bảng (0,2 s): không đoạn liền nào > 0,3 s
    assert _run(monkeypatch, tmp_path, [{"start": 7.8, "end": 12.2, "dur": 4.4, "std": 3.0, "sim": .9}]) == []


def test_bao_dung_doan_ngoai_bang(monkeypatch, tmp_path):
    errs = _run(monkeypatch, tmp_path, [{"start": 11.0, "end": 12.8, "dur": 1.8, "std": 3.0, "sim": .9}])
    assert len(errs) == 1 and "0.80s" in errs[0] and "12.0s–12.8s" in errs[0]


def test_the_chu_tron_khong_duoc_mien(monkeypatch, tmp_path):
    assert _run(monkeypatch, tmp_path, [{"start": 8.2, "end": 11.0, "dur": 2.8, "std": 3.0, "sim": .9}], vtype="word")
