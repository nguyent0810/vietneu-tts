"""Tiện ích CHỈ dùng trong test: dựng một registry entry đã qua Content
Quality Gate (S1) đúng như luồng thật -- có Quality record PASS trong kho
(thư mục tạm của test) khớp đúng final_script -- cả tầng Content (S1) lẫn
tầng Script (S7) -- không chỉ gắn nhãn "pass"."""
import content_quality_gate as cqg
import script_quality_gate as sqg


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
    script_gate = sqg.evaluate_after_content_gate(gate, invariant=None)
    assert script_gate.publishable, (script_gate.record_error, script_gate.decision.reason_codes)
    entry["script_gate_status"] = cqg.PASS
    entry["script_quality_record_id"] = script_gate.record["quality_record_id"]
    return entry
