"""CL Story Plan + Bound Script Generation + Narrow Drift Detector --
phần 2 của kiến trúc provenance-preserving (xem docstring cl_story_fact_
pack.py cho bối cảnh đầy đủ). Validate qua vòng blind round 5: 12/12
mutation an toàn bắt buộc bị chặn, 5/5 phép thử copy/stale bị chặn (phần
lớn cơ học), 0/28 grounded false-block trên 5 topic hoàn toàn chưa dùng.

C4_DRIFT_DETECTOR (run_drift_detector, dưới đây) tái dùng NGUYÊN VẸN
_score_c4_adversarial_text (cl_risk_gate_verification.py) -- KHÔNG viết
lại 1 dòng logic/prompt nào của C4. Điểm khác biệt DUY NHẤT so với cách
Phase A cũ dùng C4 (compute_phase_a_result() trong criminal_law_
storytelling_phase_a.py, đối chiếu CẢ script với TOÀN BỘ excerpt): ở đây
candidate.core_facts CHỈ gồm những fact ĐÃ ĐƯỢC Story Plan chọn hợp lệ cho
ĐÚNG segment đang kiểm tra (cộng dồn theo thứ tự plan) -- ground truth hẹp
hơn, đúng phạm vi văn xuôi thật sự được phép nói, đúng nguyên nhân vì sao
round 5 đạt 0/28 false-block so với C4 chặn nhầm 4/5 EPISODE ở kiến trúc
cũ trên cùng 5 canary."""
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import cl_claim_ledger as L  # noqa: E402
import cl_risk_gate as g  # noqa: E402
from cl_risk_gate_verification import _score_c4_adversarial_text  # noqa: E402
from content_seo import _run_codex, _run_agy, _extract_json  # noqa: E402
from cl_story_fact_pack import StoryFactPack, StoryFact  # noqa: E402

_NUMBER_RE = re.compile(r"\d+")


@dataclass
class PlanSegment:
    segment_id: str
    role: str  # HOOK | BEAT | REVEAL | PAYOFF | ...
    fact_ids: list


@dataclass
class StoryPlan:
    topic_id: str
    fact_pack_hash: str
    segments: list  # list[PlanSegment]

    def plan_hash(self) -> str:
        payload = json.dumps([asdict(s) for s in self.segments], ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:12]


_PLAN_PROMPT = """Bạn là biên tập viên lên KHUNG kể chuyện (KHÔNG viết văn xuôi ở bước này). Dưới đây là danh sách mệnh đề thực chất (facts) ĐƯỢC PHÉP dùng cho 1 câu chuyện Short kênh Hình Sự (storytelling world-crime, phong cách true-crime/bí ẩn lịch sử).

=== DANH SÁCH FACT (DỮ LIỆU) ===
{facts_block}
=== HẾT DANH SÁCH ===

Lên 1 khung kể chuyện gồm 4-6 đoạn (segment), MỖI đoạn chỉ CHỌN (không bịa thêm) 1-3 fact_id từ danh sách trên để làm nội dung. Vai trò đoạn (role) gợi ý: HOOK (mở đầu gây tò mò), BEAT (diễn biến), REVEAL (điểm ngoặt/bất thường), PAYOFF (câu hỏi/kết mở). Được TỰ DO sắp xếp lại thứ tự fact so với danh sách gốc để tạo kịch tính, nhưng KHÔNG được tạo fact_id không có trong danh sách, KHÔNG bắt buộc dùng hết mọi fact (được phép bỏ fact không cần thiết cho câu chuyện Short ngắn).

QUAN TRỌNG -- chọn fact cho PAYOFF (đoạn cuối): PAYOFF phải bổ sung thông tin/diễn giải lại/hệ quả/ý nghĩa còn bỏ ngỏ MỚI so với HOOK -- không được chỉ lặp lại đúng nội dung đã tiết lộ ở HOOK dưới hình thức khác. Nếu 1 fact "giật gân"/gây bất ngờ nhất được dùng làm HOOK, PAYOFF phải dùng fact KHÁC (hệ quả, diễn biến sau đó, hoặc câu hỏi còn bỏ ngỏ) để kết thúc, không quay lại nói y hệt điều đã nói ở đầu.

Trả về CHỈ 1 JSON object:
{{"segments": [{{"segment_id": "S1", "role": "HOOK", "fact_ids": ["F003"]}}, ...]}}"""


