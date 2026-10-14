import re
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional

import numpy as np

# ─── Regex ───────────────────────────────────────────────────────────────────

RE_NEWLINE          = re.compile(r'[\r\n]+')  # dùng chung cho cả v1 và v2
RE_SENTENCE_FINDALL = re.compile(r'[^.!?]+[.!?]*|[.!?]+')

# Một "từ" để đóng gói chunk: coi NGUYÊN một thẻ <en>...</en> là một token không
# thể tách (thẻ chứa khoảng trắng như "<en>u s d</en>" sẽ vỡ nếu .split() theo
# space). Dùng khi chia text ĐÃ normalize (có chèn <en>) thành chunk.
RE_TOKEN_KEEP_EN = re.compile(r'<en>.*?</en>|\S+', re.IGNORECASE | re.DOTALL)


def _tokenize_keep_en(s: str) -> List[str]:
    """Tách ``s`` thành token, giữ NGUYÊN mỗi cụm ``<en>...</en>``."""
    return RE_TOKEN_KEEP_EN.findall(s)


# BUG THẬT phát hiện khi audit kênh Hình Sự (2026-08-14): text đã normalize
# (chèn sẵn <en>...</en> quanh từ mượn tiếng Anh, vd "DNA" -> "<en>d n a</en>")
# được lưu NGUYÊN VĂN vào timings/manifest/.srt để làm phụ đề -- nhưng cặp thẻ
# <en>/</en> chỉ được "tiêu thụ" đúng bên trong bước G2P/phonemize (xảy ra
# RIÊNG, nội bộ trong self.v.infer(), kết quả không quay lại timings) nên
# không bao giờ được strip khỏi bản text dùng cho phụ đề -- phụ đề burn-in
# thật sự hiện literal "<en>d n a</en>" (xác nhận qua chính file .srt đã
# render của short "Vì sao cảnh sát phá án chỉ trong 10 ngày..."). CHỈ dùng để
# làm sạch bản HIỂN THỊ (phụ đề/manifest) -- KHÔNG áp cho chunk text truyền
# vào self.v.infer()/chunk_cache_fingerprint(), vì đó vẫn cần thẻ <en> nguyên
# vẹn để G2P đọc đúng phát âm tiếng Anh.
RE_STRIP_EN_TAG = re.compile(r'<en>(.*?)</en>', re.IGNORECASE | re.DOTALL)


def strip_en_tag_for_display(text: str) -> str:
    """Bỏ markup ``<en>``/``</en>`` khỏi ``text``, giữ lại nội dung bên trong
    (vd ``"<en>d n a</en>"`` -> ``"d n a"``) -- dùng khi ghi phụ đề/manifest,
    KHÔNG dùng cho text sẽ đưa vào TTS (xem ghi chú ở trên)."""
    return RE_STRIP_EN_TAG.sub(lambda m: m.group(1), text)

# v1 only
RE_SENTENCE_END = re.compile(r'(?<=[\.\!\?\…])\s+')
RE_MINOR_PUNCT  = re.compile(r'(?<=[\,\;\:\-\–\—])\s+')

# v2 noise cleanup
_NOISE_RULES: List[Tuple[re.Pattern, str]] = [
    (re.compile(r'([.!?])[.,;:]+'), r'\1'),
    (re.compile(r'[.,;:]+([.!?])'), r'\1'),
    (re.compile(r'\s+[,;]\s+'),     ' '),
    (re.compile(r' {2,}'),          ' '),
]
_MULTI_PUNCT = re.compile(r'([.!?])\s*[.!?]+')

# ─── Data class ──────────────────────────────────────────────────────────────

@dataclass
class PhoneChunk:
    text: str
    is_sentence_end: bool  # True = kết thúc câu thật | False = cắt nhân tạo

# ─── Audio utils ─────────────────────────────────────────────────────────────

