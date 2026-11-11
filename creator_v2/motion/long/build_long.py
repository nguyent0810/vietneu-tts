"""Dựng video DÀI 16:9 từ spec theo chương: giọng đọc -> mốc từng từ -> ảnh/video -> HTML -> render -> âm thanh -> ghép.

    python motion/long/build_long.py <topic> tts                # đọc hết các chương (cache theo từng câu), in thời lượng
    python motion/long/build_long.py <topic> html [chNN ...]    # dựng data.js + composition (không render)
    python motion/long/build_long.py <topic> render [chNN ...] [--draft]
    python motion/long/build_long.py <topic> final              # nối các chương + nhạc nền + loudnorm -> final.mp4

Spec: data/long/<topic>/spec.json (chung: title, accent, acc, imgs{key: "File:..."}, geo{name: {...}}, chapters[])
      data/long/<topic>/chNN.json (mỗi chương: hud{k,t}, bgm{file, at, gain}, lines[], scenes[]).
Một câu (line) là chuỗi, hoặc {"t": "...", "p": giây_nghỉ_sau}. Nghỉ mặc định 0.32s, sau câu hỏi 0.6s.
Mốc thời gian trong scenes giống motion/stier/build.py: i = đầu câu i; [i, "từ", n, lệch]; số thực = giây tuyệt đối.
Cảnh có "vid": "<id Pexels>" (+ "ms" giây bắt đầu trong clip) -> thẻ <video> nướng tĩnh vào HTML.
Ảnh Commons nhận PD/CC0/CC BY/CC BY-SA (không NC/ND); ghi công tự động vào credits.json cho mô tả video.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
import shutil
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HF = ROOT / "motion" / "hf"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "motion"))
sys.path.insert(0, str(ROOT / "motion" / "stier"))
sys.path.insert(0, str(HERE))
from factory.render_lock import render_lock  # noqa: E402

import hf_align  # noqa: E402
import hf_geo  # noqa: E402
import build as BLD  # noqa: E402
from build import Anchors, resolve, norm  # noqa: E402  (cùng cú pháp mốc với Short S-tier)

BLD.ANCHORS |= {"sumAt", "zeroAt", "titleAt", "hAt", "countAt", "hitAt", "typeAt", "burnAt", "decodeAt", "endAt", "voiceAt", "voiceEnd", "startAt", "statAt", "fwdAt", "backAt", "drawAt",
                "chipAt", "medianAt", "hlAt", "colorAt", "strikeAt",
                "modulesAt", "modulesUntil", "scanAt", "okAt", "crashAt", "tickAt", "selAt", "rowAt",
                "truthAt", "sealAt", "litAt"}   # lab.js qr/flap (12/10/2026)      # mốc riêng của cảnh video dài (breadth/basket theme chart; strikeAt: fx strike)
BLD.ANCHOR_LISTS |= {"flips", "readAt"}
import floor  # noqa: E402
import branch_gate  # noqa: E402
import long_output as LO  # noqa: E402  (ghi nguyên tử + manifest final, GH-170)
import lint_html  # noqa: E402
import sfx_long  # noqa: E402
import long_ambience as LAMB  # noqa: E402  (spec "ambience": lớp nền không gian dưới giọng + nhạc, trộn ở final)
import chartdata  # noqa: E402
import scene_params  # noqa: E402
import cine_auto  # noqa: E402
import clip_sheet  # noqa: E402
import img_sheet  # noqa: E402
import channel_table  # noqa: E402

# ffmpeg: FFMPEG_DIR, rồi bản vendor của máy sản xuất, rồi ffmpeg trong PATH (máy khác).
_FF_VENDOR = r"C:\Tools\Youtuber\video-editor\vendor\ffmpeg"
FF = (os.environ.get("FFMPEG_DIR") or (_FF_VENDOR if os.path.isdir(_FF_VENDOR) else None)
      or os.path.dirname(shutil.which("ffmpeg") or "") or _FF_VENDOR)
FFMPEG = FF + r"\ffmpeg.exe"
VOICE = "Anh Khôi"
QUOTE_VOICE = "Minh Đức"     # câu {"q": 1}: lời trích nguyên văn/diễn ý, giọng khác + lọc radio
VOICE2 = None                 # spec "voice2": giọng thứ hai cho câu {"q": 1}; None = giọng trích của kênh như cũ
VOICE2_RADIO = True           # voice2 vẫn qua lọc radio, trừ khi voice2 {"radio": false}
VOICE2_DEFAULT = "Thanh Bình"  # voice2 không ghi "voice": giọng đã dùng cho hồ sơ CL (factory/lines/cl.py), khác hẳn Anh Khôi
ASK_VOICE = None              # câu {"ask": 1}: "người hỏi" chen ngang (câu hỏi của người xem) -- giọng khác, KHÔNG lọc radio
UA = {"User-Agent": "yt-factory/1.0 (documentary research; contact via channel)"}
FREE = re.compile(r"public domain|^pd|cc0|no restrictions|^cc by(-sa)? ?\d|^cc-by|^attribution$", re.I)   # "Attribution" = {{PD-LosAlamos}}/{{Attribution}}: chỉ buộc ghi nguồn, không SA (23/10/2026)
# mastering giọng đọc (đã duyệt ở bản thử Mafia): cắt ù, bớt đục 200Hz, sáng 3.2kHz, khử xì, nén nhẹ.
# Chỉ áp ở bước trộn — mốc chữ vẫn lấy từ voice.wav thô. spec "master": false để tắt (Yakuza đã đăng bản thô).
VOICE_FX = ("highpass=f=70,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.4:g=2.5,deesser=i=0.4,"
            "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2")
TAIL = 0.9          # giây thở cuối mỗi chương
_engine = None


def paths(topic):
    return ROOT / "data" / "long" / topic, ROOT / "output" / "long" / topic


def _refuse_unreviewed_sheets(topic):
    """Dấu QA chỉ hợp lệ khi đúng với ảnh/clip mà scenes hiện đang dùng."""
    data, out = paths(topic)
    checks = (("clip", clip_sheet.clip_uses(data), clip_sheet.uses_hash, clip_sheet.ok_path(out),
               f"python motion/long/clip_sheet.py {topic}"),
              ("ảnh", img_sheet.image_uses(data), img_sheet.uses_hash, img_sheet.ok_path(out),
               f"python motion/long/img_sheet.py {topic}"))
    problems = []
    for kind, uses, hash_fn, mark, command in checks:
        if not uses:
            continue
        actual = mark.read_text(encoding="utf-8").strip() if mark.exists() else ""
        if actual != hash_fn(uses):
            state = "thiếu dấu" if not actual else "dấu đã cũ (cảnh đã đổi sau khi soát)"
            problems.append(f"{kind}: {state}. Chạy `{command}`, mở tờ soát, rồi chạy `{command} --ok`.")
    if problems:
        raise SystemExit("chặn render: chưa soát asset\n  " + "\n  ".join(problems))


SAY_EXACT = {}
SAY = {}   # chữ hiển thị -> cách đọc cho TTS (spec["say"]); phụ đề vẫn giữ chữ gốc


def _channels() -> dict:
    sys.path.insert(0, str(ROOT / "motion" / "stier"))
    import themes
    table = {}
    for code, profile in channel_table.load_long_profiles().items():
        voice = profile["voice_profile"]["tham_so"]
        theme = profile.get("theme") or {}
        row = {"voice": voice["dan"], "quote": voice["trich"]}
        if voice.get("hoi"):
            row["ask"] = voice["hoi"]
        # CL deliberately has no theme.long, matching the legacy CL row.
        if theme.get("long"):
            row["theme"] = theme["long"]
            row["brand"] = theme["brand"]
            row["accent"] = profile["typography"]["mau_nhan"]
        if theme.get("pools"):
            row["pools"] = themes.THEMES[theme["pools"]]["pools"]
        if profile.get("anh", {}).get("cam_sa"):
            row["no_sa"] = True
        if voice.get("fx"):
            row["voice_fx"] = getattr(themes, voice["fx"])
        table[code] = row
    return table


CHAN: dict = {}


def license_allowed(lic: str) -> bool:
    if not FREE.search(lic) or re.search(r"\bNC\b|\bND\b|fair use", lic, re.I):
        return False
    return not (CHAN.get("no_sa") and re.search(r"by-sa|\bsa\b", lic, re.I))


def _is_ai_image(key, spec: dict, od: Path) -> bool:
    """Nhận diện asset AI để áp luật hiển thị riêng cho MIM/CK.

    Tên ``aiNN`` giữ tương thích với các helper cũ; manifest trong spec và
    sidecar là bằng chứng khi key không theo tên đó.
    """
    if not isinstance(key, str):
        return False
    if re.fullmatch(r"ai\d+", key, re.I):
        return True
    if str((spec.get("imgs") or {}).get(key, "")).startswith("EXT:ai"):
        return True
    sidecar = od / "img" / f"{key}.json"
    try:
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(meta, dict) and str(meta.get("file", "")).startswith("EXT:ai")


def _scene_image_keys(scene: dict):
    """Các khóa ảnh mà một cảnh Long có thể dùng, không tính video."""
    yield scene.get("img")
    yield scene.get("bg")
    for part in (scene.get("a"), scene.get("b")):
        if isinstance(part, dict):
            yield part.get("img")
    for pin in scene.get("pins") or []:
        if isinstance(pin, dict):
            yield pin.get("img")


def strip_ai_illustration_labels(spec: dict, chs, od: Path) -> bool:
    """Bỏ ``illus`` chỉ khỏi cảnh AI của MIM/CK, giữ nguyên credit và CL."""
    if spec.get("channel") not in {"MIM", "CK"}:
        return False
    changed = False
    for _, chapter in chs:
        for scene in chapter.get("scenes") or []:
            if "illus" in scene and any(_is_ai_image(key, spec, od) for key in _scene_image_keys(scene)):
                scene.pop("illus")
                changed = True
    return changed


def is_legacy_topic(topic):
    """Topic có từ trước 12/11/2026 giữ hành vi cũ (#275). Không có danh sách (ROOT tạm trong test) = coi là cũ."""
    path = ROOT / "data" / "long" / "_legacy_topics.json"
    if not path.exists() or not (ROOT / "data" / "long" / topic / "spec.json").exists():
        return True   # topic giả trong test (spec dựng trong bộ nhớ / thư mục tạm) giữ hành vi cũ
    return topic in json.loads(path.read_text(encoding="utf-8"))


def apply_long_defaults(topic, spec, chapters=()):
    """Apply new-topic defaults in memory, never rewrite an existing spec."""
    if is_legacy_topic(topic):
        return spec
    channel = spec.get("channel", "CL")
    spec.setdefault("opening_gate", True)
    spec.setdefault("cine_auto", True)
    spec.setdefault("idcards", True)
    spec.setdefault("voice2", {"voice": "Ngọc Huyền" if channel == "CL" else _channels()[channel]["quote"], "radio": True})
    ambience = []
    if channel == "CL":
        for name, chapter in chapters:
            text = " ".join(line_text(line) for line in chapter.get("lines", [])).lower()
            kind = next((kind for words, kind in [(("mưa", "rain"), "rain"), (("gió", "wind"), "wind"), (("côn trùng",), "night_insects")] if any(w in text for w in words)), None)
            if kind:
                ambience.append({"chapter": name, "kind": kind})
    spec.setdefault("ambience", ambience)
    return spec


def mix_levels(topic, channel, spec=None):
    defaults = {"gain": .16, "threshold": .03, "ratio": 6.0, "ambience_db": 0.0} if is_legacy_topic(topic) else {"gain": .17, "threshold": .05, "ratio": 4.0, "ambience_db": 15.0}
    defaults.update((spec or {}).get("mix_levels", {}).get(channel, {}))
    return defaults


def load(topic):
    global VOICE, QUOTE_VOICE, ASK_VOICE, VOICE2, VOICE2_RADIO
    sd, od = paths(topic)
    spec = json.loads((sd / "spec.json").read_text(encoding="utf-8"))
    spec["channel"] = channel_table.resolve_long_channel(spec)
    chs = [(c, json.loads((sd / f"{c}.json").read_text(encoding="utf-8"))) for c in spec["chapters"] if (sd / f"{c}.json").exists()]
    apply_long_defaults(topic, spec, chs)
    CHAN.clear()
    CHAN.update(_channels()[spec["channel"]])
    VOICE, QUOTE_VOICE, ASK_VOICE = CHAN["voice"], CHAN["quote"], CHAN.get("ask")
    v2 = spec.get("voice2")
    VOICE2 = (v2.get("voice") or VOICE2_DEFAULT) if isinstance(v2, dict) else None
    VOICE2_RADIO = bool(v2.get("radio", True)) if isinstance(v2, dict) else True
    THEME["name"] = spec.get("theme", CHAN.get("theme", ""))
    BEAT2["on"] = bool(spec.get("beat2"))
    SAY.clear()
    SAY_EXACT.clear()
    for k, v in (spec.get("say") or {}).items():   # "=Di": khớp ĐÚNG hoa/thường (tránh "di cư" thành "Đi cư")
        (SAY_EXACT.__setitem__(k[1:], v) if k.startswith("=") else SAY.__setitem__(k.lower(), v))
    strip_ai_illustration_labels(spec, chs, od)
    return spec, chs, od


def line_text(x):
    return x["t"] if isinstance(x, dict) else x


def _core(tok):
    m = re.match(r"^([\"“(]*)(.*?)([\"”)…,.;:?!]*)$", tok)
    return m.group(1), m.group(2), m.group(3)


def spoken(text: str) -> str:
    out = []
    for tok in text.split():
        a, c, z = _core(tok)
        out.append(a + SAY_EXACT.get(c, SAY.get(c.lower(), c)) + z)
    return " ".join(out)


def line_pause(x):
    if isinstance(x, dict) and "p" in x:
        return x["p"]
    t = line_text(x).rstrip()
    return 0.6 if t.endswith("?") else 0.45 if t.endswith("…") else 0.32


# ---------------- giọng đọc: cache THEO CÂU (sửa một câu không phải đọc lại cả chương) ----------------
def _key(text: str, take: int = 0, voice: str = VOICE) -> str:
    """take 0 giữ đúng hash cũ (cache Yakuza còn dùng được); take k>0 là bản đọc lại khác của cùng câu."""
    return hashlib.sha1((voice + "|" + text + (f"|t{take}" if take else "")).encode("utf-8")).hexdigest()[:16]


def line_voice(x) -> str:
    if isinstance(x, dict) and x.get("ask") and ASK_VOICE:
        return ASK_VOICE
    if isinstance(x, dict) and x.get("q"):
        return VOICE2 or QUOTE_VOICE       # voice2 vắng -> đúng giọng trích cũ (khoá cache không đổi)
    return VOICE


def radio(a, sr):
    """Lời trích: băng thông điện thoại/radio cũ 300-3400 Hz -> tách hẳn khỏi giọng kể."""
    from scipy.signal import butter, sosfilt
    sos = butter(4, [300, 3400], btype="bandpass", fs=sr, output="sos")
    return (sosfilt(sos, a) * 1.4).astype("float32")


def _wav_ok(p: Path) -> bool:
    """Cache hit hợp lệ: header khớp kích thước thật, giải mã được, không rỗng, hữu hạn (GH-170)."""
    import numpy as np
    import soundfile as sf
    if not LO.wav_complete(p):
        return False
    try:
        a, _ = sf.read(str(p), dtype="float32")
    except Exception:       # noqa: BLE001  (soundfile ném RuntimeError/LibsndfileError)
        return False
    return len(a) > 0 and bool(np.isfinite(a).all())


def tts_line(text: str, cache: Path, take: int = 0, voice: str = VOICE):
    import numpy as np
    import soundfile as sf
    global _engine
    p = cache / f"{_key(text, take, voice)}.wav"
    if p.exists() and not _wav_ok(p):
        print(f"  ! TTS cache dở/hỏng, đọc lại: {p.name}", flush=True)
    if not p.exists() or not _wav_ok(p):
        from factory import integrity, speak as SP
        integrity.require_speakable(text)    # trước engine VÀ trước cache: câu hỏng không được lưu lại
        if _engine is None:
            _engine = SP._load_engine()
        a = _engine.infer(text, voice=voice)     # vieneu 3.8.3: "Anh Khôi" là alias của "Thiện Minh" (cùng embedding)
        cache.mkdir(parents=True, exist_ok=True)
        LO.sweep_temps(p)
        temp = LO.temp_path(p)
        try:
            sf.write(str(temp), a, SP.SAMPLE_RATE)
            info = sf.info(str(temp))
            if (not LO.wav_complete(temp) or info.frames != len(a) or len(a) == 0
                    or info.samplerate != SP.SAMPLE_RATE or not np.isfinite(np.asarray(a)).all()):
                raise ValueError("TTS trả về âm thanh rỗng, thiếu mẫu hoặc sai tần số; không lưu cache")
            LO.publish(temp, p, "tts")
        finally:
            temp.unlink(missing_ok=True)
    return sf.read(str(p), dtype="float32")


def _picks(cache: Path) -> dict:
    f = cache / "picks.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def speak(ch_lines, od: Path, name: str) -> dict:
    import numpy as np
    import soundfile as sf
    picks = _picks(od / "tts")       # câu nào đã chấm best-of-N thì dùng bản thắng, chưa chấm thì take 0
    parts, segs, cur, sr0 = [], [], 0.0, None
    for i, x in enumerate(ch_lines):
        sp, v = spoken(line_text(x)), line_voice(x)
        a, sr = tts_line(sp, od / "tts", picks.get(_key(sp, 0, v), 0), v)
        if isinstance(x, dict) and x.get("q") and (VOICE2_RADIO or not VOICE2):   # chỉ lời TRÍCH mới lọc radio; giọng "người hỏi" để tự nhiên
            a = radio(a, sr)
        sr0 = sr
        d = len(a) / sr
        segs.append({"index": i, "text": line_text(x), "start": round(cur, 3), "end": round(cur + d, 3),
                     **({"ask": 1} if isinstance(x, dict) and x.get("ask") else {})})
        gap = np.zeros(int(line_pause(x) * sr), dtype="float32")
        parts += [a, gap]
        cur += d + len(gap) / sr
    parts.append(np.zeros(int(TAIL * sr0), dtype="float32"))
    wav = od / name / "voice.wav"
    wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(wav), np.concatenate(parts), sr0)
    return {"duration": round(cur + TAIL, 3), "segments": segs}


