"""Helper nội bộ -- chạy trong .venv (repo root, có vieneu) qua subprocess
từ short_batch_runner.py (chạy python3 hệ thống). Nhận text qua file (né
lỗi escape ký tự tiếng Việt qua shell arg), render audio + segments-json.

Usage: .venv/bin/python _short_tts_render.py --text-file X --voice Y --output-wav Z

HỖ TRỢ ĐÁNH DẤU TỪ QUAN TRỌNG: text đầu vào có thể chứa **từ** (agy đánh
dấu lúc soạn kịch bản, xem lich_hoang_dao_generator.py/short_content_review.py).
TTS không được đọc dấu ** thành lời -- bóc marker TRƯỚC khi đưa vào
render_text(), nhưng lưu lại VỊ TRÍ TỪ (chỉ số từ toàn cục trong text đã
bóc marker) ra 1 file JSON đi kèm để render_short.py (venv khác, chạy sau)
đọc lại và gắn is_important đúng chỗ cho karaoke_writer.py."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_engine import RenderSession  # noqa: E402
from vieneu_utils.phonemize_text import _EMOTION_SPLIT_RE, _emotion_tag_token  # noqa: E402

_IMPORTANT_MARKER_RE = re.compile(r"\*\*(.+?)\*\*")


def strip_unsupported_emotion_markers(text: str) -> str:
    """Bóc SẠCH marker cảm xúc nhận diện được (``[cười]``/``[thở dài]``/
    ``[hắng giọng]`` + biến thể Anh ngữ, hoặc ``<|emotion_k|>``) khỏi text
    TRƯỚC khi vào TTS.

    Luồng Short dùng ``RenderSession(mode="standard")`` -- KHÔNG có engine
    emotion-aware (`phonemize_text_with_emotions`), nên các marker này KHÔNG
    bao giờ được model đọc thành token cảm xúc thật. Nếu để nguyên,
    ``normalize_preserving_paragraphs`` chỉ bóc dấu ngoặc/token nhưng GIỮ chữ
    bên trong ("cười"/"thở dài"...) như văn bản thường -- model SẼ ĐỌC THÀNH
    LỜI, sai với ý định của marker. Loại bỏ HẲN (không chỉ bóc ngoặc) để
    marker thật sự không được đọc thành lời.

    CHỈ bóc marker NHẬN DIỆN ĐƯỢC qua :func:`vieneu_utils.phonemize_text.
    _emotion_tag_token` (dùng chung logic nhận diện với engine emotion-aware,
    tránh drift 2 nơi) -- KHÔNG đụng ngoặc vuông khác, vì không phải mọi
    ``"[...]"`` trong script đều là emotion marker.

    Thay marker bằng 1 KHOẢNG TRẮNG (không phải chuỗi rỗng) -- SỬA theo Codex
    review vòng 2: nếu marker nằm sát chữ 2 bên không có khoảng trắng đệm
    (vd ``"A[cười]B"``), xoá bằng chuỗi rỗng sẽ nối liền 2 từ thành 1
    (``"AB"``), làm sai nội dung. Khoảng trắng thừa được dọn ở bước sau.
    """
    def _replace(m: re.Match) -> str:
        matched = m.group(0)
        return " " if _emotion_tag_token(matched) is not None else matched

    result = _EMOTION_SPLIT_RE.sub(_replace, text)
    # Dọn khoảng trắng/dấu câu thừa để lại sau khi bỏ marker (vd
    # "A  B" -> "A B", " , " còn sót -> ", "). SỬA theo Codex review vòng 3:
    # bản trước chỉ dọn dấu phẩy, để sót "Vui ." / "Thật sao ?" / "Được !"
    # (khoảng trắng thừa trước . ; : ! ?) -- nay dọn đủ các dấu câu thường gặp.
    result = re.sub(r"[ \t]+([,.;:!?…])", r"\1", result)
    result = re.sub(r"[ \t]{2,}", " ", result)
    return result.strip()


def strip_importance_markers(text: str) -> tuple[str, list[int]]:
    """Trả về (text đã bóc **, [chỉ số từ quan trọng trong text đã bóc]).
    Chỉ số tính theo word.split() đơn giản -- PHẢI khớp đúng cách
    render_short.py tách từ (segments_to_word_timestamps cũng dùng
    text.split() thuần, xem đó để không lệch)."""
    important_indices = []
    word_cursor = 0

    def _replace(m: re.Match) -> str:
        nonlocal word_cursor
        phrase = m.group(1)
        n_words = len(phrase.split())
        important_indices.extend(range(word_cursor, word_cursor + n_words))
        word_cursor += n_words
        return phrase

    # Phải xử lý theo thứ tự xuất hiện để word_cursor cộng dồn đúng --
    # thay thế lần lượt từng match, đồng thời đếm số từ THƯỜNG (không đánh
    # dấu) xen giữa các match để word_cursor luôn đúng vị trí toàn cục.
    result_parts = []
    last_end = 0
    for m in _IMPORTANT_MARKER_RE.finditer(text):
        between = text[last_end:m.start()]
        word_cursor += len(between.split())
        result_parts.append(between)
        result_parts.append(_replace(m))
        last_end = m.end()
    result_parts.append(text[last_end:])
    clean_text = "".join(result_parts)
    return clean_text, important_indices


_REQUIRED_SILENCE_MAP_KEYS = {"para", "sentence", "minor"}
# Giới hạn trên "hợp lý vận hành" cho 1 khoảng nghỉ -- KHÔNG phải giới hạn kỹ
# thuật (số hữu hạn bất kỳ đều parse được), chỉ để bắt lỗi nhập liệu rõ ràng
# (vd gõ nhầm giây thành mili-giây) trước khi nó lọt vào production render.
_MAX_REASONABLE_SILENCE_SECONDS = 5.0


def _reject_duplicate_keys(pairs: list) -> dict:
    """``object_pairs_hook`` cho ``json.loads`` -- SỬA theo Codex review vòng
    7 (caveat): mặc định ``json.loads`` ÂM THẦM giữ giá trị key trùng CUỐI
    CÙNG (vd ``{"sentence": 0.18, "sentence": 0.35}`` -> chỉ còn 0.35, không
    báo lỗi) -- với override production tường minh, đây là lỗi nhập liệu cần
    raise rõ ràng, không âm thầm chọn 1 giá trị."""
    seen = set()
    result = {}
    for key, val in pairs:
        if key in seen:
            raise ValueError(f"--silence-map-json có key trùng lặp: {key!r}")
        seen.add(key)
        result[key] = val
    return result


def _parse_and_validate_silence_map(raw_json: str | None) -> dict | None:
    """Parse + validate NGHIÊM ``--silence-map-json`` (sửa theo Codex review
    vòng 6-7): từ chối JSON không phải object, thiếu/thừa/trùng key, giá trị
    không phải số hữu hạn không âm trong khoảng hợp lý (bool cũng bị từ chối
    -- ``isinstance(x, bool)`` kiểm tra TRƯỚC ``isinstance(x, (int, float))``
    vì ``bool`` là subclass của ``int`` trong Python). Production override
    (FS/BUD) chỉ nên nhận ĐÚNG 3 key đã biết -- key lạ/thiếu key âm thầm rơi
    vào fallback ``"sentence"`` của ``gaps_to_silence()`` là hành vi không
    mong muốn cho override tường minh."""
    if raw_json is None:
        return None
    try:
        parsed = json.loads(raw_json, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as e:
        raise ValueError(f"--silence-map-json không phải JSON hợp lệ: {e}") from e
    if not isinstance(parsed, dict):
        raise ValueError(f"--silence-map-json phải là JSON object, nhận: {type(parsed).__name__}")
    if set(parsed.keys()) != _REQUIRED_SILENCE_MAP_KEYS:
        raise ValueError(
            f"--silence-map-json phải có ĐÚNG 3 key {sorted(_REQUIRED_SILENCE_MAP_KEYS)}, "
            f"nhận: {sorted(parsed.keys())}"
        )
    for key, val in parsed.items():
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise ValueError(f"--silence-map-json['{key}'] phải là số, nhận: {val!r}")
        if not (val == val) or val in (float("inf"), float("-inf")):  # NaN/Infinity check
            raise ValueError(f"--silence-map-json['{key}'] phải là số hữu hạn, nhận: {val!r}")
        if val < 0:
            raise ValueError(f"--silence-map-json['{key}'] không được âm, nhận: {val!r}")
        if val > _MAX_REASONABLE_SILENCE_SECONDS:
            raise ValueError(
                f"--silence-map-json['{key}']={val!r} vượt giới hạn hợp lý "
                f"({_MAX_REASONABLE_SILENCE_SECONDS}s) -- kiểm tra lại đơn vị (giây, không phải ms)."
            )
    return parsed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-file", required=True)
    ap.add_argument("--voice", default="Binh")
    ap.add_argument("--output-wav", required=True)
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument(
        "--silence-map-json", default=None,
        help="JSON tuỳ chọn ghi đè độ dài silence theo loại gap (xem "
             "vieneu_utils.core_utils.gaps_to_silence). Caller "
             "(short_batch_runner.py) truyền tường minh theo kênh -- "
             "helper này KHÔNG tự suy luận kênh từ voice/topic. Phải có ĐÚNG "
             "3 key para/sentence/minor, giá trị số hữu hạn không âm.",
    )
    args = ap.parse_args()

    raw_text = Path(args.text_file).read_text(encoding="utf-8").strip()
    raw_text = strip_unsupported_emotion_markers(raw_text)
    text, important_indices = strip_importance_markers(raw_text)

    silence_map = _parse_and_validate_silence_map(args.silence_map_json)

    session = RenderSession(args.voice)
    result = session.render_text(
        text, Path(args.output_wav),
        cache_dir=Path(args.cache_dir) if args.cache_dir else None,
        manifest_extra={"content_type": "Short"},
        silence_map=silence_map,
    )

    important_path = Path(args.output_wav).with_suffix(".important_words.json")
    important_path.write_text(json.dumps(important_indices), encoding="utf-8")

    print(json.dumps({
        "ok": result.success, "wav": str(result.out_path), "json": str(result.manifest_path),
        "important_words": str(important_path),
    }, ensure_ascii=False))
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
