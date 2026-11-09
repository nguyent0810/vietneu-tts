"""Bản đồ vector cho video dài (sơ đồ `map` của longform.js) -- nướng sẵn.

HyperFrames cấm mạng lúc render và cần tất định (skill motion-graphics, mục
maps, "vector lane"): biên giới được tải MỘT lần (world-atlas TopoJSON, cache
tại chunks_cache/geo/), giải mã, chiếu vào khung hình, rồi ghi thẳng đường SVG
+ toạ độ điểm vào plan lúc render. longform.js chỉ vẽ, không tính địa lý.

Quần đảo Hoàng Sa / Trường Sa là lớp riêng, lấy đúng hình `Paracel Is.` và
`Spratly Is.` trong Natural Earth 10m disputed areas (Public Domain). Chỉ vẽ
khi hình chiếu rơi vào khung 1920×1080 thật (Mercator của `_projector`), không
theo bbox khai báo.

    bake(spec) -> spec + "_geo": {countries, pins, islands}

spec: {"countries": ["India", "Nepal"], "context": ["China", ...],
       "bbox": [lon_min, lat_min, lon_max, lat_max],
       "pins": [{"name": "Lâm Tỳ Ni", "lon": 83.28, "lat": 27.48, "at": 12, ...}]}
Tên nước theo world-atlas (tiếng Anh, vd "India", "Nepal").
Thiếu bbox mà có Vietnam: dùng VN_NATIONAL_BBOX.
"""
from __future__ import annotations

import hashlib
import json
import math
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
CACHE = ROOT / "chunks_cache" / "geo" / "countries-50m.json"
SOURCE = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json"
# Khung vẽ bản đồ trong khung 1920x1080 (chừa đáy cho phụ đề, trái cho tiêu đề)
BOX = (150, 120, 1770, 860)
FRAME = (1920, 1080)
# #capzone của long: bottom 64px, phụ đề tới 2 dòng 44px × 1.38. Nhãn đảo không được chui xuống dưới.
CAP_TOP = 1080 - 64 - int(44 * 1.38 * 2)
# Bản đồ toàn quốc khi plan không khai bbox. Nới đông và nam để cả hai quần đảo vào khung.
VN_NATIONAL_BBOX = [102.0, 6.5, 118.0, 24.0]
ISLANDS_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_admin_0_disputed_areas.geojson"
ISLANDS_SHA256 = "9cafef8b7dfb6b164dc58f218f981f4ace9f716f6c03795d4c62d1ac9f3d50f5"
ISLANDS_CACHE = ROOT / "chunks_cache" / "geo" / "ne_10m_admin_0_disputed_areas.geojson"
# Khoá là thuộc tính NAME trong file (đối sha256 ở trên), không dịch, không đoán tên khác.
ISLAND_LABEL = {
    "Paracel Is.": "Quần đảo Hoàng Sa (Việt Nam)",
    "Spratly Is.": "Quần đảo Trường Sa (Việt Nam)",
}
_ISLANDS = None


def _topology() -> dict:
    if not CACHE.exists():
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(SOURCE, timeout=60) as r:
            CACHE.write_bytes(r.read())
    return json.loads(CACHE.read_text(encoding="utf-8"))


def _arcs(topo: dict) -> list[list[tuple[float, float]]]:
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    out = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:  # toạ độ lượng tử hoá, mã hoá delta
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        out.append(pts)
    return out


def _ring(arcs, idx: list[int]) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for i in idx:
        seg = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(seg[1:] if pts else seg)
    return pts


def _polygons(topo: dict, name: str) -> list[list[list[tuple[float, float]]]]:
    arcs = _arcs(topo)
    for g in topo["objects"]["countries"]["geometries"]:
        if (g.get("properties") or {}).get("name") != name:
            continue
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        return [[_ring(arcs, ring) for ring in poly] for poly in polys]
    raise KeyError(f"world-atlas không có nước {name!r}")


