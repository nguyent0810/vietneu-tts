"""Cổng kiểm hình/clip cho Long pilot (Lead 07/11, sau lượt asset Flash dùng ảnh ref làm cảnh và lặp 1 ảnh 111 lần).

    python tools/long/asset_gate.py output/cl_staging/long/plan_P1_temiya.json

ĐẠT khi:
  - không media nào là ảnh ref nhân vật (đường dẫn chứa /refs/ hoặc tên REF_)
  - mỗi ảnh/clip dùng tối đa 2 lần trong video, không 2 mốc liền nhau
  - không ảnh/clip trùng byte (SHA1, đúng luật engine) trong cùng chương
  - số ảnh/clip khác nhau >= phút * 2.4 (≈ 60 cho 25 phút)
  - cold open (trước thẻ chương thứ 2 hoặc 30 câu đầu): >= 5 mốc là clip .mp4 HOẶC ảnh có `cine` (depth:true + >= 1 fx) khác nhau
  - không còn khoá `clips` chưa đổi thành media
"""
from __future__ import annotations
import hashlib, json, sys
from itertools import combinations
from pathlib import Path

RATE = 185 / 60  # tiếng/giây
_VIDEO_EXT = {".mp4", ".mov", ".webm"}


def path_of(v) -> str:
    return (v.get("path") or v.get("src") or v.get("file") or v.get("url") or "") if isinstance(v, dict) else str(v)


def is_cold_cine(v, p: str) -> bool:
    pl = (p or "").lower()
    if pl.endswith(".mp4"):
        return True
    if not isinstance(v, dict) or not pl.endswith((".jpg", ".jpeg", ".png", ".webp")):
        return False
    pan = v.get("pan")  # 09/11: cú lia panorama có depth + fx tính là cảnh động (thay clip Flow)
    if isinstance(pan, dict) and pan.get("depth") is True and pan.get("fx"):
        return True
    cine = v.get("cine")
    if not isinstance(cine, dict) or cine.get("depth") is not True:
        return False
    fx = cine.get("fx")
    return isinstance(fx, list) and len([x for x in fx if isinstance(x, str) and x.strip()]) >= 1


def chapter_starts(lines: list[str]) -> list[int]:
    """Mốc 0-indexed cắt chương -- cùng công thức `hf_batch_render.chapter_spans` (firsts).
    Tiêu đề = câu in đậm trọn câu; câu 0 dù in đậm cũng không cắt."""
    heads = [i for i, l in enumerate(lines) if i and l.startswith("**") and l.endswith("**") and l.count("**") == 2]
    return [0] + heads


def chapter_of(n: int, starts: list[int]) -> int:
    """Câu 1-indexed -> chỉ số chương (0 = ch00). Khoá n<=0 không có mốc -> ch00."""
    return max((c for c, a in enumerate(starts) if a <= n - 1), default=0)


def resolve_file(p: str, root: Path) -> Path | None:
    if not p or str(p).startswith("http"):
        return None
    cands = [Path(p)]
    for b in (root, root / "output/cl_staging/long", Path("/")):
        cands.append(b / p)
    for c in cands:
        if c.is_file():
            return c
    return None


def _crop_sig(v, p: str) -> str:
    """crop đổi byte ảnh sau `_frame_local_image`; clip copy nguyên nên bỏ qua.

    Engine không crop khi thiếu khoá `crop` (không có mặc định kiểu center 0.72).
    Zoom 0.72 chỉ điền khi crop là list [fx, fy] thiếu phần tử thứ 3 — cùng khoá với [fx, fy, 0.72].
    """
    if not isinstance(v, dict) or not v.get("crop"):
        return ""
    if Path(p).suffix.lower() in _VIDEO_EXT:
        return ""
    crop = v["crop"]
    try:
        fx, fy = float(crop[0]), float(crop[1])
        z = float(crop[2]) if len(crop) > 2 else 0.72
    except (TypeError, ValueError, LookupError):
        return f"|crop={crop!r}"
    return f"|crop={fx:g},{fy:g},{z:g}"


def _sha1_file(fp: Path) -> str:
    """SHA1 giống `read_bytes()`, đọc khối 1 MB để clip lớn không nạp hết RAM."""
    h = hashlib.sha1()
    with fp.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def engine_digest(v, p: str, root: Path) -> str | None:
    """Khoá trùng của engine: sha1(bytes) như hyperframes_bridge.seen_assets.
    File chưa có: so theo đường dẫn (cùng path = cùng byte khi tải về)."""
    if not p:
        return None
    sig = _crop_sig(v, p)
    fp = resolve_file(p, root)
    if fp is not None:
        return _sha1_file(fp) + sig
    return "path:" + p + sig


