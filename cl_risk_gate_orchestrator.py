"""CL Risk Gate -- top-level orchestrator (Gate B, task #241). Nối:
  Stage 1 (cl_risk_gate.py: C1/C2/C3/C6 cơ học + dedupe + rank) +
  Stage 2 (cl_risk_gate_verification.py: C4/C5/C7 adversarial;
    cl_claim_exposure_gate.py: Claim-and-Exposure Gate, bắt buộc riêng) +
  §1.13 Phase A bước 3 (cl_case_generation.py: sinh final script+SEO) +
  §1.13 Phase A bước 4-7 (cl_risk_gate_lifecycle.py: run_phase_a_final_review()).

PHẠM VI FILE NÀY (đúng tinh thần honest scope statement xuyên suốt dự án):
  ĐÃ XÂY: run_full_risk_score() (7 tiêu chí C1-C7 đầy đủ, thay
    score_available_criteria()'s Stage-1-only 4 tiêu chí) + run_cl_case_gate()
    (Discover đã có sẵn ở nơi khác -- hàm này nhận list candidate ĐÃ discover,
    KHÔNG tự discover -- Score -> Dedupe -> Rank -> [với top LOW-tier candidate
    tới deficit] Generate (Phase A bước 3) -> Phase A final review (bước 4-7)).
  CHƯA XÂY: Phase B (render handoff thật vào short_batch_runner.py) + Phase C/D
    (post-render checks + atomic upload) -- đó là bước KẾ TIẾP, wiring trực
    tiếp vào short_batch_runner.py's process_one_segment() (người dùng đã
    chốt hướng đi trực tiếp sửa file chung, không tách driver riêng) -- xem
    CL_GATE_WIRING_TODO ở cuối file cho điểm nối cụ thể.
  §1.13 bước 1-2 (CL_REAL_PERSONS_v1.json manifest + symbol_library alias
    auto-write, §1.15) -- CHƯA xây, để lại cho increment kế tiếp.

GIỚI HẠN TÍCH HỢP (LỊCH SỬ, ĐÃ SỬA -- giữ lại đoạn này làm hồ sơ căn
nguyên): phát hiện qua review độc lập Cursor/Grok, xác minh trực tiếp trong
cl_risk_gate.py: Stage 1's verify_sources() từng LUÔN để
event_fingerprint.date_range=None (chưa xây trích xuất ngày tháng thật).
dedupe_against_ledger() coi date_range=None là 1 "low signal", tự động hạ
dedupe_confidence xuống "low" cho MỌI candidate không va chạm blocking --
nghĩa là run_cl_case_gate() từng escalate GẦN NHƯ MỌI candidate vào
escalated_low_confidence_dedupe (chờ người), KHÔNG có candidate nào tới
được scoring/generation trong điều kiện vận hành thật.

ĐÃ SỬA (task #261): verify_sources() giờ gọi _extract_date_range() --
event_fingerprint schema của _EXTRACT_CASE_FACTS_PROMPT có thêm
date_range_start/date_range_end/date_range_excerpt, chỉ tin khi đúng định
dạng YYYY hoặc YYYY-MM-DD VÀ excerpt grounding được trong case_text (cùng
kỷ luật fail-closed như disposition/life_status/finality_state). date_range
vẫn None (và dedupe_confidence vẫn "low") cho case genuinely không nêu rõ
thời điểm trong nguồn -- đây là hành vi ĐÚNG (không suy đoán), không phải
giới hạn còn sót lại."""
import sys
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import cl_risk_gate as g  # noqa: E402
from cl_risk_gate_verification import score_c4_adversarial, score_c5_adjudicated, score_c7_adversarial  # noqa: E402
from cl_claim_exposure_gate import score_claim_exposure_gate  # noqa: E402
from cl_case_generation import generate_cl_final_content  # noqa: E402
from cl_risk_gate_lifecycle import run_phase_a_final_review  # noqa: E402