# Im lặng (giây) chèn giữa hai chunk tuỳ RANH GIỚI đã cắt: ngắt đoạn (\n) nghỉ
# dài nhất, hết câu (.!?) nghỉ vừa, ngắt trong câu (,;: hoặc cắt cưỡng bức) gần
# như liền mạch. Dùng cho đường v3 khi có metadata gap từ splitter.
#
# GIÁ TRỊ MẶC ĐỊNH TOÀN CỤC -- KHÔNG ĐỔI bởi Phase 2 (giữ nguyên đúng giá trị
# đã có TRƯỚC patch "ranh giới câu/đoạn"). Quan trọng: "sentence": 0.18 ở đây
# là hành vi HIỆN TẠI, ĐANG SỐNG của kênh Hình Sự (CL) và bất kỳ nội dung nào
# có ranh giới "sentence" đến từ NGẮT TRONG ĐOẠN (dấu câu, `_classify_gap`) --
# cơ chế này KHÔNG liên quan gì tới bug newline-misclassification đã sửa (CL
# chưa từng có gap "para" nào, xem before_after_diff_report.txt), nên KHÔNG
# được đổi. FS/BUD ("mỗi câu 1 dòng") cần override RIÊNG để giữ trải nghiệm
# nghe hiện tại của họ (xem `FS_BUD_SENTENCE_SAFE_DEFAULT` ngay dưới) --
# override đó PHẢI được caller truyền TƯỜNG MINH qua `gaps_to_silence(...,
# silence_map=...)`/`render_engine.render_text(..., silence_map=...)`, KHÔNG
# được suy luận tên kênh bên trong module utility này (xem
# `short_batch_runner.py._silence_map_for_topic` -- nơi DUY NHẤT quyết định
# kênh nào dùng override nào).
V3_GAP_SILENCE = {"para": 0.35, "sentence": 0.18, "minor": 0.04}

# Override CÓ CHỦ ĐÍCH cho FS/BUD (Phase 2 PASS WITH CAVEAT, xem
# PHASE2_FINAL_PATCH_SUMMARY.md): trước patch "ranh giới câu/đoạn", MỌI ranh
# giới xuống dòng của script "mỗi câu 1 dòng" (quy ước FS/BUD) bị misclassify
# thành "para" -> nghe 0.35s giữa MỌI câu, xuyên suốt toàn bộ nội dung đã
# publish. Patch sửa ĐÚNG phân loại ("sentence" riêng biệt với "para"), nhưng
# giá trị pause TỐI ƯU cho "sentence" của FS/BUD vẫn CHƯA CÓ BẰNG CHỨNG: pilot
# P1 (n=1 script/n=1 người nghe) cho thấy 0.18s bị đánh giá KÉM HƠN 0.35s trên
# 4/5 tiêu chí -- tín hiệu không đủ mạnh để đổi trải nghiệm nghe hiện tại của
# audience, nhưng đủ để KHÔNG ép về 0.18s. Đặt "sentence" == "para" == 0.35s ở
# đây để giữ NGUYÊN đúng âm thanh audience đã quen, cho tới khi P1 mở rộng
# (xem scratchpad p1_expanded/DECISION_RULE_LOCKED.md, đã chuẩn bị SẴN,
# CHƯA chạy vì user yêu cầu không mở rộng nghe thêm ở vòng này) cho kết quả rõ
# ràng hơn. CHỈ dùng cho FS/BUD -- KHÔNG áp dụng cho CL hay kênh khác.
FS_BUD_SENTENCE_SAFE_DEFAULT = {"para": 0.35, "sentence": 0.35, "minor": 0.04}

# Tách 1 khối "\r\n" liên tiếp thành 1 token riêng (thay vì chỉ dùng làm điểm
# cắt như RE_NEWLINE) để giữ lại được CHÍNH khối đó, phục vụ phân loại
# _classify_newline_run bên dưới -- đây là phần cốt lõi của patch bug "ranh
# giới câu bị hiểu nhầm thành ranh giới đoạn" (xem CHANGELOG/audit Phase 2).
RE_NEWLINE_CAPTURE = re.compile(r'([\r\n]+)')


