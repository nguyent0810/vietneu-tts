"""Đọc domain_creative_profiles.json -- dùng chung bởi creative_director.py,
director_bible.py, render_short.py để tham số hoá "đạo diễn hình ảnh" theo
domain thay vì hardcode "Phật giáo/tâm linh" khắp nơi. Domain chưa có trong
file (hoặc không truyền domain_id) rơi về profile BUD -- đúng hành vi hiện
tại của mọi lệnh gọi cũ trước khi file này tồn tại, không có gì đổi ngầm
cho kênh Phật giáo đang chạy thật."""
import functools
import json
import re
import sys
import unicodedata
from pathlib import Path

import asset_safety
import rotation_state

PROFILES_FILE = Path(__file__).parent / "domain_creative_profiles.json"
DOMAIN_TOPICS_FILE = Path(__file__).parent / "domain_topics.json"
DEFAULT_DOMAIN_ID = "BUD"
SYMBOL_VARIANT_ROTATION_STATE_PATH = Path(__file__).parent / "chunks_cache" / "symbol_variant_rotation_state.json"

# NEW: gap identified while scoping the CL Risk Gate implementation (real
# incident context: an autonomous agent once picked a real case -- Ted
# Bundy -- with a minor victim, caught and cancelled by a human after the
# fact; see twice_weekly_batch.py:23-28). Verified directly against this
# codebase: creator_specs/CL_REAL_PERSONS_v1.json is a human-authored ledger
# of every real person's name-forms declared for each approved CL
# content_id, but it only feeds test_cl_real_person_safety.py's
# test_manifest_names_all_covered_by_aliases -- a CI-time cross-check, NOT
# a runtime source. resolve_symbol()'s actual routing (the mechanism that
# keeps a real name out of a Pexels query/AI-image prompt) reads ONLY the
# static, hand-typed `aliases` list in domain_creative_profiles.json. That
# means today, for HUMAN-selected CL content (not just any future
# auto-selected path), a real person declared in the ledger is NOT actually
# protected until a human separately, correctly, hand-copies the same
# string into the JSON config and remembers to run the test before merging.
# That is a real "two files must be kept in sync by hand, silently, forever"
# failure mode, independent of whether case *selection* is ever automated.
# CL_REAL_PERSONS_LEDGER_FILE + _load_cl_ledger_name_forms() close this by
# making the ledger authoritative at runtime too: load_profile("CL") now
# merges every ledger name-form into the safety-critical symbol_library
# alias list automatically, so a human only has to get ONE file right
# (the ledger) for the asset-safety net to actually apply, rather than two.
#
# FAIL-CLOSED, not fail-soft (revised after real Codex CLI adversarial
# review, round 1, High finding #1 -- the first version of this fix warned
# and silently fell back to static-aliases-only on a missing/malformed
# ledger, which the reviewer correctly called out: for a FUTURE real person
# declared ONLY in the ledger (the whole point of this fix), a broken
# ledger read would mean NO protection at all, silently, on the exact
# safety-critical path this code exists to protect. Codex's own framing,
# adopted directly: "you can fail closed for CL without affecting FS/BUD"
# -- the ledger is only ever touched when resolved_id=="CL" (see
# load_profile() below), so a hard failure here can never break FS/BUD
# regardless of how strict it is. CLRealPersonsLedgerError is allowed to
# propagate all the way out of load_profile("CL") -- every real call site
# (render_short.py, creative_director.py, long_batch_runner.py) already
# treats an unhandled exception from its content pipeline as a hard stop
# (see MAX_RETRIES_PER_*/`status="failed"` handling in short_batch_runner.py/
# long_batch_runner.py) -- there is deliberately no "emergency override"
# flag here; per this project's own stated philosophy (see
# twice_weekly_batch.py's docstring) that would be enterprise-scale
# machinery disproportionate to a 1-operator project, AND -- more
# importantly -- Codex's own recommendation was that any such override
# would itself need to be an explicit, prominently-logged operator action
# unavailable in publishing runs, which is a bigger mechanism than this
# narrow fix's scope; a genuinely broken ledger file should be fixed by a
# human before CL processing continues, not routed around.
#
# Known, accepted trade-off (Codex round 1, Medium finding #3): because
# load_profile("CL") now unconditionally injects every ledger name into the
# returned aliases, test_cl_real_person_safety.py's
# test_manifest_names_all_covered_by_aliases now passes BY CONSTRUCTION for
# any well-formed ledger -- it can no longer prove "a human remembered to
# hand-copy the alias," because that manual step no longer exists. This is
# intentional, not a bug: the guarantee that test protected (ledger names
# are actually routed to a safe symbol at runtime) now holds unconditionally
# via code instead of conditionally via human diligence, which is strictly
# stronger, not weaker -- but the test's remaining value going forward is
# mostly "does the ledger still parse/merge cleanly," not "did a human
# remember." See test_cl_ledger_alias_sync.py for the tests that actually
# exercise this fix's real guarantees (fail-closed on malformed data,
# ledger-only names get protected, no cross-domain leakage).
#
# Honest scope limit (Codex round 1, Medium finding #4, stated plainly
# rather than glossed over): this mechanism guarantees that every name-form
# a human correctly DECLARED in the ledger gets routed to a safe symbol. It
# is NOT a complete real-person-detection system -- it cannot catch a
# person omitted from the ledger entirely, a nickname/short form never
# declared, a name introduced after ledger review, or a reference that
# doesn't literally appear as declared text in the beat/scene passed to
# resolve_symbol(). That residual risk existed before this fix (the static
# alias list had the exact same limitation) and is unchanged by it.
CL_REAL_PERSONS_LEDGER_FILE = Path(__file__).parent / "creator_specs" / "CL_REAL_PERSONS_v1.json"

