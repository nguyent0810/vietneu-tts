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
import hashlib
import json
import re
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
    _classify_newline_run,
    _collapse_blank_lines,
    strip_en_tag_for_display,
)
from vieneu_utils.phonemize_text import _get_normalizer

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

# G2 (Audio Generation remediation, finding B1): TĂNG số này bất cứ khi nào
# thay đổi logic ẢNH HƯỞNG tới nội dung audio sinh ra cho 1 chunk giống hệt
# (chunking, skip_normalize, cách gọi self.v.infer...) mà KHÔNG đổi text
# đầu vào -- đây là cách duy nhất để chủ động vô hiệu hoá TOÀN BỘ cache cũ
# khi hành vi synthesis đổi, vì fingerprint tự nó không "biết" code đã đổi.
CHUNK_CACHE_VERSION = "v1"


def chunk_cache_fingerprint(chunk_text: str, voice_name: str, mode: str, sample_rate: int) -> str:
    """Fingerprint xác định danh tính 1 chunk cache -- thay cho việc key
    thuần theo INDEX vị trí như trước (Finding B1: `chunk_{i:04d}.wav` chỉ
    phụ thuộc vị trí trong danh sách chunk, KHÔNG phụ thuộc nội dung -- sửa
    text tại đúng vị trí đó, hoặc đảo thứ tự các đoạn, sẽ âm thầm dùng lại
    audio CŨ SAI nội dung mà không có cách nào phát hiện).

    Bao phủ đúng những gì audit yêu cầu: text chunk đã normalize (chính
    text sẽ đưa cho TTS), giọng, "model" (ở đây là `mode` -- lựa chọn class
    engine trong `vieneu.factory.Vieneu`, vd standard/fast/turbo/remote --
    các engine khác nhau cho audio khác nhau dù cùng text/giọng),
    sample_rate (gộp luôn định danh "sample rate mong đợi" vào fingerprint
    -- đóng góp phần cho Finding M2/B3: nếu sample_rate đổi, fingerprint đổi
    theo, cache cũ tự động miss thay vì bị đọc nhầm như đúng sample_rate
    hiện tại), và CHUNK_CACHE_VERSION (cho phép invalidate toàn bộ cache cũ
    thủ công khi sửa logic synthesis mà fingerprint tự nó không nắm được).

    Vị trí (index) của chunk trong danh sách KHÔNG nằm trong fingerprint --
    đây là ĐIỂM CHÍNH của fix: cache giờ định danh THEO NỘI DUNG, không theo
    vị trí, nên đảo thứ tự 2 đoạn giống hệt nhau vẫn tái dùng đúng cache của
    chính đoạn đó (an toàn + vẫn hưởng lợi cache), còn sửa text tại 1 vị trí
    sẽ tạo fingerprint khác hẳn -> cache miss -> render lại, KHÔNG BAO GIỜ
    tình cờ trùng với fingerprint của bản audio cũ đã sinh cho text khác.

    Payload mã hoá qua ``json.dumps`` của 1 LIST (không phải nối chuỗi bằng
    dấu phân cách thô) -- Codex review round 1 phát hiện bản nối chuỗi
    bằng ``"\\x1f".join(...)`` KHÔNG injective: 2 input khác nhau như
    ``("a\\x1fb", "c", ...)`` và ``("a", "b\\x1fc", ...)`` cho ra CÙNG
    payload nếu chunk_text/voice_name từng chứa đúng byte phân cách đó.
    JSON encode escape đúng mọi ký tự đặc biệt (kể cả U+001F) bên trong
    từng phần tử string, nên 2 list khác nhau LUÔN cho ra chuỗi JSON khác
    nhau -- loại bỏ khả năng đụng độ mã hoá dù chunk_text/voice_name/mode
    chứa ký tự gì đi nữa."""
    payload = json.dumps(
        [CHUNK_CACHE_VERSION, chunk_text, voice_name, mode, sample_rate],
        ensure_ascii=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _normalize_paragraphs(text: str) -> tuple[list[str], list[str]]:
    """Tách text thành từng "đoạn" (bởi 1+ dấu xuống dòng liên tiếp) rồi
    normalize TỪNG đoạn, KHÔNG rejoin lại thành 1 chuỗi -- tách riêng khỏi
    :func:`normalize_preserving_paragraphs` (G3, Audio Generation
    remediation finding D2) để nơi khác (``_short_tts_render.py``) có thể
    thao tác WORD-LEVEL trên từng đoạn đã normalize (gắn important_indices
    đúng theo CÙNG 1 lượt normalize) rồi tự rejoin bằng
    :func:`_rejoin_paragraphs` -- đảm bảo CHỈ 1 luồng chuẩn hoá canonical
    duy nhất được dùng cho cả synthesis lẫn word-highlight timing, thay vì
    2 lượt tách biệt dễ lệch nhau (xem D2: normalize có thể đổi SỐ LƯỢNG
    từ khi mở rộng số/ngày tháng/viết tắt, vd "123" -> "một trăm hai mươi
    ba").

    Trả về ``([], [])`` nếu text rỗng sau khi collapse."""
    normalizer = _get_normalizer()
    stripped = _collapse_blank_lines(text).strip()
    if not stripped:
        return [], []

    raw_parts = re.split(r"([\r\n]+)", stripped)
    paragraphs = raw_parts[0::2]
    separators = raw_parts[1::2]

    normalized_paragraphs = normalizer.normalize_batch(paragraphs, punc_norm=True)
    return normalized_paragraphs, separators


def _rejoin_paragraphs(paragraphs: list[str], separators: list[str]) -> str:
    """Ghép lại các đoạn ĐÃ NORMALIZE bằng đúng loại ranh giới gốc: ĐÚNG 1
    dấu xuống dòng -> giữ lại 1 ``"\\n"`` (ranh giới CÂU); >=2 dấu xuống
    dòng liên tiếp -> giữ lại ``"\\n\\n"`` (ranh giới ĐOẠN VĂN thật). Tách
    riêng khỏi :func:`_normalize_paragraphs` để ``_short_tts_render.py``
    (G3) dùng lại Y HỆT logic rejoin sau khi xử lý word-level, không lặp
    lại/lệch với :func:`normalize_preserving_paragraphs`."""
    if not paragraphs:
        return ""
    out: list[str] = [paragraphs[0]]
    for i in range(1, len(paragraphs)):
        boundary = _classify_newline_run(separators[i - 1]) if i - 1 < len(separators) else "sentence"
        out.append("\n\n" if boundary == "para" else "\n")
        out.append(paragraphs[i])
    return "".join(out)


def normalize_preserving_paragraphs(text: str) -> str:
    """Chuẩn hoá text theo từng "đoạn" (tách bởi 1 hoặc nhiều dấu xuống dòng
    liên tiếp), rồi ghép lại. BẢO TOÀN đúng loại ranh giới gốc khi ghép: ĐÚNG
    1 dấu xuống dòng (``"\\n"`` hoặc ``"\\r\\n"``) -> giữ lại 1 ``"\\n"`` (ranh
    giới CÂU); >=2 dấu xuống dòng liên tiếp -> giữ lại ``"\\n\\n"`` (ranh giới
    ĐOẠN VĂN thật).

    SỬA LỖI CŨ: trước đây hàm này LUÔN rejoin bằng đúng 1 ``"\\n"`` bất kể
    input có bao nhiêu dấu xuống dòng gốc -- xoá mất thông tin phân biệt câu/
    đoạn TRƯỚC KHI ``split_text_into_chunks_with_gaps`` kịp dùng, khiến MỌI
    ranh giới câu của script dạng "mỗi câu 1 dòng" (quy ước của FS/BUD) bị
    hiểu NHẦM thành ranh giới đoạn văn -- ĐÃ SỬA để phân loại đúng ("sentence"
    vs "para"), tách biệt khỏi câu hỏi "mỗi loại nên nghỉ bao lâu" (xem
    ``V3_GAP_SILENCE`` trong ``core_utils.py`` -- Phase 2 PASS WITH CAVEAT: cố
    ý đặt 2 loại cùng thời lượng làm default an toàn, giá trị tối ưu cho
    "sentence" riêng vẫn CHƯA có đủ bằng chứng, xem P1 pilot/calibration
    package chưa chạy).

    Dùng chung logic phân loại với ``vieneu_utils.core_utils._classify_newline_run``
    -- đổi 1 bên phải đổi bên kia, đây là 1 hợp đồng chung xuyên suốt 2 layer.

    Xây trên :func:`_normalize_paragraphs` + :func:`_rejoin_paragraphs`
    (G3) -- 2 hàm này là "nguồn sự thật" duy nhất cho việc chuẩn hoá, dùng
    chung với ``_short_tts_render.py`` để đảm bảo important_indices tính
    trên ĐÚNG token stream sẽ đưa vào TTS.
    """
    paragraphs, separators = _normalize_paragraphs(text)
    return _rejoin_paragraphs(paragraphs, separators)


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
    import shutil
    try:
        from drive_utils import RCLONE_BIN, rclone
    except Exception as exc:
        # BUG THẬT phát hiện qua Codex CLI review trước khi commit:
        # external_bin.py (nguồn RCLONE_BIN, xem drive_utils.py) resolve
        # TOÀN BỘ 5 binary ngoài (git/rclone/node/codex/npx/osascript) NGAY
        # lúc import, fail-closed -- nghĩa là thiếu BẤT KỲ cái nào trong số
        # đó (không chỉ riêng rclone) cũng khiến import này raise. Bắt rộng
        # (không chỉ MissingBinaryError) để giữ đúng tinh thần gốc của hàm
        # này: thiếu rclone (hoặc bất kỳ dependency nào của module resolve
        # nó) không bao giờ được làm crash cả tiến trình render, chỉ bỏ qua
        # bước upload Drive.
        print(f"rclone/external_bin chưa sẵn sàng ({exc}) — bỏ qua upload Drive.", flush=True)
        return False
    if not Path(RCLONE_BIN).exists() and shutil.which(RCLONE_BIN) is None:
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
        self.mode = mode  # G2: giữ lại để đưa vào chunk_cache_fingerprint()
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
        silence_map: Optional[dict] = None,
        already_normalized: bool = False,
    ) -> RenderResult:
        """``silence_map`` (tuỳ chọn): ghi đè độ dài silence theo loại gap
        (xem ``vieneu_utils.core_utils.gaps_to_silence``) -- KHÔNG đụng logic
        phân loại para/sentence/minor. Mặc định (không truyền) dùng
        ``V3_GAP_SILENCE`` chuẩn (hành vi CL hiện tại, không đổi). Caller
        (vd ``short_batch_runner.py``) truyền tường minh
        ``FS_BUD_SENTENCE_SAFE_DEFAULT`` cho nội dung FS/BUD -- quyết định
        kênh nào dùng override nào KHÔNG nằm trong hàm này.

        ``already_normalized`` (G3, finding D2): mặc định False -- hành vi
        CŨ, tự gọi ``normalize_preserving_paragraphs(text)``. Đặt True khi
        caller ĐÃ tự normalize ``text`` từ trước bằng chính
        ``_normalize_paragraphs``/``_rejoin_paragraphs`` (vd
        ``_short_tts_render.py``, cần normalize TRƯỚC để tính
        important_indices đúng theo token stream sẽ đưa vào TTS) -- BỎ QUA
        bước tự normalize ở đây, dùng ``text`` NGUYÊN VĂN làm input chunking.
        Đây là cách duy nhất đảm bảo CHỈ 1 lượt normalize canonical được
        dùng cho cả synthesis lẫn word-highlight timing -- không dựa vào
        giả định "normalize 2 lần cho kết quả giống hệt normalize 1 lần"
        (dù đúng trong thực nghiệm, không phải hợp đồng được đảm bảo)."""
        out_path = Path(out_path)
        normalized = text if already_normalized else normalize_preserving_paragraphs(text)
        chunks, gaps = split_text_into_chunks_with_gaps(normalized, max_chars=MAX_CHARS)
        silence_ps = gaps_to_silence(gaps, silence_map=silence_map)

        if cache_dir:
            cache_dir = Path(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)

        audios = []
        n_retried = 0
        n_failed = 0

        for i, chunk in enumerate(chunks):
            # G2 (Finding B1): cache key giờ là fingerprint theo NỘI DUNG
            # (text+giọng+mode+sample_rate+CHUNK_CACHE_VERSION), KHÔNG còn
            # theo index vị trí -- xem docstring chunk_cache_fingerprint().
            cache_path = (
                cache_dir / f"chunk_{chunk_cache_fingerprint(chunk, self.voice_name, self.mode, self.sample_rate)}.wav"
            ) if cache_dir else None
            if cache_path and cache_path.exists():
                audio, _sr = sf.read(cache_path)
                # G2 (Finding M2/B3): trước đây _sr đọc ra rồi bỏ luôn,
                # self.sample_rate được dùng vô điều kiện cho QA/timing dù
                # file cache thực tế có thể ở sample rate khác -- giờ
                # validate rõ ràng, sample_rate lệch thì coi như cache lỗi
                # (sinh lại) thay vì âm thầm tính timing sai.
                if _sr != self.sample_rate:
                    print(f"[{i}/{len(chunks)}] cache lỗi (sample_rate {_sr} != {self.sample_rate}), sinh lại", flush=True)
                else:
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
            # strip_en_tag_for_display: CHỈ làm sạch bản ghi timing/phụ đề --
            # chunks[i] (dùng cho self.v.infer()/cache fingerprint) giữ nguyên
            # thẻ <en> vì G2P cần nó để đọc đúng phát âm tiếng Anh (xem ghi
            # chú tại strip_en_tag_for_display()).
            timings.append((start, end, strip_en_tag_for_display(chunks[i])))
            cumulative = end
            if i < len(silence_ps):
                cumulative += silence_ps[i]

        final = join_audio_chunks(audios, self.sample_rate, silence_ps=silence_ps)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(out_path, final, self.sample_rate)

        duration_s = len(final) / self.sample_rate
        print(f"DONE: {out_path}  duration={duration_s:.1f}s  "
              f"retried={n_retried}  still_suspect={n_failed}", flush=True)

        # G1 (Codex review round 2, finding Medium #2): LUÔN ghi srt_path khi
        # write_srt_file=True, kể cả timings rỗng (vd input toàn khoảng
        # trắng sau normalize -> 0 chunks). Trước đây điều kiện "and
        # timings" khiến srt_path=None trong trường hợp này dù
        # write_srt_file=True -- upload_paths_to_drive() coi None là "không
        # có gì để upload" và trả True, nên caller đánh dấu hoàn tất dù
        # thiếu hẳn file .srt trên Drive (vi phạm đúng bất biến "đủ cả
        # wav+srt+json" mà G1 vừa thêm). write_srt() xử lý timings rỗng an
        # toàn (ghi file .srt rỗng hợp lệ).
        srt_path = None
        if write_srt_file:
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