# ---------------- best-of-N: đọc mỗi câu N lần, Whisper nghe lại, chọn bản khớp chữ nhất ----------------
# vieneu không tất định: cùng câu mỗi lần đọc một khác, đôi khi đọc sai số ("57" -> "27") hay nuốt chữ.
#   1) build_long.py <topic> takes [N=3]      (venv vieneu)  -> tts/takes.json
#   2) stt_takes.py <topic>                   (.venv-video, CUDA) -> tts/transcripts.json
#   3) build_long.py <topic> pick             (venv vieneu)  -> tts/picks.json, rồi chạy lại `tts`
def do_takes(topic, n=3, only=None):
    spec, chs, od = load(topic)
    cache, rows, t0 = od / "tts", [], time.time()
    for name, ch in chs:
        if only and name not in only:
            continue
        for x in ch["lines"]:
            sp, v = spoken(line_text(x)), line_voice(x)
            files = []
            for k in range(n):
                tts_line(sp, cache, k, v)
                files.append(f"{_key(sp, k, v)}.wav")
            rows.append({"key": _key(sp, 0, v), "ch": name, "text": sp, "files": files})
        print(f"{name}: {len(ch['lines'])} câu x{n} ({time.time() - t0:.0f}s)", flush=True)
    LO.atomic_write_text(cache / "takes.json", json.dumps(rows, ensure_ascii=False, indent=1), "takes.json")
    print(f"takes.json: {len(rows)} câu")


def _chars(text: str, nz) -> str:
    """So theo KÝ TỰ, bỏ khoảng trắng/dấu câu: tên Ý Whisper viết dính ("Capachy" ~ "Ca pa chi") chỉ lệch 1-2 ký tự,
    còn đọc sai số ("hai mươi bảy" thay "năm mươi bảy") vẫn lệch rõ."""
    return "".join(re.findall(r"[^\W_]+", nz.normalize(text).lower()))


def _edit(a, b) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def do_pick(topic):
    """Lỗi = khoảng cách sửa theo KÝ TỰ / độ dài (cả hai phía qua cùng bộ chuẩn hoá của vieneu: số -> chữ).
    Hoà thì chọn bản có độ dài gần trung vị nhất (tránh bản kéo lê / đọc vội)."""
    import soundfile as sf
    from vieneu_utils.phonemize_text import PuncNormalizer
    nz = PuncNormalizer()
    spec, chs, od = load(topic)
    cache = od / "tts"
    rows = json.loads((cache / "takes.json").read_text(encoding="utf-8"))
    hyp = json.loads((cache / "transcripts.json").read_text(encoding="utf-8"))
    picks, bad, gain = _picks(cache), [], 0
    for r in rows:
        ref = _chars(r["text"], nz)
        sc = []
        for k, f in enumerate(r["files"]):
            if f not in hyp:
                continue
            e = _edit(ref, _chars(hyp[f], nz)) / max(1, len(ref))
            sc.append((k, e, sf.info(str(cache / f)).duration))
        if not sc:
            continue
        med = sorted(d for _, _, d in sc)[len(sc) // 2]
        k, e, _ = min(sc, key=lambda z: (round(z[1], 3), abs(z[2] - med)))
        gain += sc[0][1] > e
        picks[r["key"]] = k
        if e > 0.08:
            bad.append((r["ch"], e, r["text"], hyp[r["files"][k]]))
    LO.atomic_write_text(cache / "picks.json", json.dumps(picks, indent=1), "picks.json")
    print(f"picks.json: {len(picks)} câu; {gain} câu bản 0 kém hơn bản được chọn")
    for ch, e, t, h in sorted(bad, key=lambda z: -z[1]):
        print(f"  ! {ch} {e:.0%}\n    viết: {t}\n    nghe: {h}")


def word_lines(t: dict, wav: Path) -> list[dict]:
    env, hop = hf_align.energy_envelope(wav)
    out = []
    for seg in t["segments"]:
        toks = seg["text"].split()
        wts = [sum(hf_align.token_weight(y) for y in spoken(x).split()) for x in toks]   # chữ đọc khác -> trọng số theo cách đọc
        times = hf_align.word_times(env, hop, seg["start"], seg["end"], wts)
        out.append({"text": seg["text"], "start": seg["start"], "end": seg["end"], **({"ask": 1} if seg.get("ask") else {}),
                    "words": [{"w": x, "t": a, "d": d} for x, (a, d) in zip(toks, times)]})
    return out


# ---------------- ảnh Commons (dùng tự do, có ghi công) ----------------
def fetch_img(file: str, dst: Path, credits: dict) -> dict:
    from PIL import Image
    meta = dst.with_suffix(".json")
    if file.startswith("EXT:") and not (dst.exists() and meta.exists()):   # ảnh ngoài Commons: tải trước bằng media_search.py
        raise SystemExit(f"{file}: chưa có {dst.name} — chạy motion/long/media_search.py get/sat trước")
    if not dst.exists() or not meta.exists():
        def info(width=None):
            prm = {"action": "query", "prop": "imageinfo", "titles": file, "iiprop": "url|size|extmetadata", "format": "json", "formatversion": "2"}
            if width:
                prm["iiurlwidth"] = width
            with urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(prm), headers=UA), timeout=60) as r:
                return json.loads(r.read())["query"]["pages"][0]["imageinfo"][0]
        for k in range(6):
            try:
                ii = info()
                Wd = next((w for w in (1920, 1280, 960, 500, 330) if w < ii["width"]), None)   # bản gốc bị 429 -> thumb cỡ chuẩn
                if Wd:
                    ii = info(Wd)
                md = ii.get("extmetadata", {})
                lic = md.get("LicenseShortName", {}).get("value", "")
                if not license_allowed(lic):
                    raise SystemExit(f"{file}: giấy phép '{lic}' không dùng được cho kênh này")
                artist = re.sub(r"<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip()[:120]
                url = ii.get("thumburl") or ii["url"]
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                    raw = r.read()
                break
            except SystemExit:
                raise
            except Exception as e:
                if k == 5:
                    raise
                time.sleep(4 * (k + 1) + (10 if "429" in str(e) else 0))
        im = Image.open(io.BytesIO(raw))
        if im.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", im.size, (255, 255, 255)); im = im.convert("RGBA"); bg.paste(im, mask=im.split()[-1]); im = bg
        im = im.convert("RGB")
        if max(im.size) > 2400:
            im.thumbnail((2400, 2400))
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, quality=90)
        meta.write_text(json.dumps({"file": file, "license": lic, "artist": artist}, ensure_ascii=False), encoding="utf-8")
        time.sleep(1.0)
    m = json.loads(meta.read_text(encoding="utf-8"))
    if not re.search(r"public domain|^pd|cc0|no restrictions", m["license"], re.I):
        credits[file] = m
    with Image.open(dst) as im:
        return {"w": im.size[0], "h": im.size[1], "lic": m["license"], "by": m.get("artist", ""),
                "pd": bool(re.search(r"public domain|^pd|cc0|no restrictions", m["license"], re.I))}


