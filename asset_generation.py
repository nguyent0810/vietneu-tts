"""
Sinh asset cho từng beat trong shot_list.json (từ creative_director.py):

  TYPOGRAPHY -- không cần asset ngoài, video_tool_bridge.py tự dựng nền màu
                theo visual_motif của tập.
  IMAGE      -- gọi ComfyUI local (SDXL-Turbo, xem comfyui_client.py) để
                sinh 1 ảnh minh hoạ theo prompt.
  VIDEO      -- tái dùng core.stockfootage.providers (Pexels/Pixabay) của
                video-editor, qua venv riêng (xem
                video_tool_clone/scripts/audio_tool_fetch_stock.py).

Vì sao ComfyUI thay vì agy/Gemini API cho IMAGE: cả 2 đường cloud đều dính
giới hạn tài khoản (Gemini API: billing chặn mọi model ảnh; agy/Antigravity
CLI: 20 request/ngày free tier, cạn nhiều lần ngay trong phiên làm việc).
ComfyUI + SDXL-Turbo chạy HOÀN TOÀN LOCAL trên máy (MPS/Apple Silicon),
không quota, không phụ thuộc mạng -- đã test trực tiếp 3 phong cách (thuỷ
mặc, 2D phẳng, vẽ chì tay) đúng tông nội dung Phật giáo, chất lượng đạt
yêu cầu. agy được giải phóng sang vai trò khác (xem content_seo.py).

Yêu cầu chạy: server ComfyUI phải đang chạy sẵn tại localhost:8189 (xem
comfyui_client.py để biết lệnh khởi động) -- module này KHÔNG tự khởi
động server (tải model mất thời gian, nên chạy như 1 service riêng biệt).

Cơ chế fallback khi sinh ảnh lỗi (server chưa chạy, lỗi mạng nội bộ...) --
không bao giờ để 1 beat "trắng" không có gì hiển thị:
  1. Gọi ComfyUI sinh ảnh theo prompt gốc.
  2. Nếu ComfyUI không khả dụng (server chưa chạy) -- bật circuit breaker
     ngay lần đầu phát hiện, các beat IMAGE còn lại trong CÙNG batch bỏ
     qua gọi ComfyUI (không có ý nghĩa gì thử lại 40 lần nữa khi server
     rõ ràng không chạy), rơi thẳng xuống nhánh VIDEO/TYPOGRAPHY.
  3. Nếu ComfyUI ĐANG chạy nhưng 1 lần sinh cụ thể lỗi (timeout, workflow
     lỗi...) -- không bật circuit breaker (có thể chỉ là lỗi tạm thời của
     riêng beat đó), chỉ hạ cấp đúng beat này xuống TYPOGRAPHY.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import agy_image_client
import asset_safety
import codex_image_client
import comfyui_client
import cursor_image_client
import typography_render

# Circuit breaker cấp module -- 1 lần chạy generate_assets_for_shot_list()
# chỉ cần phát hiện server không chạy/hết quota 1 lần, không cần thử lại
# cho từng beat sau (tránh chờ timeout/tốn token vô ích nhiều lần).
_comfyui_unavailable = False
_remotion_unavailable = False
_codex_unavailable = False
_agy_image_unavailable = False
_cursor_image_unavailable = False

# Màu nền mặc định cho typography card khi Director Bible không có
# color_palette rõ ràng -- khớp TYPOGRAPHY_BG_COLOR bên audio_tool_render.py
# (nền màu phẳng dự phòng) để 2 đường (Remotion / fallback ASS) nhất quán.
DEFAULT_TYPOGRAPHY_BG = "#241A10"
DEFAULT_TYPOGRAPHY_ACCENT = "#E6B45A"


def _prompt_seed(prompt: str) -> int:
    """Seed suy ra từ hash(prompt) -- cùng 1 prompt luôn sinh cùng 1 ảnh
    (idempotent khi chạy lại pipeline), không cần lưu seed riêng."""
    return int(hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8], 16)


VIDEO_TOOL_ROOT = Path(__file__).parent / "video_tool_clone"
VIDEO_TOOL_VENV_PYTHON = VIDEO_TOOL_ROOT / ".venv-video" / "bin" / "python"
FETCH_STOCK_SCRIPT = VIDEO_TOOL_ROOT / "scripts" / "audio_tool_fetch_stock.py"
STOCK_TIMEOUT_S = 120

ASSET_CACHE_DIR = Path(__file__).parent / "chunks_cache" / "beat_assets"

_VI_STOPWORDS = {"và", "của", "là", "có", "một", "những", "các", "được", "cho", "này", "đó", "khi", "để", "không", "đã", "sẽ"}


def _fallback_keywords(text: str, max_words: int = 4) -> str:
    """BUG ĐÃ SỬA: nhánh IMAGE-thất-bại-toàn-bộ-thử-VIDEO trước đây gọi
    _extract_keywords() -- hàm đó chỉ định nghĩa trong creative_director.py,
    KHÔNG hề import vào file này, làm sập cả tiến trình (NameError) ngay
    khi 1 beat IMAGE thật sự thất bại cả 3 tầng Codex/agy/ComfyUI (lần đầu
    xảy ra thật khi chạy EP006, 260 beat). Viết bản rút gọn cục bộ ở đây
    thay vì import chéo creative_director.py (kéo theo nhiều phụ thuộc
    không cần thiết chỉ để lấy 1 hàm nhỏ)."""
    words = [w.strip(".,!?;:\"'") for w in text.split()]
    candidates = [w for w in words if len(w) > 3 and w.lower() not in _VI_STOPWORDS]
    candidates.sort(key=len, reverse=True)
    return " ".join(candidates[:max_words]) if candidates else text[:40]


def _prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def get_or_generate_image(
    prompt: str, image_name: str, aspect_ratio: str = "16:9", visual_motif: str = "", premium: bool = False,
) -> Path | None:
    """Cache theo hash(prompt) -- tránh sinh lại ảnh đã có khi chạy lại
    pipeline (giống cache chunk audio của render_engine.py). Seed cũng suy
    từ hash(prompt) nên idempotent: chạy lại cùng shot_list ra đúng ảnh cũ.

    `premium=True` (beat quan trọng/phức tạp nhất, xem
    creative_director.py::select_premium_beats()) -- thử Cursor Agent CLI
    trước (Nano Banana Pro -- đã test thật, chất lượng rõ ràng cao hơn cả
    3 tầng còn lại, xem cursor_image_client.py), rồi Codex CLI, rồi agy
    (built-in generate_image), CUỐI CÙNG mới rơi xuống ComfyUI. Beat thường
    (premium=False) đi thẳng ComfyUI -- nhanh, không quota, đủ tốt cho phần
    lớn nội dung.

    Trả None (không raise) nếu MỌI tầng đều không khả dụng -- caller hạ
    cấp beat xuống VIDEO rồi TYPOGRAPHY (xem generate_assets_for_shot_list)."""
    global _comfyui_unavailable, _codex_unavailable, _agy_image_unavailable, _cursor_image_unavailable

    ASSET_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = ASSET_CACHE_DIR / f"img_{_prompt_hash(prompt)}.jpg"
    if cache_path.exists():
        return cache_path

    if premium:
        if not _cursor_image_unavailable:
            try:
                return cursor_image_client.generate_image(prompt, cache_path)
            except cursor_image_client.CursorQuotaExceededError as exc:
                _cursor_image_unavailable = True
                print(f"CẢNH BÁO: Cursor Agent hết quota/không có quyền sinh ảnh ({exc}) -- tắt Cursor cho các beat premium còn lại, chuyển sang Codex.", file=sys.stderr)
            except cursor_image_client.CursorImageError as exc:
                print(f"CẢNH BÁO: Cursor Agent lỗi cho '{image_name}' ({exc}) -- thử Codex.", file=sys.stderr)

        if not _codex_unavailable:
            try:
                return codex_image_client.generate_image(prompt, cache_path)
            except codex_image_client.CodexQuotaExceededError as exc:
                _codex_unavailable = True
                print(f"CẢNH BÁO: Codex hết token ({exc}) -- tắt Codex cho các beat premium còn lại, chuyển sang agy.", file=sys.stderr)
            except codex_image_client.CodexImageError as exc:
                print(f"CẢNH BÁO: Codex lỗi cho '{image_name}' ({exc}) -- thử agy.", file=sys.stderr)

        if not _agy_image_unavailable:
            try:
                return agy_image_client.generate_image(prompt, cache_path)
            except agy_image_client.AgyQuotaExceededError as exc:
                _agy_image_unavailable = True
                print(f"CẢNH BÁO: agy hết quota sinh ảnh ({exc}) -- tắt agy cho các beat premium còn lại, chuyển sang ComfyUI.", file=sys.stderr)
            except agy_image_client.AgyImageError as exc:
                print(f"CẢNH BÁO: agy lỗi cho '{image_name}' ({exc}) -- thử ComfyUI.", file=sys.stderr)

    if _comfyui_unavailable:
        print(f"Bỏ qua sinh ảnh cho '{image_name}' -- ComfyUI không khả dụng trong lần chạy này, dùng fallback.", file=sys.stderr)
        return None

    width, height = (1024, 576) if aspect_ratio == "16:9" else (1024, 1024)
    try:
        return comfyui_client.generate_image(prompt, cache_path, seed=_prompt_seed(prompt), width=width, height=height)
    except comfyui_client.ComfyUIUnavailableError as exc:
        if not comfyui_client.is_server_running():
            _comfyui_unavailable = True
            print(f"CẢNH BÁO: ComfyUI server không chạy ({exc}) -- bật circuit breaker, các beat IMAGE còn lại sẽ tự động dùng fallback.", file=sys.stderr)
        else:
            print(f"CẢNH BÁO: sinh ảnh lỗi cho '{image_name}' ({exc}) -- beat này hạ cấp xuống fallback.", file=sys.stderr)
        return None


def get_or_fetch_stock_video(query: str) -> Path | None:
    """Gọi video_tool_clone/scripts/audio_tool_fetch_stock.py (venv riêng)
    để tải 1 clip Pexels/Pixabay theo keyword, cache theo hash(query). Trả
    None (không raise) nếu chưa cấu hình API key hoặc lỗi mạng -- caller tự
    fallback (vd đổi beat đó sang IMAGE)."""
    if not VIDEO_TOOL_VENV_PYTHON.exists():
        print(f"CẢNH BÁO: chưa setup venv video-editor tại {VIDEO_TOOL_VENV_PYTHON} -- bỏ qua nhánh VIDEO.", file=sys.stderr)
        return None

    ASSET_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = ASSET_CACHE_DIR / f"vid_{_prompt_hash(query)}.mp4"
    if cache_path.exists():
        # G5 (Video Generation remediation): 1 cache-hit là 1 "resume path"
        # thật sự -- clip này có thể đã được đánh dấu unsafe (con người
        # hoặc scan_for_legacy_unsafe_assets) SAU LẦN tải đầu tiên. Kiểm tra
        # LẠI mỗi lần trả về từ cache, không chỉ lần tải đầu, để 1 asset đã
        # bị gắn cờ không thể lặng lẽ tái xuất hiện qua cache.
        asset_safety.assert_asset_safe_for_assembly(cache_path)
        return cache_path

    args = [
        str(VIDEO_TOOL_VENV_PYTHON), str(FETCH_STOCK_SCRIPT),
        "--query", query, "--output", str(cache_path.resolve()),
    ]
    try:
        result = subprocess.run(args, cwd=VIDEO_TOOL_ROOT, capture_output=True, text=True, timeout=STOCK_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        print(f"CẢNH BÁO: fetch stock video timeout cho query '{query}'.", file=sys.stderr)
        return None

    stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
    last_line = stdout_lines[-1] if stdout_lines else ""
    try:
        payload = json.loads(last_line)
    except json.JSONDecodeError:
        print(f"CẢNH BÁO: fetch stock video không trả JSON hợp lệ: {result.stdout[-300:]}", file=sys.stderr)
        return None

    if not payload.get("ok"):
        print(f"CẢNH BÁO: fetch stock video lỗi: {payload.get('error')}", file=sys.stderr)
        return None

    fetched_path = Path(payload["output_path"])
    # G5 Codex review round 2 finding #4 (tightened): assert BEFORE writing
    # the fresh "safe" record too, not just after -- round 1's fix only
    # checked AFTER write_asset_safety_record(), which unconditionally
    # OVERWRITES whatever sidecar already existed at this exact path. If
    # fetch_stock.py ever returns an ALTERNATE/renamed path (not the normal
    # deterministic cache-miss destination) that happens to already carry an
    # explicit unsafe/review_required/corrupt record (e.g. a human already
    # flagged a clean-named asset sitting at that exact path for an unrelated
    # reason), the post-write-only check would never see that prior record --
    # it would already be clobbered by the fresh "safe" write by the time the
    # assert runs. Checking BEFORE the write preserves whatever record (or
    # legacy filename marker) already existed; checking AFTER (kept,
    # unchanged) still catches the fresh write's OWN filename carrying a
    # legacy marker.
    asset_safety.assert_asset_safe_for_assembly(fetched_path)
    # G5: mọi asset MỚI tải từ Pexels/Pixabay giờ có 1 safety record tường
    # minh ngay từ lần đầu (không chỉ dựa vào tên file) -- không tự động
    # coi là "đã kiểm duyệt nội dung thật" (không có cơ chế đó trong
    # pipeline này), chỉ ghi rõ ràng "đã qua sanitize query, chưa xem nội
    # dung trả về" làm nguồn gốc, để audit log có đầy đủ dấu vết ngay từ
    # đầu thay vì im lặng như trước đây.
    asset_safety.write_asset_safety_record(
        fetched_path, asset_safety.AssetSafetyStatus.SAFE,
        reason=f"fetched via Pexels/Pixabay for query {query!r}",
        source="fetched_stock_video_no_content_review",
    )
    # G5 Codex review round 1 finding #4 (round 3 nit fix: the filename
    # doesn't change between the pre-write and post-write checks, so both
    # equally catch a legacy-marker filename -- that's NOT what
    # distinguishes them). Re-assert AGAIN immediately after writing the
    # fresh "safe" record, before returning -- this second check's real
    # distinct value is validating the record we JUST wrote actually reads
    # back as a passing "safe" record (defense-in-depth against a bug in
    # write_asset_safety_record() itself, or a future change to it), not
    # re-checking anything about the filename that the pre-write assert
    # above didn't already cover.
    asset_safety.assert_asset_safe_for_assembly(fetched_path)
    return fetched_path


# Quote cards only work for short, punchy lines -- the same threshold
# creative_director.py's own rule-based typography detection already uses
# for that exact reason. A failed IMAGE/VIDEO beat can be an entire
# multi-sentence paragraph (up to ~28s of narration); dumping that whole
# text into a big centered quote card overflows off-screen and is
# unreadable (found via direct visual inspection during testing -- a real
# beat's fallback rendered as illegible wall-of-text spilling past both
# screen edges). Long beats fall back to a plain-color background instead
# (reuses the same flat-background clip renderer) and keep NORMAL bottom
# captions -- `typography_card=False` tells audio_tool_render.py not to
# treat this beat's time range as a quote-card/caption-exclusion zone.
TYPOGRAPHY_FALLBACK_MAX_WORDS = 25


def _downgrade_to_typography(beat: dict) -> None:
    """Lưới an toàn cuối cùng: beat không có asset nào dùng được (ảnh lỗi
    cả 2 lần thử, video không có, quota cạn...) -- chuyển hẳn sang nền màu
    phẳng (tái dùng renderer nền màu của TYPOGRAPHY). Câu ngắn (<=25 từ) ->
    hiện như quote card thật sự; câu dài (nguyên đoạn văn nhiều câu) -> chỉ
    đổi nền màu, vẫn giữ phụ đề thường bên dưới (không nhồi cả đoạn văn vào
    1 thẻ chữ lớn giữa khung hình)."""
    word_count = len(beat["text"].split())
    beat["treatment"] = "typography"
    beat["asset_path"] = None
    beat["motion_mode"] = None
    beat["prompt_or_keywords"] = ""
    beat["source"] = beat.get("source", "rule") + "+fallback_typography"
    beat["typography_card"] = word_count <= TYPOGRAPHY_FALLBACK_MAX_WORDS
    if beat["typography_card"]:
        # Beat hạ cấp lúc runtime không đi qua creative_director.py's
        # _finalize_beat() -- tính lại style/font-size tại đây bằng cùng
        # công thức (pop_in/rise_up/word_cascade theo độ dài câu; không
        # bao giờ flip_3d vì đây là fallback, không phải Core Insight thật).
        if word_count <= 8:
            beat["typography_style"] = "pop_in"
        elif word_count <= 15:
            beat["typography_style"] = "rise_up"
        else:
            beat["typography_style"] = "word_cascade"
        beat["typography_font_size_px"] = max(32, min(130, round(1080 * (0.075 if word_count <= 8 else 0.060 if word_count <= 15 else 0.048))))


def get_or_render_typography(
    text: str, style: str, duration_s: float, font_size_px: int,
    accent_color: str = DEFAULT_TYPOGRAPHY_ACCENT, bg_color: str = DEFAULT_TYPOGRAPHY_BG,
) -> Path | None:
    """Render 1 clip typography qua Remotion (animation thật -- spring
    physics, không phải override-tag ASS thủ công), cache theo hash nội
    dung. Trả None (không raise) nếu Remotion chưa cài/lỗi -- caller
    (audio_tool_render.py) tự fallback về nền màu phẳng + ASS cũ khi không
    thấy asset_path, không bao giờ để 1 beat trắng."""
    global _remotion_unavailable

    cache_key = _prompt_hash(f"{text}|{style}|{duration_s:.2f}|{font_size_px}|{accent_color}|{bg_color}")
    ASSET_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = ASSET_CACHE_DIR / f"typo_{cache_key}.mp4"
    if cache_path.exists():
        return cache_path

    if _remotion_unavailable:
        return None

    try:
        return typography_render.render_typography_clip(
            text, style, duration_s, cache_path, accent_color=accent_color, bg_color=bg_color, font_size_px=font_size_px,
        )
    except typography_render.TypographyRenderError as exc:
        if not typography_render.is_available():
            _remotion_unavailable = True
            print(f"CẢNH BÁO: Remotion chưa setup ({exc}) -- các beat typography còn lại dùng fallback ASS/nền màu cũ.", file=sys.stderr)
        else:
            print(f"CẢNH BÁO: Remotion render lỗi cho 1 beat ({exc}) -- beat này dùng fallback ASS/nền màu cũ.", file=sys.stderr)
        return None


def get_or_render_diagram(base_image_path: str, annotations: list[dict], duration_s: float) -> Path | None:
    """Beat DIAGRAM (xem creative_director.py) -- ảnh nền (đã sinh qua
    ComfyUI, cùng đường IMAGE bình thường) + mũi tên/nhãn chỉ hướng đè lên
    qua Remotion (typography_render.render_annotated_diagram_clip). Cache
    theo hash (ảnh + annotations + thời lượng) -- cùng cơ chế circuit
    breaker/fallback như get_or_render_typography() (Remotion lỗi/chưa cài
    -> trả None, caller giữ nguyên asset_path = ảnh tĩnh gốc, KHÔNG bao giờ
    để 1 beat trắng)."""
    global _remotion_unavailable

    cache_key = _prompt_hash(f"{base_image_path}|{json.dumps(annotations, sort_keys=True)}|{duration_s:.2f}")
    ASSET_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = ASSET_CACHE_DIR / f"diagram_{cache_key}.mp4"
    if cache_path.exists():
        return cache_path

    if _remotion_unavailable:
        return None

    try:
        return typography_render.render_annotated_diagram_clip(base_image_path, annotations, duration_s, cache_path)
    except typography_render.TypographyRenderError as exc:
        if not typography_render.is_available():
            _remotion_unavailable = True
            print(f"CẢNH BÁO: Remotion chưa setup ({exc}) -- các beat diagram còn lại dùng ảnh tĩnh + Ken Burns thường.", file=sys.stderr)
        else:
            print(f"CẢNH BÁO: Remotion render diagram lỗi cho 1 beat ({exc}) -- beat này dùng ảnh tĩnh + Ken Burns thường.", file=sys.stderr)
        return None


def generate_assets_for_shot_list(shot_list_path: str) -> dict:
    """Duyệt shot_list.json, sinh/tải asset cho từng beat IMAGE/VIDEO
    (TYPOGRAPHY bỏ qua -- không cần asset ngoài), ghi ngược lại đường dẫn
    asset (`asset_path`) vào từng beat, lưu đè lên chính shot_list_path.

    Fallback cascade khi asset không sinh được (xem docstring đầu file):
    IMAGE thất bại -> thử VIDEO -> VIDEO thất bại -> thử IMAGE (và ngược
    lại tuỳ treatment gốc) -> cả 2 đều thất bại -> hạ xuống TYPOGRAPHY
    (không bao giờ để 1 beat không có gì hiển thị).

    Trả về thống kê {n_image_ok, n_image_fail, n_video_ok, n_video_fail,
    n_downgraded_typography}."""
    data = json.loads(Path(shot_list_path).read_text(encoding="utf-8"))
    visual_motif = data.get("visual_motif", "")
    stats = {
        "n_image_ok": 0, "n_image_fail": 0, "n_video_ok": 0, "n_video_fail": 0,
        "n_typography_ok": 0, "n_typography_fail": 0, "n_downgraded_typography": 0,
        "n_diagram_ok": 0, "n_diagram_fail": 0,
    }

    for i, beat in enumerate(data["beats"]):
        if beat["treatment"] in ("image", "diagram"):
            # symbol_asset_path (xem creative_director.py::resolve_symbol) --
            # beat khớp 1 ký hiệu domain_creative_profiles.json với
            # render_mode="static_asset" (vd Bát Quái) đã có sẵn ảnh CHÍNH
            # XÁC dựng thủ công, KHÔNG gọi ComfyUI/Codex/agy sinh lại (đã
            # test thật: AI vẽ sai sơ đồ cần chính xác hình học).
            if beat.get("symbol_asset_path"):
                beat["asset_path"] = beat["symbol_asset_path"]
                stats["n_image_ok"] += 1
                continue
            asset = get_or_generate_image(
                beat["prompt_or_keywords"], f"beat_{i:03d}", visual_motif=visual_motif,
                premium=bool(beat.get("premium")),
            )
            beat["asset_path"] = str(asset) if asset else None
            stats["n_image_ok" if asset else "n_image_fail"] += 1
            if asset is None:
                # Ảnh AI lỗi (hết quota, bị chặn nội dung...) -- thử VIDEO
                # trước khi hạ xuống typography: 1 clip stock dù không khớp
                # hoàn hảo vẫn "hấp dẫn" hơn nền màu phẳng, theo đúng yêu
                # cầu -- chỉ khi thật sự không còn cách nào (chưa cấu hình
                # API key, hoặc Pexels/Pixabay cũng không tìm được) mới hạ
                # xuống typography.
                video_asset = get_or_fetch_stock_video(_fallback_keywords(beat["text"]))
                stats["n_video_ok" if video_asset else "n_video_fail"] += 1
                if video_asset is not None:
                    beat["treatment"] = "video"
                    beat["asset_path"] = str(video_asset)
                    beat["motion_mode"] = None
                else:
                    _downgrade_to_typography(beat)
                    stats["n_downgraded_typography"] += 1

            # Vẫn còn là DIAGRAM sau cascade fallback trên (nghĩa là ảnh nền
            # sinh OK) -- vẽ mũi tên/nhãn đè lên qua Remotion. asset_path
            # hiện đang là ảnh TĨNH gốc; get_or_render_diagram() ghi đè
            # bằng clip ĐÃ có animation nếu thành công, giữ nguyên ảnh tĩnh
            # (audio_tool_render.py tự Ken Burns như IMAGE thường) nếu lỗi.
            if beat["treatment"] == "diagram" and beat.get("asset_path") and beat.get("diagram_annotations"):
                diagram_clip = get_or_render_diagram(
                    beat["asset_path"], beat["diagram_annotations"], beat["end"] - beat["start"],
                )
                if diagram_clip is not None:
                    beat["asset_path"] = str(diagram_clip)
                    beat["diagram_rendered"] = True
                    stats["n_diagram_ok"] += 1
                else:
                    stats["n_diagram_fail"] += 1

        elif beat["treatment"] == "video":
            asset = get_or_fetch_stock_video(beat["prompt_or_keywords"])
            beat["asset_path"] = str(asset) if asset else None
            stats["n_video_ok" if asset else "n_video_fail"] += 1
            if asset is None:
                # Không có stock phù hợp/chưa cấu hình key -- thử IMAGE
                # trước khi hạ xuống typography (đã xác nhận trước đó: nội
                # dung Phật giáo dễ có ảnh AI phù hợp hơn stock thật).
                beat["treatment"] = "image"
                fallback_asset = get_or_generate_image(beat["text"], f"beat_{i:03d}_fallback", visual_motif=visual_motif)
                beat["asset_path"] = str(fallback_asset) if fallback_asset else None
                if fallback_asset is None:
                    _downgrade_to_typography(beat)
                    stats["n_downgraded_typography"] += 1
                else:
                    beat["motion_mode"] = beat.get("motion_mode") or "slow_zoom_in"
        # TYPOGRAPHY thật sự (typography_card=True, kể cả beat vừa bị hạ
        # cấp xuống) -- render qua Remotion (animation thật). asset_path
        # để None nếu Remotion lỗi/chưa cài -- audio_tool_render.py tự
        # fallback về nền màu phẳng + ASS quote card cũ, không bao giờ để
        # 1 beat trắng.
        if beat["treatment"] == "typography" and beat.get("typography_card"):
            typo_asset = get_or_render_typography(
                beat["text"], beat.get("typography_style") or "pop_in",
                beat["end"] - beat["start"], beat.get("typography_font_size_px") or 72,
            )
            beat["asset_path"] = str(typo_asset) if typo_asset else None
            stats["n_typography_ok" if typo_asset else "n_typography_fail"] += 1

    Path(shot_list_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Sinh asset: {stats['n_image_ok']} ảnh OK / {stats['n_image_fail']} lỗi, "
        f"{stats['n_video_ok']} video OK / {stats['n_video_fail']} lỗi, "
        f"{stats['n_typography_ok']} typography (Remotion) OK / {stats['n_typography_fail']} lỗi (fallback ASS), "
        f"{stats['n_diagram_ok']} diagram (Remotion overlay) OK / {stats['n_diagram_fail']} lỗi (fallback ảnh tĩnh), "
        f"{stats['n_downgraded_typography']} beat hạ cấp xuống typography (fallback an toàn).",
        flush=True,
    )
    return stats


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--shot-list", required=True)
    args = ap.parse_args()
    generate_assets_for_shot_list(args.shot_list)
    return 0


if __name__ == "__main__":
    sys.exit(main())
