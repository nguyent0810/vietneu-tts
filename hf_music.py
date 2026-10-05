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
    python hf_music.py shorts bud         # bài của các short gần nhất

SHORT (từ lịch SHORT_FROM): trước đây cả 240 short BUD dùng Meditation Impromptu 01, cả 113 short FS dùng Asian Drums.
Giờ mỗi short một bài (ít dùng nhất trong 8 short gần nhất cùng kênh, sổ output/cl_staging/<kênh>/bgm_shorts.json).
Mỗi bài có một bản cắt riêng cho short (chunks_cache/bgm_short/): bỏ đoạn mở nhỏ, đưa về cùng độ to với bài chuẩn của
kênh -> hệ số nhạc short đã duyệt (bud .33, fs .2) giữ nguyên.

File nhạc: bgm/*.mp3 (gitignore; tải từ incompetech.com theo bgm/LICENSE.txt). Sổ: output/cl_staging/long/bgm_ledger.json.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

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

SHORT_FROM = "2026-11-18"   # short đã hẹn tới 15/11 (BUD), 17/11 (FS) giữ bài cũ, không render lại
SHORT_REF = {"bud": ("meditation_impromptu_01.mp3", .33), "fs": ("asian_drums.mp3", .2)}
SHORT_POOL = {"bud": [f for f, _ in CATALOG["bud"]], "fs": [f for f, _ in CATALOG["fs"]] + ["asian_drums.mp3"]}
SHORT_WINDOW = 8
SHORT_DIR = ROOT / "chunks_cache" / "bgm_short"


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


def _lufs(path: Path, ss: float = 0, t: float = 40) -> float:
    res = subprocess.run(["ffmpeg", "-nostats", "-ss", f"{ss:.1f}", "-t", f"{t:.0f}", "-i", str(path), "-af", "ebur128",
                          "-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?\d+(?:\.\d+)?) LUFS", res.stderr)[-1])


def _body_start(path: Path) -> float:
    """Giây đầu tiên bài đạt độ to thân bài (bỏ đoạn mở nhỏ/fade-in), tối đa 30 giây."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-t", "150", "-i", str(path), "-ac", "1", "-ar", "8000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype="float32")
    db = 20 * np.log10(np.sqrt((a[: len(a) // 8000 * 8000].reshape(-1, 8000) ** 2).mean(axis=1)) + 1e-9)
    ok = np.where(db >= np.median(db) - 6)[0]
    return float(min(ok[0], 30)) if len(ok) else 0.0


def short_bed(name: str, series: str, root: Path = ROOT) -> Path:
    """Bản cắt cho short: từ thân bài, cùng độ to với bài chuẩn của kênh (tạo một lần, cache). Giữ tên file gốc để ghi nguồn."""
    out = SHORT_DIR / series / name
    if out.exists():
        return out
    src, ref = root / "bgm" / name, root / "bgm" / SHORT_REF[series][0]
    ss, rs = _body_start(src), _body_start(ref)
    db = _lufs(ref, rs) - _lufs(src, ss)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.1f}", "-t", "240", "-i", str(src), "-af",
                    f"volume={db:.2f}dB,afade=t=in:d=0.4,aresample=44100", "-c:a", "libmp3lame", "-b:a", "192k", str(out)], check=True)
    return out


def short_pick(row: dict, root: Path = ROOT) -> tuple[str, float]:
    """(đường dẫn bản cắt, hệ số) cho một short BUD/FS lịch >= SHORT_FROM; chọn một lần rồi giữ trong sổ của kênh."""
    series = row["series"]
    led_path = root / "output" / "cl_staging" / series / "bgm_shorts.json"
    led = json.loads(led_path.read_text(encoding="utf-8")) if led_path.exists() else {}
    if row["id"] not in led:
        key = (row["day"], row.get("slot", ""))
        near = sorted(((abs(_day(v["day"]) - _day(key[0])), v["day"], v["slot"], v["file"]) for k, v in led.items()
                       if k != row["id"]))[:SHORT_WINDOW]
        uses = {}
        for *_, f in near:
            uses[f] = uses.get(f, 0) + 1
        have = [f for f in SHORT_POOL[series] if (root / "bgm" / f).exists()]
        h = lambda f: hashlib.sha1(f"{row['id']}|{f}".encode()).hexdigest()
        led[row["id"]] = {"day": key[0], "slot": key[1], "file": min(have, key=lambda f: (uses.get(f, 0), h(f)))}
        led_path.write_text(json.dumps(led, ensure_ascii=False, indent=0), encoding="utf-8")
    bed = short_bed(led[row["id"]]["file"], series, root)
    return str(bed.relative_to(root)), SHORT_REF[series][1]


def main() -> int:
    cmd, *rest = sys.argv[1:] or ["help"]
    if cmd == "library":
        d = ledger()
        for series, rows in CATALOG.items():
            print(series)
            for f, t in rows:
                n = sum(f in (v.get("used") or []) for v in d.values())
                print(f"  {n:2d} video  {'✓' if (ROOT / 'bgm' / f).exists() else 'thiếu':5s} {t}")
    elif cmd == "shorts":
        p = ROOT / "output" / "cl_staging" / rest[0] / "bgm_shorts.json"
        led = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        for k, v in sorted(led.items(), key=lambda kv: (kv[1]["day"], kv[1]["slot"]))[-20:]:
            print(f"  {v['day']} {v['slot']} {k:10s} {title(v['file'])}")
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
