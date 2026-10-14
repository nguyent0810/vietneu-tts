"""C4 Round 6 (tích hợp production) -- test cho short_batch_runner.py's
_validate_provenance_binding(), cổng tiêu thụ (consumer) cho variant
"storytelling_provenance_v1". Mirror phong cách test_short_batch_runner_
cl_gate.py (seed sidecar THẬT trên đĩa qua tmp_path, không mock path
helper trực tiếp) để bài test gần với hành vi thật nhất."""
import json

import short_batch_runner as sbr
import cl_story_fact_pack as F
import cl_story_plan_and_generation as spg

CL_TOPIC = "Hình Sự"


def _pack(topic_id="T1", facts=None):
    return F.StoryFactPack(topic_id=topic_id, source_file=f"{topic_id}.md", excerpt_hash="h", ledger_version_at_build="v1", facts=facts or [])


def _seed_pack(monkeypatch, tmp_path, pack):
    monkeypatch.setattr(F, "STORY_FACT_PACK_DIR", tmp_path / "packs")
    F.save_fact_pack(pack)


def _seed_plan_and_binding(tmp_path, episode, plan_payload, binding_payload):
    shorts_dir = tmp_path / "drive_input" / "content_repo_staged" / CL_TOPIC / "Short"
    shorts_dir.mkdir(parents=True, exist_ok=True)
    (shorts_dir / f"{episode}_Short.story_plan.json").write_text(json.dumps(plan_payload, ensure_ascii=False), encoding="utf-8")
    (shorts_dir / f"{episode}_Short.script_binding.json").write_text(json.dumps(binding_payload, ensure_ascii=False), encoding="utf-8")
    return shorts_dir


def _wire_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(sbr, "cl_story_plan_sidecar_path", lambda ep, topic: tmp_path / "drive_input" / "content_repo_staged" / topic / "Short" / f"{ep}_Short.story_plan.json")
    monkeypatch.setattr(sbr, "cl_script_binding_sidecar_path", lambda ep, topic: tmp_path / "drive_input" / "content_repo_staged" / topic / "Short" / f"{ep}_Short.script_binding.json")


def _valid_setup(monkeypatch, tmp_path, episode="EP1"):
    fact = F.StoryFact(fact_id="F001", proposition="A xảy ra năm 1990.", source_spans=["A xảy ra năm 1990"])
    pack = _pack(topic_id="T1", facts=[fact])
    _seed_pack(monkeypatch, tmp_path, pack)
    bindings = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": "A đã xảy ra năm 1990.", "pack_hash_at_generation": pack.pack_hash()}]
    plan_payload = {"topic_id": "T1", "fact_pack_hash": pack.pack_hash(), "plan_hash": "planhash1", "segments": [{"segment_id": "S1", "role": "HOOK", "fact_ids": ["F001"]}]}
    binding_payload = {"script_hash": "x", "fact_pack_hash": pack.pack_hash(), "plan_hash": "planhash1", "bindings": bindings}
    _seed_plan_and_binding(tmp_path, episode, plan_payload, binding_payload)
    _wire_paths(monkeypatch, tmp_path)
    return pack, bindings


def test_missing_sidecars_fails_closed(tmp_path, monkeypatch):
    _wire_paths(monkeypatch, tmp_path)
    reason = sbr._validate_provenance_binding("EPX", CL_TOPIC, "A đã xảy ra năm 1990.")
    assert reason is not None
    assert "Thiếu sidecar" in reason


def test_valid_binding_passes(tmp_path, monkeypatch):
    pack, bindings = _valid_setup(monkeypatch, tmp_path)
    reason = sbr._validate_provenance_binding("EP1", CL_TOPIC, "A đã xảy ra năm 1990.")
    assert reason is None


def test_missing_fact_pack_on_disk_fails_closed(tmp_path, monkeypatch):
    pack, bindings = _valid_setup(monkeypatch, tmp_path)
    # Xoá fact pack khỏi đĩa (giả lập topic chưa từng có pack, hoặc bị xoá)
    import shutil
    shutil.rmtree(tmp_path / "packs", ignore_errors=True)
    reason = sbr._validate_provenance_binding("EP1", CL_TOPIC, "A đã xảy ra năm 1990.")
    assert reason is not None
    assert "Không tìm thấy Story Fact Pack" in reason


