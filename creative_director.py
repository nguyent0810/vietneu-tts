"""
Lớp "đạo diễn điện ảnh": nhận JSON segments (từ render_engine.py — timing
chính xác 100%, không phải ASR đoán) và metadata tập (khi có, từ
02_EPISODE_PLANNER.md của Content-Creator), gộp thành "beat" (~18-25s, theo
đúng ranh giới câu/đoạn có sẵn, không bao giờ cắt giữa câu) rồi phân loại mỗi
beat thành 1 trong 3 cách xử lý hình ảnh:

  TYPOGRAPHY — chữ lớn giữa khung hình, dành cho câu châm ngôn/nguyên lý
               ngắn hoặc câu "định vị" trùng với Core Insight của tập.
  IMAGE      — 1 ảnh minh hoạ tĩnh + Ken Burns, dành cho hình ảnh ẩn dụ/tôn
               giáo cụ thể (thường chiếm phần lớn với nội dung Phật giáo, vì
               loại này hiếm khi có stock footage phù hợp).
  VIDEO      — clip stock thật, dành cho cảnh đời sống/thiên nhiên chung
               chung mà Pexels/Pixabay thực sự có và hợp tông.

Quy trình: rule-based trước (nhanh, không tốn API) → chỉ gọi Gemini làm
trọng tài cho các beat rule-based không tự tin (confidence < 0.6). Xuất
shot_list.json cho asset_generation.py + video_tool_bridge.py dùng tiếp.

Nguyên tắc dựng phim áp dụng (đã tra cứu, không tự bịa — xem plan):
Ken Burns nên đổi hướng luân phiên giữa các beat IMAGE liên tiếp, không lặp
cùng 1 hướng 2 lần liền.
"""
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path

import director_bible
import domain_creative_profiles as creative_profiles
from external_bin import CODEX_BIN, AGY_BIN, node_subprocess_env

AGY_TIMEOUT_S = 120

TARGET_BEAT_SEC = 20.0
MAX_BEAT_SEC = 35.0
MIN_BEAT_SEC = 6.0  # gộp ngược vào beat trước nếu beat cuối ngắn hơn mức này

TYPOGRAPHY_MAX_WORDS = 25
TIEBREAK_CONFIDENCE_THRESHOLD = 0.6

DEFAULT_MOTION_CYCLE = ["slow_zoom_in", "slow_pan_left", "slow_zoom_out", "slow_pan_right"]
_ALL_MOTIONS = {"slow_zoom_in", "slow_zoom_out", "slow_pan_left", "slow_pan_right"}