def _classify_newline_run(sep: str) -> str:
    """Phân loại 1 khối ký tự xuống dòng liên tiếp đã capture bởi
    ``RE_NEWLINE_CAPTURE``: ĐÚNG 1 dấu xuống dòng (``"\\n"`` hoặc ``"\\r\\n"``)
    -- ranh giới CÂU thật (``"sentence"``, nghỉ vừa, CÙNG MỨC với hết câu bằng
    dấu . ! ?); >=2 dấu xuống dòng liên tiếp (vd ``"\\n\\n"``) -- ranh giới
    ĐOẠN VĂN thật (``"para"``, nghỉ dài nhất).

    BẮT BUỘC cùng logic với ``render_engine.normalize_preserving_paragraphs``
    (2 hàm này là 1 hợp đồng chung: normalize phải BẢO TOÀN đúng số lượng
    "\\n" gốc khi ghép lại, hàm này mới phân loại đúng được) -- đổi 1 bên phải
    đổi bên kia, nếu không sẽ tái phát đúng bug đã audit (mọi ranh giới câu bị
    gộp nhầm thành ranh giới đoạn văn, ảnh hưởng chủ yếu 2 kênh FS/BUD dùng
    quy ước script "mỗi câu 1 dòng"). Lưu ý: PHÂN LOẠI đúng "para" vs
    "sentence" ở đây KHÔNG đồng nghĩa 2 loại phải nghỉ khác thời lượng nhau --
    giá trị pause thực tế nằm ở ``V3_GAP_SILENCE`` (mặc định toàn cục, giữ
    nguyên hành vi CL) hoặc ``FS_BUD_SENTENCE_SAFE_DEFAULT`` (override tường
    minh riêng cho FS/BUD, xem 2 hằng số đó để biết giá trị + lý do).
    """
    newline_count = sep.replace("\r\n", "\n").replace("\r", "\n").count("\n")
    return "para" if newline_count >= 2 else "sentence"


def _collapse_blank_lines(text: str) -> str:
    """1 dòng CHỈ chứa khoảng trắng/tab (không ký tự nào khác) nằm giữa 2 lần
    xuống dòng được coi là dòng trống THẬT -- bỏ khoảng trắng đó để 2 khối
    xuống dòng 2 bên gộp đúng thành 1 khối liên tục (``RE_NEWLINE_CAPTURE``
    dùng ``+`` nên tự gộp các dấu xuống dòng LIỀN NHAU, nhưng khoảng trắng xen
    giữa sẽ phá tính liền nhau đó nếu không xử lý trước). Không đổi bất kỳ nội
    dung chữ nào khác."""
    return re.sub(r'(?<=[\r\n])[ \t]+(?=[\r\n])', '', text)


def gaps_to_silence(gaps: List[str], silence_map: Optional[dict] = None) -> List[float]:
    """Map list loại-ranh-giới -> list độ dài im lặng (giây) cho ``join_audio_chunks``.

    ``silence_map`` (tuỳ chọn) cho phép GHI ĐÈ độ dài silence cho từng loại
    gap mà KHÔNG đụng vào logic PHÂN LOẠI boundary (para/sentence/minor, xem
    ``_classify_newline_run``/``_classify_gap`` -- không đổi bởi tham số này).
    Tách biệt rõ 2 khái niệm: "loại ranh giới này LÀ GÌ" (đã patch Phase 2,
    KHÔNG phụ thuộc calibration) vs "loại ranh giới đó NÊN NGHỈ BAO LÂU" (câu
    hỏi calibration -- P1 mở rộng, THAY ĐỔI ĐƯỢC qua tham số này). Mặc định
    (không truyền) dùng đúng ``V3_GAP_SILENCE`` hiện tại của production,
    KHÔNG đổi hành vi các call site cũ."""
    m = silence_map if silence_map is not None else V3_GAP_SILENCE
    default = m.get("sentence", V3_GAP_SILENCE["sentence"])
    return [m.get(g, default) for g in gaps]