def _projector(bbox):
    """Mercator, khớp bbox vào BOX giữ đúng tỉ lệ."""
    lon0, lat0, lon1, lat1 = bbox
    merc = lambda lat: math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    x0, x1 = math.radians(lon0), math.radians(lon1)
    y0, y1 = merc(lat0), merc(lat1)
    bx0, by0, bx1, by1 = BOX
    k = min((bx1 - bx0) / (x1 - x0), (by1 - by0) / (y1 - y0))
    ox = bx0 + ((bx1 - bx0) - k * (x1 - x0)) / 2
    oy = by0 + ((by1 - by0) - k * (y1 - y0)) / 2

    def p(lon, lat):
        lat = max(-85, min(85, lat))
        return ox + k * (math.radians(lon) - x0), oy + k * (y1 - merc(lat))
    return p


def visible_bounds(bbox) -> tuple[float, float, float, float]:
    """(lon0, lat0, lon1, lat1) của khung 1920×1080, chiếu ngược `_projector`.

    Bbox khai báo nằm lọt trong BOX và được căn giữa, nên biển hai bên rộng hơn
    bbox. Đảo có thể nằm trong khung dù ngoài bbox khai báo.
    """
    lon0, lat0, lon1, lat1 = bbox
    merc = lambda lat: math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    x0, x1 = math.radians(lon0), math.radians(lon1)
    y0, y1 = merc(lat0), merc(lat1)
    bx0, by0, bx1, by1 = BOX
    k = min((bx1 - bx0) / (x1 - x0), (by1 - by0) / (y1 - y0))
    ox = bx0 + ((bx1 - bx0) - k * (x1 - x0)) / 2
    oy = by0 + ((by1 - by0) - k * (y1 - y0)) / 2

    def inv(x, y):
        lon = math.degrees((x - ox) / k + x0)
        my = y1 - (y - oy) / k
        lat = math.degrees(2 * math.atan(math.exp(my)) - math.pi / 2)
        return lon, lat

    corners = [inv(0, FRAME[1]), inv(FRAME[0], FRAME[1]), inv(0, 0), inv(FRAME[0], 0)]
    lons = [c[0] for c in corners]
    lats = [c[1] for c in corners]
    return (round(min(lons), 1), round(min(lats), 1), round(max(lons), 1), round(max(lats), 1))


def _island_bytes() -> bytes:
    if not ISLANDS_CACHE.exists():
        ISLANDS_CACHE.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(ISLANDS_URL, timeout=120) as r:
            blob = r.read()
        if hashlib.sha256(blob).hexdigest() != ISLANDS_SHA256:
            raise RuntimeError("Natural Earth sha256 lệch, không ghi cache")
        ISLANDS_CACHE.write_bytes(blob)
        return blob
    blob = ISLANDS_CACHE.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != ISLANDS_SHA256:
        raise RuntimeError(f"cache đảo lệch sha256: {digest}")
    return blob


def _geo_rings(geom: dict) -> list[list[tuple[float, float]]]:
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [[(x, y) for x, y in ring] for ring in c]
    if t == "MultiPolygon":
        return [[(x, y) for x, y in ring] for poly in c for ring in poly]
    return []


def _island_records() -> list[tuple[str, str, list]]:
    global _ISLANDS
    if _ISLANDS is None:
        data = json.loads(_island_bytes())
        by_name = {}
        for feat in data["features"]:
            name = (feat.get("properties") or {}).get("NAME")
            if name in ISLAND_LABEL:
                by_name[name] = _geo_rings(feat["geometry"])
        missing = [n for n in ISLAND_LABEL if n not in by_name]
        if missing:
            raise RuntimeError(f"Natural Earth thiếu hình {missing}")
        _ISLANDS = [(n, ISLAND_LABEL[n], by_name[n]) for n in ISLAND_LABEL]
    return _ISLANDS


def _px_path(rings_px) -> str:
    """Giữ nguyên đỉnh của đảo nhỏ. Rút điểm chỉ khi cụm lớn hơn 6px, kẻo đảo biến mất."""
    out = []
    for pts in rings_px:
        if len(pts) < 3:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        step = 0.0 if max(max(xs) - min(xs), max(ys) - min(ys)) < 6 else 1.2
        seg, last = [], None
        for x, y in pts:
            if last and abs(x - last[0]) + abs(y - last[1]) < step:
                continue
            seg.append(f"{x:.1f},{y:.1f}")
            last = (x, y)
        if len(seg) >= 3:
            out.append("M" + " L".join(seg) + " Z")
    return " ".join(out)


