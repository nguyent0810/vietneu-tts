"""HF Director — quyết định câu nào trong một Short nên được biểu diễn bằng hình.

Đọc `script[]` của một mục trong plan, xuất `figures` (semantic, theo
`hf_figure_schema.json`) + `needs_human_figure` (dẫn xuất) ghi ngược vào chính
plan đó. Không render, không biết gì về pixel.

Quyết định theo thứ tự (ADR-0001 → ADR-0004):
  1. Một lượt đọc TOÀN BỘ kịch bản (`scan_script`) — tìm năm, số tiền, dấu
     hiệu chuỗi bước, và các cặp câu đối chiếu. Rule per-câu không nhìn thấy
     cặp đối chiếu; đó là lý do `director_bible.py` ra đời và cũng là lý do
     lượt đọc này đi trước.
  2. Rule per-câu, dựa trên kết quả lượt 1.
  3. Gemini `gemini-3.5-flash` chỉ cho câu rule không tự tin (< 0.6), nhận
     NGUYÊN kịch bản làm ngữ cảnh. Thiếu API key / lỗi mạng -> giữ kết quả
     rule, không làm sập batch.
  4. Ràng buộc CỨNG (không phải heuristic): tối đa 3/5 câu có hình, câu cuối
     luôn trống, không hai câu liền nhau cùng `type` trừ cặp `contrast`.

Bất biến quan trọng (ADR-0002): director CHỈ ĐƯỢC CẮT chữ từ chính câu văn,
không bao giờ được tự soạn chữ mới. `_steps_are_verbatim()` ép điều đó cho cả
rule lẫn Gemini — một bước `flow` không phải trích đoạn nguyên văn sẽ bị loại,
kể cả khi model rất tự tin.

Usage:
    python3 hf_director.py output/.../plan_d27.json            # cả file
    python3 hf_director.py plan_d27.json --id d27_b            # 1 mục
    python3 hf_director.py plan_d27.json --no-llm --dry-run
    python3 hf_director.py plan_d27.json --force               # ghi đè cả quyết định của người
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

import hf_figure_contract as contract

PROJECT_ROOT = Path(__file__).parent
CACHE_DIR = PROJECT_ROOT / "chunks_cache" / "hf_director"
MAX_FIGURES_PER_SHORT = 3
CONFIDENCE_THRESHOLD = contract.CONFIDENCE_THRESHOLD

# ---------------------------------------------------------------------------
# Số tiếng Việt -> số. Kịch bản viết "hai triệu đồng" chứ không viết "2000000".
# ---------------------------------------------------------------------------
_VN_DIGIT = {
    "không": 0, "một": 1, "mốt": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4, "năm": 5, "lăm": 5,
    "sáu": 6, "bảy": 7, "tám": 8, "chín": 9, "mười": 10,
}
_VN_SCALE = {"nghìn": 1_000, "ngàn": 1_000, "triệu": 1_000_000, "tỷ": 1_000_000_000, "tỉ": 1_000_000_000}
_UNIT_WORDS = ("đồng", "năm", "tháng", "ngày", "người", "phần trăm", "tấn", "mét", "cây số")

_MONEY_RE = re.compile(
    r"((?:\d[\d.,]*|" + "|".join(_VN_DIGIT) + r")"
    r"(?:\s+(?:mươi|trăm)\s*(?:" + "|".join(_VN_DIGIT) + r")?)*"
    r"(?:\s*(?:nghìn|ngàn|triệu|tỷ|tỉ))?)\s*(đồng)",
    re.IGNORECASE,
)
_YEAR_RE = re.compile(r"\b(1[0-9]{3}|2[0-9]{3})\b")
# "11 tháng 12 năm 1978", "tháng Một năm 1950", "năm 1906" -- mọi con số nằm
# trong cụm ngày tháng đều KHÔNG phải số liệu. Không chặn thì rule đọc mảnh
# ngày thành stat, và không còn ai duyệt để bắt lại.
_DATE_CTX_RE = re.compile(
    r"(?:ngày\s+\S+\s+)?tháng\s+\S+\s+năm\s+\d{4}|năm\s+\d{4}|\bngày\s+\d{1,2}\b|\btháng\s+\S+\s+năm\b",
    re.IGNORECASE)
_THRESHOLD_MARKER_RE = re.compile(
    r"\b(mốc|khởi điểm|trở lên|từ\s|trị giá từ|ngưỡng|tối thiểu|khởi điểm là)", re.IGNORECASE)
_ABOVE_ONLY_RE = re.compile(r"\b(trên|vượt quá|hơn)\s", re.IGNORECASE)
_STEP_MARKER_RE = re.compile(
    r"(->|→|\brồi\b|\bsau đó\b|\bchuyển sang\b|\bdẫn tới\b|\bdẫn đến\b|\bkéo theo\b|\bthì\b)", re.IGNORECASE)
_CONTRAST_OPEN_RE = re.compile(
    r"^\s*(nếu|ngược lại|còn khi|khác với|nhưng|trong khi đó|tuy nhiên)\b", re.IGNORECASE)
# Chỉ cắt ở dấu phân cách TƯỜNG MINH. "chuyển sang"/"dẫn tới" vẫn là dấu
# hiệu NHẬN BIẾT chuỗi bước (_STEP_MARKER_RE) nhưng KHÔNG phải chỗ cắt:
# cắt ở đó xé "tội danh thường chuyển sang lạm dụng tín nhiệm" thành hai
# mẩu vô nghĩa. Nguyên văn mà vô nghĩa thì vẫn là hình xấu.
_CLAUSE_SPLIT_RE = re.compile(r"\s*(?:->|→|,|;|:|\brồi\b|\bsau đó\b)\s*", re.IGNORECASE)
_MARKER_STRIP_RE = re.compile(r"\*\*(.+?)\*\*")


def _strip_markers(text: str) -> str:
    return _MARKER_STRIP_RE.sub(r"\1", text)


def _fold(text: str) -> str:
    """So khớp không phân biệt hoa/thường và dấu nháy — dùng để kiểm tra một
    bước `flow` có đúng là trích đoạn nguyên văn của câu hay không."""
    text = unicodedata.normalize("NFC", text).lower()
    return re.sub(r"[\s ]+", " ", text).strip(" .,;:!?\"'()")


def _tidy_number(value: float) -> float | int:
    """2000000.0 -> 2000000. Plan là file người đọc và sửa tay; số nguyên
    không nên hiện ra dưới dạng float."""
    return int(value) if float(value).is_integer() else value


def parse_vn_number(raw: str) -> float | None:
    """'hai triệu' -> 2000000.0; '2.000.000' -> 2000000.0; '50 triệu' -> 5e7.
    Trả None khi không chắc — thà bỏ qua còn hơn vẽ sai con số lên màn hình."""
    s = _fold(raw)
    if not s:
        return None
    scale = 1
    for word, mult in _VN_SCALE.items():
        if re.search(rf"\b{word}\b", s):
            scale = mult
            s = re.sub(rf"\b{word}\b", " ", s)
            break
    s = s.strip()
    digits = re.fullmatch(r"[\d.,]+", s)
    if digits:
        cleaned = s.replace(".", "").replace(",", "")
        return float(cleaned) * scale if cleaned.isdigit() else None
    tokens = [t for t in s.split() if t]
    if not tokens:
        return float(scale) if scale > 1 else None
    total, current = 0, 0
    for tok in tokens:
        if tok == "mươi":
            current = (current or 1) * 10
        elif tok == "trăm":
            current = (current or 1) * 100
        elif tok in _VN_DIGIT:
            value = _VN_DIGIT[tok]
            current = current + value if current % 10 == 0 and current else value
        else:
            return None
        total = current
    return float(total * scale) if total else None


# ---------------------------------------------------------------------------
# Lượt đọc toàn kịch bản
# ---------------------------------------------------------------------------
def _marker_near(text: str, pattern: re.Pattern, at: int, window: int = 26) -> bool:
    """Dấu hiệu ngưỡng phải đứng NGAY TRƯỚC con số. 'ba tấn vàng — nhiều hơn
    mọi tính toán ban đầu' có chữ 'hơn', nhưng nó nói về kỳ vọng chứ không
    phải một mốc số; không kiểm khoảng cách thì thành 'TRÊN 3 TẤN'."""
    return any(0 <= at - m.end() <= window for m in pattern.finditer(text))


@dataclass
class SentenceFacts:
    sentence_id: int
    text: str
    years: list[int] = field(default_factory=list)
    money: list[float] = field(default_factory=list)
    has_threshold_marker: bool = False
    has_above_marker: bool = False
    step_markers: int = 0
    opens_with_contrast: bool = False


@dataclass
class ScriptScan:
    sentences: list[SentenceFacts]
    contrast_pairs: list[tuple[int, int]] = field(default_factory=list)

    def by_id(self, sid: int) -> SentenceFacts:
        return self.sentences[sid - 1]


def scan_script(lines: list[str]) -> ScriptScan:
    facts = []
    for i, raw in enumerate(lines, start=1):
        text = _strip_markers(raw).strip()
        money = [v for v in (parse_vn_number(m.group(1)) for m in _MONEY_RE.finditer(text)) if v]
        facts.append(SentenceFacts(
            sentence_id=i,
            text=text,
            years=[int(y) for y in _YEAR_RE.findall(text)],
            money=money,
            has_threshold_marker=bool(_THRESHOLD_MARKER_RE.search(text)),
            has_above_marker=bool(_ABOVE_ONLY_RE.search(text)),
            step_markers=len(_STEP_MARKER_RE.findall(text)),
            opens_with_contrast=bool(_CONTRAST_OPEN_RE.match(text)),
        ))

    pairs = []
    for a, b in zip(facts, facts[1:]):
        both_sequential = a.step_markers >= 1 and b.step_markers >= 1
        if both_sequential and b.opens_with_contrast:
            pairs.append((a.sentence_id, b.sentence_id))
    return ScriptScan(sentences=facts, contrast_pairs=pairs)


# ---------------------------------------------------------------------------
# Quyết định
# ---------------------------------------------------------------------------
@dataclass
class Decision:
    type: str
    confidence: float
    source: str
    reason: str
    data: dict | None = None
    relation: dict | None = None

    def to_figure(self) -> dict:
        fig = {"type": self.type, "source": self.source,
               "confidence": round(float(self.confidence), 2), "reason": self.reason[:300]}
        if self.data is not None and self.type != "none":
            fig["data"] = self.data
        if self.relation is not None:
            fig["relation"] = self.relation
        return fig


def _steps_are_verbatim(steps: list[dict], sentence: str) -> bool:
    """ADR-0002: director chỉ được CẮT chữ từ câu, không được soạn chữ mới."""
    hay = _fold(sentence)
    return all(_fold(s.get("text", "")) and _fold(s["text"]) in hay for s in steps)


def _flow_steps_from(sentence: str) -> list[dict]:
    """Cắt câu thành các bước. Chỉ CẮT, không soạn (ADR-0002) -- nên chất
    lượng phụ thuộc hoàn toàn vào chỗ đặt dấu phẩy của người viết. Mẩu dưới
    3 từ bị loại: 'tội danh thường' là mẩu nguyên văn nhưng vô nghĩa khi
    đứng một mình trong ô sơ đồ."""
    parts = [p.strip(" ,.;:") for p in _CLAUSE_SPLIT_RE.split(sentence) if p and p.strip()]
    parts = [p for p in parts if 3 <= len(p.split()) and len(p) <= 52]
    if len(parts) < 2:
        return []
    chosen = parts[:4]
    steps = [{"text": p} for p in chosen]
    steps[-1]["terminal"] = True
    return steps


# ---------------------------------------------------------------------------
# Dải giá trị "từ A đến B" — phải nhận ra TRƯỚC ngưỡng, nếu không rule sẽ đọc
# "phạt tiền từ mười đến năm mươi triệu đồng" thành ngưỡng 50 triệu (ADR-0005).
# ---------------------------------------------------------------------------
_NUM_WORD = "|".join(sorted(_VN_DIGIT, key=len, reverse=True)) + "|mươi|trăm"
_NUM_PAT = rf"(?:\d[\d.,]*|(?:{_NUM_WORD})(?:\s+(?:{_NUM_WORD}))*)"
_SCALE_PAT = "|".join(_VN_SCALE)
_UNIT_PAT = "|".join(_UNIT_WORDS)
_RANGE_RE = re.compile(
    rf"(?:từ\s+)?({_NUM_PAT})\s*(?:({_SCALE_PAT})\s*)?(?:({_UNIT_PAT})\s*)?"
    rf"(?:đến|tới|-|–)\s*({_NUM_PAT})\s*(?:({_SCALE_PAT})\s*)?(?:({_UNIT_PAT})\b)?",
    re.IGNORECASE,
)


def _quantity(num: str, scale: str | None, unit: str | None) -> tuple[float, str] | None:
    """'năm mươi' + 'triệu' + 'đồng' -> (50000000, 'đồng').

    Xử lý chỗ nhập nhằng riêng của tiếng Việt: 'năm' vừa là số 5 vừa là đơn vị
    năm. 'ba năm' không có slot unit nào bắt được sẽ bị đọc thành số 5 nếu
    không bóc chữ cuối ra làm đơn vị."""
    tokens = num.split()
    if unit is None and len(tokens) > 1 and tokens[-1].lower() in _UNIT_WORDS:
        unit = tokens[-1].lower()
        num = " ".join(tokens[:-1])
    value = parse_vn_number(f"{num} {scale}" if scale else num)
    if value is None:
        return None
    return value, (unit or "").lower()


def range_span(text: str) -> tuple[int, int] | None:
    m = _RANGE_RE.search(text)
    return (m.start(), m.end()) if m else None


def detect_range(text: str) -> dict | None:
    """Trả `data` của figure `range`, hoặc None. Bên trái thiếu đơn vị/bậc thì
    thừa hưởng của bên phải — đúng lối nói tắt 'từ mười đến năm mươi triệu'."""
    m = _RANGE_RE.search(text)
    if not m:
        return None
    lnum, lscale, lunit, rnum, rscale, runit = m.groups()
    right = _quantity(rnum, rscale, runit)
    if right is None or not right[1]:
        return None
    left = _quantity(lnum, lscale or (rscale if not lunit else None), lunit)
    if left is None:
        return None
    lvalue, lu = left
    if not lu:
        lu = right[1]
    if lvalue <= 0 or right[0] <= 0 or (lu == right[1] and lvalue >= right[0]):
        return None
    return {"from": {"value": _tidy_number(lvalue), "unit": lu},
            "to": {"value": _tidy_number(right[0]), "unit": right[1]}}


def rule_decide(facts: SentenceFacts, scan: ScriptScan, series: str = "") -> Decision:
    sid = facts.sentence_id

    # Lane truyện hư cấu KHÔNG bao giờ có đồ hoạ thông tin: một truyện kể lúc
    # nửa đêm mà chèn biểu đồ thì hỏng tông, và "hai người", "bốn năm trước"
    # trong truyện là chi tiết kể chuyện, không phải số liệu.
    if series == "tale":
        return Decision("none", 0.9, "rule", "Lane truyện hư cấu -- không dùng đồ hoạ thông tin")

    if len(facts.years) >= 2:
        points = [{"year": y} for y in sorted(dict.fromkeys(facts.years))][:5]
        return Decision("timeline", 0.85, "rule", f"{len(points)} mốc năm trong cùng một câu",
                        data={"points": points})

    rng, rspan = detect_range(facts.text), range_span(facts.text)

    # Ngưỡng chỉ hợp lệ khi con số của nó nằm NGOÀI đoạn dải. Nếu nằm trong,
    # chính nó là một đầu của dải -- đọc thành ngưỡng là đúng lớp lỗi ADR-0005.
    money_outside = [m for m in _MONEY_RE.finditer(facts.text)
                     if not (rspan and m.start() >= rspan[0] and m.end() <= rspan[1])]
    threshold_first = None
    if money_outside and (facts.has_threshold_marker or facts.has_above_marker):
        value = parse_vn_number(money_outside[0].group(1))
        if value:
            direction = "above" if facts.has_above_marker and not facts.has_threshold_marker else "at_or_above"
            threshold_first = (money_outside[0].start(),
                               Decision("threshold", 0.92, "rule", "Mốc tiền tường minh kèm dấu hiệu ngưỡng",
                                        data={"value": _tidy_number(value), "unit": "đồng", "direction": direction}))

    if rng and threshold_first:
        # Câu có CẢ ngưỡng lẫn dải (vd "mốc khởi điểm là hai triệu đồng, ...
        # tù từ sáu tháng đến ba năm"). Chọn cái xuất hiện trước -- trong lối
        # viết pháp lý tiếng Việt, ý chính đứng đầu câu.
        if threshold_first[0] < rspan[0]:
            return threshold_first[1]
        return Decision("range", 0.9, "rule", "Dải giá trị 'từ A đến B' tường minh", data=rng)
    if rng:
        return Decision("range", 0.9, "rule", "Dải giá trị 'từ A đến B' tường minh", data=rng)
    if threshold_first:
        return threshold_first[1]
    if rspan:
        # Có hình dạng dải nhưng không đọc chắc hai đầu -> KHÔNG được rơi
        # xuống threshold/stat.
        return Decision("none", 0.7, "rule", "Có dạng dải giá trị nhưng không đọc chắc hai đầu")

    if facts.money:
        return Decision("stat", 0.55, "rule", "Có số tiền nhưng không rõ là ngưỡng hay chỉ là con số",
                        data={"value": _tidy_number(facts.money[0]), "unit": "đồng"})

    if facts.step_markers >= 2:
        steps = _flow_steps_from(facts.text)
        if steps and _steps_are_verbatim(steps, facts.text):
            confidence = 0.8 if facts.step_markers >= 3 else 0.66
            return Decision("flow", confidence, "rule",
                            f"{facts.step_markers} dấu hiệu chuỗi bước, các bước cắt nguyên văn",
                            data={"steps": steps})
        return Decision("none", 0.45, "rule", "Có dấu hiệu chuỗi bước nhưng không cắt được bước nguyên văn")

    date_spans = [(m.start(), m.end()) for m in _DATE_CTX_RE.finditer(facts.text)]
    for unit in _UNIT_WORDS:
        if unit == "đồng":
            continue
        for m in re.finditer(rf"\b({_NUM_PAT})\s+{unit}\b", facts.text, re.IGNORECASE):
            if any(m.start() < e and m.end() > b for b, e in date_spans):
                continue                      # nằm trong cụm ngày tháng -> bỏ
            value = parse_vn_number(m.group(1))
            if value is None or value <= 1:
                # value == 1 gần như luôn là mạo từ "một" ("một người", "một
                # vụ"), không phải số liệu. Và một con số bằng 1 thì cũng
                # chẳng có gì để vẽ.
                continue
            # Ngưỡng KHÔNG chỉ có ở tiền: "tỷ lệ tổn thương từ 11% trở lên"
            # là một mốc đúng nghĩa và đáng vẽ thành thanh ngưỡng.
            near_threshold = _marker_near(facts.text, _THRESHOLD_MARKER_RE, m.start())
            near_above = _marker_near(facts.text, _ABOVE_ONLY_RE, m.start())
            trailing = re.search(r"\btrở lên\b", facts.text[m.end():m.end() + 20], re.IGNORECASE)
            if near_threshold or near_above or trailing:
                direction = "above" if near_above and not (near_threshold or trailing) else "at_or_above"
                return Decision("threshold", 0.86, "rule", f"Mốc '{unit}' kèm dấu hiệu ngưỡng",
                                data={"value": _tidy_number(value), "unit": unit, "direction": direction})
            return Decision("stat", 0.62, "rule", f"Số liệu kèm đơn vị '{unit}'",
                            data={"value": _tidy_number(value), "unit": unit})

    signal_free = not facts.years and not facts.money and facts.step_markers == 0
    if signal_free:
        return Decision("none", 0.86, "rule", "Không có số liệu hay quan hệ nào để biểu diễn")
    return Decision("none", 0.4, "rule", "Có tín hiệu mơ hồ, rule không đủ chắc")


def apply_script_timeline(decisions: dict[int, Decision], scan: ScriptScan, series: str,
                          n_sentences: int) -> dict[int, Decision]:
    """Mốc năm hiếm khi nằm gọn trong MỘT câu.

    Kịch bản lịch sử luôn rải năm ra nhiều câu ("Năm 1894…", "Mười hai năm
    sau, năm 1906…"), nên luật per-câu đòi >= 2 năm trong cùng một câu gần
    như không bao giờ kích hoạt -- lane hồ sơ vụ án mất hẳn loại figure hợp
    với nó nhất.

    Ở đây dùng kết quả của lượt đọc toàn kịch bản: gom mọi mốc năm, rồi gắn
    timeline vào câu chứa mốc CUỐI CÙNG -- lúc đó người xem đã nghe đủ hai
    đầu của dòng thời gian, biểu đồ mới có nghĩa. Hợp đồng không đổi: figure
    vẫn thuộc về một câu, chỉ có dữ liệu là gom từ cả bài.

    Không ghi đè figure đã có, TRỪ `stat` đơn vị thời gian: "Mười hai năm
    sau" chỉ là cách nói khác của chính khoảng cách giữa hai mốc năm, nên
    timeline nói được điều đó đầy đủ hơn và thay thế được."""
    if series == "tale":
        return decisions
    years: list[int] = []
    last_sid = None
    for facts in scan.sentences:
        for y in facts.years:
            if y not in years:
                years.append(y)
        # Câu cuối luôn bị ràng buộc gỡ figure, nên gắn timeline vào đó là
        # vứt đi trong im lặng -- chọn câu có mốc năm gần cuối nhất mà KHÔNG
        # phải câu chốt.
        if facts.years and facts.sentence_id != n_sentences:
            last_sid = facts.sentence_id
    if len(years) < 2 or last_sid is None:
        return decisions
    if any(d.type == "timeline" for d in decisions.values()):
        return decisions
    current = decisions.get(last_sid)
    subsumable = (current and current.type == "stat"
                  and (current.data or {}).get("unit") in ("năm", "tháng", "ngày"))
    if current and current.type != "none" and not subsumable:
        return decisions
    points = [{"year": y} for y in sorted(years)][:5]
    decisions[last_sid] = Decision(
        "timeline", 0.8, "rule",
        f"{len(points)} mốc năm gom từ cả kịch bản, gắn vào câu có mốc cuối",
        data={"points": points})
    return decisions


# ---------------------------------------------------------------------------
# Ràng buộc cứng (Q10 vòng 2) — chạy SAU khi đã có quyết định cho từng câu
# ---------------------------------------------------------------------------
def apply_constraints(decisions: dict[int, Decision], scan: ScriptScan, n_sentences: int) -> dict[int, Decision]:
    out = dict(decisions)
    pairs = {tuple(sorted(p)) for p in scan.contrast_pairs}
    paired = {sid for pair in pairs for sid in pair}

    def drop(sid: int, reason: str) -> None:
        out[sid] = Decision("none", 0.75, "rule", reason)

    # 1. Câu cuối luôn trống
    if n_sentences in out and out[n_sentences].type != "none":
        drop(n_sentences, "Ràng buộc: câu chốt luôn để trống cho chữ và giọng đọc")

    # 2. Không hai câu liền nhau cùng type, trừ cặp contrast đã khai báo
    for sid in range(1, n_sentences):
        a, b = out.get(sid), out.get(sid + 1)
        if not a or not b or a.type == "none" or a.type != b.type:
            continue
        if tuple(sorted((sid, sid + 1))) in pairs:
            continue
        loser = sid if a.confidence < b.confidence else sid + 1
        drop(loser, f"Ràng buộc: trùng type '{a.type}' với câu liền kề, giữ câu tự tin hơn")

    # 3. Ngân sách tối đa 3 hình; cặp contrast tính là một khối
    def units() -> list[tuple[float, list[int]]]:
        seen, result = set(), []
        for sid, dec in out.items():
            if dec.type == "none" or sid in seen:
                continue
            pair = next((p for p in pairs if sid in p and out.get(p[0]) and out.get(p[1])
                         and out[p[0]].type != "none" and out[p[1]].type != "none"), None)
            group = list(pair) if pair else [sid]
            seen.update(group)
            result.append((max(out[s].confidence for s in group), group))
        return sorted(result, key=lambda t: -t[0])

    kept, budget = [], MAX_FIGURES_PER_SHORT
    for _conf, group in units():
        if len(group) <= budget:
            kept.extend(group)
            budget -= len(group)
        else:
            for sid in group:
                drop(sid, f"Ràng buộc: vượt ngân sách {MAX_FIGURES_PER_SHORT} hình mỗi Short")

    # 4. Gắn relation cho cặp contrast còn sống
    for a, b in pairs:
        if a in kept and b in kept:
            out[a].relation = {"pairs_with": b, "role": "contrast"}
            out[b].relation = {"pairs_with": a, "role": "contrast"}
        else:
            for sid in (a, b):
                if out.get(sid):
                    out[sid].relation = None
    return out


# ---------------------------------------------------------------------------
# Chạy trên 1 mục của plan
# ---------------------------------------------------------------------------
def _script_hash(lines: list[str]) -> str:
    return hashlib.sha1("\n".join(lines).encode("utf-8")).hexdigest()[:16]


def direct_entry(entry: dict, *, force: bool = False) -> dict:
    """Trả về entry MỚI (không sửa tại chỗ) đã có `figures` + `needs_human_figure`."""
    lines = [l for l in entry.get("script", []) if l and l.strip()]
    if not lines:
        raise ValueError(f"Mục {entry.get('id')} không có script")

    existing = entry.get("figures") or {}
    scan = scan_script(lines)
    decisions: dict[int, Decision] = {}

    for facts in scan.sentences:
        sid = facts.sentence_id
        prev = existing.get(str(sid))
        if prev and prev.get("source") == "human" and not force:
            decisions[sid] = Decision(prev["type"], float(prev.get("confidence", 1.0)), "human",
                                      prev.get("reason", "Quyết định của người"),
                                      data=prev.get("data"), relation=prev.get("relation"))
            continue
        decisions[sid] = rule_decide(facts, scan, entry.get("series", ""))

    decisions = apply_script_timeline(decisions, scan, entry.get("series", ""), len(lines))
    decisions = apply_constraints(decisions, scan, len(lines))

    figures = {str(sid): decisions[sid].to_figure() for sid in sorted(decisions)}
    contract.assert_valid({"figures": figures, "figure_labels": entry.get("figure_labels") or {}})

    new_entry = dict(entry)
    new_entry["figures"] = figures
    new_entry.pop("needs_human_figure", None)   # ADR-0005: trường đã chết, dọn luôn
    return new_entry


def direct_plan(path: Path, *, only_id: str | None = None, force: bool = False,
                dry_run: bool = False) -> list[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    report = []
    for i, entry in enumerate(rows):
        if only_id and entry.get("id") != only_id:
            continue
        if not entry.get("script") or entry["script"] == ["(đã render trước, giữ nguyên file)"]:
            continue
        updated = direct_entry(entry, force=force)
        rows[i] = updated
        report.append({
            "id": updated.get("id"),
            "script_hash": _script_hash(updated["script"]),
            "figures": {sid: fig["type"] for sid, fig in updated["figures"].items()},
        })

    if not dry_run and report:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        tmp.replace(path)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Quyết định figure ngữ nghĩa cho từng câu của Short")
    ap.add_argument("plan", help="File plan_*.json")
    ap.add_argument("--id", default=None, help="Chỉ xử lý 1 mục theo id")
    ap.add_argument("--force", action="store_true", help="Ghi đè cả figure sửa tay (source='human')")
    ap.add_argument("--dry-run", action="store_true", help="In kết quả, không ghi vào plan")
    args = ap.parse_args()

    report = direct_plan(Path(args.plan), only_id=args.id, force=args.force, dry_run=args.dry_run)
    if not report:
        print("Không có mục nào để xử lý.", file=sys.stderr)
        return 1
    for row in report:
        marks = " ".join(f"{sid}:{t}" for sid, t in sorted(row["figures"].items(), key=lambda kv: int(kv[0])))
        print(f"{row['id']:8s} {marks}")
    if args.dry_run:
        print("\n(dry-run: chưa ghi gì vào plan)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
