"""Driver Phase A THẬT cho content STORYTELLING kênh Hình Sự -- Option C
của yêu cầu vá lỗi "CHECK THE OPTIONAL PARAMETER FOOTGUN": đây là wrapper
production DUY NHẤT bắt buộc xác minh, thay vì để an toàn phụ thuộc việc
1 caller tương lai có nhớ truyền claim_ledger_topic_id hay không.

TRƯỚC bản vá này, KHÔNG có script nào trong repo thật sự gọi
compute_phase_a_result()/write_storytelling_sidecar() -- toàn bộ lần chạy
Phase A cho STORYTELLING trong dự án đều qua script tạm ở scratchpad
(ngoài repo, không review được, mỗi lần tái tạo lại logic fuzzy-match
title). File NÀY là driver chính thức đầu tiên, thay thế hẳn quy trình đó.

QUAN TRỌNG -- không có "chế độ bỏ qua ledger": driver này LUÔN resolve
claim_ledger_topic_id thật từ sidecar {episode}_Short.topic_meta.json (ghi
bởi criminal_law_short_generator.py's write_topic_meta_sidecar() tại thời
điểm sinh nội dung) rồi truyền cho compute_phase_a_result() -- không có
nhánh code nào ở đây gọi hàm đó với claim_ledger_topic_id=None. Episode
KHÔNG có sidecar topic_meta (sinh trước bản vá này, hoặc lỗi ghi) bị chặn
NGAY tại đây với STORYTELLING_FACT_LEDGER_MISSING, KHÔNG âm thầm chạy qua
đường cũ."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import cl_claim_ledger  # noqa: E402
import content_invariant  # noqa: E402
import content_quality_gate as cqg  # noqa: E402
import script_quality_gate as sqg  # noqa: E402
from criminal_law_storytelling_phase_a import CL_TOPIC, compute_phase_a_result, content_quality_outcome, write_storytelling_sidecar  # noqa: E402
from short_segment_discovery import cl_metadata_sidecar_path, cl_topic_meta_sidecar_path  # noqa: E402

SHORT_DIR = PROJECT_ROOT / "drive_input" / "content_repo_staged" / CL_TOPIC / "Short"


def discover_pending_storytelling_episodes() -> list:
    """Episode STORYTELLING (prefix ANDAXU_) CHƯA có sidecar Phase A --
    KHÔNG đụng episode đã PASS trước đó (đúng "existing output not
    destroyed", xem yêu cầu vá lỗi PART 10)."""
    pending = []
    for txt_path in sorted(SHORT_DIR.glob("ANDAXU_*_Short.txt")):
        episode = txt_path.name.removesuffix("_Short.txt")
        if not cl_metadata_sidecar_path(episode, CL_TOPIC).exists():
            pending.append(episode)
    return pending


def run_one(episode: str) -> tuple:
    """Chạy Phase A THẬT cho đúng 1 episode qua cổng ledger bắt buộc. Trả
    (status: str, detail: str) -- status ∈ {"PASS", "BLOCKED_FACT",
    "FACT_LEDGER_MISSING", "FAIL", "SKIPPED_ALREADY_DONE"}.

    Tự review đối kháng (yêu cầu vá lỗi PART 15) phát hiện: nếu gọi hàm
    này qua --episodes TRỰC TIẾP (bỏ qua discover_pending_storytelling_
    episodes(), vốn đã tự loại episode có sẵn sidecar) cho 1 episode ĐÃ
    PASS trước đó, nó sẽ chạy lại Phase A rồi GHI ĐÈ sidecar cũ mà không
    cảnh báo -- 1 lần chạy lại kém may mắn (nhiễu ngẫu nhiên LLM, xem
    docstring compute_phase_a_result) có thể hạ cấp 1 episode đã tốt xuống
    FAIL/BLOCKED_FACT, hoặc ngược lại ghi đè fact_verification bằng dữ
    liệu MỚI dù không có gì thay đổi thật. Chặn NGAY tại đây, không cần
    người gọi tự nhớ kiểm tra trước -- đúng tinh thần "existing output
    not destroyed" (PART 10) áp dụng cho CẢ đường gọi thủ công."""
    existing_sidecar = cl_metadata_sidecar_path(episode, CL_TOPIC)
    if existing_sidecar.exists():
        return "SKIPPED_ALREADY_DONE", f"{existing_sidecar.name} đã tồn tại -- không chạy lại (xoá sidecar cũ thủ công nếu thật sự cần re-verify)."

    txt_path = SHORT_DIR / f"{episode}_Short.txt"
    if not txt_path.exists():
        return "FAIL", f"Không tìm thấy {txt_path}"
    final_script = txt_path.read_text(encoding="utf-8")

    topic_meta_path = cl_topic_meta_sidecar_path(episode, CL_TOPIC)
    if not topic_meta_path.exists():
        _gate_ledger_missing(episode, final_script, None, f"thiếu {topic_meta_path.name}")
        return "FACT_LEDGER_MISSING", (
            f"Không tìm thấy {topic_meta_path.name} -- episode này được sinh TRƯỚC bản vá claim-ledger "
            "(hoặc thiếu metadata do lỗi khác), không có source_file để tra ledger. "
            "KHÔNG chạy Phase A qua đường không-xác-minh -- cần backfill topic_meta sidecar thủ công "
            "(tra lại research draft gốc) trước khi episode này có thể publish như nội dung MỚI đã qua gate."
        )
    import json
    topic_meta = json.loads(topic_meta_path.read_text(encoding="utf-8"))
    source_file = topic_meta.get("source_file")
    claim_ledger_topic_id = cl_claim_ledger.topic_id_from_source_file(source_file) if source_file else ""
    if not claim_ledger_topic_id:
        _gate_ledger_missing(episode, final_script, topic_meta.get("excerpt"), f"{topic_meta_path.name} thiếu source_file hợp lệ")
        return "FACT_LEDGER_MISSING", f"{topic_meta_path.name} thiếu source_file hợp lệ -- không resolve được claim_ledger_topic_id."

    result = compute_phase_a_result(
        episode, topic_meta.get("title", episode), topic_meta.get("excerpt", ""), final_script,
        claim_ledger_topic_id=claim_ledger_topic_id,  # LUÔN truyền thật -- xem docstring đầu file
    )
    # S1: mọi outcome Phase A (kể cả C4 FAIL -- trước đây chỉ in ra màn hình)
    # có Quality record kèm script, đoạn trích, case_id, các câu bị chặn.
    gate = cqg.evaluate(content_quality_outcome(
        episode, result, script=final_script, excerpt=topic_meta.get("excerpt", ""),
        generator="run_cl_storytelling_phase_a", source_file=source_file,
    ))
    if not result.passed:
        status = "BLOCKED_FACT" if result.reason_code == "STORYTELLING_BLOCKED_FACT" else "FAIL"
        return status, f"{result.reason_code}: {result.evidence}"
    if not gate.publishable:
        return "FAIL", f"Content Quality Gate chưa cho qua ({gate.record_error or gate.decision.gate_status}) -- không ghi sidecar (fail closed)."
    # S7 ngay sau S1 (cùng điểm hội tụ): invariant của storytelling legacy chỉ có
    # đoạn trích (không có beat plan); không PASS thì không ghi sidecar Phase A.
    invariant = content_invariant.build(
        claim_source_kind="topic_excerpt", claim_source_data=topic_meta, source_excerpt=topic_meta.get("excerpt"),
        versions={"quality_record_id": gate.record["quality_record_id"]},
    )
    script_gate = sqg.evaluate_after_content_gate(gate, invariant=invariant)
    if not script_gate.publishable:
        return "FAIL", (f"Script Quality Gate chưa cho qua ({script_gate.record_error or script_gate.decision.reason_codes})"
                        " -- không ghi sidecar (fail closed).")

    sidecar_path = write_storytelling_sidecar(episode, result)
    return "PASS", f"topic_id={claim_ledger_topic_id} sidecar={sidecar_path}"


def _gate_ledger_missing(episode: str, script: str, excerpt, detail: str) -> None:
    cqg.evaluate(content_quality_outcome(
        episode, {"passed": False, "reason_code": "FACT_LEDGER_MISSING", "evidence": detail},
        script=script, excerpt=excerpt, generator="run_cl_storytelling_phase_a",
    ))


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", nargs="+", default=None, help="Chạy đúng các episode này (mặc định: tự dò MỌI episode chưa có sidecar)")
    args = ap.parse_args()

    episodes = args.episodes if args.episodes else discover_pending_storytelling_episodes()
    if not episodes:
        print("Không có episode STORYTELLING nào đang chờ Phase A.")
        return 0

    n_pass = n_blocked = n_missing = n_fail = n_skipped = 0
    for episode in episodes:
        status, detail = run_one(episode)
        print(f"[{episode}] {status}: {detail}")
        if status == "PASS":
            n_pass += 1
        elif status == "BLOCKED_FACT":
            n_blocked += 1
        elif status == "FACT_LEDGER_MISSING":
            n_missing += 1
        elif status == "SKIPPED_ALREADY_DONE":
            n_skipped += 1
        else:
            n_fail += 1

    print(f"\nHoàn tất: {n_pass} PASS, {n_blocked} BLOCKED_FACT, {n_missing} FACT_LEDGER_MISSING, {n_fail} FAIL, {n_skipped} SKIPPED_ALREADY_DONE (trên {len(episodes)} episode).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
