"""Hợp đồng đầu ra Long (GH-170, docs/pm/tickets/GH-170-contract.md): ghi nguyên tử + manifest lượt final.

Builder ghi file tạm cùng thư mục, kiểm hợp lệ, rồi `publish` (os.replace). Consumer gọi `final_problems`:
có manifest mà không `ok` thì fail closed dù final.mp4 cũ còn nguyên.

    python motion/long/long_output.py check <topic>     # mã thoát 0 = final hợp lệ
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
import uuid
from datetime import datetime
from pathlib import Path

MANIFEST = "final.run.json"


def temp_path(dst: Path) -> Path:
    """Tên tạm cùng thư mục, giữ đuôi (ffmpeg/renderer chọn muxer theo đuôi). KHÔNG tạo sẵn file."""
    return dst.with_name(f".{dst.stem}-{uuid.uuid4().hex[:8]}{dst.suffix}")


def sweep_temps(dst: Path) -> None:
    """Dọn file tạm mồ côi (kill -9) của `dst`: đúng mẫu `temp_path(dst)`, kể cả tạm-của-tạm (`..`). Gọi khi đang giữ khoá."""
    for pat in (f".{dst.stem}-*{dst.suffix}", f"..{dst.stem}-*{dst.suffix}"):
        for p in dst.parent.glob(pat):
            try:
                p.unlink()
            except OSError:
                pass


def publish(src: Path, dst: Path, what: str) -> None:
    """os.replace; bị khoá/lỗi hệ thống thì báo rõ và giữ nguyên bản cũ."""
    try:
        os.replace(src, dst)
    except OSError as e:
        raise SystemExit(f"{what}: không ghi được {dst.name} ({e}); bản cũ giữ nguyên, file bị khoá? Đóng chương trình đang mở nó rồi chạy lại")


def remove(path: Path, what: str) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError as e:
        raise SystemExit(f"{what}: không xoá được {path.name} ({e})")


def atomic_write_text(path: Path, text: str, what: str = "ghi") -> None:
    tmp = temp_path(path)
    try:
        tmp.write_text(text, encoding="utf-8")
        publish(tmp, path, what)
    finally:
        tmp.unlink(missing_ok=True)


def wav_complete(path: Path) -> bool:
    """Header RIFF/data khớp kích thước thật: bắt file bị cắt dở mà libsndfile vẫn giải mã được."""
    try:
        size = path.stat().st_size
        with open(path, "rb") as f:
            head = f.read(12)
            if len(head) < 12 or head[:4] != b"RIFF" or head[8:12] != b"WAVE":
                return False
            if struct.unpack("<I", head[4:8])[0] + 8 > size:
                return False
            while True:
                ch = f.read(8)
                if len(ch) < 8:
                    return False
                cid, n = ch[:4], struct.unpack("<I", ch[4:])[0]
                if cid == b"data":
                    return n > 0 and f.tell() + n <= size
                f.seek(n + (n & 1), os.SEEK_CUR)
    except OSError:
        return False


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _write_manifest(od: Path, m: dict) -> None:
    atomic_write_text(od / MANIFEST, json.dumps(m, ensure_ascii=False, indent=1), "manifest final")


def begin_run(od: Path) -> dict:
    """Ghi `running` TRƯỚC khi đụng final cũ. Không ghi được thì dừng (chưa đổi gì)."""
    od.mkdir(parents=True, exist_ok=True)
    m = {"schema": 1, "run_id": uuid.uuid4().hex[:12], "state": "running", "started_at": _now()}
    sweep_temps(od / MANIFEST)
    _write_manifest(od, m)
    return m


def finish_ok(od: Path, m: dict, chapters: dict) -> None:
    fin, cap = od / "final.mp4", od / "captions.vi.srt"
    m = {**m, "state": "ok", "finished_at": _now(), "error": None, "chapters": chapters,
         "final": {"size": fin.stat().st_size, "sha256": sha256(fin)},
         "captions": {"size": cap.stat().st_size, "sha256": sha256(cap)}}
    _write_manifest(od, m)


def finish_failed(od: Path, m: dict, err: BaseException) -> None:
    detail = str(err) if isinstance(err, SystemExit) else f"{type(err).__name__}: {err}"
    try:
        _write_manifest(od, {**m, "state": "failed", "finished_at": _now(), "error": detail[-1500:]})
    except BaseException as e:      # noqa: BLE001  (vẫn còn `running` -> consumer vẫn chặn)
        print(f"  ! không ghi được manifest failed ({e}); manifest vẫn là running nên consumer vẫn chặn", flush=True)


def final_problems(od: Path, full: bool = False) -> list[str]:
    """Rỗng = final dùng được. Không manifest = legacy (dựng trước GH-170): chấp nhận nếu file còn."""
    mf = od / MANIFEST
    fin, cap = od / "final.mp4", od / "captions.vi.srt"
    if not mf.exists():
        return [] if fin.exists() else ["final.mp4 chưa có"]
    try:
        m = json.loads(mf.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"{MANIFEST} không đọc được ({e}): coi như lượt final hỏng"]
    if m.get("state") != "ok":
        return [f"lượt final {m.get('run_id')} trạng thái {m.get('state')}: final.mp4 hiện có KHÔNG phải kết quả lượt này"
                + (f" ({m['error'][:300]})" if m.get("error") else "") + "; chạy lại `build_long.py <topic> final`"]
    bad = []
    for name, key in (m.get("chapters") or {}).items():      # chương bị render lại/đổi sau lượt final này thì final không còn khớp
        try:
            cur = (od / name / "silent.key").read_text()
        except OSError:
            cur = None
        if cur != key:
            bad.append(f"chương {name} đã đổi sau lượt final (silent.key khác manifest)")
    for key, p in (("final", fin), ("captions", cap)):
        want = m.get(key) or {}
        if not p.exists():
            bad.append(f"{p.name} thiếu")
        elif p.stat().st_size != want.get("size"):
            bad.append(f"{p.name} khác manifest (kích thước)")
        elif full and sha256(p) != want.get("sha256"):
            bad.append(f"{p.name} khác manifest (sha256)")
    return bad


if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT))
    from factory.console import utf8_console  # noqa: E402
    utf8_console()
    if len(sys.argv) != 3 or sys.argv[1] != "check":
        raise SystemExit(__doc__)
    probs = final_problems(ROOT / "output" / "long" / sys.argv[2], full=True)
    for p in probs:
        print("  LỖI", p)
    print("final hợp lệ" if not probs else "final KHÔNG hợp lệ")
    sys.exit(1 if probs else 0)
