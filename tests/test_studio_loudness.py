"""Studio mux output must meet the Short loudness and true-peak target."""
import re
import shutil
import subprocess
import time

import pytest

import hyperframes_bridge as HB

needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="cần ffmpeg")


def _measure(path):
    err = subprocess.run(
        ["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    ).stderr
    integrated = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])
    true_peak = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])
    return integrated, true_peak


@needs_ffmpeg
def test_studio_mix_normalizes_to_short_target_and_limits_true_peak(tmp_path):
    video = tmp_path / "silent.mp4"
    voice = tmp_path / "voice.wav"
    bgm = tmp_path / "bgm.wav"
    fx = tmp_path / "fx.wav"
    mixed = tmp_path / "mix.wav"
    normalized = tmp_path / "loud.wav"
    output = tmp_path / "out.mp4"
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x36:r=10",
        "-t", "6", "-c:v", "libx264", str(video),
    ], check=True)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
        r"aevalsrc=0.12*sin(2*PI*220*t)*lt(mod(t\,6)\,4):s=48000:d=6", "-c:a", "pcm_s16le", str(voice),
    ], check=True)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=6",
        "-af", "volume=0.02", "-c:a", "pcm_s16le", str(bgm),
    ], check=True)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-t", "6", "-c:a", "pcm_s16le", str(fx),
    ], check=True)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(voice), "-stream_loop", "-1", "-i", str(bgm), "-i", str(fx),
        "-filter_complex", "[1:a]apad[v];[2:a]anull[m];[v][m][3:a]amix=inputs=3:duration=first:normalize=0[a]",
        "-map", "[a]", "-t", "6", "-c:a", "pcm_f32le", "-ar", "48000", "-ac", "2", str(mixed),
    ], check=True)
    before = _measure(mixed)
    HB.normalize_loudness(mixed, normalized, HB.LOUD_TARGET["short"], true_peak=-1.5)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(normalized), "-map", "0:v", "-map", "1:a",
        "-t", "6", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(output),
    ], check=True)
    after = _measure(output)
    assert -15 <= after[0] <= -13
    assert after[1] <= -1.0
    duration = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(output)], capture_output=True, text=True, check=True).stdout)
    assert abs(duration - 6.0) <= 0.05
    print(f"Studio loudness test: before {before[0]:.2f} LUFS / {before[1]:.2f} dBFS; after {after[0]:.2f} LUFS / {after[1]:.2f} dBFS")


@needs_ffmpeg
def test_silence_is_preserved_without_gain_or_error(tmp_path, capsys):
    src, dst = tmp_path / "silence.wav", tmp_path / "preserved.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "2", str(src)], check=True)
    _, gain = HB.normalize_loudness(src, dst, HB.LOUD_TARGET["short"])
    assert gain == 0
    assert dst.read_bytes() == src.read_bytes()
    assert "preserving original mix" in capsys.readouterr().err


@needs_ffmpeg
def test_normalization_overhead_for_synthetic_45_second_clip(tmp_path):
    src, dst = tmp_path / "45s.wav", tmp_path / "45s-normalized.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "aevalsrc=0.1*sin(2*PI*440*t):s=48000:d=45", str(src)], check=True)
    started = time.perf_counter()
    HB.normalize_loudness(src, dst, HB.LOUD_TARGET["short"], true_peak=-1.5)
    elapsed = time.perf_counter() - started
    print(f"45s normalization overhead: {elapsed:.3f}s")
    measured = _measure(dst)
    assert abs(measured[0] - HB.LOUD_TARGET["short"]) <= 1
