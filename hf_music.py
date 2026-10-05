"""Nhạc nền video dài BUD / FS: kho bài theo kênh + sổ bài đã dùng, để mỗi video nghe khác các video gần nó.

Ý từ motion/variety.py của Youtube_Creator_V2 (04/10/2026). Chính sách Spam của YouTube nêu đích danh ví dụ kênh dùng
"the exact same background music" trên nhiều video; trước ngày này mọi Long BUD chạy đúng 3 bản Meditation Impromptu,
mọi Long FS đúng 3 bản (Deliberate/Thinking/Comfortable Mystery 4).

- Mỗi video được một THỨ TỰ bài (pool) chọn một lần rồi ghi sổ -> render/trộn lại vẫn ra đúng bài cũ, ghi nguồn không lệch.
- Chọn bài ít dùng nhất trong 3 video cùng kênh gần ngày đăng nhất (hai phía), bài cũ trước 04/10 bị coi như đã dùng nhiều.
- hf_foley.music_bed phát lần lượt theo pool, chỉ đổi bài ở thẻ chương; bài thực sự vang lên ghi vào sổ (`used`).
- audit(): bộ bài đã dùng trùng > 35% (Jaccard) với một video gần đó -> cảnh báo.

    python hf_music.py library            # kho bài + số video đã dùng
    python hf_music.py audit L_bud_19     # so với 3 video gần nhất cùng kênh

File nhạc: bgm/*.mp3 (gitignore; tải từ incompetech.com theo bgm/LICENSE.txt). Sổ: output/cl_staging/long/bgm_ledger.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "output" / "cl_staging" / "long" / "bgm_ledger.json"
WINDOW = 3
MAX_OVERLAP = .35
N_PICK = 4

# (file trong bgm/, tên gốc để ghi nguồn). Tất cả Kevin MacLeod, incompetech.com, CC BY 4.0.
# Lọc theo độ to: RMS 5 giây dao động <= ~14 dB như bộ Meditation đã duyệt (10-12). Loại 04/10: Ghost Story (21),
# On the Passing of Time (19), Moonstone (17), Clear Waters (16) -- có đoạn dâng to đè giọng.
CATALOG = {
    "bud": [("white_lotus.mp3", "White Lotus"), ("peace_of_mind.mp3", "Peace of Mind"), ("garden_music.mp3", "Garden Music"),
            ("wood_and_metal_and_water.mp3", "Wood and Metal and Water"), ("that_zen_moment.mp3", "That Zen Moment"),
            ("ripples.mp3", "Ripples"), ("starry.mp3", "Starry"),
            ("parting_of_the_ways_part_1.mp3", "Parting of the Ways - Part 1"),
            ("meditation_impromptu_01.mp3", "Meditation Impromptu 01"), ("meditation_impromptu_02.mp3", "Meditation Impromptu 02"),
            ("meditation_impromptu_03.mp3", "Meditation Impromptu 03")],
    "fs": [("eastern_thought.mp3", "Eastern Thought"), ("ishikari_lore.mp3", "Ishikari Lore"), ("senbazuru.mp3", "Senbazuru"),
           ("eastminster.mp3", "Eastminster"), ("frozen_star.mp3", "Frozen Star"), ("clean_soul.mp3", "Clean Soul"),
           ("shores_of_avalon.mp3", "Shores of Avalon"),
           ("deliberate_thought.mp3", "Deliberate Thought"), ("thinking_music.mp3", "Thinking Music"),
           ("comfortable_mystery_4.mp3", "Comfortable Mystery 4")],
}
# Bài mọi Long trước 04/10/2026 đều dùng: coi như đã có mặt trong cả cửa sổ so sánh.
LEGACY = {"meditation_impromptu_01.mp3", "meditation_impromptu_02.mp3", "meditation_impromptu_03.mp3",
          "deliberate_thought.mp3", "thinking_music.mp3", "comfortable_mystery_4.mp3"}
TITLES = {f: t for rows in CATALOG.values() for f, t in rows} | {"asian_drums.mp3": "Asian Drums"}


def title(name: str) -> str:
    """Tên gốc để ghi nguồn; KeyError = bài chưa có trong danh mục -> không đăng thiếu ghi nguồn."""
    return TITLES[Path(name).name]


def credit(names: list[str]) -> str:
    tracks = ", ".join(f'"{title(n)}"' for n in dict.fromkeys(Path(n).name for n in names))
    return (f"Nhạc nền: {tracks} by Kevin MacLeod (incompetech.com), "
            "licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/)")


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}


def _save(d: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def _day(s: str) -> int:
    y, m, d = (int(x) for x in s[:10].split("-"))
    return y * 372 + m * 31 + d


def neighbors(d: dict, rid: str, series: str, day: str, n: int = WINDOW) -> list[str]:
    """n video cùng kênh gần ngày đăng nhất (cả trước lẫn sau): người xem lướt kênh theo cả hai chiều."""
    rows = [(abs(_day(v["day"]) - _day(day)), k) for k, v in d.items() if k != rid and v["series"] == series]
    return [k for _, k in sorted(rows)[:n]]


def pool_for(row: dict, root: Path = ROOT) -> list[str]:
    """Thứ tự bài ("bgm/x.mp3") cho video dài `row`; chọn một lần rồi giữ trong sổ."""
    rid, series = row["id"], row["series"]
    d = ledger()
    if rid in d and d[rid].get("pool"):
        return d[rid]["pool"]
    near = neighbors(d, rid, series, row["day"])
    uses = {}
    for k in near:
        for f in d[k].get("used") or d[k].get("pool") or []:
            uses[Path(f).name] = uses.get(Path(f).name, 0) + 1
    have = [f for f, _ in CATALOG[series] if (root / "bgm" / f).exists()]
    if not have:
        raise SystemExit(f"hf_music: chưa có file nhạc nào của kênh {series} trong bgm/")
    h = lambda f: hashlib.sha1(f"{rid}|{f}".encode()).hexdigest()
    pick = sorted(have, key=lambda f: (uses.get(f, 0) + (WINDOW if f in LEGACY else 0), h(f)))[:N_PICK]
    d[rid] = {"series": series, "day": row["day"], "pool": [f"bgm/{f}" for f in pick], "used": []}
    _save(d)
    return d[rid]["pool"]


def record(rid: str, used: list[str]) -> None:
    d = ledger()
    if rid in d:
        d[rid]["used"] = list(dict.fromkeys(Path(u).name for u in used))
        _save(d)


def audit(rid: str) -> list[str]:
    d = ledger()
    me = d.get(rid)
    if not me or not me.get("used"):
        return []
    a, out = set(me["used"]), []
    for k in neighbors(d, rid, me["series"], me["day"]):
        b = set(d[k].get("used") or [])
        if b and len(a & b) / len(a | b) > MAX_OVERLAP:
            out.append(f"nhạc nền trùng {len(a & b) / len(a | b):.0%} với {k} ({', '.join(sorted(a & b))})")
    return out


def main() -> int:
    cmd, *rest = sys.argv[1:] or ["help"]
    if cmd == "library":
        d = ledger()
        for series, rows in CATALOG.items():
            print(series)
            for f, t in rows:
                n = sum(f in (v.get("used") or []) for v in d.values())
                print(f"  {n:2d} video  {'✓' if (ROOT / 'bgm' / f).exists() else 'thiếu':5s} {t}")
    elif cmd == "audit":
        p = audit(rest[0])
        print(ledger().get(rest[0]))
        for x in p:
            print("  !", x)
        return 1 if p else 0
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