def probe_dur(p: Path) -> float:
    r = subprocess.run([FF + r"\ffprobe.exe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


def probe_color(p: Path) -> dict:
    """color_transfer / primaries / matrix của stream hình. Lỗi ffprobe nằm ở khóa ``_error``."""
    r = subprocess.run(
        [FF + r"\ffprobe.exe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=color_transfer,color_primaries,color_space",
         "-of", "json", str(p)],
        capture_output=True, text=True)
    if r.returncode != 0 or not (r.stdout or "").strip():
        return {"_error": (r.stderr or "ffprobe không trả màu").strip()[-240:]}
    try:
        streams = json.loads(r.stdout).get("streams") or []
    except json.JSONDecodeError:
        return {"_error": "ffprobe trả JSON hỏng"}
    return streams[0] if streams else {}


def collect_html_lint(topic: str, only=None) -> list[str]:
    """Con dấu, tiêu đề thẻ, clip HDR. Chương chưa có giọng thì bỏ qua (bước html sẽ báo thiếu file)."""
    spec, chs, od = load(topic)
    problems: list[str] = []
    seen: set[str] = set()
    geo_pins: dict = {}   # toạ độ ghim trên sân khấu, cho kiểm tra nhãn bản đồ zoom
    for g, v in (spec.get("geo") or {}).items():
        hf_geo.BOX = tuple(v.get("box", (180, 130, 1740, 850)))
        geo_pins[g] = {p["name"]: (p["x"], p.get("label", "")) for p in hf_geo.bake({"countries": [], "bbox": v["bbox"], "pins": v["pins"]})["_geo"]["pins"]}
    for name, ch in chs:
        if only and name not in only:
            continue
        tj, wav = od / name / "timing.json", od / name / "voice.wav"
        if not tj.exists() or not wav.exists():
            continue
        t = json.loads(tj.read_text(encoding="utf-8"))
        d = float(t["duration"])
        scenes = plan(ch, word_lines(t, wav), d)
        ec = spec.get("endcard", 0) if name == spec["chapters"][-1] else 0
        if ec:
            scenes.append({"type": "endcard", "t0": d, "t1": d + ec, "bg": spec.get("endcardBg"),
                           "sub": spec.get("endcardSub", "HỒ SƠ TIẾP THEO")})
        problems.extend(lint_html.check_scenes(name, scenes, geo_pins))
        problems.extend(lint_html.kinetic_problems(name, scenes, variety.LOOKS[spec.get("look") or "classic"]["sans"][0], variety.LOOKS[spec.get("look") or "classic"].get("kw", 1.0)))
        for i, s in enumerate(scenes):
            if not s.get("vid"):
                continue
            vid = str(s["vid"])
            if vid in seen:
                continue
            src = od / "broll" / f"{vid}.mp4"
            if not src.exists():
                continue
            seen.add(vid)
            msg = lint_html.hdr_problem(name, i, vid, probe_color(src))
            if msg:
                problems.append(msg)
            wh = subprocess.run([FF + chr(92) + "ffprobe.exe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                 "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip().split(",")
            if len(wh) == 2 and wh[0].isdigit() and int(wh[1]) > int(wh[0]):   # clip quay dọc tràn khung 16:9 sẽ mất 2/3 hình
                problems.append(f"{name} cảnh {i}: clip {vid} quay dọc ({wh[0]}x{wh[1]}), sẽ bị cắt trên khung ngang — đổi clip ngang")
    return problems


def _refuse_html_lint(topic: str, only=None) -> None:
    bad = collect_html_lint(topic, only)
    if bad:
        raise SystemExit("html lint:\n  " + "\n  ".join(bad))


# ---------------- beat text: motion/beatfx.py chọn hiệu ứng chữ (engine/beat.js), dùng chung với Short ----------------
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from beatfx import assign_beats as _assign_beats  # noqa: E402
import variety  # noqa: E402  (nhạc nền theo mood + diện mạo riêng từng video, chống "repetitive content")
THEME = {"name": ""}
BEAT2 = {"on": False}    # spec "beat2": true -> bố cục cảnh chữ + từ nhấn + giới hạn sync (PM 09/10/2026). Video cũ: tắt, y hệt từng byte.


def assign_beats(sc: list[dict], ch: dict, lines: list[dict] | None = None) -> None:
    pools = CHAN.get("pools")
    if pools and pools.get("sync") and lines:   # MIM: dòng lớn được đọc trọn -> hiện từng chữ theo giọng
        from beatfx import apply_sync
        apply_sync(sc, lines, every=3 if BEAT2["on"] else 1, max_lead=1.2 if BEAT2["on"] else None)
    _assign_beats(sc, THEME["name"] + "|" + ch.get("title", ""), pools=pools)
    if BEAT2["on"]:
        from beatfx import assign_layouts, layout_items, pick_em, pull_main
        pull_main(sc)
        assign_layouts(sc, THEME["name"] + "|" + ch.get("title", ""))
        layout_items(sc)
        pick_em(sc)


# ---------------- kế hoạch cảnh ----------------
def plan(ch: dict, lines: list[dict], dur: float) -> list[dict]:
    A = Anchors(lines)
    sc = []
    for i, s in enumerate(ch["scenes"]):
        r = resolve({k: v for k, v in s.items() if k != "at"}, A)
        r["t0"] = 0.0 if i == 0 else A(s["at"])
        sc.append(r)
    for i, r in enumerate(sc):
        r["t1"] = sc[i + 1]["t0"] if i + 1 < len(sc) else dur
        if r["t1"] <= r["t0"] + 0.6:
            if i + 1 < len(sc):     # lỗi nằm ở mốc "at" của cảnh SAU, không phải cảnh bị báo (retro 3 mục 13: "cảnh 0 (chapter) quá ngắn" ×3)
                nxt = ch["scenes"][i + 1]
                why = (f" — cảnh {i + 1} ({nxt.get('type')}) neo at={nxt.get('at')!r} trùng mốc với cảnh {i}"
                       + (" (thẻ chương luôn bắt đầu ở 0): neo cảnh sau vào câu 1 hoặc một từ ≥ 0,6 s sau đầu câu 0" if i == 0 and r["type"] == "chapter" else ""))
            else:
                why = " — cảnh cuối chạm hết chương"
            raise ValueError(f"cảnh {i} ({r['type']}) quá ngắn: {r['t0']:.2f}-{r['t1']:.2f}{why}")
        t0, t1, ty = r["t0"], r["t1"], r["type"]
        if ty == "candles":            # dữ liệu nến + chỉ báo tính ở Python (motion/long/chartdata.py), JS chỉ vẽ
            chartdata.attach(r)
        if ty == "race":
            chartdata.attach_race(r)
        if ty in ("breadth", "basket"):   # độ rộng / treemap vốn hoá HOSE (chartdata.attach_breadth / attach_basket)
            r.setdefault("drawAt", round(t0 + 0.4, 3))
            r.setdefault("until", round(max(r["drawAt"] + 0.3, min(t1 - 0.8, r["drawAt"] + (2.4 if ty == "breadth" else 2.2))), 3))
            if ty == "breadth" and r.get("animate"):
                r["animate"].setdefault("at", round(r["until"] + 0.4, 3))
                r["animate"].setdefault("until", round(max(r["animate"]["at"] + 0.5, min(t1 - 0.6, r["animate"]["at"] + 4)), 3))
            (chartdata.attach_breadth if ty == "breadth" else chartdata.attach_basket)(r)
        if ty == "date":
            if sum(c.isalpha() for c in r["date"]) > 1:   # mỗi ký tự không phải số là ô 44px -> chữ chồng nhau ("GIỮA 2027", CK E6 23/10/2026)
                print(f"  ! WARNING cảnh date '{r['date']}': chữ cái trong 'date' chồng nhau — để chữ vào 'day' (vd day 'GIỮA NĂM', date '2027')")
            r.setdefault("dayAt", t0 + 0.15)
            ng = len("".join(c if c.isdigit() else " " for c in r["date"]).split())
            r.setdefault("groupAt", [t0 + 0.4 + 0.3 * g for g in range(ng)])
            if isinstance(r.get("sub"), str):   # engine đọc sub.text/sub.at; chuỗi trần hiện chữ "undefined" (retro 23/10/2026: CK E4/E5/E6)
                r["sub"] = {"text": r["sub"], "at": round(r["groupAt"][-1] + 0.6 if r["groupAt"] else t0 + 0.6, 3)}
        if ty == "quote":
            if "typeAt" in r:
                r["at"] = r.pop("typeAt")
            r.setdefault("at", t0 + 0.45)
            r.setdefault("typeDur", round(min(len(r["text"]) * 0.035, (t1 - r["at"]) * 0.75), 3))
        if ty == "counter":
            if "countAt" in r:
                r["at"] = r.pop("countAt")
            r.setdefault("at", t0 + 0.2)
            r.setdefault("until", round(r["at"] + min(1.8, (t1 - t0) * 0.6), 3))
        if ty == "map":
            for k, p in enumerate(r.get("pins") or []):
                p.setdefault("at", round(t0 + 0.5 + 0.35 * k, 3))
            for q in r.get("routes") or []:
                q.setdefault("until", round(q["at"] + 1.0, 3))
        if ty == "slam":
            if "hitAt" in r:
                r["at"] = r.pop("hitAt")
            r.setdefault("at", round(t0 + 0.15, 3))
        if ty == "split":
            r["a"].setdefault("at", t0 + 0.15); r["b"].setdefault("at", t0 + 0.5)
            if r.get("sign"):
                r.setdefault("signAt", t0 + 0.9)
        if ty == "bars":
            for k, q in enumerate(r["items"]):
                q.setdefault("at", round(t0 + 0.4 + 0.35 * k, 3))
        if ty == "timeline":
            for k, q in enumerate(r["items"]):
                q.setdefault("at", round(t0 + 0.3 + 0.5 * k, 3))
        if ty == "org":
            for k, q in enumerate(r["nodes"]):
                q.setdefault("at", round(t0 + 0.3 + 0.3 * k, 3))
        if ty == "cards":
            r.setdefault("flips", [round(t0 + 0.8 + 0.5 * k, 3) for k in range(len(r["cards"]))])
        if ty in ("kinetic",) or r.get("kin"):
            for k, q in enumerate(r.get("items") or r.get("kin") or []):
                q.setdefault("at", round(t0 + 0.2 + 0.4 * k, 3))
        if ty == "print" and r.get("side"):
            for k, q in enumerate(r["side"].get("lines") or []):
                q.setdefault("at", round(t0 + 0.8 + 0.6 * k, 3))
        if ty == "quote" and r.get("qline") is not None:     # câu đọc giọng trích -> sóng âm chạy đúng lúc giọng vang
            q = lines[r["qline"]]
            r.setdefault("voiceAt", q["start"]); r.setdefault("voiceEnd", q["end"]); r["radio"] = True
        if ty == "seismo":
            r.setdefault("hitAt", round(t0 + 2.0, 3))
        if ty == "saint":
            r.setdefault("burnAt", round(t0 + 1.5, 3))
            r.setdefault("burnDur", round(max(1.5, min(4.5, t1 - r["burnAt"] - 0.4)), 3))
        if ty == "pizzini":
            for k, q in enumerate(r.get("notes") or []):
                q.setdefault("at", round(t0 + 0.5 + 1.2 * k, 3))
                q.setdefault("typeDur", round(min(len(q["text"]) * 0.045, 2.6), 3))
            if r.get("cipher"):
                r["cipher"].setdefault("at", round(t0 + 0.6, 3))
                r["cipher"].setdefault("decodeAt", round(r["cipher"]["at"] + 0.3 + 0.18 * len(r["cipher"]["word"]), 3))
        if ty == "dots":
            for k, q in enumerate(r.get("groups") or []):
                q.setdefault("at", round(t0 + 1.8 + 1.2 * k, 3))
        if ty == "board":
            for k, q in enumerate(r.get("pins") or []):
                q.setdefault("at", round(t0 + 0.3 + 0.45 * k, 3))
            for k, q in enumerate(r.get("links") or []):
                q.setdefault("at", round(t0 + 0.6 + 0.45 * k, 3))
        if ty == "memorial":
            for k, q in enumerate(r["names"]):
                q.setdefault("at", round(t0 + 0.8 + 0.7 * k, 3))
        if ty == "calendar":
            r.setdefault("endAt", round(t1 - 1.0, 3))
        if ty == "sticker":
            for k, q in enumerate(r["items"]):
                q.setdefault("at", round(t0 + 0.4 + 0.7 * k, 3))
        if ty == "file":
            for k, q in enumerate(r.get("rows") or []):
                q.setdefault("at", round(t0 + 0.9 + 0.5 * k, 3))
        if ty == "ledger":
            for k, q in enumerate(r.get("rows") or []):
                q.setdefault("at", round(t0 + 0.6 + 0.5 * k, 3))
        if ty in ("waterfall", "stack"):   # chart.js 27/10/2026: bước/cột chưa neo thì hiện lần lượt sau đầu cảnh
            if ty == "waterfall":
                r["start"].setdefault("at", round(t0 + 0.4, 3))
            for k, q in enumerate(r.get("steps" if ty == "waterfall" else "groups") or []):
                q.setdefault("at", round(t0 + 0.9 + 0.6 * k, 3))
            if ty == "waterfall" and r.get("end"):
                last = max([q["at"] for q in r.get("steps") or []] + [r["start"]["at"]])
                r["end"].setdefault("at", round(min(t1 - 0.5, last + 0.7), 3))
        if ty == "heat":
            r.setdefault("drawAt", round(t0 + 0.5, 3))
            r.setdefault("until", round(max(r["drawAt"] + 0.3, min(t1 - 1.2, r["drawAt"] + 0.35 * len(r["cells"]))), 3))
    assign_beats(sc, ch, lines)
    return sc


# ---------------- lint "chữ đầu tiên đến muộn" (retro 1 mục 4 -> lặp ở retro 2 mục 2 = LỖI QUY TRÌNH) ----------------
# Luật "neo dòng đầu vào từ ĐẦU câu" có từ 06/10 nhưng không có công cụ chặn -> D1 ×4, MIM #2 ×5 màn trống 1,7–4,2 s.
# Lint đọc chính danh sách cảnh sẽ nướng vào data.js: cảnh KHÔNG có nền (img/vid/bg) mà phần tử đầu tiên hiện > LATE_MAX
# giây sau đầu cảnh -> `html` cảnh báo, `render` từ chối (trừ khi --allow-late). Hiệu chỉnh 07/10 trên mim-ai-voice +
# ck-c2-phien-giao-dich: 0 cảnh vượt (kinetic sớm nhất ≤ 0,4 s; slam ≤ 0,76 s; counter ≤ 0,2 s).
LATE_MAX = 1.0
# Loại cảnh mà engine tự dựng khung/tiêu đề trong ≤ 0,5 s đầu cảnh, độc lập với mốc neo (casewide.js/lab.js/chart.js):
# thẻ chương, logo, màn kết, câu hỏi, giấy trích, sổ, khung biểu đồ (tiêu đề t0+0.1), cửa sổ chat, ảnh in/ảnh, hồ sơ, bản đồ.
FRAME_TYPES = {"chapter", "brand", "endcard", "question", "quote", "ledger", "bars", "chat", "print", "photo", "pano", "broll", "file",
               "candles", "race", "breadth", "basket", "book", "map", "guess", "nn", "go", "qr", "barcode", "flap", "captcha", "keyboard",
               "myth", "source", "units", "chess", "waterfall", "heat", "stack"}   # 3 cuối: lab.js (khung ≤ t0+0.2)
_NOT_START = {"t0", "t1", "until", "voiceEnd", "endAt", "typeDur", "burnDur", "dur"}
_DATA_LISTS = {"dots", "rects", "vals", "bars", "candles", "ohlc", "series", "cells", "keys"}     # mảng số liệu biểu đồ, không phải mốc


def unresolved_cues(o, path=""):
    """Mốc còn ở dạng [dòng, "từ", …] sau khi plan = khoá chưa khai trong BLD.ANCHORS -> engine nhận mảng thay vì giây.
    Retro 12/10/2026 (MIM "Mã QR"): modulesAt/hl/okAt của cảnh qr và crashAt của cảnh flap không được đổi ra giây,
    chấm đen không hiện, chữ "vẫn đọc được" hiện ngay đầu cảnh; qa_blank và freezedetect đều không bắt được."""
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k in _DATA_LISTS:
                continue
            if isinstance(v, list) and len(v) >= 2 and isinstance(v[0], int) and not isinstance(v[0], bool) and (v[1] is None or isinstance(v[1], str)):
                out.append(f"{path}.{k}={v}")
            else:
                out += unresolved_cues(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out += unresolved_cues(v, f"{path}[{i}]")
    return out


# Thẻ sổ (ledger): mỗi dòng là "khoá  giá trị" trên MỘT hàng, chữ JetBrains Mono (rộng 0,6 em), không xuống dòng.
# (ô trong, cỡ chữ dòng, cỡ chữ dòng tổng, khoảng cách, bề rộng tối thiểu của khoá tính theo em) -- lấy từ casewide.css.
# 15/10/2026: "chart" theo .th-chart .ledger .row 44px / tot 50px / gap 48 (trước ghi 34/40/24 -> B4 lọt dòng tràn thẻ)
LEDGER_BOX = {"lab": (1128, 46, 52, 48, 2.2), "chart": (1208, 44, 50, 48, 0), None: (968, 34, 40, 24, 0)}


def ledger_overflow(scenes, theme) -> list[str]:
    """Dòng sổ dài hơn ô -> khoá và giá trị đè lên nhau / tràn khỏi thẻ. Retro 4 (12/10/2026): MIM "Flappy Bird" đã upload với
    2 dòng như vậy (ch02, ch05); soi khung hình chỉ bắt được 1 dòng (ch04). Chốt: đo trước khi render, vượt là dừng."""
    box, fs, fst, gap, kmin = LEDGER_BOX.get(theme, LEDGER_BOX[None])
    out = []
    for k, sc in enumerate(scenes):
        if sc["type"] != "ledger":
            continue
        # The ledger has no clipping boundary of its own.  A row that reaches
        # #caps hides the subtitles even when every individual row fits.
        row_h, row_limit, caps_top = scene_params.LEDGER_LIMITS.get(theme, scene_params.LEDGER_LIMITS["default"])
        row_count = len(sc.get("rows") or []) + (1 if sc.get("total") else 0)
        if row_count > row_limit:
            out.append(f"ledger#{k} {row_count} dòng (rows + total) > {row_limit} (row {row_h}px, #caps y={caps_top}px)")
        for r in [*sc.get("rows", []), *([{**sc["total"], "tot": True}] if sc.get("total") else [])]:
            f = fst if r.get("tot") else fs
            w = (max(len(str(r.get("k", ""))) * 0.6, kmin) + len(str(r.get("v", ""))) * 0.6) * f + gap
            if w > box:
                out.append(f"ledger#{k} \"{r.get('k')} | {r.get('v')}\" ≈ {w:.0f}px > {box}px")
    return out


# Trang của công ty chứng khoán / ngân hàng / ví: không dẫn làm nguồn trên kênh CK (retro 15/10/2026: C5 dẫn dsc.com.vn).
CK_BRAND_DOMAINS = ("dsc.com.vn", "ssi.com.vn", "vndirect", "vps.com.vn", "tcbs", "hsc.com.vn", "mbs.com.vn", "vcbs", "bsc.com.vn",
                    "fpts", "kbsec", "kbsv", "mirae", "shs.com.vn", "techcombank", "vietcombank", "vietinbank",
                    "bidv", "agribank", "acb.com.vn", "vpbank", "mbbank", "tpbank", "sacombank", "hdbank", "momo", "zalopay")


def ck_source_brands(spec) -> list[str]:
    if (spec.get("channel") or "") != "CK":
        return []
    srcs = (spec.get("youtube") or {}).get("sources") or spec.get("sources") or []
    return [u for u in srcs if any(d in u.lower() for d in CK_BRAND_DOMAINS)]


def bars_collide(scenes) -> list[str]:
    """Tiêu đề biểu đồ (.bch .t 44px, trái) và chú thích (.bch .u 22px mono +.18em, phải) cùng một hàng 1620px, không xuống
    dòng -> dài là đè nhau. Retro 15/10/2026: B4 ch02, MIM khuôn mặt ch06 đè chữ; soi khung hình mới thấy."""
    out = []
    for k, sc in enumerate(scenes):
        if sc.get("title") and sc.get("unit") and sc["type"] in ("bars", "chart", "line"):
            w = len(sc["title"]) * 26.8 + len(sc["unit"]) * 17.1 + 24     # đo trên khung D3 ch02: 26.7 / 17.1 px mỗi ký tự, chừa 24px
            if w > 1620:
                out.append(f"{sc['type']}#{k} tiêu đề {len(sc['title'])} + chú thích {len(sc['unit'])} ký tự ≈ {w:.0f}px > 1620px")
        # Nhãn trục cột (.bk 24px mono +.1em, nowrap) trong ô 1620/n px: dài là đè nhãn cột bên (retro 23/10/2026: CK E5 ch01
        # "MỖI NGƯỜI PHỤ THUỘC · 2025" chồng nhãn 2026; A2 ch04 8 cột nhãn 16–22 ký tự).
        if sc["type"] == "bars" and sc.get("items"):
            slot, it = 1620 / len(sc["items"]), sc["items"]
            ws = [len(str(q.get("k", ""))) * 16.8 for q in it]          # đo trên khung E5 ch01: ~16,8 px mỗi ký tự
            for a in range(len(it) - 1):                                # hai nhãn kề nhau, mỗi nhãn canh giữa ô của nó
                if (ws[a] + ws[a + 1]) / 2 > slot - 16:
                    out.append(f"bars#{k} nhãn cột '{it[a].get('k')}' + '{it[a + 1].get('k')}' chồng nhau (ô {slot:.0f}px)")
            if ws and (ws[0] / 2 > slot / 2 + 140 or ws[-1] / 2 > slot / 2 + 140):   # nhãn đầu/cuối tràn mép khung
                out.append(f"bars#{k} nhãn cột đầu/cuối tràn mép khung")
    return out


def _starts(o, key=None):
    """Mọi mốc BẮT ĐẦU hiện (at, *At, flips, wt[0]) trong một cảnh đã plan."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k not in _NOT_START:
                yield from _starts(v, k)
    elif isinstance(o, list):
        if key in _DATA_LISTS:
            return
        if key == "wt":
            if o and isinstance(o[0], (int, float)):
                yield float(o[0])
            return
        for v in o:
            yield from _starts(v, key)
    elif isinstance(o, (int, float)) and not isinstance(o, bool) and key and (key == "at" or key.endswith("At") or key == "flips"):
        yield float(o)


def first_delay(s: dict) -> float | None:
    """Giây từ đầu cảnh tới lúc phần tử đầu tiên của cảnh hiện (theo cách engine dựng). None = không có mốc nào."""
    ts = [t for t in _starts(s) if t >= s["t0"] - 0.5]
    if not ts:
        return None
    d = min(ts) - s["t0"]
    if s["type"] == "kinetic" and d > 2.0:     # casewide.js B.kinetic: dòng đầu đến muộn > 2 s -> kéo về t0+0.5
        d = 0.5
    return d


def late_first(scenes: list[dict], ch: str = "", child_deadline: bool = True) -> list[str]:
    """Cảnh trống đầu: [chương, chỉ số cảnh, loại, độ trễ]. Counter: số đứng yên ở giá trị `from` (vd. "+0%") tới lúc đếm
    -> sai nghĩa dù có nền (retro 2 mục 3), nên soi cả khi có ảnh/clip."""
    out = []
    children = {
        "org": "nodes", "timeline": "items", "ledger": "rows", "file": "rows",
        # Kinetic lines are deliberately sequential narration, unlike the
        # independently meaningful children below.
        "dots": "groups", "board": "pins", "sticker": "items",
        "memorial": "names", "evidence": "callouts", "pizzini": "notes",
        "map": "pins", "split": None,
    }
    for i, s in enumerate(scenes):
        ty = s.get("type", "?")
        field = children.get(ty)
        parts = list(s.get(field) or []) if field else ([s.get("a"), s.get("b")] if ty == "split" else [])
        if ty == "ledger" and s.get("total"):
            parts.append(s["total"])
        if child_deadline and len(parts) >= 2:
            second = parts[1]
            at = second.get("at") if isinstance(second, dict) else None
            if isinstance(at, (int, float)) and not isinstance(at, bool) and at - s["t0"] > LATE_MAX:
                out.append(f"{ch} cảnh {i} {ty}: phần tử con thứ hai hiện sau {at - s['t0']:.1f}s — phải <= {LATE_MAX:.1f}s")
        if ty == "counter":
            d = s.get("at", s["t0"]) - s["t0"]
            if d > LATE_MAX:
                out.append(f"{ch} cảnh {i} counter: số đứng yên ở {s.get('prefix', '')}{s.get('from', 0)}{s.get('suffix', '')} "
                           f"{d:.1f}s rồi mới đếm (bỏ countAt hoặc neo vào từ đầu câu)")
            continue
        if ty in FRAME_TYPES or s.get("img") or s.get("vid") or s.get("bg"):
            continue
        d = first_delay(s)
        if d is not None and d > LATE_MAX:
            out.append(f"{ch} cảnh {i} {ty}: phần tử đầu tiên hiện sau {d:.1f}s — màn trống (neo dòng đầu vào từ ĐẦU câu, "
                       f"hoặc thêm nền img/bg)")
    return out


def late_report(topic, only=None) -> list[str]:
    """Đọc data.js đã dựng của các chương (sẽ render) -> danh sách cảnh trống đầu."""
    spec, chs, od = load(topic)
    out = []
    for name, _ in chs:
        f = od / name / "data.js"
        if only and name not in only:
            continue
        if not f.exists():      # `html` hỏng giữa chừng -> chương không có data.js; trước đây bị bỏ qua và báo "OK" (MIM #7 09/10)
            out.append(f"{name}: THIẾU data.js — `html` chưa dựng được chương này (xem lỗi của lệnh html)")
            continue
        case = json.loads(f.read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
        # Existing rendered data is kept as a baseline for the historical
        # blank-screen lint.  The stricter child rhythm gate is enforced in
        # do_html on every newly planned chapter.
        out += late_first(case["scenes"], name, child_deadline=False)
        if BEAT2["on"]:      # beat2: cả dòng CHÍNH cũng phải hiện sớm (late_first chỉ nhìn phần tử đầu tiên)
            from beatfx import light_start, overflow_lines
            out += light_start(case["scenes"], name)
            # tràn chữ vượt cả mức beat2.js tự co (40%) = chắc chắn cắt mép -> render từ chối như màn trống (retro 3 mục 15, LỖI QUY TRÌNH)
            out += [w for w in overflow_lines(case["scenes"], name) if "CẮT MÉP" in w]
    return out


# ---------------- lint mốc cảnh trùng thẻ chương (retro 3 mục 13: lặp 3 lần trong một ngày — MIM #6 ch04–07, D2 ch01–02, MIM #7 ch06) -------
# Thẻ chương (cảnh 0) luôn bắt đầu ở 0; cảnh 1 neo vào câu 0 / chữ đầu câu 0 -> cũng ở ~0 -> plan() báo "cảnh 0 (chapter) quá ngắn"
# giữa lúc `html` (sau TTS, sau khi tải ảnh, có khi trong chuỗi render). Lint TĨNH (không cần timing) chạy trước TTS và trước html,
# báo MỌI chương cùng lúc, nêu đúng cảnh cần sửa.
EARLY_WORDS = 2       # chữ thứ 1–2 của câu 0 (≈ < 0,6 s) coi là trùng mốc thẻ chương


def chapter_collisions(chs) -> list[str]:
    out = []
    for name, ch in chs:
        scenes, lines = ch.get("scenes") or [], ch.get("lines") or []
        if len(scenes) < 2 or scenes[0].get("type") != "chapter":
            continue
        at, bad = scenes[1].get("at"), False
        if isinstance(at, bool) or at is None:
            bad = at is None
        elif isinstance(at, int):
            bad = at == 0
        elif isinstance(at, float):
            bad = at < 0.6
        elif isinstance(at, list) and at and at[0] == 0:
            off = at[3] if len(at) > 3 else 0.0
            if len(at) < 2 or at[1] is None:
                bad = off < 0.6
            elif lines:
                ws = [norm(w) for w in line_text(lines[0]).split()]
                hits = [k for k, w in enumerate(ws) if w == norm(str(at[1]))]
                n = at[2] if len(at) > 2 else 0
                bad = n < len(hits) and hits[n] < EARLY_WORDS and off < 0.6
        if bad:
            out.append(f"{name} cảnh 1 ({scenes[1].get('type')}) neo at={at!r} trùng mốc 0 với thẻ chương (cảnh 0) — neo vào câu 1, "
                       f"hoặc một chữ từ thứ {EARLY_WORDS + 1} trở đi của câu 0")
    return out


def scene_gate(chs) -> None:
    bad = chapter_collisions(chs)
    if bad:
        raise SystemExit("lint cảnh (sửa gen_scenes.py rồi chạy lại):\n  " + "\n  ".join(bad))


def integrity_gate(chs, allow_repeat: bool = False) -> None:
    """Cổng toàn vẹn TRƯỚC TTS (retro 2 mục 16) — cùng luật với motion/long/script_lines.py, cho cả chNN.json sửa tay."""
    import script_lines
    bad = script_lines.gate([{"name": n, "lines": c["lines"]} for n, c in chs], allow_repeat)
    if bad:
        raise SystemExit("integrity: lời đọc chưa qua cổng, chưa đọc câu nào:\n  " + "\n  ".join(bad)
                         + "\n(câu lặp cố ý: thêm --allow-repeat-line)")


HTML = """<!doctype html>
<html lang="vi" data-resolution="landscape">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="{fonts}" rel="stylesheet" />
<link rel="stylesheet" href="assets/engine/casewide.css" />
<link rel="stylesheet" href="assets/engine/beat.css" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="{data}"></script>
</head>
<body>
<!-- Video dài: {title} — sinh bởi motion/long/build_long.py, đừng sửa tay. -->
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1920" data-height="1080" data-fps="30">
  <div class="layer" id="bed"></div>
{videos}
  <div class="layer" id="motes"></div>
  <div class="layer" id="stage"></div>
  <div class="layer" id="leak"></div>
  <svg class="layer" id="grain" width="1920" height="1080"><filter id="gn"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="7"/></filter><rect width="100%" height="100%" filter="url(#gn)"/></svg>
  <div class="layer" id="vig"></div>
  <div class="layer" id="scrims"></div>
  <div id="prog"><i></i></div>
  <div id="hud"><div class="bar"></div><div class="t"></div></div>
  <div id="caps"></div>
  <div class="layer" id="flash"></div>
</div>
<script src="assets/engine/beat.js"></script>
<script src="assets/engine/lab.js"></script>
<script src="assets/engine/chart.js"></script>
<script src="assets/engine/casewide.js"></script>
</body>
</html>
"""


B2_CSS = '<link rel="stylesheet" href="assets/engine/beat2.css" />\n'
B2_JS = '<script src="assets/engine/beat2.js"></script>\n'


def beat2_advice(spec: dict) -> str | None:
    """Kênh MIM/CK mà spec chưa bật beat2 -> engine chữ cũ (sync mờ chờ lời, khuôn lặp): MIM #5 09/10 có 9 đoạn trống ở QA final,
    phải bật beat2 rồi render lại (retro 3 mục 17). Chỉ nhắc (video cũ dựng lại giữ đúng hình cũ)."""
    if spec.get("channel") in ("MIM", "CK") and not spec.get("beat2"):
        return f"spec chưa bật \"beat2\": true (kênh {spec['channel']}) — engine chữ cũ gây màn trống/lặp khuôn (retro 3 mục 17)"
    return None


def html_for() -> str:
    """HTML của composition; beat2 bật -> thêm beat2.css (sau beat.css) + beat2.js (sau beat.js, trước casewide.js).
    beat2 tắt -> đúng HTML cũ từng byte (render_key của video cũ không đổi)."""
    if not BEAT2["on"]:
        return HTML
    h = HTML.replace('beat.css" />\n', 'beat.css" />\n' + B2_CSS, 1).replace('beat.js"></script>\n', 'beat.js"></script>\n' + B2_JS, 1)
    assert B2_CSS in h and B2_JS in h
    return h


def run(cmd, extra_env=None, **kw):
    env = os.environ.copy()
    env["PATH"] = FF + os.pathsep + env["PATH"]
    env.update(extra_env or {})
    return subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def do_tts(topic, only=None):
    spec, chs, od = load(topic)
    if not is_legacy_topic(topic):
        review_dir = ROOT / "data" / "long" / topic / "story_review"
        missing = [name for name, _ in chs if not (review_dir / f"{name}.md").is_file()]
        if missing:
            import warnings
            warnings.warn(f"STORY_REVIEW [{topic}] thiếu: {', '.join(missing)}", stacklevel=2)
    tot, rows = 0.0, []
    for name, ch in chs:
        if only and name not in only:
            continue
        t = speak(ch["lines"], od, name)
        (od / name / "timing.json").write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
        syl = sum(len(line_text(x).split()) for x in ch["lines"])
        rows.append((name, syl, t["duration"]))
        tot += t["duration"]
    for name, syl, d in rows:
        print(f"{name}: {syl:5d} âm tiết  {d / 60:5.2f} phút  ({syl / (d / 60):.0f}/phút)")
    print(f"TỔNG: {sum(r[1] for r in rows)} âm tiết, {tot / 60:.2f} phút")


def _refuse_craft(topic: str, spec: dict, chs) -> None:
    """Video mới ghi `"craft": true`. Video cũ không bật cờ, nên không bị chặn lại."""
    if not spec.get("craft"):
        return
    import craft
    import script_lines
    bad: list[str] = []
    md = ROOT / "data" / "long" / topic / "script.md"
    if md.exists():
        bad.extend(craft.audio_problems(script_lines.parse(md.read_text(encoding="utf-8"))))
    for name, ch in chs:
        if ch.get("scenes"):
            bad.extend(craft.graphic_problems(name, ch["scenes"]))
    if bad:
        raise SystemExit("craft:\n  " + "\n  ".join(bad))


def _refuse_opening(topic: str, spec: dict, allow: bool) -> None:
    """Video mới ghi `"opening_gate": true` (GH-228). `--allow-opening` bỏ qua có chủ ý."""
    if allow:
        return
    if not spec.get("opening_gate"):
        if not is_legacy_topic(topic):
            raise SystemExit('Long mới cần opening_gate: true; bỏ qua có chủ ý bằng --allow-opening')
        return
    import opening_gate
    bad = opening_gate.problems(topic)
    if bad:
        raise SystemExit("opening gate:\n  " + "\n  ".join(bad) + "\n(bỏ qua có chủ ý: --allow-opening)")


def _refuse_floor(topic: str, chs, channel: str) -> None:
    """Sàn sản xuất theo kênh; render thật/final không được bỏ qua kênh nào."""
    bad = floor.problems(chs, channel, topic)
    if bad:
        raise SystemExit(f"floor ({topic}): video này kém các Long đã đăng, không dựng bản thật:\n  " + "\n  ".join(bad))


def do_html(topic, only=None, allow_opening=False):
    _refuse_html_lint(topic, only)   # chặn trước khi tải ảnh và trộn tiếng
    spec, chs, od = load(topic)
    # ``plan()`` resolves cue aliases (hitAt/typeAt/countAt) before the engine
    # sees a scene. At this point only check image declarations; the complete
    # scene contract runs below on each planned scene.
    source_chapters = [(name, list(ch.get("scenes") or [])) for name, ch in chs if not only or name in only]
    if spec.get("endcard") and spec.get("endcardBg") and source_chapters and source_chapters[-1][0] == spec["chapters"][-1]:
        source_chapters[-1][1].append({"type": "endcard", "bg": spec["endcardBg"]})
    source_check = scene_params.validate_topic(
        source_chapters,
        spec.get("imgs") or {}, THEME["name"], check_scenes=False,
    )
    if source_check["errors"]:
        raise SystemExit("tham số cảnh:\n  " + "\n  ".join(source_check["errors"]))
    for warning in source_check["warnings"]:
        print(f"  ! WARNING tham số cảnh: {warning}", flush=True)
    _refuse_craft(topic, spec, chs)
    _refuse_opening(topic, spec, allow_opening)
    durs = {}
    for name, ch in chs:
        tj = od / name / "timing.json"
        durs[name] = json.loads(tj.read_text(encoding="utf-8"))["duration"] if tj.exists() else 150.0   # chương chưa đọc: ước lượng
    existing_panos = sum(s.get('type') == 'pano' for _, ch in chs for s in ch.get('scenes', []))
    # Each existing pano is at most 20 seconds; reserve that worst case so
    # auto-conversion cannot push the complete film above the duration floor.
    director = cine_auto.Director(topic, sum(durs.values()), existing_panos, 20 * existing_panos)
    cine_scenes = []
    cine_offset = 0.0
    credits = {}
    imgs = {}
    if beat2_advice(spec):
        print(f"  ! WARNING {beat2_advice(spec)}", flush=True)
    bad_src = ck_source_brands(spec)
    if bad_src:
        raise SystemExit("CK: nguồn trong mô tả là trang của công ty chứng khoán/ngân hàng (luật kênh: không tên thương hiệu): " + ", ".join(bad_src))
    variety.resolve_bgm(topic, spec, chs, od)   # bgm {"mood": ...} -> file cụ thể, tối thiểu trùng với video gần đây (retro 3 mục 9)
    look = variety.look(spec.get("look"))
    for key, file in spec.get("imgs", {}).items():
        wh = fetch_img(file, od / "img" / f"{key}.jpg", credits)
        imgs[key] = {"src": f"assets/long/{topic}/img/{key}.jpg", **wh}
    geo = {}
    for gname, g in (spec.get("geo") or {}).items():
        hf_geo.BOX = tuple(g.get("box", (180, 130, 1740, 850)))
        geo[gname] = hf_geo.bake({"countries": g["countries"], "context": g.get("context", []), "labels": g.get("labels", {}),
                                  "bbox": g["bbox"], "pins": g["pins"]})["_geo"]
    (od / "credits.json").write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    vdur = {}
    for name, ch in chs:
        d = durs[name]
        if only and name not in only:
            cine_offset += d
            continue
        t = json.loads((od / name / "timing.json").read_text(encoding="utf-8"))
        lines = word_lines(t, od / name / "voice.wav")
        scenes = plan(ch, lines, d)
        if spec.get('cine_auto'):
            amb = [e for e in spec.get('ambience') or [] if isinstance(e, dict) and (not e.get('chapter') or LAMB.chapter_name(e['chapter']) == name)]
            director.apply(scenes, imgs, cine_offset, ' '.join(line_text(x) for x in ch.get('lines', [])), amb)
            cine_scenes.extend(scenes)
        cine_offset += d
        ec = spec.get("endcard", 0) if name == spec["chapters"][-1] else 0
        if ec:   # 20 giây cuối cho end screen: kéo dài chương cuối, nhạc nền chạy tiếp rồi tắt dần
            scenes.append({"type": "endcard", "t0": d, "t1": d + ec, "bg": spec.get("endcardBg"),
                           "sub": spec.get("endcardSub", None if THEME["name"] == "lab" else "HỒ SƠ TIẾP THEO")})
            d = d + ec
        planned_check = scene_params.validate_topic([(name, scenes)], None, THEME["name"])
        if planned_check["errors"]:
            raise SystemExit("tham số cảnh:\n  " + "\n  ".join(planned_check["errors"]))
        for warning in planned_check["warnings"]:
            print(f"  ! WARNING tham số cảnh: {warning}", flush=True)
        pano_bad = scene_params.pano_speed_problems(name, scenes, imgs)
        if pano_bad:
            raise SystemExit("tham số cảnh:\n  " + "\n  ".join(pano_bad))
        late = late_first(scenes, name)
        if late:
            raise SystemExit("nhịp cảnh:\n  " + "\n  ".join(late))
        vids = []
        for k, s in enumerate(scenes):
            if s.get("vid"):
                vid = str(s["vid"])
                src = od / "broll" / f"{vid}.mp4"
                import mediafit
                if src.exists() and mediafit.decide(*mediafit.probe(src), 1920, 1080) == "blur":
                    fit = od / "broll" / f"{vid}fit.mp4"     # tên chỉ gồm số + "fit": khớp regex kiểm clip lúc render
                    if not fit.exists():
                        mediafit.fit_video(src, fit, 1920, 1080, seconds=600)
                        print(f"  mediafit: clip {vid} lệch khung ngang -> đặt trọn hình trên nền nhoè ({fit.name})")
                    src, vid = fit, f"{vid}fit"
                if vid not in vdur:
                    vdur[vid] = probe_dur(src)
                ms = float(s.get("ms", 0))
                need = s["t1"] - s["t0"] + 0.5
                if ms + need > vdur[vid] + 0.05:
                    raise SystemExit(f"{name} cảnh {k}: clip {vid} dài {vdur[vid]:.1f}s, cần {ms:.1f}+{need:.1f}s")
                s["vid"] = f"v{k}"
                tone = {"bw": "bw", "noir": "noir", "color": "color", "night": "night", "dim": "dimbg", "sepia": "sepia"}[s.get("tone", "night")]
                st = max(0.0, s["t0"] - 0.2)
                vids.append(f'  <video id="v{k}" class="clip bv {tone}" src="assets/long/{topic}/broll/{vid}.mp4" data-start="{st:.3f}" '
                            f'data-duration="{min(need, d - st):.3f}" data-media-start="{ms:.2f}" muted playsinline data-track-index="1"></video>')
        bad = [c for k, sc in enumerate(scenes) for c in unresolved_cues(sc, f"{sc['type']}#{k}")]
        if bad:
            raise SystemExit(f"{name}: mốc chưa đổi ra giây (thêm khoá vào BLD.ANCHORS): " + "; ".join(bad))
        # Retro 5 (14/10/2026): (a) "label" của cảnh bars/chart là thẻ góc dưới trái, đè lên nhãn trục (che chữ "MÁY", "99% THẮNG");
        # nguồn/ghi chú của biểu đồ đặt vào "unit". (b) counter có chữ số trong "prefix": số trung gian "1 / 7.698" đọc như dữ kiện thật.
        over = [f"{sc['type']}#{k}: label {sc['label'].get('k') or sc['label'].get('v')!r}" for k, sc in enumerate(scenes)
                if sc["type"] == "chart" and isinstance(sc.get("label"), dict)]   # bars: engine đã vẽ label thành dòng chú thích dưới tiêu đề
        if over:
            raise SystemExit(f"{name}: label đè nhãn trục biểu đồ (chuyển sang \"unit\"): " + "; ".join(over))
        pre = [f"counter#{k}: prefix {sc['prefix']!r}" for k, sc in enumerate(scenes)
               if sc["type"] == "counter" and any(c.isdigit() or c in "<>≈~" for c in str(sc.get("prefix") or "")) and sc.get("from", 0) != sc["to"]]
        if pre:   # retro 15/10/2026: thêm "<>≈~" cho khớp gate Shorts ("> 1.478 QUYẾT ĐỊNH" giữa chừng)
            raise SystemExit(f"{name}: counter có chữ số/dấu so sánh trong prefix (đặt \"from\" = \"to\" hoặc dùng kinetic): " + "; ".join(pre))
        tl = re.findall(r"~\s*\d[\d.,]*", json.dumps(scenes, ensure_ascii=False))
        if tl:    # retro 15/10/2026: "~120" trên màn hình đọc thành "-120"
            raise SystemExit(f"{name}: dấu ~ trước số dễ đọc thành dấu trừ (dùng ≈): " + ", ".join(tl))
        wide = ledger_overflow(scenes, THEME["name"])
        if wide:
            raise SystemExit(f"{name}: dòng sổ dài hơn thẻ (rút gọn khoá/giá trị): " + "; ".join(wide))
        bc = bars_collide(scenes)
        if bc:
            raise SystemExit(f"{name}: tiêu đề biểu đồ đè chú thích (rút gọn một trong hai): " + "; ".join(bc))
        seed = sum(ord(c) * (i + 1) for i, c in enumerate(topic + name)) % 100000 + 7
        # Chỉ mang ảnh được cảnh này tham chiếu (GH-21: ảnh của chương khác không làm đổi key).
        scene_text = json.dumps(scenes, ensure_ascii=False)
        chapter_imgs = {k: v for k, v in imgs.items() if json.dumps(k, ensure_ascii=False) in scene_text}
        chapter_index = spec["chapters"].index(name)
        case = {"topic": topic, "ch": name, "dur": d, "seed": seed, "accent": spec.get("accent", CHAN.get("accent", "#e2402d")), "look": look,
                "theme": THEME["name"] or None, **({"brand": CHAN["brand"]} if CHAN.get("brand") else {}), "autoTr": spec.get("autoTr", spec.get("theme") == "shanghai"), "hud": ch.get("hud", {}),
                "acc": spec.get("acc", []) + ch.get("acc", []), "lines": lines, "imgs": chapter_imgs, "geo": geo, "scenes": scenes,
                "prog0": chapter_index / len(spec["chapters"]), "prog1": (chapter_index + 1) / len(spec["chapters"])}
        (od / name / "data.js").write_text("window.CASE = " + json.dumps(case, ensure_ascii=False) + ";\n", encoding="utf-8")
        comp = HF / "compositions" / "long" / f"{topic}_{name}.html"
        comp.parent.mkdir(parents=True, exist_ok=True)
        comp.write_text(html_for().replace("{fonts}", variety.fonts_url(spec.get("look"))).replace("{data}", f"assets/long/{topic}/{name}/data.js").replace("{dur}", f"{d:.3f}")
                        .replace("{title}", spec["title"]).replace("{videos}", "\n".join(vids)), encoding="utf-8")
        sfx_long.build(case, od / name / "sfx.wav")
        quiet = [(s["t0"], s["t1"]) for s in scenes if s["type"] == "question"]
        quiet += [(s["at"] - 1.0, s["at"] + 0.4) for s in scenes if s["type"] == "slam" and spec.get("slamDrop", True)]
        quiet += [(s["t0"] - 0.2, s["t1"]) for s in scenes if s["type"] == "brand"]   # né nhạc nền cho âm hiệu kênh
        lift = [(s['t0'], s['t1']) for s in scenes if s['type'] == 'chapter'] if not is_legacy_topic(topic) else []
        mix_chapter(ch, od / name, d, quiet, spec.get("master", True), bgm_items(ch, lines, d), mix_levels(topic, spec['channel'], spec), not is_legacy_topic(topic), lift)
        print(f"{name}: {len(scenes)} cảnh, {len(vids)} clip, {d:.1f}s -> {comp.name}", flush=True)
        if spec.get('cine_auto'):
            print('  cine:', json.dumps(cine_auto.distribution(cine_scenes), ensure_ascii=False), flush=True)
            warning = floor.cine_warning(cine_scenes)
            if warning:
                print('  ! WARNING ' + warning, flush=True)
        for w in late_first(scenes, name):      # cảnh báo sớm; `render` sẽ từ chối nếu chưa sửa
            print(f"  ! WARNING màn trống đầu cảnh: {w}", flush=True)
        if BEAT2["on"]:
            from beatfx import light_start
            for w in light_start(scenes, name):
                print(f"  ! WARNING đầu cảnh chỉ có chữ nhỏ: {w}", flush=True)
        if BEAT2["on"]:    # tràn chữ beat2 (retro 3 mục 15: D2, C4 lên kênh mang lỗi cắt mép; QA khung hình không bắt)
            from beatfx import overflow_lines
            for w in overflow_lines(scenes, name):
                print(f"  ! WARNING tràn chữ beat2: {w}", flush=True)
        if BEAT2["on"]:    # chữ trên màn hình chép nguyên lời đọc = phụ đề phóng to (PM 09/10/2026)
            from beatfx import verbatim_share
            hit, tot = verbatim_share(scenes, lines)
            if tot and hit / tot > 0.4:
                print(f"  ! WARNING {name}: {hit}/{tot} dòng chữ lớn chép nguyên lời đọc — đổi thành từ khoá, con số, vế đối lập", flush=True)


def bgm_items(ch, lines, dur) -> list[dict]:
    """bgm: một dict (cả chương) hoặc danh sách đoạn {file, at (giây trong file), gain, start, end (mốc lời), fin, fout}."""
    b = ch.get("bgm") or []
    A = Anchors(lines)
    out = []
    for q in ([b] if isinstance(b, dict) else b):
        if not q.get("file"):
            continue
        st = A(q["start"]) if q.get("start") is not None else 0.0
        en = A(q["end"]) if q.get("end") is not None else dur
        out.append({**q, "start": round(st, 3), "end": round(min(en, dur), 3)})
    return out


def mix_chapter(ch, cd: Path, dur: float, quiet=(), master=True, items=None, levels=None, measure_music=False, music_lift=()):
    """voice + sfx + nhạc nền (né giọng) -> mix.wav 48k stereo, CHƯA loudnorm (làm một lần cho cả video).
    Nhạc nền có thể nhiều đoạn (bgm_items). Cảnh `question`: nhạc nền gần như tắt (khoảng lặng là cú đấm)."""
    if items is None:
        b = ch.get("bgm") or {}
        items = [{**b, "start": 0.0, "end": dur}] if b.get("file") else []
    levels = levels or {"gain": .16, "threshold": .03, "ratio": 6}
    duck = "".join(f",volume=enable='between(t,{a - 0.1:.2f},{z:.2f})':volume=0.12" for a, z in quiet)
    inputs = ["-i", str(cd / "voice.wav"), "-i", str(cd / "sfx.wav")]
    fc = "[0:a]aresample=48000," + (CHAN.get("voice_fx", VOICE_FX) + "," if master else "") + "pan=stereo|c0=c0|c1=c0,apad," + ("asplit=3[v][vk][vk2];" if items else "asplit=2[v][vk];") + "[1:a]volume=0.42[s0];[s0][vk]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[s];"
    if items:
        tags = []
        for k, q in enumerate(items):
            inputs += ["-ss", str(q.get("at", 0)), "-i", str(cd.parent / "bgm" / q["file"])]
            L = max(0.5, q["end"] - q["start"])
            fi, fo = q.get("fin", 1.5), q.get("fout", 2.0)
            ms = int(q["start"] * 1000)
            gain = q.get('gain', .16) if not measure_music else q.get('gain', .12) * levels['gain'] / .12
            fc += (f"[{k + 2}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{L:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={fi},"
                   f"afade=t=out:st={max(0, L - fo):.3f}:d={fo},volume={gain},adelay={ms}|{ms},apad[b{k}];")
            tags.append(f"[b{k}]")
        fc += "".join(tags) + f"amix=inputs={len(tags)}:normalize=0:duration=longest,atrim=0:{dur:.3f}{duck}[m0];"
        key = 'vk2'
        if music_lift:
            lift = ''.join(f",volume=enable='between(t,{a:.3f},{z:.3f})':volume=0" for a, z in music_lift)
            fc += f'[vk2]anull{lift}[music_key];'
            key = 'music_key'
        fc += (f"[m0][{key}]sidechaincompress=threshold={levels['threshold']}:ratio={levels['ratio']}:attack=40:release=600[m];"
               + ("[v]asplit=2[vmain][vmeasure];[m]asplit=2[mmain][mmeasure];[vmain][s][mmain]amix=inputs=3:weights='1 1 1':normalize=0:duration=first[a]" if measure_music else
               "[v][s][m]amix=inputs=3:weights='1 1 1':normalize=0:duration=first[a]")
               )
    else:
        fc += "[v][s]amix=inputs=2:weights='1 1':normalize=0:duration=first[a]"
    cmd = [FFMPEG, "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[a]", "-t", f"{dur:.3f}", "-ar", "48000", "-ac", "2", str(cd / "mix.wav")]
    if measure_music and items:
        cmd += ['-map', '[vmeasure]', '-t', f'{dur:.3f}', str(cd / 'voice_level.wav'), '-map', '[mmeasure]', '-t', f'{dur:.3f}', str(cd / 'music_level.wav')]
    r = run(cmd)
    if r.returncode != 0:
        raise SystemExit(f"mix hỏng {cd}: {r.stderr[-1500:]}")
    if measure_music and items:
        result = measure_mix_level(cd / 'voice_level.wav', cd / 'music_level.wav')
        result['mix_sha256'] = hashlib.sha256((cd / 'mix.wav').read_bytes()).hexdigest()
        (cd / 'music_level.json').write_text(json.dumps(result, indent=2), encoding='utf-8')


def measure_mix_level(voice_path, music_path):
    """RMS of processed stems in 0.5 s blocks containing both speech and music."""
    import numpy as np
    import soundfile as sf
    voice, sr = sf.read(str(voice_path), always_2d=True)
    music, msr = sf.read(str(music_path), always_2d=True)
    if sr != msr:
        raise ValueError('tần số lấy mẫu của hai stem khác nhau')
    step = max(1, sr // 2)
    vp = mp = 0.0
    blocks = 0
    for i in range(0, min(len(voice), len(music)) - step + 1, step):
        v = float(np.mean(voice[i:i+step] ** 2))
        m = float(np.mean(music[i:i+step] ** 2))
        if v > 1e-5 and m > 1e-10:
            vp += v
            mp += m
            blocks += 1
    if not blocks:
        raise ValueError('không có đoạn giọng và nhạc cùng phát để đo')
    return {'music_minus_voice_db': 10 * math.log10(mp / vp), 'blocks': blocks}


def check_mix_level(result):
    db = result.get('music_minus_voice_db')
    if not isinstance(db, (int, float)) or not math.isfinite(db) or not result.get('blocks'):
        return 'không đo được mức nhạc so với giọng; chạy lại html/mix'
    if db < -18:
        return f'nhạc nhỏ hơn giọng {-db:.1f} dB (>18 dB); tăng gain hoặc giảm nén rồi chạy lại html/mix'
    return None


# Cùng phiên bản với lệnh npx trong do_render.
LONG_NODE = 'node@22'
LONG_HYPERFRAMES = 'hyperframes@0.8.75'
LONG_RENDERER = f'{LONG_HYPERFRAMES};{LONG_NODE};fps=30;crf=20'


def render_key(topic, name, od, draft) -> str:
    """Key nội dung của chương; không băm mã nguồn mà composition không nạp (GH-21)."""
    hsh = hashlib.sha256()

    def add(label, value):
        label = label.encode('utf-8')
        hsh.update(len(label).to_bytes(8, 'big') + label)
        hsh.update(len(value).to_bytes(8, 'big') + value)

    def add_file(label, path):
        digest = hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                digest.update(block)
        add(label, digest.digest())

    add('format', b'long-chapter-v21')
    add('renderer', LONG_RENDERER.encode())
    add('quality', b'draft' if draft else b'final')
    comp = HF / 'compositions' / 'long' / f'{topic}_{name}.html'
    data = od / name / 'data.js'
    html = comp.read_text(encoding='utf-8')
    refs = data.read_text(encoding='utf-8') + html
    add_file('data', data)
    add_file('composition', comp)
    for label, path in (('spec', ROOT / 'data' / 'long' / topic / f'{name}.json'),
                        ('voice', od / name / 'voice.wav'), ('timing', od / name / 'timing.json')):
        if path.is_file():
            add_file(label, path)
    engine_refs = set(re.findall(r'''["'](assets/engine/[^"']+\.(?:js|css))["']''', html, re.I))
    if not engine_refs:  # fixture composition rỗng của các phiên bản cũ
        engine_refs = {f'assets/engine/{n}' for n in ('casewide.js', 'casewide.css', 'beat.js', 'beat.css')}
    for rel in sorted(engine_refs):
        add_file(rel, HF / rel)
    asset_refs = set(re.findall(r'''["'(]((?:assets|broll)/[^"')]+\.(?:jpe?g|png|webp|gif|svg|mp4|webm))''', refs, re.I))
    for rel in sorted(asset_refs):
        add_file(rel, HF / rel)
    return hsh.hexdigest()[:16]


def _chapter_duration_ok(video: Path, data: Path) -> bool:
    """Use the generated composition duration, including the final endcard."""
    try:
        raw = data.read_text(encoding="utf-8").strip()
        if not raw.startswith("window.CASE = ") or not raw.endswith(";"):
            return False
        expected = float(json.loads(raw[len("window.CASE = "):-1])["dur"])
        actual = probe_dur(video)
        stream = subprocess.run([FF + r"\ffprobe.exe", "-v", "error", "-select_streams", "v:0",
                                 "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(video)],
                                capture_output=True, text=True)
        return (stream.returncode == 0 and stream.stdout.strip() == "video"
                and math.isfinite(expected) and expected > 0 and math.isfinite(actual)
                and abs(expected - actual) <= 0.1)
    except (OSError, ValueError, TypeError, KeyError):
        return False


def chapter_problems(topic, name, od) -> str | None:
    """None = chương hợp lệ (video có hình, đúng độ dài, key khớp render_key hiện tại)."""
    video = od / name / "silent.mp4"
    try:
        ok = (video.is_file() and (od / name / "silent.key").read_text() == render_key(topic, name, od, False)
              and _chapter_duration_ok(video, od / name / "data.js"))
    except (OSError, ValueError):
        ok = False
    return None if ok else f"{name}: video chương thiếu, cũ hoặc không hợp lệ; cần render lại"


def do_render(topic, only=None, draft=False, force=False, allow_opening=False):
    if not draft:
        branch_gate.refuse(ROOT)  # bản nháp chỉ để soi cảnh, không cần nhánh đã đồng bộ
    _refuse_unreviewed_sheets(topic)  # áp dụng cả --draft: tờ soát phải đi trước mọi pixel render
    _refuse_html_lint(topic, only)   # không render 70 phút một bản html đã biết là hỏng
    spec, chs, od = load(topic)
    if not is_legacy_topic(topic):
        _refuse_opening(topic, spec, allow_opening)
    if not draft:
        _refuse_floor(topic, chs, spec["channel"])   # bản nháp (--draft) vẫn cho chạy để soi từng chương khi đang viết
    _refuse_craft(topic, spec, chs)
    for name, ch in chs:
        if only and name not in only:
            continue
        t0 = time.time()
        out = od / name / ("draft.mp4" if draft else "silent.mp4")
        key, kf = render_key(topic, name, od, draft), out.with_suffix(".key")
        with render_lock(f"long {topic} {name}"):   # một render một lúc trên cả máy (retro mục 9)
            data = od / name / "data.js"
            if not force and out.exists() and kf.exists() and kf.read_text() == key and _chapter_duration_ok(out, data):
                print(f"{name}: không đổi, bỏ qua", flush=True)
                continue
            LO.sweep_temps(out)
            LO.sweep_temps(out.parent / "draft_av.mp4")
            LO.sweep_temps(kf)
            # Xoá key TRƯỚC: crash hay replace hỏng giữa chừng không được để key cũ khớp bản dở (GH-170).
            LO.remove(kf, name)
            temp = LO.temp_path(out)
            try:
                cmd = ["npx.cmd", "-y", "-p", LONG_NODE, "-p", LONG_HYPERFRAMES, "hyperframes", "render", ".", "-c",
                       f"compositions/long/{topic}_{name}.html", "-o", str(temp), "--fps", "30", "--quiet"]
                cmd += ["-q", "draft"] if draft else ["--crf", "20"]
                r = run(cmd, cwd=HF, extra_env={"HF_CAPTURE_PARALLEL_STREAM": "true"} if spec.get("stream", True) else None)
                if r.returncode != 0 or not temp.is_file() or temp.stat().st_size == 0:
                    raise SystemExit(f"{name}: render hỏng\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
                if not _chapter_duration_ok(temp, data):
                    raise SystemExit(f"{name}: thời lượng video render không hợp lệ hoặc không khớp composition")
                LO.publish(temp, out, name)                     # video trước,
                LO.atomic_write_text(kf, key, name)             # key SAU khi video đã công bố
            finally:
                temp.unlink(missing_ok=True)
        if draft:   # bản nháp có tiếng để xem nhanh
            av = od / name / "draft_av.mp4"
            tav = LO.temp_path(av)
            try:
                r = run([FFMPEG, "-v", "error", "-y", "-i", str(out), "-i", str(od / name / "mix.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                         "-c:a", "aac", "-b:a", "160k", "-shortest", str(tav)])
                if r.returncode != 0 or not tav.is_file():
                    raise SystemExit(f"{name}: ghép tiếng bản nháp lỗi\n{r.stderr[-1500:]}")
                LO.publish(tav, av, name)
            finally:
                tav.unlink(missing_ok=True)
        print(f"{name}: {out.name} ({time.time() - t0:.0f}s)", flush=True)


def cmd_render(topic, only=None, rest=()):
    """`render`: lint màn trống đầu cảnh TRƯỚC khi xếp hàng render (retro 1 mục 4 lặp ở retro 2 mục 2: chặn bằng máy)."""
    late = late_report(topic, only)
    if late and "--allow-late" not in rest:
        raise SystemExit("màn trống đầu cảnh (phần tử đầu tiên > %.1fs, cảnh không nền):\n  " % LATE_MAX + "\n  ".join(late)
                         + "\nSửa neo trong gen_scenes.py rồi chạy lại `html`, hoặc thêm --allow-late nếu đã xem và chấp nhận.")
    for w in late:
        print(f"  ! WARNING (--allow-late) {w}", flush=True)
    try:     # engine đổi mà chưa soát gallery chữ có dấu (retro 2 mục 4) -> nhắc, không chặn
        import diacritics_gallery
        th = THEME["name"]
        if th in diacritics_gallery.THEMES and th in diacritics_gallery.stale():
            print(f"  ! WARNING engine đã đổi từ lần soát dấu cuối: python motion/long/diacritics_gallery.py render {th}", flush=True)
    except Exception as e:      # noqa: BLE001
        print(f"  ! WARNING không kiểm được gallery dấu: {e}", flush=True)
    with render_lock(f"long {topic} (cả lượt)"):   # giữ khoá cả lượt: không bị render khác chen giữa các chương
        names, od = pre_render_check(topic, only)
        do_render(topic, only, draft="--draft" in rest, force="--force" in rest, allow_opening="--allow-opening" in rest)
        post_render_check(names, od, draft="--draft" in rest)


def pre_render_check(topic, only=None):
    """#284: mở composition từng chương trong Chrome headless; pageerror thì dừng trước khi render (lỗi trang = video đứng hình)."""
    import pagecheck
    _, chs, od = load(topic)
    names = [name for name, _ in chs if not only or name in only]
    for name in names:
        errors = pagecheck.check(HF / "compositions" / "long" / f"{topic}_{name}.html", HF)
        if errors:
            raise SystemExit(f"{name}: lỗi trang dựng, dừng trước render:\n  " + "\n  ".join(errors))
    return names, od


def post_render_check(names, od, draft=False):
    """#284: ba khung 10/50/90% gần như giống nhau = video đứng hình; hủy key để lần sau render lại."""
    import frozen_check
    for name in names:
        video = od / name / ("draft.mp4" if draft else "silent.mp4")
        try:
            frozen = frozen_check.check(video, FFMPEG, probe_dur(video))
        except (OSError, ValueError, subprocess.SubprocessError) as e:
            LO.remove(video.with_suffix(".key"), name)
            raise SystemExit(f"{name}: không kiểm được video đứng hình: {e}") from e
        if frozen:
            LO.remove(video.with_suffix(".key"), name)
            raise SystemExit(f"{name}: video đứng hình; cần sửa và render lại")


def _write_final_commit(od: Path) -> None:
    """Ghi dấu QA của bản final sau khi video và phụ đề đều đã hoàn tất."""
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
        status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True,
                                text=True, encoding="utf-8", errors="replace")
    except OSError as e:
        raise SystemExit(f"final: không đọc được Git: {e}")
    if head.returncode != 0 or status.returncode != 0 or not head.stdout.strip():
        detail = (head.stderr or status.stderr or head.stdout or status.stdout).strip()
        raise SystemExit(f"final: không đọc được Git{': ' + detail if detail else ''}")
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    LO.atomic_write_text(
        od / "final.commit",
        f"commit: {head.stdout.strip()}\nworking_tree: {'dirty' if status.stdout.strip() else 'clean'}\ncreated_at: {stamp}\n",
        "final.commit")


def do_final(topic, check_variety=False, allow_repeat=False):
    """Một lượt final có manifest (GH-170): `running` trước, `ok` chỉ sau khi final + phụ đề đã công bố.
    Thất bại để final cũ nguyên nhưng manifest `failed`: publish_long/qa_mark từ chối."""
    with render_lock(f"long {topic} final"):     # cùng khoá với render chương
        branch_gate.refuse(ROOT)     # từ chối trước khi bắt đầu thì chưa động tới manifest/final cũ
        _refuse_unreviewed_sheets(topic)
        spec, chs, od = load(topic)
        run_m = LO.begin_run(od)
        try:
            return _do_final_locked(topic, spec, chs, od, run_m, check_variety, allow_repeat)
        except BaseException as e:      # noqa: BLE001  (kể cả Ctrl+C; kill -9 để lại `running`)
            LO.finish_failed(od, run_m, e)
            raise


def _load_amb_kinds():
    return LAMB._load_amb().KINDS


def _do_final_locked(topic, spec, chs, od, run_m, check_variety=False, allow_repeat=False):
    if check_variety:
        bad = variety.audit(topic)
        if bad and not allow_repeat:   # quá giống video gần đây: rủi ro "repetitive content" cho cả kênh
            raise SystemExit("variety audit:\n  " + "\n  ".join(bad) + "\nĐổi nhạc/look rồi dựng lại, hoặc thêm --allow-repeat nếu chấp nhận.")
    _refuse_floor(topic, chs, spec["channel"])
    _refuse_craft(topic, spec, chs)
    if not is_legacy_topic(topic):
        for n, ch in chs:
            bgm = ch.get('bgm') or []
            if not bgm:
                continue
            try:
                level = json.loads((od / n / 'music_level.json').read_text(encoding='utf-8'))
                if level.get('mix_sha256') != hashlib.sha256((od / n / 'mix.wav').read_bytes()).hexdigest():
                    raise ValueError('số đo không khớp mix.wav')
                problem = check_mix_level(level)
            except (OSError, ValueError) as e:
                problem = f'không đo được mức nhạc: {e}; chạy lại html/mix'
            if problem:
                raise SystemExit(f'{n}: {problem}')
    # Không ghép chương cũ/dở sau một lượt render hỏng hay bị ngắt.
    for n, _ in chs:
        problem = chapter_problems(topic, n, od)
        if problem:
            raise SystemExit(problem + " trước final")
    lst = od / "concat.txt"
    lst.write_text("".join(f"file '{(od / n / 'silent.mp4').as_posix()}'\n" for n, _ in chs), encoding="utf-8")
    if spec.get("ambience"):
        bad = LAMB.validate(spec, [n for n, _ in chs], _load_amb_kinds())
        if bad:
            raise SystemExit("spec.ambience sai: " + "; ".join(bad))
    # hình render làm tròn lên khung 1/30s -> đệm tiếng từng chương cho ĐÚNG bằng hình, không thì lệch cộng dồn (~0,2s ở chương cuối)
    for n, _ in chs:
        vd = probe_dur(od / n / "silent.mp4")
        # 23/10/2026: fade 5 ms hai đầu mỗi chương -- chỗ nối không còn bước nhảy ("tách" đầu chương, CL lẫn MIM)
        af = f"apad=whole_dur={vd:.6f},afade=t=in:d=0.005,afade=t=out:st={max(0.0, vd - 0.005):.6f}:d=0.005"
        bed = LAMB.bed_for_chapter(spec, n, od, vd, FF)      # None khi spec không có ambience -> lệnh y như cũ
        if bed:
            amb_db = mix_levels(topic, spec['channel'], spec)['ambience_db']
            r = run([FFMPEG, "-v", "error", "-y", "-i", str(od / n / "mix.wav"), "-i", str(bed), "-filter_complex",
                     f"[1:a]volume={amb_db}dB[amb];[0:a][amb]amix=inputs=2:weights='1 1':normalize=0:duration=first,{af}[o]", "-map", "[o]",
                     "-t", f"{vd:.6f}", str(od / n / "mixpad.wav")])
        else:
            r = run([FFMPEG, "-v", "error", "-y", "-i", str(od / n / "mix.wav"), "-af", af, "-t", f"{vd:.6f}", str(od / n / "mixpad.wav")])
        if r.returncode != 0:
            raise SystemExit(r.stderr[-1500:])
    # Kỹ thuật (cạnh nối/clip) hỏng thì mọi kênh đều chặn; buzz giọng giữ ngưỡng CL
    # vì chúng được hiệu chuẩn cho bộ lọc giọng CL, MIM/CK chỉ nhận cảnh báo cùng số đo.
    import audio_lint as AL
    try:
        technical = AL.check_parts([od / n / "mixpad.wav" for n, _ in chs], [od / n / "sfx.wav" for n, _ in chs if (od / n / "sfx.wav").exists()])
    except Exception as e:      # công cụ đo kỹ thuật hỏng: không xuất final không kiểm được
        AL.report(topic, [f"không đo được kỹ thuật: {e}"], [], True)
    AL.report(topic, technical, [], True)
    voice_block = spec["channel"] == "CL"
    try:
        verr, vwarn, _ = AL.check_voices([(n, od / n / "voice.wav") for n, _ in chs],
                                         CHAN.get("voice_fx", VOICE_FX) if spec.get("master", True) else None, FFMPEG)
    except Exception as e:      # đo buzz chỉ là cổng giọng CL; MIM/CK vẫn xuất kèm cảnh báo
        if voice_block:
            AL.report(topic, [f"không đo được buzz giọng: {e}"], [], True)
        verr, vwarn = [], [f"không đo được buzz giọng: {e}"]
    if not spec.get("master", True):   # "master": false (Yakuza) = cố ý giữ giọng thô -> buzz chỉ cảnh báo
        vwarn, verr = vwarn + verr, []
    AL.report(topic, verr, vwarn, voice_block)
    alst = od / "concat_a.txt"
    alst.write_text("".join(f"file '{(od / n / 'mixpad.wav').as_posix()}'\n" for n, _ in chs), encoding="utf-8")
    LO.sweep_temps(od / "final.mp4")
    LO.sweep_temps(od / "captions.vi.srt")
    tfinal, tsrt = LO.temp_path(od / "final.mp4"), LO.temp_path(od / "captions.vi.srt")
    try:
        r = run([FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-f", "concat", "-safe", "0", "-i", str(alst),
                 "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=192000,alimiter=limit=0.78:level=0,aresample=48000",   # 26/10/2026: chặn đỉnh thật ở 4x (5/25 Long từng vọt > −1 dBTP sau AAC; KAL đã thử limit 0.78 -> −1,7 dBTP, −14,2 LUFS)
                 "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                 "-shortest", "-movflags", "+faststart", str(tfinal)])
        if r.returncode != 0 or not tfinal.is_file() or tfinal.stat().st_size == 0:
            raise SystemExit("ghép final lỗi\n" + (r.stderr or "")[-2000:])
        try:
            ferr, fm = AL.check_final(tfinal, FFMPEG)   # true peak ≤ −1 dBTP sau AAC; đo trên file tạm, final cũ không bị đụng
        except Exception as e:
            AL.report(topic, [f"không đo được final sau AAC: {e}"], [], True)
        print(f"  audio_lint: true peak {fm['tp']} dBTP, {fm['lufs']} LUFS", flush=True)
        AL.report(topic, ferr, [], True)   # chặn = SystemExit -> manifest failed: final cũ không còn được consumer chấp nhận (15/10)
        # Phụ đề là đầu ra bắt buộc của final; srt.py lỗi phải làm lượt final lỗi.
        r = run([sys.executable, str(ROOT / "motion" / "long" / "srt.py"), topic, "--out", str(tsrt)])
        if r.returncode != 0:
            raise SystemExit((r.stderr or r.stdout)[-2000:])
        if not tsrt.is_file() or tsrt.stat().st_size == 0:
            raise SystemExit("srt.py không tạo phụ đề")
        LO.publish(tfinal, od / "final.mp4", "final")
        LO.publish(tsrt, od / "captions.vi.srt", "final")
    finally:
        tfinal.unlink(missing_ok=True)
        tsrt.unlink(missing_ok=True)
    _write_final_commit(od)
    LO.finish_ok(od, run_m, {n: (od / n / "silent.key").read_text() for n, _ in chs})
    print(od / "final.mp4", f"{probe_dur(od / 'final.mp4') / 60:.2f} phút")


if __name__ == "__main__":
    from factory.console import utf8_console  # noqa: E402
    utf8_console()  # console Windows cp1252 không in được tiếng Việt (retro 2 mục 7)
    topic, cmd, *rest = sys.argv[1:]
    only = [x for x in rest if not x.startswith("--")] or None
    if cmd in ("tts", "takes"):     # cổng toàn vẹn trước MỌI lần gọi TTS (retro 2 mục 16)
        integrity_gate(load(topic)[1], allow_repeat="--allow-repeat-line" in rest)
    if cmd in ("tts", "takes", "html"):      # mốc cảnh trùng thẻ chương: báo mọi chương TRƯỚC khi tốn TTS/tải ảnh (retro 3 mục 13)
        scene_gate([(n, c) for n, c in load(topic)[1] if not only or n in only])
    if cmd == "tts":
        do_tts(topic, only)
    elif cmd == "html":
        do_html(topic, only, allow_opening="--allow-opening" in rest)
        for x in variety.audit(topic):
            print("  ! variety:", x)
        _spec, _chs, _ = load(topic)
        print("  floor:", floor.report(_chs))
        for x in floor.problems(_chs, _spec["channel"], topic):
            print("  ! floor:", x)
    elif cmd == "render":
        cmd_render(topic, only, rest)
    elif cmd == "takes":
        nums = [x for x in rest if x.isdigit()]
        do_takes(topic, int(nums[0]) if nums else 3, [x for x in (only or []) if not x.isdigit()] or None)
    elif cmd == "pick":
        do_pick(topic)
    elif cmd == "final":
        do_final(topic, check_variety=True, allow_repeat="--allow-repeat" in rest)   # manifest lượt + final nguyên tử (GH-170)