def _label_xy(pts, text: str, fw: int, fh: int, cap_top: float) -> tuple[float, float]:
    """Nhãn ngồi trên cụm đảo, không đè hình và không chui vào #capzone.

    longform.js phóng cả sân khấu từ tâm y=540 lên tới 1.04. Chữ 34px, viền 5px.
    """
    cx = sum(x for x, _ in pts) / len(pts)
    top = min(y for _, y in pts)
    half = len(text) * 34 * 0.58 / 2
    x = min(max(cx, 36 + half), fw - 36 - half)
    below = 22.0
    y_cap = 540 + (cap_top - below - 540) / 1.04
    y = min(max(top - (below + 10), 168), y_cap)
    return round(x, 1), round(y, 1)


def _seg_hits_rect(a, b, fw, fh) -> bool:
    """Đoạn a-b có cắt hình chữ nhật [0,fw]×[0,fh] không (Liang–Barsky)."""
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0), (dx, fw - x0), (-dy, y0), (dy, fh - y0)):
        if p == 0:
            if q < 0:
                return False
            continue
        t = q / p
        if p < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return False
    return True


def _point_in_ring(x, y, pts) -> bool:
    inside = False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def _ring_hits(pts, fw, fh) -> bool:
    """Vòng đa giác (toạ độ px) có phần nào nằm trong khung fw×fh: đỉnh trong khung,
    cạnh cắt khung, hoặc khung nằm trọn trong đa giác."""
    if len(pts) < 3:
        return False
    if max(x for x, _ in pts) < 0 or min(x for x, _ in pts) > fw or max(y for _, y in pts) < 0 or min(y for _, y in pts) > fh:
        return False
    if any(0 <= x <= fw and 0 <= y <= fh for x, y in pts):
        return True
    if any(_seg_hits_rect(a, b, fw, fh) for a, b in zip(pts, pts[1:] + pts[:1])):
        return True
    return _point_in_ring(fw / 2, fh / 2, pts)


INSET_W, INSET_H, INSET_PAD = 260, 150, 18


def _inset_box(rings_px, label: str, fw: int, fh: int, cap: float) -> dict:
    """Ô phóng to cụm đảo đặt trên #capzone; `tf` là transform SVG đưa cụm vào giữa ô."""
    pts = [(min(max(x, 0), fw), min(max(y, 0), fh)) for ring in rings_px for x, y in ring]
    bx0, bx1 = min(x for x, _ in pts), max(x for x, _ in pts)
    by0, by1 = min(y for _, y in pts), max(y for _, y in pts)
    s = min((INSET_W - 2 * INSET_PAD) / max(bx1 - bx0, 1.0), (INSET_H - 2 * INSET_PAD) / max(by1 - by0, 1.0), 6.0)
    half = max(INSET_W, len(label) * 34 * 0.58) / 2
    cx = min(max((bx0 + bx1) / 2, 36 + half), fw - 36 - half)
    bottom = 540 + (cap - 8 - 540) / 1.04
    x0, y0 = cx - INSET_W / 2, bottom - INSET_H
    tx = x0 + INSET_W / 2 - s * (bx0 + bx1) / 2
    ty = y0 + INSET_H / 2 - s * (by0 + by1) / 2
    return {"x": round(x0, 1), "y": round(y0, 1), "w": INSET_W, "h": INSET_H, "cx": round(cx, 1),
            "tf": f"translate({tx:.1f},{ty:.1f}) scale({s:.3f})", "s": round(s, 3),
            # đảo nhỏ hơn 1px vẫn thành chấm thấy được trong ô (toạ độ trước transform)
            "dots": [[round(sum(x for x, _ in r) / len(r), 1), round(sum(y for _, y in r) / len(r), 1)]
                     for r in rings_px if r]}


