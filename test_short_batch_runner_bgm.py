"""Test tự động cho phần BGM của short_batch_runner.py (audit 9 điểm mục
#4, Codex review vòng 2) -- resolve_bgm_for_attribution() (fallback logic
cho legacy entry) và save_registry_entry() (lưu trung gian không ghi đè
snapshot cũ của entry khác)."""
import json

import short_batch_runner as sbr
import bgm_tracks


def test_resolve_bgm_for_attribution_uses_stored_bgm_when_present():
    entry = {"bgm": {"path": "/x/y.mp3", "attribution": "Nhạc nền: Y"}}
    result = sbr.resolve_bgm_for_attribution(entry, "Hình Sự")
    assert result == entry["bgm"]


def test_resolve_bgm_for_attribution_legacy_fallback_for_bud_fs():
    """Entry cũ (trước migration) thiếu 'bgm' -- BUD/FS PHẢI fallback về
    track đầu tiên (track duy nhất từng tồn tại lúc đó)."""
    entry_bud = {}
    result = sbr.resolve_bgm_for_attribution(entry_bud, "Phật giáo")
    assert result is not None
    assert result["path"].name == "meditation_impromptu_01.mp3"

    entry_fs = {}
    result = sbr.resolve_bgm_for_attribution(entry_fs, "Phong Thủy")
    assert result is not None
    assert result["path"].name == "asian_drums.mp3"


def test_resolve_bgm_for_attribution_no_fallback_for_cl():
    """BUG THẬT phát hiện qua Codex CLI review: entry CL cũ (trước khi CL
    có track nào) thiếu 'bgm' -- KHÔNG được fallback (video đó thật sự
    không có BGM, gán attribution sẽ sai nguồn CC BY 4.0 + sai thực tế)."""
    entry_cl = {}
    result = sbr.resolve_bgm_for_attribution(entry_cl, "Hình Sự")
    assert result is None


def test_resolve_bgm_for_attribution_unconfigured_topic_no_fallback():
    entry = {}
    result = sbr.resolve_bgm_for_attribution(entry, "Chủ đề chưa từng cấu hình")
    assert result is None


def test_save_registry_entry_does_not_clobber_other_keys_updated_concurrently(tmp_path, monkeypatch):
    """Codex review vòng 2 mục 4: mô phỏng tiến trình A load batch (registry
    trong bộ nhớ chứa key B với giá trị CŨ), sau đó tiến trình B cập nhật
    key B trên đĩa (giá trị MỚI). Tiến trình A gọi save_registry_entry()
    cho key A -- key B trên đĩa PHẢI GIỮ NGUYÊN giá trị MỚI của tiến trình
    B, không bị ghi đè bởi bản CŨ mà tiến trình A vẫn giữ trong bộ nhớ."""
    topic = "Test Topic"
    registry_path = tmp_path / "registry.json"
    monkeypatch.setattr(sbr, "_registry_path", lambda t: registry_path)

    # Trạng thái ban đầu: cả A và B đều "seed_v1" khi tiến trình A load batch.
    registry_path.write_text(json.dumps({
        "key_a": {"status": "seed_v1"},
        "key_b": {"status": "seed_v1"},
    }), encoding="utf-8")

    # Tiến trình A "load" registry vào bộ nhớ (snapshot cũ, không dùng ở đây
    # vì save_registry_entry() không nhận snapshot -- đúng điểm khác biệt
    # với save_registry()).

    # Tiến trình B cập nhật key_b trên đĩa (mới hơn snapshot của A).
    on_disk = json.loads(registry_path.read_text(encoding="utf-8"))
    on_disk["key_b"] = {"status": "updated_by_process_B"}
    registry_path.write_text(json.dumps(on_disk), encoding="utf-8")

    # Tiến trình A giờ lưu key_a (dùng save_registry_entry(), KHÔNG merge
    # snapshot cũ của key_b trong bộ nhớ).
    sbr.save_registry_entry("key_a", {"status": "updated_by_process_A"}, topic)

    final = json.loads(registry_path.read_text(encoding="utf-8"))
    assert final["key_a"]["status"] == "updated_by_process_A"
    assert final["key_b"]["status"] == "updated_by_process_B", (
        "save_registry_entry() đã ghi đè cập nhật của tiến trình khác -- BUG."
    )


def test_save_registry_merge_would_clobber_other_key_demonstrating_the_risk(tmp_path, monkeypatch):
    """Đối chứng: chứng minh save_registry() (merge CẢ snapshot bộ nhớ) THẬT
    SỰ ghi đè key khác nếu snapshot cũ -- đây CHÍNH LÀ rủi ro Codex chỉ ra,
    lý do save_registry_entry() cần tồn tại riêng cho lần lưu trung gian."""
    topic = "Test Topic"
    registry_path = tmp_path / "registry.json"
    monkeypatch.setattr(sbr, "_registry_path", lambda t: registry_path)

    registry_path.write_text(json.dumps({
        "key_a": {"status": "seed_v1"},
        "key_b": {"status": "seed_v1"},
    }), encoding="utf-8")

    # Snapshot trong bộ nhớ của tiến trình A (đọc lúc load batch, TRƯỚC khi B cập nhật).
    in_memory_registry = json.loads(registry_path.read_text(encoding="utf-8"))

    # Tiến trình B cập nhật key_b trên đĩa.
    on_disk = json.loads(registry_path.read_text(encoding="utf-8"))
    on_disk["key_b"] = {"status": "updated_by_process_B"}
    registry_path.write_text(json.dumps(on_disk), encoding="utf-8")

    # Tiến trình A dùng save_registry() (merge snapshot CŨ) -- key_b bị ghi đè lại "seed_v1".
    in_memory_registry["key_a"] = {"status": "updated_by_process_A"}
    sbr.save_registry(in_memory_registry, topic)

    final = json.loads(registry_path.read_text(encoding="utf-8"))
    assert final["key_b"]["status"] == "seed_v1", (
        "Nếu assert này FAIL, nghĩa là save_registry() KHÔNG còn bug ghi đè -- "
        "cập nhật lại docstring/test này cho khớp hành vi mới."
    )


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
