"""Test cho gap thật được xác nhận khi rà soát Gate 2 design §1.15 trước
khi xây CL Risk Gate: `creator_specs/CL_REAL_PERSONS_v1.json` (ledger người
thật CL đã duyệt) trước đây CHỈ được đối chiếu bởi
test_manifest_names_all_covered_by_aliases (kiểm tra CI-time), không hề
feed runtime -- resolve_symbol() chỉ đọc alias TĨNH viết tay trong
domain_creative_profiles.json. Nghĩa là 1 content_id CL mới khai báo tên
người thật vào ledger nhưng con người QUÊN chép tay alias sang JSON kia
(và quên chạy test trước khi duyệt) sẽ KHÔNG được resolve_symbol() bảo vệ
tại runtime thật -- silently tái tạo đúng lỗ hổng cơ chế này sinh ra để
chặn. Test này xác nhận bản vá: load_profile("CL") giờ tự động hợp nhất
MỌI name_form từ ledger vào symbol_library's aliases, và resolve_symbol()
giờ so khớp lookaround-based + NFC/casefold-normalized (không còn substring
thô, không còn \\b thô) -- cả 2 thay đổi đã xác nhận KHÔNG làm hỏng 21 test
hiện có trong test_cl_real_person_safety.py + test_cl_video_collapse_fix.py
(chạy lại nguyên vẹn, không sửa dòng nào).

Vòng review Codex CLI thật (round 1, NEEDS_REVISION) phát hiện 2 lỗi thật
trong bản vá đầu tiên, ĐÃ SỬA và test lại ở đây:
1. High: ledger thiếu/hỏng trước đây fail-SOFT (cảnh báo + tiếp tục dùng
   alias tĩnh) -- với 1 người CHỈ có trong ledger (không có alias tĩnh
   trùng), điều đó có nghĩa MẤT HOÀN TOÀN chặn an toàn, âm thầm. Sửa:
   fail-CLOSED -- CLRealPersonsLedgerError raise, không bắt, không tiếp
   tục xử lý CL khi ledger không đọc/parse/đúng schema được.
2. High: `\\b...\\b` có false-negative thật với alias kết thúc bằng ký tự
   không phải \\w (vd "O.J." -- dấu chấm cuối khiến \\b không kích hoạt
   trước 1 dấu cách theo sau). Sửa: lookaround `(?<!\\w)...(?!\\w)` +
   chuẩn hoá NFC/casefold thay vì .lower() thô."""
import json
from pathlib import Path

import pytest

import domain_creative_profiles as cp

SAFE_SYMBOL_KEYS = {"phap_luat_can_can_cong_ly", "phap_luat_toa_an"}


def _write_ledger(tmp_path: Path, data) -> Path:
    p = tmp_path / "CL_REAL_PERSONS_v1.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return p


# ─── ledger-derived aliases actually protect at runtime ────────────────

def test_ledger_only_name_gets_dynamically_routed_to_safe_symbol(tmp_path, monkeypatch):
    """Tên CHỈ có trong ledger (chưa từng được chép tay vào
    domain_creative_profiles.json) vẫn phải được resolve_symbol() bảo vệ
    -- đây là gap thật §1.15 xác nhận, và là lý do fix này tồn tại."""
    fake_ledger = _write_ledger(tmp_path, {
        "CL_D99_fake_case_for_test": ["trần thị bích ngọc", "bích ngọc"],
    })
    monkeypatch.setattr(cp, "CL_REAL_PERSONS_LEDGER_FILE", fake_ledger)

    profile = cp.load_profile("CL")
    entry = cp.resolve_symbol(profile, "bị cáo Trần Thị Bích Ngọc bị tuyên án hôm nay")
    assert entry is not None, "tên chỉ khai báo trong ledger (chưa có alias tĩnh) vẫn phải khớp symbol an toàn"
    assert entry["key"] in SAFE_SYMBOL_KEYS

    entry2 = cp.resolve_symbol(profile, "sau đó Bích Ngọc kháng cáo")
    assert entry2 is not None, "dạng rút gọn của tên ledger-only cũng phải khớp"
    assert entry2["key"] in SAFE_SYMBOL_KEYS