def island_layer(proj, fw: int, fh: int, focus: bool = True, cap_top: float | None = None) -> list[dict]:
    """Đường SVG của đúng hai quần đảo khi có phần nằm trong khung fw×fh.

    `proj(lon, lat) -> (x, y)`. Không nhìn id video hay tên cảnh.
    """
    cap = CAP_TOP if cap_top is None else cap_top
    clamp = fw == FRAME[0] and fh == FRAME[1]
    out = []
    for name, label, rings in _island_records():
        kept, vis = [], []
        for ring in rings:
            pts = [proj(lon, lat) for lon, lat in ring]
            if not _ring_hits(pts, fw, fh):
                continue
            kept.append(pts)
            inside = [p for p in pts if 0 <= p[0] <= fw and 0 <= p[1] <= fh]
            # đảo chỉ lộ qua mép, không đỉnh nào trong khung: lấy tâm phần hộp bao nằm trong khung
            vis.extend(inside or [((max(0, min(x for x, _ in pts)) + min(fw, max(x for x, _ in pts))) / 2,
                                   (max(0, min(y for _, y in pts)) + min(fh, max(y for _, y in pts))) / 2)])
        if not kept:
            continue
        d = _px_path(kept)
        if not d:
            continue
        flat = [p for ring in kept for p in ring]
        span = max(max(p[0] for p in flat) - min(p[0] for p in flat),
                   max(p[1] for p in flat) - min(p[1] for p in flat))
        # Cụm dưới 400px: nét 7px để còn đọc khi khung xem còn 360p. Cụm lớn giữ nét đất liền.
        sw = 3.2 if span >= 400 else 7.0
        rec = {"name": name, "label": label, "d": d, "sw": sw, "focus": focus}
        if clamp:
            rec["lx"], rec["ly"] = _label_xy(vis, label, fw, fh, cap)
            # Cụm đảo rơi vào vùng phụ đề (sau khi sân khấu phóng 1.04): chữ phụ đề che mất chấm đảo,
            # nên vẽ thêm ô phóng to cụm đảo ngay trên #capzone, nhãn ngồi trên ô.
            if 540 + (max(y for _, y in vis) - 540) * 1.04 > cap:
                rec["inset"] = _inset_box(kept, label, fw, fh, cap)
                rec["lx"], rec["ly"] = rec["inset"]["cx"], rec["inset"]["y"] - 26
        else:
            rec["lx"] = round(sum(x for x, _ in vis) / len(vis), 1)
            rec["ly"] = round(sum(y for _, y in vis) / len(vis), 1)
        out.append(rec)
    return out


def _vn_focus(spec: dict) -> bool:
    if "Vietnam" in spec.get("countries", []):
        return True
    if "Vietnam" in spec.get("context", []):
        return False
    return True


def _path(rings, proj, bbox, pad=6.0) -> str:
    lon0, lat0, lon1, lat1 = bbox
    out = []
    for ring in rings:
        # bỏ vòng nằm ngoài vùng nhìn (đảo xa, lãnh thổ hải ngoại)
        if not any(lon0 - pad <= x <= lon1 + pad and lat0 - pad <= y <= lat1 + pad for x, y in ring):
            continue
        last = None
        seg = []
        for lon, lat in ring:
            x, y = proj(lon, lat)
            if last and abs(x - last[0]) + abs(y - last[1]) < 1.2:
                continue  # rút gọn điểm dưới 1px
            seg.append(f"{x:.1f},{y:.1f}"); last = (x, y)
        if len(seg) >= 3:
            out.append("M" + " L".join(seg) + " Z")
    return " ".join(out)


def _pin_card_box(pin: dict, k: int) -> tuple[float, float, float, float]:
    """Hộp ước lượng của thẻ tên ghim (longform.css .lf-pin-card: chữ 34px, phụ 24px, đệm 20px, lệch 26px)."""
    w = max(len(pin.get("name") or "") * 34 * 0.6, len(pin.get("sub") or "") * 24 * 0.55) + 40
    h = 100 if pin.get("sub") else 64
    side = pin.get("side") or ("left" if k % 2 else "right")
    x0 = pin["x"] + 26 if side == "right" else pin["x"] - 26 - w
    return x0, pin["y"] - h / 2, x0 + w, pin["y"] + h / 2


