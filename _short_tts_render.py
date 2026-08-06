"""Helper nội bộ -- chạy trong .venv (repo root, có vieneu) qua subprocess
từ short_batch_runner.py (chạy python3 hệ thống). Nhận text qua file (né
lỗi escape ký tự tiếng Việt qua shell arg), render audio + segments-json.

Usage: .venv/bin/python _short_tts_render.py --text-file X --voice Y --output-wav Z

HỖ TRỢ ĐÁNH DẤU TỪ QUAN TRỌNG: text đầu vào có thể chứa **từ** (agy đánh
dấu lúc soạn kịch bản, xem lich_hoang_dao_generator.py/short_content_review.py).
TTS không được đọc dấu ** thành lời -- bóc marker TRƯỚC khi đưa vào
render_text(), nhưng lưu lại VỊ TRÍ TỪ (chỉ số từ toàn cục trong text đã
bóc marker) ra 1 file JSON đi kèm để render_short.py (venv khác, chạy sau)
đọc lại và gắn is_important đúng chỗ cho karaoke_writer.py.

G3 (Audio Generation remediation, finding D2): ``important_indices`` PHẢI
tính trên ĐÚNG token stream đã normalize (số/ngày tháng/viết tắt được mở
rộng thành nhiều từ, vd "123" -> "một trăm hai mươi ba") -- KHÔNG phải
trên text thô trước normalize như bản cũ (chỉ số từ tính bằng
``text.split()`` trên text CHƯA normalize, trong khi
``render_short.py::known_transcript_from_segments()`` tính lại chỉ số từ
trên segments CỦA MANIFEST đã normalize -- 2 nguồn khác nhau, lệch nhau
ngay khi normalize đổi số lượng từ). ``strip_importance_markers()`` giờ tự
gọi ``render_engine._normalize_paragraphs``/``_rejoin_paragraphs`` (CÙNG 1
lượt normalize canonical sẽ dùng lại nguyên văn cho TTS qua
``render_text(..., already_normalized=True)``) -- xem docstring hàm đó."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_engine import (  # noqa: E402
    RenderSession,
    _normalize_paragraphs,
    _rejoin_paragraphs,
    normalize_preserving_paragraphs,
)
from vieneu_utils.phonemize_text import _EMOTION_SPLIT_RE, _emotion_tag_token  # noqa: E402

_IMPORTANT_MARKER_RE = re.compile(r"\*\*(.+?)\*\*")
# Sentinel "từ" chèn quanh phrase đánh dấu TRƯỚC khi normalize -- survive
# qua normalizer nguyên vẹn như 1 từ riêng biệt để sau normalize vẫn định
# vị lại được ranh giới phrase, bất kể phrase đó tự nó có mở rộng/co lại
# bao nhiêu từ qua normalize hay không. PHẢI thuần chữ cái ASCII, KHÔNG
# được chứa chữ số -- đã xác nhận thực nghiệm: 1 token pha số như
# "zz9k" bị normalizer tách/đọc số riêng ("9" -> "chín"), làm vỡ token
# thành nhiều từ; thuần chữ cái thì sống sót nguyên vẹn. Đủ lạ để không
# bao giờ trùng với text kịch bản thật.
_IMPORTANT_SPAN_START_TOKEN = "importspanstartxyzqq"
_IMPORTANT_SPAN_END_TOKEN = "importspanendxyzqq"


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


def _locate_important_indices(sentinel_text: str) -> tuple[str, list[int]]:
    """Chạy 1 lượt normalize canonical trên ``sentinel_text`` (đã chèn
    sentinel quanh phrase đánh dấu), định vị lại ranh giới phrase theo
    word-level TRÊN TỪNG ĐOẠN (không regex trên toàn chuỗi -- tránh nuốt
    nhầm ranh giới \\n/\\n\\n), rồi loại sentinel + rejoin. Trả về (text
    sạch, important_indices) -- KHÔNG tự validate gì, xem
    ``strip_importance_markers`` để biết vì sao cần validate bên ngoài."""
    normalized_paragraphs, separators = _normalize_paragraphs(sentinel_text)

    important_indices: list[int] = []
    clean_paragraphs: list[str] = []
    global_word_idx = 0
    for para in normalized_paragraphs:
        clean_words: list[str] = []
        inside = False
        # Dấu câu "mồ côi" do punc_norm dính LIỀN vào sentinel (vd
        # "**từ**." -- không có khoảng trắng gốc giữa ** và "." -- sau khi
        # chèn sentinel + khoảng trắng đệm, punc_norm=True lại GỘP khoảng
        # trắng trước dấu câu, dính thành "importspanendxyzqq." nguyên 1
        # "từ" theo .split() -- KHÔNG còn khớp so sánh == token) -- giữ lại
        # để gắn vào từ liền kề, không đánh rơi ký tự.
        pending_prefix = ""
        for w in para.split():
            loc = None
            for tok in (_IMPORTANT_SPAN_START_TOKEN, _IMPORTANT_SPAN_END_TOKEN):
                idx = w.find(tok)
                if idx != -1:
                    loc = (w[:idx], tok, w[idx + len(tok):])
                    break

            if loc is None:
                word = pending_prefix + w
                pending_prefix = ""
                if inside:
                    important_indices.append(global_word_idx)
                clean_words.append(word)
                global_word_idx += 1
                continue

            prefix, tok, suffix = loc
            stray = prefix + suffix
            if stray:
                if clean_words:
                    clean_words[-1] += stray
                else:
                    pending_prefix += stray
            inside = (tok == _IMPORTANT_SPAN_START_TOKEN)

        if pending_prefix:
            if clean_words:
                clean_words[-1] += pending_prefix
            else:
                clean_words.append(pending_prefix)
        clean_paragraphs.append(" ".join(clean_words))

    clean_text = _rejoin_paragraphs(clean_paragraphs, separators)
    return clean_text, important_indices


def strip_importance_markers(text: str) -> tuple[str, list[int]]:
    """Trả về (text đã NORMALIZE + bóc **, [chỉ số từ quan trọng TRONG TEXT
    ĐÃ NORMALIZE đó]).

    G3 (finding D2, CONFIRMED bởi Codex review -- normalize có thể đổi số
    lượng từ, vd "Tôi có 123 con mèo." 5->9 từ, "Hẹn ngày 21/02/2025." 3->15
    từ, "TP.HCM có 2 người." 4->8 từ): bản CŨ tính important_indices bằng
    text.split() trên text CHƯA normalize, trong khi render_short.py tính
    lại global_word_offset trên segments CỦA MANIFEST đã normalize -- 2 chỉ
    số lệch nhau ngay khi 1 câu trước/trong phrase đánh dấu có số/ngày
    tháng/viết tắt bị normalize mở rộng. Highlight karaoke trỏ SAI TỪ.

    Kỹ thuật: chèn 2 "từ" sentinel (KHÔNG BAO GIỜ bị normalizer đụng tới)
    quanh MỖI phrase đánh dấu NGAY TRÊN TEXT THÔ (trước khi bóc ``**``),
    normalize, rồi định vị lại ranh giới phrase theo word-level (xem
    :func:`_locate_important_indices`).

    AN TOÀN NỘI DUNG (ưu tiên số 1, HƠN CẢ highlight đúng): xác nhận thực
    nghiệm -- 1 số rule normalize NHẠY NGỮ CẢNH (vd "ngày" đứng liền TRƯỚC
    ngày-tháng quyết định model có tự chêm thêm "ngày" khi mở rộng hay
    không) cho kết quả KHÁC khi có sentinel chen vào giữa so với normalize
    KHÔNG sentinel: ``"Hẹn ngày **21/02/2025** nhé."`` -> có sentinel ra
    "ngày ngày hai mươi mốt..." (THỪA 1 "ngày" so với bản không đánh dấu).
    Nếu lỡ dùng thẳng text có sentinel làm input TTS, model sẽ ĐỌC THÊM TỪ
    không có trong kịch bản gốc -- lỗi NỘI DUNG, nghiêm trọng hơn hẳn lỗi
    lệch highlight ban đầu (D2) mà gate này đang sửa.

    Vì vậy hàm này LUÔN tính riêng ``canonical_text`` = normalize KHÔNG
    sentinel (bóc ``**`` đơn giản rồi normalize thẳng -- ĐÚNG HỆT hành vi
    sẽ dùng làm input TTS thật) làm nguồn sự thật DUY NHẤT cho nội dung.
    Nếu text có sentinel (sau khi định vị + bóc sentinel) khớp Y HỆT
    ``canonical_text`` -> important_indices tính được là AN TOÀN, dùng
    luôn. KHÔNG khớp (hiếm, do rule ngữ cảnh) -> BỎ QUA important_indices
    (rỗng) nhưng VẪN trả về ``canonical_text`` -- mất highlight ở 1 vài
    trường hợp hiếm còn chấp nhận được hơn đọc thừa/sai từ.

    Chỉ số trả về (khi an toàn) là GLOBAL WORD INDEX phẳng (``.split()``
    trên toàn text đã normalize, xuyên suốt mọi đoạn) -- khớp đúng cách
    ``render_short.py::known_transcript_from_segments()`` cộng dồn
    ``global_word_offset`` qua các segment của manifest (segment text =
    chunk text = 1 phần của CHÍNH text normalize này)."""
    naive_stripped = _IMPORTANT_MARKER_RE.sub(lambda m: m.group(1), text)
    canonical_text = normalize_preserving_paragraphs(naive_stripped)

    if not _IMPORTANT_MARKER_RE.search(text):
        return canonical_text, []

    sentinel_text = _IMPORTANT_MARKER_RE.sub(
        lambda m: f" {_IMPORTANT_SPAN_START_TOKEN} {m.group(1)} {_IMPORTANT_SPAN_END_TOKEN} ",
        text,
    )
    sentinel_clean_text, important_indices = _locate_important_indices(sentinel_text)

    if sentinel_clean_text != canonical_text:
        print(
            "CẢNH BÁO: chèn sentinel để tính important_indices làm thay đổi "
            "kết quả normalize (rule ngữ cảnh) -- bỏ qua highlight từ quan "
            "trọng cho lần render này, vẫn dùng text normalize chuẩn "
            "(không sentinel) để đọc ĐÚNG nội dung gốc.",
            file=sys.stderr,
        )
        return canonical_text, []

    return canonical_text, important_indices


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
    # G3: text trả về ĐÃ NORMALIZE (xem docstring strip_importance_markers)
    # -- truyền already_normalized=True để render_text() KHÔNG normalize
    # lại lần 2, đảm bảo important_indices khớp ĐÚNG token stream thật sự
    # đưa vào TTS/manifest.
    text, important_indices = strip_importance_markers(raw_text)

    silence_map = _parse_and_validate_silence_map(args.silence_map_json)

    session = RenderSession(args.voice)
    result = session.render_text(
        text, Path(args.output_wav),
        cache_dir=Path(args.cache_dir) if args.cache_dir else None,
        manifest_extra={"content_type": "Short"},
        silence_map=silence_map,
        already_normalized=True,
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
