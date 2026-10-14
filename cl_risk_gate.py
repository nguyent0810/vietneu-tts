"""CL Risk Gate -- Discover -> Source Verification -> Risk Score (C1-C7) ->
Dedupe (C8) -> Rank -> Auto-select, cho kênh Hình Sự (CL).

NGUỒN GỐC: implement theo đúng creator_specs không nằm trong repo này mà ở
scratchpad phiên làm việc -- GATE2_DESIGN.md (Autonomous Content Factory,
Part A -- CL Risk Gate), đã qua 8 vòng Codex CLI adversarial review
(APPROVED WITH CAVEATS). File này thay thế dần cho twice_weekly_batch.py's
manual_only blanket flag bằng routing LOW/MEDIUM/HIGH thật.

QUYẾT ĐỊNH UỶ QUYỀN (không lặp lại chi tiết, xem GATE2_DESIGN.md §0): 2
agent con độc lập (Gate 1 audit, Gate 3 implementation) đều từ chối tự xây
dựng cơ chế CL auto-select vì không có cách xác minh độc lập rằng "yêu cầu
đã được người dùng xác nhận trực tiếp" mà agent chỉ nhận qua prompt relay
là thật -- mỗi lần đều được Codex CLI review nhiều vòng đồng tình. Người
dùng sau đó xác nhận TRỰC TIẾP trong chat (không qua relay) rằng: (1) sự cố
Ted Bundy có thật (video từng bị agent tự đăng nhầm case có nạn nhân vị
thành niên, phải huỷ lịch thủ công), (2) vẫn muốn thiết kế CL Risk Gate với
nguyên tắc "độ chắc chắn về bằng chứng (đã xử/lịch sử đã xác lập so với
đang tranh cãi/chưa xử) là ranh giới an toàn thật, không phải bản thân việc
có người thật/chủ đề nhạy cảm" -- và chỉ định CHÍNH thread chính (không
phải agent con) tự code phần này, vì thread chính có xác nhận trực tiếp mà
agent con không thể tự xác minh được.

PHẠM VI FILE NÀY (Stage 1 -- xem GATE2_DESIGN.md, KHÔNG bao gồm toàn bộ):
  - Toàn bộ schema dữ liệu (§1.2).
  - CL_CASE_LEDGER_v1.json -- state machine, ghi atomic (§1.10).
  - discover_candidates() (§1.3) -- đọc trực tiếp các file nghiên cứu
    Markdown đã có sẵn tại DOMAINS/CRIMINAL_LAW/SOURCES/*.md (9 file thật,
    xem GATE1_AUDIT.md) -- dự án này KHÔNG có hạ tầng tự crawl/fetch URL
    trực tiếp (đã xác nhận trong §1, GATE2_DESIGN.md), nên "nguồn" ở đây LÀ
    các file nghiên cứu đã được con người tuyển chọn kèm trích dẫn/URL
    tham khảo, đúng mô hình "human-attested source_text" đã dùng ở
    trending_short_generator.py -- KHÔNG phải fetch trực tiếp từng URL.
  - verify_sources() (§1.4, một phần) -- trích xuất single-pass qua agy
    (named_individuals/core_facts/event_fingerprint/risk_review_draft),
    grounding-check y hệt trending_short_generator.py:extract_facts().
    LegalStatusRecord/RoleVerificationRecord ở đây CHƯA cross-verified
    (cross_verified=False mặc định) -- bước xác minh 2-pass độc lập
    (agy + codex, §1.4.1) là Stage 2 (cl_risk_gate_verification.py, CHƯA
    xây), gọi cross_verify_named_individuals() để lấp field này trước khi
    C5/C6 có thể thật sự PASS.
  - C1, C2, C3, C6, C7 -- logic bảng/mechanical ĐÃ implement (không cần
    LLM adversarial pass riêng ngoài dữ liệu Source Verification đã có).
    QUAN TRỌNG (sửa sau Codex review Stage 1, 2 Blocker thật -- xem lịch sử
    sửa ở score_c6()/_c6_pass_for_individual()): C6 ở Stage 1 KHÔNG THỂ
    PASS cho BẤT KỲ candidate nào, vì mọi nhánh miễn trừ/PASS của C6 giờ
    bắt buộc role_verification.role_cross_verified=True (cho vai trò) và/hoặc
    legal_status.cross_verified=True (cho tình trạng pháp lý/sống-chết) --
    cả 2 field này LUÔN False ở Stage 1 (verify_sources() chỉ trích xuất
    single-pass, không cross-verify). Đây là hành vi ĐÚNG, CỐ Ý, fail-closed
    -- không phải bug: role/legal_status sai lệch do 1 lần LLM trích xuất
    duy nhất là chính con đường 1 người CÒN SỐNG, CHƯA kết án có thể bị PASS
    oan nếu không chặn. C1/C2/C3 cũng fail-closed cấu trúc (verify_sources()
    chưa gán corroborating_source_ids cho core_facts vì Stage 1 không xác
    định được excerpt trích từ URL cụ thể nào -- xem comment tại chỗ xây
    core_facts). C4 (LLM adversarial review) và C5 (protocol affirmtive dài,
    HISTORICAL_CONSENSUS) đòi hỏi risk_review_draft đã được LLM review --
    ĐỂ Ở Stage 2, cùng với việc thật sự lấp role_cross_verified/
    legal_status.cross_verified để C6 (và C1-C3's per-fact source
    attribution) có thể PASS thật với dữ liệu tốt.
  - tier_for() (§1.8) -- dùng được ngay khi có đủ CriterionResult.
  - CL_CASE_LEDGER_v1.json state machine + atomic write (§1.10).
  - Dedupe C8 (§1.11) -- stage 1 blocking (deterministic) + stage 2 LLM
    4-way verdict (codex).
  - rank_candidates() (§1.12).

CHƯA LÀM (Stage 2/3, xem creator_specs task tracker #240/#241/#242):
  - Dual-pass cross-verification thật (agy+codex độc lập, §1.4.1).
  - C4, C5, Claim-and-Exposure Gate (§1.6).
  - Phase B/C/D lifecycle (render-withheld, post-render review,
    UploadManifest, §1.13) + wiring vào twice_weekly_batch.py.
  - KHÔNG có gì trong file này được gọi bởi bất kỳ pipeline production
    nào (twice_weekly_batch.py's manual_only flag CHƯA bị thay) -- an
    toàn, không đổi hành vi hệ thống hiện tại cho tới khi toàn bộ gate qua
    Codex review thật và task #241 wire nó vào."""
import hashlib
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from content_seo import _run_agy, _run_codex, _extract_json, ContentSeoError  # noqa: E402
from registry_lock import FileLock  # noqa: E402

SOURCES_DIR = PROJECT_ROOT / "content_repo_clone" / "DOMAINS" / "CRIMINAL_LAW" / "SOURCES"
CASE_LEDGER_PATH = PROJECT_ROOT / "creator_specs" / "CL_CASE_LEDGER_v1.json"
SOURCE_TIERS_PATH = PROJECT_ROOT / "creator_specs" / "CL_SOURCE_TIERS_v1.json"
RETROSPECTIVE_TYPES_PATH = PROJECT_ROOT / "creator_specs" / "CL_RETROSPECTIVE_SOURCE_TYPES_v1.json"
LOCK_DIR = PROJECT_ROOT / "output" / "locks"
SCORER_VERSION = "cl_risk_gate_v1"


class CLRiskGateError(RuntimeError):
    pass


# =============================================================================
# §1.2 -- Enums
# =============================================================================

class PublisherTier(str, Enum):
    REPUTABLE_PRESS = "reputable_press"
    PUBLIC_RECORD = "public_record"
    AGGREGATOR = "aggregator"
    SOCIAL_MEDIA = "social_media"
    UNKNOWN = "unknown"


class VerdictStatus(str, Enum):
    ADJUDICATED_CONVICTED = "adjudicated_convicted"
    ADJUDICATED_ACQUITTED = "adjudicated_acquitted"
    HISTORICAL_CONSENSUS = "historical_consensus"
    UNDER_INVESTIGATION = "under_investigation"
    UNRESOLVED_DISPUTED = "unresolved_disputed"


class LifeStatus(str, Enum):
    LIVING = "living"
    DECEASED = "deceased"
    UNKNOWN = "unknown"  # fail-closed -> treated as is_living=True cho C6 trừ khi có bằng chứng khẳng định


class DispositionStatus(str, Enum):
    CONVICTED = "convicted"
    ACQUITTED = "acquitted"
    NOT_CHARGED = "not_charged"
    UNDER_INVESTIGATION = "under_investigation"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class FinalityState(str, Enum):
    FINAL = "final"
    UNDER_APPEAL = "under_appeal"
    VACATED = "vacated"
    AMNESTIED = "amnestied"
    UNKNOWN = "unknown"  # mặc định khi không có nguồn khẳng định trực tiếp -- im lặng KHÔNG BAO GIỜ nâng lên FINAL


