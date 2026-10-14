"""Test tự động cho điểm #1 audit 9 điểm: chặn an toàn khi beat CL (Hình
Sự) nhắc tên NGƯỜI THẬT (bị can/nạn nhân trong vụ án đã xử) -- resolve_symbol()
PHẢI khớp ngay vào 1 trong 2 ảnh biểu tượng trung tính (cán cân công lý/
toà án), KHÔNG được rơi qua bước phân loại IMAGE/ComfyUI/Pexels tiếp theo
(nơi tên người thật có thể lọt vào query tìm ảnh/prompt sinh ảnh AI)."""
import json
from pathlib import Path

import pytest
from PIL import Image

import domain_creative_profiles as cp

REAL_PERSON_TEXTS = [
    ("Trương Văn Cam — tức Năm Cam — và đồng phạm", "năm cam/trương văn cam"),
    ("Lê Văn Luyện, sinh ngày 18 tháng 10 năm 1993", "lê văn luyện"),
    ("Người trực tiếp thực hiện là Nguyễn Mạnh Tường, chủ cơ sở", "nguyễn mạnh tường"),
    ("chị Lê Thị Thanh Huyền đến Thẩm mỹ viện Cát Tường", "lê thị thanh huyền"),
    ("một bồi thẩm đoàn hình sự tuyên O.J. Simpson trắng án", "o.j. simpson"),
]

# Codex review phát hiện: alias chỉ khớp tên ĐẦY ĐỦ, nhưng script thật có
# CÂU SAU nhắc lại bằng tên RÚT GỌN (không có họ tên đầy đủ trong cùng
# câu/beat) -- trích NGUYÊN VĂN từ creator_specs/WEEKLY_CONTENT_PACKAGE_v1_draft.md
# để test đúng dạng beat THẬT SỰ sẽ được phân loại, không phải câu tôi tự
# nghĩ ra.
REAL_PERSON_SHORT_FORM_TEXTS = [
    ("tại thời điểm gây án, đêm 24 tháng 8 năm 2011, Luyện còn khoảng 54 ngày nữa mới đủ 18 tuổi.", "luyện (rút gọn)"),
    ("Chị Huyền đã tử vong ngay sau đó.", "chị huyền (rút gọn)"),
    ("một bồi thẩm đoàn khác đã xem xét phần lớn cùng bằng chứng đó dưới một tiêu chuẩn chứng minh thấp hơn nhiều so với hình sự, và kết luận Simpson phải chịu trách nhiệm dân sự", "simpson (rút gọn)"),
]

SAFE_SYMBOL_KEYS = {"phap_luat_can_can_cong_ly", "phap_luat_toa_an"}
MANIFEST_PATH = Path(__file__).parent / "creator_specs" / "CL_REAL_PERSONS_v1.json"


def test_known_real_persons_resolve_to_safe_symbol():
    profile = cp.load_profile("CL")
    for text, label in REAL_PERSON_TEXTS:
        entry = cp.resolve_symbol(profile, text)
        assert entry is not None, f"'{label}' KHÔNG khớp symbol an toàn nào -- có thể lọt xuống Pexels/AI generation."
        assert entry["key"] in SAFE_SYMBOL_KEYS, f"'{label}' khớp sai symbol: {entry['key']}"


def test_generic_legal_text_without_real_name_still_works():
    """Không phải mọi câu CL đều cần symbol -- câu chỉ nói luật chung
    (không tên người) mà không khớp alias legal-concept nào thì vẫn rơi về
    None như trước, hành vi KHÔNG đổi cho câu không liên quan người thật."""
    profile = cp.load_profile("CL")
    entry = cp.resolve_symbol(profile, "Theo Điều 74 Bộ luật Hình sự năm 1999")
    assert entry is None