# Ưu tiên gộp alias ledger vào ĐÚNG entry này theo `key` (không phụ thuộc
# thứ tự list) -- Codex round 1: "should be validated explicitly or
# targeted by a configured key rather than relying on list order." Nếu
# entry này không tồn tại/không còn safety_critical, rơi về entry
# safety_critical ĐẦU TIÊN tìm thấy (hành vi cũ, vẫn an toàn -- cả 2 entry
# CL hiện tại trỏ tới ảnh biểu tượng trung tính như nhau).
CL_LEDGER_ALIAS_TARGET_KEY = "phap_luat_can_can_cong_ly"


class CLRealPersonsLedgerError(RuntimeError):
    """Ledger creator_specs/CL_REAL_PERSONS_v1.json bị THIẾU, hỏng JSON,
    hoặc sai schema (không phải object ở cấp cao nhất; 1 content_id có giá
    trị không phải list; 1 phần tử trong list không phải chuỗi khác rỗng).
    RAISE ở đây là CÓ CHỦ ĐÍCH (fail-closed) -- xem comment dài phía trên
    CL_REAL_PERSONS_LEDGER_FILE. KHÔNG được bắt lỗi này rồi âm thầm tiếp
    tục xử lý CL bằng alias tĩnh mà thôi -- một người thật CHỈ khai báo
    trong ledger (không có alias tĩnh trùng) sẽ hoàn toàn mất chặn an toàn
    nếu lỗi này bị nuốt."""
    pass


