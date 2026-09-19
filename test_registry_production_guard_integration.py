"""G1 (Video Generation remediation) -- test end-to-end qua
short_batch_runner.py/long_batch_runner.py's load_registry/save_registry/
save_registry_entry thật, xác nhận chúng dùng ĐÚNG các lớp bảo vệ mới của
registry_lock.py (không chỉ test registry_lock.py's primitives 1 mình, xem
test_registry_lock_safety.py).

AN TOÀN: mọi test ở đây monkeypatch CẢ _registry_path LẪN
_REGISTRY_PRODUCTION_ROOT sang cùng 1 cây tmp_path giả lập -- path trông
"giống" production (để guard coi nó là production) nhưng KHÔNG BAO GIỜ là
output/shorts hay output/long thật. Không test nào trong file này chạm tới
registry.json production thật."""
import json

import pytest

import registry_lock as rl
import short_batch_runner as sbr
import long_batch_runner as lbr


# ─── short_batch_runner.py ──────────────────────────────────────────────

def test_short_save_registry_blocked_when_unmarked_and_path_looks_like_production(tmp_path, monkeypatch):
    """Mô phỏng CHÍNH XÁC kịch bản bug thật đã xảy ra: 1 script (ở đây là
    test này, đóng vai 'ad-hoc script') import save_registry() rồi gọi
    thẳng, KHÔNG đi qua main() (nên không có mark_production_entry()).
    _registry_path() BỊ monkeypatch (bắt buộc, để không đụng path thật) --
    nhưng trỏ vào 1 cây tmp_path mà guard vẫn coi là 'production' vì
    _REGISTRY_PRODUCTION_ROOT CŨNG được monkeypatch xuống ĐÚNG cây
    tmp_path đó (thay vì cây output/shorts thật) -- mô phỏng cấu trúc
    "path nằm trong production_root" một cách an toàn, KHÔNG BAO GIỜ trỏ
    production_root vào path thật. Codex review G1 vòng 1 (nit): docstring
    bản trước ghi nhầm là _registry_path() không bị monkeypatch -- đã sửa."""
    fake_root = tmp_path / "output" / "shorts"
    fake_path = fake_root / "Test Topic" / "registry.json"
    monkeypatch.setattr(sbr, "_REGISTRY_PRODUCTION_ROOT", fake_root)
    monkeypatch.setattr(sbr, "_registry_path", lambda topic: fake_path)
    monkeypatch.delenv(rl._PRODUCTION_ENTRY_ENV, raising=False)

    with pytest.raises(rl.RegistryWriteBlocked):
        sbr.save_registry({"k": {"status": "uploaded"}}, topic="Test Topic")
    assert not fake_path.exists(), "the exact real-world incident: must be blocked BEFORE any write happens"


def test_short_save_registry_entry_blocked_when_unmarked(tmp_path, monkeypatch):
    fake_root = tmp_path / "output" / "shorts"
    fake_path = fake_root / "Test Topic" / "registry.json"
    monkeypatch.setattr(sbr, "_REGISTRY_PRODUCTION_ROOT", fake_root)
    monkeypatch.setattr(sbr, "_registry_path", lambda topic: fake_path)
    monkeypatch.delenv(rl._PRODUCTION_ENTRY_ENV, raising=False)

    with pytest.raises(rl.RegistryWriteBlocked):
        sbr.save_registry_entry("k1", {"status": "uploaded"}, topic="Test Topic")
    assert not fake_path.exists()


def test_short_save_registry_allowed_when_mark_production_entry_called(tmp_path, monkeypatch):
    """Đúng luồng THẬT của main(): mark_production_entry() được gọi trước,
    rồi save_registry() phải thành công."""
    fake_root = tmp_path / "output" / "shorts"
    fake_path = fake_root / "Test Topic" / "registry.json"
    monkeypatch.setattr(sbr, "_REGISTRY_PRODUCTION_ROOT", fake_root)
    monkeypatch.setattr(sbr, "_registry_path", lambda topic: fake_path)
    monkeypatch.delenv(rl._PRODUCTION_ENTRY_ENV, raising=False)

    rl.mark_production_entry()  # exactly what main()'s first line does
    sbr.save_registry({"k": {"status": "uploaded"}}, topic="Test Topic")
    assert fake_path.exists()
    assert json.loads(fake_path.read_text(encoding="utf-8")) == {"k": {"status": "uploaded"}}


