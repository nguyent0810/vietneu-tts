import json
import shutil
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf

import hf_ambience as ha
import hf_foley as foley
import hf_sound
import hyperframes_bridge as HB

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "output" / "cl_staging" / "grok" / "render_011"
MAIN_OUT_DIR = Path("/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/output/cl_staging/grok/render_011")
OUT_DIR.mkdir(parents=True, exist_ok=True)
MAIN_OUT_DIR.mkdir(parents=True, exist_ok=True)

SR = 48000
DUR = 60.0
N = int(DUR * SR)

# 1. Kịch bản 6 câu 60s
lines = [
    {"sentence_id": 1, "start": 0.8, "end": 4.5, "heading": True, "text": "**Chương 1: Khu rừng tĩnh lặng**", "words": []},
    {"sentence_id": 2, "start": 5.5, "end": 14.5, "text": "Gió nhẹ lướt qua **tán cây cổ thụ**, mang theo hơi sương sớm của núi rừng.", "words": []},
    {"sentence_id": 3, "start": 16.0, "end": 25.5, "text": "Người lữ hành ngồi yên dưới bóng râm, tâm trí **tĩnh lặng** như mặt hồ không một gợn sóng.", "words": []},
    {"sentence_id": 4, "start": 27.0, "end": 29.5, "heading": True, "text": "**Chương 2: Mưa ngàn chấn động**", "words": []},
    {"sentence_id": 5, "start": 31.8, "end": 44.0, "text": "Bầu trời bỗng chuyển đen kịt, một tiếng sấm **chấn** động xé toang không gian tĩnh mịch.",
     "words": [{"w": "tiếng", "t": 32.5}, {"w": "sấm", "t": 33.0}, {"w": "chấn", "t": 33.5}, {"w": "động", "t": 34.0}]},
    {"sentence_id": 6, "start": 46.0, "end": 57.5, "text": "Nhưng tâm người tu hành vẫn bất biến giữa vạn biến, **an nhiên** tự tại đón nhận cơn mưa.", "words": []},
]

# 2. Tạo giọng đọc mẫu chất lượng cao 48kHz stereo
cache_files = sorted(list(Path("chunks_cache/voice_lines").glob("*.wav")))
assert len(cache_files) >= 6, f"Cần ít nhất 6 file voice mẫu, có {len(cache_files)}"

v_total = np.zeros(N, dtype=np.float32)
for i, ln in enumerate(lines):
    seg_dur = ln["end"] - ln["start"]
    src_f = cache_files[i * 7 % len(cache_files)]
    d, sr = sf.read(src_f, dtype="float32")
    if sr != SR:
        from scipy.signal import resample_poly
        d = resample_poly(d, SR, sr).astype("float32")
    if d.ndim == 2:
        d = d.mean(axis=1)
    target_samples = int(seg_dur * SR)
    if len(d) >= target_samples:
        seg = d[:target_samples]
    else:
        seg = np.pad(d, (0, target_samples - len(d)))
    fade = int(0.05 * SR)
    seg[:fade] *= np.linspace(0, 1, fade)
    seg[-fade:] *= np.linspace(1, 0, fade)
    
    st_idx = int(ln["start"] * SR)
    en_idx = st_idx + len(seg)
    if en_idx <= N:
        v_total[st_idx:en_idx] += seg

from hf_foley import lufs, _db
voice_lufs = lufs(v_total)
v_total *= _db(-22.0 - voice_lufs)
voice_wav = OUT_DIR / "sample_voice.wav"
sf.write(voice_wav, np.stack([v_total, v_total], axis=1), SR, subtype="PCM_24")

# 3. Nhạc nền BGM
bgm_src = ROOT / "chunks_cache" / "bgm_short" / "bud" / "garden_music.mp3"
if not bgm_src.exists():
    bgm_src = next(Path("chunks_cache/bgm_short").glob("*/*.mp3"))

# 4. Cấu hình plan Long
row = {
    "id": "011_pilot_ambience_60s",
    "series": "bud",
    "lane": "long",
    "day": "2026-11-07",
    "script": [ln["text"] for ln in lines],
    "ambience": [
        {"kind": "forest", "gain_db": 0},
        {"chapter": 2, "kind": "rain", "gain_db": -1.5},
    ],
    "beats": {
        "5": {"beat": "silence", "dur": 1.8, "at": "before"},
        "5_hit": {"beat": "hit", "sid": 5, "word": "chấn"}
    },
    "sound": {
        "preset_long": "C",
        "music_gap": 17.0,
        "duck_db": 6.0,
        "target_lufs": {"long": -16.0}
    }
}

sound_spec = ha.sound_spec(row, record_ledger=True)
sound_spec["beats"] = {
    "5": {"beat": "silence", "dur": 1.8, "at": "before"},
    "5_h": {"beat": "hit", "sid": 5, "word": "chấn"}
}

# 5. Thực hiện trộn 4 lớp âm thanh
raw_mix_wav = OUT_DIR / "sample_raw_mix.wav"
final_mix_wav = OUT_DIR / "sample_011_60s.wav"

foley.mix_long(lines, "bud", voice_wav, bgm_src, DUR, sound_spec, set(), raw_mix_wav, seed=42)

# Chuẩn hoá LUFS về -16.0 LUFS và TP <= -1.0 dBTP
HB.normalize_loudness(raw_mix_wav, final_mix_wav, target=-16.0, true_peak=-1.0)

# Đo kiểm chuẩn bằng ebur128
meas = ha.measure(final_mix_wav)
print("KẾT QUẢ ĐO KIỂM 60S SAMPLE:")
print(f"  Integrated LUFS: {meas['lufs']} LUFS")
print(f"  True Peak:       {meas['tp']} dBTP")
print(f"  LRA:             {meas['lra']} LU")

# 6. Dựng video MP4 60s
final_mp4 = OUT_DIR / "sample_011_60s.mp4"

cmd = [
    "ffmpeg", "-v", "error", "-y",
    "-f", "lavfi", "-i", f"color=c=0x10141a:s=1280x720:d={DUR}:r=30",
    "-i", str(final_mix_wav),
    "-map", "0:v", "-map", "1:a",
    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    "-shortest", str(final_mp4)
]
subprocess.run(cmd, check=True)
print(f"Rendered video: {final_mp4}")

shutil.copyfile(final_mix_wav, MAIN_OUT_DIR / "sample_011_60s.wav")
shutil.copyfile(final_mp4, MAIN_OUT_DIR / "sample_011_60s.mp4")

qa_info = {
    "id": row["id"],
    "duration_s": DUR,
    "ambience_kinds": ["forest", "rain"],
    "silence_beats": [{"sid": 5, "dur": 1.8, "at": "before"}],
    "hit_beats": [{"sid": 5, "word": "chấn", "time_s": 33.5}],
    "integrated_lufs": meas["lufs"],
    "true_peak_dbtp": meas["tp"],
    "lra_lu": meas["lra"],
    "target_lufs": -16.0,
    "pass_lufs": abs(meas["lufs"] - (-16.0)) <= 0.5,
    "pass_tp": meas["tp"] <= -1.0,
    "files": {
        "wav": str(final_mix_wav),
        "mp4": str(final_mp4)
    }
}
(OUT_DIR / "qa_report.json").write_text(json.dumps(qa_info, ensure_ascii=False, indent=2), encoding="utf-8")
(MAIN_OUT_DIR / "qa_report.json").write_text(json.dumps(qa_info, ensure_ascii=False, indent=2), encoding="utf-8")
print("QA Report saved successfully!")