def test_stale_fact_pack_hash_fails_closed(tmp_path, monkeypatch):
    """Fact pack đã bị REBUILD (nội dung khác) kể từ lúc plan được tạo --
    pack_hash() tính lại KHÁC plan_data.fact_pack_hash đã ghi -- fail-closed."""
    fact = F.StoryFact(fact_id="F001", proposition="A xảy ra năm 1990.", source_spans=["A xảy ra năm 1990"])
    pack = _pack(topic_id="T1", facts=[fact])
    _seed_pack(monkeypatch, tmp_path, pack)
    bindings = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": "A đã xảy ra năm 1990.", "pack_hash_at_generation": pack.pack_hash()}]
    plan_payload = {"topic_id": "T1", "fact_pack_hash": "STALE_HASH_TU_LAN_BUILD_TRUOC", "plan_hash": "planhash1", "segments": [{"segment_id": "S1", "role": "HOOK", "fact_ids": ["F001"]}]}
    binding_payload = {"script_hash": "x", "fact_pack_hash": "STALE_HASH_TU_LAN_BUILD_TRUOC", "plan_hash": "planhash1", "bindings": bindings}
    _seed_plan_and_binding(tmp_path, "EP2", plan_payload, binding_payload)
    _wire_paths(monkeypatch, tmp_path)
    reason = sbr._validate_provenance_binding("EP2", CL_TOPIC, "A đã xảy ra năm 1990.")
    assert reason is not None
    assert "không khớp fact pack HIỆN TẠI" in reason


def test_copied_binding_from_another_topic_fails_closed(tmp_path, monkeypatch):
    """Mutation #12 THẬT (C4 Round 4/5): binding bị copy từ pack/topic khác
    -- pack_hash_at_generation của binding không khớp pack HIỆN TẠI đang
    được xét (dù fact_id trùng namespace)."""
    fact_a = F.StoryFact(fact_id="F001", proposition="A thuộc topic A.", source_spans=["A thuộc topic A"])
    pack_a = _pack(topic_id="TOPIC_A", facts=[fact_a])
    _seed_pack(monkeypatch, tmp_path, pack_a)
    fake_other_hash = "deadbeef0000"
    bindings = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": "B thuộc topic B.", "pack_hash_at_generation": fake_other_hash}]
    plan_payload = {"topic_id": "TOPIC_A", "fact_pack_hash": pack_a.pack_hash(), "plan_hash": "ph", "segments": [{"segment_id": "S1", "role": "HOOK", "fact_ids": ["F001"]}]}
    binding_payload = {"script_hash": "x", "fact_pack_hash": pack_a.pack_hash(), "plan_hash": "ph", "bindings": bindings}
    _seed_plan_and_binding(tmp_path, "EP3", plan_payload, binding_payload)
    _wire_paths(monkeypatch, tmp_path)
    reason = sbr._validate_provenance_binding("EP3", CL_TOPIC, "B thuộc topic B.")
    assert reason is not None


def test_modified_script_after_validation_fails_closed(tmp_path, monkeypatch):
    """Hạng mục rà đối kháng bắt buộc #8 ('modified script'): script text
    ĐANG publish khác với văn bản ghép từ bindings trên đĩa -- dù script
    'nghe hợp lý' và dù không đổi số liệu cụ thể nào, vẫn phải fail-closed
    vì đây KHÔNG PHẢI văn bản đã qua guard/drift thật."""
    pack, bindings = _valid_setup(monkeypatch, tmp_path)
    tampered_script = "Một câu HOÀN TOÀN khác, không phải văn bản đã qua Phase A."
    reason = sbr._validate_provenance_binding("EP1", CL_TOPIC, tampered_script)
    assert reason is not None
    assert "không khớp script đang publish" in reason


def test_numeric_tampering_after_validation_fails_closed(tmp_path, monkeypatch):
    """Biến thể cụ thể của #8: chỉ đổi 1 con số trong script SAU khi Phase A
    (guard/drift đã chạy trên bản GỐC) -- bindings trên đĩa vẫn ghi prose
    GỐC, nên joined_prose sẽ khác script_text đã bị sửa -- bắt được NGAY
    ở bước so khớp văn bản, không cần chạy lại numeric guard riêng."""
    pack, bindings = _valid_setup(monkeypatch, tmp_path)
    tampered_script = "A đã xảy ra năm 1995."  # đổi 1990 -> 1995 sau khi đã qua Phase A
    reason = sbr._validate_provenance_binding("EP1", CL_TOPIC, tampered_script)
    assert reason is not None


def test_foreign_fact_id_in_binding_fails_closed(tmp_path, monkeypatch):
    fact = F.StoryFact(fact_id="F001", proposition="A xảy ra năm 1990.", source_spans=["A xảy ra năm 1990"])
    pack = _pack(topic_id="T1", facts=[fact])
    _seed_pack(monkeypatch, tmp_path, pack)
    bindings = [{"segment_id": "S1", "fact_ids": ["F999"], "prose": "Nội dung bịa.", "pack_hash_at_generation": pack.pack_hash()}]
    plan_payload = {"topic_id": "T1", "fact_pack_hash": pack.pack_hash(), "plan_hash": "ph", "segments": [{"segment_id": "S1", "role": "HOOK", "fact_ids": ["F999"]}]}
    binding_payload = {"script_hash": "x", "fact_pack_hash": pack.pack_hash(), "plan_hash": "ph", "bindings": bindings}
    _seed_plan_and_binding(tmp_path, "EP4", plan_payload, binding_payload)
    _wire_paths(monkeypatch, tmp_path)
    reason = sbr._validate_provenance_binding("EP4", CL_TOPIC, "Nội dung bịa.")
    assert reason is not None
