"""Giờ đăng short tự cải thiện cho BUD / FS: giờ nào yếu nhiều tuần liền thì đổi, giờ nào ổn thì giữ.

Người dùng 06/10/2026: "giờ nào thấy lượt view yếu trong nhiều tuần thì đổi, giờ nào ổn thì giữ, cần có hệ thống tự cải thiện".
Nguồn số liệu: bảng điểm của hf_brief (cửa sổ 7 ngày PT, hạng engagedViews TRONG CÙNG TUẦN, chỉ tuần sạch từ 05/10/2026),
nên hiệu ứng cấp kênh (một tuần cả kênh tụt) không bị đổ cho giờ đăng.

    slots.json (output/cl_staging/<kênh>/slots.json): {"slots": ["03:30", ...] (giờ UTC như plan), "history": [...]}
    python hf_slots.py show bud          # bộ giờ hiện tại + điểm từng giờ
    python hf_slots.py review bud        # đánh giá và (nếu đủ điều kiện) đổi MỘT giờ, ghi lịch sử

Builder short: `import hf_slots; SL = hf_slots.current("bud")` -> short thứ k trong ngày lấy SL[k].

Luật đổi (thận trọng, như V2: không tối ưu trên dữ liệu mỏng):
- Chỉ xét 4 tuần sạch gần nhất. Một giờ "yếu" khi: >= 6 video từ >= 3 tuần, hạng trung vị <= 0.35, và thấp hơn giờ
  tốt nhất của kênh >= 0.20; đồng thời ít nhất 3 tuần có trung vị tuần < 0.45 (yếu kéo dài, không phải một tuần xui).
- Mỗi lần review đổi TỐI ĐA MỘT giờ (giờ yếu nhất). Giờ vừa đổi được giữ ít nhất 3 tuần (đủ số liệu mới).
- Giờ thay thế: giờ đã có số liệu tốt trên kênh (>= 6 video, hạng trung vị >= 0.55, chưa là giờ của mình) -> ưu tiên;
  không có thì THỬ một giờ chưa thử trong danh sách khám phá. Mọi giờ cách nhau >= 90 phút.
"""
from __future__ import annotations

import json
import statistics as st
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT = {"bud": ["03:30", "08:00", "12:30", "16:20", "23:00"], "fs": ["04:30", "08:00", "12:00", "15:00"]}
EXPLORE_VN = ["07:00", "09:00", "12:00", "17:30", "20:30", "21:30", "22:30"]   # giờ VN để thử khi chưa có giờ tốt sẵn
WEEKS, MIN_N, MIN_WEEKS, WEAK, GAP, GOOD, COOLDOWN_W = 4, 6, 3, .35, .20, .55, 3


def _path(ch: str) -> Path:
    return ROOT / "output" / "cl_staging" / ch / "slots.json"


def load(ch: str) -> dict:
    p = _path(ch)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"slots": list(DEFAULT[ch]), "history": []}


def save(ch: str, d: dict) -> None:
    _path(ch).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def current(ch: str) -> list[str]:
    return list(load(ch)["slots"])


def utc_to_vn(hhmm: str) -> str:
    h, m = map(int, hhmm.split(":"))
    return f"{(h + 7) % 24:02d}:{m:02d}"


def vn_to_utc(hhmm: str) -> str:
    h, m = map(int, hhmm.split(":"))
    return f"{(h - 7) % 24:02d}:{m:02d}"


def _mins(hhmm: str) -> int:
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def _apart(a: str, b: str) -> int:
    d = abs(_mins(a) - _mins(b))
    return min(d, 1440 - d)


def hour_stats(rows: list[dict]) -> dict[str, dict]:
    """rows: short đã xếp hạng (hf_brief.score_shorts, chỉ tuần sạch). Khoá = giờ VN 'HH' -> thống kê."""
    by: dict[str, list[dict]] = {}
    for x in rows:
        by.setdefault(x["vn"][11:13], []).append(x)
    out = {}
    for h, xs in by.items():
        weeks: dict[str, list[float]] = {}
        for x in xs:
            weeks.setdefault(x["week"], []).append(x["rank"])
        out[h] = {"n": len(xs), "weeks": len(weeks), "med": st.median(x["rank"] for x in xs),
                  "weak_weeks": sum(1 for w in weeks.values() if st.median(w) < .45),
                  "views": st.median(x["views"] for x in xs)}
    return out