def join_audio_chunks(
    chunks: List[np.ndarray],
    sr: int,
    silence_p: float = 0.0,
    crossfade_p: float = 0.0,
    silence_ps: Optional[List[float]] = None,
) -> np.ndarray:
    """Ghép các chunk audio. ``silence_ps`` (tuỳ chọn) cho im lặng RIÊNG từng khe
    nối — ``silence_ps[i]`` là im lặng (giây) giữa chunk ``i`` và ``i+1`` — dùng để
    nghỉ dài/ngắn khác nhau theo loại ranh giới. Khi truyền ``silence_ps`` thì
    ``silence_p``/``crossfade_p`` bị bỏ qua.
    """
    if not chunks:
        return np.array([], dtype=np.float32)
    if len(chunks) == 1:
        return chunks[0]

    silence_samples   = int(sr * silence_p)
    crossfade_samples = int(sr * crossfade_p)
    final_wav = chunks[0]

    for i in range(1, len(chunks)):
        next_chunk = chunks[i]
        if silence_ps is not None:
            gap_samples = int(sr * silence_ps[i - 1]) if i - 1 < len(silence_ps) else 0
            if gap_samples > 0:
                silence   = np.zeros(gap_samples, dtype=np.float32)
                final_wav = np.concatenate([final_wav, silence, next_chunk])
            else:
                final_wav = np.concatenate([final_wav, next_chunk])
        elif silence_samples > 0:
            silence   = np.zeros(silence_samples, dtype=np.float32)
            final_wav = np.concatenate([final_wav, silence, next_chunk])
        elif crossfade_samples > 0:
            overlap = min(len(final_wav), len(next_chunk), crossfade_samples)
            if overlap > 0:
                fade_out  = np.linspace(1.0, 0.0, overlap, dtype=np.float32)
                fade_in   = np.linspace(0.0, 1.0, overlap, dtype=np.float32)
                blended   = final_wav[-overlap:] * fade_out + next_chunk[:overlap] * fade_in
                final_wav = np.concatenate([final_wav[:-overlap], blended, next_chunk[overlap:]])
            else:
                final_wav = np.concatenate([final_wav, next_chunk])
        else:
            final_wav = np.concatenate([final_wav, next_chunk])

    return final_wav

# ─── v1: split raw text ──────────────────────────────────────────────────────

def split_text_into_chunks(text: str, max_chars: int = 256) -> List[str]:
    """Split raw text (chưa phonemize) thành chunks <= max_chars."""
    if not text:
        return []

    paragraphs   = RE_NEWLINE.split(text.strip())
    final_chunks: List[str] = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        sentences = RE_SENTENCE_END.split(para)
        buffer    = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(sentence) > max_chars:
                if buffer:
                    final_chunks.append(buffer)
                    buffer = ""

                sub_parts = RE_MINOR_PUNCT.split(sentence)
                for part in sub_parts:
                    part = part.strip()
                    if not part:
                        continue
                    if len(buffer) + 1 + len(part) <= max_chars:
                        buffer = (buffer + ' ' + part) if buffer else part
                    else:
                        if buffer:
                            final_chunks.append(buffer)
                        buffer = part
                        if len(buffer) > max_chars:
                            words, current = _tokenize_keep_en(buffer), ""
                            for word in words:
                                if current and len(current) + 1 + len(word) > max_chars:
                                    final_chunks.append(current)
                                    current = word
                                else:
                                    current = (current + ' ' + word) if current else word
                            buffer = current
            else:
                if buffer and len(buffer) + 1 + len(sentence) > max_chars:
                    final_chunks.append(buffer)
                    buffer = sentence
                else:
                    buffer = (buffer + ' ' + sentence) if buffer else sentence

        if buffer:
            final_chunks.append(buffer)

    return [c.strip() for c in final_chunks if c.strip()]


def _classify_gap(chunk: str) -> str:
    """Phân loại ranh giới NGAY SAU ``chunk`` dựa trên dấu câu cuối: hết câu
    (``.!?``) -> ``"sentence"``; còn lại (``,;:`` hoặc cắt cưỡng bức giữa câu)
    -> ``"minor"``. Ranh giới ``"para"`` (ngắt đoạn) do caller gán riêng."""
    c = chunk.rstrip()
    return "sentence" if c and c[-1] in ".!?" else "minor"


