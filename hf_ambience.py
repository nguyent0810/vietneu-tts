"""Long điện ảnh (task 011, #138): lớp âm thanh không gian theo chương/cảnh + nhịp đạo diễn (lặng / nhấn).

Foley cũ (hf_foley) là tiếng động lẻ khớp hình + `amb` 5 loại đơn giản. Ở đây thêm một LỚP NỀN không gian
cho từng chương hay từng cảnh, nằm dưới giọng và dưới nhạc, tự lùi khi có giọng, và hai nhịp đạo diễn:

  beat "silence"  0,5-2 s nhạc + tiếng động tắt hẳn, chỉ còn ambience (khoảng nghỉ TTS tự giãn cho vừa).
  beat "hit"      một phát nhấn trầm (trống trầm + sub) ngay đầu câu hoặc đúng một chữ.

Plan (một row Long; khoá cấp row, cạnh `visuals`/`silence`):

    "ambience": [
        {"kind": "night_insects", "gain_db": 0},                    # cả video (không ghi chapter/from)
        {"chapter": 2, "kind": "rain", "gain_db": -2},             # cả chương 2 (0 = cold open trước thẻ chương đầu)
        {"from": 40, "to": 58, "kind": "temple_bell_far"},         # theo cảnh: câu 40..58 (số câu như `visuals`)
        {"chapter": 4, "kind": "none"}                              # chương 4 không nền
    ],
    "beats": {"57": "silence",                                      # lặng 1,2 s NGAY TRƯỚC câu 57
              "58": {"beat": "hit", "word": "chôn"},                # nhấn đúng lúc đọc chữ "chôn"
              "90": {"beat": "silence", "dur": 1.5, "at": "after", "hold": false}}

  Ưu tiên: cảnh > chương > cả video; cùng mức thì khai sau thắng. Đổi loại: chồng mờ equal-power 2,5 s.
  gain_db: cộng vào mức chuẩn (giọng - `amb_gap` 26 LU), kẹp -24..+6 và luôn dưới nhạc >= 3 LU.
  Plan cũ dùng `sound.amb` (wind/room/river/night/dawn) giữ nguyên; có `ambience` thì `amb` cũ bị bỏ qua.

Nguồn âm: MẶC ĐỊNH TỰ TỔNG HỢP bằng numpy (tất định theo seed, CC0 -- repo tự tạo, không mẫu ngoài).
Muốn thay bằng bản thu thật: đặt file vào assets/ambience/ và khai trong assets/ambience/sources.json
    {"rain": {"file": "rain_xxx.flac", "source": "<URL trang gốc>", "author": "...", "license": "CC0-1.0"}}
license chỉ nhận CC0 / Public Domain (ALLOWED_LICENSES); khác là dừng (không tải nguồn không rõ giấy phép).
Mỗi video đã khai ambience được ghi sổ output/cl_staging/long/ambience_ledger.json (loại + nguồn + giấy phép).

Loop không lộ mối nối: mỗi ô (tile) 40 s là tín hiệu TUẦN HOÀN (nhiễu lọc vòng, sự kiện đặt vòng, vang tích
chập vòng) -> lặp chính nó không có mối; nền dài hơn ghép 3 biến thể luân phiên, chồng mờ equal-power 2 s.

    python hf_ambience.py library                      # 10 loại + nguồn + giấy phép
    python hf_ambience.py preview rain 20 /tmp/r.wav   # nghe thử một loại
    python hf_ambience.py check <plan.json> [--only id]  # soát khai báo ambience/beats của plan
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
SR = 48000
LEDGER = ROOT / "output" / "cl_staging" / "long" / "ambience_ledger.json"
FILE_DIR = ROOT / "assets" / "ambience"
ALLOWED_LICENSES = {"cc0", "cc0-1.0", "cc0 1.0", "pd", "public domain", "public-domain", "pdm", "pdm-1.0"}

KINDS = ("rain", "wind", "forest", "river", "temple_bell_far", "market", "night_insects", "fire", "cave", "none")
BEATS = ("silence", "hit")

TILE_S = 40.0          # độ dài một ô tuần hoàn
JOIN_S = 2.0           # chồng mờ giữa hai biến thể
N_VARIANTS = 3
XFADE_S = 2.5          # chồng mờ khi đổi loại / đổi mức giữa hai đoạn
LEAD_S = 0.6           # đổi nền sớm hơn đầu câu một chút (rơi vào khoảng nghỉ)
TILE_RMS = 0.03        # ~ -30 dBFS, mức thô trước khi đặt theo LUFS giọng

AMB_GAP = 26.0         # nền nằm dưới giọng 26 LU (plan cũ amb_gap 25-28)
AMB_DUCK_DB = 4.0      # lùi thêm khi có giọng
UNDER_MUSIC = 3.0      # luôn dưới nhạc ít nhất 3 LU
GAIN_RANGE = (-24.0, 6.0)
SWELL_DB = 3.0         # trong khoảng lặng, nền dâng nhẹ cho "không khí" lấp chỗ nhạc

SILENCE_DUR = (0.5, 2.0)
SILENCE_DEFAULT = 1.2
FADE_OUT_S = .35       # nhạc tắt trước khoảng lặng
RETURN_S = 1.5         # nhạc trở lại sau khoảng lặng
HIT_REL_DB = -3.0      # đỉnh phát nhấn so với đỉnh giọng
HIT_DIP_DB = 4.0       # nhạc lùi nhẹ ngay trước phát nhấn

_SYNTH = "tự tổng hợp numpy (hf_ambience.{fn}), tất định theo seed -- không dùng mẫu ngoài"
_CC0 = "CC0 1.0 (âm do repo tự tạo)"
SOURCES = {k: {"nguon": _SYNTH.format(fn=f"_{k}"), "giay_phep": _CC0} for k in KINDS if k != "none"}


# ---------------------------------------------------------------- lọc / tiện ích
@lru_cache(maxsize=64)
def _sos(kind: str, lo: float, hi: float, order: int = 2):
    ny = SR / 2
    if kind == "low":
        return butter(order, hi / ny, "low", output="sos")
    if kind == "high":
        return butter(order, lo / ny, "high", output="sos")
    return butter(order, [lo / ny, hi / ny], "band", output="sos")


def _circ(x: np.ndarray, kind: str, lo: float = 0.0, hi: float = 0.0, order: int = 2) -> np.ndarray:
    """Lọc TUẦN HOÀN: lọc [x, x] rồi lấy nửa sau -> đầu ra có chu kỳ đúng len(x), lặp không mối nối."""
    n = len(x)
    return sosfilt(_sos(kind, lo, hi, order), np.concatenate([x, x]), axis=0)[n:]


def _pmod(rng: np.random.Generator, n: int, kmin: int, kmax: int, comps: int = 3) -> np.ndarray:
    """Đường cong chậm 0..1 tuần hoàn theo ô (mỗi thành phần có số chu kỳ nguyên trong ô)."""
    t = np.arange(n) / n
    s = sum(np.sin(2 * np.pi * rng.integers(kmin, kmax + 1) * t + rng.random() * 6.283) * rng.uniform(.5, 1)
            for _ in range(comps))
    s = s - s.min()
    return s / (s.max() + 1e-9)


def _put(buf: np.ndarray, sig: np.ndarray, pos: int, pan: float = 0.0, gain: float = 1.0) -> None:
    """Cộng sự kiện mono vào bộ đệm stereo, VÒNG qua cuối ô (đuôi tràn sang đầu)."""
    n, m = len(buf), len(sig)
    st = np.stack([sig * np.sqrt((1 - pan) / 2), sig * np.sqrt((1 + pan) / 2)], axis=1) * gain
    pos %= n
    k = min(m, n - pos)
    buf[pos:pos + k] += st[:k]
    if k < m:
        buf[:m - k] += st[k:]


def _creverb(x: np.ndarray, decay: float, rng: np.random.Generator, predelay: float = .03, lp: float = 5000) -> np.ndarray:
    """Vang tích chập VÒNG (FFT cùng độ dài ô): đuôi vang cuối ô vòng sang đầu ô."""
    n = len(x)
    m = int(min(n - 1, (decay * 5 + predelay) * SR))
    t = np.arange(m) / SR
    ir = np.stack([sosfilt(_sos("low", 0, lp), rng.standard_normal(m)) for _ in range(2)], axis=1)
    ir *= np.exp(-t / decay)[:, None] * (t >= predelay)[:, None]
    ir /= np.sqrt((ir ** 2).sum(axis=0, keepdims=True)) + 1e-9
    pad = np.zeros((n, 2))
    pad[:m] = ir
    return np.fft.irfft(np.fft.rfft(x, axis=0) * np.fft.rfft(pad, axis=0), n, axis=0)


def _noise2(rng: np.random.Generator, n: int, corr: float = .35) -> np.ndarray:
    a, b = rng.standard_normal(n), rng.standard_normal(n)
    return np.stack([a + corr * b, b + corr * a], axis=1) / np.sqrt(1 + corr ** 2)


def _db(x: float) -> float:
    return float(10 ** (x / 20))


# ---------------------------------------------------------------- 9 loại nền
def _rain(rng, n):
    hiss = _circ(_noise2(rng, n), "band", 900, 9000)
    body = _circ(_noise2(rng, n), "band", 250, 1800)
    mod = (.85 + .15 * _pmod(rng, n, 1, 4))[:, None]
    imp = np.zeros((n, 2))
    cnt = int(n / SR * 380)
    for c in range(2):
        imp[rng.integers(0, n, cnt), c] = np.minimum(rng.pareto(3.0, cnt) * .35, 2.0) * rng.choice([-1, 1], cnt)
    patter = _circ(imp, "band", 2000, 9000)
    out = hiss * .55 * mod + body * .25 + patter * .9
    m = int(.06 * SR)
    tt = np.arange(m) / SR
    for _ in range(int(n / SR * 4)):                                  # giọt to: "bloop" cao độ đi lên
        f0 = rng.uniform(900, 2200)
        ph = 2 * np.pi * np.cumsum(f0 * (1 + .6 * (1 - np.exp(-tt / .015)))) / SR
        _put(out, np.sin(ph) * np.exp(-tt / .012), int(rng.integers(n)), rng.uniform(-.7, .7), rng.uniform(.05, .25))
    return out


def _wind(rng, n):
    g = _pmod(rng, n, 2, 7)[:, None]
    low = _circ(_noise2(rng, n, .6), "band", 70, 450)
    mid = _circ(_noise2(rng, n, .4), "band", 350, 1600)
    f = rng.uniform(560, 760)
    whistle = _circ(_noise2(rng, n, .8), "band", f * .96, f * 1.04)
    return low * (.5 + .5 * g) + mid * .6 * g ** 1.6 + whistle * .5 * g ** 3


def _bird(rng):
    sp = rng.integers(3)
    if sp == 0:                                                       # chíp quét lên
        m = int(.07 * SR); u = np.arange(m) / SR
        f0, f1 = rng.uniform(2400, 3300), rng.uniform(3600, 5000)
        one = np.sin(2 * np.pi * (f0 * u + (f1 - f0) / (2 * .07) * u ** 2)) * np.hanning(m)
        out = np.zeros(int(.6 * SR))
        for p in range(int(rng.integers(2, 6))):
            i = int(p * .11 * SR); out[i:i + m] += one[: len(out) - i]
        return out
    if sp == 1:                                                       # huýt hai nốt
        m = int(.5 * SR); u = np.arange(m) / SR
        f = np.where(u < .22, rng.uniform(1800, 2400), rng.uniform(1400, 1900))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * u / .5) ** .5 * (np.abs(u - .23) > .02)
    m = int(rng.uniform(.4, .8) * SR); u = np.arange(m) / SR       # láy (trill)
    return np.sin(2 * np.pi * rng.uniform(3000, 4200) * u) * (.5 + .5 * np.sin(2 * np.pi * rng.uniform(16, 24) * u)) \
        * np.hanning(m)


def _forest(rng, n):
    gust = _pmod(rng, n, 2, 6)[:, None]
    leaves = _circ(_circ(_noise2(rng, n, .2), "high", 1800), "low", 0, 7500)
    low = _circ(_noise2(rng, n, .6), "band", 90, 350)
    out = leaves * (.35 + .65 * gust) * .5 + low * .3
    t = rng.uniform(0, 2)
    while t < n / SR:
        b = _bird(rng)
        _put(out, b, int(t * SR), rng.uniform(-.8, .8), rng.uniform(.04, .16))
        t += rng.uniform(2.2, 6.0)
    return out


def _river(rng, n):
    rush = _circ(_noise2(rng, n, .3), "low", 0, 1200)
    gurgle = _circ(_noise2(rng, n, .3), "band", 200, 700) * (.6 + .4 * _pmod(rng, n, 40, 120, 4))[:, None]
    out = rush * .7 + gurgle * .5
    m = int(.04 * SR); tt = np.arange(m) / SR
    for _ in range(int(n / SR * 14)):
        f0 = rng.uniform(350, 1000)
        ph = 2 * np.pi * np.cumsum(f0 * (1 + tt * 9)) / SR
        _put(out, np.sin(ph) * np.exp(-tt / rng.uniform(.008, .015)), int(rng.integers(n)), rng.uniform(-.6, .6),
             rng.uniform(.03, .12))
    return out


def _temple_bell_far(rng, n):
    from hf_foley import Foley  # noqa: PLC0415 -- dùng lại chuông đại hồng chung của foley
    room = _circ(_noise2(rng, n, .7), "low", 0, 220) * .4 + _circ(_noise2(rng, n, .5), "band", 150, 600) * .08
    bells = np.zeros((n, 2))
    p = Foley(int(rng.integers(1 << 30)))
    for frac in (.12, .62):
        b = p.temple_bell(f0=98.0 * rng.uniform(.97, 1.03), dur=12.0)
        b = sosfilt(_sos("low", 0, 1600), b)                         # xa: mất bội âm cao
        _put(bells, b / (np.abs(b).max() + 1e-9), int((frac + rng.uniform(-.05, .05)) * n), rng.uniform(-.25, .25), .5)
    return room + bells * .35 + _creverb(bells, 1.4, rng, .06, 3500) * .5


def _market(rng, n):
    T = n / SR
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for _ in range(10):                                               # 10 người nói xa, không ra chữ
        f0 = round(rng.uniform(95, 230) * T) / T                      # số chu kỳ nguyên trong ô -> pha khép vòng
        k = int(rng.integers(1, 4))
        ph = f0 * t + (.06 * f0 * T / (2 * np.pi * k)) * np.sin(2 * np.pi * k * t / T + rng.random() * 6)
        saw = 2 * (ph % 1.0) - 1
        voiced = _circ(saw, "band", rng.uniform(280, 420), rng.uniform(800, 1000)) \
            + .6 * _circ(saw, "band", rng.uniform(1000, 1300), rng.uniform(2000, 2600))
        env = np.zeros((n, 2))
        u = rng.uniform(0, 2)
        while u < T:
            ph_len, s = rng.uniform(1.0, 3.5), u
            while s < u + ph_len:
                m = int(rng.uniform(.12, .22) * SR)
                _put(env, np.hanning(m) * rng.uniform(.5, 1), int(s * SR))
                s += rng.uniform(.15, .25)
            u += ph_len + rng.uniform(.4, 2.0)
        pan, g = rng.uniform(-.8, .8), rng.uniform(.3, 1)
        e = env[:, 0]
        out[:, 0] += voiced * e * g * np.sqrt((1 - pan) / 2)
        out[:, 1] += voiced * e * g * np.sqrt((1 + pan) / 2)
    out = _circ(out, "low", 0, 3200)
    out = out + _creverb(out, .35, rng, .02, 4000) * .4 + _circ(_noise2(rng, n, .6), "band", 150, 700) * .15
    m = int(.4 * SR); tt = np.arange(m) / SR
    s = rng.uniform(0, 2)
    while s < T:                                                      # tiếng bát đĩa, kim loại lách cách
        f = rng.uniform(2200, 3800)
        c = sum(a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt / d) for r, a, d in ((1, 1, .12), (1.5, .5, .07), (2.3, .3, .04)))
        _put(out, c, int(s * SR), rng.uniform(-.7, .7), rng.uniform(.02, .06))
        s += rng.uniform(1.5, 4.0)
    return out


def _night_insects(rng, n):
    T = n / SR
    t = np.arange(n) / SR
    out = _circ(_noise2(rng, n, .6), "band", 180, 1100) * (.6 + .4 * _pmod(rng, n, 2, 5))[:, None] * .25
    for _ in range(4):                                                # dế: chuỗi 3-4 xung, chu kỳ khép vòng
        f = round(rng.uniform(3800, 5200) * T) / T
        cnt = max(1, round(T / rng.uniform(.45, .9)))
        per = T / cnt
        gate = np.zeros((n, 2))
        m = int(.018 * SR)
        off = rng.uniform(0, per)
        for j in range(cnt):
            for p in range(int(rng.integers(3, 5))):
                _put(gate, np.hanning(m), int((off + j * per + p * .034) * SR))
        pan, g = rng.uniform(-.8, .8), rng.uniform(.05, .2)
        car = np.sin(2 * np.pi * f * t) * gate[:, 0] * g * (.7 + .3 * _pmod(rng, n, 1, 3))
        out[:, 0] += car * np.sqrt((1 - pan) / 2)
        out[:, 1] += car * np.sqrt((1 + pan) / 2)
    am = .5 + .5 * np.sin(2 * np.pi * round(45 * T) / T * t)          # ve sầu/muỗm nền rất nhỏ
    out += _circ(_noise2(rng, n, .3), "band", 5500, 8000) * am[:, None] * .05
    m = int(.35 * SR); tt = np.arange(m) / SR                          # ếch xa
    croak = sosfilt(_sos("band", 300, 900), (np.sin(2 * np.pi * 25 * tt) > .6) * rng.standard_normal(m)) * np.hanning(m)
    s = rng.uniform(0, 3)
    while s < T:
        _put(out, croak, int(s * SR), rng.uniform(-.6, .6), rng.uniform(.05, .12))
        s += rng.uniform(3, 7)
    return out


def _fire(rng, n):
    rumble = _circ(_noise2(rng, n, .7), "low", 0, 180) * (.8 + .2 * _pmod(rng, n, 2, 6))[:, None]
    roar = _circ(_noise2(rng, n, .5), "band", 200, 900) * (.5 + .5 * _pmod(rng, n, 20, 60, 4))[:, None]
    hiss = _circ(_noise2(rng, n, .2), "high", 3000)
    out = rumble * .6 + roar * .2 + hiss * .05
    imp = np.zeros((n, 2))
    for _ in range(int(n / SR * 7)):                                  # lách tách: 1-4 tiếng nổ nhỏ
        s = int(rng.integers(n)); c = int(rng.random() < .5)
        for k in range(int(rng.integers(1, 5))):
            m = int(rng.uniform(.0003, .0025) * SR)
            i = (s + int(k * rng.uniform(.004, .02) * SR)) % (n - m)
            imp[i:i + m, c] += rng.standard_normal(m) * min(rng.pareto(2.5) * .5, 3)
    out += _circ(imp, "band", 1500, 8000) * .6
    m = int(.015 * SR); tt = np.arange(m) / SR
    for _ in range(int(n / SR * .25)):                                # tiếng nổ củi to hơn
        _put(out, sosfilt(_sos("band", 300, 1500), rng.standard_normal(m)) * np.exp(-tt / .004), int(rng.integers(n)),
             rng.uniform(-.4, .4), rng.uniform(.4, .8))
    return out


def _cave(rng, n):
    room = _circ(_noise2(rng, n, .8), "low", 0, 120) * .5 + _circ(_noise2(rng, n, .8), "low", 0, 60) * .3
    air = _circ(_noise2(rng, n, .4), "band", 300, 1200) * .04
    drips = np.zeros((n, 2))
    m = int(.12 * SR); tt = np.arange(m) / SR
    s = rng.uniform(0, 1)
    while s < n / SR:
        f0 = rng.uniform(700, 1400)
        ph = 2 * np.pi * np.cumsum(f0 * (1 + .5 * (1 - np.exp(-tt / .01)))) / SR
        _put(drips, np.sin(ph) * np.exp(-tt / rng.uniform(.025, .06)), int(s * SR), rng.uniform(-.7, .7), rng.uniform(.3, 1))
        s += rng.uniform(1.2, 4.0)
    return room + air + drips * .25 + _creverb(drips, 1.1, rng, .04, 4000) * .6


SYNTH = {"rain": _rain, "wind": _wind, "forest": _forest, "river": _river, "temple_bell_far": _temple_bell_far,
         "market": _market, "night_insects": _night_insects, "fire": _fire, "cave": _cave}


# ---------------------------------------------------------------- nguồn file CC0/PD (tuỳ chọn)
def file_sources(root: Path | None = None) -> dict:
    """assets/ambience/sources.json -> {kind: info}; chỉ nhận CC0/PD, khác thì dừng hẳn."""
    p = (root or ROOT) / "assets" / "ambience" / "sources.json"
    if not p.is_file():
        return {}
    reg = json.loads(p.read_text(encoding="utf-8"))
    for k, info in reg.items():
        if k not in KINDS or k == "none":
            raise ValueError(f"hf_ambience: sources.json có loại lạ '{k}'")
        lic = str(info.get("license", "")).strip().lower()
        if lic not in ALLOWED_LICENSES:
            raise ValueError(f"hf_ambience: '{k}' giấy phép '{info.get('license')}' -- chỉ nhận CC0 / Public Domain")
        if not info.get("source"):
            raise ValueError(f"hf_ambience: '{k}' thiếu 'source' (URL trang gốc) -- không dùng nguồn không rõ")
    return reg


def source_of(kind: str, root: Path | None = None) -> dict:
    reg = file_sources(root)
    if kind in reg and ((root or ROOT) / "assets" / "ambience" / reg[kind]["file"]).is_file():
        i = reg[kind]
        return {"nguon": f"{i['file']} -- {i['source']}" + (f" ({i['author']})" if i.get("author") else ""),
                "giay_phep": i["license"]}
    return SOURCES[kind]


def _file_tile(path: Path, n: int, variant: int) -> np.ndarray:
    """Một ô tuần hoàn từ bản thu: cắt đoạn thứ `variant`, khép vòng bằng chồng mờ equal-power đuôi -> đầu."""
    with tempfile.TemporaryDirectory() as td:
        o = Path(td) / "a.f32"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ar", str(SR), "-ac", "2", "-f", "f32le", str(o)],
                       check=True)
        a = np.fromfile(o, dtype="float32").reshape(-1, 2).astype("float64")
    X = int(JOIN_S * SR)
    if len(a) < n + X:
        a = np.concatenate([a] * int(np.ceil((n + X) / max(1, len(a)))))
    off = (variant * (len(a) // N_VARIANTS)) % max(1, len(a) - n - X + 1)
    y = a[off:off + n + X]
    out = y[:n].copy()
    r = (np.arange(X) / X * np.pi / 2)[:, None]
    out[:X] = y[:X] * np.sin(r) + y[n:n + X] * np.cos(r)
    return out


# ---------------------------------------------------------------- ô / nền dài
def _kind_seed(kind: str, seed: int, variant: int) -> int:
    return int.from_bytes(hashlib.sha1(f"{kind}|{seed}|{variant}".encode()).digest()[:4], "little")


@lru_cache(maxsize=12)
def tile(kind: str, seed: int = 11, variant: int = 0) -> np.ndarray:
    """Một ô TILE_S giây (n, 2) float32, tuần hoàn (lặp chính nó không có mối), RMS = TILE_RMS."""
    if kind not in SYNTH:
        raise ValueError(f"hf_ambience: loại '{kind}' không có -- dùng {', '.join(KINDS)}")
    n = int(TILE_S * SR)
    reg = file_sources()
    if kind in reg and (FILE_DIR / reg[kind]["file"]).is_file():
        x = _file_tile(FILE_DIR / reg[kind]["file"], n, variant)
    else:
        x = SYNTH[kind](np.random.default_rng(_kind_seed(kind, seed, variant)), n)
    x = x - x.mean(axis=0, keepdims=True)
    x *= TILE_RMS / (np.sqrt((x ** 2).mean()) + 1e-12)
    pk = np.abs(x).max()
    if pk > .5:                       # sự kiện quá nhọn (chuông, củi nổ): hạ cả ô, mức cuối vẫn đặt theo LUFS
        x *= .5 / pk
    return x.astype("float32")


def bed_slice(kind: str, i0: int, i1: int, seed: int = 11) -> np.ndarray:
    """Mẫu [i0, i1) của nền `kind` đặt theo THỜI GIAN TUYỆT ĐỐI (cùng loại ở hai đoạn kề nhau đọc cùng tín hiệu).
    Các ô nối nhau theo bước TILE-JOIN, biến thể luân phiên j % 3, chồng mờ equal-power JOIN_S."""
    n, X = int(TILE_S * SR), int(JOIN_S * SR)
    S = n - X
    out = np.zeros((max(0, i1 - i0), 2), dtype="float32")
    if i1 <= i0:
        return out
    r = np.arange(X, dtype="float32") / X * (np.pi / 2)
    fin, fout = np.sin(r)[:, None], np.cos(r)[:, None]
    for j in range(max(0, (i0 - X) // S), (i1 - 1) // S + 1):
        a = j * S
        lo, hi = max(a, i0), min(a + n, i1)
        if hi <= lo:
            continue
        seg = tile(kind, seed, j % N_VARIANTS).copy()
        if j:
            seg[:X] *= fin
        seg[-X:] *= fout
        out[lo - i0:hi - i0] += seg[lo - a:hi - a]
    return out


@lru_cache(maxsize=32)
def tile_lufs(kind: str, seed: int = 11) -> float:
    from hf_foley import lufs  # noqa: PLC0415
    return float(lufs(tile(kind, seed, 0)))


# ---------------------------------------------------------------- khai báo -> đoạn
def chapters_of(lines: list[dict]) -> list[int]:
    """Chương của từng dòng: 0 = trước thẻ chương đầu; dòng tiêu đề mở chương mới."""
    out, ch = [], 0
    for ln in lines:
        ch += bool(ln.get("heading"))
        out.append(ch)
    return out


def _entry_ok(e: dict) -> str | None:
    if not isinstance(e, dict):
        return "mục ambience phải là object"
    if e.get("kind") not in KINDS:
        return f"kind '{e.get('kind')}' không có (dùng {'|'.join(KINDS)})"
    if "gain_db" in e and not isinstance(e["gain_db"], (int, float)):
        return "gain_db phải là số"
    if "chapter" in e and ("from" in e or "to" in e):
        return "khai chapter HOẶC from/to, không cả hai"
    return None


def assign(lines: list[dict], entries: list[dict]) -> list[tuple[str, float] | None]:
    """(loại, gain_db) cho từng dòng. Ưu tiên cảnh (from/to) > chương > cả video; cùng mức khai sau thắng."""
    chs = chapters_of(lines)
    sid = [int(ln["sentence_id"]) for ln in lines]
    best: list[tuple[int, int, tuple[str, float]] | None] = [None] * len(lines)
    for order, e in enumerate(entries or []):
        if _entry_ok(e):
            continue
        val = (e["kind"], float(np.clip(float(e.get("gain_db", 0.0)), *GAIN_RANGE)))
        if "from" in e or "to" in e:
            a, b, pr = int(e.get("from", sid[0] if sid else 1)), int(e.get("to", sid[-1] if sid else 1)), 2
            hit = [a <= s <= b for s in sid]
        elif "chapter" in e:
            pr = 1
            hit = [c == int(e["chapter"]) for c in chs]
        else:
            pr = 0
            hit = [True] * len(lines)
        for i, h in enumerate(hit):
            if h and (best[i] is None or (pr, order) >= best[i][:2]):
                best[i] = (pr, order, val)
    return [b[2] if b else None for b in best]


def segments(lines: list[dict], entries: list[dict], duration: float) -> list[dict]:
    """Đoạn liền nhau [{s0, s1, kind, gain_db}] phủ kín 0..duration (kind 'none' = không nền)."""
    if not lines or not entries:
        return []
    val = assign(lines, entries)
    zs = [0.0] + [max(0.0, float(ln["start"]) - LEAD_S) for ln in lines[1:]] + [float(duration)]
    out: list[dict] = []
    for i, v in enumerate(val):
        kind, g = v if v else ("none", 0.0)
        if out and out[-1]["kind"] == kind and out[-1]["gain_db"] == g:
            out[-1]["s1"] = zs[i + 1]
        else:
            out.append({"s0": zs[i], "s1": zs[i + 1], "kind": kind, "gain_db": g})
    return [s for s in out if s["s1"] > s["s0"]]


def _ramp(x: np.ndarray, equal_power: bool) -> np.ndarray:
    x = np.clip(x, 0, 1)
    return np.sin(x * np.pi / 2) if equal_power else x


def layer(lines: list[dict], spec: dict, voice: np.ndarray | None, voice_lufs: float, duration: float,
          seed: int = 11, music_gap: float = 18.0) -> tuple[np.ndarray, list[str]]:
    """Lớp ambience stereo (N, 2) float32 đã đặt mức, đã lùi theo giọng, đã dâng nhẹ trong khoảng lặng.
    Trả (lớp, các loại thực sự phát)."""
    N = int(duration * SR)
    amb = np.zeros((N, 2), dtype="float32")
    segs = segments(lines, spec.get("ambience") or [], duration)
    if not segs:
        return amb, []
    L_v = voice_lufs if np.isfinite(voice_lufs) and voice_lufs > -70 else -23.0
    gap = float(spec.get("amb_gap", AMB_GAP))
    cap = L_v - float(music_gap) - UNDER_MUSIC
    X = int(XFADE_S * SR)
    used = []
    for k, s in enumerate(segs):
        if s["kind"] == "none":
            continue
        prev = segs[k - 1]["kind"] if k else None
        nxt = segs[k + 1]["kind"] if k + 1 < len(segs) else None
        a, b = int(s["s0"] * SR), int(s["s1"] * SR)
        i0 = max(0, a - X // 2) if k else 0
        i1 = min(N, b + X // 2) if nxt is not None else N
        if i1 <= i0:
            continue
        idx = np.arange(i0, i1)
        env = np.ones(i1 - i0, dtype="float32")
        if k:
            env *= _ramp((idx - (a - X / 2)) / X, prev != s["kind"])
        else:
            env *= np.clip(idx / SR / 1.0, 0, 1)                        # vào nhẹ 1 s ở đầu video
        if nxt is not None:
            env *= _ramp(((b + X / 2) - idx) / X, nxt != s["kind"])
        else:
            env *= np.clip((N - idx) / SR / 2.0, 0, 1)                  # ra 2 s ở cuối
        target = min(L_v - gap + s["gain_db"], cap)
        g = _db(target - tile_lufs(s["kind"], seed))
        amb[i0:i1] += bed_slice(s["kind"], i0, i1, seed) * (env * g)[:, None]
        used.append(s["kind"])
    if voice is not None and len(voice):
        from hf_foley import envelope  # noqa: PLC0415
        v = voice if voice.ndim == 1 else voice.mean(axis=1)
        e = envelope(np.pad(v, (0, max(0, N - len(v))))[:N])
        amb *= (1 - (1 - _db(-float(spec.get("amb_duck_db", AMB_DUCK_DB)))) * e).astype("float32")[:, None]
    sw = _db(float(spec.get("amb_swell_db", SWELL_DB)))
    if sw != 1.0:
        for w in silence_windows(lines, spec, duration):
            m = _window_mask(N, w["a"] - .3, w["b"] + .3, .3)
            amb *= (1 + (sw - 1) * m).astype("float32")[:, None]
    return amb, list(dict.fromkeys(used))


# ---------------------------------------------------------------- nhịp: lặng / nhấn
def parse_beats(spec: dict) -> list[dict]:
    out = []
    raw = spec.get("beats") or {}
    items = raw if isinstance(raw, list) else raw.items() if isinstance(raw, dict) else []
    for item in items:
        if isinstance(raw, list):
            k, v = (item.get("sid", 1), item) if isinstance(item, dict) else (1, item)
        else:
            k, v = item
        d = {"beat": v} if isinstance(v, str) else dict(v or {})
        sid = d.get("sid")
        if sid is None:
            m = re.match(r"^(\d+)", str(k))
            sid = int(m.group(1)) if m else None
        if sid is None:
            continue
        d["sid"] = int(sid)
        d.setdefault("beat", "silence")
        if d["beat"] == "silence":
            d["dur"] = float(d.get("dur", SILENCE_DEFAULT))
            d.setdefault("at", "before")
            d["hold"] = bool(d.get("hold", False))
        out.append(d)
    return sorted(out, key=lambda d: d["sid"])


def silence_windows(lines: list[dict], spec: dict, duration: float) -> list[dict]:
    """Khoảng lặng thật [a, b] (không giọng) cho mỗi beat silence. `short` > 0: khoảng nghỉ TTS hẹp hơn khai báo."""
    by = {int(ln["sentence_id"]): i for i, ln in enumerate(lines)}
    out = []
    for d in parse_beats(spec):
        if d["beat"] != "silence" or d["sid"] not in by:
            continue
        i = by[d["sid"]]
        ln = lines[i]
        dur = float(np.clip(d["dur"], *SILENCE_DUR))
        if d["at"] == "after":
            a = float(ln["end"]) + .03
            lim = float(lines[i + 1]["start"]) - .03 if i + 1 < len(lines) else float(duration)
            b = min(lim, a + dur)
            rel = b
        else:
            b = float(ln["start"]) - .02
            lim = float(lines[i - 1]["end"]) + .03 if i else 0.0
            a = max(lim, b - dur)
            rel = float(ln["end"]) if d["hold"] else b
        if b - a < .05:
            continue
        out.append({"sid": d["sid"], "a": a, "b": b, "rel": rel, "dur": dur, "short": round(max(0.0, dur - (b - a)), 3)})
    return out


def _window_mask(N: int, a: float, b: float, ramp: float) -> np.ndarray:
    """1 trong [a, b], dốc cos `ramp` giây hai bên, 0 ngoài."""
    t = np.arange(N) / SR
    up = np.clip((t - (a - ramp)) / ramp, 0, 1)
    dn = np.clip(((b + ramp) - t) / ramp, 0, 1)
    return (.5 - .5 * np.cos(np.pi * np.minimum(up, dn))).astype("float32")


def music_gain(lines: list[dict], spec: dict, duration: float) -> np.ndarray | None:
    """Hệ số nhân cho NHẠC: 0 trong khoảng lặng (tắt trước FADE_OUT_S, về lại RETURN_S), lùi nhẹ trước phát nhấn."""
    ws, hs = silence_windows(lines, spec, duration), hit_times(lines, spec)
    if not ws and not hs:
        return None
    N = int(duration * SR)
    t = np.arange(N) / SR
    g = np.ones(N, dtype="float32")
    for w in ws:
        down = np.clip((w["a"] - t) / FADE_OUT_S, 0, 1)                # 1 -> 0 tới mốc a
        up = np.clip((t - w["rel"]) / RETURN_S, 0, 1)                  # 0 -> 1 từ mốc rel
        shape = np.where(t < w["a"], down, np.where(t <= w["rel"], 0.0, up))
        g *= (.5 - .5 * np.cos(np.pi * shape)).astype("float32")
    dip = _db(-HIT_DIP_DB)
    for th, _ in hs:
        pre = np.clip((t - (th - .6)) / .5, 0, 1)
        post = np.clip(((th + 1.2) - t) / 1.2, 0, 1)
        m = np.where(t < th, pre, post) * ((t > th - .6) & (t < th + 1.2))
        g *= (1 - (1 - dip) * m).astype("float32")
    return g


def fx_gate(lines: list[dict], spec: dict, duration: float) -> np.ndarray | None:
    """Hệ số cho tiếng động / nền trầm: tắt hẳn trong khoảng lặng (dốc 0,1 s)."""
    ws = silence_windows(lines, spec, duration)
    if not ws:
        return None
    N = int(duration * SR)
    g = np.ones(N, dtype="float32")
    for w in ws:
        g *= 1 - _window_mask(N, w["a"], w["b"], .1)
    return g


def hit_times(lines: list[dict], spec: dict) -> list[tuple[float, float]]:
    """[(giây, gain_db)] cho mỗi beat hit: đầu câu (-0,02 s) hoặc lúc đọc `word` (cùng luật when() của longform.js)."""
    by_sid = {int(ln["sentence_id"]): ln for ln in lines}
    out = []
    for d in parse_beats(spec):
        if d["beat"] != "hit" or d["sid"] not in by_sid:
            continue
        ln = by_sid[d["sid"]]
        t = float(ln["start"]) + float(d.get("offset", -0.02))
        key = (d.get("word") or "").replace("**", "").strip().lower()
        if key:
            for w in ln.get("words") or []:
                w_str = (w.get("w") or w.get("word") or "").replace("**", "").strip().lower()
                if key in w_str:
                    t = float(w.get("t", w.get("start", t)))
                    break
        out.append((max(0.0, t), float(d.get("gain_db", 0.0))))
    return out


def hit_signal(seed: int = 11) -> np.ndarray:
    """Một phát nhấn trầm (mono, đỉnh 1): sub hạ cao độ 68 -> 38 Hz + thân trống trầm ~82/180 Hz + tiếng da ngắn.
    Thân trống để loa điện thoại (không ra < 100 Hz) vẫn nghe thấy."""
    rng = np.random.default_rng(seed)
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    att = 1 - np.exp(-t / .004)
    sub = np.sin(2 * np.pi * np.cumsum(38 + 30 * np.exp(-t / .12)) / SR) * np.exp(-t / .7)
    drum = (np.sin(2 * np.pi * np.cumsum(82 + 25 * np.exp(-t / .05)) / SR) * np.exp(-t / .35)
            + .35 * np.sin(2 * np.pi * 180 * t) * np.exp(-t / .12))
    thump = sosfilt(_sos("low", 0, 220), rng.standard_normal(n)) * np.exp(-t / .05) * .8
    skin = sosfilt(_sos("band", 300, 1200), rng.standard_normal(n)) * np.exp(-t / .02) * .15
    s = (sub + .8 * drum + thump) * att + skin
    s *= np.minimum(1, (t[-1] - t) / .3)
    return s / (np.abs(s).max() + 1e-12)


def hits(lines: list[dict], spec: dict, duration: float, ref_peak: float, seed: int = 11) -> np.ndarray | None:
    """Lớp phát nhấn (N, 2): đỉnh = đỉnh giọng + HIT_REL_DB + gain_db."""
    hs = hit_times(lines, spec)
    if not hs:
        return None
    N = int(duration * SR)
    out = np.zeros((N, 2), dtype="float32")
    sig = hit_signal(seed)
    for th, gdb in hs:
        i = int(th * SR)
        k = min(len(sig), N - i)
        if k > 0:
            out[i:i + k] += (sig[:k] * max(ref_peak, .05) * _db(HIT_REL_DB + gdb))[:, None]
    return out


# ---------------------------------------------------------------- plan
def tts_with_beats(row: dict) -> dict | None:
    """Spec TTS có khoảng nghỉ đủ cho beat silence: before -> nghỉ sau câu trước, after -> nghỉ sau chính câu.
    Không có beat silence -> trả nguyên row['tts'] (khoá TTS/băm kịch bản của plan cũ không đổi)."""
    tts = row.get("tts")
    sil = [d for d in parse_beats(row) if d["beat"] == "silence"]
    if not tts or not sil:
        return tts
    out = json.loads(json.dumps(tts))
    pauses = {str(k): float(v) for k, v in (out.get("pauses") or {}).items()}
    for d in sil:
        key = d["sid"] - 1 if d["at"] == "before" else d["sid"]
        if key < 1:
            continue
        need = round(float(np.clip(d["dur"], *SILENCE_DUR)) + .25, 2)
        pauses[str(key)] = max(pauses.get(str(key), 0.0), need)
    out["pauses"] = pauses
    return out


def sound_spec(row: dict, record_ledger: bool = True) -> dict:
    """`sound` của row + `ambience`/`beats` cấp row -> spec cho hf_foley.mix_long / hf_sound.mix_long_c."""
    spec = dict(row.get("sound") or {})
    for k in ("ambience", "beats"):
        if row.get(k):
            spec[k] = row[k]
    amb_entries = spec.get("ambience")
    if record_ledger and amb_entries and row.get("id"):
        kinds = sorted({e.get("kind") for e in amb_entries if isinstance(e, dict) and e.get("kind") in KINDS} - {"none"})
        if kinds:
            record(row["id"], row.get("series", ""), row.get("day", ""), kinds)
    return spec


def issues(row: dict) -> list[str]:
    """Lỗi khai báo (chặn render): loại lạ, chương/câu ngoài kịch bản, beat lạ, lặng ngoài 0,5-2 s."""
    script = row.get("script") or []
    n = len(script)
    n_ch = sum(1 for t in script if t.startswith("**") and t.endswith("**") and t.count("**") == 2)
    out = []
    for e in row.get("ambience") or []:
        why = _entry_ok(e)
        if why:
            out.append(f"ambience {e}: {why}")
            continue
        if "chapter" in e and not 0 <= int(e["chapter"]) <= n_ch:
            out.append(f"ambience chapter {e['chapter']}: kịch bản chỉ có chương 0..{n_ch}")
        for key in ("from", "to"):
            if key in e and not 1 <= int(e[key]) <= n:
                out.append(f"ambience {key}={e[key]}: ngoài 1..{n}")
        if "from" in e and "to" in e and int(e["from"]) > int(e["to"]):
            out.append(f"ambience from {e['from']} > to {e['to']}")
    if row.get("ambience") and row.get("sound") is None:
        out.append("có ambience nhưng row không có `sound` (đường trộn 4 lớp) -- ambience sẽ không phát")
    for k, v in (row.get("beats") or {}).items():
        m_sid = re.match(r"^(\d+)", str(k))
        if not m_sid or not 1 <= int(m_sid.group(1)) <= n:
            out.append(f"beats '{k}': số câu ngoài 1..{n}")
            continue
        d = {"beat": v} if isinstance(v, str) else (v or {})
        b = d.get("beat", "silence")
        if b not in BEATS:
            out.append(f"beats {k}: '{b}' không có (silence|hit)")
        elif b == "silence":
            dur = float(d.get("dur", SILENCE_DEFAULT))
            if not SILENCE_DUR[0] <= dur <= SILENCE_DUR[1]:
                out.append(f"beats {k}: silence {dur} s ngoài {SILENCE_DUR[0]}-{SILENCE_DUR[1]} s")
            if d.get("at", "before") not in ("before", "after"):
                out.append(f"beats {k}: at phải là before|after")
            if d.get("at", "before") == "before" and int(k) == 1:
                out.append("beats 1: silence 'before' câu 1 không có khoảng nghỉ trước -- dùng at=after")
    return out


# ---------------------------------------------------------------- sổ nguồn
def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}


def record(rid: str, series: str, day: str, kinds: list[str]) -> None:
    d = ledger()
    d[rid] = {"series": series, "day": day, "kinds": kinds, "sources": {k: source_of(k) for k in kinds}}
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def measure(path: Path) -> dict:
    """LUFS tích hợp, true peak (dBTP), LRA bằng ffmpeg ebur128."""
    res = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True)
    err = res.stderr or ""
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    lra = re.findall(r"LRA:\s+(-?[\d.]+) LU", err)
    tp = re.findall(r"True peak:\s+Peak:\s+(-?[\d.inf]+) dBFS", err)
    return {"lufs": float(i[-1]) if i else float("nan"), "lra": float(lra[-1]) if lra else float("nan"),
            "tp": float(tp[-1]) if tp else float("nan")}


def main() -> int:
    cmd, *rest = sys.argv[1:] or ["help"]
    if cmd == "library":
        for k in KINDS:
            if k != "none":
                s = source_of(k)
                print(f"  {k:16s} {s['giay_phep']:28s} {s['nguon']}")
    elif cmd == "preview":
        import soundfile as sf  # noqa: PLC0415
        kind, sec, out = rest[0], float(rest[1]), Path(rest[2])
        x = bed_slice(kind, 0, int(sec * SR))
        sf.write(out, x / max(1e-9, np.abs(x).max()) * .5, SR)
        print(out)
    elif cmd == "check":
        plan = json.loads(Path(rest[0]).read_text(encoding="utf-8"))
        rows = plan if isinstance(plan, list) else plan.get("rows", [plan])
        only = rest[rest.index("--only") + 1] if "--only" in rest else None
        bad = 0
        for r in rows:
            if only and r.get("id") != only:
                continue
            p = issues(r)
            bad += bool(p)
            print(f"{r.get('id')}: {'ĐẠT' if not p else 'LỖI'}")
            for x in p:
                print("  !", x)
        return 1 if bad else 0
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
