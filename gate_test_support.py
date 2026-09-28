"""Tiện ích CHỈ dùng trong test: dựng một registry entry đã qua Content
Quality Gate (S1) đúng như luồng thật -- có Quality record PASS trong kho
(thư mục tạm của test) khớp đúng final_script, không chỉ gắn nhãn "pass"."""
import content_quality_gate as cqg


def stamp_content_gate_pass(entry: dict, domain: str) -> dict:
    script = entry["final_script"]
    gate = cqg.evaluate(cqg.SourceOutcome(
        source=cqg.SOURCE_RUNNER_STAGED, domain=domain,
        raw={"record": {"gate_status": cqg.PASS, "script": script, "quality_record_id": "seed"}, "script": script},
        content_id=entry.get("key"),
    ))
    assert gate.publishable, gate.record_error
    entry["content_gate_status"] = cqg.PASS
    entry["quality_record_id"] = gate.record["quality_record_id"]
    return entry