def split_text_into_chunks_with_gaps(
    text: str, max_chars: int = 256
) -> Tuple[List[str], List[str]]:
    """Như :func:`split_text_into_chunks` nhưng trả kèm loại ranh giới GIỮA các
    chunk để ghép audio nghỉ dài/ngắn khác nhau.

    Trả về ``(chunks, gaps)`` với ``gaps[i] in {"para","sentence","minor"}`` là
    ranh giới giữa ``chunks[i]`` và ``chunks[i+1]`` (``len(gaps) == len(chunks)-1``):
      * ``"para"``     — hai chunk cách nhau bởi >=2 dấu xuống dòng LIÊN TIẾP
                         (đoạn văn thật, vd ``"\\n\\n"``)              -> nghỉ dài
      * ``"sentence"`` — hết câu (chunk trái tận cùng ``.!?``), HOẶC cách nhau
                         bởi ĐÚNG 1 dấu xuống dòng (script quy ước mỗi câu 1
                         dòng, vd FS/BUD)                              -> nghỉ vừa
      * ``"minor"``    — ngắt trong câu (``,;:`` / cắt cưỡng bức)       -> gần như liền

    Phân biệt 1 vs >=2 dấu xuống dòng liên tiếp qua :func:`_classify_newline_run`
    -- SỬA lỗi cũ (trước đây MỌI ranh giới ``[\\r\\n]+`` đều bị gán cứng
    ``"para"`` bất kể 1 hay nhiều dấu xuống dòng, khiến script "mỗi câu 1
    dòng" luôn nhận nhầm nghỉ dài nhất cho MỌI câu). Yêu cầu ``text`` đầu vào
    đã bảo toàn đúng số lượng ``"\\n"`` gốc (xem
    ``render_engine.normalize_preserving_paragraphs``) -- nếu upstream đã gộp
    về 1 ``"\\n"`` duy nhất thì hàm này không còn cách nào phục hồi lại được
    phân biệt câu/đoạn.
    """
    if not text:
        return [], []

    stripped = _collapse_blank_lines(text).strip()
    if not stripped:
        return [], []

    raw_parts = RE_NEWLINE_CAPTURE.split(stripped)
    paragraphs = raw_parts[0::2]
    separators = raw_parts[1::2]
    chunks: List[str] = []
    gaps: List[str] = []
    for i, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue
        para_chunks = split_text_into_chunks(para, max_chars=max_chars)
        if not para_chunks:
            continue
        if chunks:                       # ranh giới với đoạn TRƯỚC đó -- phân loại theo
                                          # đúng số lượng dấu xuống dòng đã capture
            boundary_type = (
                _classify_newline_run(separators[i - 1]) if 0 <= i - 1 < len(separators) else "para"
            )
            gaps.append(boundary_type)
        for j, ch in enumerate(para_chunks):
            if j > 0:                    # ranh giới trong CÙNG đoạn: theo dấu câu
                gaps.append(_classify_gap(para_chunks[j - 1]))
            chunks.append(ch)

    return chunks, gaps

# ─── v2 helpers ──────────────────────────────────────────────────────────────

def _pick_strongest(m: re.Match) -> str:
    s = m.group(0)
    return '!' if '!' in s else '?' if '?' in s else '.'


def _clean_phoneme_noise(text: str) -> str:
    for pattern, repl in _NOISE_RULES:
        text = pattern.sub(repl, text)
    return _MULTI_PUNCT.sub(_pick_strongest, text).strip()


def _find_best_split(text: str, max_size: int) -> Tuple[int, bool]:
    mid = max_size // 2
    best_comma_pos, best_comma_dist = -1, max_size
    best_space_pos, best_space_dist = -1, max_size

    for i in range(min(max_size, len(text))):
        ch = text[i]
        if ch == ',':
            d = abs(i - mid)
            if d < best_comma_dist:
                best_comma_dist, best_comma_pos = d, i
        elif ch == ' ':
            d = abs(i - mid)
            if d < best_space_dist:
                best_space_dist, best_space_pos = d, i

    if best_comma_pos != -1:
        return best_comma_pos, True
    if best_space_pos != -1:
        return best_space_pos, False
    return -1, False


