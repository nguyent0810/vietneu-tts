"""Âm thanh 4 lớp cho video dài BUD / FS: giọng · không khí nơi chốn · nhạc biết thở · tiếng động chất liệu.

Học từ kênh Hình Sự của V2 (motion/long/sfx_long.py): mỗi VẬT trên màn hình kêu đúng
tiếng chất liệu của nó (hồ sơ -> gõ phím, ảnh -> màn trập), khớp từng nhịp chuyển động.
Ở đây đổi chất liệu cho hai kênh:
  Phật giáo : bút sắt khắc lá bối, tràng hạt, bước chân, tích trượng, đại hồng chung, bấc đèn
  Phong Thuỷ: bàn tính gỗ, đồng xu gieo quẻ, la bàn tách tách, cồng, đàn tranh (ngũ âm)
Thêm: không khí nơi chốn (dế đêm, gió, chim sớm, sông), giai điệu chủ đề gảy dây
(Karplus-Strong), nhạc nền nén theo giọng (lùi khi có lời, dâng ở khoảng nghỉ), tắt
trước câu đỉnh, vang phòng nhẹ cho giọng BUD. Tất cả tổng hợp bằng numpy, tất định.

    mix_long(lines, series, voice_wav, bgm_path, duration, sound_spec, silence, out_wav)
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, lfilter

from hf_sfx import SR, Mix, Palette, _env, when

NOTE = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.0, "A4": 440.0,
        "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99, "A5": 880.0, "D3": 146.83, "A3": 220.0, "C3": 130.81, "G3": 196.0}
# Ngũ âm ứng ngũ hành (truyền thống): Cung-Thổ, Thương-Kim, Giốc-Mộc, Chủy-Hoả, Vũ-Thuỷ (thang Cung = Đô)
NGU_AM = {"Thổ": "C4", "Kim": "D4", "Mộc": "E4", "Hỏa": "G4", "Thủy": "A4"}


def _bp(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return lfilter(b, a, x)


def _lp(x, hi, order=2):
    b, a = butter(order, hi / (SR / 2), "low")
    return lfilter(b, a, x)


class Foley(Palette):
    # ---------- Phật giáo ----------
    def temple_bell(self, f0=98.0, dur=9.0):
        """Đại hồng chung: tiếng hum dài + nhiều bội âm lệch, có nhịp phách."""
        s = self._partials(f0, [.5, 1, 1.19, 1.5, 2.0, 2.52, 2.66, 3.01], [.8, 1, .55, .35, .5, .25, .2, .12],
                           [7.5, 5.5, 3.5, 2.8, 2.4, 1.4, 1.1, .8], dur, 0.35)
        n = len(s)
        knock = _lp(self.rng.standard_normal(n), 900) * np.exp(-np.arange(n) / SR / .03) * .9
        return s + knock

    def stylus(self):
        """Bút sắt khắc lá bối: một nét cào khô, hạt nhám."""
        n = int(.11 * SR)
        g = (self.rng.random(n) > .55) * self.rng.standard_normal(n)
        s = _bp(g, 2200, 7500) * np.sin(np.pi * np.arange(n) / n) ** .7
        return s * .9

    def bead(self):
        """Tràng hạt: hai hạt gỗ chạm nhau."""
        out = np.zeros(int(.12 * SR))
        for k, (f, g) in enumerate([(2350, 1.0), (1980, .55)]):
            n = int(.05 * SR); t = np.arange(n) / SR; i = int(k * .028 * SR)
            hit = np.sin(2 * np.pi * f * t) * np.exp(-t / .012) + .4 * _bp(self.rng.standard_normal(n), 2500, 8000) * np.exp(-t / .003)
            out[i:i + n] += hit * g
        return out

    def footstep(self):
        n = int(.22 * SR); t = np.arange(n) / SR
        thump = _lp(self.rng.standard_normal(n), 260) * np.exp(-t / .05) * 2.2
        grit = _bp(self.rng.standard_normal(n), 1200, 5000) * np.exp(-t / .035) * .35
        return thump + grit

    def khakkhara(self):
        """Tích trượng: các khoen kim loại rung leng keng."""
        out = np.zeros(int(1.2 * SR))
        for k in range(5):
            i = int((k * .045 + self.rng.random() * .02) * SR)
            f0 = 2600 + self.rng.random() * 900
            ring = self._partials(f0, [1, 1.47, 2.09], [1, .5, .3], [.35, .2, .1], .9, 3.0)
            out[i:i + len(ring)] += ring[: len(out) - i] * (1 - k * .12)
        return out * .6

    def hooves(self, dur=3.0):
        """Vó ngựa: bước đi rồi phi nước đại (nhịp ba)."""
        out = np.zeros(int(dur * SR))
        t, k = 0.0, 0
        while t < dur - .1:
            n = int(.09 * SR); tt = np.arange(n) / SR
            clop = (np.sin(2 * np.pi * (420 + 60 * (k % 3)) * tt) * np.exp(-tt / .02)
                    + _lp(self.rng.standard_normal(n), 800) * np.exp(-tt / .025) * 1.4)
            i = int(t * SR); out[i:i + n] += clop[: len(out) - i] * (.6 + .4 * min(1, t / (dur * .5)))
            gallop = t > dur * .45
            t += ((.11, .11, .32)[k % 3] if gallop else .42) + self.rng.random() * .02
            k += 1
        return out * np.minimum(1, (dur - np.arange(len(out)) / SR) / .6)

    def gate(self):
        """Cánh cổng gỗ nặng: tiếng cót két rồi tiếng chạm trầm."""
        dur = 1.5; n = int(dur * SR); t = np.arange(n) / SR
        rate = 38 + 22 * np.sin(2 * np.pi * .7 * t)
        ph = np.cumsum(rate) / SR
        pulses = (np.mod(ph, 1) < .08).astype(float) * self.rng.standard_normal(n)
        creak = _bp(pulses, 400, 2200) * np.sin(np.pi * t / dur) ** .5 * 1.6
        thud = np.zeros(n); m = int(.4 * SR); i = n - m
        thud[i:] = _lp(self.rng.standard_normal(m), 180) * np.exp(-np.arange(m) / SR / .09) * 2.5
        return creak + thud

    def lamp(self):
        n = int(.6 * SR); t = np.arange(n) / SR
        puff = _bp(self.rng.standard_normal(n), 300, 3000) * np.exp(-t / .07) * (t < .4)
        crack = (self.rng.random(n) > .996) * self.rng.standard_normal(n) * np.exp(-t / .3)
        return puff + crack * .6

    # ---------- Phong Thuỷ ----------
    def abacus(self):
        """Bàn tính gỗ: hạt gỗ cứng đập vào thanh."""
        n = int(.07 * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1750 * t) * np.exp(-t / .009) + .7 * np.sin(2 * np.pi * 3100 * t) * np.exp(-t / .005)
                + .5 * _bp(self.rng.standard_normal(n), 1500, 6000) * np.exp(-t / .004)) * .9

    def ratchet(self, n=10, gap=.045):
        # bộ đệm tính cả độ lệch ngẫu nhiên tối đa (.01 s mỗi nhịp): n > 10 từng làm i vượt độ dài -> lỗi broadcast (F5, 03/10/2026)
        out = np.zeros(int((n * (gap + .01) + .1) * SR))
        for k in range(n):
            c = self.tick() * (.5 + .5 * self.rng.random())
            i = int(k * (gap + self.rng.random() * .01) * SR)
            if i >= len(out):
                break
            out[i:i + len(c)] += c[: len(out) - i]
        return out

    def coin_flick(self):
        n = int(.3 * SR); t = np.arange(n) / SR
        ping = self._partials(5200, [1, 1.33, 1.71], [1, .5, .3], [.12, .08, .05], .3, 6.0)
        return ping * .5 + _bp(self.rng.standard_normal(n), 1500, 6000) * np.exp(-t / .02) * .3

    def coin_land(self):
        """Xu đồng rơi xuống mặt gỗ, nảy hai lần rồi lăn."""
        out = np.zeros(int(.7 * SR))
        for k, (dt, g) in enumerate([(0, 1), (.09, .55), (.16, .3)]):
            f = 3100 + self.rng.random() * 400
            c = self._partials(f, [1, 1.51, 2.02, 2.73], [1, .6, .4, .2], [.09, .06, .04, .03], .3, 4.0)
            i = int(dt * SR); out[i:i + len(c)] += c[: len(out) - i] * g
        return out * .8

    def pluck(self, f, dur=2.6, damp=.996):
        """Gảy dây kiểu đàn tranh (Karplus-Strong), có luyến nhẹ lên nốt ở đầu."""
        n = int(dur * SR)
        N = max(2, int(SR / f))
        buf = _lp(self.rng.standard_normal(N), 6000)
        out = np.zeros(n)
        for i in range(n):
            j = i % N
            out[i] = buf[j]
            buf[j] = damp * .5 * (buf[j] + buf[(j + 1) % N])
        return _lp(out, 5000) * _env(n, .003, 1e9)

    def drone(self, dur, root=73.4, gain=1.0):
        """Nền trầm (cold open trước khi nhạc vào): quãng năm, phập phồng chậm."""
        t = np.arange(int(dur * SR)) / SR
        s = sum(a * np.sin(2 * np.pi * root * r * t + p) for r, a, p in [(1, 1, 0), (1.003, .7, 1), (1.5, .45, 2), (2, .25, .5)])
        return s * (.7 + .3 * np.sin(2 * np.pi * .07 * t)) * np.minimum(1, t / 3) * gain


# ---------- Không khí nơi chốn ----------
def ambience(kind: str, dur: float, rng: np.random.Generator) -> np.ndarray:
    n = int(dur * SR); t = np.arange(n) / SR
    wind = _bp(rng.standard_normal(n), 180, 1100) * (.55 + .45 * np.sin(2 * np.pi * .09 * t + rng.random() * 6)) * .5
    if kind == "wind":
        return wind * 1.6
    if kind == "room":
        brown = np.cumsum(rng.standard_normal(n)); brown = _lp(brown - _lp(brown, 20), 400)
        return brown / (np.abs(brown).max() + 1e-9) * .5 + wind * .35
    if kind == "river":
        bub = np.zeros(n)
        for _ in range(int(dur * 9)):
            i = int(rng.random() * (n - 4000)); m = int(.03 * SR); tt = np.arange(m) / SR
            bub[i:i + m] += np.sin(2 * np.pi * (380 + rng.random() * 500) * tt * (1 + tt * 8)) * np.exp(-tt / .01) * .4
        return _lp(rng.standard_normal(n), 1400) * .7 + bub + wind * .3
    if kind == "night":   # dế + gió nhẹ
        out = wind * .6
        for c in range(3):
            f = 4200 + c * 650 + rng.random() * 200
            gate = np.zeros(n); tt = rng.random() * .5
            while tt < dur:
                for p in range(3 + int(rng.random() * 2)):
                    i = int((tt + p * .034) * SR); m = int(.018 * SR)
                    if i + m < n:
                        gate[i:i + m] += np.hanning(m)
                tt += .55 + rng.random() * .5
            out += np.sin(2 * np.pi * f * t) * gate * (.22 - c * .05)
        return out
    if kind == "dawn":    # chim sớm + gió
        out = wind * .5
        tt = rng.random()
        while tt < dur - .5:
            for p in range(2 + int(rng.random() * 4)):
                m = int(.07 * SR); i = int((tt + p * .11) * SR); u = np.arange(m) / SR
                f0, f1 = 2400 + rng.random() * 900, 3600 + rng.random() * 1400
                ch = np.sin(2 * np.pi * (f0 * u + (f1 - f0) / (2 * .07) * u ** 2)) * np.hanning(m)
                if i + m < n:
                    out[i:i + m] += ch * .28
            tt += 1.2 + rng.random() * 2.5
        return out
    return wind


# ---------- Sự kiện ----------
def _words(ln):
    return ln.get("words") or []


def events(lines: list[dict], series: str, spec: dict, silence: set[int]) -> list[tuple[float, str, float, dict]]:
    fs = series == "fs"
    ev: list[tuple[float, str, float, dict]] = []
    motif_at = set(spec.get("motif") or [])
    for i, ln in enumerate(lines):
        sid, t0 = ln["sentence_id"], float(ln["start"])
        if sid in silence:
            continue
        v = ln.get("visual") or {}
        ty = v.get("type")
        if ln.get("heading"):
            ev.append((t0 - .05, "gong" if fs else "temple_bell", .9 if not fs else .8, {}))
            if sid in motif_at:
                ev.append((t0 + .5, "motif", .7, {}))
            continue
        if i and not ln.get("visual_cont") and not ln.get("media_cont") and ty not in ("ask", "shadow"):
            ev.append((t0 - .3, "whoosh", .1, {}))
        if ty == "word":
            ev.append((t0 + .1, "gong" if fs else "bell", .32 if fs else .38, {}))
        elif ty == "map":
            pins = v.get("pins") or []
            for k, p in enumerate(pins):
                tp = when(lines, p, t0 + 1.6 + k * 1.2)
                if k and v.get("footsteps") and not fs:
                    for j in range(5):
                        ev.append((tp - 1.25 + j * .24, "footstep", .5, {"pan": (-.2 if j % 2 else .2)}))
                ev.append((tp + .05, "chime" if fs else "khakkhara", .55 if fs else .5, {}))
        elif ty == "cuudieu":
            ev.append((t0 + .2, "whoosh", .25, {}))
            for k, st in enumerate(v.get("steps") or []):
                ev.append((when(lines, st, t0 + 1.5 + k * 1.2), "chime", .5, {}))
        elif ty == "eclipse":
            st = (v.get("steps") or [None])[0]
            ev.append((when(lines, st, t0 + 3) - .2, "gong", .5, {}))
        elif ty == "napam":
            ev.append((t0 - .1, "whoosh", .25, {}))
            ev.append((t0 + .15, "abacus" if fs else "bead", .45, {}))
        elif ty == "museum":
            ev.append((t0 - .1, "whoosh", .3, {}))
            ev.append((t0 + .1, "paper" if not fs else "chime", .3, {}))
            prev = t0 + 1.2
            for n in v.get("notes") or []:
                tn = max(prev + .6, when(lines, n, prev + 2)); prev = tn
                ev.append((tn - .65, "whoosh", .18, {}))
                ev.append((tn + .5, "brush", .45, {}))
        elif ty == "lookup":
            for k, it in enumerate(v.get("rows") or []):
                ev.append((when(lines, it, t0 + .45 + k * .18), "abacus" if fs else "bead", .4, {}))
            for j, f in enumerate(v.get("find") or []):
                tf = when(lines, f, t0 + 2 + j * 4)
                for c in range(6):   # trống số lật lách cách
                    ev.append((tf - .4 + c * .14, "abacus" if fs else "bead", .28, {"pan": .3}))
                ev.append((tf + .12, "stylus", .55, {"pan": -.1}))
                ev.append((tf + .4, "stylus", .45, {"pan": -.1}))
            if v.get("pause"):
                ev.append((when(lines, v["pause"], t0 + 6), "chime", .5, {}))
        elif ty == "annot":
            ev.append((t0 - .15, "paper", .5, {}))
            for j, m in enumerate(v.get("marks") or []):
                tm = when(lines, m, t0 + 1.2 + j * 1.6)
                ev.append((tm, "stylus", .55, {"pan": .1}))
                ev.append((tm + .25, "stylus", .4, {"pan": .2}))
                if m.get("note"):
                    ev.append((tm + .85, "brush", .4, {}))
        elif ty == "relic":
            ev.append((t0 - .1, "brush", .45, {}))
            ev.append((t0 + .6, "brush", .35, {}))
            ev.append((t0 + 2.0, "whoosh", .3, {}))
            ev.append((t0 + 2.3, "chime" if fs else "temple_bell", .35, {}))
            prev = t0 + 3.5
            for n in v.get("notes") or []:
                tn = max(prev + .8, when(lines, n, prev + 2)); prev = tn
                ev.append((tn - .65, "whoosh", .18, {}))
                ev.append((tn + .5, "brush", .4, {}))
        elif ty == "chiwheel":
            for j, st in enumerate(v.get("steps") or []):
                ts = when(lines, st, t0 + 1.4 + j * .9)
                ev.append((ts, "gong" if st.get("arc") else "abacus" if fs else "bead", .45 if st.get("arc") else .5, {}))
        elif ty == "pie":
            for k, p in enumerate(v.get("parts") or []):
                tp = when(lines, p, t0 + .8 + k * 1.2)
                ev.append((tp, "brush", .5, {}))
                ev.append((tp + .7, "coin_land" if fs else "bead", .45, {}))
        elif ty == "compass":
            for k, d in enumerate(v.get("dirs") or []):
                ev.append((when(lines, d, t0 + 1.4 + k * .9), "chime" if fs else "bell", .32, {}))
        elif ty == "clues":
            for k, c in enumerate(v.get("cards") or []):
                tc = when(lines, c, t0 + .4 + k * 1.2)
                ev.append((tc, "paper", .4, {"pan": (-.3 if k % 2 else .3)}))
                ev.append((tc + .35, "bead" if not fs else "abacus", .35, {}))
            for L in v.get("links") or []:
                ev.append((when(lines, L, t0 + 2), "stylus", .45, {}))
            if v.get("answer"):
                ev.append((when(lines, v["answer"], t0 + 6) + .2, "gong" if fs else "temple_bell", .5, {}))
        elif ty == "stamp":
            ev.append((t0, "paper", .35, {}))
            ev.append((when(lines, v, t0 + 2.2) + .2, "gate", .7, {}))
        elif ty == "scroll":
            ev.append((t0 - .1, "paper", .55, {}))
            ev.append((t0 + .5, "brush", .35, {}))
        elif ty == "dialog":
            for k, tn in enumerate(v.get("turns") or []):
                ev.append((when(lines, tn, t0 + .8 + k * 2.5) - .45, "bead", .25, {"pan": (.35 if tn.get("who") == "right" else -.35)}))
        elif ty == "wind":
            for j, stp in enumerate(v.get("steps") or []):
                ev.append((when(lines, stp, t0 + 1.4 + j * 2.4) - .3, "whoosh", .45, {"pan": -.3}))
        elif ty == "bagua":
            ev.append((t0 - .1, "whoosh", .3, {}))
            for j, stp in enumerate(v.get("steps") or []):
                ev.append((when(lines, stp, t0 + 1.5 + j * 2), "chime" if stp.get("show") == "marker" else ("abacus" if fs else "bead"), .45, {}))
        elif ty == "teaser":
            ev.append((t0 - .1, "whoosh", .3, {}))
            ev.append((t0 + 1.2, "chime", .4, {}))
        elif ty == "ledger":
            for k, it in enumerate(v.get("rows") or []):
                ev.append((when(lines, it, t0 + .5 + k * .25), "abacus" if fs else "bead", .5, {}))
        elif ty in ("list", "timeline"):
            for k, it in enumerate(v.get("items") or []):
                tw = when(lines, {**it, "word": it.get("word") or it.get("yr")}, t0 + .4 + k * .8)
                ev.append((tw, "abacus" if fs else "bead", .6 if fs else .7, {}))
        elif ty == "stat":
            land = when(lines, v, t0 + .3)
            for k in range(12):
                ev.append((t0 + .1 + (land + .5 - t0 - .1) * (1 - (1 - (k + 1) / 12) ** 2), "abacus" if fs else "bead", .35, {}))
            ev.append((land + .45, "chime", .55, {}))
        elif ty == "quote":
            ev.append((t0 - .1, "paper", .35, {}))
            for w in _words(ln):   # mỗi chữ một nét khắc
                ev.append((float(w["t"]) + .02, "stylus", .32, {"pan": .15}))
        elif ty == "shadow":
            sc = v.get("scene")
            if sc == "departure":
                st = (v.get("steps") or [None])[0]
                ev.append((when(lines, st, t0 + 3) - .1, "gate", .8, {}))
            elif sc == "turtle":
                st = (v.get("steps") or [None])[0]
                td = when(lines, st, t0 + 3)
                for c in range(9):
                    ev.append((td + c * .22, "pluck", .35, {"f": NOTE[["C5", "D5", "E5", "G5", "A5"][c % 5]]}))
                ev.append((t0 + .4, "whoosh", .3, {}))
            elif sc == "lamp":
                st = v.get("steps") or []
                ev.append((when(lines, st[0] if st else None, t0 + 1.5), "lamp", .7, {}))
                if len(st) > 1:
                    ev.append((when(lines, st[1], t0 + 4), "bowl", .35, {}))
            elif sc == "forest":
                st = (v.get("steps") or [None])[0]
                tstop = when(lines, st, t0 + 4)
                k = 0
                tt = t0 + .2
                while tt < tstop:
                    ev.append((tt, "footstep", .22 if k % 3 else .3, {"pan": .3}))
                    tt += .5; k += 1
                tt = t0 + .3
                while tt < tstop:
                    ev.append((tt, "footstep", .4, {"pan": -.35}))
                    tt += .19
            else:
                ev.append((t0 + .2, "bowl", .3, {}))
        elif ty == "hexagram":
            steps, last = v.get("steps") or [], t0
            for k in range(len(v.get("lines") or [])):
                t = max(last + 1.0, when(lines, steps[k] if k < len(steps) else None, last + 1.4)); last = t
                ev.append((t, "coin_flick", .5, {}))
                for j in range(3):
                    ev.append((t + .66 + j * .06, "coin_land", .55, {"pan": (j - 1) * .35}))
                ev.append((t + 1.0, "woodblock", .45, {}))
            ev.append((max(when(lines, v.get("reveal"), last + 1.6), last + 1.5), "gong", .55, {}))
        elif ty == "luoshu":
            st = {s.get("do"): s for s in v.get("steps") or []}
            ev.append((t0 + .1, "paper", .3, {}))
            if "numbers" in st:
                tn = when(lines, st["numbers"], t0 + 3)
                for k in range(9):
                    ev.append((tn + k * .18 + .12, "abacus", .6, {"pan": ((k % 3) - 1) * .3}))
            for key in ("rows", "cols"):
                if key in st:
                    for k in range(3):
                        ev.append((when(lines, st[key], t0) + k * .45 + .1, "chime", .45, {}))
            if "diags" in st:
                for k in range(2):
                    ev.append((when(lines, st["diags"], t0) + k * .5, "brush", .55, {}))
            if "center" in st:
                tc = when(lines, st["center"], t0)
                ev.append((tc, "pluck", .8, {"f": NOTE[NGU_AM["Thổ"]]}))       # Cung = Thổ
                ev.append((tc + .02, "gong", .3, {}))
            if "dirs" in st:
                ev.append((when(lines, st["dirs"], t0), "ratchet", .5, {}))
        elif ty == "illus":
            sc = v.get("scene")
            if sc == "house":
                ev.append((t0 + 1.3, "ratchet", .55, {"n": 16}))
                ev.append((t0 + 3.0, "tick", .5, {}))
            elif sc == "sunrise" and not fs:
                ev.append((t0 + .3, "bowl", .35, {}))
        if sid in motif_at and not ln.get("heading"):
            ev.append((max(t0, float(ln["end"]) - 1.5), "motif", .65, {}))
    for fx in spec.get("fx") or []:
        ev.append((when(lines, fx, 0.0), fx["s"], float(fx.get("gain", .6)), {"dur": fx.get("dur")}))
    return ev


def motif(p: Foley, fs: bool) -> np.ndarray:
    """Giai điệu chủ đề kênh: 5 nốt ngũ cung gảy dây."""
    seq = ([("C5", .0), ("D5", .32), ("E5", .64), ("G5", .96), ("E5", 1.45), ("C5", 1.95)] if fs else
           [("D4", .0), ("F4", .55), ("G4", 1.1), ("A4", 1.65), ("G4", 2.5), ("D4", 3.2)])
    out = np.zeros(int(6.5 * SR))
    for name, at in seq:
        s = p.pluck(NOTE[name] * (1 if fs else 1), dur=3.0)
        i = int(at * SR); out[i:i + len(s)] += s[: len(out) - i] * (1 if name != seq[-1][0] else .9)
    if not fs:
        b = p.bowl(f0=146.83, dur=6.0) * .35
        out[: len(b)] += b[: len(out)]
    return out


def build_sfx(lines, series, spec, silence, dur, seed=11) -> np.ndarray:
    mix = Mix(dur, seed)
    p = Foley(seed)
    mix.p = p
    for k, (t, name, g, kw) in enumerate(sorted(events(lines, series, spec, silence), key=lambda e: e[0])):
        if name == "motif":
            sig = motif(p, series == "fs")
        elif name == "pluck":
            sig = p.pluck(kw["f"])
        elif name == "hooves":
            sig = p.hooves(kw.get("dur") or 3.0)
        elif name == "ratchet":
            sig = p.ratchet(kw.get("n", 10))
        else:
            sig = getattr(p, name)()
        mix.put(t, sig, g, pan=kw.get("pan", ((k * 37) % 11 - 5) / 30))
    return mix.bus[: int(dur * SR)]


# ---------- Trộn ----------
def _decode(path: Path, dur: float) -> np.ndarray:
    with tempfile.TemporaryDirectory() as td:
        o = Path(td) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", str(path), "-t", f"{dur:.3f}",
                        "-ar", str(SR), "-ac", "2", str(o)], check=True)
        a, _ = sf.read(o, dtype="float32")
    out = np.zeros((int(dur * SR), 2), dtype="float32")
    out[: len(a)] = a[: len(out)]
    return out


# Nền nhạc theo chương (04/10/2026, ý từ BGM nhiều đoạn của Youtube_Creator_V2). Trước đây một bản 3-4 phút lặp
# 8-9 lần qua -stream_loop trong video 30 phút; bản nào cũng kết bằng 2-3 giây im (-40..-155 dB) nên cứ vài phút
# nhạc lại hụt về im rồi bật lại từ đầu, ở vị trí ngẫu nhiên giữa câu. Giờ: cắt im đầu/cuối, phát liền một bản,
# chỉ đổi sang bản cùng mood ở THẺ CHƯƠNG khi chương tới không còn vừa phần còn lại, chồng mờ 3 giây.
BGM_POOL = {"bud": ["bgm/meditation_impromptu_01.mp3", "bgm/meditation_impromptu_02.mp3", "bgm/meditation_impromptu_03.mp3"],
            "fs": ["bgm/deliberate_thought.mp3", "bgm/thinking_music.mp3", "bgm/comfortable_mystery_4.mp3"]}
XFADE = 3.0


def _trimmed(path: Path) -> np.ndarray:
    """Cả bản (không lặp), cắt khoảng im/đuôi tắt dần ở đầu và cuối (dưới thân bài 35 dB)."""
    with tempfile.TemporaryDirectory() as td:
        o = Path(td) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ar", str(SR), "-ac", "2", str(o)], check=True)
        a, _ = sf.read(o, dtype="float32")
    hop = int(.05 * SR)
    rms = np.sqrt(np.mean(a[: len(a) // hop * hop].mean(axis=1).reshape(-1, hop) ** 2, axis=1)) + 1e-9
    db = 20 * np.log10(rms)
    loud = np.where(db > np.median(db) - 35)[0]
    return a[loud[0] * hop: (loud[-1] + 1) * hop] if len(loud) else a


def _loop(tr: np.ndarray, n: int, X: int) -> np.ndarray:
    """n mẫu từ đầu bản `tr`; hết bản thì nối lại từ đầu, chồng mờ X mẫu (chỉ khi một đoạn dài hơn cả bản)."""
    res, got, pos = np.zeros((n, 2), dtype="float32"), 0, 0
    while got < n:
        take = min(n - got, len(tr) - pos)
        res[got: got + take] += tr[pos: pos + take]
        got += take
        pos += take
        if got < n:
            back = min(X, got, len(tr))
            ramp = np.linspace(0, 1, back, dtype="float32")[:, None]
            res[got - back: got] = res[got - back: got] * (1 - ramp) + tr[:back] * ramp
            pos = back
    return res


def music_bed(first: Path, series: str, starts: list[float], dur: float, root: Path) -> tuple[np.ndarray, list[str]]:
    """Nền nhạc dài `dur` giây, chỉ đổi bản ở các mốc `starts` (giây bắt đầu thẻ chương)."""
    names = BGM_POOL.get(series) or []
    rel = next((n for n in names if Path(n).name == first.name), None)
    order = ([rel] + [n for n in names if n != rel]) if rel else [str(first)]
    tracks = [_trimmed(root / n) for n in order]
    N, X = int(dur * SR), int(XFADE * SR)
    cuts = sorted({0.0, *[t for t in starts if XFADE < t < dur - XFADE]}) + [dur]
    runs, k, off = [], 0, 0          # [bản, mẫu bắt đầu, mẫu kết thúc]; mỗi lượt phát một bản từ đầu
    for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
        A, B = int(a * SR), int(b * SR)
        if i and off + (B - A) > len(tracks[k]) and len(tracks) > 1:
            k, off = (k + 1) % len(tracks), 0
        if runs and runs[-1][0] == k and runs[-1][2] == A:
            runs[-1][2] = B
        else:
            runs.append([k, A, B])
        off += B - A
    out = np.zeros((N + X, 2), dtype="float32")
    for j, (k, A, B) in enumerate(runs):
        s0 = A - (X // 2 if j else 0)
        s1 = min(len(out), B + (X - X // 2 if j < len(runs) - 1 else 0))
        seg = _loop(tracks[k], s1 - s0, X)
        if j:
            seg[:X] *= np.linspace(0, 1, X, dtype="float32")[:, None]
        if j < len(runs) - 1:
            seg[-X:] *= np.linspace(1, 0, X, dtype="float32")[:, None]
        out[s0:s1] += seg
    return out[:N], [Path(order[k]).name for k, _, _ in runs]


def lufs(x: np.ndarray) -> float:
    from hyperframes_bridge import integrated_lufs  # noqa: PLC0415
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.wav"
        sf.write(p, x, SR)
        return integrated_lufs(p)


def _db(x):
    return 10 ** (x / 20)


def _st(x):
    return x if x.ndim == 2 else np.stack([x, x], axis=1)


def reverb_ir(seed=3, decay=.38, predelay=.022) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(max(.4, decay * 4.5) * SR); t = np.arange(n) / SR
    ir = np.stack([_lp(rng.standard_normal(n), 5200) * np.exp(-t / decay) for _ in range(2)], axis=1)
    ir = np.vstack([np.zeros((int(predelay * SR), 2)), ir])
    return ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True))


def envelope(x: np.ndarray, att=.06, rel=.7) -> np.ndarray:
    """Đường bao giọng (0..1) để nén nhạc theo giọng: lên nhanh, xuống chậm."""
    hop = int(.01 * SR)
    m = np.abs(x if x.ndim == 1 else x.mean(axis=1))
    n = len(m) // hop
    r = np.sqrt((m[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    r = r / (np.percentile(r[r > 0], 90) + 1e-9) if (r > 0).any() else r
    a, b = np.exp(-.01 / att), np.exp(-.01 / rel)
    e, out = 0.0, np.zeros(n)
    for i, v in enumerate(np.minimum(1, r * 2.5)):
        e = a * e + (1 - a) * v if v > e else b * e + (1 - b) * v
        out[i] = e
    return np.repeat(out, hop)[: len(x)] if n else np.zeros(len(x))


def mix_long(lines: list[dict], series: str, voice_wav: Path, bgm: Path | None, duration: float,
             spec: dict, silence: set[int], out_wav: Path, seed: int = 11) -> Path:
    fs = series == "fs"
    v, sr = sf.read(voice_wav, dtype="float32")
    if sr != SR:
        from scipy.signal import resample_poly  # noqa: PLC0415
        v = resample_poly(v, SR, sr).astype("float32")
    v = v.mean(axis=1) if v.ndim == 2 else v
    N = int(duration * SR)
    v = np.pad(v, (0, max(0, N - len(v))))[:N]
    if spec.get("voice_eq"):
        # Giọng TTS 24 kHz có dải rè ở trên ~10 kHz và ù dưới 70 Hz: cắt bớt hai đầu cho sạch.
        b, a = butter(2, 70 / (SR / 2), "high"); v = lfilter(b, a, v)
        v = _lp(v, float(spec.get("voice_lp", 10500))).astype("float32")
    L_v = lufs(v)
    voice = _st(v)
    if spec.get("reverb"):
        ir = reverb_ir(seed, float(spec.get("reverb_decay", .38)))
        wet = np.stack([fftconvolve(v, ir[:, c])[:N] for c in range(2)], axis=1)
        voice = voice + wet * float(spec["reverb"])
    rng = np.random.default_rng(seed)
    by_id = {ln["sentence_id"]: ln for ln in lines}
    t = np.arange(N) / SR

    # Nhạc nền: vào từ câu `music_from`, nén theo giọng, tắt ở câu lặng / trước câu đỉnh.
    music = np.zeros((N, 2), dtype="float32")
    if bgm:
        starts = [float(ln["start"]) - .3 for ln in lines if ln.get("heading")]
        if spec.get("bgm_rotate", True) and starts:
            music, used = music_bed(bgm, series, starts, duration, Path(__file__).parent)
            print(f"    nền nhạc theo chương: {' -> '.join(used)}", flush=True)
        else:
            music = _decode(bgm, duration)
        music *= _db(L_v - float(spec.get("music_gap", 15)) - lufs(music))
        g = np.ones(N)
        mf = spec.get("music_from")
        if mf and mf in by_id:
            m0 = float(by_id[mf]["start"]) - .2
            g *= np.clip((t - m0) / 2.0, 0, 1)
        cut = [(float(by_id[s]["start"]) - .15, float(by_id[s]["end"]) + .4) for s in silence if s in by_id]
        cut += [(float(by_id[s]["start"]) - 1.0, float(by_id[s]["end"]) + .3) for s in spec.get("drops") or [] if s in by_id]
        for a, b in cut:
            ramp = np.clip(np.minimum((a + .6 - t) / .6, (t - b) / 1.6), 0, 1)
            g *= np.where((t > a) & (t < b + 1.6), ramp, 1)
        duck = 1 - .5 * envelope(v)            # ~-6 dB khi đang có lời
        fade = np.clip((duration - t) / 2.0, 0, 1)
        music *= (g * duck * fade)[:, None]

    # Nền trầm cho đoạn mở trước khi nhạc vào.
    p = Foley(seed)
    drone = np.zeros(N)
    mf = spec.get("music_from")
    if mf and mf in by_id:
        end = float(by_id[mf]["start"]) + 1.0
        d = p.drone(end + 2, root=(110.0 if fs else 73.42))[: N]
        d *= np.clip((end + 1.5 - t[: len(d)]) / 2.5, 0, 1)
        drone[: len(d)] = d
        if np.abs(drone).max() > 0:
            drone *= _db(L_v - float(spec.get("drone_gap", 24)) - lufs(drone[: int(end * SR)]))

    # Không khí nơi chốn theo khoảng câu.
    amb = np.zeros(N)
    for a in spec.get("amb") or []:
        s0 = float(by_id[a["from"]]["start"]) - .8 if a["from"] in by_id else 0.0
        s1 = float(by_id[a["to"]]["end"]) + 1.2 if a["to"] in by_id else duration
        s0, s1 = max(0.0, s0), min(duration, s1)
        seg = ambience(a["kind"], s1 - s0, rng)
        seg *= _db(L_v - float(a.get("gap", spec.get("amb_gap", 25))) - lufs(seg))
        k = np.arange(len(seg)) / SR
        seg *= np.clip(np.minimum(k / 1.5, (s1 - s0 - k) / 1.5), 0, 1)
        i = int(s0 * SR); amb[i:i + len(seg)] += seg[: N - i]

    sfx = build_sfx(lines, series, spec, silence, duration, seed)
    pk = np.abs(sfx).max()
    if pk > 0:
        sfx *= (np.abs(v).max() * float(spec.get("sfx_peak", .5))) / pk   # .5 = đỉnh tiếng động dưới đỉnh giọng ~6 dB

    out = voice + music + _st(drone) + _st(amb) + sfx
    out /= max(1.0, np.abs(out).max() / .98)
    sf.write(out_wav, out.astype("float32"), SR, subtype="PCM_24")
    return out_wav
