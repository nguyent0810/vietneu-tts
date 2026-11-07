"""webauto: phần logic thuần (parse file, luật chặn, dựng prompt, CLI). Không mở trình duyệt, không mạng.

Phần chạm trình duyệt (Flow, ChatGPT, Muse, TikTok) chỉ kiểm bằng tay, vì phụ thuộc giao diện trang.
"""
import importlib.util
import json
from pathlib import Path

import pytest

from webauto import chatgpt, cli, common, flow, muse, tiktok
from webauto.browsentic import parse_payload


def test_slug_bo_dau_va_chu_d():
    assert common.slug("Đức Phật dạy") == "duc-phat-day"
    assert common.slug("!!!") == "item"
    assert len(common.slug("a" * 100)) == 40


def test_parse_prompts_ten_va_danh_so(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("# ghi chú\n\nfox | red fox in snow\nA lighthouse at dusk\nname |\n", encoding="utf-8")
    got = common.parse_prompts(f)
    assert got[0] == ("fox", "red fox in snow")
    assert got[1] == ("002_a-lighthouse-at-dusk", "A lighthouse at dusk")
    assert got[2][1] == "name |"  # "tên |" không có prompt thì cả dòng là prompt


def test_parse_blocks_gom_dong_va_bo_chu_thich(tmp_path):
    f = tmp_path / "q.txt"
    f.write_text("# c\nmột\nhai\n\nba\n\n\nbốn", encoding="utf-8")
    assert common.parse_blocks(f) == ["một hai", "ba", "bốn"]


def test_write_md_co_ghi_chu_chua_kiem_chung(tmp_path):
    p = common.write_md(tmp_path / "sub" / "r.md", "Tiêu đề", {"Nguồn": "x"}, common.UNVERIFIED_NOTE, "nội dung")
    t = p.read_text(encoding="utf-8")
    assert t.startswith("# Tiêu đề")
    assert "chưa được kiểm chứng" in t and "- Nguồn: x" in t and t.rstrip().endswith("nội dung")


def test_parse_payload_lay_json_trong_phong_bi():
    text = 'Untrusted page content follows.\n<<<x>>>\n{"a": 1, "b": {"c": "}"}}\n<<<y>>>'
    assert parse_payload(text) == {"a": 1, "b": {"c": "}"}}
    assert parse_payload("không có json") == {}


def test_last_reply_cat_phan_chan_trang():
    full = "x\nChatGPT said:\ncũ\nYou said:\nhỏi\nChatGPT said:\nTrả lời mới\nChatGPT can make mistakes. Check.\nLatest response"
    assert chatgpt.last_reply(full) == "Trả lời mới"
    assert chatgpt.last_reply("chưa có trả lời") == ""


def test_build_review_prompt_co_ten_va_khung_code():
    p = chatgpt.build_review_prompt("Hãy review", "retro.md", "# Tiêu đề")
    assert p.startswith("Hãy review") and "retro.md" in p and "```markdown\n# Tiêu đề\n```" in p


ROWS = [
    {"id": "1111", "title": "a", "privacy": "Only me", "more_selector": "#b1"},
    {"id": "2222", "title": "b", "privacy": "Everyone", "more_selector": "#b2"},
    {"id": "⟦card:x⟧…3333", "title": "c", "privacy": "Only me", "more_selector": None},
    {"id": "11112", "title": "d", "privacy": "Only me", "more_selector": "#b4"},
    {"id": "4444", "title": "e", "privacy": "Only me", "more_selector": "#b5"},
]


def test_delete_chi_xoa_bai_rieng_tu_khop_dung_mot_dong():
    assert tiktok.check_delete(ROWS, "4444", False)["title"] == "e"
    assert tiktok.check_delete(ROWS, "2222", True)["title"] == "b"  # công khai chỉ khi có --allow-public


@pytest.mark.parametrize("pid,allow", [
    ("2222", False),   # bài công khai
    ("9999", False),   # không có dòng nào
    ("111", False),    # id thiếu số: trước đây khớp kiểu "chứa trong", nay phải khớp đúng
    ("3333", True),    # id bị che, không có nút "…"
])
def test_delete_tu_choi(pid, allow):
    with pytest.raises(SystemExit):
        tiktok.check_delete(ROWS, pid, allow)


def test_delete_khop_id_chinh_xac():
    assert tiktok.check_delete(ROWS, "1111", False)["title"] == "a"   # không lẫn với 11112


def _el(y, **kw):
    return {"bounds": {"x": 1400, "y": y, "width": 34, "height": 20}, **kw}


def test_ghep_dong_theo_toa_do_khong_theo_thu_tu():
    links = [_el(100, href="/video/1", text="a"), _el(200, href="/video/2", text="b"), _el(300, href="/video/3", text="c")]
    # dòng giữa thiếu cả nút quyền xem lẫn nút "…": ghép theo chỉ số sẽ đẩy nút của dòng 3 lên dòng 2
    priv = [_el(300, text="Everyone"), _el(100, text="Only me")]
    mores = [_el(102, selector="#m1"), _el(301, selector="#m3")]
    rows = tiktok.pair_rows(links, priv, mores)
    assert [(r["id"], r["privacy"], r["more_selector"]) for r in rows] == [
        ("1", "Only me", "#m1"), ("2", "?", None), ("3", "Everyone", "#m3")]
    with pytest.raises(SystemExit):
        tiktok.check_delete(rows, "2", True)


def test_create_mac_dinh_rieng_tu():
    tiktok.check_create("private", False)
    with pytest.raises(SystemExit):
        tiktok.check_create("public", False)
    tiktok.check_create("public", True)


def test_flow_session_file_from_flag_or_env(monkeypatch, tmp_path):
    monkeypatch.delenv("WEBAUTO_FLOW_SESSION", raising=False)
    assert flow.session_file() is None
    monkeypatch.setenv("WEBAUTO_FLOW_SESSION", str(tmp_path / "env.json"))
    assert flow.session_file() == tmp_path / "env.json"
    assert flow.session_file(str(tmp_path / "flag.json")) == tmp_path / "flag.json"


def test_flow_missing_session_file_stops_before_browser(tmp_path):
    with pytest.raises(SystemExit, match="export-session"):
        flow.launch(None, session=str(tmp_path / "none.json"))


def test_flow_image_can_mode_video():
    with pytest.raises(SystemExit):
        flow.generate([("a", "b")], "out", mode="image", image="x.png")


def test_cli_dung_duoc_moi_lenh():
    p = cli.build_parser()
    g = p.parse_args(["flow", "generate", "--prompt", "x"])
    assert (g.mode, g.count, g.duration, g.quality) == ("image", 1, 6, "720p")
    v = p.parse_args(["flow", "generate", "--mode", "video", "--image", "a.png", "--prompts-file", "f"])
    assert v.mode == "video" and v.image == "a.png"
    assert p.parse_args(["chatgpt", "images", "--prompts-file", "f"]).gap == 5
    assert p.parse_args(["chatgpt", "ask", "--file", "d.md"]).file == "d.md"
    assert p.parse_args(["muse", "research", "--questions", "q", "--out", "o"]).min_chars == 1500
    assert p.parse_args(["tiktok", "create", "--video", "v.mp4"]).privacy == "private"
    with pytest.raises(SystemExit):
        p.parse_args(["tiktok", "delete"])  # thiếu --id
    with pytest.raises(SystemExit):
        p.parse_args(["flow", "generate"])  # thiếu --prompt / --prompts-file


def test_browsentic_server_params_theo_bien_moi_truong(monkeypatch):
    pytest.importorskip("mcp")
    from webauto.browsentic import server_params
    monkeypatch.setenv("WEBAUTO_BROWSENTIC_CMD", "browsentic mcp")
    sp = server_params()
    assert (sp.command, sp.args) == ("browsentic", ["mcp"])


def test_home_theo_bien_moi_truong(monkeypatch, tmp_path):
    monkeypatch.setenv("WEBAUTO_HOME", str(tmp_path))
    assert common.profile_dir("flow") == tmp_path / "profiles" / "flow"
    assert (tmp_path / "profiles" / "flow").is_dir()


def test_nap_cli_khong_keo_mcp_va_playwright():
    """`python -m webauto --help` phải chạy trên máy chưa cài hai thư viện nặng: chỉ import khi dùng."""
    import subprocess
    import sys
    code = ("import sys, webauto.cli; "
            "sys.exit(1 if ('mcp' in sys.modules or 'playwright' in sys.modules) else 0)")
    assert subprocess.run([sys.executable, "-c", code]).returncode == 0
    assert muse.URL.startswith("https://") and json.loads("{}") == {}


# ---- đăng nhập: chờ chủ máy tự đăng nhập, không bao giờ tự nhập mật khẩu -----------------------------------

def test_auth_da_dang_nhap_thi_di_tiep():
    import asyncio
    from webauto import auth
    said = []
    asyncio.run(auth.ensure(lambda: _async(True), "Site", "https://x", wait_s=5, say=said.append))
    assert said == []


async def _async(v):
    return v


def test_auth_cho_den_khi_dang_nhap_roi_tiep_tuc():
    import asyncio
    from webauto import auth
    calls, said = [], []

    async def check():
        calls.append(1)
        return len(calls) >= 3  # lần 1 chưa, lần 2 chưa, lần 3 đã đăng nhập

    asyncio.run(auth.ensure(check, "Site", "https://x", wait_s=5, poll=0, say=said.append))
    assert len(calls) == 3
    assert "not signed in" in said[0] and "continuing" in said[-1]


def test_auth_wait_0_bao_loi_ngay_va_noi_ro_khong_tu_nhap_mat_khau():
    import asyncio
    from webauto import auth
    with pytest.raises(auth.LoginRequired) as e:
        asyncio.run(auth.ensure(lambda: _async(False), "ChatGPT", "https://chatgpt.com/", wait_s=0))
    msg = str(e.value)
    assert "ChatGPT" in msg and "https://chatgpt.com/" in msg and "never enters passwords" in msg
    assert isinstance(e.value, SystemExit)  # thoát gọn với thông báo, không in traceback


def test_auth_het_gio_cho_thi_bao_loi():
    import asyncio
    from webauto import auth
    with pytest.raises(auth.LoginRequired) as e:
        asyncio.run(auth.ensure(lambda: _async(False), "Muse", "https://muse.ai/", wait_s=0.05, poll=0.01, say=lambda m: None))
    assert "waited" in str(e.value)


def test_auth_sync_cho_playwright():
    from webauto import auth
    n = []

    def check():
        n.append(1)
        return len(n) >= 2

    auth.ensure_sync(check, "Flow", "https://flow.google.com/", wait_s=5, poll=0, say=lambda m: None)
    assert len(n) == 2
    with pytest.raises(auth.LoginRequired):
        auth.ensure_sync(lambda: False, "Flow", "https://flow.google.com/", wait_s=0)


def test_auth_nhan_biet_chua_dang_nhap():
    from webauto import auth
    assert auth.chatgpt_signed_out("ChatGPT Log in Sign up for free Ask ChatGPT")
    assert auth.chatgpt_signed_out("Just a moment... Verify you are human")  # Cloudflare: chủ máy tự xử lý
    assert not auth.chatgpt_signed_out("New chat Library Recents Create Coffee Image Plus")
    assert auth.url_is_login("https://accounts.google.com/v3/signin/identifier")
    assert auth.url_is_login("https://www.tiktok.com/login?redirect=x")
    assert not auth.url_is_login("https://studio.youtube.com/channel/UCabc")


def test_cli_wait_login_toan_cuc(monkeypatch):
    from webauto import auth
    p = cli.build_parser()
    assert p.parse_args(["tiktok", "list"]).wait_login == auth.WAIT_LOGIN
    assert p.parse_args(["--wait-login", "30", "tiktok", "list"]).wait_login == 30
    seen = {}
    monkeypatch.setattr(auth, "configure", lambda s: seen.setdefault("w", s))
    monkeypatch.setattr("webauto.tiktok.list_posts", lambda a: None)
    monkeypatch.setattr("webauto.tiktok.run", lambda coro: None)
    cli.main(["--wait-login", "7", "tiktok", "list"])
    assert seen["w"] == 7


# ---- Flow: gỡ dấu ✦ ở góc (imagefix). Không mở trình duyệt. ---------------------------------------------

# Pillow + opencv nằm trong extra `webauto`: máy chưa cài thì bỏ qua thay vì báo lỗi.
needs_imaging = pytest.mark.skipif(
    importlib.util.find_spec("cv2") is None or importlib.util.find_spec("PIL") is None,
    reason="cần extra webauto (pillow, opencv-python-headless)")


def _scene(w, h, kind):
    """Nền có vân. kind: diamond (✦ 4 cánh cong), circle, rhombus (thoi thẳng), none."""
    import numpy as np
    from PIL import Image, ImageDraw

    yy, xx = np.mgrid[0:h, 0:w]
    rgb = np.zeros((h, w, 3), np.uint8)
    rgb[:, :, 0] = np.clip(36 + 28 * np.sin(xx / 41.0) + 14 * np.cos(yy / 23.0), 0, 255)
    rgb[:, :, 1] = np.clip(48 + 16 * np.cos(xx / 33.0) + 8 * np.sin(yy / 19.0), 0, 255)
    rgb[:, :, 2] = np.clip(32 + 10 * np.sin((xx + yy) / 29.0), 0, 255)
    base = Image.fromarray(rgb, "RGB")
    if kind == "none":
        return base
    cx, cy = int(round(0.928 * w)), int(round(0.873 * h))
    r = max(16, int(round(0.017 * w)))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    if kind == "diamond":
        # 4 cánh cong: mũi trên 4 trục, eo kéo vào. Không phải hình thoi thẳng.
        inn = r * 0.40
        draw.polygon(
            [(cx, cy - r), (cx + inn, cy - inn), (cx + r, cy), (cx + inn, cy + inn),
             (cx, cy + r), (cx - inn, cy + inn), (cx - r, cy), (cx - inn, cy - inn)],
            fill=(255, 255, 255, 160))
    elif kind == "rhombus":
        draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=(255, 255, 255, 160))
    else:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 160))
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB"), (cx, cy, r)


