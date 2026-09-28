"""Nhận diện emotion tag (non-verbal cue) -- thuần stdlib.

Tách khỏi `phonemize_text` (module đó import sea_g2p lúc load) để các nơi chỉ
cần NHẬN DIỆN tag -- vd kiểm Toàn vẹn văn bản của Short (`short_spoken_text`,
chạy cả trong python3 hệ thống của runner, không có sea_g2p) -- dùng đúng MỘT
logic nhận diện với engine emotion-aware, không bản sao.
"""
import re
from typing import Optional

# ---------------------------------------------------------------------------
# Inline non-verbal cues (emotion tokens) — v3 Turbo emotion checkpoint
# ---------------------------------------------------------------------------
# The emotion checkpoint was trained with three non-verbal cues embedded directly
# in the PHONEME stream as special tokens. In the *text* they appear as bracketed
# tags; phonemization must leave them as the matching <|emotion_k|> token instead
# of spelling the bracketed words out. The mapping + spacing reproduce the
# training data (cột `phones` của VieNeu-TTS-1000h-in-the-wild-coded) EXACTLY.
#
#   [chuckle]      / [cười]       -> <|emotion_1|>  (cười)
#   [sigh]         / [thở dài]    -> <|emotion_2|>  (thở dài)
#   [clear throat] / [hắng giọng] -> <|emotion_3|>  (hắng giọng)
_EMOTION_TAG_TO_K = {
    "chuckle": 1, "cười": 1, "cuoi": 1,
    "sigh": 2, "thở dài": 2, "tho dai": 2,
    "clear throat": 3, "hắng giọng": 3, "hang giong": 3,
}
# Split on a [bracketed tag] or an already-resolved <|emotion_k|> token.
_EMOTION_SPLIT_RE = re.compile(r"(\[[^\]]+\]|<\|emotion_\d+\|>)")
# Punctuation that stays attached to the preceding emotion token (no space),
# mirroring the training phones, e.g. "... <|emotion_2|>. ...".
_ATTACHING_PUNCT = set(".,!?;:…)]}\"'’”")


def _emotion_tag_token(tag: str) -> Optional[str]:
    """Map a raw ``[tag]`` / ``<|emotion_k|>`` string to its ``<|emotion_k|>`` form.

    Returns ``None`` for an unrecognized bracketed span (caller phonemizes it as
    ordinary text).
    """
    t = tag.strip()
    if t.startswith("<|"):
        return t  # already an explicit emotion token — pass through unchanged
    inner = t[1:-1].strip().lower()  # drop the surrounding [ ]
    k = _EMOTION_TAG_TO_K.get(inner)
    return f"<|emotion_{k}|>" if k is not None else None