def chapter_dup_issues(row: dict, root: Path) -> list[str]:
    """Hết cặp ảnh/clip trùng SHA1 trong cùng chương. Mỗi dòng một cặp."""
    starts = chapter_starts(row["script"])
    raw = {int(k): v for k, v in (row.get("media") or {}).items() if str(k).isdigit()}
    groups: dict[tuple[int, str], list[tuple[int, str]]] = {}
    for n in sorted(raw):
        v = raw[n]
        p = path_of(v)
        digest = engine_digest(v, p, root)
        if not digest:
            continue
        ch = chapter_of(n, starts)
        groups.setdefault((ch, digest), []).append((n, Path(p).name or p))
    out = []
    for (ch, _d), occ in groups.items():
        if len(occ) < 2:
            continue
        for (n1, f1), (n2, f2) in combinations(occ, 2):
            out.append(f"ch{ch:02d}: câu {n2} ({f2}) trùng hệt câu {n1} ({f1})")
    return out


def check(plan_path: Path) -> list[str]:
    r = json.loads(plan_path.read_text(encoding="utf-8"))[0]
    lines = r["script"]
    words = sum(len(l.replace("*", "").split()) for l in lines)
    minutes = words / RATE / 60
    raw_media = {int(k): v for k, v in (r.get("media") or {}).items() if str(k).isdigit()}
    media = {k: path_of(v) for k, v in raw_media.items()}
    bad = []
    refs = [k for k, p in media.items() if "/refs/" in p or "REF_" in Path(p).name]
    if refs:
        bad.append(f"ảnh ref nhân vật dùng làm cảnh ở {len(refs)} mốc (vd câu {refs[:5]})")
    order = [media[k] for k in sorted(media)]
    from collections import Counter
    c = Counter(order)
    over = [(p, n) for p, n in c.items() if n > 2]
    if over:
        bad.append(f"{len(over)} hình dùng > 2 lần (nhiều nhất {max(n for _, n in over)} lần: {Path(max(over, key=lambda x: x[1])[0]).name})")
    adj = sum(1 for a, b in zip(order, order[1:]) if a == b)
    if adj:
        bad.append(f"{adj} chỗ cùng một hình ở 2 mốc liền nhau")
    need = int(minutes * 2.4)
    if len(c) < need:
        bad.append(f"chỉ {len(c)} hình/clip khác nhau, cần >= {need} cho {minutes:.1f} phút")
    heads = [i for i, l in enumerate(lines, 1) if l.startswith("**")]
    cold_end = heads[1] if len(heads) > 1 and heads[0] == 1 else (heads[0] if heads else 30)
    cold_end = min(cold_end, 30)
    cold_clips = {p for k, p in media.items() if k < cold_end and is_cold_cine(raw_media[k], p)}
    if len(cold_clips) < 5:
        bad.append(f"cold open (câu 1–{cold_end - 1}) chỉ có {len(cold_clips)} clip .mp4 / ảnh cine khác nhau, cần >= 5")
    root = Path(__file__).resolve().parents[2]
    missing = [p for p in set(media.values()) if p and not p.startswith("http")
               and not any((b / p).exists() for b in (root, root / "output/cl_staging/long", Path("/")))]
    if missing:
        bad.append(f"{len(missing)} file media không tồn tại (vd {missing[:2]})")
    dups = chapter_dup_issues(r, root)
    if dups:
        bad.append(f"{len(dups)} cặp ảnh/clip trùng trong cùng chương")
        bad.extend(dups)
    if r.get("clips"):
        bad.append(f"còn {len(r['clips'])} khoá `clips` chưa đổi thành media")
    print(f"{r['id']}: {minutes:.1f} phút, {len(media)} mốc media, {len(c)} hình/clip khác nhau, cold open {len(cold_clips)} clip/cine")
    return bad


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plans", nargs="+")
    args = parser.parse_args()
    rc = 0
    for a in args.plans:
        bad = check(Path(a))
        print("  ĐẠT" if not bad else "\n".join("  CHẶN: " + b for b in bad))
        rc |= bool(bad)
    sys.exit(rc)
