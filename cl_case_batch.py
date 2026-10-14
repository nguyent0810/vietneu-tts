"""CL Risk Gate -- driver CLI nối Stage 1 (discover/verify) + Stage 2
(cross-verify + risk_review_draft) + Stage 3 orchestrator (score/dedupe/
rank/generate/Phase A review, cl_risk_gate_orchestrator.run_cl_case_gate())
với bundle+sidecar mà short_batch_runner.py's CL branch (task #241, xem
process_one_segment()) đọc vào.

CHỦ ĐÍCH CHẠY THỦ CÔNG, KHÔNG nằm trong twice_weekly_batch.py's cron path
(increment này). twice_weekly_batch.py's CL vẫn giữ nguyên "manual_only"
(chỉ log BLOCKED_REVIEW) -- việc TỰ ĐỘNG gọi script này mỗi tuần là 1
QUYẾT ĐỊNH RỦI RO RIÊNG (gỡ bỏ đúng checkpoint con người đã được thêm vào
SAU 1 sự cố thật: agent CL từng chọn nhầm case có nạn nhân vị thành niên,
xem docstring twice_weekly_batch.py), để lại có chủ đích cho SAU KHI task
#242 (7 kịch bản test bắt buộc + review Codex CLI đối kháng thật) PASS --
đúng tinh thần "self-review không bao giờ thay thế cổng Codex bắt buộc"
đã áp dụng xuyên suốt dự án này. Script này CHỈ ghi file ra đĩa cho người/
agent xem lại trước khi (nếu đồng ý) chạy short_batch_runner.py --topic
"Hình Sự" thủ công.

Output cho MỖI auto_selected candidate:
  - drive_input/content_repo_staged/Hình Sự/Short/CLGATE_<case_id>_Short.txt
    (marker "*** 1" + final_script, ĐÚNG format discover_segments() đọc)
  - <cùng thư mục>/CLGATE_<case_id>_Short.cl_meta.json (sidecar --
    reviewed_editorial_hash/final_editorial/named_individuals/case_id,
    xem cl_metadata_sidecar_path()/docstring process_one_segment())

Mọi bucket escalate (HIGH/MEDIUM/dedupe/claim-gate/generation/Phase A fail/
deferred_deficit) CHỈ được in ra cho người xem, KHÔNG ghi bundle nào --
đúng thiết kế "chỉ auto_selected mới sẵn sàng Phase B" của
cl_risk_gate_orchestrator.py."""
import argparse
import json
import os
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import cl_risk_gate as g  # noqa: E402
from cl_risk_gate_verification import cross_verify_named_individuals, generate_risk_review_draft  # noqa: E402
from cl_risk_gate_orchestrator import run_cl_case_gate  # noqa: E402
from cl_risk_gate_lifecycle import _script_text_hash  # noqa: E402
from short_segment_discovery import cl_metadata_sidecar_path  # noqa: E402

CL_TOPIC = "Hình Sự"


def _serialize_named_individuals(named_individuals: list) -> list:
    """CHỈ giữ 2 field mà Phase C's person-reference check thật sự đọc
    (_mechanical_person_reference_scan()/run_visual_person_reference_check(),
    cl_risk_gate_lifecycle.py) -- canonical_name/short_form_alias/role.
    KHÔNG serialize legal_status/role_verification (nội bộ Stage 2, không
    cần thiết cho Phase C, tránh sidecar phình to vô ích)."""
    return [
        {"canonical_name": p.canonical_name, "short_form_alias": p.short_form_alias, "role": p.role}
        for p in named_individuals
    ]


