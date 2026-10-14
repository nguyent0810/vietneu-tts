"""
Director Bible: gọi 1 LẦN/tập, đọc TOÀN BỘ kịch bản + metadata (không phải
từng câu rời rạc), tổng hợp ra 1 "tầm nhìn đạo diễn" có cấu trúc — ràng buộc
MỌI quyết định hình ảnh sau đó (typography/image/video/Pexels/chuyển cảnh)
trong creative_director.py + asset_generation.py + audio_tool_render.py.

Đây là thay đổi kiến trúc có chủ đích: creative_director.py trước đây tự
phân loại từng beat độc lập bằng luật cứng giống nhau cho MỌI tập (số từ,
danh sách từ khoá cố định...). Giờ luật đó chỉ còn là bước LỌC SƠ BỘ (câu
có đủ ngắn/đủ dài để CÓ THỂ là typography không) — quyết định CUỐI CÙNG
(dùng bao nhiêu thẻ typo, tông màu ảnh, khi nào chấp nhận Pexels dù không
khớp...) đến từ chính nội dung/tông của tập đó, do 1 lần đọc tổng thể quyết
định, không phải quy tắc chung áp cho mọi tập.

Gọi Gemini API dạng TEXT (không phải sinh ảnh) — đã xác nhận model text
không bị chặn billing như model ảnh (xem ghi chú trong asset_generation.py
và lịch sử phiên làm việc). Cache theo episode_id trong
chunks_cache/director_bibles/ -- đạo diễn không "đổi ý" giữa các lần chạy
lại pipeline cho cùng 1 tập; dùng --force-refresh nếu thật sự muốn tổng hợp
lại (vd sau khi kịch bản được sửa).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

DIRECTOR_BIBLE_CACHE_DIR = Path(__file__).parent / "chunks_cache" / "director_bibles"
GEMINI_MODEL = "gemini-3.5-flash"

# P1 (E2E validation remediation, real incident): cache key used to be bare
# `{episode_id}.json` -- every channel numbers its own episodes starting at
# EP001, so 2+ channels sharing an episode number collided on the exact same
# cache file, with no domain/channel check on cache HIT at all. Reproduced
# for real: CL's EP001 silently inherited BUD's cached Buddhist-themed
# bible, contaminating every fresh CL image-generation prompt with temple/
# statue/incense text. Fixed by namespacing the cache filename with the
# RESOLVED domain_id (not the raw possibly-None arg -- see
# domain_creative_profiles.resolve_domain_id()) plus a cache-format version
# suffix (_BIBLE_CACHE_VERSION): bumping this constant, whenever the prompt
# template/schema changes in a way that makes old cached bibles no longer a
# safe drop-in, invalidates EVERY existing cache entry at once (new
# filenames -> guaranteed cache miss -> fresh regeneration), rather than
# risking a schema-stale bible being silently reused forever. The old bare
# `{episode_id}.json` files are NEVER read by this new scheme (different
# filename pattern entirely) -- they are moved into
# `_legacy_ambiguous_pre_namespace/` (see migrate_legacy_ambiguous_cache())
# for forensic reference, not deleted, but no code path reads them again.
# v3 (2026-08-14): thêm pacing_guidance/editing_rhythm domain-aware vào
# prompt (audit kênh Hình Sự) -- bible cũ đã cache (nhịp chậm mặc định) KHÔNG
# còn là bản drop-in an toàn, buộc bump để mọi episode (kể cả CL EP001 nếu đã
# từng cache) sinh lại bible mới thay vì âm thầm dùng lại bản nhịp chậm cũ.
_BIBLE_CACHE_VERSION = "v3"
from external_bin import AGY_BIN  # noqa: F401 -- gom về 1 nguồn duy nhất (xem docstring ở đó)
AGY_TIMEOUT_S = 180  # bible dài (đọc cả kịch bản đầy đủ), cho nhiều thời gian hơn các lệnh agy khác

# Dùng khi chưa có GEMINI_API_KEY hoặc lệnh gọi thất bại -- không để cả
# pipeline dừng lại vì thiếu "tầm nhìn đạo diễn"; đây là bản trung tính,
# hợp lý cho nội dung Phật giáo/tâm linh nói chung (không đặc thù theo
# từng tập), tốt hơn không có gì nhưng kém hơn 1 bible thật sự đọc kịch bản.
DEFAULT_BIBLE = {
    "creative_vision": "Trầm lắng, ấm áp, tôn trọng — hình ảnh minh hoạ mang tính ẩn dụ, không mô tả trực tiếp/graphic.",
    "emotion_curve": [{"phase": "toàn tập", "mood": "trầm, suy ngẫm, dần ấm lên về cuối"}],
    "color_palette": {"primary": "warm amber/gold", "secondary": "soft brown", "avoid": "màu sắc rực rỡ, tương phản gắt, neon"},
    "camera_language": {
        "preferred_motions": ["slow_zoom_in", "slow_pan_left", "slow_pan_right", "slow_zoom_out"],
        "avoid_motions": [], "framing_notes": "trung cảnh/toàn cảnh, tránh cận mặt cụ thể",
    },
    "editing_rhythm": {"target_beat_sec": 20, "pacing_notes": "chậm, không cắt dồn dập kiểu MTV"},
    "typography_policy": {
        "max_count": 3,
        "criteria": "câu châm ngôn/nguyên lý ngắn tự thân đầy đủ ý, hoặc câu định vị trùng Core Insight",
        "style_bias": "flip_3d dành riêng cho câu quan trọng nhất (Core Insight), còn lại pop_in/rise_up/word_cascade theo độ dài",
    },
    "image_policy": {
        "style_descriptor": "minh hoạ tranh vẽ ấm áp, ánh sáng dịu, không photorealistic quá mức, không có chữ trong ảnh",
        "favor_subjects": [], "avoid_subjects": ["mặt người cụ thể có thể nhận diện", "hình ảnh bạo lực/máu me/graphic"],
    },
    "ai_video_policy": {"when_acceptable": "chưa áp dụng — chưa có nguồn AI video trong pipeline"},
    "pexels_acceptance_policy": {
        "threshold": "chỉ chấp nhận cảnh chung chung (thiên nhiên, đời sống, kiến trúc trung tính) làm nền phụ; không chấp nhận cho hình ảnh tôn giáo/biểu tượng cụ thể của tập",
    },
    "transition_style": {"type": "fade", "duration_sec": 0.3},
    "consistency_rules": [
        "không lặp lại cùng 1 ẩn dụ hình ảnh quá 2 lần liên tiếp",
        "không dùng cùng hướng Ken Burns 2 lần liên tiếp",
    ],
}


def _read_text_if_exists(path) -> str:
    if not path:
        return ""
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _find_continuity_registry(episode_planner_path: str) -> str | None:
    """Tìm CONTINUITY_REGISTRY.md bằng cách dò ngược lên từ thư mục chứa
    episode planner -- best-effort, không bắt buộc phải tìm thấy (tập
    nguồn không phải Content-Creator sẽ không có file này)."""
    if not episode_planner_path:
        return None
    current = Path(episode_planner_path).resolve().parent
    for _ in range(8):
        candidate = current / "CONTINUITY_REGISTRY.md"
        if candidate.exists():
            return str(candidate)
        found = list(current.glob("**/CONTINUITY_REGISTRY.md"))
        if found:
            return str(found[0])
        if current.parent == current:
            break
        current = current.parent
    return None


def _derive_episode_id(episode_planner_path: str | None, segments_json_path: str) -> str:
    for path in (episode_planner_path, segments_json_path):
        if not path:
            continue
        m = re.search(r"EP[_]?(\d{3,4})", str(path), re.I)
        if m:
            return f"EP{m.group(1)}"
    return Path(segments_json_path).stem


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


_BIBLE_PROMPT_TEMPLATE = """Bạn là đạo diễn hình ảnh (creative director) cho 1 tập {genre_label} tiếng Việt, dựng từ audio narration + hình ảnh minh hoạ AI / video stock / chữ trên nền (typography card).