def _save_jpg(im, path):
    im.save(path, format="JPEG", quality=90)


@needs_imaging
def test_find_mark_thay_kim_cuong_va_fill_dua_vung_ve_nen(tmp_path):
    import numpy as np
    from PIL import Image

    from webauto.imagefix import find_mark, strip_mark

    w, h = 1280, 720
    im, (cx, cy, r) = _scene(w, h, "diamond")
    path = tmp_path / "mark.jpg"
    _save_jpg(im, path)
    box = find_mark(Image.open(path))
    assert box is not None
    x0, y0, x1, y1 = box
    assert x0 <= cx <= x1 and y0 <= cy <= y1
    assert x0 > w * 0.7 and y0 > h * 0.6  # chỉ góc phải dưới

    before = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    strip_mark(path, "fill")
    after = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    assert after.shape == before.shape

    def core(arr):
        return arr[cy - r // 3:cy + r // 3, cx - r // 3:cx + r // 3].mean()

    # vòng ngay ngoài hình thoi, không dính dấu
    ring = before[cy - r - 8:cy - r - 2, cx - 6:cx + 6].mean()
    assert core(before) > ring + 25
    assert abs(core(after) - ring) < 15
    # vá xong thì lần dò sau không còn thấy dấu
    assert find_mark(Image.open(path)) is None


@needs_imaging
def test_khong_co_dau_thi_khong_doi_file(tmp_path):
    import hashlib
    from PIL import Image

    from webauto.imagefix import find_mark, strip_mark

    im = _scene(1280, 720, "none")
    path = tmp_path / "clean.jpg"
    _save_jpg(im, path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert find_mark(Image.open(path)) is None
    assert strip_mark(path, "fill") == path
    assert strip_mark(path, "crop") == path
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest

    # vệt tròn trắng ở cùng góc không phải dấu ✦
    circle, _ = _scene(1280, 720, "circle")
    cpath = tmp_path / "circle.jpg"
    _save_jpg(circle, cpath)
    raw = cpath.read_bytes()
    assert find_mark(Image.open(cpath)) is None
    strip_mark(cpath, "fill")
    assert cpath.read_bytes() == raw


@needs_imaging
def test_crop_giu_ti_le_16_9(tmp_path):
    from PIL import Image

    from webauto.imagefix import strip_mark

    w, h = 1280, 720  # đúng 16:9
    im, (cx, cy, _r) = _scene(w, h, "diamond")
    path = tmp_path / "wide.jpg"
    _save_jpg(im, path)
    strip_mark(path, "crop")
    w2, h2 = Image.open(path).size
    assert w2 < w and h2 < h
    assert abs(w2 - h2 * 16 / 9) <= 1
    # dấu nằm ngoài khung đã cắt
    assert cx >= w2 or cy >= h2


@needs_imaging
def test_keep_raw_chi_khi_co_sua(tmp_path):
    from webauto.flow import finish_image

    marked, _ = _scene(960, 540, "diamond")
    path = tmp_path / "a.jpg"
    _save_jpg(marked, path)
    original = path.read_bytes()
    finish_image(path, "fill", keep_raw=True)
    raw = tmp_path / "a_raw.jpg"
    assert raw.read_bytes() == original
    assert path.read_bytes() != original

    clean = _scene(960, 540, "none")
    other = tmp_path / "b.jpg"
    _save_jpg(clean, other)
    untouched = other.read_bytes()
    finish_image(other, "fill", keep_raw=True)
    assert other.read_bytes() == untouched
    assert not (tmp_path / "b_raw.jpg").exists()
    finish_image(other, "off", keep_raw=True)
    assert other.read_bytes() == untouched


def test_cli_strip_mark_mac_dinh_crop():
    p = cli.build_parser()
    g = p.parse_args(["flow", "generate", "--prompt", "x"])
    assert g.strip_mark == "crop" and g.keep_raw is False
    c = p.parse_args(["flow", "generate", "--prompt", "x", "--strip-mark", "fill", "--keep-raw"])
    assert c.strip_mark == "fill" and c.keep_raw is True
    assert p.parse_args(["flow", "generate", "--prompt", "x", "--strip-mark", "off"]).strip_mark == "off"


def _paste(base, draw_fn):
    from PIL import Image

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_fn(overlay)
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


@needs_imaging
def test_find_mark_bo_sao_cham_net_va_thoi_thang():
    """Sao, chấm, vệt nến và hình thoi thẳng không phải dấu ✦. Dấu 4 cánh cong thì thấy."""
    import math

    from PIL import Image, ImageDraw

    from webauto.imagefix import find_mark

    w, h = 1280, 720
    base = _scene(w, h, "none")
    cx, cy = int(round(0.928 * w)), int(round(0.873 * h))
    r = max(16, int(round(0.017 * w)))

    def star(n_pts, inner):
        def draw(overlay, n_pts=n_pts, inner=inner):
            d = ImageDraw.Draw(overlay)
            pts = []
            for i in range(n_pts * 2):
                ang = -math.pi / 2 + i * math.pi / n_pts
                rad = r if i % 2 == 0 else r * inner
                pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
            d.polygon(pts, fill=(255, 255, 255, 230))
        return draw

    def dot(overlay):
        ImageDraw.Draw(overlay).ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=(255, 245, 210, 255))

    def candle(overlay):
        ImageDraw.Draw(overlay).rectangle((cx - 4, cy - 16, cx + 5, cy + 17), fill=(255, 226, 145, 255))

    cases = {
        "star8": star(8, 0.45),
        "star5": star(5, 0.40),
        "dot": dot,
        "candle": candle,
    }
    for name, draw in cases.items():
        assert find_mark(_paste(base, draw)) is None, name

    rhombus, _ = _scene(w, h, "rhombus")
    assert find_mark(rhombus) is None

    # Đúng hình Codex review từng nhận nhầm: sao 8 đỉnh, nền phẳng, lệch khỏi tâm dấu.
    flat = Image.new("RGB", (w, h), (38, 38, 38))
    d = ImageDraw.Draw(flat)
    d.polygon(
        [(1240, 620), (1244, 628), (1252, 632), (1244, 636),
         (1240, 644), (1236, 636), (1228, 632), (1236, 628)],
        fill=(255, 255, 255))
    assert find_mark(flat) is None

    marked, (mx, my, _r) = _scene(w, h, "diamond")
    box = find_mark(marked)
    assert box is not None
    x0, y0, x1, y1 = box
    assert x0 <= mx <= x1 and y0 <= my <= y1


@needs_imaging
def test_known_flow_crop_nen_trang_cat_vung_dau(tmp_path):
    """Ảnh Flow vừa tải luôn bị cắt góc, kể cả nền trắng không có dấu nhìn thấy."""
    from PIL import Image

    from webauto.imagefix import find_mark, fixed_mark_box, image_mark_box, strip_mark

    w, h = 1376, 768
    path = tmp_path / "white.jpg"
    Image.new("RGB", (w, h), (255, 255, 255)).save(path, quality=95)
    raw = path.read_bytes()
    assert find_mark(path) is None
    assert strip_mark(path, "crop") == path
    assert path.read_bytes() == raw

    box = fixed_mark_box(w, h)
    assert box == (1243, 634, 1315, 706)
    assert image_mark_box(w, h) == box
    strip_mark(path, "crop", known_flow=True)
    w2, h2 = Image.open(path).size
    assert (w2, h2) == (1242, 693)  # chỉ cần kết thúc bên trái HOẶC phía trên hộp
    assert w2 <= box[0] or h2 <= box[1]
    assert abs(w2 - h2 * w / h) <= 1
    assert find_mark(path) is None


@needs_imaging
def test_known_flow_fill_khong_thay_khong_sua(tmp_path, capsys):
    from PIL import Image

    from webauto.imagefix import strip_mark

    path = tmp_path / "white.jpg"
    Image.new("RGB", (w := 960, h := 540), (250, 250, 250)).save(path, quality=95)
    raw = path.read_bytes()
    assert strip_mark(path, "fill", known_flow=True) == path
    assert path.read_bytes() == raw
    assert "không thấy" in capsys.readouterr().err
    assert strip_mark(path, "fill") == path
    assert path.read_bytes() == raw
    assert capsys.readouterr().err == ""


@needs_imaging
def test_ba_goc_bo_sot_crop_known_flow(tmp_path):
    """Góc phải dưới của 3 ảnh Lead bỏ sót. Gỗ và dốc xám thì thấy; khung tranh thì không.
    crop known_flow vẫn cắt hộp cố định ở cả ba.
    """
    from PIL import Image

    from webauto.imagefix import find_mark, fixed_mark_box, strip_mark

    root = Path(__file__).resolve().parent / "fixtures" / "flow_mark"
    w, h = 1376, 768
    paste_at = (1080, 520)  # đúng ô đã cắt từ khung 1376×768
    expect = {
        "y3_a_2_1_cf53849a_corner.png": (1251, 644, 1306, 699),
        "y3_b_1_1_2da2e0e4_corner.png": (1251, 642, 1306, 697),
        "y3_c_2_1_ae90c419_corner.png": None,
    }
    box = fixed_mark_box(w, h)
    for name, seen in expect.items():
        corner = Image.open(root / name).convert("RGB")
        canvas = Image.new("RGB", (w, h), (30, 30, 30))
        canvas.paste(corner, paste_at)
        assert find_mark(canvas) == seen, name
        path = tmp_path / name
        canvas.save(path, format="PNG")
        if seen is None:
            raw = path.read_bytes()
            assert strip_mark(path, "crop") == path
            assert path.read_bytes() == raw
        strip_mark(path, "crop", known_flow=True)
        w2, h2 = Image.open(path).size
        assert w2 <= box[0] or h2 <= box[1]
        assert abs(w2 - h2 * w / h) <= 1
        assert find_mark(path) is None


@needs_imaging
def test_finish_image_crop_cat_ca_khi_khong_thay_dau(tmp_path):
    from PIL import Image

    from webauto.flow import finish_image

    path = tmp_path / "a.jpg"
    Image.new("RGB", (1376, 768), (255, 255, 255)).save(path, quality=90)
    original = path.read_bytes()
    finish_image(path, "crop", keep_raw=True)
    assert (tmp_path / "a_raw.jpg").read_bytes() == original
    w2, h2 = Image.open(path).size
    assert (w2, h2) == (1242, 693)


# ---- Flow: tải ảnh 2K (menu Download > 2K Upscaled) ---------------------------------------------------

def test_image_size_mac_dinh_2k_co_cua_so_1k_khi_chay_an():
    assert flow.image_size_for(None, headless=False) == "2K"
    assert flow.image_size_for(None, headless=True) == "1K"
    assert flow.image_size_for("1K", headless=True) == "1K"
    assert flow.image_size_for("2K", headless=False) == "2K"
    with pytest.raises(SystemExit, match="cửa sổ"):
        flow.image_size_for("2K", headless=True)  # chạy ẩn Flow báo "Upscaling failed!"


def test_cli_image_size():
    p = cli.build_parser()
    assert p.parse_args(["flow", "generate", "--prompt", "x"]).image_size is None
    assert p.parse_args(["flow", "generate", "--prompt", "x", "--image-size", "2K"]).image_size == "2K"
    with pytest.raises(SystemExit):
        p.parse_args(["flow", "generate", "--prompt", "x", "--image-size", "4K"])  # cần gói cao hơn


def test_image_mark_box_theo_canh_dai_va_2k():
    """Đo 06/11 trên ảnh thật: 1K dấu cách phải 97, đáy 98 px cả ngang lẫn dọc; 2K cách 113/114 px, cỡ giữ nguyên."""
    pytest.importorskip("numpy")
    from webauto.imagefix import image_mark_box

    for w, h, dx, dy in [(1376, 768, 97, 98), (768, 1376, 97, 98), (2752, 1536, 113, 114), (1536, 2752, 113, 114)]:
        x0, y0, x1, y1 = image_mark_box(w, h)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        assert abs((w - cx) - dx) <= 1 and abs((h - cy) - dy) <= 1, (w, h)
        assert 70 <= x1 - x0 <= 73, (w, h)  # 55 px + lề 8 px mỗi bên, không phóng ×2 ở 2K


def test_video_crop_van_cat_ca_hai_mep():
    """Video giữ luật cũ (cắt phải VÀ dưới): dấu 1080p nằm lùi ~180 px, ngoài hộp fixed_mark_box."""
    pytest.importorskip("numpy")
    from webauto.imagefix import _crop_size, fixed_mark_box

    box = fixed_mark_box(1920, 1080)
    cw, ch = _crop_size(1920, 1080, box, either=False)
    assert (cw, ch) == (1586, 892)
    assert cw < 1920 - 180 - 40  # mép trái dấu 1080p (tâm cách phải 180 px, rộng ~70 px)
    assert _crop_size(1920, 1080, box)[0] > cw  # ảnh: chỉ cần trái HOẶC trên


@needs_imaging
@pytest.mark.parametrize("w,h,shift,expect", [
    (768, 1376, 0, (693, 1242)),      # 1K dọc 9:16
    (2752, 1536, 16, (2602, 1452)),   # 2K ngang 16:9: dấu lùi vào 16 px
    (1536, 2752, 16, (1452, 2602)),   # 2K dọc 9:16
])
def test_dau_that_o_khung_doc_va_2k(tmp_path, w, h, shift, expect):
    """Dán góc ảnh Flow thật (dấu cách mép 97/98 px) vào khung khác cỡ: dò thấy, cắt sạch, giữ tỉ lệ."""
    from PIL import Image

    from webauto.imagefix import find_mark, image_mark_box, strip_mark

    root = Path(__file__).resolve().parent / "fixtures" / "flow_mark"
    corner = Image.open(root / "y3_a_2_1_cf53849a_corner.png").convert("RGB")
    canvas = Image.new("RGB", (w, h), (30, 30, 30))
    canvas.paste(corner, (w - corner.width - shift, h - corner.height - shift))
    seen = find_mark(canvas)
    assert seen is not None
    box = image_mark_box(w, h)
    assert box[0] <= seen[0] and box[1] <= seen[1] and seen[2] <= box[2] + 2 and seen[3] <= box[3] + 2
    path = tmp_path / "x.png"
    canvas.save(path)
    strip_mark(path, "crop", known_flow=True)
    w2, h2 = Image.open(path).size
    assert (w2, h2) == expect
    assert w2 <= seen[0] or h2 <= seen[1]
    assert abs(w2 - h2 * w / h) <= 1
    assert find_mark(path) is None


@needs_imaging
@pytest.mark.parametrize("w,h", [
    (1024, 1024),   # 1:1, dấu ở 97/98 px như 1K đo được
    (1376, 1376),   # 1:1 cạnh dài 1376
    (1184, 888),    # 4:3
    (888, 1184),    # 3:4
])
def test_khung_chua_do_cat_ca_hai_mep_va_bo_het_loi_dau(tmp_path, w, h):
    """Tỉ lệ/cỡ chưa đo (1:1, 4:3, 3:4): cắt phải VÀ dưới, lõi dấu ở 97/98 px phải mất hết."""
    from PIL import Image

    from webauto.imagefix import find_mark, measured_frame, strip_mark

    assert not measured_frame(w, h)
    root = Path(__file__).resolve().parent / "fixtures" / "flow_mark"
    corner = Image.open(root / "y3_a_2_1_cf53849a_corner.png").convert("RGB")
    canvas = Image.new("RGB", (w, h), (30, 30, 30))
    canvas.paste(corner, (w - corner.width, h - corner.height))  # tâm dấu cách phải 97, đáy 98 px
    path = tmp_path / "x.png"
    canvas.save(path)
    strip_mark(path, "crop", known_flow=True)
    w2, h2 = Image.open(path).size
    cx, cy, core = w - 97, h - 98, 24  # lõi + cánh ~48 px
    assert w2 <= cx - core and h2 <= cy - core  # hai mép đều ở ngoài dấu
    assert abs(w2 - h2 * w / h) <= 1
    assert find_mark(path) is None


def test_measured_frame_chi_1k_2k_16_9_va_9_16():
    pytest.importorskip("numpy")
    from webauto.imagefix import measured_frame

    for wh in [(1376, 768), (768, 1376), (2752, 1536), (1536, 2752), (2753, 1536)]:
        assert measured_frame(*wh), wh
    for wh in [(1024, 1024), (1280, 720), (1184, 888), (1920, 1080), (2048, 2048)]:
        assert not measured_frame(*wh), wh


@needs_imaging
def test_keep_raw_ten_file_2k(tmp_path):
    from PIL import Image

    from webauto.flow import finish_image

    path = tmp_path / "rice_1_5af1a83b_2K.jpg"
    Image.new("RGB", (2752, 1536), (255, 255, 255)).save(path, quality=90)
    original = path.read_bytes()
    finish_image(path, "crop", keep_raw=True)
    assert (tmp_path / "rice_1_5af1a83b_2K_raw.jpg").read_bytes() == original
    assert Image.open(path).size == (2602, 1452)


def test_ten_muc_tai_anh_neo_dau_chuoi():
    pat = flow.size_item_name("2K")
    assert pat.search("2K Upscaled") and pat.search("2K\nUpscaled")
    assert not pat.search("12K Upscaled") and not pat.search("download Download")
    assert not pat.search("4K Upscaled 2K")
    assert flow.size_item_name("1K").search("1K Original size")


class _FakeLoc:
    """Locator giả: lọc theo role/name trên một cây phần tử nhỏ."""

    def __init__(self, items):
        self.items = items

    def count(self):
        return len(self.items)

    @property
    def last(self):
        return _FakeLoc(self.items[-1:])

    @property
    def first(self):
        return _FakeLoc(self.items[:1])

    def get_by_role(self, role, name=None):
        found = []
        for it in self.items:
            found += _match(it.get("children", []), role, name)
        return _FakeLoc(found)


def _match(nodes, role, name):
    out = []
    for n in nodes:
        if n["role"] == role and (name is None or name.search(n["name"])):
            out.append(n)
        out += _match(n.get("children", []), role, name)
    return out


class _FakePage:
    def __init__(self, tree):
        self.tree = tree

    def get_by_role(self, role, name=None):
        return _FakeLoc(_match(self.tree, role, name))


def test_chon_muc_trong_menu_con_download():
    """Ưu tiên mục trong menu con đang mở (menu mở sau cùng), không lấy mục trùng tên ở chỗ khác."""
    stray = {"role": "menuitem", "name": "2K Upscaled", "id": "stray"}
    main = {"role": "menu", "name": "", "children": [
        {"role": "menuitem", "name": "Download"}, stray]}
    sub = {"role": "menu", "name": "", "children": [
        {"role": "menuitem", "name": "1K Original size", "id": "1k"},
        {"role": "menuitem", "name": "2K Upscaled", "id": "2k"},
        {"role": "menuitem", "name": "4K Upscaled", "id": "4k"}]}
    page = _FakePage([main, sub])
    assert flow.size_menu_item(page, "2K").items[0]["id"] == "2k"
    assert flow.size_menu_item(page, "1K").items[0]["id"] == "1k"
    # không có menu con: lấy mục đầu trang có tên bắt đầu bằng cỡ
    only = _FakePage([{"role": "menuitem", "name": "2K Upscaled", "id": "x"}])
    assert flow.size_menu_item(only, "2K").items[0]["id"] == "x"


def test_cli_flow_shots_parser():
    p = cli.build_parser()
    args = p.parse_args(["flow", "shots", "--ref", "monk.png", "--shots", "shots.txt", "--out", "out_dir"])
    assert args.ref == "monk.png"
    assert args.shots == "shots.txt"
    assert args.out == "out_dir"
    assert args.model == "omni1.1"
    assert args.max_per_project == 2
    assert args.quality == "1080p"

    args12 = p.parse_args(["flow", "shots", "--ref", "monk.png", "--shots", "shots.txt", "--model", "omni12"])
    assert args12.model == "omni12"


def test_resolve_model_info():
    assert flow.resolve_model_info(None) == ("Omni 1.1 Flash", 10, 6)
    assert flow.resolve_model_info("omni1.1") == ("Omni 1.1 Flash", 10, 6)
    assert flow.resolve_model_info("omni12") == ("Omni 1.2 Flash", 24, 8)
    assert flow.resolve_model_info("omni1.2") == ("Omni 1.2 Flash", 24, 8)


def test_parse_shots_file_valid_and_custom_frames(tmp_path):
    ref_img = tmp_path / "ref.png"
    ref_img.write_text("fake ref")
    custom_img = tmp_path / "custom.png"
    custom_img.write_text("fake custom")

    shots_file = tmp_path / "shots.txt"
    shots_file.write_text(
        f"# Comment line\n\n"
        f"shot01 | A monk smiles peacefully\n"
        f"shot02 | The monk turns his head | frame={custom_img.name}\n"
        f"shot03 | frame={custom_img.name} | The monk raises his hand\n"
    )

    shots = flow.parse_shots_file(shots_file, str(ref_img))
    assert len(shots) == 3
    assert shots[0]["name"] == "shot01"
    assert shots[0]["prompt"] == "A monk smiles peacefully"
    assert shots[0]["frame"] == str(ref_img.resolve())

    assert shots[1]["name"] == "shot02"
    assert shots[1]["prompt"] == "The monk turns his head"
    assert shots[1]["frame"] == str(custom_img.resolve())

    assert shots[2]["name"] == "shot03"
    assert shots[2]["prompt"] == "The monk raises his hand"
    assert shots[2]["frame"] == str(custom_img.resolve())


def test_parse_shots_file_missing_frame_raises(tmp_path):
    ref_img = tmp_path / "ref.png"
    ref_img.write_text("fake ref")
    shots_file = tmp_path / "shots.txt"
    shots_file.write_text("shot01 | A monk | frame=non_existent.png\n")

    with pytest.raises(SystemExit, match="frame image not found"):
        flow.parse_shots_file(shots_file, str(ref_img))


def test_generate_five_clips_auto_new_project(tmp_path, monkeypatch, capsys):
    """Chứng minh chạy 5 clip liền một lệnh: tự mở project mới sau mỗi 2 clip và luôn gắn ref cho từng clip."""
    calls = {"new_project": 0, "apply_settings": 0, "set_start_frame": 0, "generate_video": 0}

    class FakePage:
        pass

    class FakeCtx:
        pages = [FakePage()]
        def close(self):
            pass

    class FakeBrowser:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr(flow, "launch", lambda p, headless, session: FakeCtx())

    def fake_new_project(page, headless=False):
        calls["new_project"] += 1

    def fake_apply_settings(page, mode, model=None, count=1, duration=6, ratio=None, res=None):
        calls["apply_settings"] += 1

    def fake_set_start_frame(page, image):
        calls["set_start_frame"] += 1

    def fake_generate_video(page, prompt, out, tag, quality="720p", timeout_s=900, strip_mark="crop", keep_raw=False):
        calls["generate_video"] += 1
        f = out / f"{tag}_1_{quality}.mp4"
        f.write_text("fake video bytes")
        return [f]

    monkeypatch.setattr(flow, "new_project", fake_new_project)
    monkeypatch.setattr(flow, "apply_settings", fake_apply_settings)
    monkeypatch.setattr(flow, "set_start_frame", fake_set_start_frame)
    monkeypatch.setattr(flow, "verify_start_frame_chip", lambda page: True)
    monkeypatch.setattr(flow, "generate_video", fake_generate_video)

    import playwright.sync_api
    monkeypatch.setattr(playwright.sync_api, "sync_playwright", lambda: FakeBrowser())

    prompts = [
        ("s1", "clip 1 prompt"),
        ("s2", "clip 2 prompt"),
        ("s3", "clip 3 prompt"),
        ("s4", "clip 4 prompt"),
        ("s5", "clip 5 prompt"),
    ]
    ref_img = tmp_path / "ref.png"
    ref_img.write_text("ref")

    out_dir = tmp_path / "out_5clips"
    saved = flow.generate(prompts, out_dir, mode="video", image=str(ref_img), max_per_project=2)

    assert len(saved) == 5
    # 5 clips with max_per_project=2 -> 3 projects (clip 1-2, clip 3-4, clip 5)
    assert calls["new_project"] == 3
    assert calls["generate_video"] == 5
    assert calls["set_start_frame"] == 5  # ref được gắn cho MỌI clip
    out_text = capsys.readouterr().out
    assert "reached 2 clip(s) in project (max 2), opening new project..." in out_text


def test_shots_generate_five_shots_manifest(tmp_path, monkeypatch, capsys):
    """Chứng minh flow shots chạy 5 clip, gắn ref mọi shot, ghi manifest.json đầy đủ trường."""
    calls = {"new_project": 0, "generate_video": 0, "set_start_frame": 0}

    class FakePage:
        pass

    class FakeCtx:
        pages = [FakePage()]
        def close(self):
            pass

    class FakeBrowser:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr(flow, "launch", lambda p, headless, session: FakeCtx())
    monkeypatch.setattr(flow, "new_project", lambda page, headless=False: calls.update(new_project=calls["new_project"]+1))
    monkeypatch.setattr(flow, "apply_settings", lambda *args, **kw: None)
    monkeypatch.setattr(flow, "set_start_frame", lambda page, img: calls.update(set_start_frame=calls["set_start_frame"]+1))
    monkeypatch.setattr(flow, "verify_start_frame_chip", lambda page: True)
    from webauto import videofix
    monkeypatch.setattr(videofix, "_probe", lambda p: (1920, 1080))

    def fake_generate_video(page, prompt, out, tag, quality="1080p", timeout_s=900, strip_mark="crop", keep_raw=False):
        calls["generate_video"] += 1
        f = out / f"{tag}_1_{quality}.mp4"
        f.write_text("fake video bytes")
        return [f]

    monkeypatch.setattr(flow, "generate_video", fake_generate_video)

    import playwright.sync_api
    monkeypatch.setattr(playwright.sync_api, "sync_playwright", lambda: FakeBrowser())

    ref_img = tmp_path / "monk_ref.png"
    ref_img.write_text("ref")

    shots = [
        {"name": f"shot_0{i}", "prompt": f"Motion prompt {i}", "frame": str(ref_img)}
        for i in range(1, 6)
    ]
    out_dir = tmp_path / "shots_out"
    manifest_shots = flow.shots_generate(shots, out_dir, ref=str(ref_img), model="omni1.1", max_per_project=2)

    assert len(manifest_shots) == 5
    assert calls["new_project"] == 3
    assert calls["generate_video"] == 5
    assert calls["set_start_frame"] == 5  # Start frame được gán cho MỌI shot!

    manifest_file = out_dir / "manifest.json"
    assert manifest_file.exists()
    data = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert data["model"] == "Omni 1.1 Flash"
    assert data["estimated_credits_per_clip"] == 10
    assert data["total_estimated_credits"] == 50
    assert data["ai_generated"] is True
    assert "upscaled" in data
    assert len(data["shots"]) == 5
    for s in data["shots"]:
        assert s["ai_generated"] is True
        assert s["model"] == "Omni 1.1 Flash"
        assert s["estimated_credits"] == 10
        assert s["file"].endswith(".mp4")
        assert "prompt" in s
        assert "upscaled" in s


def test_shots_generate_aborts_when_start_frame_chip_fails(tmp_path, monkeypatch):
    """BLOCKER: nếu UI không xác nhận được chip khung đầu thì dừng shot với RuntimeError, không tạo text-to-video."""
    class FakePage:
        pass

    class FakeCtx:
        pages = [FakePage()]
        def close(self):
            pass

    class FakeBrowser:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr(flow, "launch", lambda p, headless, session: FakeCtx())
    monkeypatch.setattr(flow, "new_project", lambda page, headless=False: None)
    monkeypatch.setattr(flow, "apply_settings", lambda *args, **kw: None)
    monkeypatch.setattr(flow, "set_start_frame", lambda page, img: None)
    monkeypatch.setattr(flow, "verify_start_frame_chip", lambda page: False)  # chip failure!

    import playwright.sync_api
    monkeypatch.setattr(playwright.sync_api, "sync_playwright", lambda: FakeBrowser())

    ref_img = tmp_path / "monk_ref.png"
    ref_img.write_text("ref")
    shots = [{"name": "shot01", "prompt": "monk meditates", "frame": str(ref_img)}]

    with pytest.raises(RuntimeError, match="UI failed to confirm start frame chip"):
        flow.shots_generate(shots, tmp_path / "out", ref=str(ref_img))


def test_upscale_video_1080p_lanczos(tmp_path):
    """Kiểm tra hàm upscale_video_1080p sử dụng ffmpeg lanczos nâng 720p lên 1920x1080."""
    import subprocess
    from webauto.videofix import _probe, upscale_video_1080p
    # Tạo video test 720p 1s bằng ffmpeg
    sample_720p = tmp_path / "sample_720p.mp4"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=blue:s=1280x720:d=1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(sample_720p)
    ], check=True)

    w, h = _probe(sample_720p)
    assert (w, h) == (1280, 720)

    out_path, was_upscaled = upscale_video_1080p(sample_720p)
    assert was_upscaled is True
    w_new, h_new = _probe(out_path)
    assert (w_new, h_new) == (1920, 1080)

    # Nâng lần nữa -> đã 1080p nên was_upscaled là False
    _, re_upscaled = upscale_video_1080p(out_path)
    assert re_upscaled is False