def _load_cl_ledger_name_forms() -> list[str]:
    """Đọc creator_specs/CL_REAL_PERSONS_v1.json và trả về danh sách MỌI
    cách gọi (name_form) đã khai báo, gộp từ mọi content_id (loại các key
    bắt đầu bằng "_", đó là chú thích). FAIL-CLOSED (xem comment trên
    CL_REAL_PERSONS_LEDGER_FILE): file thiếu, JSON hỏng, không phải object,
    hoặc sai schema (giá trị 1 content_id không phải list, hoặc list chứa
    phần tử không phải chuỗi/chuỗi rỗng) -- RAISE CLRealPersonsLedgerError,
    không âm thầm trả [] rồi rơi về "chỉ dùng alias tĩnh". Ledger RỖNG
    nhưng HỢP LỆ (vd {} hoặc mọi content_id đều có mảng [] -- trạng thái
    THẬT của vài content_id CL hôm nay, đã rà soát xác nhận không có người
    thật) KHÔNG raise -- đó là 1 kết quả hợp lệ, khác với "không đọc
    được"."""
    if not CL_REAL_PERSONS_LEDGER_FILE.exists():
        raise CLRealPersonsLedgerError(
            f"Ledger người thật CL không tồn tại: {CL_REAL_PERSONS_LEDGER_FILE} -- KHÔNG thể xác "
            f"nhận alias an toàn cho content CL, DỪNG (fail-closed) thay vì tiếp tục xử lý không "
            f"có chặn ledger-derived. Khôi phục file trước khi tiếp tục."
        )
    try:
        raw = CL_REAL_PERSONS_LEDGER_FILE.read_text(encoding="utf-8")
    except OSError as exc:
        raise CLRealPersonsLedgerError(
            f"Không đọc được {CL_REAL_PERSONS_LEDGER_FILE} ({exc}) -- DỪNG (fail-closed)."
        ) from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CLRealPersonsLedgerError(
            f"JSON hỏng trong {CL_REAL_PERSONS_LEDGER_FILE} ({exc}) -- DỪNG (fail-closed), không "
            f"đoán/bỏ qua nội dung hỏng vì đây là ledger an toàn tên người thật."
        ) from exc
    if not isinstance(data, dict):
        raise CLRealPersonsLedgerError(
            f"{CL_REAL_PERSONS_LEDGER_FILE} phải là 1 object JSON cấp cao nhất (content_id -> danh "
            f"sách chuỗi), nhận được {type(data).__name__} -- DỪNG (fail-closed)."
        )
    name_forms: list[str] = []
    for content_id, forms in data.items():
        if not isinstance(content_id, str):
            raise CLRealPersonsLedgerError(
                f"{CL_REAL_PERSONS_LEDGER_FILE}: key không phải chuỗi ({content_id!r}) -- DỪNG (fail-closed)."
            )
        if content_id.startswith("_"):
            continue  # chú thích (vd "_comment"), không phải content_id thật
        if not isinstance(forms, list):
            raise CLRealPersonsLedgerError(
                f"{CL_REAL_PERSONS_LEDGER_FILE}: content_id {content_id!r} có giá trị không phải "
                f"list ({type(forms).__name__}) -- DỪNG (fail-closed), không âm thầm bỏ qua entry "
                f"sai schema trong ledger an toàn tên người thật."
            )
        for form in forms:
            if not isinstance(form, str) or not form.strip():
                raise CLRealPersonsLedgerError(
                    f"{CL_REAL_PERSONS_LEDGER_FILE}: content_id {content_id!r} có phần tử không "
                    f"phải chuỗi khác rỗng ({form!r}) -- DỪNG (fail-closed)."
                )
            name_forms.append(form.strip())
    return name_forms


def _merge_ledger_aliases_into_cl_profile(profile: dict) -> dict:
    """Hợp nhất MỌI name_form từ CL_REAL_PERSONS_v1.json vào alias list của
    1 entry safety_critical trong symbol_library CL -- ưu tiên
    CL_LEDGER_ALIAS_TARGET_KEY theo key cụ thể (không phụ thuộc thứ tự
    list, Codex round 1), rơi về entry safety_critical đầu tiên nếu key đó
    không tồn tại/không còn safety_critical (cả 2 entry CL hiện tại trỏ
    tới ảnh biểu tượng trung tính như nhau -- cán cân công lý/toà án --
    nên vẫn an toàn, khớp đúng cách test_cl_real_person_safety.py xác nhận
    kết quả: entry["key"] thuộc SAFE_SYMBOL_KEYS, không đòi hỏi 1 key cụ
    thể). Không thêm trùng (so khớp NFC+casefold, xem _normalize_for_match).
    Ledger RỖNG (không có tên nào) -- trả nguyên profile, không đổi gì, dù
    profile có/không có entry safety_critical (không có gì cần route).

    FAIL-CLOSED (fixes Codex CLI round 2, High finding -- phát hiện thật
    sau khi round 1 được sửa): ledger CÓ tên NHƯNG profile symbol_library
    KHÔNG CÒN entry safety_critical nào để gộp alias vào (vd
    domain_creative_profiles.json bị sửa/xoá nhầm 2 entry CL an toàn) --
    trước đây hàm này ÂM THẦM trả profile KHÔNG ĐỔI (bảo toàn ledger_names
    nhưng không route đi đâu cả), khiến load_profile("CL") "thành công"
    trong khi KHÔNG CÓ nơi an toàn nào để chặn tên người thật -- Codex tái
    hiện trực tiếp: resolve_symbol() trả None cho 1 tên đã khai báo trong
    ledger. Giờ RAISE CLRealPersonsLedgerError thay vì trả profile
    không được bảo vệ -- cùng nguyên tắc fail-closed như
    _load_cl_ledger_name_forms()."""
    ledger_names = _load_cl_ledger_name_forms()  # raises CLRealPersonsLedgerError on bad data, not caught here
    if not ledger_names:
        return profile
    safety_entries = [e for e in profile.get("symbol_library", []) if e.get("safety_critical")]
    if not safety_entries:
        raise CLRealPersonsLedgerError(
            f"Ledger CL có {len(ledger_names)} tên người thật đã khai báo, nhưng symbol_library CL "
            f"HIỆN TẠI không có entry safety_critical nào để gộp alias vào -- DỪNG (fail-closed), "
            f"KHÔNG được tiếp tục xử lý CL mà không có nơi an toàn nào để route tên người thật tới. "
            f"Đây là dấu hiệu domain_creative_profiles.json bị sửa/xoá nhầm phần safety_critical của "
            f"CL (vd phap_luat_can_can_cong_ly/phap_luat_toa_an)."
        )
    target = next((e for e in safety_entries if e.get("key") == CL_LEDGER_ALIAS_TARGET_KEY), safety_entries[0])
    existing = list(target.get("aliases", []))
    existing_norm = {_normalize_for_match(a) for a in existing}
    for name in ledger_names:
        norm = _normalize_for_match(name)
        if norm not in existing_norm:
            existing.append(name)
            existing_norm.add(norm)
    target["aliases"] = existing
    return profile


