"""Render 1 đoạn Short (9:16) qua engine AssemblyJob có sẵn trong
video_tool_clone -- KHÔNG dùng nhánh Director Bible/ComfyUI của Long
(creative_director.py/asset_generation.py) vì Short không cần ảnh AI, chỉ
cần B-roll cắt nhanh + chữ to (xem trao đổi trong phiên: "chỉ cần typo và
video chuyển cảnh liên tục, tăng speed... tool video đã có hỗ trợ render
cho cả size ngang và dọc mà nhỉ" -- đúng, `scripts/run_auto_assembly.py` đã
có preset short-form (9:16, scene 4s, motion cao, broll speed 1.6) sẵn.

CHỖ SỬA DUY NHẤT so với dùng thẳng run_auto_assembly.py: AssemblyJob mặc
định luôn chạy Whisper (transcribe_audio) để tự đoán lại text/timestamp từ
audio -- vô lý vì mình ĐÃ CÓ text gốc chính xác 100% (văn bản đưa vào TTS)
và timestamp chính xác (render_engine.py xuất sẵn segments start/end khi
render audio). Whisper ở đây chỉ tổ đoán sai dấu tiếng Việt và tốn ~13s/short
vô ích. Patch bằng cách thay thế transcribe_audio() bằng 1 bản trả thẳng
TranscriptResult dựng từ segments-json có sẵn -- toàn bộ phần còn lại
(scene-plan, fetch B-roll, dựng caption/karaoke, encode) của AssemblyJob
giữ nguyên, không viết lại.
"""
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
VIDEO_TOOL_ROOT = PROJECT_ROOT / "video_tool_clone"
sys.path.insert(0, str(VIDEO_TOOL_ROOT))

import re  # noqa: E402

from core.stockfootage.assembly_job import AssemblyJob, AssemblyResult, run_assembly_job  # noqa: E402
import core.stockfootage.assembly_job as assembly_job_module  # noqa: E402
from core.stockfootage.env_keys import ENV_FILENAME, load_api_keys_from_env_file  # noqa: E402
from core.stockfootage.providers.pexels import PexelsProvider  # noqa: E402
from core.stockfootage.scene_plan import group_transcript_into_scenes  # noqa: E402
from core.pipeline.bgm import BGMConfig  # noqa: E402
from core.pipeline.subtitle_job import SubtitleArtifacts, SubtitleConfig  # noqa: E402
from core.subtitles.transcribe import TranscriptResult, TranscriptSegment, WordTimestamp  # noqa: E402
import core.pipeline.subtitle_job as subtitle_job_module  # noqa: E402

import domain_creative_profiles as creative_profiles  # noqa: E402

SHORT_FORM_WIDTH = 1080
SHORT_FORM_HEIGHT = 1920
SHORT_FORM_SCENE_SEC = 4.0
SHORT_FORM_MAX_SCENE_SEC = 8.0
SHORT_FORM_TRANSITION_SEC = 0.3
SHORT_FORM_MOTION_STRENGTH = "high"
SHORT_FORM_BROLL_SPEED = 1.6

FFMPEG_BIN = VIDEO_TOOL_ROOT / "vendor" / "ffmpeg-macos-libass" / "ffmpeg"
SYMBOL_CLIP_CACHE_DIR = PROJECT_ROOT / "chunks_cache" / "symbol_clips"

# BUG PHÁT HIỆN THẬT trên pilot batch EP005 seg 1 (Phật giáo): translate_vi_to_en()
# là dịch máy chữ-đúng-chữ (argos-translate, không có ngữ cảnh), nên câu
# "cũng không phải hình phạt của một đấng thần linh" (đang PHỦ ĐỊNH ý đó)
# vẫn dịch ra "punishment of a deity" -- Pexels lại thường gán các từ này
# cho ảnh Công giáo phương Tây (đã xác nhận trực tiếp: B-roll trả về là ảnh
# 1 linh mục đứng trước bàn thờ nhà thờ). Danh sách sanitize (thay từ dễ
# gây lẫn sang từ trung tính/đúng hướng hơn) giờ đọc theo TỪNG DOMAIN từ
# domain_creative_profiles.json (`broll_query_sanitizer`) thay vì hardcode
# cố định cho Phật giáo -- BUD giữ nguyên danh sách gốc y hệt (không đổi
# hành vi), domain khác tự có danh sách riêng khi phát hiện lẫn nội dung
# thật (đúng cách danh sách BUD từng được xây từ 1 lỗi thật, không đoán
# trước toàn bộ).
def _compile_sanitizer_patterns(topic: str) -> list[tuple[re.Pattern, str]]:
    profile = creative_profiles.load_profile_for_topic(topic)
    rules = profile.get("broll_query_sanitizer") or []
    return [(re.compile(r["pattern"], re.IGNORECASE), r["replacement"]) for r in rules]