def _island_box(isl: dict) -> tuple[float, float, float, float]:
    half = len(isl["label"]) * 34 * 0.58 / 2
    x0, x1, y0, y1 = isl["lx"] - half, isl["lx"] + half, isl["ly"] - 22, isl["ly"] + 22
    if "inset" in isl:
        b = isl["inset"]
        x0, x1, y1 = min(x0, b["x"]), max(x1, b["x"] + b["w"]), b["y"] + b["h"]
    return x0, y0, x1, y1


def _dodge_pin_cards(islands: list[dict], pins: list[dict]) -> None:
    """Nhãn (và ô phóng to) của đảo đè thẻ tên ghim thì dời ngang tới chỗ trống gần nhất trong khung."""
    cards = [_pin_card_box(p, k) for k, p in enumerate(pins)]

    def hits(box):
        return [c for c in cards if not (box[2] < c[0] or box[0] > c[2] or box[3] < c[1] or box[1] > c[3])]

    for isl in islands:
        box = _island_box(isl)
        if not hits(box):
            continue
        w, home = box[2] - box[0], isl["lx"]
        # ứng viên: sát phải / sát trái từng thẻ, trong khung, không đè thẻ nào; lấy chỗ gần nhất
        cands = []
        for c in cards:
            for left in (c[2] + 16, c[0] - 16 - w):
                if 36 <= left and left + w <= FRAME[0] - 36:
                    dx = left - box[0]
                    if not hits((box[0] + dx, box[1], box[2] + dx, box[3])):
                        cands.append(dx)
        if not cands:
            continue
        dx = min(cands, key=abs)
        isl["lx"] = round(home + dx, 1)
        if "inset" in isl:
            b = isl["inset"]
            b["x"], b["cx"] = round(b["x"] + dx, 1), round(b["cx"] + dx, 1)
            t, sc = b["tf"].split(" scale")
            tx, ty = t[len("translate("):-1].split(",")
            b["tf"] = f"translate({float(tx) + dx:.1f},{ty}) scale{sc}"


