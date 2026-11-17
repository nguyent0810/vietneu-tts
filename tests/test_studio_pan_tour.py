"""pan_tour: các tween camera nối đuôi, không chồng giờ (lỗi Quét nhà NIj0goKjNtc, 17/11/2026).

Hai tween cùng giành `scale` của camera (tween mở cảnh 1,2 s + cú máy tới điểm dừng đầu ở giây 0,4)
làm ảnh trượt mà không phóng rồi giật một khung đúng lúc tween mở cảnh hết. Test chạy thật tour.js
trong Node với timeline giả ghi lại mọi tween.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

TOUR = Path(__file__).resolve().parents[1] / "hyperframes_short" / "studio" / "devices" / "tour.js"

HARNESS = r"""
const fs = require("fs");
let DEV = null;
global.HFS = { device: (name, def) => { DEV = def; } };
eval(fs.readFileSync(process.argv[1], "utf8"));
const cases = JSON.parse(process.argv[2]);
const node = () => ({ style: {}, setAttribute() {}, appendChild() {} });
const out = cases.map(({ t0, dur, stops }) => {
  const tw = [], revealed = new Set();
  const tl = {
    set: (target, v, at) => tw.push({ target, kind: "set", at, dur: 0, props: Object.keys(v) }),
    to: (target, v, at) => tw.push({ target, kind: "to", at, dur: v.duration, props: Object.keys(v).filter(k => !["duration", "ease"].includes(k)) }),
    fromTo: (target, a, v, at) => tw.push({ target, kind: "fromTo", at, dur: v.duration, props: Object.keys(a) }),
  };
  const c = { tl, dur, L: { wide: false }, S: x => x, E: { entry: "e", move: "m" },
    el: node, sv: node, esc: x => x, rng: () => () => .5,
    t: (x, d) => (typeof x === "number" ? x : d), draw() {}, reveal(n) { revealed.add(n); } };
  const s = { w: 1080, h: 1920, stops };
  const h = DEV.build(c, s, node(), 0);
  DEV.enter(c, h, t0, s);
  const cam = tw.filter(x => x.target === h.cam && x.kind !== "set").map(x => [x.at, x.at + x.dur, x.props]);
  const notes = h.stops.filter(p => p.note).map(p => ({
    revealed: revealed.has(p.note),
    hidden: tw.some(x => x.target === p.note && x.kind === "set" && x.at === 0 && x.props.includes("autoAlpha")) }));
  return { cam, notes };
});
console.log(JSON.stringify(out));
"""


def _run(cases):
    if not shutil.which("node"):
        pytest.skip("không có node")
    res = subprocess.run(["node", "-e", HARNESS, str(TOUR), json.dumps(cases)],
                         capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def _assert_no_overlap(tweens):
    tweens = sorted(tweens)
    for (a0, a1, pa), (b0, b1, pb) in zip(tweens, tweens[1:]):
        if set(pa) & set(pb):
            assert a1 <= b0 + 1e-6, f"tween camera chồng giờ: {a0:.2f}-{a1:.2f} {pa} và {b0:.2f}-{b1:.2f} {pb}"


@pytest.mark.parametrize("case", [
    # Quét nhà dòng 0: điểm dừng đầu ngay chữ đầu câu (giây 0) -> trước đây chồng tween mở cảnh
    {"t0": 0.0, "dur": 5.6, "stops": [{"x": .5, "y": .5, "z": 1.65, "at": 0.0}, {"x": .6, "y": .52, "z": 2.3, "at": 4.6}]},
    # Quét nhà dòng 2: ba điểm dừng, cảnh không bắt đầu ở 0
    {"t0": 9.27, "dur": 14.9, "stops": [{"x": .5, "y": .5, "z": 1.65, "at": 9.39},
                                        {"x": .6, "y": .3, "z": 2.1, "at": 11.9, "note": "Thủy thần", "r": 170},
                                        {"x": .55, "y": .56, "z": 2.5, "at": 13.6, "note": "Như Nguyệt", "r": 130}]},
    # hai điểm dừng sát nhau (0,3 s) và mốc lùi về trước điểm trước
    {"t0": 2.0, "dur": 9.0, "stops": [{"x": .3, "y": .3, "z": 2, "at": 3.0, "note": "A", "r": 90}, {"x": .7, "y": .7, "z": 2, "at": 3.3, "note": "B", "r": 90},
                                      {"x": .5, "y": .5, "z": 1.5, "at": 3.1}]},
    # điểm dừng đầu muộn: tween mở cảnh vẫn chạy đủ, không chồng
    {"t0": 0.0, "dur": 8.0, "stops": [{"x": .5, "y": .5, "z": 1.8, "at": 3.0}]},
    # không có điểm dừng
    {"t0": 0.0, "dur": 4.0, "stops": []},
])
def test_camera_tweens_never_overlap(case):
    (res,) = _run([case])
    tweens = res["cam"]
    _assert_no_overlap(tweens)
    for n in res["notes"]:   # nhãn dựng sẵn hiện từ đầu: hoặc reveal đúng mốc, hoặc tắt hẳn
        assert n["revealed"] or n["hidden"]
    for a0, a1, _ in tweens:
        assert a0 >= case["t0"] - 1e-6


def test_late_first_stop_keeps_entry_and_early_drops_it():
    late, early = (r["cam"] for r in _run([
        {"t0": 0.0, "dur": 8.0, "stops": [{"x": .5, "y": .5, "z": 1.8, "at": 3.0}]},
        {"t0": 0.0, "dur": 5.6, "stops": [{"x": .5, "y": .5, "z": 1.65, "at": 0.0}]},
    ]))
    assert any(abs(a0) < 1e-6 and abs((a1 - a0) - 1.2) < 1e-6 for a0, a1, _ in late)   # mở cảnh đủ 1,2 s
    first_move = min(a0 for a0, _, p in early if "x" in p)
    assert all(a1 <= first_move + 1e-6 for a0, a1, p in early if a0 < first_move)        # mở cảnh (nếu có) hết trước cú máy