def _sanitize_broll_query(query: str, patterns: list[tuple[re.Pattern, str]]) -> str:
    for pattern, repl in patterns:
        query = pattern.sub(repl, query)
    return query


def _install_religion_safe_translate_patch(topic: str = "Phật giáo") -> None:
    """Bọc translate_vi_to_en() thật (giữ nguyên chất lượng dịch) bằng 1
    lớp sanitize kết quả (theo domain của `topic`) trước khi assembly_job
    dùng làm query tìm B-roll."""
    patterns = _compile_sanitizer_patterns(topic)
    real_translate = assembly_job_module.translate_vi_to_en

    def _safe_translate(vi_text):
        result = real_translate(vi_text)
        return _sanitize_broll_query(result, patterns) if result else result

    assembly_job_module.translate_vi_to_en = _safe_translate


def _segment_to_word_timestamps(text: str, start: float, end: float, global_word_offset: int, important_indices: set[int]) -> list[WordTimestamp]:
    """Nội suy timestamp từng từ theo tỷ lệ số ký tự trong khoảng
    [start, end] đã biết -- CÙNG kỹ thuật audio_tool_render.py đã dùng cho
    Long (segments_to_word_timestamps), đã qua kiểm chứng thực tế.
    `global_word_offset`: chỉ số từ TOÀN CỤC (tính từ đầu cả kịch bản, xuyên
    suốt mọi segment) của từ ĐẦU TIÊN trong đoạn này -- phải khớp đúng cách
    _short_tts_render.py::strip_importance_markers() đã đếm (cùng dùng
    text.split() thuần), để is_important gắn đúng từ, không lệch segment."""
    words = text.strip().split()
    if not words:
        return []
    duration = max(end - start, 0.001)
    total_chars = sum(len(w) for w in words) or 1
    out = []
    cursor = start
    for i, w in enumerate(words):
        share = len(w) / total_chars
        w_dur = duration * share
        out.append(WordTimestamp(word=w, start=cursor, end=cursor + w_dur, probability=1.0,
                                  is_important=(global_word_offset + i) in important_indices))
        cursor += w_dur
    return out


def known_transcript_from_segments(segments_json_path: str, important_words_path: str | None = None) -> TranscriptResult:
    data = json.loads(Path(segments_json_path).read_text(encoding="utf-8"))
    raw_segments = data["segments"]

    important_indices: set[int] = set()
    if important_words_path and Path(important_words_path).exists():
        important_indices = set(json.loads(Path(important_words_path).read_text(encoding="utf-8")))

    segments = []
    full_text_parts = []
    global_word_offset = 0
    for seg in raw_segments:
        text = seg["text"].strip()
        if not text:
            continue
        start, end = float(seg["start"]), float(seg["end"])
        words = _segment_to_word_timestamps(text, start, end, global_word_offset, important_indices)
        segments.append(TranscriptSegment(start=start, end=end, text=text, words=words))
        full_text_parts.append(text)
        global_word_offset += len(text.split())
    return TranscriptResult(
        segments=segments, language="vi", language_probability=1.0,
        full_text=" ".join(full_text_parts),
    )


def _install_known_transcript_patch(segments_json_path: str, important_words_path: str | None = None) -> None:
    """Thay transcribe_audio() (được subtitle_job.py import theo tên riêng
    vào namespace của chính nó) bằng bản trả sẵn transcript đã biết --
    patch đúng chỗ TÊN ĐƯỢC TRA CỨU LÚC GỌI (namespace của subtitle_job
    module), không phải nơi định nghĩa gốc (core.subtitles.transcribe),
    nếu không patch sẽ không có tác dụng gì."""
    known = known_transcript_from_segments(segments_json_path, important_words_path)

    def _fake_transcribe_audio(audio_path, narration_duration, model_dir=None, on_progress=None,
                                model_manager=None, model_size="small"):
        if on_progress is not None:
            on_progress(99.0)
        return known

    subtitle_job_module.transcribe_audio = _fake_transcribe_audio


