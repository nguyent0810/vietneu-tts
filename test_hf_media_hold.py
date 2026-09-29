"""Video dài giữ ảnh qua nhiều câu (media_holds trong bridge + nhánh media_cont
trong engine). Bản đầu của L_bud_01 để ảnh sống đúng một câu: 2/3 thời lượng
là thẻ chữ trên nền trơn, render vẫn báo "ok".
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / "hyperframes_short" / "compositions" / "engine.js"


def _media_holds():
    # Bóc hàm bằng ast thay vì import: import bridge kéo theo kiểm external_bin.
    src = (ROOT / "hyperframes_bridge.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    keep = [n for n in tree.body
            if (isinstance(n, ast.FunctionDef) and n.name == "media_holds")
            or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "HOLD_MAX_S" for t in n.targets))]
    ns: dict = {}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "bridge", "exec"), ns)
    return ns["media_holds"]


def _lines(n, step=5.0, headings=()):
    return [{"sentence_id": i + 1, "start": i * step, "end": (i + 1) * step,
             "heading": (i + 1) in headings} for i in range(n)]


def test_hold_until_next_media():
    holds = _media_holds()(_lines(6), {1, 4})
    assert holds == {0: 2, 3: 5}


def test_hold_stops_before_chapter_heading():
    holds = _media_holds()(_lines(6), {1}, max_span=99)
    assert holds == {0: 5}
    holds = _media_holds()(_lines(6, headings={3}), {1}, max_span=99)
    assert holds == {0: 1}


def test_hold_respects_time_cap():
    # 5 giây mỗi câu, trần 12 giây -> giữ được câu 2 (tới 10s), không tới câu 3 (15s)
    assert _media_holds()(_lines(6), {1}, max_span=12) == {0: 1}


def test_hold_stops_before_figure():
    lines = _lines(4)
    lines[2]["figure"] = {"type": "stat"}
    assert _media_holds()(lines, {1}, max_span=99) == {0: 1}


def test_engine_handles_continuation_scenes():
    js = ENGINE.read_text(encoding="utf-8")
    assert "ln.media_cont" in js, "engine không dựng cảnh nối tiếp -> câu sau hiện thẻ chữ đè ảnh"
    assert "ln.media_end || ln.end" in js, "clip phải tắt ở cuối khoảng giữ, không phải cuối câu gốc"


def test_stock_cache_key_depends_on_orientation(tmp_path, monkeypatch):
    # Ảnh dọc đã cache cho short không được quay lại cho video dài 16:9.
    import stock_image
    monkeypatch.setattr(stock_image, "CACHE_DIR", tmp_path)
    seen = []
    monkeypatch.setattr(stock_image, "search", lambda q, o: seen.append(o) or None)
    (tmp_path / f"img_{stock_image._query_hash('goat')}.jpg").write_bytes(b"x")
    monkeypatch.setattr(stock_image.asset_safety, "assert_asset_safe_for_assembly", lambda p: None)
    assert stock_image.get_or_fetch_stock_image("goat") is not None      # dọc: khoá cũ, trúng cache
    assert stock_image.get_or_fetch_stock_image("goat", "landscape") is None  # ngang: phải tìm lại
    assert seen == ["landscape"]