def _normalize_for_match(s: str) -> str:
    """Chuẩn hoá 1 chuỗi để so khớp alias: NFC (gộp tổ hợp dấu tiếng Việt
    về 1 dạng chuẩn -- 1 ký tự có dấu có thể được mã hoá NFC [1 code point]
    hay NFD [chữ cái + dấu kết hợp riêng], 2 dạng NHÌN GIỐNG HỆT nhưng so
    sánh chuỗi thô sẽ KHÔNG khớp nếu 2 bên khác dạng] rồi casefold (mạnh
    hơn .lower(), xử lý đúng nhiều trường hợp Unicode hơn) -- Codex round 1
    khuyến nghị trực tiếp. Áp dụng CẢ 2 phía (alias lẫn text) trước khi so
    khớp."""
    return unicodedata.normalize("NFC", s).casefold()


@functools.lru_cache(maxsize=1024)
def _compile_alias_pattern(alias_normalized: str) -> re.Pattern:
    """Regex biên dịch 1 lần/alias: lookaround-based
    `(?<!\\w)...(?!\\w)`, KHÔNG dùng `\\b...\\b` (bản vá vòng 1 dùng \\b --
    Codex round 1, High finding #2, phát hiện false-negative thật: \\b yêu
    cầu CHUYỂN TIẾP word<->non-word ở đúng vị trí biên, nên 1 alias KẾT
    THÚC bằng ký tự không phải \\w [vd "O.J." kết thúc bằng dấu chấm] đứng
    trước 1 ký tự cũng không phải \\w [vd dấu cách] sẽ KHÔNG có \\b nào ở
    đó -- "O.J." trong "O.J. bị bắt" KHÔNG khớp, dù alias xuất hiện nguyên
    văn. Lookaround âm tính chỉ đòi hỏi ký tự NGAY SAU/TRƯỚC alias không
    phải \\w -- đúng ngữ nghĩa "alias không phải là 1 phần của từ dài hơn"
    mà không áp đặt yêu cầu ký tự BIÊN của chính alias phải là \\w). Vẫn
    chặn đúng "an" không khớp nhầm bên trong "anh" (ký tự sau alias, 'h',
    LÀ \\w -- (?!\\w) fail). `\\w` của Python re trên chuỗi str mặc định là
    Unicode-aware nên biên từ tiếng Việt có dấu hoạt động đúng."""
    return re.compile(r"(?<!\w)" + re.escape(alias_normalized) + r"(?!\w)")


