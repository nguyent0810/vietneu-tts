"""
Lõi render dùng chung — tách từ render_natural.py để có thể GIỮ MODEL ĐÃ
LOAD và tái dùng cho nhiều file/đoạn trong CÙNG 1 process, tránh phải load
lại model mỗi lần (~6-9s/lần) như khi mỗi file là 1 subprocess riêng.

Mỗi lần render còn xuất kèm:
  - {out}.srt   : phụ đề theo từng chunk. Vì audio sinh ra TỪ chính text này
                  (không phải thu sẵn), timing suy ra trực tiếp từ độ dài
                  audio + khoảng nghỉ giữa các chunk — CHÍNH XÁC TUYỆT ĐỐI,
                  không cần forced-alignment hay ASR.
  - {out}.json  : manifest (giọng, thời lượng, timing từng chunk, thời điểm
                  sinh, + metadata tuỳ caller truyền vào như chủ đề/nguồn)
                  để tool khác (video, YouTube uploader...) tiêu thụ mà
                  không cần quét lại Drive để suy luận thông tin.
"""
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf

from vieneu_utils.core_utils import (
    split_text_into_chunks_with_gaps,
    gaps_to_silence,
    join_audio_chunks,
)
from vieneu_utils.phonemize_text import _get_normalizer, RE_NEWLINE_SPLIT

MAX_CHARS = 256
SEC_PER_CHAR = 0.055          # tốc độ đọc bình thường quan sát được (~18-20 ký tự/s)
MAX_RETRIES = 6
RETRY_TEMPERATURES = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]   # thử lần lượt nếu chunk bị nghi lỗi
INTERNAL_SILENCE_THRESHOLD = 1.2            # giây im lặng liên tục bên trong 1 chunk -> nghi lỗi
DURATION_RATIO_THRESHOLD = 1.6              # tỉ lệ duration/kỳ vọng vượt mức này -> nghi lỗi
# Các ngưỡng trên được tinh chỉnh thực nghiệm cho giọng/nội dung đã test (v2
# standard, văn phong chiêm nghiệm/kể chuyện tiếng Việt). Nếu đổi giọng khác
# hẳn hoặc nội dung có nhịp đọc rất khác, nên theo dõi tỷ lệ retry — tăng bất
# thường là dấu hiệu cần hiệu chỉnh lại ngưỡng.


def normalize_preserving_paragraphs(text: str) -> str:
    normalizer = _get_normalizer()
    paragraphs = [p for p in RE_NEWLINE_SPLIT.split(text) if p.strip()]
    return "\n".join(normalizer.normalize_batch(paragraphs, punc_norm=True))


def longest_internal_silence(audio: np.ndarray, sr: int, win_s: float = 0.1, thresh: float = 0.0015) -> float:
    """Giây im lặng liên tục dài nhất bên trong 1 đoạn audio (RMS < ngưỡng).

    ``thresh`` nới hơn 1 chút so với ngưỡng "im lặng tuyệt đối" để không bị nhiễu
    nền nhỏ (blip RMS ~0.001) cắt vụn một khoảng lặng thực chất là liên tục.
    """
    win = max(1, int(win_s * sr))
    n = len(audio) // win
    if n == 0:
        return 0.0
    longest = cur = 0
    for i in range(n):
        seg = audio[i * win:(i + 1) * win]
        rms = float(np.sqrt(np.mean(seg.astype(np.float64) ** 2)))
        if rms < thresh:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0
    return longest * win_s


def chunk_is_suspect(chunk_text: str, audio: np.ndarray, sr: int) -> Optional[str]:
    dur = len(audio) / sr
    expected = len(chunk_text) * SEC_PER_CHAR
    if dur > max(3.0, expected * DURATION_RATIO_THRESHOLD):
        return f"duration bất thường: {dur:.1f}s (kỳ vọng ~{expected:.1f}s)"
    gap = longest_internal_silence(audio, sr)
    if gap >= INTERNAL_SILENCE_THRESHOLD:
        return f"có khoảng lặng nội bộ {gap:.1f}s"
    return None


