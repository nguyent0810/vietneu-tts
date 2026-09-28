"""Các bước strip dùng chung giữa bước render Short (`_short_tts_render.py`) và
kiểm tra Toàn vẹn văn bản (S8, `script_integrity.py`) -- MỘT nguồn duy nhất,
không bản sao: S8 kiểm đúng thứ bước render sẽ đưa vào TTS.

Module nhẹ (chỉ phụ thuộc bộ nhận diện emotion tag của vieneu_utils), không
kéo theo engine render/model."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from vieneu_utils.phonemize_text import _EMOTION_SPLIT_RE, _emotion_tag_token  # noqa: E402

# `**cụm quan trọng**` -- marker karaoke, bóc trước khi đọc.
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


def strip_importance_markers_plain(text: str) -> str:
    """Bóc `**...**` giữ nội dung bên trong -- đúng bước bóc marker của
    `_short_tts_render.strip_importance_markers` TRƯỚC khi normalize."""
    return _IMPORTANT_MARKER_RE.sub(lambda m: m.group(1), text)


def spoken_text(script: str) -> str:
    """Text sẽ thật sự được đọc (trước bước normalize số/chữ của TTS): bỏ
    emotion tag rồi bỏ `**` -- cùng thứ tự với `_short_tts_render.main()`."""
    return strip_importance_markers_plain(strip_unsupported_emotion_markers(script))