# =============================================================================
# run_full_risk_score() -- 7 tiêu chí ĐẦY ĐỦ (C1-C7), thay
# score_available_criteria() (chỉ 4 tiêu chí Stage 1) làm nguồn THẬT cho
# tier_for(). KHÔNG đặt trong cl_risk_gate.py (sẽ tạo import vòng: file đó
# bị cl_risk_gate_verification.py import làm `g`).
# =============================================================================

ALLOWLIST_VERSION = "CL_SOURCE_TIERS_v1"


def run_full_risk_score(candidate: g.CandidateCase) -> g.RiskScoreResult:
    """Chạy ĐỦ 7 tiêu chí (C1/C2/C3/C6 cơ học -- cl_risk_gate.py; C4/C5/C7
    adversarial -- cl_risk_gate_verification.py, cần candidate.risk_review_draft
    VÀ named_individuals[*].legal_status/role_verification đã cross_verified
    qua Stage 2's cross_verify_named_individuals() TRƯỚC ĐÓ -- hàm này KHÔNG
    tự chạy cross-verify, chỉ ĐỌC kết quả đã có). high_risk_triggers: evidence
    của MỌI tiêu chí STRUCTURAL (C5/C6) fail -- lý do cụ thể đẩy case lên HIGH
    tier, không chỉ mã tiêu chí suông."""
    criteria = [
        g.score_c1(candidate), g.score_c2(candidate), g.score_c3(candidate),
        score_c4_adversarial(candidate), score_c5_adjudicated(candidate),
        g.score_c6(candidate), score_c7_adversarial(candidate),
    ]
    failing_criteria = [c.criterion_id for c in criteria if not c.passed]
    high_risk_triggers = [f"{c.criterion_id}: {c.evidence}" for c in criteria if not c.passed and c.criterion_id in g.STRUCTURAL_CRITERIA]
    result = g.RiskScoreResult(
        tier="",  # lấp ngay dưới, tier_for() cần result đã có failing_criteria
        criteria=criteria, failing_criteria=failing_criteria, high_risk_triggers=high_risk_triggers,
        rationale=f"{len(criteria) - len(failing_criteria)}/{len(criteria)} tiêu chí PASS." + (f" FAIL: {failing_criteria}." if failing_criteria else ""),
        scorer_version=g.SCORER_VERSION, allowlist_version=ALLOWLIST_VERSION,
        scored_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    result.tier = g.tier_for(result)
    return result


# =============================================================================
# run_cl_case_gate() -- §1.13's CLGateResult orchestrator, PHẦN Score->
# Dedupe->Rank->Generate->PhaseA (chưa gồm Phase B/C/D, xem docstring đầu
# file). Nhận list candidate ĐÃ discover (không tự discover ở đây).
# =============================================================================

@dataclass
class CLGateResult:
    auto_selected: list = field(default_factory=list)  # list[tuple[CandidateCase, CLGenerationResult, PhaseAFinalReviewResult]] -- sẵn sàng Phase B. FIX (finding thật từ review độc lập Cursor/Grok round 2, HIGH): bản đầu CHỈ giữ (candidate, review_result) -- PhaseAFinalReviewResult KHÔNG mang final_script/final_editorial (chỉ có hash/refs/claim_ledger), nghĩa là artifact ĐÃ PASS review bị VỨT MẤT ngay sau khi review xong -- Phase B (caller) không có gì để TTS/render, và re-generate lại để lấy nội dung sẽ cho hash KHÁC (không còn khớp reviewed_editorial_hash đã lưu). Giữ CẢ gen_result (có final_script/final_editorial thật) LẪN review_result (có reviewed_editorial_hash để Phase D so khớp sau này).
    escalated_high: list = field(default_factory=list)  # list[tuple[CandidateCase, RiskScoreResult]]
    escalated_medium_exhausted: list = field(default_factory=list)
    rejected_duplicate: list = field(default_factory=list)  # list[tuple[CandidateCase, DedupeResult]]
    escalated_low_confidence_dedupe: list = field(default_factory=list)
    escalated_generation_failed: list = field(default_factory=list)  # list[tuple[CandidateCase, CLGenerationResult]]
    escalated_phase_a_review_failed: list = field(default_factory=list)  # list[tuple[CandidateCase, CLGenerationResult, PhaseAFinalReviewResult]] -- FIX (Low/Medium #8, review độc lập): TÁCH khỏi escalated_generation_failed -- 2 kiểu object khác nhau (.reason vs .reason_code) chung 1 list khiến caller dễ đọc nhầm field. Giữ gen_result CẢ Ở NHÁNH FAIL (đối xứng với auto_selected's fix round 2) -- người review thủ công cần thấy ĐÚNG script/SEO đã fail, không phải regenerate để xem lại.
    escalated_claim_exposure_failed: list = field(default_factory=list)  # list[tuple[CandidateCase, ClaimGateResult]] -- MỚI, xem Fix #1
    deferred_deficit: list = field(default_factory=list)  # list[CandidateCase] -- FIX (Medium #6): LOW-tier, dedupe sạch, claim-gate PASS, nhưng KHÔNG được chọn vì đã đủ deficit -- KHÔNG phải escalation (không có gì sai), nhưng PHẢI có bucket riêng, không lẫn vào "chưa từng được nhắc tới"
    audit_log: list = field(default_factory=list)  # mỗi entry: {"case_id", "stage", "outcome", "detail"}


def _log(audit_log: list, case_id: str, stage: str, outcome: str, detail: str) -> None:
    audit_log.append({"case_id": case_id, "stage": stage, "outcome": outcome, "detail": detail[:2000]})


def run_cl_case_gate(candidates: list, ledger: g.CaseLedger, deficit: int, max_script_rounds: int = 3, max_seo_iterations: int = 3) -> CLGateResult:
    """§1.13's orchestrator, PHẦN Score->Dedupe->Rank->Generate->Phase A.

    Thứ tự XỬ LÝ (khác thứ tự BƯỚC trong spec -- lý do: dedupe RẺ hơn full
    7-criteria scoring rất nhiều, loại trùng TRƯỚC khi tốn chi phí LLM cho
    C4/C5/C7 trên case đằng nào cũng bị loại):
      1. Dedupe TỪNG candidate chống ledger hiện có, VÀ chống các candidate
         KHÁC trong CÙNG batch này (FIX High #3, review độc lập Cursor/
         Grok -- xem docstring case_key match dưới đây cho giới hạn thật
         của cơ chế intra-batch) -- loại/escalate ngay nếu trùng/nghi
         trùng, KHÔNG tốn chi phí scoring cho case đó.
      2. Full risk score (7 tiêu chí) cho candidate còn lại -- escalate
         theo tier (HIGH/MEDIUM -- KHÔNG tự sinh, chờ người; chỉ LOW mới
         vào bước tiếp; tier lạ/rỗng -- FIX Medium #5 -- fail-closed như
         HIGH, KHÔNG mặc định coi là LOW).
      3. Claim-and-Exposure Gate (§1.6, MANDATORY, KHÔNG phải 1 trong 7
         tiêu chí -- FIX High #1, review độc lập: bản đầu import nhưng
         KHÔNG BAO GIỜ gọi, "nối Stage 2 đầy đủ" là overclaim) chạy trên
         candidate.risk_review_draft cho MỌI candidate LOW-tier TRƯỚC khi
         xếp hạng/sinh nội dung -- fail thì escalate, không lãng phí chi
         phí generate cho case đằng nào cũng bị chặn ở đây.
      4. Rank các candidate LOW-tier đã qua claim-gate, LẶP qua theo thứ tự
         hạng (FIX Medium #7 -- backfill: KHÔNG chỉ thử đúng slice
         [:deficit] một lần rồi dừng, mà tiếp tục thử candidate hạng kế
         tiếp nếu candidate trước đó generation/Phase A review fail, tới
         khi auto_selected đủ deficit HOẶC hết candidate) -- với MỖI
         candidate: sinh final content (Phase A bước 3) rồi Phase A final
         review (bước 4-7) -- PASS thì vào auto_selected (sẵn sàng Phase
         B), KHÔNG PASS thì escalate kèm lý do cụ thể VÀ thử candidate kế
         tiếp. Candidate LOW-tier hợp lệ nhưng KHÔNG được thử tới (đã đủ
         deficit) -> deferred_deficit (FIX Medium #6), KHÔNG bị coi là
         "chưa từng được nhắc tới".

    `deficit` PHẢI là int >= 0 (FIX High #2, review độc lập: bản đầu dùng
    thẳng `ranked[:deficit]` -- deficit ÂM qua Python slice semantics lấy
    GẦN HẾT list thay vì rỗng, vd `ranked[:-1]` == "mọi phần tử trừ cuối
    cùng"; đây là gate RỦI RO CAO, không được tin input chưa validate) --
    raise ValueError nếu không hợp lệ, fail-closed thay vì âm thầm nhận
    input sai.

    GIỚI HẠN THẬT VỀ INTRA-BATCH DEDUPE (ghi rõ, không giấu): so khớp CHỈ
    dựa trên `case_key` TRÙNG TUYỆT ĐỐI (cùng cách sinh case_key đã dùng
    cho ledger, xem cl_risk_gate.py's case_id/case_key convention) -- bắt
    được đúng 1 case bị discover 2 lần TRONG CÙNG 1 lần gọi batch (case_key
    tất định từ cùng nguồn), KHÔNG bắt được 2 candidate MÔ TẢ CÙNG sự kiện
    thật nhưng có case_key khác nhau (viết khác tên/nguồn khác) -- việc đó
    cần full stage1_blocking()-style so sánh cặp, TỐN KÉM hơn nhiều (O(n²)
    so sánh fingerprint), để lại cho increment sau nếu batch size lớn dần
    lên khiến rủi ro này đáng kể hơn chi phí.

    KHÔNG tự discover (candidates là input) -- xem docstring đầu file. Ghi
    audit_log CHO MỌI candidate ở MỌI outcome (không rơi rớt case nào không
    ai biết), đúng nguyên tắc "escalated/rejected candidates are NEVER
    silently dropped" của §1.13 -- bao gồm CẢ candidate bị deferred vì hết
    deficit (FIX Medium #6)."""
    if not isinstance(deficit, int) or isinstance(deficit, bool) or deficit < 0:
        raise ValueError(f"deficit phải là int >= 0 (nhận được: {deficit!r}, kiểu {type(deficit).__name__}) -- fail-closed, không tin input gate rủi ro cao chưa validate.")

    result = CLGateResult()

    still_in_play = []
    seen_case_keys_this_batch = set()
    for candidate in candidates:
        if candidate.case_key in seen_case_keys_this_batch:
            fake_dedupe = g.DedupeResult(
                is_duplicate=True, verdict="SAME_EVENT", matched_case_id=None, matched_case_status=None,
                related_case_ids=[], method="intra_batch_case_key_match", dedupe_confidence="high",
                candidates_compared=[], evidence=f"case_key '{candidate.case_key}' trùng với 1 candidate KHÁC đã xử lý TRONG CÙNG batch này (chưa kịp vào ledger) -- xem giới hạn thật ở docstring hàm.",
            )
            result.rejected_duplicate.append((candidate, fake_dedupe))
            _log(result.audit_log, candidate.case_id, "dedupe", "REJECTED_DUPLICATE_INTRA_BATCH", fake_dedupe.evidence)
            continue

        dedupe_result = g.dedupe_against_ledger(candidate, ledger)
        if dedupe_result.dedupe_confidence == "low":
            result.escalated_low_confidence_dedupe.append((candidate, dedupe_result))
            _log(result.audit_log, candidate.case_id, "dedupe", "ESCALATED_LOW_CONFIDENCE", dedupe_result.evidence)
            continue
        if dedupe_result.is_duplicate:
            result.rejected_duplicate.append((candidate, dedupe_result))
            _log(result.audit_log, candidate.case_id, "dedupe", "REJECTED_DUPLICATE", dedupe_result.evidence)
            continue
        _log(result.audit_log, candidate.case_id, "dedupe", "CLEARED", dedupe_result.evidence)
        seen_case_keys_this_batch.add(candidate.case_key)
        still_in_play.append(candidate)

    low_tier_candidates = []
    for candidate in still_in_play:
        score = run_full_risk_score(candidate)
        if score.tier == "LOW":
            _log(result.audit_log, candidate.case_id, "score", "LOW_CLEARED", score.rationale)
            low_tier_candidates.append(candidate)
        elif score.tier == "MEDIUM":
            result.escalated_medium_exhausted.append((candidate, score))
            _log(result.audit_log, candidate.case_id, "score", "ESCALATED_MEDIUM", score.rationale)
        else:
            # FIX (Medium #5, review độc lập): "HIGH" LẪN bất kỳ giá trị
            # tier nào KHÁC LOW/MEDIUM (rỗng, typo, giá trị lạ tương lai)
            # đều fail-closed vào escalated_high -- bản đầu dùng `else`
            # bắt HIGH tự nhiên nhưng đồng thời cũng ÂM THẦM coi mọi giá
            # trị lạ là "LOW" ở nhánh khác, đúng loại fail-open đã sửa
            # nhiều lần trong dự án này.
            _log(result.audit_log, candidate.case_id, "score", "ESCALATED_HIGH" if score.tier == "HIGH" else "ESCALATED_UNKNOWN_TIER_FAIL_CLOSED", score.rationale)
            result.escalated_high.append((candidate, score))

    claim_gate_cleared = []
    for candidate in low_tier_candidates:
        # FIX (High #1, review độc lập): Claim-and-Exposure Gate (§1.6) là
        # MANDATORY, "áp dụng bất kể C1-C7 risk tier" -- bản đầu IMPORT
        # nhưng KHÔNG BAO GIỜ GỌI, khiến case fail claim-gate trên chính
        # risk_review_draft (Stage 2 output) vẫn đi thẳng vào generation
        # (Phase A chỉ chặn được TRÊN FINAL SCRIPT, không phải input Stage
        # 2 đã có sẵn) -- đóng khoảng hở TRƯỚC khi tốn chi phí generate.
        claim_result = score_claim_exposure_gate(candidate)
        if not claim_result.passed:
            result.escalated_claim_exposure_failed.append((candidate, claim_result))
            _log(result.audit_log, candidate.case_id, "claim_exposure_gate", f"ESCALATED_{claim_result.reason_code}", claim_result.evidence)
            continue
        _log(result.audit_log, candidate.case_id, "claim_exposure_gate", "CLEARED", claim_result.evidence)
        claim_gate_cleared.append(candidate)

    ranked = g.rank_candidates(claim_gate_cleared)

    # FIX (Medium #7, review độc lập -- backfill): LẶP qua TOÀN BỘ ranked
    # theo thứ tự, KHÔNG chỉ thử đúng deficit candidate đầu tiên -- candidate
    # generation/Phase A review fail KHÔNG được tính vào deficit đã lấp,
    # thử tiếp candidate hạng kế tiếp cho tới khi auto_selected đủ deficit
    # HOẶC hết candidate.
    for candidate in ranked:
        if len(result.auto_selected) >= deficit:
            result.deferred_deficit.append(candidate)
            _log(result.audit_log, candidate.case_id, "rank", "DEFERRED_DEFICIT", f"LOW-tier, claim-gate PASS, hạng #{ranked.index(candidate) + 1}/{len(ranked)}, nhưng đã đủ deficit={deficit} -- không phải lỗi, chờ vòng sau.")
            continue

        gen_result = generate_cl_final_content(candidate, max_script_rounds=max_script_rounds, max_seo_iterations=max_seo_iterations)
        if not gen_result.passed:
            result.escalated_generation_failed.append((candidate, gen_result))
            _log(result.audit_log, candidate.case_id, "generate", "ESCALATED_GENERATION_FAILED", gen_result.reason or "")
            continue

        review_result = run_phase_a_final_review(candidate, gen_result.final_script, gen_result.final_editorial)
        if not review_result.passed:
            result.escalated_phase_a_review_failed.append((candidate, gen_result, review_result))
            _log(result.audit_log, candidate.case_id, "phase_a_review", f"ESCALATED_{review_result.reason_code}", review_result.evidence)
            continue

        result.auto_selected.append((candidate, gen_result, review_result))
        _log(result.audit_log, candidate.case_id, "phase_a_review", "PASSED_READY_FOR_PHASE_B", review_result.evidence)

    return result


# =============================================================================
# CL_GATE_WIRING_TODO -- điểm nối CỤ THỂ vào short_batch_runner.py (Phase
# B/C/D), CHƯA triển khai trong increment này. Ghi lại rõ ràng để không ai
# (kể cả increment sau) phải dò lại từ đầu:
#
# 1. process_one_segment() (short_batch_runner.py) hiện đi thẳng từ
#    status="seo_ready" -> upload_short() (bước 5), KHÔNG có hook nào ở
#    giữa. Cần thêm nhánh `if topic == "Hình Sự":` NGAY TRƯỚC lệnh gọi
#    upload_short() thật (dòng ~624), gọi:
#      a. Phase C: cl_risk_gate_lifecycle.verify_phase_c_audio_chain(...) +
#         sample_frame_timestamps()/sample_and_ocr_frames()/
#         run_visual_person_reference_check() trên video_path đã render --
#         audio custody chain áp dụng dạng suy biến N=1 segment (script
#         nguyên khối = 1 segment, xem ghi chú kiến trúc trong báo cáo gửi
#         người dùng phiên này -- run_tts() ở đây sinh 1 WAV DUY NHẤT cho cả
#         script, KHÔNG có file audio riêng từng câu).
#      b. Phase D: stage_artifacts_exclusive() + assemble_upload_manifest()
#         + safe_upload() -- upload_fn truyền vào PHẢI wrap upload_short()
#         hiện có (không viết lại logic upload YouTube).
#    Cả 2 bước fail -> entry["status"] = "needs_review" (cùng pattern các
#    gate khác trong hàm này), KHÔNG tự tiến upload.
# 2. Cần thêm field mới vào registry entry cho CL: run_id (cho §1.16 audit +
#    staging exclusive-create), reviewed_editorial_hash (persist từ Phase A
#    để Phase D so khớp KHI RESUME -- nếu tiến trình bị ngắt giữa Phase A và
#    Phase D, resume phải đọc LẠI hash đã lưu, không tính lại từ registry
#    hiện tại có thể đã bị sửa).
# 3. CandidateCase's named_individuals cần route qua CL_REAL_PERSONS_v1.json
#    + symbol_library alias TRƯỚC KHI TTS/render chạy (§1.13 bước 1-2, CHƯA
#    xây) -- nếu bỏ qua bước này, asset-safety gate (G5, đã có sẵn trong
#    short_batch_runner.py) có thể không có asset an toàn để route real-
#    person reference tới, khiến render dùng fallback không phù hợp.
# 4. twice_weekly_batch.py's CL "manual_only" branch cần thay bằng lời gọi
#    run_cl_case_gate() (candidates lấy từ Stage 1's discover mechanism,
#    CHƯA xây tách biệt run_full_risk_score() khỏi cl_risk_gate.py's
#    discover_and_verify flow -- cần xác nhận lại discover thật lấy
#    candidate từ đâu, hàm đó chưa được review trong increment này).
# =============================================================================