def _srt_timestamp(seconds: float) -> str:
    seconds = max(0.0, seconds)
    ms_total = int(round(seconds * 1000))
    h, ms_total = divmod(ms_total, 3_600_000)
    m, ms_total = divmod(ms_total, 60_000)
    s, ms = divmod(ms_total, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path: Path, timings: list[tuple[float, float, str]]) -> None:
    lines = []
    for i, (start, end, text) in enumerate(timings, 1):
        lines.append(str(i))
        lines.append(f"{_srt_timestamp(start)} --> {_srt_timestamp(end)}")
        lines.append(text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def upload_paths_to_drive(paths: list[Path], drive_remote: str) -> bool:
    """Upload nhiều file (wav + srt + json) lên cùng 1 thư mục Drive."""
    from drive_utils import rclone
    from external_bin import MissingBinaryError, get_rclone_bin

    # BUG THẬT phát hiện qua Codex CLI review trước khi commit (đã sửa gốc
    # ở external_bin.py -- xem PR #2 review): get_rclone_bin() giờ LAZY,
    # chỉ resolve đúng lúc gọi ở đây, không còn resolve CẢ 6 binary ngoài
    # (git/rclone/node/codex/npx/osascript) lúc import module -- nghĩa là
    # import `drive_utils`/`external_bin` không còn có thể raise vì lý do
    # KHÔNG liên quan tới rclone nữa. Vẫn giữ ĐÚNG tinh thần gốc của hàm
    # này: thiếu rclone không bao giờ được làm crash cả tiến trình render,
    # chỉ bỏ qua bước upload Drive -- bắt đúng MissingBinaryError (không
    # cần bắt rộng như trước, vì giờ đây là lỗi DUY NHẤT có thể xảy ra ở
    # bước resolve này).
    try:
        get_rclone_bin()
    except MissingBinaryError:
        print("rclone chưa cài — bỏ qua upload Drive.", flush=True)
        return False
    ok = True
    for p in paths:
        if p is None or not Path(p).exists():
            continue
        result = rclone("copy", str(p), drive_remote)
        if result.returncode == 0:
            print(f"Upload Drive OK: {drive_remote}{Path(p).name}", flush=True)
        else:
            print(f"Upload Drive LỖI ({Path(p).name}): {result.stderr.strip()}", flush=True)
            ok = False
    return ok


@dataclass
class RenderResult:
    out_path: Path
    duration_s: float
    n_chunks: int
    n_retried: int
    n_failed: int
    success: bool
    srt_path: Optional[Path] = None
    manifest_path: Optional[Path] = None


class RenderSession:
    """Giữ 1 model đã load, tái dùng cho nhiều lần render_text() liên tiếp
    thay vì load lại model mỗi lần (tiết kiệm ~6-9s/lần)."""

    def __init__(self, voice_name: str, mode: str = "standard",
                 backbone_device: str = "mps", codec_device: str = "mps"):
        from vieneu import Vieneu
        t0 = time.time()
        self.v = Vieneu(mode=mode, backbone_device=backbone_device, codec_device=codec_device)
        self.voice_name = voice_name
        self.voice = self.v.get_preset_voice(voice_name)
        self.sample_rate = self.v.sample_rate
        self.load_time = time.time() - t0
        print(f"[RenderSession:{voice_name}] Model loaded in {self.load_time:.1f}s", flush=True)

    def render_text(
        self,
        text: str,
        out_path: Path,
        cache_dir: Optional[Path] = None,
        write_srt_file: bool = True,
        write_manifest: bool = True,
        manifest_extra: Optional[dict] = None,
    ) -> RenderResult:
        out_path = Path(out_path)
        normalized = normalize_preserving_paragraphs(text)
        chunks, gaps = split_text_into_chunks_with_gaps(normalized, max_chars=MAX_CHARS)
        silence_ps = gaps_to_silence(gaps)

        if cache_dir:
            cache_dir = Path(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)

        audios = []
        n_retried = 0
        n_failed = 0

        for i, chunk in enumerate(chunks):
            cache_path = (cache_dir / f"chunk_{i:04d}.wav") if cache_dir else None
            if cache_path and cache_path.exists():
                audio, _sr = sf.read(cache_path)
                reason = chunk_is_suspect(chunk, audio, self.sample_rate)
                if reason is None:
                    audios.append(audio)
                    continue
                print(f"[{i}/{len(chunks)}] cache lỗi ({reason}), sinh lại", flush=True)

            best_audio, best_reason = None, None
            for attempt, temp in enumerate(RETRY_TEMPERATURES[:MAX_RETRIES + 1]):
                audio = self.v.infer(chunk, voice=self.voice, skip_normalize=True, temperature=temp)
                reason = chunk_is_suspect(chunk, audio, self.sample_rate)
                best_audio, best_reason = audio, reason
                if reason is None:
                    if attempt > 0:
                        n_retried += 1
                        print(f"[{i}/{len(chunks)}] OK sau {attempt} lần retry (temp={temp})", flush=True)
                    break
                next_temp = RETRY_TEMPERATURES[min(attempt + 1, len(RETRY_TEMPERATURES) - 1)]
                print(f"[{i}/{len(chunks)}] nghi lỗi ({reason}), thử lại temp={next_temp}", flush=True)

            if best_reason is not None:
                n_failed += 1
                print(f"[{i}/{len(chunks)}] CẢNH BÁO: vẫn nghi lỗi sau {MAX_RETRIES} lần retry "
                      f"({best_reason}) — giữ bản cuối, cần nghe lại thủ công", flush=True)

            if cache_path:
                sf.write(cache_path, best_audio, self.sample_rate)
            audios.append(best_audio)

            if (i + 1) % 20 == 0:
                print(f"... {i+1}/{len(chunks)} chunk xong", flush=True)

        # Timing từng chunk TRƯỚC khi ghép — dùng đúng công thức join_audio_chunks
        # (chunk + gap xen giữa) nên khớp chính xác với audio cuối cùng.
        timings: list[tuple[float, float, str]] = []
        cumulative = 0.0
        for i, audio in enumerate(audios):
            start = cumulative
            dur = len(audio) / self.sample_rate
            end = start + dur
            timings.append((start, end, chunks[i]))
            cumulative = end
            if i < len(silence_ps):
                cumulative += silence_ps[i]

        final = join_audio_chunks(audios, self.sample_rate, silence_ps=silence_ps)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(out_path, final, self.sample_rate)

        duration_s = len(final) / self.sample_rate
        print(f"DONE: {out_path}  duration={duration_s:.1f}s  "
              f"retried={n_retried}  still_suspect={n_failed}", flush=True)

        srt_path = None
        if write_srt_file and timings:
            srt_path = out_path.with_suffix(".srt")
            write_srt(srt_path, timings)

        manifest_path = None
        if write_manifest:
            manifest_path = out_path.with_suffix(".json")
            manifest = {
                "output_file": out_path.name,
                "voice": self.voice_name,
                "duration_s": round(duration_s, 2),
                "n_chunks": len(chunks),
                "n_retried": n_retried,
                "n_failed_qa": n_failed,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "segments": [
                    {"start": round(s, 3), "end": round(e, 3), "text": t}
                    for s, e, t in timings
                ],
            }
            if manifest_extra:
                manifest.update(manifest_extra)
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        return RenderResult(
            out_path=out_path, duration_s=duration_s, n_chunks=len(chunks),
            n_retried=n_retried, n_failed=n_failed, success=(n_failed == 0),
            srt_path=srt_path, manifest_path=manifest_path,
        )