def _load_all_profiles() -> dict:
    if not PROFILES_FILE.exists():
        return {}
    data = json.loads(PROFILES_FILE.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def resolve_domain_id(domain_id: str | None) -> str:
    """P1 (E2E validation remediation): trả về domain_id THỰC SỰ sẽ được
    load_profile() dùng (áp dụng ĐÚNG cùng logic fallback -- domain rỗng
    hoặc không có trong profiles.json -> DEFAULT_DOMAIN_ID) -- KHÔNG phải
    domain_id thô truyền vào (có thể None/không hợp lệ). Dùng để namespace
    mọi cache theo domain THẬT đã dùng để tổng hợp nội dung, tránh 2 lời
    gọi có domain_id thô khác nhau (vd None vs "BUD") nhưng cùng rơi về 1
    profile thật lại bị coi là 2 namespace cache khác nhau một cách sai
    lệch, hoặc ngược lại."""
    profiles = _load_all_profiles()
    if domain_id and domain_id in profiles:
        return domain_id
    return DEFAULT_DOMAIN_ID


def load_profile(domain_id: str | None) -> dict:
    profiles = _load_all_profiles()
    if domain_id and domain_id in profiles:
        resolved_id = domain_id
        profile = profiles[domain_id]
    else:
        if domain_id and domain_id != DEFAULT_DOMAIN_ID:
            print(
                f"CẢNH BÁO: domain '{domain_id}' chưa có trong domain_creative_profiles.json "
                f"-- dùng profile mặc định ({DEFAULT_DOMAIN_ID}).", file=sys.stderr,
            )
        resolved_id = DEFAULT_DOMAIN_ID
        profile = profiles.get(DEFAULT_DOMAIN_ID, {})
    if resolved_id == "CL":
        # xem comment ở CL_REAL_PERSONS_LEDGER_FILE phía trên: hợp nhất
        # alias người thật từ ledger vào symbol_library TẠI ĐÂY, mỗi lần
        # gọi (mỗi lời gọi đã đọc JSON tươi từ đĩa qua _load_all_profiles(),
        # không cache toàn cục, nên sửa `profile` tại chỗ ở đây an toàn --
        # không có state chia sẻ giữa các lần gọi khác nhau). CỐ Ý KHÔNG
        # try/except CLRealPersonsLedgerError ở đây -- fail-closed CHỈ cho
        # domain CL (FS/BUD không bao giờ vào nhánh này, không bị ảnh
        # hưởng); caller (render_short.py/creative_director.py/
        # long_batch_runner.py) đã coi exception không bắt được từ bước
        # đọc profile là lỗi cứng, dừng xử lý content_id đó -- đúng hành vi
        # mong muốn khi ledger an toàn tên người thật không đọc được.
        profile = _merge_ledger_aliases_into_cl_profile(profile)
    return profile


class SafetyCriticalAssetMissingError(RuntimeError):
    """Asset tĩnh của 1 symbol_library entry safety_critical=true (dùng để
    chặn tên người thật khỏi Pexels/AI-generation, xem điểm #1 audit 9
    điểm) bị THIẾU trên đĩa. KHÔNG được bắt lỗi này rồi âm thầm rơi về
    Pexels/ComfyUI -- Codex review chỉ ra: render_short.py vốn có hành vi
    "asset thiếu -> cảnh báo + dùng Pexels bình thường" cho symbol_library
    NÓI CHUNG (chấp nhận được cho khái niệm pháp lý chung, không chấp nhận
    được cho chặn an toàn tên người thật -- mất chặn ĐÚNG lúc cần nhất).
    Dừng render, buộc con người khôi phục file trước khi tiếp tục."""
    pass


def domain_id_for_topic(topic: str) -> str | None:
    """Tra ngược tên chủ đề (vd 'Phong Thủy') -> domain_id (vd 'FS') qua
    domain_topics.json -- Short thao tác theo topic string, không có
    domain_id sẵn trong tay như CLI của Long (--domain)."""
    if not DOMAIN_TOPICS_FILE.exists():
        return None
    data = json.loads(DOMAIN_TOPICS_FILE.read_text(encoding="utf-8"))
    for did, name in data.get("domains", {}).items():
        if name == topic:
            return did
    return None


def topic_for_domain_id(domain_id: str) -> str | None:
    """P4c (E2E validation remediation) -- chiều XUÔI của
    domain_id_for_topic(): domain_id (vd 'FS') -> tên chủ đề (vd 'Phong
    Thủy') qua domain_topics.json. long_batch_runner.py's CLI dùng để tự
    suy ra --topic ĐÚNG theo --domain khi --topic bị bỏ trống, thay vì
    dùng 1 default tĩnh hard-code riêng cho BUD ('Phật giáo') áp nhầm cho
    mọi domain khác -- lỗi thật: gọi `--domain FS` (hoặc CL) mà quên
    `--topic` trước đây âm thầm rơi về topic của BUD, khiến toàn bộ
    registry/output đọc/ghi nhầm thư mục kênh trong khi profile sáng tạo
    (creative_director.py) vẫn dùng ĐÚNG domain FS/CL -- lẫn lộn kênh
    ngay trong 1 lần chạy. Không tự đoán tên (cùng nguyên tắc như
    domain_id_for_topic) -- domain chưa có trong domain_topics.json trả
    về None, caller phải tự quyết định (raise) chứ không âm thầm dùng
    default sai."""
    if not DOMAIN_TOPICS_FILE.exists():
        return None
    data = json.loads(DOMAIN_TOPICS_FILE.read_text(encoding="utf-8"))
    return data.get("domains", {}).get(domain_id)


def load_profile_for_topic(topic: str) -> dict:
    return load_profile(domain_id_for_topic(topic))


def resolve_symbol(profile: dict, text: str) -> dict | None:
    """Trả entry symbol_library đầu tiên có alias xuất hiện trong `text`
    (so khớp lookaround-based, không phân biệt hoa/thường, NFC-normalized
    -- xem _compile_alias_pattern()/_normalize_for_match(); trước đây so
    khớp chuỗi con thô) -- None nếu không khớp. Rẻ (không gọi agy/API),
    dùng làm bước tiền lọc trước khi quyết định treatment, cho cả beat của
    Long lẫn scene của Short."""
    normalized_text = _normalize_for_match(text)
    for entry in profile.get("symbol_library", []):
        for alias in entry.get("aliases", []):
            alias_norm = _normalize_for_match(alias.strip())
            if not alias_norm:
                continue
            if _compile_alias_pattern(alias_norm).search(normalized_text):
                return entry
    return None


def is_video_unsafe_topic(profile: dict, text: str) -> bool:
    """G3 (Video Generation remediation): True nếu `text` khớp 1 cụm trong
    profile['video_unsafe_terms'] (so khớp chuỗi con, không phân biệt hoa/
    thường -- cùng kiểu match như resolve_symbol()). Domain không khai báo
    `video_unsafe_terms` (mọi domain trừ CL hiện tại) -> luôn False.

    KHÁC resolve_symbol(): khớp ở đây KHÔNG ép về 1 symbol/asset tĩnh cố
    định nào -- chỉ đánh dấu "không được chọn Treatment.VIDEO" (tránh
    catalog Pexels tự thiên lệch sang hình ảnh không phù hợp cho các chủ đề
    pháp lý chung chung, xem domain_creative_profiles.json's
    _video_unsafe_terms_note). Beat khớp đây vẫn được phân loại IMAGE/
    TYPOGRAPHY bình thường theo tỷ lệ ở caller (creative_director.py::
    _build_shot_list_by_ratio) -- tách RIÊNG khỏi symbol_library's aliases
    vì trước đây gộp chung khiến 34/36 beat 1 tập THẬT collapse về đúng 1
    ảnh tĩnh (xem note đầy đủ ở phap_luat_can_can_cong_ly entry)."""
    lowered = text.lower()
    return any(term.lower() in lowered for term in profile.get("video_unsafe_terms", []))


def pick_symbol_asset_path(entry: dict) -> str | None:
    """Trả về đường dẫn TUYỆT ĐỐI (string) của asset tĩnh sẽ dùng cho
    entry symbol_library này -- audit 9 điểm mục #2 ("trùng lặp ảnh Ngũ
    Hành khá nhiều"): entry có `asset_paths` (list, nhiều biến thể) thì
    XOAY VÒNG qua rotation_state.py (cùng cơ chế anti-repeat đã dùng cho
    element_color/iching/western_zodiac generator -- có nhận biết lịch sử
    gần đây, không phải chọn ngẫu nhiên/hash) để không lặp đúng 1 file mỗi
    lần; entry chỉ có `asset_path` (string đơn, vd 2 asset pháp luật của
    CL) thì trả thẳng, không cần rotation vì chỉ có 1 lựa chọn.

    KHÔNG có bước "thử rồi có thể fail" giữa chọn và dùng ở đây (khác
    caller sinh script LLM) -- chọn 1 file ảnh tĩnh có sẵn luôn thành công.
    Dùng pick_and_commit_next() (đọc-chọn-ghi NGUYÊN TỬ trong 1 lock) chứ
    KHÔNG dùng peek_next()+commit() (2 lock riêng) -- Codex review phát
    hiện race condition thật: Long và Short render song song có thể cùng
    gọi peek_next() trước khi bên nào kịp commit(), dẫn tới đảo lịch sử
    hoặc cả 2 dùng trùng variant trong cùng 1 đợt. state_key khác nhau
    (last_bat_quai_variant / last_ngu_hanh_variant) an toàn dùng CHUNG 1
    file state vì pick_and_commit_next() không có reservation liên
    state_key như peek_next() (vốn dùng field reserved_item/reserved_at
    KHÔNG namespace theo state_key, chỉ an toàn khi mỗi state_key có file
    riêng như các caller LLM hiện có)."""
    paths = [p for p in (entry.get("asset_paths") or []) if p and p.strip()]
    single = entry.get("asset_path")
    single = single if single and single.strip() else None

    # Codex review điểm #1 vòng 3 (blocker): trước đây, entry safety_critical
    # THIẾU HẲN asset_path/asset_paths (vd cấu hình JSON bị xoá/lỗi nhầm)
    # khiến chosen=None -- điều kiện raise cũ yêu cầu `chosen` truthy nên
    # KHÔNG raise, và caller (render_short.py/creative_director.py) có
    # guard "chỉ gọi hàm này nếu asset_path/asset_paths tồn tại" khiến hàm
    # này thậm chí KHÔNG BAO GIỜ được gọi trong trường hợp đó -- chặn an
    # toàn bị bỏ qua hoàn toàn, êm ru, không ai biết. Kiểm tra safety_critical
    # NGAY TỪ ĐẦU, không phụ thuộc paths/single có hay không.
    if not paths and not single:
        if entry.get("safety_critical"):
            raise SafetyCriticalAssetMissingError(
                f"Symbol an toàn '{entry.get('key')}' (safety_critical=true, dùng chặn tên người "
                f"thật) KHÔNG có asset_path/asset_paths trong cấu hình -- DỪNG, không được tiếp tục "
                f"xử lý beat này qua Pexels/AI generation. Kiểm tra domain_creative_profiles.json."
            )
        return None

    if paths:
        variant = rotation_state.pick_and_commit_next(
            SYMBOL_VARIANT_ROTATION_STATE_PATH, paths, f"last_{entry['key']}_variant",
        )
        chosen = str(Path(__file__).parent / variant)
    else:
        chosen = str(Path(__file__).parent / single)

    # Cấu hình CÓ path nhưng file thật KHÔNG tồn tại/không phải file thật
    # trên đĩa (vd bị xoá nhầm, hoặc path trỏ nhầm sang thư mục) -- cùng lý
    # do dừng cứng như trên. Dùng is_file() (không phải exists()) -- Codex
    # review: exists() vẫn trả True cho thư mục trùng tên, is_file() chặt
    # hơn, đúng ngữ nghĩa "đây phải là 1 file ảnh dùng được".
    if entry.get("safety_critical") and not Path(chosen).is_file():
        raise SafetyCriticalAssetMissingError(
            f"Symbol an toàn '{entry['key']}' (safety_critical=true, dùng chặn tên người thật) "
            f"trỏ tới asset KHÔNG TỒN TẠI hoặc không phải file hợp lệ: {chosen} -- DỪNG render, "
            f"không được fallback Pexels/AI generation vì sẽ làm lộ tên người thật vào query/prompt "
            f"không kiểm soát. Khôi phục file trước khi tiếp tục."
        )

    # G5 (Video Generation remediation): symbol_library asset đã được con
    # người xác nhận an toàn thủ công (xem docstring hàm), NHƯNG nếu 1 file
    # sau đó bị đổi tên/đánh dấu UNSAFE (vd phát hiện lỗi sau khi đã dùng),
    # hoặc có safety record tường minh 'unsafe'/'review_required' -- CHẶN
    # ngay tại đây, không im lặng dùng tiếp. Đây là đường asset an toàn NHẤT
    # trong pipeline (curated, không phải Pexels catalog không kiểm soát)
    # nên rẻ và đáng để kiểm tra mọi lần, không chỉ symbol safety_critical.
    asset_safety.assert_asset_safe_for_assembly(chosen)
    return chosen


def get_symbol_entry_by_key(profile: dict, symbol_key: str) -> dict | None:
    """Tra `symbol_library` theo ĐÚNG `key` (không phải so khớp alias như
    resolve_symbol()) -- dùng khi đã biết chắc symbol_key của 1 beat (đã
    lưu sẵn trong shot_list_final.json) và chỉ cần tra lại entry cấu hình
    HIỆN TẠI của nó, xem heal_stale_symbol_asset_paths()."""
    for entry in profile.get("symbol_library", []):
        if entry.get("key") == symbol_key:
            return entry
    return None


def heal_stale_symbol_asset_paths(shot_list_path: str, domain_id: str | None) -> int:
    """P4b (E2E validation remediation, real incident, FS channel):
    pick_symbol_asset_path() resolves a symbol's asset path ONCE, baked
    into shot_list_final.json at shot-list-creation time
    (creative_director.py). If the symbol_library naming convention later
    changes (confirmed real: FS's Bát Quái/Ngũ Hành went from a flat
    filename to a 3-color rotation, leaving no flat file at all), an OLD
    shot list's baked-in path goes stale -- any future resume/re-render
    then crashes deep inside ffmpeg with a generic "No such file or
    directory" instead of a clear, actionable error, and with no attempt
    to self-heal even though the CURRENT config still has a perfectly
    valid replacement asset for that same symbol.

    Called before every Long-form video-render step (fresh or resumed):
    for every beat with `symbol_key` set whose baked-in `asset_path` no
    longer points at a real file, re-resolves fresh via the CURRENT
    profile's pick_symbol_asset_path() (same function, same G5
    safety-gate, same rotation-state mechanism as a brand-new resolution)
    and rewrites the shot list in place. Short-form doesn't have this
    problem -- it already resolves fresh on every render, never bakes a
    path in.

    Fails LOUDLY (raises, does not swallow) if a beat's symbol_key no
    longer exists in the current profile at all, or the current entry
    ALSO doesn't point at a real file -- that is a genuine configuration
    problem needing a human, not something to silently paper over.
    Returns the number of beats healed (0 if nothing was stale)."""
    profile = load_profile(domain_id)
    shot_list_path_obj = Path(shot_list_path)
    data = json.loads(shot_list_path_obj.read_text(encoding="utf-8"))
    healed = 0
    for beat in data.get("beats", []):
        symbol_key = beat.get("symbol_key")
        if not symbol_key:
            continue
        asset_path = beat.get("asset_path")
        if asset_path and Path(asset_path).is_file():
            continue  # still valid -- nothing to heal for this beat
        entry = get_symbol_entry_by_key(profile, symbol_key)
        if entry is None:
            raise RuntimeError(
                f"Beat có symbol_key={symbol_key!r} nhưng domain hiện tại (resolve_domain_id={domain_id!r}) "
                f"KHÔNG còn entry này trong symbol_library -- không thể tự hồi phục đường dẫn asset đã mất "
                f"({asset_path!r}). Kiểm tra domain_creative_profiles.json hoặc regenerate shot list."
            )
        fresh_path = pick_symbol_asset_path(entry)
        if not fresh_path or not Path(fresh_path).is_file():
            raise RuntimeError(
                f"Beat có symbol_key={symbol_key!r}: đường dẫn asset cũ đã mất ({asset_path!r}), và entry "
                f"HIỆN TẠI cũng không trỏ tới file hợp lệ ({fresh_path!r}) -- không thể tự hồi phục."
            )
        beat["asset_path"] = fresh_path
        if beat.get("symbol_asset_path"):
            beat["symbol_asset_path"] = fresh_path
        healed += 1
    if healed:
        shot_list_path_obj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return healed