def test_short_load_registry_recovers_corrupt_file_from_backup(tmp_path, monkeypatch):
    fake_root = tmp_path / "output" / "shorts"
    fake_path = fake_root / "Test Topic" / "registry.json"
    monkeypatch.setattr(sbr, "_REGISTRY_PRODUCTION_ROOT", fake_root)
    monkeypatch.setattr(sbr, "_registry_path", lambda topic: fake_path)
    rl.mark_production_entry()

    sbr.save_registry({"k": {"status": "uploaded"}}, topic="Test Topic")
    sbr.save_registry_entry("k2", {"status": "video_ready"}, topic="Test Topic")  # rotates a valid backup
    fake_path.write_text("{{{ corrupted", encoding="utf-8")

    recovered = sbr.load_registry(topic="Test Topic")
    assert recovered == {"k": {"status": "uploaded"}}, "must recover from the last valid backup, not crash or lose data"


def test_short_load_registry_still_returns_empty_dict_for_missing_file(tmp_path, monkeypatch):
    """Regression: hành vi CŨ (file không tồn tại -> {}) không được đổi."""
    fake_path = tmp_path / "output" / "shorts" / "Test" / "registry.json"
    monkeypatch.setattr(sbr, "_registry_path", lambda topic: fake_path)
    assert sbr.load_registry(topic="Test") == {}


# ─── long_batch_runner.py (cùng cơ chế, kiểm tra không bị lệch giữa 2 file) ─

def test_long_save_registry_blocked_when_unmarked(tmp_path, monkeypatch):
    fake_root = tmp_path / "output" / "long"
    fake_path = fake_root / "Test Topic" / "registry.json"
    monkeypatch.setattr(lbr, "_REGISTRY_PRODUCTION_ROOT", fake_root)
    monkeypatch.setattr(lbr, "_registry_path", lambda topic: fake_path)
    monkeypatch.delenv(rl._PRODUCTION_ENTRY_ENV, raising=False)

    with pytest.raises(rl.RegistryWriteBlocked):
        lbr.save_registry({"EP001": {"status": "assets_ready"}}, "Test Topic")
    assert not fake_path.exists()


def test_long_save_registry_allowed_when_marked(tmp_path, monkeypatch):
    fake_root = tmp_path / "output" / "long"
    fake_path = fake_root / "Test Topic" / "registry.json"
    monkeypatch.setattr(lbr, "_REGISTRY_PRODUCTION_ROOT", fake_root)
    monkeypatch.setattr(lbr, "_registry_path", lambda topic: fake_path)
    rl.mark_production_entry()

    lbr.save_registry({"EP001": {"status": "assets_ready"}}, "Test Topic")
    assert fake_path.exists()
    assert json.loads(fake_path.read_text(encoding="utf-8")) == {"EP001": {"status": "assets_ready"}}


def test_long_load_registry_recovers_from_backup(tmp_path, monkeypatch):
    fake_root = tmp_path / "output" / "long"
    fake_path = fake_root / "Test Topic" / "registry.json"
    monkeypatch.setattr(lbr, "_REGISTRY_PRODUCTION_ROOT", fake_root)
    monkeypatch.setattr(lbr, "_registry_path", lambda topic: fake_path)
    rl.mark_production_entry()

    lbr.save_registry({"EP001": {"status": "assets_ready"}}, "Test Topic")
    lbr.save_registry({"EP001": {"status": "assets_ready"}, "EP002": {"status": "video_ready"}}, "Test Topic")
    fake_path.write_text("not json at all", encoding="utf-8")

    recovered = lbr.load_registry("Test Topic")
    assert recovered == {"EP001": {"status": "assets_ready"}}


# ─── existing conventions must keep working unmodified ──────────────────

def test_existing_monkeypatch_convention_still_works_without_touching_production_root(tmp_path, monkeypatch):
    """Hầu hết test HIỆN CÓ (vd test_short_batch_runner_bgm.py) chỉ
    monkeypatch _registry_path sang tmp_path, KHÔNG đụng
    _REGISTRY_PRODUCTION_ROOT và KHÔNG gọi mark_production_entry(). Path đó
    không nằm trong cây production THẬT (PROJECT_ROOT/output/shorts) nên
    guard phải tự động cho qua -- xác nhận G1 không phá test hiện có."""
    registry_path = tmp_path / "registry.json"
    monkeypatch.setattr(sbr, "_registry_path", lambda t: registry_path)
    monkeypatch.delenv(rl._PRODUCTION_ENTRY_ENV, raising=False)

    sbr.save_registry({"k": {"status": "uploaded"}}, topic="anything")
    assert registry_path.exists()
    assert sbr.load_registry(topic="anything") == {"k": {"status": "uploaded"}}


def test_real_production_root_constants_point_at_real_output_dirs():
    """Sanity xác nhận hằng số _REGISTRY_PRODUCTION_ROOT khớp đúng cây thật
    (không phải kiểm tra ghi -- chỉ kiểm tra path, không I/O)."""
    assert sbr._REGISTRY_PRODUCTION_ROOT == sbr.PROJECT_ROOT / "output" / "shorts"
    assert lbr._REGISTRY_PRODUCTION_ROOT == lbr.PROJECT_ROOT / "output" / "long"