def build_story_plan(pack: StoryFactPack) -> StoryPlan:
    facts_block = "\n".join(f"- [{f.fact_id}] ({f.risk_class}): {f.proposition}" for f in pack.facts)
    prompt = _PLAN_PROMPT.format(facts_block=facts_block)
    result = _extract_json(_run_codex(prompt))
    if not isinstance(result, dict) or not isinstance(result.get("segments"), list):
        raise ValueError("Story plan: response không hợp lệ.")
    valid_ids = {f.fact_id for f in pack.facts}
    segments = []
    for i, raw in enumerate(result["segments"], start=1):
        if not isinstance(raw, dict):
            continue
        fact_ids = raw.get("fact_ids")
        if not isinstance(fact_ids, list) or not fact_ids:
            continue
        # Fail-closed: loại NGAY fact_id không có thật trong pack (không tự sửa/đoán).
        if not all(fid in valid_ids for fid in fact_ids):
            raise ValueError(f"Story plan tham chiếu fact_id không có trong pack: {fact_ids}")
        segments.append(PlanSegment(
            segment_id=raw.get("segment_id", f"S{i}"), role=raw.get("role", "BEAT"), fact_ids=fact_ids,
        ))
    if not segments:
        raise ValueError("Story plan rỗng -- fail-closed.")
    return StoryPlan(topic_id=pack.topic_id, fact_pack_hash=pack.pack_hash(), segments=segments)


_SEGMENT_PROSE_PROMPT = """Viết 1 CÂU (hoặc 2 câu ngắn liền mạch) văn xuôi tự nhiên cho lời bình Short (audio-first, TTS đọc) dựa DUY NHẤT trên các mệnh đề đã CHỌN dưới đây cho đoạn "{role}" này. ĐƯỢC diễn giải lại/nén/đổi thứ tự/nối các mệnh đề bằng ngôn ngữ kể chuyện tự nhiên (kể cả câu hỏi tu từ nếu vai trò là HOOK/PAYOFF). TUYỆT ĐỐI KHÔNG thêm bất kỳ sự kiện/số liệu/danh tính/động cơ/nhân quả nào KHÔNG có trong các mệnh đề dưới đây.

=== MỆNH ĐỀ ĐƯỢC CHỌN CHO ĐOẠN NÀY ===
{facts_block}
=== HẾT MỆNH ĐỀ ===

Trả về CHỈ 1 JSON object: {{"prose": "câu văn xuôi"}}"""