def test_ledger_merge_is_cl_only_does_not_leak_to_other_domains(tmp_path, monkeypatch):
    fake_ledger = _write_ledger(tmp_path, {
        "CL_D99_fake_case_for_test": ["trần thị bích ngọc"],
    })
    monkeypatch.setattr(cp, "CL_REAL_PERSONS_LEDGER_FILE", fake_ledger)

    for domain_id in ("BUD", "FS"):
        profile = cp.load_profile(domain_id)
        entry = cp.resolve_symbol(profile, "Trần Thị Bích Ngọc")
        assert entry is None, f"alias CL từ ledger không được lọt sang domain {domain_id}"


def test_empty_but_valid_ledger_is_not_an_error(tmp_path, monkeypatch):
    """Ledger RỖNG nhưng HỢP LỆ (mọi content_id đã rà soát, xác nhận không
    có người thật -- trạng thái THẬT của CL_D2/CL_D7 hôm nay) KHÔNG được
    coi là lỗi -- khác hẳn "không đọc được"/"sai schema"."""
    fake_ledger = _write_ledger(tmp_path, {"CL_D2_luat1_an_treo": [], "_comment": "note"})
    monkeypatch.setattr(cp, "CL_REAL_PERSONS_LEDGER_FILE", fake_ledger)
    profile = cp.load_profile("CL")  # must not raise
    # alias tĩnh có sẵn vẫn hoạt động bình thường
    entry = cp.resolve_symbol(profile, "Lê Văn Luyện, sinh năm 1993")
    assert entry is not None and entry["key"] in SAFE_SYMBOL_KEYS


# ─── fail-closed on a broken/malformed ledger (Codex round 1, High #1) ──

def test_missing_ledger_file_fails_closed(tmp_path, monkeypatch):
    """File ledger không tồn tại -- PHẢI raise (fail-closed), KHÔNG được
    âm thầm rơi về "chỉ dùng alias tĩnh" -- 1 người CHỈ khai báo trong
    ledger sẽ mất chặn hoàn toàn nếu lỗi này bị nuốt."""
    monkeypatch.setattr(cp, "CL_REAL_PERSONS_LEDGER_FILE", tmp_path / "does_not_exist.json")
    with pytest.raises(cp.CLRealPersonsLedgerError):
        cp.load_profile("CL")


def test_malformed_json_ledger_fails_closed(tmp_path, monkeypatch):
    bad = _write_ledger(tmp_path, "placeholder")
    bad.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(cp, "CL_REAL_PERSONS_LEDGER_FILE", bad)
    with pytest.raises(cp.CLRealPersonsLedgerError):
        cp.load_profile("CL")


def test_non_object_top_level_ledger_fails_closed(tmp_path, monkeypatch):
    fake_ledger = _write_ledger(tmp_path, ["not", "an", "object"])
    monkeypatch.setattr(cp, "CL_REAL_PERSONS_LEDGER_FILE", fake_ledger)
    with pytest.raises(cp.CLRealPersonsLedgerError):
        cp.load_profile("CL")


def test_wrong_type_content_id_value_fails_closed(tmp_path, monkeypatch):
    """1 content_id trỏ tới 1 chuỗi thay vì 1 list -- trước đây bị ÂM THẦM
    BỎ QUA (Codex round 1, Medium #1 trong finding High #1's danh sách) --
    giờ PHẢI raise."""
    fake_ledger = _write_ledger(tmp_path, {"CL_D99": "not a list"})
    monkeypatch.setattr(cp, "CL_REAL_PERSONS_LEDGER_FILE", fake_ledger)
    with pytest.raises(cp.CLRealPersonsLedgerError):
        cp.load_profile("CL")


def test_empty_string_name_form_fails_closed(tmp_path, monkeypatch):
    fake_ledger = _write_ledger(tmp_path, {"CL_D99": ["   "]})
    monkeypatch.setattr(cp, "CL_REAL_PERSONS_LEDGER_FILE", fake_ledger)
    with pytest.raises(cp.CLRealPersonsLedgerError):
        cp.load_profile("CL")