def _hanoi_features(proj) -> list[dict]:
    """Các đối tượng địa lý cho bản đồ Thăng Long / Hà Nội (địa hình, sông, hồ, thành)."""
    feats = []

    # 1. Nền đồng bằng / Kinh thành Thăng Long
    terrain_pts = [
        (105.78, 21.09), (105.84, 21.08), (105.88, 21.04), (105.90, 21.00),
        (105.87, 20.97), (105.82, 20.98), (105.79, 21.01), (105.78, 21.05)
    ]
    px_terrain = [proj(lon, lat) for lon, lat in terrain_pts]
    d_terrain = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in px_terrain) + " Z"
    feats.append({
        "type": "polygon",
        "cls": "terrain",
        "d": d_terrain,
        "label": "ĐỒNG BẰNG THĂNG LONG",
        "lx": round(sum(p[0] for p in px_terrain) / len(px_terrain), 1),
        "ly": round(sum(p[1] for p in px_terrain) / len(px_terrain) + 120, 1),
    })

    # 2. Sông Hồng (dòng chảy chính uốn lượn hùng vĩ từ Tây Bắc xuống Đông Nam)
    song_hong_pts = [
        (105.75, 21.11), (105.78, 21.09), (105.82, 21.07), (105.85, 21.055),
        (105.875, 21.035), (105.90, 21.00), (105.94, 20.95)
    ]
    px_sh = [proj(lon, lat) for lon, lat in song_hong_pts]
    d_sh = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in px_sh)
    feats.append({
        "type": "line",
        "cls": "river",
        "d": d_sh,
        "label": "SÔNG HỒNG",
        "lx": round(px_sh[3][0] + 50, 1),
        "ly": round(px_sh[3][1] - 30, 1),
    })

    # 3. Sông Tô Lịch (uốn quanh phía Tây và Nam kinh thành)
    to_lich_pts = [
        (105.815, 21.055), (105.80, 21.04), (105.798, 21.015), (105.82, 20.98),
        (105.845, 20.96)
    ]
    px_tl = [proj(lon, lat) for lon, lat in to_lich_pts]
    d_tl = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in px_tl)
    feats.append({
        "type": "line",
        "cls": "river sub",
        "d": d_tl,
        "label": "SÔNG TÔ LỊCH",
        "lx": round(px_tl[1][0] - 40, 1),
        "ly": round(px_tl[1][1], 1),
    })

    # 4. Hồ Tây (hồ lớn phía Bắc cạnh đền Quán Thánh)
    ho_tay_pts = [
        (105.810, 21.050), (105.805, 21.058), (105.812, 21.068), (105.825, 21.072),
        (105.835, 21.065), (105.838, 21.055), (105.832, 21.045), (105.820, 21.044)
    ]
    px_ht = [proj(lon, lat) for lon, lat in ho_tay_pts]
    d_ht = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in px_ht) + " Z"
    feats.append({
        "type": "polygon",
        "cls": "water lake",
        "d": d_ht,
        "label": "HỒ TÂY",
        "lx": round(sum(p[0] for p in px_ht) / len(px_ht), 1),
        "ly": round(sum(p[1] for p in px_ht) / len(px_ht), 1),
    })

    # 5. Hồ Trúc Bạch (cạnh Hồ Tây và Quán Thánh)
    truc_bach_pts = [
        (105.836, 21.048), (105.842, 21.048), (105.841, 21.042), (105.835, 21.042)
    ]
    px_tb = [proj(lon, lat) for lon, lat in truc_bach_pts]
    d_tb = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in px_tb) + " Z"
    feats.append({
        "type": "polygon",
        "cls": "water lake",
        "d": d_tb,
        "label": "TRÚC BẠCH",
        "lx": round(sum(p[0] for p in px_tb) / len(px_tb), 1),
        "ly": round(sum(p[1] for p in px_tb) / len(px_tb) - 15, 1),
    })

    # 6. Hồ Hoàn Kiếm (trung tâm phía Đông cạnh đền Bạch Mã)
    hoan_kiem_pts = [
        (105.850, 21.033), (105.855, 21.033), (105.854, 21.026), (105.849, 21.026)
    ]
    px_hk = [proj(lon, lat) for lon, lat in hoan_kiem_pts]
    d_hk = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in px_hk) + " Z"
    feats.append({
        "type": "polygon",
        "cls": "water lake",
        "d": d_hk,
        "label": "HỒ HOÀN KIẾM",
        "lx": round(sum(p[0] for p in px_hk) / len(px_hk), 1),
        "ly": round(sum(p[1] for p in px_hk) / len(px_hk), 1),
    })

    # 7. Hồ Bảy Mẫu (phía Nam gần đền Kim Liên)
    bay_mau_pts = [
        (105.838, 21.018), (105.846, 21.018), (105.846, 21.011), (105.838, 21.011)
    ]
    px_bm = [proj(lon, lat) for lon, lat in bay_mau_pts]
    d_bm = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in px_bm) + " Z"
    feats.append({
        "type": "polygon",
        "cls": "water lake",
        "d": d_bm,
        "label": "HỒ BẢY MẪU",
        "lx": round(sum(p[0] for p in px_bm) / len(px_bm), 1),
        "ly": round(sum(p[1] for p in px_bm) / len(px_bm), 1),
    })

    # 8. Hồ Thủ Lệ (phía Tây cạnh đền Voi Phục)
    thu_le_pts = [
        (105.805, 21.035), (105.812, 21.035), (105.811, 21.028), (105.804, 21.028)
    ]
    px_tl_lake = [proj(lon, lat) for lon, lat in thu_le_pts]
    d_tl_lake = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in px_tl_lake) + " Z"
    feats.append({
        "type": "polygon",
        "cls": "water lake",
        "d": d_tl_lake,
        "label": "HỒ THỦ LỆ",
        "lx": round(sum(p[0] for p in px_tl_lake) / len(px_tl_lake), 1),
        "ly": round(sum(p[1] for p in px_tl_lake) / len(px_tl_lake), 1),
    })

    # 9. Hoàng Thành Thăng Long (thành lũy cổ ở trung tâm)
    citadel_outer_pts = [
        (105.830, 21.042), (105.848, 21.042), (105.848, 21.028), (105.830, 21.028)
    ]
    px_co = [proj(lon, lat) for lon, lat in citadel_outer_pts]
    d_co = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in px_co) + " Z"
    feats.append({
        "type": "polygon",
        "cls": "citadel outer",
        "d": d_co,
        "label": "HOÀNG THÀNH",
        "lx": round(sum(p[0] for p in px_co) / len(px_co), 1),
        "ly": round(px_co[0][1] - 12, 1),
    })

    citadel_inner_pts = [
        (105.835, 21.038), (105.844, 21.038), (105.844, 21.031), (105.835, 21.031)
    ]
    px_ci = [proj(lon, lat) for lon, lat in citadel_inner_pts]
    d_ci = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in px_ci) + " Z"
    feats.append({
        "type": "polygon",
        "cls": "citadel inner",
        "d": d_ci,
        "label": "TỬ CẤM THÀNH",
        "lx": round(sum(p[0] for p in px_ci) / len(px_ci), 1),
        "ly": round(sum(p[1] for p in px_ci) / len(px_ci), 1),
    })

    return feats