def test_real_person_aliases_only_added_to_cl_domain():
    """Các alias tên người thật (năm cam, lê văn luyện...) CHỈ được thêm
    vào domain CL -- không vô tình lọt sang domain khác (BUD/FS) qua copy-paste."""
    for domain_id in ("BUD", "FS"):
        profile = cp.load_profile(domain_id)
        for text, label in REAL_PERSON_TEXTS:
            entry = cp.resolve_symbol(profile, text)
            assert entry is None, f"Domain {domain_id} vô tình khớp alias tên người thật CL: '{label}' -> {entry}"


def test_real_person_short_form_mentions_resolve_to_safe_symbol():
    """Codex review (điểm #1, vòng 1 NEEDS_REVISION): câu SAU trong cùng
    script chỉ nhắc tên RÚT GỌN (Luyện/Chị Huyền/Simpson), không lặp lại
    họ tên đầy đủ -- PHẢI vẫn khớp symbol an toàn, không được rơi qua
    pipeline thường chỉ vì đây là câu thứ 2+ trong đoạn."""
    profile = cp.load_profile("CL")
    for text, label in REAL_PERSON_SHORT_FORM_TEXTS:
        entry = cp.resolve_symbol(profile, text)
        assert entry is not None, f"'{label}' (dạng rút gọn) KHÔNG khớp symbol an toàn -- lọt xuống pipeline thường."
        assert entry["key"] in SAFE_SYMBOL_KEYS


def test_short_form_aliases_do_not_false_positive_on_common_words():
    """'luyện còn khoảng' (cụm ngữ cảnh, KHÔNG phải chỉ 'luyện' một mình)
    -- xác nhận các từ tiếng Việt thông dụng chứa cùng âm tiết ('luyện
    tập', 'huấn luyện', 'rèn luyện') KHÔNG bị coi là nhắc người thật.

    Codex review vòng 2: assertion trước SAI -- chỉ kiểm tra chuỗi
    "luyện còn khoảng" có xuất hiện literal trong CÂU THỬ hay không (luôn
    False vì câu thử không chứa cụm đó), không kiểm tra alias có THỰC SỰ
    KHỚP hay không (resolve_symbol có thể trả entry khác qua alias hợp lệ
    như "phạm tội", khiến assertion cũ luôn pass giả). Sửa bằng cách dựng
    1 profile TỐI GIẢN CHỈ chứa riêng alias "luyện còn khoảng" (loại bỏ
    mọi alias khác có thể khớp hợp lệ) -- cô lập đúng điều cần kiểm: alias
    rút gọn có tự ý khớp vào các từ thông dụng chứa cùng âm tiết không."""
    isolated_profile = {
        "symbol_library": [{
            "key": "phap_luat_can_can_cong_ly",
            "aliases": ["luyện còn khoảng"],
        }]
    }
    common_word_texts = [
        "Người phạm tội cần được rèn luyện nhân cách trong quá trình cải tạo.",
        "Chương trình huấn luyện dành cho cán bộ điều tra.",
        "Bị cáo thường xuyên luyện tập thể thao trong trại giam.",
    ]
    for text in common_word_texts:
        entry = cp.resolve_symbol(isolated_profile, text)
        assert entry is None, (
            f"'{text}' bị nhận nhầm là nhắc người thật -- alias rút gọn 'luyện còn khoảng' "
            f"khớp nhầm vào từ thông dụng chứa cùng âm tiết."
        )


