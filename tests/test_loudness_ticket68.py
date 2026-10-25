"""Ticket 68: độ to đầu ra (Short -14, Long -16 LUFS, đỉnh thật <= -1 dBTP) và nhạc dễ lấn giọng không vào Long."""
import re
import shutil
import subprocess

import numpy as np
import pytest
import soundfile as sf

import hf_music
import hyperframes_bridge as HB

needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="cần ffmpeg")


def _speechy(path, seconds=12.0, sr=48000, seed=1):
    """Tín hiệu giống giọng TTS: nhỏ trung bình nhưng đỉnh nhọn (hệ số đỉnh cao) -- ca làm loudnorm một lượt hụt đích."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(seconds * sr)) / sr
    env = (np.sin(2 * np.pi * 3.1 * t) > .2) * (.3 + .7 * rng.random(len(t)) ** 8)
    x = .05 * np.sin(2 * np.pi * 180 * t) * env + .04 * rng.standard_normal(len(t)) * env
    x[:: sr // 7] = .5                                    # gai đỉnh
    sf.write(path, np.stack([x, x], axis=1).astype("float32"), sr)


def _measure(path):
    err = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])


@needs_ffmpeg
@pytest.mark.parametrize("lane", ["short", "long"])
def test_normalize_dat_dich_va_chan_dinh(tmp_path, lane):
    src, dst = tmp_path / "in.wav", tmp_path / "out.wav"
    _speechy(src)
    assert HB.integrated_lufs(src) < -20                  # đầu vào nhỏ, phải kéo lên nhiều
    HB.normalize_loudness(src, dst, HB.LOUD_TARGET[lane])
    lufs, tp = _measure(dst)
    assert abs(lufs - HB.LOUD_TARGET[lane]) <= HB.LOUD_TOL + .1
    assert tp <= HB.LOUD_TP + .2                          # ebur128 đo đỉnh thật; chừa .2 cho sai số đo


@needs_ffmpeg
def test_mux_audio_ghi_dung_do_to_long(tmp_path):
    video, narr = tmp_path / "v.mp4", tmp_path / "n.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x36:r=10", "-t", "12",
                    "-c:v", "libx264", str(video)], check=True)
    _speechy(narr)
    out = tmp_path / "o.mp4"
    HB.mux_audio(video, narr, out, duration=12, loudness=HB.LOUD_TARGET["long"])
    lufs, tp = _measure(out)
    assert abs(lufs - HB.LOUD_TARGET["long"]) <= .8        # AAC làm lệch thêm (tín hiệu thử toàn gai; giọng thật lệch ~.2)
    assert tp <= -0.5
    assert not list(tmp_path.glob("*._mix.wav")) and not list(tmp_path.glob("*._loud.wav"))


def test_pool_long_bo_bai_lan_giong(tmp_path, monkeypatch):
    (tmp_path / "bgm").mkdir()
    for f, _ in hf_music.CATALOG["fs"]:
        (tmp_path / "bgm" / f).write_bytes(b"x")
    monkeypatch.setattr(hf_music, "LEDGER", tmp_path / "ledger.json")
    pool = hf_music.pool_for({"id": "L_fs_x", "series": "fs", "day": "2026-11-01"}, root=tmp_path)
    assert pool and not {p.split("/")[-1] for p in pool} & hf_music.MASKS_VOICE
    assert hf_music.title("eastern_thought.mp3") == "Eastern Thought"   # vẫn ghi nguồn được cho video cũ
