"""Sinh nội dung Short "Án đã xử / Kiến thức luật hình sự" kênh Hình Sự (CL)
qua kiến trúc PROVENANCE-PRESERVING (C4 Repair Round 4/5, tích hợp production
ở Round 6) -- thay thế con đường free-form + judge-panel của criminal_law_
short_generator.py bằng: Story Fact Pack -> Story Plan -> bound generation
-> guard/drift hẹp -> claim-ledger -> SEO -> person-check, TẤT CẢ trong 1
lượt chạy (giống cl_case_batch.py's mô hình "generate rồi Phase A NGAY, ghi
sidecar 1 lần" -- KHÁC 2-bước-tách-rời của criminal_law_short_generator.py +
run_cl_storytelling_phase_a.py). Vì Phase A chạy NGAY tại đây trước khi ghi
`.cl_meta.json`, run_cl_storytelling_phase_a.py's discover_pending_
storytelling_episodes() (lọc episode CHƯA có sidecar) tự động bỏ qua episode
sinh từ đường này -- KHÔNG cần sửa gì ở run_cl_storytelling_phase_a.py.

TÁI DÙNG topic bank THẬT của criminal_law_short_generator.py (cùng file
cache, cùng cơ chế "đã dùng") -- KHÔNG tạo topic bank song song, tránh 2
generator vô tình chọn trùng 1 chủ đề."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import criminal_law_short_generator as legacy_gen  # noqa: E402 -- tái dùng topic bank THẬT, không tạo bank song song
import cl_claim_ledger  # noqa: E402
from criminal_law_storytelling_phase_a import (  # noqa: E402
    compute_phase_a_result_provenance, write_storytelling_sidecar, write_provenance_sidecars, CL_TOPIC,
)
from short_segment_discovery import cl_topic_meta_sidecar_path  # noqa: E402

OUTPUT_DIR = legacy_gen.OUTPUT_DIR


def _slug_episode(title: str) -> str:
    import re
    slug = re.sub(r"[^a-zA-Z0-9]+", "", title)[:30] or "ChuDe"
    episode = f"ANDAXU_{slug}"
    n = 1
    while (OUTPUT_DIR / f"{episode}_Short.txt").exists():
        n += 1
        episode = f"ANDAXU_{slug}_{n}"
    return episode


def write_topic_meta_sidecar(episode: str, topic: dict) -> Path:
    """CÙNG schema {title, source_file, excerpt} với criminal_law_short_
    generator.py's write_topic_meta_sidecar() -- giữ 1 quy ước đọc DUY
    NHẤT cho MỌI tool khác đọc topic_meta.json bất kể variant nào đã sinh
    ra episode (audit/backfill/health-check)."""
    import json, uuid, os
    sidecar_path = cl_topic_meta_sidecar_path(episode, CL_TOPIC)
    sidecar = {"title": topic["title"], "source_file": topic["source_file"], "excerpt": topic["excerpt"]}
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = sidecar_path.with_suffix(sidecar_path.suffix + f".tmp{uuid.uuid4().hex[:8]}")
    tmp_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp_path, sidecar_path)
    return sidecar_path


def run_one(topic: dict) -> tuple:
    """Chạy TOÀN BỘ provenance pipeline cho 1 topic {title, excerpt,
    source_file} (từ next_unused_topic()) -- trả (status, detail).
    status ∈ {"PASS", "BLOCKED_FACT", "FAIL"}. Ghi sidecar CHỈ khi PASS
    (đúng nguyên tắc 'existing output not destroyed' -- topic vẫn giữ
    trạng thái CHƯA DÙNG nếu fail, có thể thử lại sau)."""
    topic_id = cl_claim_ledger.topic_id_from_source_file(topic["source_file"])
    if not topic_id:
        return "FAIL", f"Không resolve được topic_id từ source_file={topic['source_file']!r}."

    episode = _slug_episode(topic["title"])
    result, script_text, plan, bindings = compute_phase_a_result_provenance(
        episode, topic_id, topic["source_file"], topic["excerpt"],
    )
    if not result.passed:
        status = "BLOCKED_FACT" if result.reason_code == "STORYTELLING_BLOCKED_FACT" else "FAIL"
        return status, f"{result.reason_code}: {result.evidence}"

    txt_path, plan_path, binding_path = write_provenance_sidecars(episode, result, script_text, plan, bindings)
    write_topic_meta_sidecar(episode, topic)
    sidecar_path = write_storytelling_sidecar(episode, result)
    return "PASS", f"topic_id={topic_id} txt={txt_path} sidecar={sidecar_path} plan={plan_path} binding={binding_path}"


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild-bank", action="store_true", help="Trích lại toàn bộ topic bank từ SOURCES (bỏ qua cache) -- CÙNG bank với criminal_law_short_generator.py")
    args = ap.parse_args()

    if args.rebuild_bank:
        legacy_gen.build_full_topic_bank(force_refresh=True)

    topic = legacy_gen.next_unused_topic()
    if topic is None:
        print("DỪNG: hết chủ đề AN TOÀN trong topic bank -- cần --rebuild-bank hoặc SOURCES có thêm research draft mới.", file=sys.stderr)
        return 1

    print(f"Chủ đề: {topic['title']} (nguồn: {topic['source_file']})", flush=True)
    status, detail = run_one(topic)
    print(f"{status}: {detail}")
    if status != "PASS":
        print("DỪNG: không ghi file Short -- topic vẫn giữ trạng thái CHƯA DÙNG để thử lại.", file=sys.stderr)
        return 1

    legacy_gen.mark_topic_used(topic["title"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