def prepare_candidates(limit: int, tiers_config: dict) -> list:
    """Stage 1 (discover + verify_sources) + Stage 2 (cross_verify_named_
    individuals + generate_risk_review_draft) cho tối đa `limit` candidate
    mới phát hiện -- ĐÚNG thứ tự run_full_risk_score()'s docstring đòi hỏi
    (cl_risk_gate_orchestrator.py: "cần candidate.risk_review_draft VÀ
    named_individuals[*].legal_status/role_verification đã cross_verified
    qua Stage 2's cross_verify_named_individuals() TRƯỚC ĐÓ"). 1 candidate
    lỗi ở bất kỳ bước nào bị BỎ QUA (in cảnh báo), KHÔNG làm hỏng cả batch
    -- các candidate còn lại vẫn được thử."""
    stubs = g.discover_candidates(dry_run=False)
    print(f"Discover: {len(stubs)} candidate case(s) trong {g.SOURCES_DIR}.", flush=True)
    candidates = []
    for stub in stubs[:limit]:
        title = stub["working_title"]
        try:
            candidate = g.verify_sources(stub, tiers_config)
            candidate = cross_verify_named_individuals(candidate, stub["case_text"])
            candidate.risk_review_draft = generate_risk_review_draft(candidate)
        except Exception as exc:  # noqa: BLE001 -- 1 candidate lỗi không được chặn cả batch
            print(f"  BỎ QUA '{title}' (case_id={stub['case_id']}): lỗi Stage 1/2 ({type(exc).__name__}): {exc}", file=sys.stderr, flush=True)
            continue
        candidates.append(candidate)
    return candidates


def _atomic_write_text(path: Path, content: str) -> None:
    """write_text() thường KHÔNG atomic (torn write nếu tiến trình khác đọc
    giữa chừng, hoặc process bị kill giữa lúc ghi) -- ghi ra file tạm CÙNG
    thư mục (đảm bảo os.replace() cùng filesystem, atomic thật trên POSIX)
    rồi rename đè lên đích. FIX (review độc lập Cursor/Grok, MEDIUM #2):
    bản đầu dùng write_text() thẳng cho CẢ bundle .txt LẪN sidecar .json --
    2 tiến trình cùng ghi 1 case_id (dù script này chủ đích chạy thủ công,
    không loại trừ chạy tay trùng lúc) có thể xen kẽ, để lại 1 cặp bundle/
    sidecar KHÔNG khớp nhau (vd bundle của lần chạy B, sidecar của lần chạy
    A). Atomic per-file thu hẹp còn đúng 1 rủi ro dư (không giả vờ hết): 2
    lần rename (sidecar rồi bundle, xem thứ tự thật trong write_bundle_and_
    sidecar() bên dưới) không phải 1 giao dịch -- 1 tiến trình
    khác ĐỌC ĐÚNG khoảng giữa 2 lần rename đó vẫn có thể thấy cặp không
    khớp trong khoảnh khắc rất ngắn. Chấp nhận được ở quy mô công cụ thủ
    công/1 người vận hành (không xây transaction 2-file đầy đủ)."""
    tmp_path = path.with_suffix(path.suffix + f".tmp{uuid.uuid4().hex[:8]}")
    tmp_path.write_text(content, encoding="utf-8")
    os.replace(tmp_path, path)


def write_bundle_and_sidecar(candidate, gen_result, review_result, out_dir: Path) -> Path:
    file_id = f"CLGATE_{candidate.case_id}"
    bundle_path = out_dir / f"{file_id}_Short.txt"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)

    sidecar = {
        "case_id": candidate.case_id,
        "reviewed_editorial_hash": review_result.reviewed_editorial_hash,
        "reviewed_script_hash": _script_text_hash(gen_result.final_script),
        "final_editorial": gen_result.final_editorial,
        "named_individuals": _serialize_named_individuals(candidate.named_individuals),
    }
    sidecar_path = cl_metadata_sidecar_path(file_id, CL_TOPIC)
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)

    # Ghi sidecar TRƯỚC, bundle SAU: nếu 1 tiến trình khác (short_batch_
    # runner.py) đang trong lúc quét thư mục thấy bundle .txt xuất hiện
    # TRƯỚC sidecar tương ứng, discover_segments() coi đó là 1 segment
    # bình thường -- process_one_segment() bước 1 sẽ fail-closed đúng cách
    # (sidecar thiếu -> needs_review) THAY VÌ đọc phải sidecar CŨ/của case
    # khác khớp nhầm hash. Thứ tự ngược lại (bundle trước) mở ra khoảng hở
    # sidecar-chưa-tồn-tại NHƯNG bundle đã sẵn sàng bị discover -- cùng kết
    # cục fail-closed thật ra, nhưng ghi sidecar trước vẫn là thứ tự an
    # toàn hơn về mặt logic (dữ liệu review có trước dữ liệu công khai).
    _atomic_write_text(sidecar_path, json.dumps(sidecar, ensure_ascii=False, indent=2))
    _atomic_write_text(bundle_path, f"*** 1\n{gen_result.final_script}\n")
    return bundle_path