Đọc TOÀN BỘ kịch bản và metadata tập dưới đây, sau đó tổng hợp ra "Director Bible" -- định hướng MỌI quyết định hình ảnh cho CHÍNH tập này (phải bám sát nội dung/tông thật của tập, không trả lời chung chung áp được cho tập nào cũng đúng).

=== EPISODE PLANNER (Visual Motif, Emotional Arc, Core Insight đã có sẵn) ===
{planner}

=== RESEARCH BRIEF ===
{brief}

=== KỊCH BẢN ĐẦY ĐỦ (narration thật) ===
{script}

=== RÀNG BUỘC LIÊN TỤC TOÀN SERIES (ẩn dụ/tông đã dùng ở các tập trước -- KHÔNG lặp lại) ===
{registry}

=== NHỊP DỰNG (editing_rhythm) -- BẮT BUỘC theo đúng định hướng thể loại này, KHÔNG áp nhịp chiêm nghiệm chậm rãi mặc định của thể loại khác ===
{pacing_guidance}

Trả về CHỈ 1 JSON object hợp lệ (không markdown, không giải thích thêm, không có text nào khác ngoài JSON), đúng schema sau:
{{
  "creative_vision": "1-2 câu tinh thần hình ảnh tổng thể của tập này cụ thể",
  "emotion_curve": [{{"phase": "...", "mood": "..."}}, ...],
  "color_palette": {{"primary": "...", "secondary": "...", "avoid": "..."}},
  "camera_language": {{"preferred_motions": [chọn trong "slow_zoom_in","slow_zoom_out","slow_pan_left","slow_pan_right"], "avoid_motions": [...], "framing_notes": "..."}},
  "editing_rhythm": {{"target_beat_sec": <10-30, PHẢI nằm trong khoảng cụ thể nêu ở mục "NHỊP DỰNG" bên trên -- số ngoài khoảng đó là KHÔNG hợp lệ>, "pacing_notes": "..."}},
  "typography_policy": {{"max_count": <1-6>, "criteria": "...", "style_bias": "..."}},
  "image_policy": {{"style_descriptor": "...", "favor_subjects": [...], "avoid_subjects": [...]}},
  "ai_video_policy": {{"when_acceptable": "..."}},
  "pexels_acceptance_policy": {{"threshold": "..."}},
  "transition_style": {{"type": "fade", "duration_sec": <0.2-0.6>}},
  "consistency_rules": ["...", "..."]
}}"""


def cache_filename(domain_id: str, episode_id: str) -> str:
    """`domain_id` must already be RESOLVED (see
    domain_creative_profiles.resolve_domain_id()) -- this function does not
    apply any fallback itself, so 2 different raw domain_id spellings that
    resolve to the same effective domain (e.g. None and "BUD") must be
    resolved to the identical string BEFORE calling this, or they will
    (correctly, safely) be treated as 2 different cache entries -- safe
    (extra cache miss) vs. the old bug's failure mode (silent collision),
    but callers should still resolve first to get proper cache reuse."""
    return f"{domain_id}_{episode_id}_{_BIBLE_CACHE_VERSION}.json"


def build_director_bible(
    episode_id: str,
    script_master_path: str | None = None,
    episode_planner_path: str | None = None,
    research_brief_path: str | None = None,
    continuity_registry_path: str | None = None,
    gemini_api_key: str | None = None,
    force_refresh: bool = False,
    creative_profile: dict | None = None,
    domain_id: str = "BUD",
) -> dict:
    """`domain_id` (P1 fix): the RESOLVED domain/channel this bible is
    being built for (see domain_creative_profiles.resolve_domain_id()) --
    required to namespace the cache correctly; defaults to "BUD" only for
    backward-compatible direct calls that predate this parameter (e.g. ad
    hoc scripts/tests) -- every real pipeline call site (creative_director.py)
    now passes it explicitly, resolved from --domain."""
    DIRECTOR_BIBLE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = DIRECTOR_BIBLE_CACHE_DIR / cache_filename(domain_id, episode_id)
    if cache_path.exists() and not force_refresh:
        print(f"Director Bible: dùng bản đã cache cho {episode_id} ({cache_path}).", flush=True)
        return json.loads(cache_path.read_text(encoding="utf-8"))

    if not continuity_registry_path:
        continuity_registry_path = _find_continuity_registry(episode_planner_path)

    genre_label = (creative_profile or {}).get("bible_genre_label", "phim tài liệu suy ngẫm Phật giáo")
    # Audit kênh Hình Sự (2026-08-14): thiếu field này khiến LLM tự chọn nhịp
    # dựng "chậm rãi chiêm nghiệm" (giống nội dung Phật giáo) cho CẢ tập điều
    # tra hình sự thật (EP001 đo được target_beat_sec=18) -- không có gì
    # trong prompt trước đây phân biệt nhịp dựng theo thể loại. Default dưới
    # đây CHỈ áp dụng khi creative_profile thiếu field (không nên xảy ra với
    # domain_creative_profiles.json hiện tại, cả 3 domain đều đã có).
    pacing_guidance = (creative_profile or {}).get(
        "pacing_guidance",
        "Nhịp dựng vừa phải -- target_beat_sec ở khoảng giữa khung cho phép (16-22 giây/beat).",
    )
    prompt = _BIBLE_PROMPT_TEMPLATE.format(
        genre_label=genre_label,
        planner=_read_text_if_exists(episode_planner_path)[:15000] or "(không có)",
        brief=_read_text_if_exists(research_brief_path)[:8000] or "(không có)",
        script=_read_text_if_exists(script_master_path)[:20000] or "(không có)",
        registry=_read_text_if_exists(continuity_registry_path)[:6000] or "(không có)",
        pacing_guidance=pacing_guidance,
    )

    required_keys = {
        "creative_vision", "emotion_curve", "color_palette", "camera_language",
        "editing_rhythm", "typography_policy", "image_policy", "ai_video_policy",
        "pexels_acceptance_policy", "transition_style", "consistency_rules",
    }

    bible = None
    if gemini_api_key:
        bible = _call_gemini_api(prompt, required_keys)
    if bible is None:
        # Không có GEMINI_API_KEY hoặc lệnh Gemini API lỗi -- thử agy
        # (Antigravity CLI, đã xác thực sẵn/dùng ổn định cho TEXT xuyên
        # suốt dự án -- quota sinh ẢNH của agy có thể cạn riêng, không ảnh
        # hưởng gì tới quota TEXT, 2 pool tách biệt).
        bible = _call_agy(prompt, required_keys)
    if bible is None:
        print("CẢNH BÁO: cả Gemini API lẫn agy đều không dùng được -- dùng Director Bible mặc định (trung tính, không đặc thù theo tập).", file=sys.stderr)
        bible = dict(DEFAULT_BIBLE)
        # Audit kênh Hình Sự (2026-08-14): DEFAULT_BIBLE nguyên bản được ghi chú
        # rõ "hợp lý cho nội dung Phật giáo/tâm linh nói chung" -- nếu domain
        # THẬT SỰ không phải BUD (vd CL/FS) mà rơi vào nhánh fallback hiếm gặp
        # này, ít nhất KHÔNG áp nhịp dựng "chậm, chiêm nghiệm" sai thể loại cho
        # editing_rhythm (phần còn lại của DEFAULT_BIBLE -- màu sắc/creative_vision
        # -- vẫn giữ nguyên trung tính, ngoài phạm vi audit này).
        # Cursor review (2026-08-14): 16s trung bình cho MỌI domain khác BUD là
        # sai lệch cho CL cụ thể (CL cần 10-15s, 16 nằm NGOÀI khoảng đó, gần
        # với FS hơn) -- tách rõ theo domain thay vì gộp chung "không phải BUD".
        _FALLBACK_TARGET_BEAT_SEC = {"CL": 12, "FS": 18}  # BUD dùng nguyên DEFAULT_BIBLE (20)
        if domain_id in _FALLBACK_TARGET_BEAT_SEC:
            bible["editing_rhythm"] = {
                "target_beat_sec": _FALLBACK_TARGET_BEAT_SEC[domain_id],
                "pacing_notes": "Bản mặc định trung lập (không gọi được LLM) -- KHÔNG áp nhịp chiêm nghiệm chậm rãi của nội dung Phật giáo/tâm linh cho domain khác.",
            }
        elif domain_id != "BUD":
            bible["editing_rhythm"] = {
                "target_beat_sec": 18,
                "pacing_notes": "Bản mặc định trung lập (không gọi được LLM) -- nhịp vừa phải, KHÔNG áp nhịp chiêm nghiệm chậm rãi của nội dung Phật giáo/tâm linh cho domain khác.",
            }

    cache_path.write_text(json.dumps(bible, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Director Bible: {bible['creative_vision']}", flush=True)
    return bible


def _call_gemini_api(prompt: str, required_keys: set) -> dict | None:
    try:
        from google import genai
        import os
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        bible = json.loads(_strip_json_fences(resp.text or ""))
        missing = required_keys - bible.keys()
        if missing:
            raise ValueError(f"Director Bible thiếu field: {missing}")
        return bible
    except Exception as exc:
        print(f"CẢNH BÁO: Director Bible qua Gemini API lỗi ({exc}) -- thử agy.", file=sys.stderr)
        return None


def _call_agy(prompt: str, required_keys: set) -> dict | None:
    if not AGY_BIN.exists():
        print(f"CẢNH BÁO: chưa cài agy tại {AGY_BIN}.", file=sys.stderr)
        return None
    try:
        result = subprocess.run([str(AGY_BIN), "-p", prompt], capture_output=True, text=True, timeout=AGY_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        print(f"CẢNH BÁO: agy timeout sau {AGY_TIMEOUT_S}s khi tổng hợp Director Bible.", file=sys.stderr)
        return None
    if result.returncode != 0:
        print(f"CẢNH BÁO: agy lỗi (exit {result.returncode}) khi tổng hợp Director Bible: {result.stderr[-500:]}", file=sys.stderr)
        return None
    try:
        bible = json.loads(_strip_json_fences(result.stdout))
        missing = required_keys - bible.keys()
        if missing:
            print(f"CẢNH BÁO: Director Bible từ agy thiếu field: {missing}.", file=sys.stderr)
            return None
        return bible
    except json.JSONDecodeError:
        # agy đôi khi thêm giải thích trước/sau JSON dù đã dặn "CHỈ JSON" --
        # thử tìm khối {...} ngoài cùng thay vì bỏ cuộc ngay.
        match = re.search(r"\{.*\}", result.stdout, re.S)
        if not match:
            print(f"CẢNH BÁO: agy không trả JSON hợp lệ cho Director Bible: {result.stdout[-500:]}", file=sys.stderr)
            return None
        try:
            bible = json.loads(match.group(0))
            missing = required_keys - bible.keys()
            if missing:
                return None
            return bible
        except json.JSONDecodeError:
            return None


_LEGACY_AMBIGUOUS_DIR = DIRECTOR_BIBLE_CACHE_DIR / "_legacy_ambiguous_pre_namespace"
# New-scheme files always end "_v<N>.json" (see cache_filename()) -- a bare
# ".json" file counts as legacy/ambiguous ONLY if it does NOT match this
# (distinguishes it from a coincidentally similar-looking new-format name,
# rather than matching on "has underscores" which both schemes share).
_VERSIONED_CACHE_NAME_RE = re.compile(r"^.+_v\d+\.json$")


def migrate_legacy_ambiguous_cache() -> list[Path]:
    """P1 fix, one-time hygiene utility (not called automatically by
    build_director_bible() -- the version-suffixed filename already makes
    every legacy entry unreachable by any code path regardless). Moves
    every OLD bare-`{episode_id}.json`-style file (no domain prefix, no
    version suffix -- i.e. files that predate this fix and cannot be
    attributed to a specific channel without guessing) out of the live
    cache directory into `_legacy_ambiguous_pre_namespace/`, preserved for
    forensic reference, never deleted, never silently reused. Idempotent --
    safe to re-run. Returns the list of files moved this call."""
    if not DIRECTOR_BIBLE_CACHE_DIR.is_dir():
        return []
    moved = []
    for path in DIRECTOR_BIBLE_CACHE_DIR.iterdir():
        if not path.is_file() or path.suffix != ".json":
            continue
        if _VERSIONED_CACHE_NAME_RE.match(path.name):
            continue  # new-scheme file, not legacy
        _LEGACY_AMBIGUOUS_DIR.mkdir(parents=True, exist_ok=True)
        dest = _LEGACY_AMBIGUOUS_DIR / path.name
        path.rename(dest)
        moved.append(dest)
    return moved


def main() -> int:
    import argparse
    import os

    ap = argparse.ArgumentParser()
    ap.add_argument("--episode-id", required=True)
    ap.add_argument("--script-master", default=None)
    ap.add_argument("--episode-planner", default=None)
    ap.add_argument("--research-brief", default=None)
    ap.add_argument("--continuity-registry", default=None)
    ap.add_argument("--output", default=None)
    ap.add_argument("--force-refresh", action="store_true")
    ap.add_argument("--domain", default=None, help="domain_id (BUD/FS/CL...) -- namespace cache đúng kênh, tra domain_creative_profiles.json")
    args = ap.parse_args()

    import domain_creative_profiles as creative_profiles
    resolved_domain_id = creative_profiles.resolve_domain_id(args.domain)

    bible = build_director_bible(
        args.episode_id, args.script_master, args.episode_planner,
        args.research_brief, args.continuity_registry,
        gemini_api_key=os.environ.get("GEMINI_API_KEY"), force_refresh=args.force_refresh,
        domain_id=resolved_domain_id,
    )
    if args.output:
        Path(args.output).write_text(json.dumps(bible, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(bible, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(main())
