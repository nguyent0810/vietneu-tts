"""Tính danh sách thao tác (fit.json) để mọi cảnh nằm trong 2,5–9 giây theo timing thật. Chạy sau tts, trước html.

    python data/long/bao-thanh-thien/fit_calc.py      (đọc chNN.json đã sinh bởi gen_scenes.py, ghi fit.json)
Thao tác: drop_next  = bỏ cảnh ngắn, cảnh kế bắt đầu sớm hơn (nhận phần thời gian);
          drop_prev  = bỏ cảnh ngắn, cảnh trước kéo dài;
          shift      = thẻ chương quá ngắn: cảnh kế dời mốc sang chữ thứ hai của câu 1.
gen_scenes.py áp lại fit.json sau balance, nên chạy lại gen_scenes luôn ra cùng kết quả.
"""
import copy
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
sys.path.insert(0, str(ROOT / "motion" / "long"))
sys.path.insert(0, str(ROOT))
import build_long as b  # noqa: E402

LO, HI = 2.55, 9.0


def durations(ch, lines, dur):
    sc = b.plan(copy.deepcopy(ch), lines, dur)
    return [s["t1"] - s["t0"] for s in sc if s["type"] != "endcard"]


FIELD = {"org": "nodes", "ledger": "rows", "file": "rows", "map": "pins"}


def apply_sync(sc):
    """Mọi phần tử con (hàng, nút, ghim, hai nửa split) và số đếm cùng mốc với đầu cảnh: hiện ngay khi cảnh mở."""
    at0 = sc.get("at")
    if at0 is None:
        return
    if sc["type"] in FIELD:
        for p in sc[FIELD[sc["type"]]][:2]:
            p["at"] = at0
        if sc["type"] == "map":
            for r in sc.get("routes", []):
                r["at"] = at0
    elif sc["type"] == "split":
        sc["a"]["at"] = at0
        sc["b"]["at"] = at0
    elif sc["type"] == "counter":
        sc["countAt"] = at0


def main():
    spec, chs, od = b.load("bao-thanh-thien")
    ops = []
    keep = []
    ch_shift, ds_ok, chapter_done = {}, set(), set()
    for name, ch in chs:
        tj = json.loads((od / name / "timing.json").read_text(encoding="utf-8"))
        lines = b.word_lines(tj, od / name / "voice.wav")
        for _ in range(60):
            ds = durations(ch, lines, tj["duration"])
            sc = ch["scenes"]
            bad = [i for i, d in enumerate(ds) if d < (2.5 if sc[i]["type"] == "chapter" else LO) and not (sc[i]["type"] == "chapter" and name in chapter_done)]
            if not bad:
                break
            i = bad[0]
            d = ds[i]
            if sc[i]["type"] == "chapter":
                nxt = sc[i + 1]
                words = [w.strip(".,;:!?\"“”") for w in b.line_text(ch["lines"][1]).split()]
                k = min(len(words) - 1, ch_shift.get(name, 0) + 1)
                if ch_shift.get(name, 0) >= 4 or d >= 2.5:
                    ds_ok.add(name)
                ch_shift[name] = k
                nxt["at"] = [1, words[k]]
                ops = [o for o in ops if not (o["ch"] == name and o["op"] == "shift")]
                ops.append({"ch": name, "op": "shift", "word": words[k]})
                if d >= 2.5 or k >= 4:
                    chapter_done.add(name)
                continue
            plain = ("kinetic", "slam", "photo", "date", "print", "question", "broll", "sketch")
            nxt_ok = i + 1 < len(sc) and ds[i + 1] + d <= HI and sc[i + 1]["type"] != "chapter"
            prv_ok = i > 0 and ds[i - 1] + d <= HI
            if nxt_ok and sc[i + 1]["type"] in plain:
                mode = "drop_next"
            elif prv_ok:
                mode = "drop_prev"
            elif nxt_ok:
                mode = "drop_next"
            else:
                mode = None
            if mode == "drop_next":
                sc[i + 1]["at"] = sc[i].get("at") if sc[i].get("at") is not None else sc[i + 1].get("at")
                del sc[i]
                ops.append({"ch": name, "op": "drop_next", "idx": i})
            elif mode == "drop_prev":
                del sc[i]
                ops.append({"ch": name, "op": "drop_prev", "idx": i})
            else:
                print(name, "KHÔNG XỬ LÝ ĐƯỢC cảnh", i, sc[i]["type"], round(d, 2))
                break
        # A4: phần tử con thứ hai của thẻ (hàng ledger/file, nút org, ghim map, hai nửa split) phải hiện trong 1 s đầu: cho nó cùng mốc với phần tử đầu
        for _ in range(3):
            planned = [x for x in b.plan(copy.deepcopy(ch), lines, tj["duration"]) if x["type"] != "endcard"]
            msgs = b.late_first(planned, name)
            idxs = sorted({int(m.split()[2]) for m in msgs})
            if not idxs:
                break
            for i in idxs:
                apply_sync(ch["scenes"][i])
                ops.append({"ch": name, "op": "sync", "idx": i})
        ds = durations(ch, lines, tj["duration"])
        for m in b.late_first([x for x in b.plan(copy.deepcopy(ch), lines, tj["duration"]) if x["type"] != "endcard"], name):
            print("  !", m)
        keep.append((name, ch, lines, tj["duration"]))
        print(name, "còn", [(i, round(x, 2)) for i, x in enumerate(ds) if x < LO or x > HI])
    # clip phải dài hơn cảnh dùng nó (engine không lặp clip): đổi sang clip dài đủ, còn lượt dùng
    import balance
    bro = od / "broll"
    cdur = {}

    def clip_dur(v):
        if v not in cdur:
            cdur[v] = b.probe_dur(bro / f"{v}.mp4")
        return cdur[v]
    use = {}
    for _, ch, _, _ in keep:
        for sc in ch["scenes"]:
            if sc.get("vid"):
                use[sc["vid"]] = use.get(sc["vid"], 0) + 1
    for name, ch, lines, dur in keep:
        ds = durations(ch, lines, dur)
        for i, sc in enumerate(ch["scenes"]):
            v = sc.get("vid")
            if not v or i >= len(ds):
                continue
            need = ds[i] + sc.get("ms", 0) / 1000 + 0.6
            if clip_dur(v) >= need:
                continue
            g = balance._group_of(v, balance.VID_GROUPS)
            pool = [x for x in balance.VID_GROUPS.get(g, []) if x != v] + [x for x in balance.ALL_VIDS if x != v]
            pool = [x for x in pool if use.get(x, 0) < 3 and clip_dur(x) >= need and x not in ("19486650", "3967264", "5594429")]
            if not pool:
                print("  ! không có clip đủ dài cho", name, i, round(need, 1))
                continue
            new = min(pool, key=lambda x: (use.get(x, 0), pool.index(x)))
            use[v] -= 1
            use[new] = use.get(new, 0) + 1
            sc["vid"] = new
            ops.append({"ch": name, "op": "clip", "idx": i, "vid": new})
    (D / "fit.json").write_text(json.dumps(ops, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(ops), "thao tác")


if __name__ == "__main__":
    main()