def generate_bound_script(plan: StoryPlan, pack: StoryFactPack) -> tuple:
    """Sinh văn xuôi TỪNG SEGMENT riêng (KHÔNG để LLM tự báo cáo binding sau
    khi viết cả kịch bản -- binding ở đây LÀ CẤU TRÚC, xác định TRƯỚC từ
    plan, không phải tự khai). Trả (script_text, bindings).

    Kiểm tra plan.fact_pack_hash == pack.pack_hash() TRƯỚC KHI dùng --
    fact_id là namespace CHUNG (F001, F002, ...) KHÔNG gắn topic_id, nên 1
    StoryPlan bị copy từ topic khác (hoặc từ 1 lần build_story_plan cũ
    trước khi pack được rebuild) sẽ ÂM THẦM bind nhầm sang fact SAI của
    pack hiện tại thay vì lỗi rõ ràng -- fail-closed ngay tại đây."""
    if plan.fact_pack_hash != pack.pack_hash():
        raise ValueError(
            f"Story plan fact_pack_hash={plan.fact_pack_hash} không khớp pack hiện tại "
            f"hash={pack.pack_hash()} (topic_id={pack.topic_id}) -- plan có thể bị copy từ topic/pack "
            f"khác hoặc pack đã bị rebuild sau khi plan được tạo. Fail-closed, không sinh script."
        )
    facts_by_id = {f.fact_id: f for f in pack.facts}
    bindings = []
    prose_parts = []
    for seg in plan.segments:
        facts_block = "\n".join(f"- {facts_by_id[fid].proposition}" for fid in seg.fact_ids)
        prompt = _SEGMENT_PROSE_PROMPT.format(role=seg.role, facts_block=facts_block)
        result = _extract_json(_run_agy(prompt))
        if not isinstance(result, dict) or not isinstance(result.get("prose"), str) or not result["prose"].strip():
            raise ValueError(f"Segment {seg.segment_id}: sinh văn xuôi thất bại/rỗng.")
        prose = result["prose"].strip()
        prose_parts.append(prose)
        # pack_hash_at_generation neo binding vào ĐÚNG pack đã dùng để sinh --
        # phát hiện qua chính mutation test round 4 (copied_fact_binding_
        # across_topics): fact_id là namespace CHUNG nên 1 binding bị copy
        # từ topic khác có thể lọt qua check tồn tại đơn thuần nếu 2 pack
        # tình cờ không lệch nội dung khác biệt đủ rõ -- neo hash tại đây
        # khiến giả mạo bị phát hiện CƠ HỌC, không phụ thuộc may rủi nội
        # dung 2 pack có trùng hay không (xác nhận qua blind round 5).
        bindings.append({
            "segment_id": seg.segment_id, "fact_ids": seg.fact_ids, "prose": prose,
            "pack_hash_at_generation": pack.pack_hash(),
        })
    script_text = "\n".join(prose_parts)
    return script_text, bindings


def script_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode()).hexdigest()[:16]


@dataclass
class DriftResult:
    segment_id: str
    passed: bool
    evidence: str


def validate_binding_integrity(bindings: list, pack: StoryFactPack) -> list:
    """Guard cơ học chạy TRƯỚC MỌI guard/drift khác -- 1 binding có fact_id
    không thuộc pack đang xét (binding bị copy từ 1 topic khác, hoặc pack
    đã bị rebuild sau khi binding được tạo) trả về violation CÓ KIỂM SOÁT
    thay vì để KeyError crash pipeline. Trả về list violation string; RỖNG
    nghĩa là mọi fact_id tồn tại thật VÀ binding thuộc ĐÚNG pack đang xét
    (pack_hash_at_generation khớp)."""
    valid_ids = {f.fact_id for f in pack.facts}
    current_hash = pack.pack_hash()
    violations = []
    for b in bindings:
        unknown = [fid for fid in b.get("fact_ids", []) if fid not in valid_ids]
        if unknown:
            violations.append(
                f"[{b.get('segment_id', '?')}] fact_id {unknown} không tồn tại trong fact pack "
                f"(hash={current_hash}) đang xét -- binding có thể bị copy từ pack/topic khác "
                f"hoặc pack đã bị rebuild sau khi binding được tạo. Fail-closed."
            )
            continue
        gen_hash = b.get("pack_hash_at_generation")
        if gen_hash is not None and gen_hash != current_hash:
            violations.append(
                f"[{b.get('segment_id', '?')}] pack_hash_at_generation={gen_hash} không khớp pack hiện tại "
                f"hash={current_hash} (topic_id={pack.topic_id}) -- binding bị copy từ 1 pack khác "
                f"(có thể trùng fact_id nhưng KHÁC nội dung) hoặc pack đã bị rebuild. Fail-closed."
            )
    return violations


