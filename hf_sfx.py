"""Âm thanh bám cảnh cho short/long (Phase D) -- tổng hợp bằng numpy, không file ngoài.

Ý tưởng từ Youtube_Creator_V2 (motion/stier/sfx.py): tiếng động đặt ĐÚNG các mốc
mà hình chuyển động (chữ bật, số chạm đích, mục danh sách sáng, vòng khoanh đỏ),
nên tai "thấy" nhịp cắt. Khác V2: bảng âm của kênh Phật giáo / Phong Thuỷ phải
mềm -- chuông, chuông xoay, mõ, gió, cồng -- không có tiếng đập / còi / song sắt
của phim vụ án. Câu hỏi lặng (`silence`) thì KHÔNG có tiếng nào, nhạc nền tắt hẳn.

Mốc lấy từ chính `lines` bridge đã dựng (words + visual + media), cùng cách tính
`when()` của longform.js -- một chỗ tính giờ, hai nơi dùng.
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, lfilter

SR = 48000


def _env(n: int, a: float, r: float) -> np.ndarray:
    t = np.arange(n) / SR
    return np.minimum(1.0, t / max(a, 1e-4)) * np.exp(-t / r)


class Palette:
    """Nguyên liệu âm. Mọi thứ tất định theo seed (render lại ra y hệt)."""

    def __init__(self, seed: int):
        self.rng = np.random.default_rng(seed)

    def _partials(self, f0, ratios, amps, decays, dur, detune=0.0):
        n = int(dur * SR)
        t = np.arange(n) / SR
        s = np.zeros(n)
        for r, a, d in zip(ratios, amps, decays):
            f = f0 * r
            s += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
            if detune:  # hai nhánh lệch nhẹ -> tiếng "ngân" có nhịp phách như chuông thật
                s += a * 0.6 * np.sin(2 * np.pi * (f + detune) * t) * np.exp(-t / d)
        return s * _env(n, 0.002, 1e9)

    def bell(self, f0=523.0, dur=3.2):          # chuông nhỏ: chữ khoá bật, minh hoạ
        return self._partials(f0, [1, 2.76, 5.40, 8.93], [1, .45, .22, .1], [2.2, 1.0, .5, .25], dur, 0.9)

    def bowl(self, f0=196.0, dur=5.0):          # chuông xoay: mở/kết, trích kinh
        return self._partials(f0, [1, 2.71, 5.15], [1, .5, .2], [3.8, 1.8, .8], dur, 0.7) * _env(int(dur * SR), .03, 1e9)

    def chime(self, f0=1318.0, dur=1.6):        # leng keng: bước sơ đồ, số chạm đích
        return self._partials(f0, [1, 2.0, 3.01], [1, .35, .15], [.9, .4, .2], dur, 1.5)

    def gong(self, f0=98.0, dur=3.6):           # cồng: chữ khoá kênh Phong Thuỷ
        s = self._partials(f0, [1, 1.48, 2.1, 2.92], [1, .6, .4, .2], [2.6, 1.6, 1.0, .6], dur, 0.5)
        return s * _env(int(dur * SR), .015, 1e9)

    def woodblock(self, f0=820.0):              # mõ: mục danh sách, mốc thời gian
        n = int(0.25 * SR)
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * f0 * t) * np.exp(-t / .045) + .5 * np.sin(2 * np.pi * f0 * 1.52 * t) * np.exp(-t / .02)
        b, a = butter(2, [1500 / (SR / 2), 6000 / (SR / 2)], "band")
        click = lfilter(b, a, self.rng.standard_normal(n)) * np.exp(-t / .004)
        return s + .4 * click

    def tick(self):                              # tích tắc đồng hồ
        n = int(0.06 * SR)
        t = np.arange(n) / SR
        b, a = butter(2, 2500 / (SR / 2), "high")
        return lfilter(b, a, self.rng.standard_normal(n)) * np.exp(-t / .006) * .8 + np.sin(2 * np.pi * 3200 * t) * np.exp(-t / .01) * .3

    def _noise(self, dur, lo, hi):
        n = int(dur * SR)
        b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band")
        return lfilter(b, a, self.rng.standard_normal(n)), n

    def whoosh(self, dur=0.7):                   # gió nhẹ: chuyển cảnh, ảnh vào
        s, n = self._noise(dur, 300, 2400)
        t = np.arange(n) / SR
        return s * np.sin(np.pi * t / dur) ** 2 * .9

    def brush(self):                             # nét bút: vòng khoanh đỏ, gạch chân
        s, n = self._noise(.24, 1800, 7000)
        t = np.arange(n) / SR
        return s * np.sin(np.pi * t / .24) * .7

    def paper(self):                             # lật giấy: thẻ trích dẫn
        s, n = self._noise(.35, 900, 5000)
        t = np.arange(n) / SR
        crackle = (self.rng.random(n) > .985) * self.rng.standard_normal(n) * .6
        return (s * .5 + crackle) * np.sin(np.pi * t / .35)


class Mix:
    def __init__(self, dur: float, seed: int):
        self.N = int(dur * SR) + SR
        self.bus = np.zeros((self.N, 2))
        self.p = Palette(seed)

    def put(self, t: float, sig: np.ndarray, gain: float = 1.0, pan: float = 0.0):
        i = int(max(0.0, t) * SR)
        if i >= self.N:
            return
        sig = sig[: self.N - i] * gain
        self.bus[i:i + len(sig), 0] += sig * (1 - max(0.0, pan))
        self.bus[i:i + len(sig), 1] += sig * (1 + min(0.0, pan))

    def write(self, path: Path, dur: float, peak: float = 0.3):
        x = self.bus[: int(dur * SR)]
        m = np.abs(x).max()
        if m > 0:
            x = x / m * peak
        pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
        with wave.open(str(path), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())


def _clean(s: str) -> str:
    return (s or "").replace("**", "").strip().lower()


def when(lines: list[dict], step: dict | None, fallback: float) -> float:
    """Cùng luật với when() trong longform.js: đầu câu `at` (+0.3), hoặc lúc đọc `word`."""
    if not step or not step.get("at"):
        return fallback
    L = lines[int(step["at"]) - 1]
    key = (step.get("word") or "").lower()
    if key:
        for w in L.get("words") or []:
            if key in _clean(w.get("w")):
                return float(w["t"])
    return float(L["start"]) + float(step.get("offset", 0.3))


def events(lines: list[dict], series: str, silence: set[int]) -> list[tuple[float, str, float]]:
    """[(giây, âm, gain)] từ lines đã có visual/media. Câu trong `silence`: không tiếng nào."""
    fs = series == "fs"
    ev: list[tuple[float, str, float]] = []
    for i, ln in enumerate(lines):
        sid, t0 = ln["sentence_id"], float(ln["start"])
        if sid in silence:
            continue
        v = ln.get("visual") or {}
        ty = v.get("type")
        if i and not ln.get("visual_cont") and not ln.get("media_cont"):
            ev.append((t0 - .35, "whoosh", .35))                       # chuyển cảnh
        if ty == "word":
            ev.append((t0 + .12, "gong" if fs else "bell", .6))
        elif ty == "stat":
            land = when(lines, v, t0 + .3)
            n = 10
            for k in range(n):                                          # tick dày dần theo ease-out của số đếm
                ev.append((t0 + .1 + (land + .5 - t0 - .1) * (1 - (1 - (k + 1) / n) ** 2), "tick", .25))
            ev.append((land + .45, "chime", .6))
        elif ty in ("list", "timeline"):
            for it in v.get("items") or []:
                ev.append((when(lines, it, t0 + .3), "woodblock", .55))
        elif ty in ("wheel", "elements"):
            for st in v.get("steps") or []:
                ev.append((when(lines, st, t0 + .3) + .1, "chime", .6))
        elif ty == "clock":
            end = float(lines[min(len(lines), int(v.get("until") or sid)) - 1]["end"])
            k, tt = 0, t0 + .2
            while tt < end - .2:                                       # tích tắc đều suốt cảnh đồng hồ
                ev.append((tt, "tick", .18 if k % 2 else .24))
                tt += .5
                k += 1
            for st in v.get("steps") or []:
                ev.append((when(lines, st, t0 + .3) + .1, "chime", .7))
        elif ty == "quote":
            ev.append((t0 + .05, "paper", .5))
            ev.append((t0 + .3, "bowl", .45))
        elif ty in ("doc", "photo"):
            ev.append((t0, "whoosh", .45))
            for c in v.get("circles") or []:
                ev.append((when(lines, c, t0 + .5), "brush", .6))
        elif ty == "illus":
            ev.append((t0 + .1, "bell", .5))
        elif ln.get("media") and not ln.get("media_cont"):
            ev.append((t0, "whoosh", .25))
    if lines:
        ev.append((0.0, "bowl" if not fs else "gong", .42))                # mở video
    return ev


def build(lines: list[dict], series: str, out: Path, dur: float, *, silence: set[int] | None = None,
          seed: int = 7) -> Path:
    mix = Mix(dur, seed)
    p = mix.p
    make = {"bell": p.bell, "bowl": p.bowl, "chime": p.chime, "gong": p.gong, "woodblock": p.woodblock,
            "tick": p.tick, "whoosh": p.whoosh, "brush": p.brush, "paper": p.paper}
    cache: dict[str, np.ndarray] = {}
    for k, (t, name, g) in enumerate(sorted(events(lines, series, silence or set()))):
        sig = cache.setdefault(name, make[name]()) if name not in ("tick", "woodblock", "brush", "paper") else make[name]()
        mix.put(t, sig, g, pan=((k * 37) % 11 - 5) / 25)
    mix.write(out, dur)
    return out