def bake(spec: dict) -> dict:
    topo = _topology()
    bbox = spec.get("bbox")
    if not bbox:
        names = list(spec.get("countries") or []) + list(spec.get("context") or [])
        if "Vietnam" not in names:
            raise KeyError("bbox")
        bbox = list(VN_NATIONAL_BBOX)
    proj = _projector(bbox)
    countries = []
    for name, focus in [(n, True) for n in spec.get("countries", [])] + [(n, False) for n in spec.get("context", [])]:
        polys = _polygons(topo, name)
        d = " ".join(_path(poly, proj, bbox) for poly in polys).strip()
        # nhãn nước: trọng tâm của PHẦN nằm trong khung (nước lớn như Trung Quốc
        # có trọng tâm cả nước rơi ra ngoài khung)
        bx0, by0, bx1, by1 = BOX
        vis = [(x, y) for poly in polys for ring in poly for x, y in (proj(lon, lat) for lon, lat in ring)
               if bx0 <= x <= bx1 and by0 <= y <= by1]
        cx = sum(x for x, _ in vis) / len(vis) if vis else -999
        cy = sum(y for _, y in vis) / len(vis) if vis else -999
        countries.append({"name": name, "label": spec.get("labels", {}).get(name, ""), "d": d, "focus": focus,
                          "lx": round(cx, 1), "ly": round(cy, 1)})
    pins = []
    for pin in spec.get("pins", []):
        x, y = proj(pin["lon"], pin["lat"])
        pins.append({**pin, "x": round(x, 1), "y": round(y, 1)})
    islands = island_layer(proj, FRAME[0], FRAME[1], focus=_vn_focus(spec))
    _dodge_pin_cards(islands, pins)
    features = []
    is_hanoi = (
        (105.6 <= bbox[0] <= 106.0 and 20.8 <= bbox[1] <= 21.2) or
        any("Thăng Long" in (pin.get("name") or "") or "Trấn" in (pin.get("name") or "") for pin in spec.get("pins", [])) or
        "Thăng Long" in (spec.get("title") or "")
    )
    if is_hanoi:
        features = _hanoi_features(proj)
    return {**spec, "bbox": list(bbox), "_geo": {"countries": countries, "pins": pins, "islands": islands, "features": features}}


if __name__ == "__main__":
    demo = bake({"countries": ["India", "Nepal"], "context": ["China", "Bangladesh", "Bhutan"],
                 "bbox": [80.5, 23.2, 88.8, 29.2],
                 "pins": [{"name": "Lâm Tỳ Ni", "lon": 83.2767, "lat": 27.4833}]})
    for c in demo["_geo"]["countries"]:
        print(c["name"], len(c["d"]), c["lx"], c["ly"])
    print(demo["_geo"]["pins"])