def test_ledger_names_with_no_safety_critical_entry_fails_closed(monkeypatch):
    """Codex round 2 (High, phát hiện thật sau khi round 1 được sửa):
    ledger CÓ tên nhưng profile CL bị hỏng/sửa nhầm KHÔNG còn entry
    safety_critical nào -- trước đây hàm gộp ÂM THẦM trả profile không đổi
    (không route đi đâu), khiến resolve_symbol() trả None cho 1 tên đã
    khai báo trong ledger dù load_profile("CL") "thành công". Giờ phải
    raise thay vì trả về 1 profile trông có vẻ hợp lệ nhưng KHÔNG bảo vệ
    được ledger names nào."""
    monkeypatch.setattr(cp, "_load_cl_ledger_name_forms", lambda: ["Ledger Only"])
    broken_profile = {"symbol_library": []}  # không còn entry safety_critical nào
    with pytest.raises(cp.CLRealPersonsLedgerError):
        cp._merge_ledger_aliases_into_cl_profile(broken_profile)


def test_ledger_error_does_not_affect_other_domains(tmp_path, monkeypatch):
    """Fail-closed CHỈ áp dụng cho CL -- FS/BUD load_profile() vẫn hoạt
    động bình thường dù ledger CL đang hỏng (đúng khẳng định Codex round 1:
    ledger chỉ được đọc khi resolved_id=="CL")."""
    monkeypatch.setattr(cp, "CL_REAL_PERSONS_LEDGER_FILE", tmp_path / "does_not_exist.json")
    for domain_id in ("FS", "BUD"):
        profile = cp.load_profile(domain_id)  # must not raise
        assert isinstance(profile, dict) and profile, f"load_profile({domain_id!r}) phải hoạt động bình thường dù ledger CL hỏng"


# ─── lookaround matching: fixes real \b false-negative (Codex round 1, High #2) ──

def test_word_boundary_prevents_prefix_substring_false_positive():
    isolated_profile = {
        "symbol_library": [{"key": "phap_luat_can_can_cong_ly", "aliases": ["cam"]}]
    }
    assert cp.resolve_symbol(isolated_profile, "chiếc camera an ninh ghi lại toàn bộ") is None
    assert cp.resolve_symbol(isolated_profile, "Năm Cam bị bắt giữ") is not None


def test_word_boundary_distinguishes_an_from_anh():
    isolated_profile = {
        "symbol_library": [{"key": "phap_luat_can_can_cong_ly", "aliases": ["trần văn an"]}]
    }
    assert cp.resolve_symbol(isolated_profile, "nghi phạm Trần Văn An bị khởi tố") is not None
    assert cp.resolve_symbol(isolated_profile, "nhân chứng Trần Văn Anh được mời") is None


def test_alias_ending_in_punctuation_still_matches():
    """Regression thật từ Codex round 1: alias "O.J." (kết thúc bằng dấu
    chấm, không phải \\w) KHÔNG khớp với \\b...\\b (bản vá vòng 1) vì \\b
    đòi hỏi chuyển tiếp word<->non-word ngay tại biên -- dấu chấm (non-word)
    theo sau bởi dấu cách (cũng non-word) không tạo \\b nào. Lookaround chỉ
    đòi hỏi ký tự NGAY SAU alias không phải \\w -- khớp đúng."""
    isolated_profile = {
        "symbol_library": [{"key": "phap_luat_can_can_cong_ly", "aliases": ["O.J."]}]
    }
    assert cp.resolve_symbol(isolated_profile, "O.J. bị bắt") is not None
    assert cp.resolve_symbol(isolated_profile, "hôm nay O.J. ra toà") is not None


def test_alias_with_hash_prefix_still_matches():
    isolated_profile = {
        "symbol_library": [{"key": "phap_luat_can_can_cong_ly", "aliases": ["#abc"]}]
    }
    assert cp.resolve_symbol(isolated_profile, "#abc bị bắt") is not None