def main() -> int:
    ap = argparse.ArgumentParser(description=(
        "CL Risk Gate -- chạy Stage 1/2/3 (Score->Dedupe->Rank->Generate->Phase A) "
        "rồi ghi bundle+sidecar cho short_batch_runner.py's CL branch. THỦ CÔNG, "
        "KHÔNG nằm trong cron -- xem docstring đầu file."
    ))
    ap.add_argument("--deficit", type=int, required=True, help="Số slot CL cần lấp (int >= 0).")
    ap.add_argument("--limit", type=int, default=10, help="Số candidate MỚI tối đa để chạy Stage 1/2 (mỗi candidate tốn nhiều lượt gọi agy/Codex thật).")
    ap.add_argument("--out-dir", default=None, help=f"Mặc định drive_input/content_repo_staged/{CL_TOPIC}/Short/.")
    args = ap.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else PROJECT_ROOT / "drive_input" / "content_repo_staged" / CL_TOPIC / "Short"

    tiers_config = g.load_source_tiers()
    candidates = prepare_candidates(args.limit, tiers_config)
    print(f"Sẵn sàng scoring: {len(candidates)}/{args.limit} candidate qua Stage 1/2.", flush=True)

    ledger = g.CaseLedger.load()
    result = run_cl_case_gate(candidates, ledger, args.deficit)

    for candidate, gen_result, review_result in result.auto_selected:
        bundle_path = write_bundle_and_sidecar(candidate, gen_result, review_result, out_dir)
        print(f"[AUTO_SELECTED] {candidate.working_title} (case_id={candidate.case_id}) -> {bundle_path}", flush=True)

    def _print_bucket(name: str, items: list):
        if items:
            print(f"[{name}] {len(items)} case", flush=True)
            for item in items:
                candidate = item[0] if isinstance(item, tuple) else item
                print(f"  - {candidate.working_title} (case_id={candidate.case_id})", flush=True)

    _print_bucket("ESCALATED_HIGH", result.escalated_high)
    _print_bucket("ESCALATED_MEDIUM_EXHAUSTED", result.escalated_medium_exhausted)
    _print_bucket("REJECTED_DUPLICATE", result.rejected_duplicate)
    _print_bucket("ESCALATED_LOW_CONFIDENCE_DEDUPE", result.escalated_low_confidence_dedupe)
    _print_bucket("ESCALATED_GENERATION_FAILED", result.escalated_generation_failed)
    _print_bucket("ESCALATED_PHASE_A_REVIEW_FAILED", result.escalated_phase_a_review_failed)
    _print_bucket("ESCALATED_CLAIM_EXPOSURE_FAILED", result.escalated_claim_exposure_failed)
    _print_bucket("DEFERRED_DEFICIT", result.deferred_deficit)

    print(f"\nTổng kết: auto_selected={len(result.auto_selected)}/{args.deficit} deficit.", flush=True)
    if len(result.auto_selected) < args.deficit:
        print("CHƯA đủ deficit -- xem các bucket escalate ở trên, CẦN NGƯỜI xử lý thủ công (không tự retry/nới lỏng gate).", flush=True)
    if result.auto_selected:
        print(
            "\nSau khi người xem lại các file trên, chạy tiếp (thủ công):\n"
            f'  python short_batch_runner.py --topic "{CL_TOPIC}" --episodes CLGATE '
            f'--credentials .youtube_channels/hinh_su.json --count {len(result.auto_selected)}\n'
            "(prefix 'CLGATE' khớp glob discover_segments() dùng -- xem short_segment_discovery.py.)",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
