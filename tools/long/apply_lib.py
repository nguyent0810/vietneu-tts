"""Dùng chung cho các tập Long ngắn tháng 11: ghi media/visual/metadata vào plan. Chạy từ gốc repo."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

A = "output/cl_staging/long/research/ai_media/"
L, F, N = A + "fs_vt_t11/", A + "fs_2027_12tuoi/", A + "t11_new/"
HAC = {"bad": [3]}
PANO = A + "pano/"


def pano(path: str, lines: list[int], direction: str = "ltr", grade: str = "cold") -> dict:
    """Ảnh rộng 3:1 quét ngang (028): mỗi câu một điểm dừng = một nhát cắt với cổng nhịp."""
    n = len(lines)
    xs = [round(i / (n - 1), 3) for i in range(n)] if n > 1 else [0.5]
    if direction == "rtl":
        xs = xs[::-1]
    return {"kind": "local", "path": PANO + path, "label": False, "layout": "full",
            "pan": {"dir": direction, "stops": [{"line": ln, "x": x} for ln, x in zip(lines, xs)],
                    "ease": "inOut", "depth": True, "fx": ["mist_drift"], "grade": grade}}


def _line_map(old: list, new: list) -> dict:
    """Số câu cũ -> số câu mới, khớp đúng văn bản theo thứ tự (câu đã sửa/xoá thì mất)."""
    out, j = {}, 0
    for i, t in enumerate(old, 1):
        for k in range(j, len(new)):
            if new[k] == t:
                out[i], j = k + 1, k + 1
                break
    return out


def _remap_ints(obj, m):
    if isinstance(obj, dict):
        return {k: (m.get(v, v) if k in ("at", "until") and isinstance(v, int) else _remap_ints(v, m)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_remap_ints(x, m) for x in obj]
    return obj


def apply(plan_id: str, img: dict, vis: dict, meta: dict, extra_img: dict | None = None) -> None:
    p = ROOT / f"output/cl_staging/long/plan_{plan_id}.json"
    rows = json.loads(p.read_text(encoding="utf-8"))
    r = rows[0]
    olds = json.loads((ROOT / "output/cl_staging/long/research/t11_12tuoi/old_scripts.json").read_text(encoding="utf-8"))
    key = plan_id.rsplit("_", 1)[-1]
    if key in olds and olds[key] != r["script"]:
        m = _line_map(olds[key], r["script"])
        lost = sorted(set(img) | set(vis) - set(m))
        img = {m[k]: v for k, v in img.items() if k in m}
        vis = {m[k]: _remap_ints(v, m) for k, v in vis.items() if k in m}
        print("  remap: mất mốc", [k for k in lost if k not in m])
    img = {**img, **(extra_img or {})}  # ảnh cho câu mới, theo số câu MỚI
    clash = sorted(k for k in set(img) & set(vis) if not vis[k].get("overlay"))
    if clash:
        raise SystemExit(f"câu vừa có ảnh vừa có visual: {clash}")
    r["media"] = {str(k): (v if isinstance(v, dict) else {"kind": "local", "path": v}) for k, v in img.items()}
    r["visuals"] = {str(k): v for k, v in vis.items()}
    heads = [i for i, l in enumerate(r["script"], 1) if l.startswith("**") and l.endswith("**") and l.count("**") == 2]
    r["ambience"] = [{"chapter": c, "kind": "wind", "gain_db": 0} for c in range(0, len(heads) + 1)]
    r.pop("kinetic_suggest", None)
    for v in r["visuals"].values():  # kinetic opt-in (#086): thẻ số dùng preset number_impact
        if v.get("type") == "stat":
            v.setdefault("preset", "number_impact")
    import hf_style_suggest as HSS  # cảnh style #258 sau khi ảnh/visual tay đã đặt
    HSS.apply_suggestions(r, adopt=True)
    r.update(meta)
    # Preset âm C chọn nhạc theo mood (hf_sound.pick_mood_track), bỏ qua `bgm`/sổ nhạc: ghim bằng sound.mood_segments.
    segs = json.loads((ROOT / "output/cl_staging/long/research/t11_12tuoi/bgm_segments.json").read_text(encoding="utf-8"))
    key = plan_id.rsplit("_", 1)[-1]
    if key in segs:
        r.setdefault("sound", {})["mood_segments"] = segs[key]
        r["sound"].pop("bgm_rotate", None)
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    missing = sorted({(v["path"] if isinstance(v, dict) else v) for v in img.values()
                      if not Path(v["path"] if isinstance(v, dict) else v).exists()})
    n = len(r["script"])
    covered = set(img) | {k for k in vis} | set(heads)
    for k, v in vis.items():
        covered |= set(range(k, int(v.get("until", k)) + 1))
    print(plan_id, "câu", n, "heads", heads, "media", len(img), "visual", len(vis), "thiếu ảnh", len(missing))
    print("  câu trơn (không ảnh/visual/thẻ):", [i for i in range(1, n + 1) if i not in covered])
    for m in missing:
        print("  thiếu", m)