def run_drift_detector(bindings: list, pack: StoryFactPack) -> list:
    """C4_DRIFT_DETECTOR: tái dùng NGUYÊN _score_c4_adversarial_text. Phạm
    vi candidate.core_facts cho segment thứ N là CỘNG DỒN (cumulative) mọi
    fact đã được plan chọn cho segment 1..N -- KHÔNG phải "toàn bộ
    excerpt" (mất tính precision-first) và KHÔNG phải "chỉ đúng fact của
    riêng segment N" (segment sau có thể quy chiếu ngược đại từ/thực thể
    đã giới thiệu ở segment trước -- văn kể chuyện tự nhiên LUÔN tích lũy
    ngữ cảnh, đây không phải hallucination mà là REFERENCE_RESOLUTION).
    Vẫn fail-closed với fact THẬT SỰ mới (không có trong pack, không có
    trong bất kỳ segment nào tới N) vì core_facts vẫn chỉ gồm fact đã được
    plan chọn, không phải fact tự bịa.

    Gọi validate_binding_integrity() TRƯỚC -- fact_id lạ (binding bị copy
    từ pack/topic khác) trả FAIL cho MỌI segment ngay, không chạy C4 trên
    dữ liệu không xác định được nguồn gốc thật."""
    integrity_violations = validate_binding_integrity(bindings, pack)
    if integrity_violations:
        return [
            DriftResult(segment_id=b.get("segment_id", "?"), passed=False,
                        evidence=f"BINDING INTEGRITY FAIL (fail-closed, không chạy C4): {integrity_violations}")
            for b in bindings
        ]
    facts_by_id = {f.fact_id: f for f in pack.facts}
    results = []
    cumulative_ids = []
    for b in bindings:
        cumulative_ids.extend(fid for fid in b["fact_ids"] if fid not in cumulative_ids)
        core_facts = [
            g.CoreFact(fact_id=fid, statement=facts_by_id[fid].proposition, fact_type="story_fact_pack_selected")
            for fid in cumulative_ids
        ]
        candidate = g.CandidateCase(
            case_id=f"DRIFT_{b['segment_id']}", case_key=f"DRIFT_{b['segment_id']}", working_title="drift check",
            domain_topic="Hình Sự", named_individuals=[], core_facts=core_facts, sources=[],
        )
        result = _score_c4_adversarial_text(b["prose"], candidate)
        results.append(DriftResult(segment_id=b["segment_id"], passed=result.passed, evidence=result.evidence))
    return results


def _numeric_tokens(text: str) -> set:
    return set(_NUMBER_RE.findall(text))


def run_deterministic_guards(bindings: list, pack: StoryFactPack) -> list:
    """Guard cơ học ĐỘC LẬP với C4 drift detector -- không cho phép LLM
    'diễn giải' vượt qua đổi số liệu (cùng cơ chế _numeric_tokens_mismatch
    đã dùng trong cl_claim_ledger.py). Gọi validate_binding_integrity()
    TRƯỚC -- nếu có vi phạm integrity, trả ngay violation đó.

    Bound_numbers lấy từ CẢ proposition LẪN source_spans (không chỉ
    proposition): source_spans LÀ nguyên văn từ excerpt (đã validate cơ
    học tồn tại thật -- _span_exists() trong cl_story_fact_pack.py) nên
    số trong đó luôn đáng tin ngang proposition; gộp cả hai loại bỏ false
    positive do khác biệt định dạng chữ số/chữ viết giữa 2 cách diễn đạt
    của CÙNG 1 nguồn thật (vd fact ghi "Mười chín" bằng chữ trong khi
    source_span/prose dùng chữ số "19")."""
    integrity_violations = validate_binding_integrity(bindings, pack)
    if integrity_violations:
        return integrity_violations
    facts_by_id = {f.fact_id: f for f in pack.facts}
    violations = []
    for b in bindings:
        bound_numbers = set()
        for fid in b["fact_ids"]:
            fact = facts_by_id[fid]
            bound_numbers |= _numeric_tokens(fact.proposition)
            for span in fact.source_spans:
                bound_numbers |= _numeric_tokens(span)
        prose_numbers = _numeric_tokens(b["prose"])
        extra = prose_numbers - bound_numbers
        if extra:
            violations.append(f"[{b['segment_id']}] Số liệu {extra} xuất hiện trong văn xuôi nhưng KHÔNG có trong fact đã chọn (proposition + source_spans) -- numeric guard chặn (fail-closed).")
    return violations