def _synthesize_ken_burns_clip(image_path: str, duration: float, video_width: int, video_height: int) -> Path:
    """Ken Burns (zoompan) từ 1 ảnh tĩnh -- dùng cho scene khớp
    symbol_library render_mode=static_asset (xem
    domain_creative_profiles.json, vd Bát Quái/Ngũ Hành: đã test thật AI
    vẽ sai sơ đồ này, cần asset dựng sẵn thay vì sinh mới mỗi lần). Cache
    theo (ảnh, kích thước, thời lượng làm tròn 0.5s) -- nhiều scene/tập có
    thể nhắc cùng 1 ký hiệu, không cần dựng lại."""
    SYMBOL_CLIP_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    duration = max(duration, 1.0)
    cache_key = f"{Path(image_path).stem}_{video_width}x{video_height}_{round(duration * 2) / 2:.1f}s.mp4"
    out_path = SYMBOL_CLIP_CACHE_DIR / cache_key
    if out_path.exists():
        return out_path

    fps = 30
    n_frames = max(1, round(duration * fps))
    zoom_end = 1.12
    zoom_step = (zoom_end - 1.0) / n_frames
    vf = (
        f"scale={video_width * 2}:{video_height * 2}:force_original_aspect_ratio=increase,"
        f"crop={video_width * 2}:{video_height * 2},"
        f"zoompan=z='min(zoom+{zoom_step:.6f}\\,{zoom_end})':d={n_frames}:s={video_width}x{video_height}:fps={fps},"
        f"format=yuv420p"
    )
    args = [
        str(FFMPEG_BIN), "-y", "-loop", "1", "-i", str(image_path),
        "-t", f"{duration:.3f}", "-vf", vf, "-r", str(fps), "-an", str(out_path),
    ]
    result = subprocess.run(args, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"Ken Burns clip lỗi cho {image_path}: {result.stderr[-800:]}")
    return out_path


def _resolve_manual_scene_clips(known: TranscriptResult, topic: str, video_width: int, video_height: int) -> dict[int, str]:
    """Scan scene y hệt cách assembly_job.py sẽ tự tính (cùng
    group_transcript_into_scenes, cùng target/max_sec) để biết TRƯỚC scene
    nào khớp symbol_library của domain -- chỉ xử lý render_mode=static_asset
    (Bát Quái, Ngũ Hành...) vì Short chưa nối vào ComfyUI/asset_generation.py
    như Long; render_mode=ai_generate_ok (Thanh Long, Bạch Hổ...) tạm rơi về
    Pexels bình thường (gap đã biết, chưa làm trong lần này -- xem phiên
    làm việc)."""
    profile = creative_profiles.load_profile_for_topic(topic)
    if not profile.get("symbol_library"):
        return {}
    scenes = group_transcript_into_scenes(known.segments, target_sec=SHORT_FORM_SCENE_SEC, max_sec=SHORT_FORM_MAX_SCENE_SEC)
    manual_clips: dict[int, str] = {}
    for i, scene in enumerate(scenes):
        entry = creative_profiles.resolve_symbol(profile, scene.text)
        if entry is None:
            continue
        # entry safety_critical (chặn tên người thật) PHẢI luôn gọi
        # pick_symbol_asset_path() dù thiếu render_mode/asset_path -- guard
        # cũ (chỉ gọi khi có sẵn asset_path) khiến entry cấu hình lỗi/thiếu
        # path BỎ QUA HOÀN TOÀN chặn an toàn (Codex review điểm #1 vòng 3).
        if not entry.get("safety_critical") and (entry.get("render_mode") != "static_asset" or not (entry.get("asset_paths") or entry.get("asset_path"))):
            continue
        image_path = Path(creative_profiles.pick_symbol_asset_path(entry))
        if not image_path.exists():
            print(f"CẢNH BÁO: symbol '{entry['key']}' trỏ tới asset không tồn tại ({image_path}) -- bỏ qua, dùng Pexels bình thường.", file=sys.stderr)
            continue
        duration = max(scene.end - scene.start, 1.0)
        clip_path = _synthesize_ken_burns_clip(str(image_path), duration, video_width, video_height)
        manual_clips[i] = str(clip_path)
    return manual_clips