def decide(slots: list[str], stats: dict[str, dict], history: list[dict], today: date) -> dict | None:
    """Đề xuất đổi MỘT giờ (hoặc None). slots: giờ UTC; stats theo giờ VN."""
    if not stats:
        return None
    if history and (today - date.fromisoformat(history[-1]["date"])).days < 7:   # tối đa một lần đổi mỗi tuần
        return None
    best = max(v["med"] for v in stats.values() if v["n"] >= MIN_N) if any(v["n"] >= MIN_N for v in stats.values()) else None
    recent = {h["to"] for h in history if (today - date.fromisoformat(h["date"])).days < 7 * COOLDOWN_W}
    weak = []
    for s in slots:
        if s in recent:
            continue
        v = stats.get(utc_to_vn(s)[:2])
        if (v and best is not None and v["n"] >= MIN_N and v["weeks"] >= MIN_WEEKS and v["med"] <= WEAK
                and best - v["med"] >= GAP and v["weak_weeks"] >= 3):
            weak.append((v["med"], s, v))
    if not weak:
        return None
    _, out_slot, v = min(weak)
    others = [s for s in slots if s != out_slot]
    ok = lambda cand: all(_apart(cand, o) >= 90 for o in others)
    mine_h = {utc_to_vn(s)[:2] for s in slots}
    good = sorted(((st_["med"], h) for h, st_ in stats.items() if st_["n"] >= MIN_N and st_["med"] >= GOOD and h not in mine_h),
                  reverse=True)
    for med, h in good:
        cand = vn_to_utc(f"{h}:00")
        if ok(cand):
            return {"from": out_slot, "to": cand, "why": f"giờ {utc_to_vn(out_slot)} VN yếu ({v['med']:.2f}, {v['n']} video/{v['weeks']} tuần); "
                                                         f"giờ {h}:xx VN đã tốt trên kênh ({med:.2f})", "kind": "dùng giờ tốt"}
    tried = {h["to"] for h in history}
    for vn in EXPLORE_VN:
        cand = vn_to_utc(vn)
        if cand not in tried and cand not in slots and ok(cand):
            return {"from": out_slot, "to": cand, "why": f"giờ {utc_to_vn(out_slot)} VN yếu ({v['med']:.2f}, {v['n']} video/{v['weeks']} tuần); "
                                                         f"thử giờ mới {vn} VN", "kind": "thử giờ mới"}
    return None


def review(ch: str, rows: list[dict] | None = None, apply: bool = True, today: date | None = None) -> list[str]:
    """Chạy từ hf_brief hằng tuần. Trả các dòng markdown cho bản tóm tắt."""
    today = today or date.today()
    if rows is None:
        import hf_brief  # noqa: PLC0415
        m = json.loads((hf_brief.CACHE / f"metrics_{ch}.json").read_text(encoding="utf-8"))
        rows, _ = hf_brief.score_shorts(m, hf_brief.our_rows(ch))
    clean = [x for x in rows if x["clean"]]
    weeks = sorted({x["week"] for x in clean})[-WEEKS:]
    stats = hour_stats([x for x in clean if x["week"] in weeks])
    d = load(ch)
    lines = [f"Bộ giờ hiện tại (VN): {', '.join(utc_to_vn(s) for s in d['slots'])} · dữ liệu {len(weeks)} tuần sạch gần nhất."]
    for s in d["slots"]:
        v = stats.get(utc_to_vn(s)[:2])
        lines.append(f"- {utc_to_vn(s)} VN: " + (f"hạng trung vị {v['med']:.2f}, {v['n']} video/{v['weeks']} tuần, view trung vị {v['views']:.0f}"
                                                 if v else "chưa đủ số liệu"))
    ch_ = decide(d["slots"], stats, d["history"], today)
    if ch_ and apply:
        d["slots"] = sorted([ch_["to"] if s == ch_["from"] else s for s in d["slots"]], key=lambda s: _mins(utc_to_vn(s)))
        d["history"].append({"date": today.isoformat(), **ch_})
        save(ch, d)
        lines.append(f"**ĐỔI GIỜ**: {utc_to_vn(ch_['from'])} → {utc_to_vn(ch_['to'])} VN ({ch_['kind']}). Lý do: {ch_['why']}. "
                     "Áp dụng cho các lô short build từ giờ; lịch đã hẹn giữ nguyên.")
    elif not ch_:
        lines.append("Giữ nguyên: chưa giờ nào yếu đủ lâu (cần >= 3 tuần sạch, >= 6 video, trung vị <= 0.35).")
    return lines


def main() -> int:
    cmd, ch = (sys.argv[1:3] + ["show", "bud"])[:2]
    if cmd == "review":
        print("\n".join(review(ch)))
    else:
        d = load(ch)
        print(ch, [utc_to_vn(s) for s in d["slots"]], "lịch sử:", d["history"][-3:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
