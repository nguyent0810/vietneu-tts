"""Bản đồ VÙNG cho video dài (cảnh `region` và `profile` của longform.js) -- nướng sẵn.

`hf_geo.py` chỉ có biên giới quốc gia 1:50 triệu: ở tỉ lệ một tỉnh không thấy sông,
phá, núi. Module này nướng một ảnh nền địa hình lớn hơn khung hình (mặc định
3840x2160 = phóng được 2x mà vẫn nét) từ dữ liệu mở đã tải sẵn:

  - Copernicus GLO-30 DEM (bóng địa hình, mặt cắt độ cao) -- ghi công bắt buộc;
  - trích OpenStreetMap qua Overpass (sông, phá, mặt nước) -- ODbL, ghi công.

Nước hiện đại (hồ chứa, ao nuôi, kênh thuỷ lợi, mặt nước nhỏ không tên) bị lọc
khỏi nền: nền dùng cho chuyện trước 1858. Ảnh nền cache theo
sha1(bbox, cỡ, kiểu, phiên bản dữ liệu) trong chunks_cache/geo/region/: bài sau
cùng vùng không nướng lại. Lúc render longform.js chỉ dời camera trên ảnh và vẽ
lớp phủ mỏng; không tính địa lý, không mạng.

    bake(spec)    -> spec + "_geo": {src, W, H, cams, pins, lines, areas, credit}
    profile(spec) -> spec + "_prof": {area, line, marks, ticks, credit}

Cần thêm `rasterio` + `scipy` lúc nướng (`uv pip install rasterio`); render thì không.
Dữ liệu thô: $VIENEU_GEO_DATA (mặc định output/rock/geo_data/raw), gồm
copernicus/*.tif và osm/*.json (Overpass `out geom`).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent
DATA = Path(os.environ.get("VIENEU_GEO_DATA", ROOT / "output" / "rock" / "geo_data" / "raw"))
CACHE = ROOT / "chunks_cache" / "geo" / "region"
DATA_VERSION = "1"
FRAME = (1920, 1080)
CREDIT = "Nền địa hình: Copernicus DEM GLO-30 © DLR/Airbus, cung cấp bởi Copernicus (EU/ESA); sông nước: © OpenStreetMap contributors (ODbL)"
CREDIT_SHORT = "Copernicus DEM · © OpenStreetMap"

# Nước hiện đại không có ở thế kỷ 17: bỏ khỏi nền lịch sử.
MODERN_WATER = {"reservoir", "pond", "basin", "wastewater", "canal", "moat", "fish_pond", "lock"}
MIN_AREA_FRAC = 1500 / (3840 * 2160)   # mặt nước không tên nhỏ hơn mức này (theo diện tích khung) thì bỏ
MIN_RIVER_FRAC = 0.06                  # sông không tên ngắn hơn 6% bề ngang khung thì bỏ (mương, rạch)

STYLES = {
    # giấy trầm: địa hình thật nhưng nhạt, để nhãn và mũi tên nổi lên (duyệt 27/10)
    "giay": {"ramp": [(0, (228, 216, 184)), (15, (218, 205, 168)), (120, (196, 186, 146)), (400, (170, 160, 122)), (1000, (140, 128, 98))],
             "sea": (92, 112, 118), "water": (104, 124, 128), "gray": .35, "paper": (236, 226, 204), "tint": .18, "grain": 3.0},
}


# ---------------------------------------------------------------- khung và phép chiếu
def fit_bbox(bbox, aspect: float = FRAME[0] / FRAME[1]):
    """Nới bbox [lon0, lat0, lon1, lat1] ra đúng tỉ lệ khung (chiếu phẳng, co kinh độ theo cos vĩ độ giữa)."""
    lon0, lat0, lon1, lat1 = bbox
    k = math.cos(math.radians((lat0 + lat1) / 2))
    w, h = (lon1 - lon0) * k, lat1 - lat0
    if w / h < aspect:
        d = (h * aspect / k - (lon1 - lon0)) / 2
        lon0, lon1 = lon0 - d, lon1 + d
    else:
        d = (w / aspect - h) / 2
        lat0, lat1 = lat0 - d, lat1 + d
    return [round(lon0, 5), round(lat0, 5), round(lon1, 5), round(lat1, 5)]


def projector(bbox, W: int, H: int):
    lon0, lat0, lon1, lat1 = bbox
    return lambda lon, lat: ((lon - lon0) / (lon1 - lon0) * W, (lat1 - lat) / (lat1 - lat0) * H)


def km_per_px(bbox, W: int) -> float:
    lon0, lat0, lon1, lat1 = bbox
    return (lon1 - lon0) * 111.32 * math.cos(math.radians((lat0 + lat1) / 2)) / W


def haversine_km(a, b) -> float:
    (lo1, la1), (lo2, la2) = a, b
    p1, p2 = math.radians(la1), math.radians(la2)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 6371.0088 * 2 * math.asin(math.sqrt(h))


# ---------------------------------------------------------------- dữ liệu
def _data_files() -> list[Path]:
    return sorted(list((DATA / "copernicus").glob("*.tif")) + list((DATA / "osm").glob("*.json")))


def cache_key(bbox, W: int, H: int, style: str) -> str:
    files = [(p.name, p.stat().st_size) for p in _data_files()]
    raw = json.dumps({"bbox": [round(x, 5) for x in bbox], "W": W, "H": H, "style": style, "v": DATA_VERSION, "files": files})
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


def dem(bbox, W: int, H: int) -> np.ndarray:
    import rasterio  # noqa: PLC0415 -- chỉ cần lúc nướng, không cần lúc render
    from rasterio.enums import Resampling  # noqa: PLC0415
    from rasterio.merge import merge  # noqa: PLC0415
    tifs = sorted((DATA / "copernicus").glob("*.tif"))
    if not tifs:
        raise FileNotFoundError(f"thiếu DEM trong {DATA / 'copernicus'} (đặt VIENEU_GEO_DATA)")
    srcs = [rasterio.open(p) for p in tifs]
    try:
        lon0, lat0, lon1, lat1 = bbox
        arr, _ = merge(srcs, bounds=(lon0, lat0, lon1, lat1), res=((lon1 - lon0) / W, (lat1 - lat0) / H),
                       resampling=Resampling.bilinear, nodata=0)
    finally:
        for s in srcs:
            s.close()
    z = np.zeros((H, W), "float32")
    a = arr[0, :H, :W].astype("float32")
    z[: a.shape[0], : a.shape[1]] = a   # ô DEM thiếu (biển xa) = 0
    return z


def osm_elements() -> list[dict]:
    out = []
    for p in sorted((DATA / "osm").glob("*.json")):
        out += json.loads(p.read_text(encoding="utf-8")).get("elements", [])
    return out


def _geoms(e: dict) -> list[list[dict]]:
    if "geometry" in e:
        return [e["geometry"]]
    return [m["geometry"] for m in e.get("members", []) if m.get("role") in ("outer", "") and "geometry" in m]


def _area(pts) -> float:
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2


def _length(pts) -> float:
    return sum(math.hypot(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in zip(pts, pts[1:]))


def historic_water(elements, proj, W: int, H: int) -> tuple[list, list]:
    """(đa giác mặt nước, đường sông) đã chiếu, sau khi lọc nước hiện đại. Mỗi đường sông: (pts, có_tên)."""
    polys, rivers = [], []
    for e in elements:
        t = e.get("tags", {})
        if t.get("water") in MODERN_WATER or t.get("landuse") in ("reservoir", "aquaculture") or t.get("waterway") == "canal":
            continue
        named = bool(t.get("name"))
        if t.get("natural") in ("water", "wetland"):
            for g in _geoms(e):
                pts = [proj(p["lon"], p["lat"]) for p in g]
                # mảnh nhỏ không tên (ao, ruộng trũng -- kể cả mảnh gắn nhầm water=river) thì bỏ
                if len(pts) > 2 and (named or _area(pts) >= MIN_AREA_FRAC * W * H):
                    polys.append((pts, t.get("natural")))
        elif t.get("waterway") == "river" and e["type"] == "way" and "geometry" in e:
            pts = [proj(p["lon"], p["lat"]) for p in e["geometry"]]
            if named or _length(pts) >= MIN_RIVER_FRAC * W:
                rivers.append((pts, named))
    return polys, rivers


# ---------------------------------------------------------------- ảnh nền
def hillshade(z: np.ndarray, bbox, az: float = 315, alt: float = 40, exag: float = 1.6) -> np.ndarray:
    H, W = z.shape
    lon0, lat0, lon1, lat1 = bbox
    px = (lon1 - lon0) / W * 111320 * math.cos(math.radians((lat0 + lat1) / 2))
    py = (lat1 - lat0) / H * 110570
    gy, gx = np.gradient(z * exag, py, px)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    a, b = math.radians(az), math.radians(alt)
    return np.clip(math.sin(b) * np.cos(slope) + math.cos(b) * np.sin(slope) * np.cos(a - aspect), 0, 1)


def sea_mask(z: np.ndarray, level: float = 0.3, min_frac: float = 0.005) -> np.ndarray:
    """Biển = vùng thấp nối với mép khung và đủ lớn; ao, ruộng trũng trong đất liền không tính."""
    from scipy import ndimage  # noqa: PLC0415
    lab, _ = ndimage.label(z <= level)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    sizes = ndimage.sum(np.ones_like(lab), lab, list(edge)) if edge else []
    keep = [k for k, s in zip(edge, sizes) if s >= min_frac * z.size]
    return np.isin(lab, keep)


def _ramp(z: np.ndarray, stops) -> np.ndarray:
    out = np.zeros(z.shape + (3,), "float32")
    zs = np.array([s[0] for s in stops], "float32")
    for c in range(3):
        out[..., c] = np.interp(z, zs, [s[1][c] for s in stops])
    return out


def render_base(bbox, W: int, H: int, style: str = "giay"):
    from PIL import Image, ImageDraw, ImageFilter  # noqa: PLC0415
    S = STYLES[style]
    z = dem(bbox, W, H)
    sea = sea_mask(z)
    hs = hillshade(np.where(sea, 0, z), bbox)
    rgb = _ramp(z, S["ramp"]) * (0.62 + 0.5 * hs[..., None])
    rgb[sea] = S["sea"]
    gray = rgb.mean(axis=2, keepdims=True)
    rgb = rgb * (1 - S["gray"]) + gray * S["gray"]
    rgb = rgb * (1 - S["tint"]) + np.array(S["paper"], "float32") * S["tint"]
    rgb += np.random.default_rng(7).normal(0, S["grain"], rgb.shape[:2])[..., None]   # hạt giấy, cố định theo seed
    img = Image.fromarray(np.clip(rgb, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(img, "RGBA")
    polys, rivers = historic_water(osm_elements(), projector(bbox, W, H), W, H)
    water = S["water"] + (255,)
    for pts, kind in polys:
        d.polygon(pts, fill=water if kind == "water" else S["water"] + (90,))
    for pts, named in rivers:
        d.line(pts, fill=water if named else S["water"] + (150,), width=max(2, round(W / (550 if named else 1280))), joint="curve")
    return img.filter(ImageFilter.SMOOTH)


def base(bbox, W: int = 3840, H: int = 2160, style: str = "giay") -> Path:
    """Ảnh nền đã nướng (JPEG), cache theo khoá; có rồi thì không nướng lại."""
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{cache_key(bbox, W, H, style)}.jpg"
    if not out.exists():
        tmp = out.with_suffix(".tmp.jpg")
        render_base(bbox, W, H, style).save(tmp, quality=90)
        tmp.replace(out)
    return out


# ---------------------------------------------------------------- cảnh `region`
def _path(pts) -> str:
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def bake(spec: dict, render: bool = True) -> dict:
    """spec: {"bbox": [...], "base_px": 3840, "camera": [{"at", "center": [lon, lat], "zoom"}],
    "pins": [{"name", "lon", "lat", "at"}], "lines": [{"name", "coords": [[lon, lat]..], "kind": "wall|route|arrow|river", "at"}],
    "areas": [{"name", "center": [lon, lat], "r_km", "at"}]}. Toạ độ ra theo pixel ảnh nền."""
    W = int(spec.get("base_px", 3840))
    H = round(W * FRAME[1] / FRAME[0])
    bbox = fit_bbox(spec["bbox"])
    proj = projector(bbox, W, H)
    kpp = km_per_px(bbox, W)
    geo = {"W": W, "H": H, "bbox": bbox, "credit": CREDIT_SHORT}
    if render:
        geo["src"] = str(base(bbox, W, H, spec.get("style", "giay")))
    geo["cams"] = [{**c, "x": round(proj(*c["center"])[0], 1), "y": round(proj(*c["center"])[1], 1)}
                   for c in spec.get("camera", [])] or [{"x": W / 2, "y": H / 2, "zoom": 1}]
    geo["pins"] = [{**p, "x": round(proj(p["lon"], p["lat"])[0], 1), "y": round(proj(p["lon"], p["lat"])[1], 1)}
                   for p in spec.get("pins", [])]
    lines = []
    for ln in spec.get("lines", []):
        pts = [proj(lon, lat) for lon, lat in ln["coords"]]
        (ax, ay), (bx, by) = pts[-2], pts[-1]
        # nhãn đặt ở giữa đường; plan dời được bằng "label": [lon, lat] khi đè nhãn khác
        mid = proj(*ln["label"]) if ln.get("label") else pts[len(pts) // 2]
        lines.append({**ln, "d": _path(pts), "end": [round(bx, 1), round(by, 1)],
                      "angle": round(math.degrees(math.atan2(by - ay, bx - ax)), 1),
                      "lx": round(mid[0], 1), "ly": round(mid[1], 1),
                      "km": round(sum(haversine_km(a, b) for a, b in zip(ln["coords"], ln["coords"][1:])), 1)})
    geo["lines"] = lines
    geo["areas"] = [{**a, "x": round(proj(*a["center"])[0], 1), "y": round(proj(*a["center"])[1], 1),
                     "r": round(a.get("r_km", 2) / kpp, 1)} for a in spec.get("areas", [])]
    return {**spec, "_geo": geo}


# ---------------------------------------------------------------- cảnh `profile`
PROFILE_BOX = (220, 300, 1700, 800)   # vùng vẽ mặt cắt trong khung 1920x1080 (chừa tiêu đề, phụ đề)


def sample_line(a, b, n: int = 240) -> tuple[np.ndarray, np.ndarray]:
    """n điểm đều trên đoạn a->b: (km từ a, độ cao m) đọc thẳng từ DEM (song tuyến)."""
    import rasterio  # noqa: PLC0415
    lons = np.linspace(a[0], b[0], n)
    lats = np.linspace(a[1], b[1], n)
    z = np.full(n, np.nan, "float32")
    for p in sorted((DATA / "copernicus").glob("*.tif")):
        with rasterio.open(p) as src:
            l, bt, r, tp = src.bounds
            m = (lons >= l) & (lons < r) & (lats > bt) & (lats <= tp) & np.isnan(z)
            if m.any():
                z[m] = [v[0] for v in src.sample(zip(lons[m], lats[m]), indexes=1)]
    z = np.nan_to_num(z, nan=0.0)
    km = np.array([haversine_km(a, (lo, la)) for lo, la in zip(lons, lats)], "float32")
    return km, np.maximum(z, 0)


def profile(spec: dict) -> dict:
    """spec: {"from": [lon, lat], "to": [lon, lat], "marks": [{"label", "lon", "lat" | "km", "at"}], "zmax"}."""
    a, b = spec["from"], spec["to"]
    km, z = sample_line(a, b, int(spec.get("samples", 240)))
    km, z = km.astype(float), z.astype(float)   # ra JSON: không để lọt np.float32
    x0, y0, x1, y1 = PROFILE_BOX
    zmax = float(spec.get("zmax") or max(50.0, math.ceil(z.max() * 1.15 / 50) * 50))
    X = lambda k: x0 + k / km[-1] * (x1 - x0)
    Y = lambda m: y1 - m / zmax * (y1 - y0)
    pts = [(X(k), Y(m)) for k, m in zip(km, z)]
    line = _path(pts)
    area = line + f" L{x1:.1f},{y1:.1f} L{x0:.1f},{y1:.1f} Z"
    marks = []
    for mk in spec.get("marks", []):
        k = mk["km"] if "km" in mk else haversine_km(a, (mk["lon"], mk["lat"]))
        i = int(np.argmin(np.abs(km - k)))
        marks.append({**mk, "km": round(float(k), 2), "x": round(X(k), 1), "y": round(Y(float(z[i])), 1), "z": round(float(z[i]))})
    step_km = next(s for s in (0.5, 1, 2, 5, 10, 20, 50) if km[-1] / s <= 8)
    ticks = {"x": [{"v": round(s, 1), "p": round(X(s), 1)} for s in np.arange(0, km[-1] + 1e-6, step_km)],
             "y": [{"v": int(v), "p": round(Y(v), 1)} for v in np.linspace(0, zmax, 5)]}
    # phóng đại đứng = (m/px dọc) chia (m/px ngang): người xem phải biết dốc bị kéo cao bao nhiêu lần
    exag = (km[-1] * 1000 / (x1 - x0)) / (zmax / (y1 - y0))
    return {**spec, "_prof": {"line": line, "area": area, "marks": marks, "ticks": ticks, "box": PROFILE_BOX,
                              "km": round(float(km[-1]), 2), "zmax": zmax, "exag": round(exag, 1), "credit": "Copernicus DEM GLO-30"}}


if __name__ == "__main__":   # nướng thử vùng Đồng Hới, in số liệu
    s = bake({"bbox": [106.30, 17.25, 106.95, 17.75], "camera": [{"center": [106.62, 17.46], "zoom": 1}],
              "pins": [{"name": "Quảng Bình Quan", "lon": 106.62405, "lat": 17.46334}]})
    print(s["_geo"]["src"], s["_geo"]["bbox"], s["_geo"]["pins"])
    p = profile({"from": [106.40, 17.47], "to": [106.70, 17.47], "marks": [{"label": "Quảng Bình Quan", "lon": 106.62405, "lat": 17.46334}]})
    print(p["_prof"]["km"], p["_prof"]["zmax"], p["_prof"]["exag"], p["_prof"]["marks"])