def render_short(
    audio_path: str,
    segments_json_path: str,
    output_path: str,
    bgm_path: str | None = None,
    bgm_volume_pct: float | None = None,
    dynamic_captions: bool = True,
    important_words_path: str | None = None,
    topic: str = "Phật giáo",
) -> AssemblyResult:
    # Mặc định suy ra từ audio_path theo đúng quy ước _short_tts_render.py
    # đã ghi (Path(output_wav).with_suffix(".important_words.json")) --
    # không có file thì set rỗng, không lỗi (từ quan trọng là tính năng
    # thêm, không phải bắt buộc để render được).
    if important_words_path is None:
        candidate = Path(audio_path).with_suffix(".important_words.json")
        important_words_path = str(candidate) if candidate.exists() else None

    _install_known_transcript_patch(segments_json_path, important_words_path)
    _install_religion_safe_translate_patch(topic)

    known = known_transcript_from_segments(segments_json_path, important_words_path)
    manual_scene_clips = _resolve_manual_scene_clips(known, topic, SHORT_FORM_WIDTH, SHORT_FORM_HEIGHT)

    pexels_key, _ = load_api_keys_from_env_file(VIDEO_TOOL_ROOT / ENV_FILENAME)
    if not pexels_key:
        raise RuntimeError(f"Không tìm thấy Pexels API key trong {VIDEO_TOOL_ROOT / ENV_FILENAME}")
    provider = PexelsProvider(pexels_key)

    # G4 (Audio Generation remediation, finding E2): volume_pct giờ được
    # caller (short_batch_runner.py) tính RIÊNG cho từng track BGM đã chọn
    # (xem bgm_tracks.py: đo loudness thật qua ffmpeg ebur128, gain riêng
    # từng track để về cùng 1 mức "nền" mục tiêu, có giới hạn true-peak) --
    # trước đây LUÔN dùng default 10% chung cho MỌI track (BGMConfig ở
    # video_tool_clone/core/pipeline/bgm.py), làm 7 track có độ to gốc
    # chênh nhau ~8 LU ra video vẫn chênh y hệt vậy, không nhất quán giữa
    # các Short. Không truyền (None) -> giữ nguyên default cũ của BGMConfig
    # (không đổi hành vi khi gọi thủ công/debug không có giá trị đo sẵn).
    bgm_kwargs = {"enabled": True, "path": bgm_path, "loop": True}
    if bgm_volume_pct is not None:
        bgm_kwargs["volume_pct"] = bgm_volume_pct
    bgm = BGMConfig(**bgm_kwargs) if bgm_path else None

    job = AssemblyJob(
        audio_path=audio_path,
        output_path=output_path,
        provider=provider,
        bgm=bgm,
        subtitles=SubtitleConfig(enabled=True, dynamic_captions_enabled=dynamic_captions,
                                  uppercase_emphasis=True, font_style_italic=True),
        video_width=SHORT_FORM_WIDTH,
        video_height=SHORT_FORM_HEIGHT,
        scene_target_sec=SHORT_FORM_SCENE_SEC,
        scene_max_sec=SHORT_FORM_MAX_SCENE_SEC,
        transition_sec=SHORT_FORM_TRANSITION_SEC,
        motion_strength=__import__("core.pipeline.video_effects", fromlist=["IntensityLevel"]).IntensityLevel.HIGH,
        broll_speed_factor=SHORT_FORM_BROLL_SPEED,
        manual_scene_clips=manual_scene_clips or None,
    )

    def on_stage(state):
        print(f"STAGE: {state.name}", flush=True)

    result = run_assembly_job(job, on_stage=on_stage)
    return result


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--segments-json", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--bgm", default=None)
    ap.add_argument(
        "--bgm-volume-pct", type=float, default=None,
        help="volume_pct riêng cho track BGM đã chọn (G4 -- xem bgm_tracks.py: "
             "tính từ loudness đo thật, per-track). Không truyền -> dùng default "
             "chung của BGMConfig (hành vi cũ).",
    )
    ap.add_argument("--no-dynamic-captions", action="store_true")
    ap.add_argument("--topic", default="Phật giáo", help="Chủ đề (tra domain_creative_profiles.json cho sanitizer/symbol_library) -- mặc định Phật giáo")
    args = ap.parse_args()

    result = render_short(
        args.audio, args.segments_json, args.output,
        bgm_path=args.bgm, bgm_volume_pct=args.bgm_volume_pct,
        dynamic_captions=not args.no_dynamic_captions, topic=args.topic,
    )
    print(json.dumps({
        "ok": result.state.name == "COMPLETED", "state": result.state.name,
        "output_path": result.output_path, "scene_count": result.scene_count,
        "error": result.error, "warnings": result.warnings,
    }, ensure_ascii=False))
    return 0 if result.state.name == "COMPLETED" else 1


if __name__ == "__main__":
    sys.exit(main())