def test_manifest_names_all_covered_by_aliases():
    """VALIDATOR FAIL-CLOSED: MỌI cách gọi khai báo trong
    creator_specs/CL_REAL_PERSONS_v1.json PHẢI có alias khớp qua
    cp.load_profile("CL") (CL symbol_library).

    LƯU Ý VỀ Ý NGHĨA (cập nhật sau Codex CLI adversarial review thật, vòng
    2, khi rà soát tích hợp CL Risk Gate -- Medium finding, "a comment does
    not make this test meaningful again... editing/replacing/removing the
    test is the correct response"): trước đây, alias trong
    domain_creative_profiles.json HOÀN TOÀN là chuỗi viết tay thủ công, nên
    test này thực sự kiểm tra "con người đã nhớ chép tay đủ alias chưa" --
    một điều kiện có thể FAIL nếu ai đó quên. Từ khi domain_creative_profiles.py's
    load_profile("CL") tự động hợp nhất MỌI name_form từ chính
    CL_REAL_PERSONS_v1.json vào alias list (xem
    _merge_ledger_aliases_into_cl_profile()), test này giờ PASS THEO CẤU
    TRÚC cho bất kỳ ledger hợp lệ nào -- không còn chứng minh "con người đã
    nhớ", mà chứng minh "ledger đọc/parse/gộp thành công VÀ mọi tên đã khai
    báo thực sự resolve đúng 2 symbol an toàn" (vẫn là 1 test tích hợp thật,
    có giá trị regression thật -- nhưng không còn là "phát hiện con người
    quên" nữa, vì bước chép tay đó không còn tồn tại). Cơ chế MỚI (ledger
    authoritative + fail-closed khi ledger thiếu/hỏng/sai schema, hoặc khi
    profile CL mất hết entry safety_critical) được test riêng, đầy đủ hơn,
    trong test_cl_ledger_alias_sync.py -- đó mới là nơi xác nhận bất biến
    an toàn THẬT SỰ của cơ chế hiện tại."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    profile = cp.load_profile("CL")
    missing = []
    for content_id, name_forms in manifest.items():
        if content_id.startswith("_"):
            continue
        for name_form in name_forms:
            entry = cp.resolve_symbol(profile, name_form)
            if entry is None or entry["key"] not in SAFE_SYMBOL_KEYS:
                missing.append((content_id, name_form))
    assert not missing, (
        f"Các cách gọi sau trong manifest CHƯA có alias an toàn khớp -- "
        f"BỔ SUNG alias trước khi duyệt nội dung: {missing}"
    )


def test_cl_safe_symbol_assets_exist_on_disk():
    """Codex review: nếu asset PNG bị mất, Short sẽ fallback về Pexels
    (image_path.exists() check trong render_short.py) -- mất luôn chặn an
    toàn dù alias vẫn khớp đúng. Xác nhận file thật tồn tại + là ảnh hợp lệ."""
    profile = cp.load_profile("CL")
    checked = 0
    for entry in profile["symbol_library"]:
        if entry["key"] not in SAFE_SYMBOL_KEYS:
            continue
        path = Path(__file__).parent / entry["asset_path"]
        assert path.exists(), f"Asset an toàn bị thiếu trên đĩa: {path} (key={entry['key']})"
        with Image.open(path) as img:
            assert img.size[0] > 0 and img.size[1] > 0
        checked += 1
    assert checked == len(SAFE_SYMBOL_KEYS)


def test_all_ledger_cl_content_ids_have_manifest_entry():
    """VALIDATOR FAIL-CLOSED THẬT SỰ (Codex review vòng 2): test trước chỉ
    kiểm tên ĐÃ khai báo trong manifest, không phát hiện content_id CL bị
    QUÊN khai báo HOÀN TOÀN. Đối chiếu TRỰC TIẾP với
    creator_specs/WEEKLY_PUBLISHING_LEDGER_v1.json (nguồn thật, không phải
    tự liệt kê tay) -- MỌI content_id CL trong ledger PHẢI có entry trong
    manifest (dù rỗng [] nếu đã rà soát và xác nhận không có người thật).
    FAIL nếu content_id CL nào đó HOÀN TOÀN VẮNG MẶT khỏi manifest -- đây
    là tín hiệu "chưa ai rà soát", không tự động coi là an toàn."""
    ledger_path = Path(__file__).parent / "creator_specs" / "WEEKLY_PUBLISHING_LEDGER_v1.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    items = ledger["items"] if "items" in ledger else ledger
    if isinstance(items, dict):
        items = list(items.values())
    ledger_cl_ids = {it["content_id"] for it in items if it["content_id"].startswith("CL_")}

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_ids = {k for k in manifest if not k.startswith("_")}

    missing_entirely = ledger_cl_ids - manifest_ids
    assert not missing_entirely, (
        f"Các content_id CL sau HOÀN TOÀN VẮNG MẶT khỏi {MANIFEST_PATH.name} -- "
        f"chưa ai rà soát người thật, PHẢI thêm entry (dù rỗng [] nếu xác nhận không có): {missing_entirely}"
    )


def test_safety_critical_asset_missing_raises_not_fallback():
    """Codex review vòng 2 (blocker): render_short.py vốn fail-OPEN khi
    asset thiếu (cảnh báo + dùng Pexels bình thường) -- đúng cho symbol
    khái niệm chung, SAI cho symbol safety_critical=true (chặn tên người
    thật). Xác nhận pick_symbol_asset_path() RAISE (không trả path/None
    lặng lẽ) khi entry safety_critical=true trỏ tới file không tồn tại
    (path CÓ cấu hình nhưng file bị xoá)."""
    fake_entry = {
        "key": "phap_luat_can_can_cong_ly",
        "asset_path": "assets/symbol_library/__does_not_exist__.png",
        "safety_critical": True,
    }
    with pytest.raises(cp.SafetyCriticalAssetMissingError):
        cp.pick_symbol_asset_path(fake_entry)


def test_safety_critical_entry_with_no_path_configured_raises():
    """Codex review vòng 3 (blocker nghiêm trọng hơn): entry safety_critical
    HOÀN TOÀN THIẾU asset_path/asset_paths trong cấu hình (vd JSON bị sửa
    nhầm, xoá field) -- trước đây chosen=None nên điều kiện raise cũ
    (yêu cầu `chosen` truthy) KHÔNG kích hoạt, và caller còn có guard
    "chỉ gọi hàm khi có asset_path" khiến hàm này thậm chí không được gọi
    -- chặn an toàn bị bỏ qua ÊM RU. Xác nhận raise NGAY cả khi không có
    path nào cấu hình."""
    fake_entry = {"key": "phap_luat_can_can_cong_ly", "safety_critical": True}
    with pytest.raises(cp.SafetyCriticalAssetMissingError):
        cp.pick_symbol_asset_path(fake_entry)


def test_non_safety_critical_entry_with_no_path_returns_none_unchanged():
    """Hành vi CŨ (không đổi) cho entry KHÔNG an toàn-tới-hạn: thiếu path
    thì trả None lặng lẽ như trước, không raise -- chỉ safety_critical mới
    có yêu cầu nghiêm ngặt hơn."""
    fake_entry = {"key": "some_ai_generate_entry"}
    assert cp.pick_symbol_asset_path(fake_entry) is None


def test_safe_symbol_entries_have_required_structure():
    """Codex review vòng 3: xác nhận CẤU TRÚC cả 2 entry an toàn CL luôn
    có safety_critical=True, render_mode static_asset, và asset_path
    không rỗng -- nếu ai đó lỡ sửa/xoá field này sau này, test FAIL ngay
    thay vì chỉ phát hiện khi render thật."""
    profile = cp.load_profile("CL")
    checked = 0
    for entry in profile["symbol_library"]:
        if entry["key"] not in SAFE_SYMBOL_KEYS:
            continue
        assert entry.get("safety_critical") is True, f"{entry['key']} thiếu safety_critical=true"
        assert entry.get("render_mode") == "static_asset", f"{entry['key']} sai render_mode"
        assert entry.get("asset_path") or entry.get("asset_paths"), f"{entry['key']} thiếu asset_path/asset_paths"
        checked += 1
    assert checked == len(SAFE_SYMBOL_KEYS)


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