def _bible_str(value, default: str = "") -> str:
    """Gemini không phải lúc nào cũng theo đúng schema lồng nhau đã yêu cầu
    -- vd ai_video_policy/pexels_acceptance_policy đôi khi trả về string
    thẳng thay vì {"threshold": "..."}. Chấp nhận cả 2 dạng thay vì bắt lỗi
    cứng nhắc."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("threshold") or value.get("when_acceptable") or value.get("criteria") or json.dumps(value, ensure_ascii=False)
    return default


def _motion_cycle_from_bible(bible: dict) -> list[str]:
    cam = bible.get("camera_language", {}) if isinstance(bible.get("camera_language"), dict) else {}
    preferred = [m for m in cam.get("preferred_motions", []) if m in _ALL_MOTIONS]
    avoid = set(cam.get("avoid_motions", []) or [])
    preferred = [m for m in preferred if m not in avoid]
    if preferred:
        return preferred
    return [m for m in DEFAULT_MOTION_CYCLE if m not in avoid] or DEFAULT_MOTION_CYCLE

# Từ khoá gợi ý hình ảnh ẩn dụ/tôn giáo cụ thể — ưu tiên IMAGE (sinh ảnh AI,
# vì stock hiếm khi có nội dung tôn giáo Việt Nam phù hợp).
_CONCRETE_IMAGERY_WORDS = (
    "gánh", "đèn", "ngọn đèn", "bàn thờ", "hương", "nhang", "lửa", "ánh sáng",
    "bóng tối", "cửa", "ngưỡng cửa", "con đường", "sương", "hơi sương",
    "địa ngục", "địa tạng", "bồ tát", "tượng phật", "kinh", "chuông", "lễ",
    "quan tài", "mộ", "linh hồn", "vong", "trung ấm", "quỳ", "chắp tay",
)
# Từ khoá gợi ý cảnh đời sống/thiên nhiên chung chung — stock Pexels/Pixabay
# thường có sẵn và hợp tông.
_GENERIC_SCENE_WORDS = (
    "thiên nhiên", "đôi tay", "bàn tay", "bước đi", "ngồi yên", "nắng",
    "mưa", "biển", "núi", "rừng", "cây", "gió", "sông", "hoàng hôn",
    "bình minh", "mây", "lá",
)
# CHỈ những marker mở đầu câu, mang tính lời mời/mệnh lệnh trực tiếp tới
# người xem -- KHÔNG dùng các từ nối thông thường như "không phải"/"có lẽ"
# (xuất hiện tự nhiên trong hầu hết câu văn suy ngẫm, không phải tín hiệu
# đáng tin cho 1 câu châm ngôn độc lập; đã thử và gây quá nhiều false
# positive khi test trên EP007 thật).
_APHORISM_START_MARKERS = ("hãy ", "đừng ", "xin đừng ", "xin nhớ ")

TYPOGRAPHY_MIN_WORDS = 6
TYPOGRAPHY_MIN_SEC = 2.5


class Treatment(str, Enum):
    TYPOGRAPHY = "typography"
    IMAGE = "image"
    VIDEO = "video"
    DIAGRAM = "diagram"  # ảnh AI + mũi tên/nhãn chỉ hướng đè lên qua Remotion -- xem batch_detect_diagram_beats()


@dataclass
class Beat:
    start: float
    end: float
    text: str
    treatment: str = ""
    motion_mode: str | None = None
    prompt_or_keywords: str = ""
    source: str = "rule"  # "rule" hoặc "gemini"
    typography_card: bool = True  # False = nền màu phẳng + phụ đề thường (xem asset_generation.py fallback dài)
    typography_style: str | None = None  # "pop_in"|"rise_up"|"flip_3d"|"word_cascade" -- xem _pick_typography_style()
    typography_font_size_px: int | None = None
    premium: bool = False  # beat IMAGE quan trọng/phức tạp nhất -- thử Codex/agy trước ComfyUI, xem select_premium_beats()
    symbol_key: str | None = None  # khớp domain_creative_profiles.json symbol_library -- xem resolve_symbol()
    symbol_asset_path: str | None = None  # chỉ set khi symbol_key có render_mode="static_asset" -- asset_generation.py dùng thẳng, bỏ qua sinh ảnh AI
    diagram_annotations: list[dict] | None = None  # [{"label":..., "angleDeg":...}, ...] -- xem batch_detect_diagram_beats(), None nếu treatment != DIAGRAM


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def segments_to_sentences(segments: list[dict]) -> list[dict]:
    """Tách mỗi segment (chunk tự nhiên theo đoạn/câu ghép từ core_utils —
    CÓ THỂ chứa nhiều câu, vd văn phong kể chuyện của tập này hay nối 2-3
    câu ngắn thành 1 chunk) thành từng câu riêng, nội suy thời gian theo
    tỉ lệ số ký tự trong đoạn gốc (cùng kỹ thuật đã dùng để suy
    word-timestamp trong audio_tool_render.py). Bắt buộc phải làm bước
    này TRƯỚC khi phân loại TYPOGRAPHY: nếu phân loại ngay ở cấp độ
    segment gộp nhiều câu, 1 câu châm ngôn ngắn (vd "Lòng thành không có
    hạn sử dụng.") sẽ bị chìm trong tổng số từ của cả segment và không
    bao giờ được nhận diện."""
    sentences = []
    for seg in segments:
        text = seg["text"].strip()
        start, end = seg["start"], seg["end"]
        duration = max(end - start, 0.001)
        parts = [p.strip() for p in _SENTENCE_SPLIT_RE.split(text) if p.strip()]
        if len(parts) <= 1:
            sentences.append({"start": start, "end": end, "text": text})
            continue
        total_chars = sum(len(p) for p in parts) or 1
        cursor = start
        for p in parts:
            share = len(p) / total_chars
            p_dur = duration * share
            sentences.append({"start": cursor, "end": cursor + p_dur, "text": p})
            cursor += p_dur
    return sentences


def _flush_bucket(bucket: list[dict]) -> Beat:
    return Beat(
        start=bucket[0]["start"],
        end=bucket[-1]["end"],
        text=" ".join(s["text"].strip() for s in bucket),
    )


def group_segments_into_beats(
    segments: list[dict], target_sec: float = TARGET_BEAT_SEC, max_sec: float = MAX_BEAT_SEC,
) -> list[Beat]:
    """Gộp segment (đơn vị chunk từ render_engine.py, đã tự nhiên theo câu/
    đoạn nhờ thuật toán cắt của core_utils) thành beat ~target_sec, cap
    max_sec — theo đúng nguyên lý group_transcript_into_scenes bên
    video-editor (đổi cảnh mỗi khi chuyển ý, không đổi mỗi caption), nhưng
    tự viết lại vì input/output type khác (segment JSON của mình, không
    phải TranscriptSegment của Whisper). 1 segment dài hơn max_sec một
    mình không bao giờ bị cắt (tránh lệch khỏi audio gốc) — trở thành 1
    beat quá khổ, chấp nhận được vì hiếm khi xảy ra với văn bản đã cắt tự
    nhiên."""
    if not segments:
        return []

    # 1.0s -- rõ ràng lớn hơn khoảng lặng bình thường giữa 2 chunk liên tiếp
    # (para/sentence/minor gap: 0.04-0.35s, xem V3_GAP_SILENCE trong
    # core_utils), nhưng nhỏ hơn nhiều so với 1 câu TYPOGRAPHY bị tách riêng
    # (tối thiểu TYPOGRAPHY_MIN_SEC=2.5s) -- đủ để phân biệt "khoảng lặng
    # bình thường" (bỏ qua) với "có 1 câu đã bị tách sang beat riêng ở pass
    # 1" (bắt buộc flush, tránh overlap).
    GAP_EPSILON = 1.0

    beats: list[Beat] = []
    bucket: list[dict] = []
    bucket_start = None

    for seg in segments:
        # Có khoảng hở thời gian với segment trước (vd 1 câu TYPOGRAPHY đã bị
        # tách riêng ở pass 1, nằm xen giữa) -- BẮT BUỘC flush trước khi thêm
        # segment mới, nếu không beat.end sẽ "nhảy qua" khoảng hở đó và lấn
        # (overlap) vào đúng dải thời gian của beat TYPOGRAPHY đã tách riêng.
        has_time_gap = bucket and (seg["start"] - bucket[-1]["end"]) > GAP_EPSILON
        would_exceed_max = bucket and (seg["end"] - bucket_start) > max_sec
        if has_time_gap or would_exceed_max:
            beats.append(_flush_bucket(bucket))
            bucket = []
            bucket_start = None

        if bucket_start is None:
            bucket_start = seg["start"]
        bucket.append(seg)

        if (seg["end"] - bucket_start) >= target_sec:
            beats.append(_flush_bucket(bucket))
            bucket = []
            bucket_start = None

    if bucket:
        beats.append(_flush_bucket(bucket))

    # Beat cuối quá ngắn (vd phần dư nhỏ cuối tập) -> gộp ngược vào beat trước
    # thay vì để 1 beat vụn vài giây, không đủ thời gian cho bất kỳ treatment nào.
    if len(beats) >= 2 and (beats[-1].end - beats[-1].start) < MIN_BEAT_SEC:
        last = beats.pop()
        prev = beats[-1]
        beats[-1] = Beat(start=prev.start, end=last.end, text=f"{prev.text} {last.text}")

    return beats


def read_episode_planner_context(planner_md_path: Path | None) -> dict:
    """Đọc Core Insight + Visual Motif từ 02_EPISODE_PLANNER.md (định dạng
    do chính pipeline nội dung tự viết ra, xem EP007) — dùng làm định
    hướng nhất quán cho phân loại + prompt sinh ảnh. Trả về rỗng nếu
    không có file (tập nguồn Drive thuần không có file này — không phải
    lỗi, chỉ là thiếu định hướng thêm)."""
    if not planner_md_path or not Path(planner_md_path).exists():
        return {"core_insight": "", "visual_motif": ""}

    text = Path(planner_md_path).read_text(encoding="utf-8")

    def _section(name: str) -> str:
        m = re.search(rf"## {re.escape(name)}\n\n(.+?)(?=\n## |\Z)", text, re.S)
        return m.group(1).strip() if m else ""

    return {"core_insight": _section("Core Insight"), "visual_motif": _section("Visual Motif")}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _fuzzy_contains(core_insight: str, beat_text: str) -> bool:
    """Core Insight thường là 1 đoạn dài giải thích ẩn dụ — không khớp
    nguyên văn với câu trong script. Coi là khớp nếu >=8 từ liên tiếp của
    beat xuất hiện trong Core Insight (cửa sổ 8 từ đủ đặc trưng để không
    khớp nhầm câu văn thông thường có vài từ trùng ngẫu nhiên; 6 từ đã thử
    và vẫn quá dễ khớp nhầm)."""
    if not core_insight or not beat_text:
        return False
    ci = _normalize(core_insight)
    words = _normalize(beat_text).split()
    if len(words) < 8:
        return False
    for i in range(len(words) - 7):
        window = " ".join(words[i:i + 8])
        if window in ci:
            return True
    return False


def _looks_like_aphorism(text: str) -> bool:
    """Câu hỏi tu từ NGẮN (không phải câu hỏi ghép dài dòng), hoặc câu mở
    đầu bằng lời mời/mệnh lệnh trực tiếp tới người xem -- 2 tín hiệu hẹp,
    có chủ đích, thay vì bắt theo từ nối chung chung."""
    stripped = text.strip()
    lowered = stripped.lower()
    word_count = len(stripped.split())
    if stripped.endswith("?") and word_count <= 15:
        return True
    return any(lowered.startswith(marker) for marker in _APHORISM_START_MARKERS)


def _has_concrete_imagery(text: str) -> bool:
    lowered = text.lower()
    return any(w in lowered for w in _CONCRETE_IMAGERY_WORDS)


def _has_generic_scene(text: str) -> bool:
    lowered = text.lower()
    return any(w in lowered for w in _GENERIC_SCENE_WORDS)


def extract_pexels_hints(bible: dict) -> list[str]:
    """Rút cụm cảnh CỤ THỂ mà Director Bible xác nhận HỢP để dùng stock
    video CHO ĐÚNG TẬP NÀY (field pexels_acceptance_policy -- xem
    director_bible.py) -- ví dụ EP007: "thắp nến dâng Phật, hoa sen nở
    chậm, gia đình ngồi trầm tư...". Trước đây field này được sinh ra
    nhưng KHÔNG hề được code đọc -- mọi quyết định VIDEO chỉ dựa vào 1 bộ
    từ khoá cố định giống nhau cho mọi tập (_GENERIC_SCENE_WORDS). Giờ
    dùng field này làm tín hiệu VIDEO ưu tiên cao hơn, cụ thể theo từng
    tập thay vì chung chung."""
    raw = _bible_str(bible.get("pexels_acceptance_policy"))
    if not raw:
        return []
    if ":" in raw:
        raw = raw.split(":", 1)[1]
    parts = re.split(r"[,.;]", raw)
    return [p.strip() for p in parts if len(p.strip().split()) >= 2]


def batch_judge_video_eligibility(
    beats: list[Beat], pexels_hints: list[str], context_label: str = "Phật giáo/tâm linh",
) -> set[int]:
    """1 lệnh gọi agy DUY NHẤT (không phải 1 lệnh/beat -- cùng nguyên tắc
    "1 lệnh/tập" đã dùng cho Director Bible và batch_translate_visual_hints)
    xét THEO NGHĨA xem beat nào THẬT SỰ mô tả 1 trong các cảnh mà Director
    Bible xác nhận hợp để dùng video stock thật (pexels_acceptance_policy).

    Trước đây thử so khớp CHUỖI KÝ TỰ (cụm từ liên tiếp) thay cho bước
    này -- quá thô: câu "gia đình bạn, vì bất cứ lý do gì..." (đang nói về
    hoàn cảnh/lý do, KHÔNG mô tả cảnh gì cả) vẫn khớp chuỗi "gia đình" với
    hint "gia đình ngồi trầm tư..." dù nội dung chẳng liên quan. Cần hiểu
    NGHĨA câu mới phân biệt được "nhắc tới từ khoá" và "đang mô tả đúng
    cảnh đó".

    Trả về set các INDEX (0-based, đúng thứ tự `beats`) mà agy xác nhận
    THẬT SỰ khớp. Lỗi bất kỳ (agy chưa cài, quota, JSON không hợp lệ...)
    -- trả về set() rỗng, xử lý an toàn theo hướng "thà bỏ sót còn hơn gán
    nhầm" (0 video vẫn tốt hơn video sai nội dung -- đã là bài học từ lần
    thử so khớp chuỗi ký tự)."""
    if not beats or not pexels_hints or not AGY_BIN.exists():
        return set()

    items = "\n".join(f"{i}: {b.text}" for i, b in enumerate(beats))
    scenes = "\n".join(f"- {h}" for h in pexels_hints)
    prompt = (
        f"Bạn là đạo diễn hình ảnh cho 1 video {context_label} tiếng Việt.\n"
        f"Danh sách cảnh THỰC TẾ được duyệt dùng video stock cho tập này:\n{scenes}\n\n"
        "Với MỖI câu thoại dưới đây (đánh số), xác định câu đó có THẬT SỰ đang mô tả 1 "
        "trong các cảnh ở trên không -- không phải chỉ nhắc tới từ khoá liên quan (vd chỉ "
        "nhắc \"gia đình\" khi đang nói về hoàn cảnh/lý do KHÔNG tính), mà phải đúng là câu "
        "đang mô tả cảnh đó xảy ra mới tính.\n\n"
        f"{items}\n\n"
        "Trả lời CHỈ 1 JSON array of integers (số thứ tự các câu THẬT SỰ khớp, có thể là "
        "mảng rỗng []), không giải thích gì thêm."
    )
    try:
        result = subprocess.run([str(AGY_BIN), "-p", prompt], capture_output=True, text=True, timeout=AGY_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        print("CẢNH BÁO: agy timeout khi xét video eligibility -- bỏ qua, giữ nguyên 0 video từ tín hiệu này.", file=sys.stderr)
        return set()
    if result.returncode != 0:
        print(f"CẢNH BÁO: agy lỗi (exit {result.returncode}) khi xét video eligibility -- bỏ qua.", file=sys.stderr)
        return set()

    indices = _extract_json_array(result.stdout)
    if not isinstance(indices, list):
        print("CẢNH BÁO: agy không trả JSON array hợp lệ khi xét video eligibility -- bỏ qua.", file=sys.stderr)
        return set()
    return {int(i) for i in indices if isinstance(i, (int, float)) and 0 <= int(i) < len(beats)}


def classify_beat_rule_based(
    beat: Beat, core_insight: str = "", video_eligible: bool = False,
) -> tuple[Treatment, float]:
    """Trả (treatment, confidence 0.0-1.0). confidence < TIEBREAK_CONFIDENCE_THRESHOLD
    nghĩa là nên đẩy qua Gemini phân xử thay vì tin rule-based.

    `video_eligible` -- đã được agy xét THEO NGHĨA từ trước (xem
    batch_judge_video_eligibility()), không phải tự so khớp trong hàm
    này -- hàm này giữ nguyên tính chất pure/nhanh (không I/O), việc gọi
    agy tốn thời gian mạng chỉ nên xảy ra ĐÚNG 1 LẦN/tập ở build_shot_list()."""
    text = beat.text.strip()
    word_count = len(text.split())
    duration = beat.end - beat.start

    # Cổng tối thiểu: 1 câu quá ngắn (dưới ~2.5s hoặc dưới 6 từ) không đủ để
    # đứng riêng thành 1 typography card có nghĩa (không đủ thời gian đọc,
    # và thường là mệnh đề phụ thuộc câu trước, không tự thân đầy đủ ý) --
    # loại ngay từ đầu, bất kể có khớp tín hiệu nào khác.
    long_enough = word_count >= TYPOGRAPHY_MIN_WORDS and duration >= TYPOGRAPHY_MIN_SEC

    if long_enough and core_insight and _fuzzy_contains(core_insight, text):
        return Treatment.TYPOGRAPHY, 0.95

    if long_enough and word_count <= TYPOGRAPHY_MAX_WORDS and _looks_like_aphorism(text):
        return Treatment.TYPOGRAPHY, 0.75

    has_imagery = _has_concrete_imagery(text)

    # Tín hiệu VIDEO ưu tiên cao nhất: agy đã xác nhận THEO NGHĨA beat này
    # thật sự mô tả 1 cảnh mà Director Bible cho phép dùng video stock cho
    # TẬP NÀY (pexels_acceptance_policy) -- cụ thể hơn hẳn bộ từ khoá cố
    # định _GENERIC_SCENE_WORDS dùng chung cho mọi tập, nên ưu tiên trước.
    # Vẫn nhường IMAGE nếu câu cũng có hình ảnh tôn giáo cụ thể (has_imagery)
    # -- tránh lấn 1 cảnh biểu tượng quan trọng (địa ngục, tượng Phật...)
    # bằng b-roll chung chung.
    if not has_imagery and video_eligible:
        return Treatment.VIDEO, 0.8

    has_scene = _has_generic_scene(text)

    if has_imagery and not has_scene:
        return Treatment.IMAGE, 0.7
    if has_scene and not has_imagery:
        return Treatment.VIDEO, 0.65
    if has_imagery and has_scene:
        return Treatment.IMAGE, 0.4  # cả 2 tín hiệu -> không chắc, đẩy Gemini

    # Không tín hiệu rõ ràng nào -- nghiêng IMAGE làm mặc định (đã xác nhận
    # stock hiếm khi hợp nội dung Phật giáo), nhưng confidence thấp để
    # Gemini có cơ hội phân xử khi có API key.
    return Treatment.IMAGE, 0.3


def gemini_tiebreak(
    beat: Beat, visual_motif: str, api_key: str,
    context_label: str = "Phật giáo/tâm linh", tone_label: str = "giọng trang nghiêm, tôn trọng",
) -> Treatment | None:
    """Gọi Gemini API (text, không phải CLI tương tác — xem ghi chú trong
    plan: gemini CLI không có tool sinh/ghi ảnh, và bản thân CLI cũng chỉ
    là 1 lớp bọc quanh cùng API key này) làm trọng tài cho beat rule-based
    không tự tin. Trả None nếu gọi lỗi (mạng, quota...) -- caller giữ
    nguyên kết quả rule-based, không để 1 lỗi API làm sập cả batch."""
    try:
        from google import genai
    except ImportError:
        return None

    prompt = (
        f"Bạn là đạo diễn hình ảnh cho 1 video {context_label} tiếng Việt, {tone_label}.\n"
        f"Ẩn dụ hình ảnh trung tâm của tập: {visual_motif or '(không có)'}\n"
        f'Đoạn lời thoại cần quyết định cách thể hiện hình ảnh: "{beat.text}"\n\n'
        "Chọn ĐÚNG 1 trong 3 cách xử lý:\n"
        "- typography: chữ lớn giữa khung hình -- dùng cho câu châm ngôn/nguyên lý ngắn, câu hỏi trực tiếp tới người xem.\n"
        "- image: 1 ảnh minh hoạ tĩnh có chuyển động nhẹ -- dùng cho hình ảnh ẩn dụ/tôn giáo cụ thể.\n"
        "- video: clip video thật -- dùng cho cảnh đời sống/thiên nhiên chung chung.\n\n"
        "Trả lời CHỈ 1 từ, không giải thích: typography, image, hoặc video."
    )
    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
        answer = (resp.text or "").strip().lower()
    except Exception as exc:
        print(f"CẢNH BÁO: Gemini tie-break lỗi ({exc}), giữ kết quả rule-based", file=sys.stderr)
        return None

    for t in Treatment:
        if t.value in answer:
            return t
    return None


def _extract_json_array(text: str) -> list | None:
    """agy đôi khi bọc JSON trong ```json fences -- tìm khối [...] ngoài
    cùng đầu tiên thay vì json.loads() thẳng cả chuỗi (cùng cách xử lý đã
    dùng cho _extract_json() trong content_seo.py)."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\[.*\]", text, re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _extract_json_object(text: str) -> dict | None:
    """Giống _extract_json_array() nhưng tìm khối {...} -- dùng cho các
    hàm chấm điểm trả về {"index": score, ...} thay vì mảng."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _chunked(items: list, size: int):
    for i in range(0, len(items), size):
        yield i, items[i:i + size]


CODEX_TEXT_TIMEOUT_S = 120


def _run_codex_text(prompt: str, timeout_s: int = CODEX_TEXT_TIMEOUT_S) -> str | None:
    """Fallback TEXT (không phải imagegen) qua Codex CLI -- dùng khi agy
    hết quota TEXT (pool RIÊNG, tách biệt hẳn quota sinh ảnh của agy đã
    gặp trước đó -- cả 2 đều có thể cạn độc lập). Codex là coding-agent
    CLI khác hẳn agy, quota/tài khoản khác, nên vẫn dùng được dù agy đã
    cạn. Output parse giống content_seo.py::_run_codex() -- codex exec in
    banner rồi lặp lại câu trả lời 2 lần (sau marker 'codex' VÀ lần nữa ở
    cuối sau 'tokens used'), lấy đoạn ĐẦU TIÊN."""
    try:
        result = subprocess.run(
            [CODEX_BIN, "exec", "--skip-git-repo-check", prompt], capture_output=True, text=True, timeout=timeout_s,
            env=node_subprocess_env(),
        )
    except subprocess.TimeoutExpired:
        print(f"CẢNH BÁO: Codex timeout sau {timeout_s}s.", file=sys.stderr)
        return None
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        print(f"CẢNH BÁO: Codex lỗi (exit {result.returncode}): {result.stderr[-300:]}", file=sys.stderr)
        return None
    match = re.search(r"\ncodex\n(.*?)\ntokens used\n", result.stdout, re.S)
    return match.group(1).strip() if match else result.stdout.strip()


def _run_agy_prompt(prompt: str, timeout_s: int = AGY_TIMEOUT_S) -> str | None:
    """Thử agy trước (nhanh, đã dùng ổn định xuyên suốt dự án); rơi xuống
    Codex CLI nếu agy chưa cài/lỗi/hết quota (pool riêng, không liên quan
    quota agy) -- không để 1 tầng hết quota làm sập cả batch (đã gặp thật:
    agy TEXT quota cạn giữa lúc xử lý EP006)."""
    if AGY_BIN.exists():
        try:
            result = subprocess.run([str(AGY_BIN), "-p", prompt], capture_output=True, text=True, timeout=timeout_s)
            if result.returncode == 0:
                return result.stdout
            print(f"CẢNH BÁO: agy lỗi (exit {result.returncode}): {result.stderr[-300:]} -- thử Codex.", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"CẢNH BÁO: agy timeout sau {timeout_s}s -- thử Codex.", file=sys.stderr)
    return _run_codex_text(prompt)


def batch_score_typography_suitability(
    beats: list[Beat], core_insight: str, chunk_size: int = 80,
) -> dict[int, float]:
    """Chấm điểm 0-10 mức độ phù hợp làm THẺ CHỮ LỚN (typography quote-card)
    cho MỌI beat -- dùng để XẾP HẠNG chọn top-N theo quota tỷ lệ (khác hẳn
    cơ chế luật cứng aphorism-marker cũ, vốn chỉ tìm được rất ít câu, không
    đủ cho quota lớn như 20% của cả tập). Chunk nếu tập dài (vd 500+ beat)
    -- 1 lệnh agy/chunk, không phải 1 lệnh/beat, vẫn giữ số lệnh gọi nhỏ và
    có kiểm soát (vài lệnh/tập thay vì hàng trăm)."""
    scores: dict[int, float] = {}
    for offset, chunk in _chunked(beats, chunk_size):
        items = "\n".join(f"{offset + i}: {b.text}" for i, b in enumerate(chunk))
        prompt = (
            "Bạn là biên tập video, đang chọn câu thoại phù hợp làm THẺ CHỮ LỚN "
            "(typography quote-card) hiển thị giữa màn hình vài giây.\n"
            f"Ý chính (Core Insight) của tập: {core_insight or '(không có)'}\n\n"
            "Với MỖI câu dưới đây (đánh số), cho điểm 0-10: câu càng ĐỘC LẬP về nghĩa "
            "(đọc rời khỏi ngữ cảnh vẫn hiểu được), súc tích, có sức nặng châm ngôn/insight/"
            "câu hỏi gợi mở thì điểm CÀNG CAO; câu càng miêu tả sự việc cụ thể, phụ thuộc "
            "câu trước/sau, hoặc quá dài (>25 từ) thì điểm CÀNG THẤP.\n\n"
            f"{items}\n\n"
            f'Trả lời CHỈ 1 JSON object dạng {{"index": score}}, đúng {len(chunk)} phần tử, không giải thích.'
        )
        stdout = _run_agy_prompt(prompt)
        if not stdout:
            continue
        result = _extract_json_object(stdout)
        for k, v in (result or {}).items():
            try:
                scores[int(k)] = float(v)
            except (ValueError, TypeError):
                continue
    return scores


def batch_score_video_suitability(beats: list[Beat], bible: dict, chunk_size: int = 80) -> dict[int, float]:
    """Chấm điểm 0-10 khả năng minh hoạ bằng VIDEO STOCK THỰC TẾ cho MỌI
    beat còn lại (sau khi đã tách typography) -- dùng để xếp hạng chọn
    top-N theo quota. ĐÂY LÀ BẢN "NỚI RULE" theo yêu cầu: thay vì chỉ chấp
    nhận đúng vài cảnh cụ thể mà Director Bible liệt kê
    (pexels_acceptance_policy, quá hẹp để đạt tỷ lệ video cao), giờ diễn
    giải RỘNG RÃI hơn hẳn -- chỉ cần gợi đúng KHÔNG KHÍ/CHỦ ĐỀ, không cần
    khớp chính xác câu chữ."""
    image_policy = bible.get("image_policy", {}) if isinstance(bible.get("image_policy"), dict) else {}
    style = image_policy.get("style_descriptor", "")
    scores: dict[int, float] = {}
    for offset, chunk in _chunked(beats, chunk_size):
        items = "\n".join(f"{offset + i}: {b.text}" for i, b in enumerate(chunk))
        prompt = (
            "Bạn là biên tập video, đang chọn beat nào nên minh hoạ bằng VIDEO STOCK THỰC TẾ "
            "(cảnh quay có sẵn trên kho video, khác với ảnh AI vẽ riêng).\n"
            f"Phong cách hình ảnh chung của tập (dùng cho phần còn lại, không phải video): {style}\n\n"
            "Với MỖI câu dưới đây (đánh số), cho điểm 0-10 khả năng có thể minh hoạ HỢP LÝ bằng 1 "
            "cảnh video thực tế đời thường/thiên nhiên/con người/không gian tôn giáo chung chung -- "
            "KHÔNG cần khớp chính xác câu chữ, chỉ cần có 1 cảnh THỰC TẾ nào đó gợi đúng KHÔNG KHÍ/"
            "CHỦ ĐỀ của câu là được (diễn giải RỘNG RÃI, thoáng -- mục tiêu là dùng video cho PHẦN LỚN "
            "nội dung, không phải chỉ những cảnh khớp tuyệt đối). Câu càng cần 1 hình ảnh biểu tượng/ẩn "
            "dụ tôn giáo RẤT ĐẶC THÙ (tên riêng kinh sách, khái niệm trừu tượng không có cảnh thực tế "
            "tương ứng) thì điểm càng thấp.\n\n"
            f"{items}\n\n"
            f'Trả lời CHỈ 1 JSON object dạng {{"index": score}}, đúng {len(chunk)} phần tử, không giải thích.'
        )
        stdout = _run_agy_prompt(prompt)
        if not stdout:
            continue
        result = _extract_json_object(stdout)
        for k, v in (result or {}).items():
            try:
                scores[int(k)] = float(v)
            except (ValueError, TypeError):
                continue
    return scores


def batch_translate_visual_hints(
    beats: list[Beat], bible: dict, chunk_size: int = 80, context_label: str = "Phật giáo/tâm linh",
) -> dict[int, str]:
    """1 vài lệnh gọi agy (Antigravity CLI, đã dùng cho content_seo.py/
    content_review.py -- xem docstring 2 file đó), CHUNK nếu tập dài
    (không phải 1 lệnh/beat -- tránh tốn quota Google theo số lượng beat,
    giữ đúng nguyên tắc "1 lệnh/tập" đã dùng cho Director Bible, chỉ khác
    là chia nhỏ thành vài lệnh khi N lớn để tránh response quá dài/kém
    chất lượng). Dịch + rút gọn nội dung hình ảnh cụ thể của từng beat
    IMAGE sang tiếng Anh ngắn (~8-12 từ) -- CLIP (bộ mã hoá văn bản của
    SDXL) hiểu tiếng Anh tốt hơn hẳn tiếng Việt trừu tượng, thiếu bước
    này thì ảnh sinh ra đúng TÔNG chung nhưng không bám sát NỘI DUNG riêng
    của từng beat (đã xác nhận qua test trực tiếp, xem _build_image_prompt()).

    Trả về {beat_index: english_hint}. Lỗi bất kỳ (agy chưa cài, quota,
    JSON không hợp lệ, thiếu/lệch số phần tử...) -- bỏ qua chunk đó, caller
    tự fallback về _natural_content_hint() tiếng Việt cho beat thiếu, không
    để 1 lỗi agy làm sập cả batch."""
    if not beats or not AGY_BIN.exists():
        return {}

    image_policy = bible.get("image_policy", {}) if isinstance(bible.get("image_policy"), dict) else {}
    style = image_policy.get("style_descriptor", "")

    hints: dict[int, str] = {}
    for offset, chunk in _chunked(beats, chunk_size):
        items = "\n".join(f"{offset + i}: {b.text}" for i, b in enumerate(chunk))
        prompt = (
            f"Bạn là đạo diễn hình ảnh cho 1 video {context_label} tiếng Việt.\n"
            f"Phong cách hình ảnh chung của tập: {style}\n\n"
            "Với MỖI câu thoại dưới đây (đánh số), viết 1 mô tả hình ảnh NGẮN GỌN bằng "
            "TIẾNG ANH (8-12 từ), cụ thể, tả được 1 cảnh/hình ảnh có thể vẽ minh hoạ được -- "
            "không dịch nguyên văn triết lý trừu tượng, mà hình dung ra 1 hình ảnh ẩn dụ/tượng "
            "trưng phù hợp với ý câu đó (vd đôi vai gánh nặng, ánh đèn trước tượng Phật, bàn tay "
            "nâng bát nước, đá đè lên bùn...).\n\n"
            f"{items}\n\n"
            "Trả lời CHỈ 1 JSON array of strings tiếng Anh, đúng thứ tự số ở trên, không giải "
            f"thích gì thêm khác. Phải có đúng {len(chunk)} phần tử."
        )
        stdout = _run_agy_prompt(prompt)
        if not stdout:
            continue
        result = _extract_json_array(stdout)
        if not isinstance(result, list) or len(result) != len(chunk):
            print(
                f"CẢNH BÁO: agy trả về {len(result) if isinstance(result, list) else 'không phải'} phần tử, "
                f"cần đúng {len(chunk)} -- bỏ qua chunk này, dùng fallback tiếng Việt.", file=sys.stderr,
            )
            continue
        for i, h in enumerate(result):
            hints[offset + i] = str(h)
    return hints


# 0=Bắc(trên), xuôi kim đồng hồ -- CÙNG quy ước la bàn đã dùng vẽ sơ đồ
# bát quái (generate_symbol_assets.py::generate_bat_quai()) để nhất quán
# trong toàn bộ domain. Đưa thẳng bảng số vào prompt thay vì để agy tự tính góc
# -- rủi ro sai lệch thật (nội dung hướng nhà sai là sai kiến thức, không
# chỉ "không đẹp", cùng mức cẩn trọng đã áp dụng cho Bát Quái/Ngũ Hành).
_DIRECTION_ANGLE_TABLE = {
    "Bắc": 0, "Đông Bắc": 45, "Đông": 90, "Đông Nam": 135,
    "Nam": 180, "Tây Nam": 225, "Tây": 270, "Tây Bắc": 315,
}


def batch_detect_diagram_beats(
    beats: list[Beat], context_label: str, base_image_style: str, chunk_size: int = 60,
) -> dict[int, dict]:
    """Trong các beat đã phân loại IMAGE, tìm beat nào THẬT SỰ đang mô tả
    hướng/khu vực cụ thể gắn với 1 ý nghĩa (vd "hướng Đông Nam là góc tài
    lộc") -- loại nội dung này hợp hơn với DIAGRAM (ảnh nền + mũi tên/nhãn
    chỉ đúng hướng qua Remotion) hơn là 1 ảnh minh hoạ tĩnh thông thường.
    Chỉ dùng cho domain có `supports_diagram_treatment=true` (xem
    domain_creative_profiles.json) -- caller chịu trách nhiệm không gọi
    hàm này cho domain không hợp (vd Phật giáo không có khái niệm hướng
    nhà kiểu này).

    Trả về {beat_index: {"base_image_prompt": str, "annotations": [{"label":str,"angleDeg":float}]}}
    -- CHỈ gồm các beat THẬT SỰ khớp (không phải mọi beat). Lỗi bất kỳ
    (agy chưa cài, quota, JSON không hợp lệ...) -- trả về {} rỗng, caller
    giữ nguyên các beat đó ở treatment IMAGE bình thường (an toàn, không
    mất nội dung)."""
    if not beats or not AGY_BIN.exists():
        return {}

    direction_lines = "\n".join(f"- {name}: {angle}" for name, angle in _DIRECTION_ANGLE_TABLE.items())
    results: dict[int, dict] = {}
    for offset, chunk in _chunked(beats, chunk_size):
        items = "\n".join(f"{offset + i}: {b.text}" for i, b in enumerate(chunk))
        prompt = (
            f"Bạn là đạo diễn hình ảnh cho 1 video {context_label} tiếng Việt.\n"
            "Bảng góc la bàn CHUẨN (0=Bắc/trên cùng, xuôi kim đồng hồ) -- PHẢI dùng ĐÚNG số này, không tự tính:\n"
            f"{direction_lines}\n\n"
            "Với MỖI câu dưới đây (đánh số), xác định câu đó có đang mô tả 1 HƯỚNG/KHU VỰC CỤ THỂ gắn với "
            "1 Ý NGHĨA hay không (vd \"hướng Đông Nam là góc tài lộc\", \"hướng Bắc hợp sự nghiệp\") -- "
            "CHỈ tính khi câu nêu rõ ít nhất 1 hướng trong bảng trên VÀ ý nghĩa/công dụng gắn với hướng đó. "
            "Câu chỉ nhắc chung chung không có hướng cụ thể thì KHÔNG tính.\n\n"
            f"{items}\n\n"
            f"Trả lời CHỈ 1 JSON object, key là số thứ tự câu KHỚP (bỏ qua câu không khớp), "
            "value dạng: {{\"base_image_prompt\": \"mô tả ảnh nền tiếng Anh ngắn 8-12 từ, "
            f"phong cách: {base_image_style}, KHÔNG mô tả hướng/mũi tên gì cả (phần đó vẽ đè lên sau)\", "
            "\"annotations\": [{{\"label\": \"tên ý nghĩa ngắn tiếng Việt (vd Tài Lộc)\", \"angleDeg\": <số từ bảng trên>}}, ...]}}. "
            "Không giải thích gì thêm ngoài JSON."
        )
        stdout = _run_agy_prompt(prompt)
        if not stdout:
            continue
        parsed = _extract_json_object(stdout)
        if not isinstance(parsed, dict):
            print("CẢNH BÁO: agy không trả JSON object hợp lệ khi phát hiện diagram beat -- bỏ qua chunk này.", file=sys.stderr)
            continue
        for key, value in parsed.items():
            try:
                idx = int(key)
            except (TypeError, ValueError):
                continue
            if not (offset <= idx < offset + len(chunk)):
                continue
            if not isinstance(value, dict) or not value.get("annotations"):
                continue
            results[idx] = value
    return results


def batch_translate_video_keywords(beats: list[Beat], chunk_size: int = 80) -> dict[int, str]:
    """Giống batch_translate_visual_hints() nhưng cho beat VIDEO -- dịch
    sang cụm từ khoá tiếng Anh NGẮN (3-5 từ) để tìm kiếm trên Pexels/
    Pixabay, không phải mô tả cảnh đầy đủ. Trước đây beat VIDEO dùng
    _extract_keywords() (rút "vài từ dài nhất" từ câu tiếng Việt gốc, xáo
    trộn thứ tự) -- ra chuỗi vô nghĩa kiểu "thương người người ngày" khi
    làm search query, gần như chắc chắn khớp sai/không ra kết quả tốt trên
    Pexels (đúng lỗi "video không khớp nội dung" đã gặp và cố tránh từ đầu
    phiên). Cụm từ khoá tiếng Anh ngắn, cụ thể (vd "empty wooden chair
    warm light") tìm được kết quả liên quan hơn hẳn."""
    if not beats or not AGY_BIN.exists():
        return {}
    keywords: dict[int, str] = {}
    for offset, chunk in _chunked(beats, chunk_size):
        items = "\n".join(f"{offset + i}: {b.text}" for i, b in enumerate(chunk))
        prompt = (
            "Bạn đang chọn từ khoá tìm kiếm video stock (Pexels/Pixabay) để minh hoạ cho từng câu thoại.\n\n"
            "Với MỖI câu dưới đây (đánh số), viết 1 cụm từ khoá TIẾNG ANH NGẮN (3-5 từ) mô tả 1 CẢNH THỰC "
            "TẾ cụ thể (vd \"empty wooden chair warm light\", \"elderly person walking slowly\", \"candle "
            "flame close up\") -- phải là cảnh có thể QUAY THẬT được, không phải khái niệm trừu tượng.\n\n"
            f"{items}\n\n"
            "Trả lời CHỈ 1 JSON array of strings tiếng Anh, đúng thứ tự số ở trên, không giải thích gì "
            f"thêm khác. Phải có đúng {len(chunk)} phần tử."
        )
        stdout = _run_agy_prompt(prompt)
        if not stdout:
            continue
        result = _extract_json_array(stdout)
        if not isinstance(result, list) or len(result) != len(chunk):
            continue
        for i, kw in enumerate(result):
            keywords[offset + i] = str(kw)
    return keywords


def _extract_keywords(text: str, max_words: int = 4) -> str:
    """Rút keyword thô cho tìm kiếm Pexels/Pixabay -- v1 đơn giản (bỏ từ
    ngắn/hư từ phổ biến, lấy vài từ dài nhất). asset_generation.py có thể
    tái dùng core/stockfootage/keyword_extract.py + translate.py của
    video-editor (TF-IDF + dịch sang tiếng Anh) cho bản đầy đủ hơn -- hàm
    này chỉ là fallback nhanh không cần venv riêng."""
    stopwords = {"và", "của", "là", "có", "một", "những", "các", "được", "cho", "này", "đó", "khi", "để", "không", "đã", "sẽ"}
    words = [w.strip(".,!?;:\"'") for w in text.split()]
    candidates = [w for w in words if len(w) > 3 and w.lower() not in stopwords]
    candidates.sort(key=len, reverse=True)
    return " ".join(candidates[:max_words]) if candidates else text[:40]


def _natural_content_hint(text: str, max_words: int = 15) -> str:
    """Lấy N từ ĐẦU câu, GIỮ NGUYÊN thứ tự gốc -- khác _extract_keywords()
    (xáo trộn theo độ dài từ, hợp cho search engine nhưng ra chuỗi vô nghĩa
    khi làm prompt sinh ảnh). Giữ thứ tự tự nhiên vẫn cho CLIP cơ hội nắm
    được cụm từ/ngữ cảnh cục bộ, dù CLIP vốn yếu với tiếng Việt trừu tượng
    -- đây là phần "hương vị" nội dung riêng của beat, phần chịu trách
    nhiệm chính cho tính đúng-thị-giác vẫn là motif cụ thể (favor_subjects)
    được chọn riêng cho beat này, xem _build_image_prompt()."""
    words = text.strip().split()
    return " ".join(words[:max_words])


def _build_image_prompt(
    text: str, visual_motif: str, bible: dict, beat_index: int = 0, english_hint: str = "",
    style_anchor: str = "Respectful Vietnamese Buddhist reflection illustration, digital oil painting, "
    "warm muted earth tones, solemn contemplative mood",
) -> str:
    """PHẢI ngắn -- CLIP text encoder của SDXL cắt cứng ở 77 token, quá đó
    coi như model không hề "thấy". Bug từng có: nhồi nguyên `visual_motif`
    (bài luận ~1500+ ký tự giải thích ẩn dụ cho CẢ tập, không phải gợi ý
    ảnh ngắn cho 1 beat) + toàn bộ favor/avoid list vào MỖI beat -- vượt
    token budget cỡ 10 lần, phần sống sót qua truncation gần như luôn là
    đoạn mở đầu giống hệt nhau ở mọi beat, không phải nội dung riêng của
    từng beat.

    Lần sửa thứ nhất (chỉ bỏ phần dư, giữ nguyên tiếng Việt) RA ẢNH TỆ HƠN:
    bản gốc dù bị cắt vẫn còn giữ được cụm mở đầu tiếng Anh "A single
    symbolic, respectful illustration for a Vietnamese Buddhist reflection
    video" -- CLIP hiểu tiếng Anh tốt hơn hẳn tiếng Việt trừu tượng, cụm
    đó chính là thứ neo đúng phong cách/tông màu. Giữ neo tiếng Anh cố
    định, nhưng thử nghiệm cho thấy PHẦN NỘI DUNG RIÊNG của từng beat vẫn
    cần ở dạng tiếng Anh mới thực sự "vào" được CLIP -- content tiếng Việt
    dù ngắn cũng gần như bị model bỏ qua, ảnh đúng tông chung nhưng không
    bám nội dung câu thoại. `english_hint` (từ batch_translate_visual_hints(),
    dịch 1 lần cho cả tập) ưu tiên dùng khi có; fallback về
    _natural_content_hint() tiếng Việt (vẫn còn hơn không) khi dịch lỗi/
    thiếu API key."""
    image_policy = bible.get("image_policy", {}) if isinstance(bible.get("image_policy"), dict) else {}
    favor = image_policy.get("favor_subjects") or []

    content_hint = english_hint.strip() if english_hint else _natural_content_hint(text, max_words=10)
    motif_hint = favor[beat_index % len(favor)] if favor else ""

    parts = [style_anchor, content_hint, motif_hint, "16:9"]
    return ", ".join(p for p in parts if p)


def _pick_typography_style(text: str, is_core_insight: bool) -> str:
    """4 style animation Remotion (xem remotion_typography/src/) -- FLIP_3D
    dành riêng cho câu trùng Core Insight (hiệu ứng mạnh nhất, chỉ 1 lần/
    tập để giữ impact), còn lại theo độ dài câu."""
    word_count = len(text.split())
    if is_core_insight:
        return "flip_3d"
    if word_count <= 8:
        return "pop_in"
    if word_count <= 15:
        return "rise_up"
    return "word_cascade"


def _typography_font_size(word_count: int) -> int:
    """Câu càng ngắn/càng "đắt" thì chữ càng to -- % chiều cao khung hình
    1080p, cùng công thức đã dùng cho phiên bản ASS cũ, giữ nhất quán khi
    chuyển sang Remotion."""
    if word_count <= 8:
        pct = 0.075
    elif word_count <= 15:
        pct = 0.060
    else:
        pct = 0.048
    return max(32, min(130, round(1080 * pct)))


def _finalize_beat(
    beat: Beat, treatment: Treatment, source: str, visual_motif: str, motion_idx: list[int],
    bible: dict, motion_cycle: list[str], core_insight: str = "", english_hint: str = "",
    video_keyword: str = "", style_anchor: str | None = None,
) -> None:
    beat.treatment = treatment.value
    beat.source = source
    if treatment == Treatment.IMAGE:
        beat.motion_mode = motion_cycle[motion_idx[0] % len(motion_cycle)]
        image_prompt_kwargs = {"style_anchor": style_anchor} if style_anchor else {}
        beat.prompt_or_keywords = _build_image_prompt(beat.text, visual_motif, bible, motion_idx[0], english_hint, **image_prompt_kwargs)
        motion_idx[0] += 1
    elif treatment == Treatment.DIAGRAM:
        # base_image_prompt đã soạn sẵn, sạch, riêng cho ảnh NỀN (không mô
        # tả hướng/mũi tên -- phần đó Remotion vẽ đè lên sau) -- dùng thẳng,
        # KHÔNG qua _build_image_prompt() (sẽ thêm style_anchor/motif chung
        # không hợp bố cục ảnh nền cho diagram).
        beat.motion_mode = motion_cycle[motion_idx[0] % len(motion_cycle)]
        beat.prompt_or_keywords = english_hint.strip() or _natural_content_hint(beat.text, max_words=10)
        motion_idx[0] += 1
    elif treatment == Treatment.VIDEO:
        # Ưu tiên từ khoá tiếng Anh đã dịch (xem batch_translate_video_keywords())
        # -- fallback về _extract_keywords() tiếng Việt thô nếu agy lỗi/chưa cài.
        beat.prompt_or_keywords = video_keyword.strip() if video_keyword else _extract_keywords(beat.text)
    elif treatment == Treatment.TYPOGRAPHY and beat.typography_card:
        is_core_insight = bool(core_insight) and _fuzzy_contains(core_insight, beat.text)
        beat.typography_style = _pick_typography_style(beat.text, is_core_insight)
        beat.typography_font_size_px = _typography_font_size(len(beat.text.split()))
    # TYPOGRAPHY (typography_card=False, đoạn dài fallback): không cần
    # prompt/style riêng -- audio_tool_render.py tự dựng nền màu + giữ phụ
    # đề thường, xem _is_typography_card() bên đó.


PREMIUM_BEAT_MAX_COUNT = 8
_COMPLEXITY_HINT_WORDS = (
    "people", "family", "children", "child", "hands", "hand", "group",
    "crowd", "several", "elder", "elders", "monks", "many", "together",
    "holding", "gathered",
)


def select_premium_beats(beats: list[Beat], core_insight: str, max_count: int = PREMIUM_BEAT_MAX_COUNT) -> None:
    """Đánh dấu beat.premium=True cho tối đa `max_count` beat IMAGE quan
    trọng/phức tạp nhất -- dùng để quyết định thử Codex CLI/agy (chất
    lượng cao hơn hẳn ComfyUI, đặc biệt tay/mặt, nhưng chậm + tốn token,
    không kham nổi cho MỌI beat) trước khi rơi về ComfyUI cho phần còn
    lại. Ưu tiên: (1) khớp Core Insight của tập -- beat quan trọng nhất
    về mặt Ý NGHĨA, (2) mô tả cảnh đông người/nhiều chi tiết phức tạp
    (dựa theo prompt tiếng Anh đã dịch -- keyword đơn giản đủ dùng, không
    cần thêm 1 lệnh agy riêng chỉ để phân loại việc này)."""
    image_beats = [b for b in beats if b.treatment == "image"]
    if not image_beats:
        return

    def score(b: Beat) -> float:
        s = 0.0
        if core_insight and _fuzzy_contains(core_insight, b.text):
            s += 10.0
        hint = (b.prompt_or_keywords or "").lower()
        s += sum(1.0 for w in _COMPLEXITY_HINT_WORDS if w in hint)
        return s

    ranked = sorted(image_beats, key=score, reverse=True)
    for b in ranked[:max_count]:
        b.premium = True


def _build_shot_list_by_ratio(
    sentences: list[dict], target_beat_sec: float, treatment_ratio: dict, core_insight: str,
    visual_motif: str, bible: dict, motion_cycle: list[str], output_path: str,
    profile: dict | None = None,
) -> list[Beat]:
    """Nhánh phân bổ theo TỶ LỆ CỐ ĐỊNH (vd 60% video/20% ảnh/20%
    typography) -- khác hẳn nhánh mặc định (bible tự quyết định độc lập
    từng beat, không có mục tiêu tỷ lệ tổng). Dùng khi người biên tập
    muốn ép cơ chế đầu ra theo đúng tỷ lệ, bất kể nội dung tập trừu tượng
    hay cụ thể đến đâu.

    Thuật toán: gộp TOÀN BỘ câu thành beat trước (không tách riêng
    typography ở cấp câu như nhánh mặc định), rồi CHẤM ĐIỂM xếp hạng toàn
    bộ beat cho typography-suitability và video-suitability (2-3 lệnh agy
    tuỳ độ dài tập, xem batch_score_*), chọn đúng top-N theo quota mỗi
    loại. Xếp hạng đảm bảo LUÔN đạt đúng số lượng mục tiêu (khác nhánh mặc
    định vốn có thể ra 0 video nếu không có beat nào khớp luật).

    Beat khớp domain_creative_profiles.json symbol_library (vd "Bát Quái")
    bị RÚT KHỎI vòng xếp hạng typography/video TRƯỚC khi tính quota -- ép
    thẳng IMAGE, dùng asset tĩnh đã kiểm chứng (render_mode=static_asset)
    hoặc prompt tiếng Anh đã soạn sẵn (render_mode=ai_generate_ok), không
    phó mặc cho agy dịch/xếp hạng như beat thường (xem phiên làm việc: test
    thật cho thấy AI vẽ sai sơ đồ Bát Quái, cần asset chính xác dựng sẵn)."""
    profile = profile or creative_profiles.load_profile(None)
    context_label = profile.get("context_label", "Phật giáo/tâm linh")
    style_anchor = profile.get("image_style_anchor")

    all_beats = group_segments_into_beats(sentences, target_sec=target_beat_sec)
    n_total = len(all_beats)

    symbol_by_index: dict[int, dict] = {}
    for i, beat in enumerate(all_beats):
        entry = creative_profiles.resolve_symbol(profile, beat.text)
        if entry is None:
            continue
        beat.symbol_key = entry["key"]
        # entry.get("safety_critical") PHẢI luôn gọi pick_symbol_asset_path()
        # dù thiếu render_mode/asset_path -- guard cũ (chỉ gọi khi có sẵn
        # asset_path) khiến entry safety_critical cấu hình lỗi/thiếu path
        # BỎ QUA HOÀN TOÀN chặn an toàn tên người thật, không ai biết
        # (Codex review điểm #1 vòng 3, xem docstring pick_symbol_asset_path).
        if entry.get("safety_critical") or (entry.get("render_mode") == "static_asset" and (entry.get("asset_paths") or entry.get("asset_path"))):
            beat.symbol_asset_path = creative_profiles.pick_symbol_asset_path(entry)
        symbol_by_index[i] = entry

    eligible_indices = [i for i in range(n_total) if i not in symbol_by_index]
    n_typography = round(n_total * treatment_ratio.get("typography", 0.0))
    n_video = round(n_total * treatment_ratio.get("video", 0.0))

    eligible_beats = [all_beats[i] for i in eligible_indices]
    typo_scores = batch_score_typography_suitability(eligible_beats, core_insight)
    ranked_typo_local = sorted(range(len(eligible_beats)), key=lambda i: -typo_scores.get(i, 0.0))
    typography_indices = {eligible_indices[i] for i in ranked_typo_local[:n_typography]}

    remaining_indices = [i for i in eligible_indices if i not in typography_indices]
    # G3 (Video Generation remediation): beat khớp domain_creative_profiles.
    # json's video_unsafe_terms (vd chủ đề pháp lý chung chung của CL --
    # "hình phạt"/"phạm tội"...) KHÔNG được chọn Treatment.VIDEO (tránh
    # catalog Pexels tự thiên lệch, xem is_video_unsafe_topic() docstring)
    # -- loại khỏi candidate pool NGAY TỪ ĐẦU (trước khi chấm điểm/xếp
    # hạng), không phải lọc SAU khi đã chọn, để không bao giờ có thể lọt
    # vào video_indices dù điểm suitability cao thế nào. KHÁC symbol_library
    # (loại hẳn khỏi eligible_indices phía trên) -- ở đây vẫn được xét
    # TYPOGRAPHY/IMAGE bình thường, chỉ riêng VIDEO là không.
    video_candidate_indices = [
        i for i in remaining_indices if not creative_profiles.is_video_unsafe_topic(profile, all_beats[i].text)
    ]
    video_candidate_beats = [all_beats[i] for i in video_candidate_indices]
    video_scores = batch_score_video_suitability(video_candidate_beats, bible)
    ranked_video_local = sorted(range(len(video_candidate_beats)), key=lambda i: -video_scores.get(i, 0.0))
    video_indices = {video_candidate_indices[i] for i in ranked_video_local[:n_video]}

    classified: list[tuple[Beat, Treatment, str]] = []
    for i, beat in enumerate(all_beats):
        if i in symbol_by_index:
            treatment, source = Treatment.IMAGE, "symbol_library"
        elif i in typography_indices:
            treatment, source = Treatment.TYPOGRAPHY, "ratio"
        elif i in video_indices:
            treatment, source = Treatment.VIDEO, "ratio"
        else:
            treatment, source = Treatment.IMAGE, "ratio"
        classified.append((beat, treatment, source))

    # Beat IMAGE khớp symbol_library KHÔNG cần agy dịch prompt -- static_asset
    # không dùng prompt gì cả, ai_generate_ok đã có image_prompt_hint soạn sẵn
    # trong profile (chính xác/ổn định hơn để agy tự dịch lại mỗi lần).
    image_beats = [beat for beat, treatment, _ in classified if treatment == Treatment.IMAGE and beat.symbol_key is None]
    visual_hints = batch_translate_visual_hints(image_beats, bible, context_label=context_label)
    hint_by_start = {image_beats[i].start: hint for i, hint in visual_hints.items() if i < len(image_beats)}
    for i, entry in symbol_by_index.items():
        prompt_hint = entry.get("image_prompt_hint")
        if prompt_hint:
            hint_by_start[all_beats[i].start] = prompt_hint

    # Beat DIAGRAM (ảnh nền + mũi tên/nhãn chỉ hướng qua Remotion) -- chỉ
    # xét cho domain hỗ trợ (vd Phong Thuỷ), trong số beat IMAGE không phải
    # symbol_library (Bát Quái/Ngũ Hành đã có asset cố định riêng, không
    # phải nội dung "thay đổi theo tập" mà DIAGRAM nhắm tới).
    diagram_starts: set[float] = set()
    if profile.get("supports_diagram_treatment"):
        diagram_matches = batch_detect_diagram_beats(image_beats, context_label, profile.get("diagram_base_image_style", ""))
        for local_idx, value in diagram_matches.items():
            if local_idx >= len(image_beats):
                continue
            beat = image_beats[local_idx]
            beat.diagram_annotations = value.get("annotations")
            diagram_starts.add(beat.start)
            if value.get("base_image_prompt"):
                hint_by_start[beat.start] = value["base_image_prompt"]
    if diagram_starts:
        classified = [
            (beat, Treatment.DIAGRAM if beat.start in diagram_starts else treatment, source)
            for beat, treatment, source in classified
        ]

    video_beats = [beat for beat, treatment, _ in classified if treatment == Treatment.VIDEO]
    video_keywords = batch_translate_video_keywords(video_beats)
    keyword_by_start = {video_beats[i].start: kw for i, kw in video_keywords.items() if i < len(video_beats)}

    motion_idx = [0]
    for beat, treatment, source in classified:
        if treatment == Treatment.TYPOGRAPHY:
            # An toàn cho beat dài bị quota ép chọn dù điểm không cao (xếp
            # hạng vẫn phải lấy đủ top-N) -- nếu quá dài để làm thẻ chữ gọn
            # gàng, hạ xuống nền màu phẳng + phụ đề thường thay vì tràn chữ
            # (đúng bug đã gặp và fix trước đây cho nhánh fallback runtime).
            beat.typography_card = len(beat.text.split()) <= TYPOGRAPHY_MAX_WORDS
        _finalize_beat(
            beat, treatment, source, visual_motif, motion_idx, bible, motion_cycle,
            core_insight, english_hint=hint_by_start.get(beat.start, ""),
            video_keyword=keyword_by_start.get(beat.start, ""), style_anchor=style_anchor,
        )

    n_typo_actual = sum(1 for b in all_beats if b.treatment == "typography")
    n_video_actual = sum(1 for b in all_beats if b.treatment == "video")
    n_image_actual = sum(1 for b in all_beats if b.treatment == "image")
    n_diagram_actual = sum(1 for b in all_beats if b.treatment == "diagram")
    select_premium_beats(all_beats, core_insight)
    n_premium = sum(1 for b in all_beats if b.premium)
    print(
        f"Đạo diễn (tỷ lệ cố định {treatment_ratio}): {n_total} beat -- "
        f"typography {n_typo_actual}/{n_typography} mục tiêu, "
        f"video {n_video_actual}/{n_video} mục tiêu, "
        f"image {n_image_actual} (phần còn lại, {n_premium} premium cho Codex/agy), "
        f"diagram {n_diagram_actual} (hướng/khu vực cụ thể, vẽ mũi tên qua Remotion), "
        # diagram_starts LÀ TẬP CON của image_beats (beat diagram vốn được
        # phân loại IMAGE trước khi phát hiện lại) -- không cộng dồn 2 lần.
        f"{len(hint_by_start)}/{len(image_beats)} beat IMAGE+DIAGRAM dịch prompt tiếng Anh, "
        f"{len(keyword_by_start)}/{len(video_beats)} beat VIDEO dịch từ khoá Pexels thành công.",
        flush=True,
    )

    out = {
        "visual_motif": visual_motif, "core_insight": core_insight,
        "director_bible": bible, "beats": [asdict(b) for b in all_beats],
    }
    Path(output_path).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return all_beats


def build_shot_list(
    segments_json_path: str,
    output_path: str,
    episode_planner_path: str | None = None,
    gemini_api_key: str | None = None,
    bible: dict | None = None,
    target_beat_sec_override: float | None = None,
    treatment_ratio: dict | None = None,
    creative_profile: dict | None = None,
) -> list[Beat]:
    """`bible` (Director Bible, xem director_bible.py) LÀ RÀNG BUỘC cho mọi
    quyết định ở đây -- không còn tự phân loại độc lập từng beat bằng luật
    cứng giống nhau cho mọi tập. Luật rule-based (classify_beat_rule_based)
    giờ chỉ còn vai trò LỌC SƠ BỘ ứng viên (câu có đủ ngắn để CÓ THỂ là
    typography không); quyết định cuối cùng (dùng bao nhiêu, hướng camera
    nào, tông ảnh ra sao) đến từ bible. Nếu không truyền bible, dùng
    director_bible.DEFAULT_BIBLE (trung tính, không đặc thù theo tập).

    `creative_profile` (xem domain_creative_profiles.py) quyết định khung
    cảnh domain cho các lệnh gọi agy/Gemini (context_label, tone, style
    anchor ảnh) + symbol_library (ký hiệu cố định như Bát Quái/Thanh Long,
    xem resolve_symbol()). Không truyền -> rơi về profile BUD, đúng hành
    vi hardcode "Phật giáo/tâm linh" trước khi có domain_creative_profiles."""
    bible = bible or director_bible.DEFAULT_BIBLE
    profile = creative_profile or creative_profiles.load_profile(None)
    context_label = profile.get("context_label", "Phật giáo/tâm linh")
    tone_label = profile.get("tone_label", "giọng trang nghiêm, tôn trọng")
    style_anchor = profile.get("image_style_anchor")

    data = json.loads(Path(segments_json_path).read_text(encoding="utf-8"))
    segments = data["segments"]
    sentences = segments_to_sentences(segments)

    ctx = read_episode_planner_context(Path(episode_planner_path) if episode_planner_path else None)
    core_insight = ctx["core_insight"]
    visual_motif = ctx["visual_motif"]

    if target_beat_sec_override is not None:
        # Ghi đè thủ công (vd --target-beat-sec) -- ưu tiên hơn quyết định
        # nhịp dựng của bible. Dùng khi người biên tập muốn đổi tông dựng
        # nhanh/chậm rõ ràng cho 1 tập cụ thể, bất kể Gemini đã tự chọn gì.
        target_beat_sec = max(3.0, min(35.0, target_beat_sec_override))
    else:
        editing_rhythm = bible.get("editing_rhythm", {}) if isinstance(bible.get("editing_rhythm"), dict) else {}
        target_beat_sec = float(editing_rhythm.get("target_beat_sec") or TARGET_BEAT_SEC)
        target_beat_sec = max(10.0, min(35.0, target_beat_sec))  # giới hạn an toàn, tránh bible trả giá trị bất thường

    typography_policy = bible.get("typography_policy", {}) if isinstance(bible.get("typography_policy"), dict) else {}
    typography_max_count = int(typography_policy.get("max_count") or 3)

    motion_cycle = _motion_cycle_from_bible(bible)
    pexels_hints = extract_pexels_hints(bible)

    if treatment_ratio is not None:
        return _build_shot_list_by_ratio(
            sentences, target_beat_sec, treatment_ratio, core_insight, visual_motif,
            bible, motion_cycle, output_path, profile=profile,
        )

    # Pass 1 -- xét TYPOGRAPHY ở cấp độ CÂU (không phải beat gộp ~20s): chỉ
    # ở cấp độ này mới còn giữ được tín hiệu "câu ngắn/châm ngôn" của 1 câu
    # đơn lẻ, thay vì bị pha loãng khi gộp chung với các câu xung quanh.
    # Thu thập TẤT CẢ ứng viên trước, KHÔNG chốt ngay -- số lượng cuối cùng
    # bị giới hạn bởi typography_policy.max_count của bible (Director Bible
    # coi typography là "điểm nhấn hiếm", không phải cứ khớp luật là dùng).
    candidates: list[tuple[Beat, float]] = []
    remaining_sentences: list[dict] = []
    for sent in sentences:
        # Câu khớp symbol_library (vd nhắc "Bát Quái") không được xét làm
        # typography -- luôn phải là IMAGE mang đúng ký hiệu (asset tĩnh
        # chính xác hoặc ảnh AI đã kiểm chứng), xử lý ở Pass 2 bên dưới.
        if creative_profiles.resolve_symbol(profile, sent["text"]) is not None:
            remaining_sentences.append(sent)
            continue
        probe = Beat(sent["start"], sent["end"], sent["text"])
        # video_eligible=False ở pass 1 -- chỉ đang xét TYPOGRAPHY ở đây,
        # tín hiệu VIDEO không ảnh hưởng gì tới quyết định typography (đã
        # check trước trong hàm), không cần tính trước lúc này.
        treatment, confidence = classify_beat_rule_based(probe, core_insight)
        if treatment == Treatment.TYPOGRAPHY and confidence >= TIEBREAK_CONFIDENCE_THRESHOLD:
            candidates.append((probe, confidence))
        else:
            remaining_sentences.append(sent)

    # Ưu tiên confidence cao hơn (core_insight match=0.95 trước aphorism
    # marker=0.75), giữ thứ tự thời gian gốc làm tiêu chí phụ (ổn định,
    # không random) -- chỉ giữ lại top typography_max_count ứng viên.
    candidates.sort(key=lambda pair: (-pair[1], pair[0].start))
    selected = candidates[:typography_max_count]
    rejected = candidates[typography_max_count:]
    selected_starts = {b.start for b, _ in selected}
    for beat, _confidence in rejected:
        # Ứng viên bị loại (vượt quota typo của tập) -- trả về remaining để
        # pass 2 gộp vào beat IMAGE bình thường, không bị mất khỏi timeline.
        remaining_sentences.append({"start": beat.start, "end": beat.end, "text": beat.text})
    remaining_sentences.sort(key=lambda s: s["start"])

    typography_beats = [b for b, _ in selected]
    motion_idx = [0]
    for beat in typography_beats:
        _finalize_beat(beat, Treatment.TYPOGRAPHY, "rule", visual_motif, motion_idx, bible, motion_cycle, core_insight)

    # Pass 2 -- phần câu còn lại (không phải TYPOGRAPHY) được gộp thành beat
    # theo target_beat_sec của bible, phân loại IMAGE/VIDEO (rule-based +
    # Gemini tie-break cho ca không tự tin).
    grouped_beats = group_segments_into_beats(remaining_sentences, target_sec=target_beat_sec)

    # 1 lệnh gọi agy DUY NHẤT cho TOÀN BỘ grouped_beats, xét THEO NGHĨA beat
    # nào thật sự khớp các cảnh pexels_acceptance_policy cho phép (xem
    # batch_judge_video_eligibility()) -- phải làm TRƯỚC vòng lặp phân loại
    # bên dưới vì classify_beat_rule_based() giờ chỉ nhận kết quả đã tính
    # sẵn (video_eligible: bool), không tự gọi agy (giữ hàm đó pure/nhanh).
    video_eligible_indices = batch_judge_video_eligibility(grouped_beats, pexels_hints, context_label=context_label)

    n_gemini_calls = 0
    classified: list[tuple[Beat, Treatment, str]] = []
    for idx, beat in enumerate(grouped_beats):
        symbol_entry = creative_profiles.resolve_symbol(profile, beat.text)
        if symbol_entry is not None:
            beat.symbol_key = symbol_entry["key"]
            # Xem chú thích cùng nội dung ở build_shot_list() -- entry
            # safety_critical PHẢI luôn gọi pick_symbol_asset_path() dù
            # thiếu render_mode/asset_path.
            if symbol_entry.get("safety_critical") or (symbol_entry.get("render_mode") == "static_asset" and (symbol_entry.get("asset_paths") or symbol_entry.get("asset_path"))):
                beat.symbol_asset_path = creative_profiles.pick_symbol_asset_path(symbol_entry)
            classified.append((beat, Treatment.IMAGE, "symbol_library"))
            continue

        treatment, confidence = classify_beat_rule_based(beat, core_insight, idx in video_eligible_indices)
        source = "rule"

        # Beat đã gộp nhiều câu -- không còn phù hợp cho TYPOGRAPHY (chữ quá
        # dài để hiện giữa khung hình), dù rule-based có thể vẫn khớp
        # core_insight một phần. Ép về IMAGE thay vì để lọt 1 "typography
        # card" dài cả đoạn văn.
        if treatment == Treatment.TYPOGRAPHY:
            treatment, confidence = Treatment.IMAGE, 1.0

        if confidence < TIEBREAK_CONFIDENCE_THRESHOLD and gemini_api_key:
            tiebreak_result = gemini_tiebreak(beat, visual_motif, gemini_api_key, context_label=context_label, tone_label=tone_label)
            n_gemini_calls += 1
            if tiebreak_result is not None and tiebreak_result != Treatment.TYPOGRAPHY:
                treatment, source = tiebreak_result, "gemini"

        # G3 (Video Generation remediation, round 1 Codex finding #1): nhánh
        # KHÔNG dùng treatment_ratio (treatment_ratio=None -- vd gọi CLI
        # creative_director.py trực tiếp mà không truyền --video-ratio) đi
        # qua vòng lặp NÀY, không phải _build_shot_list_by_ratio() -- trước
        # bản vá này, is_video_unsafe_topic() CHỈ được áp dụng ở nhánh tỷ lệ
        # cố định, nên 1 beat khớp video_unsafe_terms (rule-based có_scene
        # HOẶC Gemini tie-break) vẫn có thể lọt thành Treatment.VIDEO ở
        # nhánh này -- đúng lỗ hổng Codex review round 1 phát hiện. Ép lại
        # về IMAGE ở ĐÂY (sau rule-based lẫn sau Gemini, vì cả 2 đều có thể
        # gán VIDEO) để đảm bảo CÙNG 1 guarantee như nhánh tỷ lệ cố định:
        # never let a video_unsafe_terms beat reach Treatment.VIDEO, bất kể
        # đường nào gán treatment.
        if treatment == Treatment.VIDEO and creative_profiles.is_video_unsafe_topic(profile, beat.text):
            treatment, confidence, source = Treatment.IMAGE, 1.0, "video_unsafe_topic"

        classified.append((beat, treatment, source))

    # Dịch NGẮN GỌN sang tiếng Anh cho TOÀN BỘ beat IMAGE trong 1 lệnh gọi
    # Gemini DUY NHẤT (không phải 1 lệnh/beat) -- xem
    # batch_translate_visual_hints(). Phải biết treatment TRƯỚC (vòng lặp
    # trên) mới biết beat nào là IMAGE để đưa vào lô dịch. Beat symbol_library
    # không cần agy dịch -- static_asset không dùng prompt, ai_generate_ok đã
    # có image_prompt_hint soạn sẵn trong profile.
    image_beats = [beat for beat, treatment, _ in classified if treatment == Treatment.IMAGE and beat.symbol_key is None]
    visual_hints = batch_translate_visual_hints(image_beats, bible, context_label=context_label)
    hint_by_start = {image_beats[i].start: hint for i, hint in visual_hints.items() if i < len(image_beats)}
    n_hints_ok = len(hint_by_start)
    for beat, treatment, _source in classified:
        if beat.symbol_key and treatment == Treatment.IMAGE:
            entry = creative_profiles.resolve_symbol(profile, beat.text)
            if entry and entry.get("image_prompt_hint"):
                hint_by_start[beat.start] = entry["image_prompt_hint"]

    # Beat DIAGRAM (ảnh nền + mũi tên/nhãn chỉ hướng qua Remotion) -- chỉ
    # xét cho domain hỗ trợ (vd Phong Thuỷ), cùng logic nhánh tỷ lệ cố định
    # (_build_shot_list_by_ratio), xem docstring ở đó.
    diagram_starts: set[float] = set()
    if profile.get("supports_diagram_treatment"):
        diagram_matches = batch_detect_diagram_beats(image_beats, context_label, profile.get("diagram_base_image_style", ""))
        for local_idx, value in diagram_matches.items():
            if local_idx >= len(image_beats):
                continue
            beat = image_beats[local_idx]
            beat.diagram_annotations = value.get("annotations")
            diagram_starts.add(beat.start)
            if value.get("base_image_prompt"):
                hint_by_start[beat.start] = value["base_image_prompt"]
    if diagram_starts:
        classified = [
            (beat, Treatment.DIAGRAM if beat.start in diagram_starts else treatment, source)
            for beat, treatment, source in classified
        ]

    video_beats = [beat for beat, treatment, _ in classified if treatment == Treatment.VIDEO]
    video_keywords = batch_translate_video_keywords(video_beats)
    keyword_by_start = {video_beats[i].start: kw for i, kw in video_keywords.items() if i < len(video_beats)}

    for beat, treatment, source in classified:
        _finalize_beat(
            beat, treatment, source, visual_motif, motion_idx, bible, motion_cycle,
            english_hint=hint_by_start.get(beat.start, ""),
            video_keyword=keyword_by_start.get(beat.start, ""), style_anchor=style_anchor,
        )

    all_beats = sorted(typography_beats + grouped_beats, key=lambda b: b.start)
    select_premium_beats(all_beats, core_insight)
    n_premium = sum(1 for b in all_beats if b.premium)

    print(
        f"Đạo diễn: {len(all_beats)} beat "
        f"({len(typography_beats)} typography [tối đa {typography_max_count} theo bible, "
        f"{len(rejected)} ứng viên bị loại vì vượt quota], "
        f"{sum(1 for b in all_beats if b.treatment == 'image')} image ({n_premium} premium cho Codex/agy), "
        f"{sum(1 for b in all_beats if b.treatment == 'video')} video), "
        f"target_beat_sec={target_beat_sec:.0f}s, {n_gemini_calls} lần gọi Gemini tie-break, "
        f"{n_hints_ok}/{len(image_beats)} beat IMAGE dịch prompt tiếng Anh thành công.",
        flush=True,
    )

    out = {
        "visual_motif": visual_motif, "core_insight": core_insight,
        "director_bible": bible, "beats": [asdict(b) for b in all_beats],
    }
    Path(output_path).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return all_beats


def main() -> int:
    import argparse
    import os

    ap = argparse.ArgumentParser()
    ap.add_argument("--segments-json", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--episode-planner", default=None, help="Đường dẫn 02_EPISODE_PLANNER.md nếu có (tập nguồn Content-Creator)")
    ap.add_argument("--script-master", default=None, help="Đường dẫn 03_AUDIO_SCRIPT_MASTER.md -- cần để build Director Bible")
    ap.add_argument("--research-brief", default=None, help="Đường dẫn 01_RESEARCH_BRIEF.md -- cần để build Director Bible")
    ap.add_argument("--episode-id", default=None, help="Vd EP007 -- suy ra tự động từ đường dẫn nếu bỏ trống")
    ap.add_argument("--no-gemini", action="store_true", help="Chỉ dùng rule-based, không gọi Gemini tie-break/Director Bible")
    ap.add_argument("--force-refresh-bible", action="store_true", help="Tổng hợp lại Director Bible dù đã có cache")
    ap.add_argument("--target-beat-sec", type=float, default=None, help="Ghi đè nhịp dựng của bible (giây/beat), vd 5.0 cho cắt nhanh")
    ap.add_argument("--video-ratio", type=float, default=None, help="Tỷ lệ VIDEO cố định (0-1) -- truyền cùng --image-ratio/--typography-ratio để bật nhánh phân bổ theo tỷ lệ")
    ap.add_argument("--image-ratio", type=float, default=None, help="Tỷ lệ IMAGE cố định (0-1)")
    ap.add_argument("--typography-ratio", type=float, default=None, help="Tỷ lệ TYPOGRAPHY cố định (0-1)")
    ap.add_argument("--domain", default=None, help="domain_id (BUD/FS/CL...) -- tra domain_creative_profiles.json, mặc định BUD nếu bỏ trống")
    args = ap.parse_args()

    api_key = None if args.no_gemini else os.environ.get("GEMINI_API_KEY")
    # P1 (E2E validation remediation): resolve_domain_id() applies the SAME
    # fallback logic load_profile() itself uses, so the domain namespacing
    # the Director Bible cache is keyed on always matches which profile was
    # actually loaded -- see director_bible.py's cache collision fix.
    resolved_domain_id = creative_profiles.resolve_domain_id(args.domain)
    profile = creative_profiles.load_profile(args.domain)

    episode_id = args.episode_id or director_bible._derive_episode_id(args.episode_planner, args.segments_json)
    bible = director_bible.build_director_bible(
        episode_id,
        script_master_path=args.script_master,
        episode_planner_path=args.episode_planner,
        research_brief_path=args.research_brief,
        gemini_api_key=api_key,
        force_refresh=args.force_refresh_bible,
        creative_profile=profile,
        domain_id=resolved_domain_id,
    )

    treatment_ratio = None
    if args.video_ratio is not None or args.image_ratio is not None or args.typography_ratio is not None:
        treatment_ratio = {
            "video": args.video_ratio or 0.0,
            "image": args.image_ratio or 0.0,
            "typography": args.typography_ratio or 0.0,
        }
        total = sum(treatment_ratio.values())
        if abs(total - 1.0) > 0.01:
            print(f"LỖI: --video-ratio + --image-ratio + --typography-ratio phải cộng lại = 1.0 (hiện tại: {total}).", file=sys.stderr)
            return 1

    build_shot_list(
        args.segments_json, args.output, args.episode_planner, api_key, bible=bible,
        target_beat_sec_override=args.target_beat_sec, treatment_ratio=treatment_ratio,
        creative_profile=profile,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