class DecisionIdentifierConsistency(str, Enum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class CaseLedgerStatus(str, Enum):
    SURFACED = "surfaced"
    VERIFYING = "verifying"
    LOW_CLEARED = "low_cleared"
    MEDIUM_IN_PROGRESS = "medium_in_progress"
    ESCALATED_HIGH = "escalated_high"
    ESCALATED_MEDIUM_EXHAUSTED = "escalated_medium_exhausted"
    REJECTED_DUPLICATE = "rejected_duplicate"
    REJECTED_POLICY = "rejected_policy"
    MERGED_INTO = "merged_into"
    AUTO_SELECTED = "auto_selected"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    DRAFT = "draft"
    HUMAN_APPROVED = "human_approved"


# =============================================================================
# §1.2 -- Dataclasses
# =============================================================================

@dataclass
class FieldEvidence:
    source_id: str
    supporting_excerpt_ref: str


@dataclass
class LegalStatusRecord:
    disposition: DispositionStatus = DispositionStatus.UNKNOWN
    disposition_evidence: list = field(default_factory=list)
    life_status: LifeStatus = LifeStatus.UNKNOWN
    life_status_evidence: list = field(default_factory=list)
    jurisdiction: str | None = None
    decision_body: str | None = None
    decision_identifier: str | None = None
    decision_identifier_consistent: DecisionIdentifierConsistency = DecisionIdentifierConsistency.INSUFFICIENT_EVIDENCE
    decision_date: str | None = None
    finality_state: FinalityState = FinalityState.UNKNOWN
    finality_evidence: list = field(default_factory=list)
    interpretations_agree: bool = False
    evidence_requirement_satisfied: bool = False
    cross_verified: bool = False  # LUÔN False cho tới khi Stage 2's cross_verify_named_individuals() chạy thật
    evidentiary_path: str | None = None  # "allowlisted_public_record" | "two_independent_qualified_sources" | None
    pass1_model_config: str | None = None
    pass2_model_config: str | None = None
    verified_at: str | None = None


@dataclass
class RoleVerificationRecord:
    pass1_role: str = ""
    pass2_role: str = ""
    role_interpretations_agree: bool = False
    role_evidence_requirement_satisfied: bool = False
    role_cross_verified: bool = False
    pass1_model_config: str | None = None
    pass2_model_config: str | None = None
    pass1_role_evidence: list = field(default_factory=list)
    pass2_role_evidence: list = field(default_factory=list)
    pass1_raw_response_ref: str | None = None
    pass2_raw_response_ref: str | None = None


@dataclass
class SourceRecord:
    source_id: str
    url: str
    publisher: str
    publisher_tier: PublisherTier
    source_lineage_id: str
    origin_claim: str
    independence_verified: bool
    retrieved_at: str
    page_content_hash: str
    excerpt_hash: str
    excerpt_context_window: str
    excerpt: str
    excerpt_entailment_note: str
    supports_fact_ids: list = field(default_factory=list)


@dataclass
class CoreFact:
    fact_id: str
    statement: str
    fact_type: str
    corroborating_source_ids: list = field(default_factory=list)
    corroborating_lineage_ids: list = field(default_factory=list)
    corroborating_verified_independent_lineage_ids: list = field(default_factory=list)


@dataclass
class NamedIndividual:
    canonical_name: str
    identity_confidence: str  # "high" | "low"
    role: str  # victim | official_capacity | convicted_perpetrator | acquitted | accused_unconvicted | named_relative_or_associate
    role_verification: RoleVerificationRecord = field(default_factory=RoleVerificationRecord)
    legal_status: LegalStatusRecord = field(default_factory=LegalStatusRecord)
    short_form_alias: str | None = None
    short_form_confidence: str | None = None
    name_match_is_retrieval_only: bool = True


@dataclass
class FinalReferenceEntry:
    reference_text: str
    resolved_individual: str | None
    detection_mechanism: str
    status: str
    detected_at_phase: str


@dataclass
class EventFingerprint:
    normalized_core_act: str
    date_range: tuple | None
    locations: list = field(default_factory=list)
    organizations: list = field(default_factory=list)
    all_named_individuals: list = field(default_factory=list)
    decision_identifiers: list = field(default_factory=list)


@dataclass
class CandidateCase:
    case_id: str
    case_key: str
    working_title: str
    domain_topic: str = "Hình Sự"
    discovered_at: str = ""
    discovery_source_file: str = ""
    named_individuals: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    core_facts: list = field(default_factory=list)
    verdict_status: VerdictStatus | None = None
    event_fingerprint: EventFingerprint | None = None
    risk_review_draft: str | None = None
    final_script: str | None = None
    final_referenced_individuals: list = field(default_factory=list)


@dataclass
class ClaimRecord:
    claim_id: str
    text: str
    surface: str
    segment_index: int
    category: str | None
    about_individual: str | None
    evidence_fact_ids: list
    entailment_strength: str | None
    necessity_verified: bool | None
    verified: bool


@dataclass
class CriterionResult:
    criterion_id: str
    passed: bool
    evidence: str
    checked_by: str
    raw_response_ref: str | None = None


@dataclass
class RiskScoreResult:
    tier: str
    criteria: list
    failing_criteria: list
    high_risk_triggers: list
    rationale: str
    scorer_version: str
    allowlist_version: str
    scored_at: str


@dataclass
class DedupeResult:
    is_duplicate: bool
    verdict: str | None
    matched_case_id: str | None
    matched_case_status: str | None
    related_case_ids: list
    method: str
    dedupe_confidence: str  # "high" | "low"
    candidates_compared: list
    evidence: str


@dataclass
class CaseLedgerEntry:
    case_id: str
    canonical_names: list
    title_keywords: list
    fingerprint: EventFingerprint | None
    status: CaseLedgerStatus
    policy_trigger: str | None
    rejection_scope: str | None
    recheck_policy: str | None
    evidence_as_of: str | None
    next_eligible_review_at: str | None
    pending_alias_write: bool
    merged_into_case_id: str | None
    first_seen_at: str
    last_updated_at: str
    history: list = field(default_factory=list)


# =============================================================================
# JSON (de)serialization helpers -- dataclasses chứa Enum members, cần tự xử
# lý (dataclasses.asdict() giữ nguyên Enum object, không tự thành JSON được).
# =============================================================================

def _to_jsonable(obj):
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj):
        return {f.name: _to_jsonable(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    return obj


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# Config loaders -- fail-closed y hệt domain_creative_profiles.py's
# CL_REAL_PERSONS_LEDGER_FILE loader (file thiếu/hỏng => raise, KHÔNG âm
# thầm dùng danh sách rỗng cho 1 cơ chế an toàn nội dung).
# =============================================================================

def load_source_tiers() -> dict:
    if not SOURCE_TIERS_PATH.exists():
        raise CLRiskGateError(f"Không tìm thấy {SOURCE_TIERS_PATH} -- DỪNG (fail-closed), không thể phân loại publisher_tier.")
    try:
        data = json.loads(SOURCE_TIERS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CLRiskGateError(f"Không đọc được {SOURCE_TIERS_PATH} ({exc}) -- DỪNG (fail-closed).") from exc
    if not isinstance(data, dict) or "domains" not in data or not isinstance(data["domains"], dict):
        raise CLRiskGateError(f"{SOURCE_TIERS_PATH} sai cấu trúc (thiếu 'domains' object) -- DỪNG (fail-closed).")
    return data


def load_retrospective_types() -> dict:
    if not RETROSPECTIVE_TYPES_PATH.exists():
        raise CLRiskGateError(f"Không tìm thấy {RETROSPECTIVE_TYPES_PATH} -- DỪNG (fail-closed).")
    try:
        return json.loads(RETROSPECTIVE_TYPES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CLRiskGateError(f"Không đọc được {RETROSPECTIVE_TYPES_PATH} ({exc}) -- DỪNG (fail-closed).") from exc


def _extract_domain(url: str) -> str:
    match = re.match(r"^https?://([^/]+)", url.strip())
    return match.group(1).lower() if match else ""


def classify_publisher_tier(url: str, tiers_config: dict) -> PublisherTier:
    """Phân loại THEO ĐÚNG domain (không path prefix trong v1 -- danh sách
    allowlist khởi tạo dùng domain-level; per-article downgrade [Medium M1,
    §1.4.2] là việc của LLM extraction pass ở verify_sources(), KHÔNG phải
    hàm này -- hàm này CHỈ tra allowlist tĩnh). Domain KHÔNG có trong
    allowlist => UNKNOWN, KHÔNG BAO GIỜ tự nâng hạng (§1.7)."""
    domain = _extract_domain(url)
    entry = tiers_config.get("domains", {}).get(domain)
    if not entry:
        return PublisherTier.UNKNOWN
    try:
        return PublisherTier(entry["tier"])
    except (KeyError, ValueError):
        return PublisherTier.UNKNOWN


# =============================================================================
# §1.10 -- CL_CASE_LEDGER_v1.json: state machine, atomic writes
# =============================================================================

def _atomic_write_json(path: Path, data: dict) -> None:
    """Ghi tạm cùng thư mục rồi fsync + os.replace() -- cùng kỹ thuật
    registry_lock.py::write_registry_atomic() đã dùng cho registry.json
    (§1.10: 'reuses registry_lock.py's exact proven pattern'), KHÔNG tái
    dùng thẳng hàm đó vì nó gắn với schema/production-write-gate riêng của
    registry.json (mark_production_entry/_is_production_write_allowed) --
    không áp dụng cho ledger này.

    FIX (Codex review Stage 1, Low #10): tên tmp cũ chỉ dùng PID -- 2 thread
    CÙNG process gọi trực tiếp (không qua FileLock, vd lỗi lập trình tương
    lai) sẽ đụng cùng tmp path. Dùng tempfile.mkstemp() (unique thật, kernel
    đảm bảo) thay vì tự ghép PID. Cũng fsync THƯ MỤC CHA sau os.replace() --
    trên 1 số filesystem, rename không đảm bảo durable qua mất điện nếu
    directory entry chưa fsync (write_registry_atomic() gốc cũng chưa làm
    bước này, nhưng ledger này an toàn nội dung, nên siết chặt hơn)."""
    import tempfile
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
    dir_fd = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def _read_ledger_raw() -> dict:
    if not CASE_LEDGER_PATH.exists():
        return {}
    try:
        data = json.loads(CASE_LEDGER_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CLRiskGateError(f"Không đọc được {CASE_LEDGER_PATH} ({exc}) -- DỪNG (fail-closed), không tự tạo ledger mới đè lên dữ liệu có thể vẫn đọc được 1 phần.") from exc
    if not isinstance(data, dict):
        raise CLRiskGateError(f"{CASE_LEDGER_PATH} không phải object JSON cấp cao nhất -- DỪNG (fail-closed).")
    return data


def _entry_to_dict(entry: CaseLedgerEntry) -> dict:
    return _to_jsonable(entry)


def _ledger_date_range(raw) -> tuple | None:
    """FIX (Codex review round 1, Low #7): _entry_from_dict() trước đây tin
    THẲNG bất kỳ giá trị truthy nào của fp['date_range'] thành tuple, không
    kiểm tra số phần tử/kiểu/lịch hợp lệ -- ledger đọc từ đĩa (có thể bị sửa
    tay/hỏng 1 phần) rồi được stage1_blocking() index [0]/[1] trực tiếp, dữ
    liệu thiếu phần tử sẽ crash, dữ liệu sai định dạng sẽ làm overlap tính
    sai. Validate lại đúng cùng quy tắc _valid_date_range_value() dùng khi
    TRÍCH mới, VÀ cùng quy tắc từ chối mixed precision của _extract_date_
    range() (FIX Codex review round 2, MEDIUM #5 -- áp dụng nhất quán cả 2
    nơi) -- không hợp lệ -> None (fail-closed), không crash/không tin liều."""
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        return None
    start, end = raw
    if not isinstance(start, str) or not isinstance(end, str):
        return None
    if not _valid_date_range_value(start) or not _valid_date_range_value(end):
        return None
    if len(start) != len(end):
        return None
    return (start, end) if start <= end else (end, start)


def _entry_from_dict(d: dict) -> CaseLedgerEntry:
    fp = d.get("fingerprint")
    fingerprint = EventFingerprint(
        normalized_core_act=fp["normalized_core_act"], date_range=_ledger_date_range(fp.get("date_range")),
        locations=fp.get("locations", []), organizations=fp.get("organizations", []),
        all_named_individuals=fp.get("all_named_individuals", []), decision_identifiers=fp.get("decision_identifiers", []),
    ) if fp else None
    return CaseLedgerEntry(
        case_id=d["case_id"], canonical_names=d.get("canonical_names", []), title_keywords=d.get("title_keywords", []),
        fingerprint=fingerprint, status=CaseLedgerStatus(d["status"]), policy_trigger=d.get("policy_trigger"),
        rejection_scope=d.get("rejection_scope"), recheck_policy=d.get("recheck_policy"),
        evidence_as_of=d.get("evidence_as_of"), next_eligible_review_at=d.get("next_eligible_review_at"),
        pending_alias_write=d.get("pending_alias_write", False), merged_into_case_id=d.get("merged_into_case_id"),
        first_seen_at=d["first_seen_at"], last_updated_at=d["last_updated_at"], history=d.get("history", []),
    )


class CaseLedger:
    """Load 1 lần vào bộ nhớ. MỌI thay đổi thật phải đi qua
    upsert_entry_locked() (giữ FileLock trong suốt đọc-sửa-ghi, đúng pattern
    twice_weekly_batch.py's per-channel FileLock, §1.10's 'atomic invariant'
    yêu cầu 1 lock bao trọn transaction chứ không chỉ bước ghi)."""

    def __init__(self, entries: dict):
        self.entries = entries  # case_id -> CaseLedgerEntry

    @classmethod
    def load(cls) -> "CaseLedger":
        raw = _read_ledger_raw()
        return cls({cid: _entry_from_dict(d) for cid, d in raw.items() if not cid.startswith("_")})

    def get(self, case_id: str) -> CaseLedgerEntry | None:
        return self.entries.get(case_id)

    def all_entries(self) -> list:
        return list(self.entries.values())

    def find_by_case_key(self, case_key: str) -> CaseLedgerEntry | None:
        for entry in self.entries.values():
            if case_key in entry.title_keywords:
                return entry
        return None


def upsert_entry_locked(case_id: str, mutate_fn, lock_dir: Path = LOCK_DIR) -> CaseLedgerEntry:
    """FIX (Codex review Stage 1, Medium #8 -- lost update): chữ ký CŨ nhận
    thẳng 1 `entry` đã được caller load/sửa TRƯỚC KHI vào lock -- 2 worker
    cùng load case X, mỗi worker sửa 1 field khác nhau, worker sau upsert
    sẽ GHI ĐÈ nguyên object của mình lên, XOÁ MẤT thay đổi worker trước vừa
    ghi (vì cả 2 đều dựa trên cùng bản đọc CŨ). Chữ ký MỚI nhận
    `mutate_fn(current_entry_or_None) -> CaseLedgerEntry` -- toàn bộ
    đọc-sửa-quyết định-ghi giờ chạy TRỌN VẸN BÊN TRONG lock (đúng pattern
    twice_weekly_batch.py's 'read lại số liệu THẬT trong lúc giữ lock,
    không dùng số đã tính ở ngoài' đã áp dụng cho race tương tự), loại bỏ
    hẳn khả năng ghi đè 1 bản đọc đã stale."""
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / "cl_case_ledger"
    with FileLock(lock_path):
        raw = _read_ledger_raw()
        current = _entry_from_dict(raw[case_id]) if case_id in raw else None
        new_entry = mutate_fn(current)
        # FIX (Codex review Stage 1 round 2, Medium mới #2): mutate_fn là
        # callback do caller cung cấp -- 1 callback lỗi (trả sai kiểu, đổi
        # case_id) trước đây sẽ âm thầm tạo 1 entry MỚI trong ledger dưới
        # case_id khác trong khi entry CŨ vẫn còn nguyên (rác 2 bản), hoặc
        # crash muộn/khó hiểu trong lúc serialize. Validate NGAY, trong
        # lock, trước khi ghi bất cứ gì.
        if not isinstance(new_entry, CaseLedgerEntry):
            raise CLRiskGateError(f"mutate_fn phải trả về CaseLedgerEntry, nhận {type(new_entry).__name__}.")
        if new_entry.case_id != case_id:
            raise CLRiskGateError(f"mutate_fn đổi case_id ({case_id!r} -> {new_entry.case_id!r}) -- không được phép, dùng upsert_entry_locked riêng cho case_id mới nếu thật sự cần.")
        raw[new_entry.case_id] = _entry_to_dict(new_entry)
        _atomic_write_json(CASE_LEDGER_PATH, raw)
        return new_entry


def surface_candidate_locked(case_id: str, case_key: str, working_title: str, discovery_source_file: str, lock_dir: Path = LOCK_DIR) -> bool:
    """§1.3: mint case_id + ghi SURFACED NGAY, TRƯỚC KHI verify -- idempotent
    (nếu case_id đã tồn tại, không ghi đè trạng thái/lịch sử hiện có -- trả
    về False, coi là 'đã surfaced từ trước', khớp §1.10's honest-scope
    guarantee 'mọi candidate đã extract thành công được giữ atomic từ lúc
    đó', không phải ghi đè mù quáng mỗi lần discover chạy lại)."""
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / "cl_case_ledger"
    with FileLock(lock_path):
        raw = _read_ledger_raw()
        if case_id in raw:
            return False
        now = _now_iso()
        entry = CaseLedgerEntry(
            case_id=case_id, canonical_names=[], title_keywords=[case_key], fingerprint=None,
            status=CaseLedgerStatus.SURFACED, policy_trigger=None, rejection_scope=None, recheck_policy=None,
            evidence_as_of=None, next_eligible_review_at=None, pending_alias_write=False, merged_into_case_id=None,
            first_seen_at=now, last_updated_at=now,
            history=[{"at": now, "from_status": None, "to_status": "surfaced", "reason": f"discovered từ {discovery_source_file}"}],
        )
        raw[case_id] = _entry_to_dict(entry)
        _atomic_write_json(CASE_LEDGER_PATH, raw)
        return True


# =============================================================================
# §1.3 -- Discover
# =============================================================================

_CASE_HEADING_RE = re.compile(r"^## \d+\.\s+(.+)$", re.MULTILINE)
_REFERENCES_HEADING_RE = re.compile(r"^### Nguồn tham khảo\s*$", re.MULTILINE)
_NEXT_HEADING_RE = re.compile(r"^(##|###)\s", re.MULTILINE)
# FIX (Codex review Stage 1 round 5, Medium/Low caveat): regex CŨ loại ')'
# ngay ở character class -- khiến _strip_trailing_url_punctuation()'s logic
# "giữ ')' nếu cân bằng với '('" không bao giờ có cơ hội chạy, vì URL đã bị
# cắt trước khi tới đó (vd "wiki/X_(disambiguation)" bị cắt mất ")"). Nhận
# ')' vào match, để _strip_trailing_url_punctuation() (hàm CÓ logic cân
# bằng ngoặc thật) quyết định giữ hay cắt.
_URL_RE = re.compile(r"https?://[^\s>\]]+")


def _slugify_case_key(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", normalized.lower()).strip("_")


def _split_source_file_into_cases(text: str) -> list[tuple[str, str]]:
    """Tách 1 file RESEARCH_DRAFT_*.md thành các đoạn '## N. Vụ án ...'
    riêng biệt -- KHỚP đúng cấu trúc thật đã xác nhận trong
    content_repo_clone/DOMAINS/CRIMINAL_LAW/SOURCES/*.md (vd
    RESEARCH_DRAFT_AN_DA_XU.md: '## 1. Vụ án Năm Cam...', '## 2. Vụ án Lê
    Văn Luyện...'). File/section không khớp pattern này (vd
    SOURCE_REGISTRY.md, hoặc phần mở đầu trước heading '## 1.' đầu tiên) bị
    bỏ qua -- không tự đoán ranh giới case."""
    headings = list(_CASE_HEADING_RE.finditer(text))
    cases = []
    for i, m in enumerate(headings):
        title = m.group(1).strip()
        start = m.start()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        cases.append((title, text[start:end]))
    return cases


def _strip_trailing_url_punctuation(url: str) -> str:
    """FIX (Codex review Stage 1 round 4, Medium/Low): _URL_RE khớp tham
    lam tới ký tự whitespace/)>] gần nhất -- dấu câu cuối câu văn thường
    (., ,, ;, ", ') hay bị dính vào URL trần trong văn bản Markdown (vd
    "...xem tại https://a.example.com/x." -- dấu . thuộc câu văn, không
    thuộc URL). Giữ NGUYÊN URL nếu ')' cân bằng với '(' trong chuỗi (URL
    Wikipedia/MediaWiki thật có thể chứa dấu ngoặc hợp lệ, vd
    "...wiki/X_(disambiguation)") -- chỉ cắt dấu câu kết thúc câu ở cuối,
    không cắt ')' hợp lệ."""
    trailing_sentence_punct = ".,;:!?\"'"
    while url and url[-1] in trailing_sentence_punct:
        url = url[:-1]
    # ')' ở cuối chỉ cắt nếu KHÔNG cân bằng với '(' trong URL (vd URL bị
    # theo sau bởi "(xem thêm)" trong markdown, không phải 1 phần URL).
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1]
    return url


def _extract_reference_urls(case_text: str) -> list[str]:
    ref_match = _REFERENCES_HEADING_RE.search(case_text)
    if not ref_match:
        return []
    rest = case_text[ref_match.end():]
    next_heading = _NEXT_HEADING_RE.search(rest)
    references_block = rest[:next_heading.start()] if next_heading else rest
    return [_strip_trailing_url_punctuation(u) for u in _URL_RE.findall(references_block)]


def discover_candidates(sources_dir: Path = SOURCES_DIR, lock_dir: Path = LOCK_DIR, dry_run: bool = False) -> list[dict]:
    """Trả về danh sách stub {case_id, case_key, working_title,
    discovery_source_file, case_text, reference_urls} -- verify_sources()
    xử lý tiếp mỗi stub. dry_run=True: KHÔNG ghi SURFACED vào ledger (§1.13
    dry-run purity), chỉ tính toán trong bộ nhớ."""
    if not sources_dir.exists():
        raise CLRiskGateError(f"Không tìm thấy thư mục nguồn CL: {sources_dir}")

    stubs = []
    for md_file in sorted(sources_dir.glob("*.md")):
        if md_file.name == "SOURCE_REGISTRY.md":
            continue
        text = md_file.read_text(encoding="utf-8")
        for title, case_text in _split_source_file_into_cases(text):
            case_key = _slugify_case_key(title)
            case_id = hashlib.sha256(f"{md_file.name}:{_slugify_case_key(title)}".encode("utf-8")).hexdigest()[:16]
            if not dry_run:
                surface_candidate_locked(case_id, case_key, title, md_file.name, lock_dir=lock_dir)
            stubs.append({
                "case_id": case_id, "case_key": case_key, "working_title": title,
                "discovery_source_file": md_file.name, "case_text": case_text,
                "reference_urls": _extract_reference_urls(case_text),
            })
    return stubs


# =============================================================================
# §1.4 -- Source Verification (single-pass extraction; cross-verification
# thật là Stage 2, xem docstring đầu file)
# =============================================================================

_EXTRACT_CASE_FACTS_PROMPT = """Bạn là chuyên gia trích xuất dữ kiện có cấu trúc từ 1 đoạn nghiên cứu vụ án hình sự tiếng Việt, phục vụ hệ thống chấm điểm an toàn nội dung TỰ ĐỘNG (KHÔNG phải sinh kịch bản) -- vì vậy PHẢI trung thực tuyệt đối, KHÔNG suy đoán/bổ sung chi tiết không có trong văn bản.

=== VĂN BẢN NGUỒN (nguyên văn, căn cứ DUY NHẤT) ===
{case_text}

Trích xuất:
1. "named_individuals": mảng object, MỖI người thật được nêu tên trong văn bản (không phân biệt vai trò -- nạn nhân, bị cáo, điều tra viên, người thân...), mỗi object:
   {{"canonical_name": "...", "role": "victim|official_capacity|convicted_perpetrator|acquitted|accused_unconvicted|named_relative_or_associate", "disposition": "convicted|acquitted|not_charged|under_investigation|not_applicable|unknown", "disposition_excerpt": "câu/đoạn NGUYÊN VĂN xác nhận disposition (rỗng nếu unknown)", "life_status": "living|deceased|unknown", "life_status_excerpt": "câu NGUYÊN VĂN xác nhận sống/chết (rỗng nếu unknown)", "finality_state": "final|under_appeal|vacated|amnestied|unknown", "finality_excerpt": "câu NGUYÊN VĂN xác nhận hiệu lực bản án (rỗng nếu unknown)", "identity_confidence": "high nếu có định danh riêng biệt (số hiệu bản án) HOẶC >=2 thuộc tính phân biệt (năm sinh VÀ quê quán) khớp nhau giữa các nguồn, low nếu không"}}
2. "core_facts": mảng object, MỖI dữ kiện cốt lõi (danh tính người bị kết án/buộc tội, hành vi phạm tội chính, kết quả pháp lý từng người, tình trạng kháng cáo/hiệu lực từng người, mức độ chi tiết nhận dạng nạn nhân đã có sẵn trong nguồn), mỗi object:
   {{"fact_id": "F1", "statement": "...", "fact_type": "identity|criminal_act|legal_outcome|appeal_status|victim_detail", "excerpt": "câu NGUYÊN VĂN chứng minh"}}
3. "event_fingerprint": {{"normalized_core_act": "mô tả NGẮN loại hành vi (KHÔNG bao gồm disposition/finality)", "locations": ["..."], "organizations": ["..."], "decision_identifiers": ["số hiệu bản án nếu có"], "date_range_start": "năm hoặc ngày HÀNH VI PHẠM TỘI CHÍNH thật sự xảy ra BẮT ĐẦU -- TUYỆT ĐỐI KHÔNG dùng ngày khởi tố/điều tra/xét xử/bản án có hiệu lực/đăng báo trừ khi chính khung thời gian tố tụng đó LÀ sự kiện đang mô tả, định dạng 'YYYY' hoặc 'YYYY-MM-DD', RỖNG nếu văn bản không nêu rõ thời điểm hành vi", "date_range_end": "năm hoặc ngày HÀNH VI PHẠM TỘI CHÍNH KẾT THÚC (hoặc bằng date_range_start nếu chỉ 1 thời điểm) -- cùng quy tắc loại trừ ngày tố tụng như trên, RỖNG nếu không nêu rõ", "date_range_excerpt": "câu/đoạn NGUYÊN VĂN chứng minh CHÍNH XÁC 2 giá trị date_range_start/end ở trên (không phải chỉ 'có nhắc tới thời gian' chung chung) -- RỖNG nếu date_range_start/end đều rỗng"}}

Trả về CHỈ 1 JSON object:
{{"named_individuals": [...], "core_facts": [...], "event_fingerprint": {{...}}}}"""


def _normalize_for_substring_check(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _excerpt_grounded(excerpt, source_text: str) -> bool:
    if not isinstance(excerpt, str) or not excerpt.strip():
        return False
    return _normalize_for_substring_check(excerpt) in _normalize_for_substring_check(source_text)


def _hash_text(text: str) -> str:
    return hashlib.sha256(_normalize_for_substring_check(text).encode("utf-8")).hexdigest()


_DATE_RANGE_YEAR_RE = re.compile(r"^\d{4}$")
_DATE_RANGE_FULL_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATE_RANGE_MIN_YEAR, _DATE_RANGE_MAX_YEAR = 1900, 2100


def _valid_date_range_value(value: str) -> bool:
    """'YYYY' hoặc 'YYYY-MM-DD' hợp lệ THẬT (lịch có thật, năm trong biên
    hợp lý cho hồ sơ vụ án) -- FIX (Codex review round 1, Medium #3): regex
    hình dạng suông trước đây chấp nhận '0000', '9999-99-99', '2021-02-29'
    (không phải năm nhuận). datetime.strptime() validate lịch thật, kể cả
    nhuận."""
    if _DATE_RANGE_YEAR_RE.match(value):
        year = int(value)
        return _DATE_RANGE_MIN_YEAR <= year <= _DATE_RANGE_MAX_YEAR
    if _DATE_RANGE_FULL_RE.match(value):
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return False
        return _DATE_RANGE_MIN_YEAR <= parsed.year <= _DATE_RANGE_MAX_YEAR
    return False


def _date_range_bound(value: str, *, latest: bool) -> str:
    """Mở rộng 1 giá trị date_range ('YYYY' kém chính xác hơn 'YYYY-MM-DD')
    thành 1 mốc ISO đầy đủ để SO SÁNH overlap -- FIX (Codex review round 1,
    HIGH #4): so sánh string thô trước đây làm '2001' < '2001-06-15' (Python
    coi tiền tố ngắn hơn là "nhỏ hơn"), khiến 1 case chỉ có năm và 1 case có
    ngày CÙNG năm bị tính SAI là không trùng lặp thời gian -- hướng SAI cho
    hệ thống fail-closed (bỏ lọt duplicate còn nguy hiểm hơn escalate oan).
    latest=False mở rộng về ĐẦU năm (mốc dưới), latest=True về CUỐI năm (mốc
    trên) -- luôn mở rộng theo hướng AN TOÀN HƠN cho overlap check. Giá trị
    đã đủ 'YYYY-MM-DD' thì không còn gì để mở rộng, trả nguyên."""
    if _DATE_RANGE_YEAR_RE.match(value):
        return f"{value}-12-31" if latest else f"{value}-01-01"
    return value


# FIX (Codex review round 4, task #262, MEDIUM): '-' ASCII không phải dấu
# gạch nối/gạch ngang DUY NHẤT xuất hiện trong văn bản thật -- text copy từ
# Word/PDF thường chứa các biến thể Unicode trông giống hệt nhưng KHÔNG
# khớp lớp `[\w/-]` (vd "2001–A", "A–24/8/2011–B" với en dash '–' U+2013
# thay vì ASCII '-'), khiến ranh giới round 3 vẫn lọt. Liệt kê tường minh
# các dash Unicode thường gặp -- KHÔNG được hưởng ngoại lệ "range liền kề"
# (chỉ ASCII '-' mới có ngoại lệ đó, xem _cue_anchored_years()).
_DATE_RANGE_UNICODE_DASHES = "‐‑‒–—−"  # ‐ ‑ ‒ – — −
_DATE_RANGE_IDENTIFIER_BOUNDARY_CLASS = r"[\w/\-" + _DATE_RANGE_UNICODE_DASHES + r"]"
_DATE_RANGE_CUE_THEN_YEAR_RE = re.compile(
    r"(?<!" + _DATE_RANGE_IDENTIFIER_BOUNDARY_CLASS + r")(?:năm|tháng|ngày|khoảng|hồi|vào) +(\d{4})",
    re.IGNORECASE,
)
_DATE_RANGE_CLEAN_YEAR_RANGE_TAIL_RE = re.compile(r"-(\d{4})(?!" + _DATE_RANGE_IDENTIFIER_BOUNDARY_CLASS + r")")


def _cue_anchored_years(excerpt: str) -> list:
    """MỌI token 4-chữ-số được 1 (đúng 1, KHÔNG nối chuỗi) từ cue thời gian
    đứng NGAY TRƯỚC xác nhận trực tiếp -- trả list (start, end). CHỈ hướng
    cue -> năm, KHÔNG chấp nhận cue đứng SAU năm (xem docstring
    _year_value_entailed_by_excerpt cho lý do).

    FIX (Codex review round 5, HIGH #1 -- 2 vấn đề mới sau khi round 4's
    thiết kế 1-chiều đã đóng đúng bypass round 4): (a) bản trước dùng `\\s+`
    làm dấu phân cách -- khớp CẢ newline/tab, khiến 1 cue ở CUỐI DÒNG này
    "neo" nhầm 1 số ở ĐẦU DÒNG KẾ TIẾP không liên quan (repro: "...không rõ
    năm\\n2001 là số bản án." -- '2001' bị xác nhận sai). Giờ CHỈ chấp nhận
    dấu cách thường (` +`) -- không tab, không newline (Codex xác nhận tab
    cho false positive tương tự newline). (b) bản trước còn cho
    phép NỐI CHUỖI nhiều từ cue liên tiếp ("vào năm" thành 1 cụm) qua
    `(?:\\s+(?:cue))*` -- nhóm lặp lồng nhau này có rủi ro thời gian chạy
    O(n^2)/backtracking bất thường trên input cố ý có nhiều cue liên tiếp
    KHÔNG kết thúc bằng năm (case_text tới từ nguồn nghiên cứu bên ngoài,
    KHÔNG phải input tin cậy tuyệt đối). Việc nối chuỗi thật ra KHÔNG CẦN
    THIẾT -- với "vào năm 2001", từ NGAY TRƯỚC năm luôn là "năm" (đã tự nó
    là 1 cue hợp lệ), nên chỉ cần khớp ĐÚNG 1 từ cue ngay trước năm là đủ
    cho MỌI cách viết tiếng Việt thực tế đã kiểm chứng -- loại bỏ nhóm lặp
    lồng nhau, quét tuyến tính O(n), không còn rủi ro backtracking.

    FIX (Codex review round 3, task #262, MEDIUM -- '/' và '-' không nằm
    trong `\\w` nên ranh giới round 2 vẫn lọt số hiệu bản án/quyết định
    dùng CHÍNH 2 dấu này làm phân cách, vd "năm 2001/QĐ-TA" hay "năm 2001-A"
    -- Vụ án THẬT thường viết số hiệu quyết định dạng "<số>/<năm>/QĐ-<toà>",
    khiến '/'/'−' liền ngay sau 1 năm CÓ THỂ là phần số hiệu, không phải kết
    thúc token năm): ranh giới cuối token giờ cấm CẢ '/' VÀ '-' liền kề,
    NGOẠI TRỪ đúng 1 trường hợp -- '-' được theo sau NGAY bởi 1 năm 4-chữ-số
    KHÁC có ranh giới sạch (cú pháp khoảng thời gian thật, vd "khoảng
    2001-2004") -- đây là ngoại lệ DUY NHẤT được kiểm tra tường minh bằng
    _DATE_RANGE_CLEAN_YEAR_RANGE_TAIL_RE, không suy luận ngầm trong 1 regex
    lồng nhau (dễ sai, đã học từ nhiều vòng review regex trước)."""
    anchored = []
    for m in _DATE_RANGE_CUE_THEN_YEAR_RE.finditer(excerpt):
        y_start, y_end = m.span(1)
        tail = excerpt[y_end:y_end + 1]
        if tail == "-":
            if not _DATE_RANGE_CLEAN_YEAR_RANGE_TAIL_RE.match(excerpt, y_end):
                continue  # '-' ASCII không mở đầu 1 năm khác sạch -- có thể là số hiệu (vd "2001-A"), không phải range
        elif tail and re.match(_DATE_RANGE_IDENTIFIER_BOUNDARY_CLASS, tail):
            continue  # dính liền identifier/mã (chữ/số/underscore/slash/dash Unicode) -- không phải năm độc lập
        anchored.append((y_start, y_end))
    return anchored


def _year_value_entailed_by_excerpt(year: str, excerpt: str) -> bool:
    """Kiểm tra 'YYYY' thật sự được excerpt NÊU LÀ THỜI ĐIỂM (không phải
    substring 4 chữ số ngẫu nhiên trong 1 số khác -- số hiệu bản án, tuổi,
    mã hồ sơ...) -- FIX (Codex review round 2, HIGH #1 vẫn CHƯA đóng ở round
    1): check round 1 chỉ `year in excerpt`, lọt qua "Bản án số 2001, hành
    vi xảy ra không rõ năm." (2001 là số hiệu bản án, không phải năm).

    FIX ROUND 2 (round 3 review): bản round 2 chỉ đòi cue nằm ĐÂU ĐÓ trong
    cửa sổ ±12 ký tự quanh year -- cue thuộc về 1 số KHÁC gần đó vẫn "mượn"
    được nếu nằm cùng cửa sổ (vd "Bản án số 2001, vào năm 2005." -- cue "vào
    năm" thuộc về 2005 vẫn xác nhận nhầm 2001).

    FIX ROUND 3 (round 4 review): bản round 3 sửa bằng "nearest cue token"
    (đo khoảng cách 2 CHIỀU từ cuối cụm cue) vẫn lọt "Năm 2005, Tòa ra bản án
    số 2001, năm đó bị cáo bỏ trốn." -- cụm cue hồi chỉ "năm đó" (KHÔNG có
    số nào theo sau nó) vẫn được tính vì nearest-token tìm NGƯỢC về "2001"
    đứng trước nó trong toàn văn bản, dù "năm đó" ngữ nghĩa hồi chỉ "2005"
    (năm đã nêu trước đó), không mô tả "2001".

    THIẾT KẾ HIỆN TẠI: bỏ hẳn cách "tìm số gần cue nhất theo mọi hướng" --
    CHỈ chấp nhận (a) year được 1 từ cue đứng NGAY TRƯỚC xác nhận trực tiếp
    (`_cue_anchored_years()`, đúng hướng cue->năm, KHÔNG suy ngược), HOẶC
    (b) year liền kề 1 token đã được xác nhận như vậy qua ĐÚNG dấu '-' (cho
    phép cú pháp khoảng, vd "khoảng 2001-2004" -- cue "khoảng" xác nhận
    trực tiếp "2001", "2004" được chấp nhận vì liền kề "2001" qua dấu '-').
    Cue đứng SAU năm (hồi chỉ như "năm đó", "năm này") KHÔNG BAO GIỜ tự xác
    nhận được năm nào -- fail-closed đúng hướng an toàn hơn (bỏ sót còn hơn
    xác nhận nhầm, vì date_range non-None tự nâng dedupe_confidence lên
    "high"). FIX (Codex review round 5, phần còn lại của HIGH #1): nhánh (b)
    trước đây chấp nhận khoảng trắng ĐƠN THUẦN làm "liền kề" (vd "Năm 2005
    2001/QĐ..." -- '2001' bị xác nhận nhầm chỉ vì đứng ngay sau '2005' cách
    1 dấu cách, không có dấu '-' thật) -- giờ đòi phần đệm giữa 2 token,
    sau khi bỏ khoảng trắng 2 đầu, PHẢI CÒN LẠI ít nhất 1 ký tự VÀ toàn bộ
    ký tự còn lại đó đều là dấu '-' (không chấp nhận đệm rỗng/chỉ khoảng
    trắng nữa).

    Đây vẫn là heuristic cơ học, KHÔNG hiểu ngữ nghĩa thật, nên VẪN CÓ THỂ
    lọt qua trường hợp excerpt nói đúng từ khoá thời gian NGAY TRƯỚC năm
    nhưng chỉ LOẠI ngày (điều tra/xét xử/đăng bài) chứ không phải ngày hành
    vi -- đó là giới hạn ĐÃ BIẾT, ghi rõ ở đây thay vì giấu, được giảm nhẹ
    bởi (1) _EXTRACT_CASE_FACTS_PROMPT yêu cầu LLM chỉ trích ngày hành vi,
    (2) date_range chỉ là 1/3 tín hiệu blocking, KHÔNG tự nó quyết định case
    trùng/không trùng."""
    # FIX (Codex review round 2, task #262 -- cùng lớp lỗi áp dụng ngược lại
    # cho nhánh 'YYYY' này): ranh giới trước đây chỉ cấm CHỮ SỐ liền kề
    # (`.isdigit()`), không cấm CHỮ CÁI -- 'A2001B' vẫn bị coi là năm '2001'
    # độc lập dù thực chất là 1 phần của mã định danh chữ-số. Dùng lookaround
    # `\w` (loại cả chữ cái LẪN chữ số/underscore liền kề), cùng kỷ luật với
    # _full_date_value_entailed_by_excerpt().
    anchored = _cue_anchored_years(excerpt)
    for m in re.finditer(rf"(?<!\w){re.escape(year)}(?!\w)", excerpt):
        y_start, y_end = m.start(), m.end()
        if (y_start, y_end) in anchored:
            return True
        for a_start, a_end in anchored:
            gap = excerpt[a_end:y_start] if a_end <= y_start else excerpt[y_end:a_start] if y_end <= a_start else None
            if gap is None:
                continue
            # FIX (Codex review round 6, HIGH #1): gap.strip() từng xoá CẢ
            # newline/tab (không chỉ dấu cách), khiến "Năm 2005\n- 2001/QĐ..."
            # (dấu gạch đầu dòng bullet-list, KHÔNG phải cú pháp khoảng thời
            # gian) vẫn bị coi là "liền kề qua dấu -". Giờ CHỈ chấp nhận đúng
            # dấu cách thường 2 bên dấu '-' -- không newline/tab.
            if re.fullmatch(r" *-+ *", gap):
                return True
    return False


def _full_date_value_entailed_by_excerpt(value: str, excerpt: str) -> bool:
    """Kiểm tra 1 giá trị 'YYYY-MM-DD' thật sự được viết ra trong excerpt --
    KHÔNG chỉ chấp nhận literal ISO ('2011-08-24'), mà CẢ cách viết ngày
    tháng tự nhiên của văn bản tiếng Việt (DD/MM/YYYY hoặc DD-MM-YYYY, có
    hoặc không số 0 đứng đầu, vd '24/8/2011'/'24/08/2011') -- FIX (phát hiện
    qua kiểm thử trực tiếp trên dữ liệu CL thật sau task #261: LLM trích
    ĐÚNG date_range_start=end='2011-08-24' với excerpt "Đêm 24/8/2011, tại
    tiệm vàng..." (case Lê Văn Luyện) -- excerpt grounding thật, nhưng check
    literal-ISO-substring cũ luôn FAIL vì nguồn tiếng Việt không bao giờ
    viết ngày theo định dạng ISO, khiến date_range=None cho HẦU HẾT case có
    ngày thật, làm fix #261 gần như vô nghĩa trên dữ liệu thật). Không cần
    cue thời gian đi kèm (khác nhánh 'YYYY' đơn thuần) vì 1 ngày-tháng-năm
    đầy đủ đã đủ đặc trưng, khó trùng ngẫu nhiên với số khác.

    FIX (Codex review round 1, MEDIUM): bản đầu dùng `cand in excerpt`
    (substring trần) -- '24/8/2011' là substring của '124/8/2011' (vd 1
    phần của mã hồ sơ dài hơn dạng số/số/số), khiến false positive giống
    đúng lớp lỗi token-boundary mà nhánh 'YYYY' (task #261) đã chủ động
    chặn. FIX round 2: ranh giới chỉ cấm CHỮ SỐ liền kề (`(?<!\d)`) vẫn lọt
    'A24/8/2011B'/'A2011-08-24B' (chữ CÁI liền kề không bị chặn) -- đổi sang
    `\w` (loại cả chữ cái LẪN chữ số/underscore liền kề).

    FIX (Codex review round 3, MEDIUM): '/' và '-' không nằm trong `\w`, nên
    ranh giới round 2 vẫn lọt ngày nằm giữa 1 mã định danh dùng CHÍNH 2 dấu
    này làm phân cách, vd "A-24/8/2011-B" hay "X/2011-08-24/Y" (thực tế:
    số hiệu quyết định pháp lý Việt Nam thường viết dạng "<số>/<năm>/QĐ-
    <toà>", dùng đúng '/' và '-'). Ngày ĐẦY ĐỦ (khác nhánh 'YYYY' đơn thuần)
    KHÔNG có cú pháp "khoảng liền kề" nào cần giữ ngoại lệ -- cấm thẳng CẢ
    '/' LẪN '-' liền kề 2 đầu, không cần ngoại lệ như nhánh 'YYYY'.

    FIX (Codex review round 4, MEDIUM): '-' ASCII không phải dấu gạch nối
    DUY NHẤT -- text copy từ Word/PDF thường chứa dash Unicode trông giống
    hệt (en dash '–', non-breaking hyphen '‑'...) nhưng KHÔNG khớp `[\\w/-]`,
    vd "A–24/8/2011–B" vẫn lọt. Dùng chung `_DATE_RANGE_IDENTIFIER_BOUNDARY_
    CLASS` (đã liệt kê các dash Unicode thường gặp) với nhánh 'YYYY'."""
    year, month, day = value.split("-")
    day_variants = {day, str(int(day))}
    month_variants = {month, str(int(month))}
    candidates = {value}
    for d in day_variants:
        for m in month_variants:
            for sep in ("/", "-"):
                candidates.add(f"{d}{sep}{m}{sep}{year}")
    boundary = _DATE_RANGE_IDENTIFIER_BOUNDARY_CLASS
    return any(re.search(rf"(?<!{boundary}){re.escape(cand)}(?!{boundary})", excerpt) for cand in candidates)


def _extract_date_range(ef: dict, case_text: str) -> tuple | None:
    """Đọc date_range_start/end từ event_fingerprint do LLM trích -- chỉ
    tin khi: (a) CẢ HAI giá trị đúng lịch thật ('YYYY' hoặc 'YYYY-MM-DD', xem
    _valid_date_range_value()), (b) CÙNG độ chính xác (FIX Codex review
    round 2, MEDIUM #5: swap bằng string thô trên 2 giá trị KHÁC độ chính
    xác, vd start='2001-12-31'/end='2001', cho kết quả ngữ nghĩa mơ hồ --
    'YYYY' nào đại diện ngày nào sau khi mở bound? Không cố suy luận, fail-
    closed về None thẳng khi mixed precision), (c) date_range_excerpt thật
    sự grounding được trong case_text (cùng kỷ luật disposition/life_status/
    finality_state ở verify_sources()), VÀ (d) với 'YYYY-MM-DD': TOÀN BỘ giá
    trị (không chỉ năm) xuất hiện nguyên văn trong excerpt; với 'YYYY':
    _year_value_entailed_by_excerpt() (ranh giới token + từ khoá thời gian
    sát cạnh, xem docstring hàm đó cho giới hạn đã biết) -- FIX (Codex review
    round 1+2, HIGH #1): grounding-trong-case_text một mình không xác nhận
    excerpt chứng minh ĐÚNG start/end; date_range non-None tự nâng dedupe_
    confidence lên "high" nên fabrication ở đây nguy hiểm hơn hầu hết field
    khác. Bất kỳ điều kiện nào không đạt -> None (fail-closed, KHÔNG suy
    đoán)."""
    start, end = ef.get("date_range_start"), ef.get("date_range_end")
    excerpt = ef.get("date_range_excerpt")
    if not isinstance(start, str) or not isinstance(end, str) or not start.strip() or not end.strip():
        return None
    start, end = start.strip(), end.strip()
    if not _valid_date_range_value(start) or not _valid_date_range_value(end):
        return None
    if len(start) != len(end):  # mixed precision ('YYYY' vs 'YYYY-MM-DD') -- fail-closed, xem docstring
        return None
    if not _excerpt_grounded(excerpt, case_text):
        return None
    if _DATE_RANGE_FULL_RE.match(start):
        if not _full_date_value_entailed_by_excerpt(start, excerpt) or not _full_date_value_entailed_by_excerpt(end, excerpt):
            return None
    else:
        if not _year_value_entailed_by_excerpt(start, excerpt) or not _year_value_entailed_by_excerpt(end, excerpt):
            return None
    if end < start:
        start, end = end, start
    return (start, end)


def extract_case_facts(case_text: str) -> dict:
    """FIX (Codex review Stage 1, Medium #9): trước đây chỉ kiểm tra key có
    mặt, không kiểm tra KIỂU -- 1 response hợp lệ cú pháp JSON nhưng sai
    kiểu (named_individuals là dict thay vì list, event_fingerprint là
    string...) sẽ crash sâu trong verify_sources() với TypeError mơ hồ thay
    vì 1 ContentSeoError rõ ràng ngay tại điểm trích xuất."""
    prompt = _EXTRACT_CASE_FACTS_PROMPT.format(case_text=case_text)
    result = _extract_json(_run_agy(prompt))
    if not isinstance(result, dict):
        raise ContentSeoError(f"agy trả về không phải JSON object cấp cao nhất: {result!r}"[:500])
    for key in ("named_individuals", "core_facts"):
        if key not in result or not isinstance(result[key], list):
            raise ContentSeoError(f"agy trích case facts thiếu key '{key}' hoặc không phải list: {result!r}"[:500])
        for item in result[key]:
            if not isinstance(item, dict):
                raise ContentSeoError(f"agy trích '{key}' chứa phần tử không phải object: {item!r}"[:500])
    if "event_fingerprint" not in result or not isinstance(result["event_fingerprint"], dict):
        raise ContentSeoError(f"agy trích case facts thiếu key 'event_fingerprint' hoặc không phải object: {result!r}"[:500])
    for person in result["named_individuals"]:
        if not isinstance(person.get("canonical_name"), str) or not person["canonical_name"].strip():
            raise ContentSeoError(f"named_individuals có phần tử thiếu 'canonical_name' hợp lệ: {person!r}"[:500])
    # FIX (Codex review Stage 1 round 2, Finding 9 phần còn lại): fact_id/
    # statement/fact_type trước đây không ép kiểu string -- 1 giá trị số/
    # None/list ở đây sẽ lan xuống CoreFact rồi làm hỏng .strip()/so sánh
    # chuỗi ở nơi khác (score_c2/c3, audit log) với lỗi mơ hồ ở xa điểm gốc.
    for cf in result["core_facts"]:
        for key in ("fact_type",):
            if key in cf and not isinstance(cf[key], str):
                raise ContentSeoError(f"core_facts có phần tử '{key}' không phải string: {cf!r}"[:500])
        if "statement" in cf and not isinstance(cf["statement"], str):
            raise ContentSeoError(f"core_facts có phần tử 'statement' không phải string: {cf!r}"[:500])
        if "fact_id" in cf and cf["fact_id"] is not None and not isinstance(cf["fact_id"], str):
            raise ContentSeoError(f"core_facts có phần tử 'fact_id' không phải string/None: {cf!r}"[:500])
        if "excerpt" in cf and cf["excerpt"] is not None and not isinstance(cf["excerpt"], str):
            raise ContentSeoError(f"core_facts có phần tử 'excerpt' không phải string/None: {cf!r}"[:500])
    return result


def verify_sources(stub: dict, tiers_config: dict) -> CandidateCase:
    """§1.4: điền named_individuals/core_facts/event_fingerprint/sources từ
    case_text (đã có sẵn, không fetch URL trực tiếp -- xem docstring đầu
    file) + reference_urls (dùng để dựng SourceRecord với publisher_tier
    thật, nhưng excerpt vẫn lấy/grounding-check từ case_text vì đây là văn
    bản đã tổng hợp, không phải từng trang gốc). Mọi LegalStatusRecord ở
    đây có cross_verified=False -- CHƯA qua bước 2-pass độc lập (Stage 2)."""
    case_text = stub["case_text"]
    try:
        extracted = extract_case_facts(case_text)
    except ContentSeoError as exc:
        # FIX (Codex review Stage 1 round 4, Medium): áp dụng nhất quán quy
        # tắc "không đưa nội dung exception vào message" -- ContentSeoError
        # có thể mang theo response/payload động (extract_case_facts() tự
        # nhúng result!r vào message của nó), bản trước vẫn lộ nguyên văn.
        raise CLRiskGateError(f"Trích facts thất bại cho case '{stub['working_title']}' (loại lỗi: {type(exc).__name__}) -- DỪNG (fail-closed), không đưa candidate thiếu dữ liệu vào chấm điểm.") from exc
    except Exception as exc:  # noqa: BLE001 -- FIX (Codex review Stage 1 round 2, Finding 9): lỗi runtime khác ContentSeoError (vd từ _run_agy/_extract_json/subprocess) trước đây thoát thẳng khỏi verify_sources(), có thể crash cả batch đang xử lý nhiều candidate khác. Fail-closed rõ ràng cho ĐÚNG 1 candidate này.
        # FIX (Codex review Stage 1 round 3, Medium mới #1 áp dụng luôn ở
        # đây): CHỈ nêu tên loại exception, không đưa str(exc) (có thể chứa
        # path/token/subprocess output) vào message -- exception này sẽ
        # tiếp tục nổi lên caller, có thể tới log/report.
        raise CLRiskGateError(f"Trích facts thất bại cho case '{stub['working_title']}' (loại lỗi: {type(exc).__name__}) -- DỪNG (fail-closed).") from exc

    # Sources: 1 SourceRecord/URL tham khảo, publisher_tier tra allowlist thật.
    sources = []
    for i, url in enumerate(stub["reference_urls"]):
        domain = _extract_domain(url)
        tier = classify_publisher_tier(url, tiers_config)
        source_id = f"src_{hashlib.sha256(url.strip().encode('utf-8')).hexdigest()[:8]}"
        sources.append(SourceRecord(
            source_id=source_id, url=url, publisher=domain, publisher_tier=tier,
            source_lineage_id=source_id,  # v1: mỗi URL riêng 1 lineage cho tới khi Stage 2 chạy lineage-grouping LLM pass thật (§1.4.5)
            origin_claim="unstated",  # v1: chưa chạy LLM origin-claim extraction -- fail-closed mặc định
            independence_verified=False,  # bắt buộc False cho tới khi origin_claim được xác nhận rõ ràng (§1.4.5)
            retrieved_at=_now_iso(), page_content_hash=_hash_text(case_text), excerpt_hash="",
            excerpt_context_window="", excerpt="", excerpt_entailment_note="",
        ))

    named_individuals = []
    for person in extracted["named_individuals"]:
        disposition_excerpt = person.get("disposition_excerpt", "")
        life_status_excerpt = person.get("life_status_excerpt", "")
        finality_excerpt = person.get("finality_excerpt", "")
        try:
            disposition = DispositionStatus(person.get("disposition", "unknown"))
        except ValueError:
            disposition = DispositionStatus.UNKNOWN
        try:
            life_status = LifeStatus(person.get("life_status", "unknown"))
        except ValueError:
            life_status = LifeStatus.UNKNOWN
        try:
            finality_state = FinalityState(person.get("finality_state", "unknown"))
        except ValueError:
            finality_state = FinalityState.UNKNOWN

        # Grounding: excerpt phải THẬT sự là substring của case_text, nếu
        # không -- fail-closed về UNKNOWN cho field đó (không tin field
        # không grounding được, đúng pattern extract_facts()).
        if disposition != DispositionStatus.UNKNOWN and not _excerpt_grounded(disposition_excerpt, case_text):
            disposition = DispositionStatus.UNKNOWN
            disposition_excerpt = ""
        if life_status != LifeStatus.UNKNOWN and not _excerpt_grounded(life_status_excerpt, case_text):
            life_status = LifeStatus.UNKNOWN
            life_status_excerpt = ""
        if finality_state != FinalityState.UNKNOWN and not _excerpt_grounded(finality_excerpt, case_text):
            finality_state = FinalityState.UNKNOWN
            finality_excerpt = ""

        internal_source_id = f"local_{stub['case_id']}"
        legal_status = LegalStatusRecord(
            disposition=disposition,
            disposition_evidence=[FieldEvidence(internal_source_id, disposition_excerpt)] if disposition_excerpt else [],
            life_status=life_status,
            life_status_evidence=[FieldEvidence(internal_source_id, life_status_excerpt)] if life_status_excerpt else [],
            finality_state=finality_state,
            finality_evidence=[FieldEvidence(internal_source_id, finality_excerpt)] if finality_excerpt else [],
            cross_verified=False,  # Stage 2
        )
        role = person.get("role", "")
        if role not in ("victim", "official_capacity", "convicted_perpetrator", "acquitted", "accused_unconvicted", "named_relative_or_associate"):
            role = "accused_unconvicted"  # fail-closed: vai trò không nhận diện được -> vai trò cần soi kỹ nhất
        identity_confidence = person.get("identity_confidence") if person.get("identity_confidence") in ("high", "low") else "low"
        named_individuals.append(NamedIndividual(
            canonical_name=person["canonical_name"], identity_confidence=identity_confidence,
            role=role, legal_status=legal_status,
        ))

    def _as_str_list(value) -> list:
        return [x for x in value if isinstance(x, str)] if isinstance(value, list) else []

    ef = extracted["event_fingerprint"]
    event_fingerprint = EventFingerprint(
        normalized_core_act=ef.get("normalized_core_act", "") if isinstance(ef.get("normalized_core_act"), str) else "",
        date_range=_extract_date_range(ef, case_text),
        locations=_as_str_list(ef.get("locations")), organizations=_as_str_list(ef.get("organizations")),
        all_named_individuals=[p["canonical_name"] for p in extracted["named_individuals"]],
        decision_identifiers=_as_str_list(ef.get("decision_identifiers")),
    )

    core_facts = []
    for i, cf in enumerate(extracted["core_facts"]):
        excerpt = cf.get("excerpt", "")
        if not _excerpt_grounded(excerpt, case_text):
            continue  # excerpt bịa/không grounding được -- loại bỏ fact này hoàn toàn, không giữ lại "statement" không có bằng chứng thật
        fact_id = cf.get("fact_id") or f"F{i + 1}"
        # FIX (Codex review Stage 1, Medium #7): bản trước gán
        # corroborating_source_ids=["local_<case_id>"] -- 1 id KHÔNG khớp
        # bất kỳ SourceRecord.source_id thật nào trong `sources` ở trên
        # (những cái đó đều "src_<hash url>"). Hệ quả: C1/C3 tưởng đã
        # implement đầy đủ nhưng THỰC RA luôn FAIL vì lookup ID không bao
        # giờ khớp -- fail-closed đúng nhưng VÌ SAI LÝ DO (bug ID-namespace,
        # không phải đánh giá sourcing thật). Stage 1 KHÔNG có khả năng xác
        # định excerpt trong case_text THỰC SỰ trích từ URL nào trong số
        # reference_urls (extraction prompt không hỏi câu đó) -- nên trung
        # thực để corroborating_source_ids RỖNG (không tự nhận vơ 1 nguồn
        # không xác định được) thay vì tạo ID giả. C1/C2/C3 vì vậy fail-
        # closed đúng bản chất: "chưa có per-fact source attribution thật",
        # không phải 1 bug ngẫu nhiên trùng kết quả.
        core_facts.append(CoreFact(
            fact_id=fact_id, statement=cf.get("statement", ""), fact_type=cf.get("fact_type", ""),
            corroborating_source_ids=[], corroborating_lineage_ids=[],
            corroborating_verified_independent_lineage_ids=[],  # v1: 0 cho tới khi independence_verified thật (Stage 2)
        ))

    return CandidateCase(
        case_id=stub["case_id"], case_key=stub["case_key"], working_title=stub["working_title"],
        discovered_at=_now_iso(), discovery_source_file=stub["discovery_source_file"],
        named_individuals=named_individuals, sources=sources, core_facts=core_facts,
        event_fingerprint=event_fingerprint,
    )


# =============================================================================
# §1.5 -- C1, C2, C3, C6, C7 (mechanical). C4/C5 -- Stage 2 (đòi hỏi
# risk_review_draft đã qua LLM adversarial review + HISTORICAL_CONSENSUS
# affirmative protocol dài, chưa xây ở Stage 1).
# =============================================================================

def score_c1(candidate: CandidateCase) -> CriterionResult:
    ok = any(s.publisher_tier in (PublisherTier.REPUTABLE_PRESS, PublisherTier.PUBLIC_RECORD) for s in candidate.sources)
    return CriterionResult("C1", ok, f"{sum(1 for s in candidate.sources if s.publisher_tier in (PublisherTier.REPUTABLE_PRESS, PublisherTier.PUBLIC_RECORD))} nguồn reputable_press/public_record trong {len(candidate.sources)} nguồn.", "allowlist_lookup")


def _verified_independent_lineages_for_fact(candidate: CandidateCase, cf: CoreFact) -> set:
    """FIX (Codex review Stage 1, Medium #6): score_c2() trước đây tin
    THẲNG cf.corroborating_verified_independent_lineage_ids mà không đối
    chiếu lại candidate.sources -- nếu field đó bị dựng sai/lỗi ở bất kỳ
    caller nào (dữ liệu cũ, bug Stage 2 tương lai, object test không nhất
    quán), C2 PASS giả mà không ai phát hiện. Tính LẠI từ dữ liệu nguồn
    thật: 1 lineage chỉ được tính khi (a) claimed trong
    corroborating_verified_independent_lineage_ids, (b) có source THẬT
    trong candidate.sources thuộc lineage đó, (c) source đó
    independence_verified=True, VÀ (d) source_id của nó thật sự có trong
    cf.corroborating_source_ids (nguồn đó thật sự được gán trích dẫn cho
    ĐÚNG fact này, không phải trích dẫn cho fact khác rồi mượn danh)."""
    claimed = set(cf.corroborating_verified_independent_lineage_ids)
    if not claimed:
        return set()
    real = set()
    for sid in cf.corroborating_source_ids:
        source = next((s for s in candidate.sources if s.source_id == sid), None)
        if source is not None and source.independence_verified and source.source_lineage_id in claimed:
            real.add(source.source_lineage_id)
    return real


def score_c2(candidate: CandidateCase) -> CriterionResult:
    if not candidate.core_facts:
        return CriterionResult("C2", False, "Không có core_facts nào được trích xuất.", "mechanical")
    failing = []
    for cf in candidate.core_facts:
        verified_lineages = _verified_independent_lineages_for_fact(candidate, cf)
        social_only = all(
            next((s.publisher_tier for s in candidate.sources if s.source_id == sid), PublisherTier.UNKNOWN) == PublisherTier.SOCIAL_MEDIA
            for sid in cf.corroborating_source_ids
        ) if cf.corroborating_source_ids else True
        if len(verified_lineages) < 2 or social_only:
            failing.append(cf.fact_id)
    ok = not failing
    return CriterionResult("C2", ok, f"Fact thiếu >=2 lineage độc lập đã xác minh (đối chiếu thật với candidate.sources): {failing}" if failing else "Mọi fact có >=2 lineage độc lập đã xác minh.", "mechanical")


def score_c3(candidate: CandidateCase) -> CriterionResult:
    if not candidate.core_facts:
        return CriterionResult("C3", False, "Không có core_facts nào được trích xuất.", "mechanical")
    failing = []
    for cf in candidate.core_facts:
        tiers = [next((s.publisher_tier for s in candidate.sources if s.source_id == sid), PublisherTier.UNKNOWN) for sid in cf.corroborating_source_ids]
        if not any(t in (PublisherTier.REPUTABLE_PRESS, PublisherTier.PUBLIC_RECORD) for t in tiers):
            failing.append(cf.fact_id)
    ok = not failing
    return CriterionResult("C3", ok, f"Fact KHÔNG có nguồn reputable_press/public_record nào: {failing}" if failing else "Mọi fact có >=1 nguồn reputable_press/public_record.", "mechanical")


def identifier_ok(legal_status: LegalStatusRecord) -> bool:
    """§1.4.1 bước 8 -- 1 hàm DUY NHẤT, C5/C6 đều gọi qua đây, không tự
    lặp lại điều kiện (đúng fix cho round-5 Medium M1's 3-way inconsistent
    restatement)."""
    if legal_status.decision_identifier_consistent == DecisionIdentifierConsistency.INCONSISTENT:
        return False
    if legal_status.decision_identifier_consistent == DecisionIdentifierConsistency.CONSISTENT:
        return True
    return legal_status.evidentiary_path == "allowlisted_public_record"


def _c6_pass_for_individual(person: NamedIndividual) -> tuple[bool, str]:
    """FIX (Codex review Stage 1, Blocker #1): `role` ở Stage 1 đến từ MỘT
    lần trích xuất agy duy nhất (verify_sources()), KHÔNG grounding, KHÔNG
    cross-verify -- role_verification.role_cross_verified LUÔN False cho
    tới khi Stage 2 chạy 2-pass độc lập (§1.4.1's protocol áp dụng y hệt
    cho role, không chỉ legal_status). Nếu bảng miễn trừ (victim/
    official_capacity/acquitted) tin thẳng role chưa cross-verified, 1 người
    THẬT SỰ là accused_unconvicted còn sống chỉ cần LLM gán NHẦM
    thành 'victim'/'acquitted'/'official_capacity' là C6 PASS oan -- đúng
    lỗ hổng Codex tìm thấy. Do đó: KHÔNG role nào được áp dụng nhánh miễn
    trừ/PASS nào ở Stage 1 -- mọi named_individual FAIL C6 cho tới khi
    role_cross_verified=True (Stage 2). Đây là hệ quả TRỰC TIẾP, không phải
    tình cờ: C6 không thể PASS thật cho tới khi cả role LẪN legal_status
    đều qua xác minh độc lập."""
    if not person.role_verification.role_cross_verified:
        return False, f"{person.canonical_name}: role='{person.role}' chưa cross-verified (Stage 2 chưa chạy) -- KHÔNG áp dụng bất kỳ nhánh miễn trừ/PASS nào, fail-closed."

    role = person.role
    ls = person.legal_status
    if role == "victim":
        return True, "victim -- exempt (role đã cross-verified)."
    if role == "official_capacity":
        return True, "official_capacity -- exempt (role đã cross-verified)."
    if role == "acquitted":
        return True, "acquitted -- không lặp lại buộc tội, C6 không áp dụng (role đã cross-verified; khung hình ngụ ý tội xử lý ở C4/Claim Gate, không phải C6)."
    if role == "convicted_perpetrator":
        if (ls.disposition == DispositionStatus.CONVICTED and ls.finality_state == FinalityState.FINAL
                and ls.cross_verified and identifier_ok(ls)):
            return True, f"{person.canonical_name}: convicted_perpetrator, CONVICTED+FINAL, cross_verified, identifier_ok."
        return False, f"{person.canonical_name}: convicted_perpetrator nhưng chưa đủ điều kiện (disposition={ls.disposition.value}, finality={ls.finality_state.value}, cross_verified={ls.cross_verified}, identifier_ok={identifier_ok(ls)})."
    if role == "accused_unconvicted":
        # FIX (Blocker #2): nhánh deceased trước đây chỉ đọc life_status,
        # KHÔNG đòi legal_status.cross_verified -- 1 excerpt grounding yếu
        # (chỉ cần khớp substring, không chứng minh entailment thật, xem
        # High #5) có thể khiến 1 người CÒN SỐNG bị gán nhầm deceased rồi
        # PASS oan. Giờ bắt buộc cross_verified=True cho life_status trước
        # khi tin deceased.
        if ls.life_status == LifeStatus.DECEASED and ls.cross_verified:
            return True, f"{person.canonical_name}: accused_unconvicted nhưng đã xác nhận deceased (cross_verified) -- không còn rủi ro danh dự sống."
        return False, f"{person.canonical_name}: accused_unconvicted, life_status={ls.life_status.value} cross_verified={ls.cross_verified} -- LUÔN FAIL trừ khi deceased ĐÃ cross-verified, không có ngoại lệ khác (presumption of innocence)."
    if role == "named_relative_or_associate":
        return False, f"{person.canonical_name}: named_relative_or_associate phải tự clear bảng này với vai trò thật của họ hoặc được ẩn danh trong script -- Stage 2/§1.6 xử lý tiếp, v1 fail-closed."
    return False, f"{person.canonical_name}: role '{role}' không nhận diện được -- fail-closed."


def score_c6(candidate: CandidateCase) -> CriterionResult:
    """§1.5 bảng C6 -- bảng đóng, không có 'etc.'. Fail-closed thêm:
    identity_confidence=='low' + life_status!=DECEASED + có ngụ ý sai phạm
    => FAIL bất kể role (bảo vệ nhận nhầm người). LƯU Ý (sau fix Blocker
    #1/#2): ở Stage 1, C6 KHÔNG THỂ PASS cho bất kỳ candidate nào (role
    luôn role_cross_verified=False) -- đây là hành vi ĐÚNG và CỐ Ý, không
    phải bug, cho tới khi Stage 2's dual-pass role verification chạy thật."""
    if not candidate.named_individuals:
        return CriterionResult("C6", False, "Không có named_individuals nào được trích xuất.", "table_lookup")
    reasons = []
    ok = True
    for person in candidate.named_individuals:
        if person.identity_confidence == "low" and person.legal_status.life_status != LifeStatus.DECEASED and person.role not in ("victim", "official_capacity"):
            ok = False
            reasons.append(f"{person.canonical_name}: identity_confidence=low + chưa xác nhận deceased + vai trò '{person.role}' ngụ ý sai phạm -- FAIL (bảo vệ nhận nhầm người).")
            continue
        passed, reason = _c6_pass_for_individual(person)
        reasons.append(reason)
        if not passed:
            ok = False
    return CriterionResult("C6", ok, " | ".join(reasons), "table_lookup")


def score_c7(candidate: CandidateCase) -> CriterionResult:
    """§1.5 C7 -- yêu cầu risk_review_draft đã tồn tại và qua LLM adversarial
    pass xác nhận mọi claim đều attributed. risk_review_draft CHƯA được
    sinh ở Stage 1 (đó là bước cuối §1.4 mà Stage 1 chưa làm) -- v1 fail-
    closed rõ ràng thay vì giả định PASS."""
    if not candidate.risk_review_draft:
        return CriterionResult("C7", False, "risk_review_draft chưa tồn tại (Stage 2 chưa chạy) -- fail-closed, không thể xác nhận factual attribution.", "not_yet_implemented")
    raise NotImplementedError("score_c7(): LLM adversarial attribution-review pass là Stage 2, xem GATE2_DESIGN.md §1.5 C7 + task #240.")


def score_c4(candidate: CandidateCase) -> CriterionResult:
    if not candidate.risk_review_draft:
        return CriterionResult("C4", False, "risk_review_draft chưa tồn tại (Stage 2 chưa chạy) -- fail-closed.", "not_yet_implemented")
    raise NotImplementedError("score_c4(): LLM adversarial unsupported-assertion review là Stage 2, xem GATE2_DESIGN.md §1.5 C4 + task #240.")


def score_c5(candidate: CandidateCase) -> CriterionResult:
    raise NotImplementedError("score_c5(): protocol ADJUDICATED_*/HISTORICAL_CONSENSUS đầy đủ là Stage 2, xem GATE2_DESIGN.md §1.5 C5 + task #240.")


# =============================================================================
# §1.8 -- Risk tiering
# =============================================================================

MEDIUM_ELIGIBLE_CRITERIA = {"C1", "C2", "C3", "C4", "C7"}
STRUCTURAL_CRITERIA = {"C5", "C6"}


def tier_for(result: RiskScoreResult) -> str:
    if not result.failing_criteria:
        return "LOW"
    if any(c in STRUCTURAL_CRITERIA for c in result.failing_criteria):
        return "HIGH"
    if all(c in MEDIUM_ELIGIBLE_CRITERIA for c in result.failing_criteria):
        return "MEDIUM"
    return "HIGH"  # fail-closed: bất kỳ criterion nào không nhận diện được cũng đẩy lên HIGH, không mặc định MEDIUM


def score_available_criteria(candidate: CandidateCase) -> list:
    """Chỉ chạy các tiêu chí ĐÃ implement ở Stage 1 (C1/C2/C3/C6) -- C4/C5/C7
    raise NotImplementedError nếu gọi trực tiếp, nên KHÔNG gọi ở đây. Hàm
    này phục vụ test/inspection Stage 1, KHÔNG phải run_cl_case_gate() đầy
    đủ (đó cần toàn bộ 7 tiêu chí, tức cần Stage 2)."""
    return [score_c1(candidate), score_c2(candidate), score_c3(candidate), score_c6(candidate)]


# =============================================================================
# §1.11 -- Dedupe (C8)
# =============================================================================

def _normalize_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", normalized.lower()).strip()


def _is_self_or_alias_of(entry: CaseLedgerEntry, candidate_case_id: str) -> bool:
    """FIX (Codex review Stage 1 round 4, High mới): entry.case_id ==
    candidate_case_id (đúng self) không phải trường hợp duy nhất cần loại.
    Kịch bản thật: case B từng bị merge làm alias của case A
    (status=MERGED_INTO, merged_into_case_id="A"). Sau này A được xử lý
    lại (vd re-verify) -- B vẫn còn trong ledger và VẪN chia sẻ fingerprint
    với A (đó chính là lý do B từng được merge vào A). Nếu không loại B ở
    đây, stage1_blocking() sẽ đưa candidate A đi adjudicate với B, LLM hợp
    lý trả SAME_EVENT, và A (case CHÍNH DANH) bị đánh nhầm là "duplicate
    của chính alias của nó" -- ngược hoàn toàn logic merge. Đây là single-
    hop resolution (không theo đuổi merge chain nhiều bước) -- đủ cho Stage
    1 vì §1.10's merge logic hiện tại cũng chỉ tạo chain 1 bước (case sau
    trỏ thẳng về case TRƯỚC, không merge lồng nhau); resolve chain nhiều
    hop đầy đủ là việc của Stage 3 khi merge logic thật được xây."""
    return entry.case_id == candidate_case_id or entry.merged_into_case_id == candidate_case_id


def stage1_blocking(candidate: CandidateCase, ledger: CaseLedger) -> list[CaseLedgerEntry]:
    """§1.11 stage 1 -- collision nếu (a) decision_identifiers trùng CHÍNH
    XÁC, (b) tên trong all_named_individuals trùng (sau chuẩn hoá), hoặc (c)
    >=2/3 của {date_range, location, organization} trùng. Fail-closed
    fallback: candidate không có named_individuals hoặc toàn identity_confidence=low
    => LUÔN so với TOÀN BỘ ledger."""
    ef = candidate.event_fingerprint
    all_entries = ledger.all_entries()
    low_signal = not candidate.named_individuals or all(p.identity_confidence == "low" for p in candidate.named_individuals)
    if low_signal or ef is None:
        # FIX (Codex review Stage 1 round 3, High mới): bản trước trả
        # THẲNG all_entries -- vì discover_candidates() đã ghi SURFACED cho
        # CHÍNH candidate này TRƯỚC KHI verify (§1.3), ledger CÓ THỂ đã
        # chứa entry của chính candidate.case_id. Nếu không lọc, dedupe sẽ
        # đưa candidate đi adjudicate với CHÍNH NÓ -- LLM gần như chắc chắn
        # trả SAME_EVENT, khiến candidate bị đánh duplicate oan ngay từ
        # collision đầu tiên. Nhánh bình thường (dưới đây) đã lọc đúng
        # (entry.case_id == candidate.case_id), fallback phải lọc y hệt.
        return [entry for entry in all_entries if not _is_self_or_alias_of(entry, candidate.case_id)]

    cand_names = {_normalize_name(n) for n in ef.all_named_individuals}
    cand_ids = set(ef.decision_identifiers)
    collisions = []
    for entry in all_entries:
        if _is_self_or_alias_of(entry, candidate.case_id) or entry.fingerprint is None:
            continue
        efp = entry.fingerprint
        if cand_ids and set(efp.decision_identifiers) & cand_ids:
            collisions.append(entry)
            continue
        entry_names = {_normalize_name(n) for n in efp.all_named_individuals}
        if cand_names & entry_names:
            collisions.append(entry)
            continue
        overlap_count = 0
        if ef.date_range and efp.date_range:
            # So sánh qua _date_range_bound() (mở rộng 'YYYY' về mốc AN
            # TOÀN HƠN theo hướng cần), KHÔNG so string thô -- xem docstring
            # _date_range_bound() cho lỗi cụ thể đã sửa (Codex review round 1
            # HIGH #4: "2001" < "2001-06-15" khiến năm và ngày CÙNG năm bị
            # tính sai là không overlap).
            ef_lo, ef_hi = _date_range_bound(ef.date_range[0], latest=False), _date_range_bound(ef.date_range[1], latest=True)
            efp_lo, efp_hi = _date_range_bound(efp.date_range[0], latest=False), _date_range_bound(efp.date_range[1], latest=True)
            if not (ef_hi < efp_lo or efp_hi < ef_lo):
                overlap_count += 1
        if set(ef.locations) & set(efp.locations):
            overlap_count += 1
        if set(ef.organizations) & set(efp.organizations):
            overlap_count += 1
        if overlap_count >= 2:
            collisions.append(entry)
    return collisions


_DEDUPE_ADJUDICATION_PROMPT = """So sánh VỤ ÁN A và VỤ ÁN B. Chọn CHÍNH XÁC 1 trong 4 nhãn:
SAME_EVENT -- mô tả CÙNG 1 sự kiện/vụ án có thật, dù được kể khác hẳn hoặc xoay quanh người khác (vd 1 hồ sơ xoay quanh đồng phạm/nạn nhân/điều tra viên CỦA CHÍNH sự kiện đó vẫn là SAME_EVENT).
RELATED_BUT_DISTINCT -- có chung người/tổ chức/địa điểm với VỤ ÁN A nhưng mô tả 1 hành vi/vụ việc/tố tụng KHÁC (vd 2 vụ án riêng biệt của cùng 1 nhóm tội phạm; cùng 1 người liên quan tới 2 vụ án khác nhau).
DIFFERENT_EVENT -- không có liên hệ đáng kể ngoài trùng hợp.
UNCLEAR -- thật sự không đủ thông tin để xác định.

=== VỤ ÁN A ===
{case_a}

=== VỤ ÁN B ===
{case_b}

Trả về CHỈ 1 JSON object:
{{"verdict": "SAME_EVENT|RELATED_BUT_DISTINCT|DIFFERENT_EVENT|UNCLEAR", "reason": "1 câu ngắn gọn"}}"""


def _candidate_summary_for_dedupe(ef: EventFingerprint | None, title: str, names: list) -> str:
    if ef is None:
        return f"Tiêu đề: {title}\nNgười liên quan: {', '.join(names)}"
    return (f"Tiêu đề: {title}\nHành vi: {ef.normalized_core_act}\nNgười liên quan: {', '.join(ef.all_named_individuals)}\n"
            f"Địa điểm: {', '.join(ef.locations)}\nTổ chức: {', '.join(ef.organizations)}")


def stage2_adjudicate(candidate: CandidateCase, entry: CaseLedgerEntry) -> tuple[str, str]:
    """FIX (Codex review Stage 1, High #4): trước đây chỉ bắt
    ContentSeoError -- 1 lỗi bất ngờ khác (TypeError từ response dạng
    list/None, OSError từ subprocess, v.v.) sẽ crash NGUYÊN CẢ BATCH đang
    xử lý nhiều candidate khác, không chỉ riêng candidate này. Bắt rộng
    Exception + validate result THẬT SỰ là dict trước khi .get() -- mọi lỗi
    không lường trước đều fail-closed về UNCLEAR cho ĐÚNG 1 candidate này,
    không làm crash tiến trình."""
    case_a = _candidate_summary_for_dedupe(candidate.event_fingerprint, candidate.working_title, candidate.event_fingerprint.all_named_individuals if candidate.event_fingerprint else [])
    case_b = _candidate_summary_for_dedupe(entry.fingerprint, ", ".join(entry.title_keywords), entry.canonical_names)
    prompt = _DEDUPE_ADJUDICATION_PROMPT.format(case_a=case_a, case_b=case_b)
    try:
        result = _extract_json(_run_codex(prompt))
    except Exception as exc:  # noqa: BLE001 -- cố ý rộng, xem docstring
        # FIX (Codex review Stage 1 round 3, Medium mới #1 -- cắt ngắn
        # KHÔNG PHẢI redact, round 2's fix vẫn để lọt nội dung nhạy cảm
        # trong 200 ký tự đầu): evidence này rồi sẽ được ghi vào audit
        # log/ledger (Stage 3) -- KHÔNG đưa str(exc) vào evidence nữa dưới
        # BẤT KỲ hình thức nào (kể cả cắt ngắn), chỉ giữ TÊN loại exception
        # (an toàn, không mang nội dung động). Chi tiết đầy đủ (path/token/
        # subprocess output) chỉ nên đi vào log nội bộ có kiểm soát quyền
        # truy cập riêng -- việc đó là của caller (Stage 3), không phải
        # hàm này tự ghi log.
        return "UNCLEAR", f"Lỗi adjudication (loại lỗi: {type(exc).__name__}) -- fail-closed về UNCLEAR."
    if not isinstance(result, dict):
        return "UNCLEAR", f"Response adjudication không phải JSON object (kiểu: {type(result).__name__}) -- fail-closed về UNCLEAR."
    verdict = result.get("verdict", "")
    if verdict not in ("SAME_EVENT", "RELATED_BUT_DISTINCT", "DIFFERENT_EVENT", "UNCLEAR"):
        # verdict là chuỗi LLM tự sinh, không phải nội dung hệ thống nhạy
        # cảm như exception -- vẫn cắt ngắn phòng hờ (chống 1 response bất
        # thường quá dài/chứa payload lạ lọt vào evidence).
        return "UNCLEAR", f"Verdict không hợp lệ từ LLM (cắt ngắn): {str(verdict)[:100]!r} -- fail-closed về UNCLEAR."
    return verdict, str(result.get("reason", ""))[:500]


# Trạng thái ledger coi như "case_id này đã có kết luận rồi" -- rediscovery
# của ĐÚNG case_id đó (cùng file nguồn + cùng tiêu đề -> case_id tất định
# giống hệt, §1.10) phải bị chặn lại, KHÔNG được lặng lẽ đi qua dedupe như
# 1 case hoàn toàn mới.
_LEDGER_STATUSES_BLOCKING_RESURFACE = {
    CaseLedgerStatus.REJECTED_DUPLICATE, CaseLedgerStatus.REJECTED_POLICY, CaseLedgerStatus.MERGED_INTO,
}


def dedupe_against_ledger(candidate: CandidateCase, ledger: CaseLedger) -> DedupeResult:
    """FIX (Codex review Stage 1, High #3): stage1_blocking() tự loại trừ
    entry.case_id == candidate.case_id (đúng, tránh so 1 candidate với
    chính bản ghi SURFACED/VERIFYING của nó) -- NHƯNG case_id được sinh TẤT
    ĐỊNH từ (discovery_source_file, working_title) (§1.10), nên 1 case đã
    bị REJECTED_POLICY/REJECTED_DUPLICATE/MERGED_INTO rồi được discover LẠI
    (chạy discover_candidates() lần nữa trên cùng file nguồn) sẽ SINH RA
    ĐÚNG case_id cũ -- và bị stage1_blocking() loại trừ luôn khỏi so sánh,
    khiến dedupe_against_ledger() trả 'không trùng' oan. Kiểm tra TRỰC TIẾP
    trạng thái của ĐÚNG case_id này trong ledger TRƯỚC KHI chạy stage1
    blocking -- không dựa vào so khớp fingerprint để bắt lại chính nó."""
    self_entry = ledger.get(candidate.case_id)
    if self_entry is not None and self_entry.status in _LEDGER_STATUSES_BLOCKING_RESURFACE:
        return DedupeResult(
            is_duplicate=True, verdict="SAME_EVENT", matched_case_id=self_entry.case_id, matched_case_status=self_entry.status.value,
            related_case_ids=[], method="same_case_id_already_terminal_in_ledger", dedupe_confidence="high",
            candidates_compared=[self_entry.case_id],
            evidence=f"case_id '{candidate.case_id}' đã có trạng thái '{self_entry.status.value}' trong ledger (policy_trigger={self_entry.policy_trigger!r}) -- không tự động coi là case mới.",
        )

    collisions = stage1_blocking(candidate, ledger)
    if not collisions:
        # FIX (Codex review Stage 1 round 2, High mới #1; cập nhật sau khi
        # verify_sources() được sửa để trích date_range thật qua
        # _extract_date_range() thay vì hardcode None): date_range GIỜ có
        # thể có giá trị thật, nhưng vẫn None bất cứ khi nào văn bản nguồn
        # không nêu rõ thời điểm/không grounding được -- trường hợp đó,
        # tiêu chí blocking ">=2/3 của {date, location, organization}" ở
        # stage1_blocking() vẫn tụt xuống ">=2/2" (location VÀ organization
        # đều phải trùng), yếu hơn thiết kế §1.11 nêu. 1 case thật trùng
        # nhưng viết tên khác/thiếu organization trong 1 trong 2 bên có thể
        # lọt qua blocking hoàn toàn mà vẫn nhận "high confidence" (sai).
        # Hạ confidence về "low" bất cứ khi nào date_range không sẵn có --
        # đúng dịp cho fingerprint yếu hơn tiêu chuẩn 3 tín hiệu đầy đủ.
        low_signal = (
            not candidate.named_individuals
            or all(p.identity_confidence == "low" for p in candidate.named_individuals)
            or candidate.event_fingerprint is None
            or candidate.event_fingerprint.date_range is None
        )
        return DedupeResult(
            is_duplicate=False, verdict=None, matched_case_id=None, matched_case_status=None, related_case_ids=[],
            method="stage1_no_collision", dedupe_confidence="low" if low_signal else "high",
            candidates_compared=[], evidence="Không có collision ở stage 1 blocking.",
        )

    # FIX (Codex review Stage 1 round 2, High mới #2): bản trước return
    # NGAY khi gặp UNCLEAR đầu tiên trong vòng lặp -- 1 collision SAU đó
    # trong cùng danh sách có thể là SAME_EVENT thật nhưng KHÔNG BAO GIỜ
    # được xét tới, khiến 1 duplicate thật bị bỏ sót (chỉ vì thứ tự ngẫu
    # nhiên trong `collisions`). Giờ xử lý HẾT mọi collision trước khi
    # quyết định: SAME_EVENT (bất kỳ đâu trong danh sách) luôn thắng và trả
    # về ngay lập tức khi gặp (không cần đợi hết, vì đây là verdict chung
    # cuộc); nếu không có SAME_EVENT nào nhưng có >=1 UNCLEAR, kết quả cuối
    # cùng là UNCLEAR (chỉ SAU KHI đã chắc chắn không collision nào khác là
    # SAME_EVENT); RELATED_BUT_DISTINCT không chặn, chỉ ghi nhận.
    related_case_ids = []
    actually_compared = []  # FIX (round 3, Low mới): chỉ ghi những case_id THẬT SỰ đã adjudicate, không phải toàn bộ collisions (khi return sớm vì SAME_EVENT, các entry phía sau chưa từng được so sánh)
    saw_unclear = False
    unclear_entry = None
    unclear_reason = ""
    for entry in collisions:
        verdict, reason = stage2_adjudicate(candidate, entry)
        actually_compared.append(entry.case_id)
        if verdict == "SAME_EVENT":
            return DedupeResult(
                is_duplicate=True, verdict="SAME_EVENT", matched_case_id=entry.case_id, matched_case_status=entry.status.value,
                related_case_ids=related_case_ids, method="stage2_llm_adjudication", dedupe_confidence="high",
                candidates_compared=list(actually_compared), evidence=reason,
            )
        if verdict == "RELATED_BUT_DISTINCT":
            related_case_ids.append(entry.case_id)
        elif verdict == "UNCLEAR":
            saw_unclear = True
            if unclear_entry is None:
                unclear_entry, unclear_reason = entry, reason

    # FIX (round 3, Medium mới): thứ tự ưu tiên verdict TỔNG HỢP đúng như
    # thiết kế 4-way (§1.11): SAME_EVENT (đã return ở trên nếu có) >
    # UNCLEAR > RELATED_BUT_DISTINCT > DIFFERENT_EVENT. Bản trước, khi
    # KHÔNG có SAME_EVENT/UNCLEAR nhưng CÓ RELATED_BUT_DISTINCT, vẫn trả
    # verdict="DIFFERENT_EVENT" -- xoá mất chính thông tin RELATED_BUT_DISTINCT
    # ở field verdict cấp cao nhất (dù related_case_ids vẫn giữ, 1 consumer
    # chỉ đọc `verdict` sẽ hiểu sai là "không liên quan gì cả").
    if saw_unclear:
        return DedupeResult(
            is_duplicate=False, verdict="UNCLEAR", matched_case_id=unclear_entry.case_id, matched_case_status=unclear_entry.status.value,
            related_case_ids=related_case_ids, method="stage2_llm_adjudication", dedupe_confidence="low",
            candidates_compared=actually_compared, evidence=unclear_reason,
        )
    if related_case_ids:
        return DedupeResult(
            is_duplicate=False, verdict="RELATED_BUT_DISTINCT", matched_case_id=None, matched_case_status=None,
            related_case_ids=related_case_ids, method="stage2_llm_adjudication", dedupe_confidence="high",
            candidates_compared=actually_compared, evidence="Có collision RELATED_BUT_DISTINCT nhưng không có SAME_EVENT/UNCLEAR nào -- không phải duplicate, nhưng có liên hệ (xem related_case_ids).",
        )
    return DedupeResult(
        is_duplicate=False, verdict="DIFFERENT_EVENT", matched_case_id=None, matched_case_status=None,
        related_case_ids=related_case_ids, method="stage2_llm_adjudication", dedupe_confidence="high",
        candidates_compared=actually_compared, evidence="Mọi collision đều DIFFERENT_EVENT sau adjudication.",
    )


# =============================================================================
# §1.12 -- Rank
# =============================================================================

# §1.12's đủ thiết kế xếp hạng còn có bước "phân bố đều theo sub-pillar
# (round-robin)" -- CHƯA implement ở Stage 1 (Codex review Stage 1, Low
# #10: docstring bản trước tuyên bố đã làm nhưng code không hề dùng danh
# sách này). CandidateCase hiện KHÔNG có field pillar/sub-category nào để
# round-robin dựa vào (chỉ có domain_topic="Hình Sự" chung cho cả kênh) --
# cần Stage 2/3 gắn nhãn sub-pillar cho candidate trước khi có thể làm thật
# bước này. Giữ hằng số ở đây làm tài liệu tham chiếu cho việc đó, KHÔNG
# dùng trong rank_candidates() hiện tại.
_SUB_PILLARS = ("AN_DA_XU", "CHAN_DUNG_SAT_NHAN", "TO_CHUC_TOI_PHAM", "VU_AN_CHUA_LOI_GIAI", "LUAT_HINH_SU")


def _source_quality_score(candidate: CandidateCase) -> tuple:
    """FIX (Codex review Stage 1 round 4, Low): bản trước cộng weight_sum
    cho TỪNG SourceRecord kể cả khi 2 record trùng source_id (vd URL tham
    khảo bị liệt kê lặp trong file nghiên cứu gốc) -- 1 case chỉ vì liệt kê
    trùng URL sẽ được cộng điểm gấp đôi dù không có thêm bằng chứng thật
    nào. Tính weight 1 LẦN/source_id duy nhất."""
    tier_weight = {PublisherTier.PUBLIC_RECORD: 3, PublisherTier.REPUTABLE_PRESS: 2, PublisherTier.AGGREGATOR: 1, PublisherTier.SOCIAL_MEDIA: 0, PublisherTier.UNKNOWN: 0}
    seen_source_ids = set()
    lineage_ids = set()
    weight_sum = 0
    for s in candidate.sources:
        lineage_ids.add(s.source_lineage_id)
        if s.source_id in seen_source_ids:
            continue
        seen_source_ids.add(s.source_id)
        weight_sum += tier_weight.get(s.publisher_tier, 0)
    return (len(lineage_ids), weight_sum)


def rank_candidates(candidates: list[CandidateCase]) -> list[CandidateCase]:
    """§1.12 -- Stage 1 CHỈ xếp hạng theo source-quality score (giảm dần).
    Phân bố đều theo sub-pillar (round-robin, Medium M7's yêu cầu gốc) CHƯA
    implement -- xem ghi chú ở _SUB_PILLARS phía trên, cần Stage 2/3 gắn
    nhãn pillar cho candidate trước. 'Recency of discovery' KHÔNG dùng làm
    yếu tố xếp hạng (Medium M7 -- ưu tiên tin mới có thể khuyến khích chọn
    case còn đang phát triển) -- phần NÀY đã implement đúng (đơn giản là
    không có mặt trong _source_quality_score)."""
    scored = sorted(candidates, key=lambda c: _source_quality_score(c), reverse=True)
    return scored


# =============================================================================
# CLI (kiểm tra thủ công / dry-run -- KHÔNG dùng trong production pipeline)
# =============================================================================

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="CL Risk Gate -- Stage 1 (discover + verify + C1/C2/C3/C6 + dedupe + rank). KHÔNG publish gì.")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi ledger.")
    parser.add_argument("--limit", type=int, default=3, help="Số candidate tối đa để verify (tránh gọi agy hàng loạt khi chỉ kiểm tra thủ công).")
    args = parser.parse_args()

    tiers_config = load_source_tiers()
    stubs = discover_candidates(dry_run=args.dry_run)
    print(f"Discover: {len(stubs)} candidate case(s) tìm thấy trong {SOURCES_DIR}.", flush=True)

    ledger = CaseLedger.load()
    for stub in stubs[:args.limit]:
        print(f"\n=== {stub['working_title']} (case_id={stub['case_id']}) ===", flush=True)
        try:
            candidate = verify_sources(stub, tiers_config)
        except CLRiskGateError as exc:
            print(f"  LỖI verify_sources: {exc}", file=sys.stderr)
            continue
        results = score_available_criteria(candidate)
        for r in results:
            print(f"  {r.criterion_id}: {'PASS' if r.passed else 'FAIL'} -- {r.evidence[:200]}", flush=True)
        dedupe = dedupe_against_ledger(candidate, ledger)
        print(f"  Dedupe: is_duplicate={dedupe.is_duplicate} confidence={dedupe.dedupe_confidence} ({dedupe.evidence[:150]})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