def _smart_split_body(text: str, max_chunk_size: int) -> List[str]:
    result: List[str] = []
    stack = [text.strip()]

    while stack:
        seg = stack.pop()
        if not seg:
            continue
        if len(seg) <= max_chunk_size:
            result.append(seg)
            continue

        pos, _ = _find_best_split(seg, max_chunk_size)
        if pos != -1:
            left  = seg[:pos].rstrip()
            right = seg[pos + 1:].lstrip()
        else:
            cut = max_chunk_size
            while cut > 0 and seg[cut - 1] != ' ':
                cut -= 1
            if cut == 0:
                cut = max_chunk_size
            left  = seg[:cut].rstrip()
            right = seg[cut:].lstrip()

        if right:
            stack.append(right)
        if left:
            stack.append(left)

    return result


def _split_sentence(sent: str, max_chunk_size: int) -> List[PhoneChunk]:
    sent = sent.strip()
    if not sent:
        return []

    if sent[-1] in '.!?':
        body, punct = sent[:-1].rstrip(), sent[-1]
    else:
        body, punct = sent, '.'

    if not body:
        return []

    if len(sent) <= max_chunk_size:
        return [PhoneChunk(text=body + punct, is_sentence_end=True)]

    sub_chunks = _smart_split_body(body, max_chunk_size)
    if not sub_chunks:
        return [PhoneChunk(text=punct, is_sentence_end=True)]

    last_idx = len(sub_chunks) - 1
    return [
        PhoneChunk(
            text=chunk + (punct if i == last_idx else '.'),
            is_sentence_end=(i == last_idx),
        )
        for i, chunk in enumerate(sub_chunks)
        if chunk
    ]

# ─── v2: split phoneme string ────────────────────────────────────────────────

def split_into_chunks_v2(
    full_phones: str,
    max_chunk_size: int = 256,
    min_chunk_size: int = 10,
) -> List[PhoneChunk]:
    """
    Phân đoạn chuỗi phoneme thành các PhoneChunk.
      is_sentence_end=True  → kết thúc câu thật → cần silence
      is_sentence_end=False → cắt nhân tạo → không cần silence
    """
    if not full_phones:
        return []

    full_phones = _clean_phoneme_noise(full_phones)

    raw_parts: List[PhoneChunk] = []
    for para in RE_NEWLINE.split(full_phones):
        para = para.strip()
        if not para:
            continue
        for sent in RE_SENTENCE_FINDALL.findall(para):
            sent = sent.strip()
            if sent:
                raw_parts.extend(_split_sentence(sent, max_chunk_size))

    if not raw_parts:
        return []

    merged: List[PhoneChunk] = []
    i, n = 0, len(raw_parts)
    while i < n:
        cur = raw_parts[i]
        while len(cur.text) < min_chunk_size and i + 1 < n:
            nxt       = raw_parts[i + 1]
            candidate = cur.text.rstrip('.!?').rstrip() + ' ' + nxt.text
            if len(candidate) <= max_chunk_size:
                cur = PhoneChunk(text=candidate, is_sentence_end=nxt.is_sentence_end)
                i += 1
            else:
                break
        merged.append(cur)
        i += 1

    if len(merged) >= 2 and len(merged[-1].text) < min_chunk_size:
        last      = merged.pop()
        candidate = merged[-1].text.rstrip('.!?').rstrip() + ' ' + last.text
        if len(candidate) <= max_chunk_size:
            merged[-1] = PhoneChunk(text=candidate, is_sentence_end=last.is_sentence_end)
        else:
            merged.append(last)

    return merged


def get_silence_duration_v2(chunk: PhoneChunk) -> float:
    """
    Silence sau chunk (giây).
      is_sentence_end=False → 0.0s
      kết thúc '!'/'?' → 0.4s
      kết thúc '.' → 0.3s
    """
    if not chunk.is_sentence_end:
        return 0.0
    return 0.4 if chunk.text.strip()[-1] in '!?' else 0.3

# ─── Misc ────────────────────────────────────────────────────────────────────

def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ('1', 'true', 'yes', 'y', 'on')