def test_nfc_nfd_unicode_forms_both_match():
    """Chữ có dấu tiếng Việt có thể mã hoá NFC (1 code point, vd "ọ" =
    U+1ECD) hoặc NFD (chữ cái + dấu kết hợp riêng, vd "o" + U+0323 + U+0301)
    -- 2 dạng NHÌN GIỐNG HỆT NHAU nhưng so sánh chuỗi thô KHÔNG khớp nếu 2
    bên khác dạng. resolve_symbol() phải khớp cả 2 dạng qua NFC
    normalization (Codex round 1 khuyến nghị)."""
    import unicodedata
    alias_nfc = "trần thị bích ngọc"
    alias_nfd = unicodedata.normalize("NFD", alias_nfc)
    assert alias_nfc != alias_nfd, "sanity check: NFC và NFD phải khác nhau ở mức chuỗi thô"

    isolated_profile = {
        "symbol_library": [{"key": "phap_luat_can_can_cong_ly", "aliases": [alias_nfd]}]
    }
    # text ở dạng NFC, alias cấu hình ở dạng NFD -- vẫn phải khớp
    text_nfc = "bị cáo Trần Thị Bích Ngọc bị tuyên án"
    assert cp.resolve_symbol(isolated_profile, text_nfc) is not None


# ─── no duplication after merge ─────────────────────────────────────────

def test_ledger_merge_does_not_duplicate_already_static_aliases():
    """Toàn bộ name_form thật trong CL_REAL_PERSONS_v1.json hôm nay đã
    trùng với alias tĩnh có sẵn trong domain_creative_profiles.json (xác
    nhận trực tiếp) -- hợp nhất không được tạo bản sao, và không được đổi
    hành vi của bộ 21 test hiện có (real_person_safety + video_collapse_fix,
    chạy riêng để xác nhận, xem test 2 file đó)."""
    profile = cp.load_profile("CL")
    target = next(e for e in profile["symbol_library"] if e["key"] == "phap_luat_can_can_cong_ly")
    aliases_lower = [a.lower() for a in target["aliases"]]
    assert len(aliases_lower) == len(set(aliases_lower)), (
        f"alias list chứa bản sao sau khi hợp nhất ledger: {target['aliases']}"
    )


def test_ledger_merge_targets_stable_key_not_list_order(tmp_path, monkeypatch):
    """Codex round 1: gộp phải nhắm ĐÚNG key ổn định
    (CL_LEDGER_ALIAS_TARGET_KEY), không phụ thuộc thứ tự list -- xác nhận
    trực tiếp bằng 1 ledger giả lập có kiểm soát (không phụ thuộc dữ liệu
    production thật) và đảo thứ tự 2 entry safety_critical trong profile,
    kiểm tra alias ledger-only vẫn vào ĐÚNG entry phap_luat_can_can_cong_ly
    dù nó đứng SAU trong list."""
    fake_ledger = _write_ledger(tmp_path, {"CL_D99_fake_case_for_test": ["trần thị bích ngọc"]})
    monkeypatch.setattr(cp, "CL_REAL_PERSONS_LEDGER_FILE", fake_ledger)

    reordered_profile = {
        "symbol_library": [
            {"key": "phap_luat_toa_an", "aliases": ["nguyễn mạnh tường"], "safety_critical": True},
            {"key": "phap_luat_can_can_cong_ly", "aliases": ["năm cam"], "safety_critical": True},
        ]
    }
    merged = cp._merge_ledger_aliases_into_cl_profile(reordered_profile)
    target = next(e for e in merged["symbol_library"] if e["key"] == "phap_luat_can_can_cong_ly")
    other = next(e for e in merged["symbol_library"] if e["key"] == "phap_luat_toa_an")
    assert "trần thị bích ngọc" in [a.lower() for a in target["aliases"]]
    # "other" (phap_luat_toa_an) không nhận thêm alias ledger nào ngoài alias tĩnh gốc của nó
    assert other["aliases"] == ["nguyễn mạnh tường"]


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
