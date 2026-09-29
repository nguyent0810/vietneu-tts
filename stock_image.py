"""Lấy ẢNH tĩnh từ nguồn miễn phí (Pexels, Pixabay) cho nhánh HyperFrames.

Vì sao cần: `video_tool_clone/core/stockfootage` chỉ tìm VIDEO
(`/videos/search`) -- không có đường lấy ảnh. Mà với kênh Phật giáo thì ảnh
mới là thứ chính: `creative_director.py` đã ghi rõ "stock hiếm khi hợp nội
dung Phật giáo", và 47 rule sanitizer của BUD toàn là đổi từ Thiên Chúa giáo
sang Phật giáo -- dấu hiệu tìm video cho nội dung này hay trôi sang nhà thờ
phương Tây. Một tấm ảnh tĩnh chọn kỹ + Ken Burns chậm hợp nhịp 18-28 giây
của kênh hơn hẳn một clip động.

Dùng CHUNG khoá với nhánh video (`video_tool_clone/.env`), cache theo hash
query, và đi qua đúng nghi thức `asset_safety` của nhánh video: assert
TRƯỚC khi ghi record, ghi record, assert LẠI sau khi ghi.

`video_tool_clone/` là bản clone pull-only nên module này nằm ở repo chính,
không đụng vào clone.
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import asset_safety

PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / "video_tool_clone" / ".env"
CACHE_DIR = PROJECT_ROOT / "chunks_cache" / "beat_assets"
TIMEOUT_S = 30
USER_AGENT = "VieNeu-TTS/1.0 (stock image fetch)"


class StockImageError(RuntimeError):
    pass


def load_keys(env_file: Path = ENV_FILE) -> tuple[str | None, str | None]:
    """(pexels, pixabay). Không có file -> (None, None), caller tự xử lý."""
    values: dict[str, str] = {}
    try:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        return None, None
    return values.get("PEXELS_API_KEY") or None, values.get("PIXABAY_API_KEY") or None


def _get_json(url: str, headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pick_pexels(payload: dict, min_width: int = 1200) -> dict | None:
    """Ảnh đầu tiên đủ lớn để phủ khung 1080x1920 (renderer dùng object-fit
    cover nên chỉ cần một chiều đủ, không cần đúng tỉ lệ)."""
    for photo in payload.get("photos") or []:
        src = photo.get("src") or {}
        # Kích cỡ Pexels: `portrait` cắt sẵn 800x1200, `large2x` giới hạn
        # trong khung 940x650@2x nên ảnh DỌC chỉ ra ~867x1300 -- vẫn thiếu
        # so với khung 1080x1920. Chỉ `original` mới đủ nét; ảnh gốc vài MB
        # là chấp nhận được vì đã cache lại.
        url = src.get("original") or src.get("large2x") or src.get("portrait")
        if not url:
            continue
        if max(photo.get("width", 0), photo.get("height", 0)) < min_width:
            continue
        return {"url": url, "provider": "pexels", "page": photo.get("url", ""),
                "author": photo.get("photographer", ""), "id": str(photo.get("id", ""))}
    return None


def pick_pixabay(payload: dict, min_width: int = 1200) -> dict | None:
    for hit in payload.get("hits") or []:
        url = hit.get("largeImageURL") or hit.get("webformatURL")
        if not url:
            continue
        if max(hit.get("imageWidth", 0), hit.get("imageHeight", 0)) < min_width:
            continue
        return {"url": url, "provider": "pixabay", "page": hit.get("pageURL", ""),
                "author": hit.get("user", ""), "id": str(hit.get("id", ""))}
    return None


def search(query: str, orientation: str = "portrait") -> dict | None:
    """Tìm ở Pexels trước, không có thì Pixabay. Trả metadata hoặc None."""
    pexels_key, pixabay_key = load_keys()
    q = urllib.parse.quote(query)

    if pexels_key:
        try:
            payload = _get_json(
                f"https://api.pexels.com/v1/search?query={q}&orientation={orientation}"
                f"&size=large&per_page=15",
                headers={"Authorization": pexels_key})
            hit = pick_pexels(payload)
            if hit:
                return hit
        except Exception as exc:  # noqa: BLE001 -- một nguồn hỏng không được chặn nguồn kia
            print(f"CẢNH BÁO: Pexels ảnh lỗi cho {query!r}: {exc}", file=sys.stderr)

    if pixabay_key:
        pix_orient = {"portrait": "vertical", "landscape": "horizontal"}.get(orientation, "all")
        try:
            payload = _get_json(
                f"https://pixabay.com/api/?key={pixabay_key}&q={q}&image_type=photo"
                f"&orientation={pix_orient}&safesearch=true&per_page=15")
            hit = pick_pixabay(payload)
            if hit:
                return hit
        except Exception as exc:  # noqa: BLE001
            print(f"CẢNH BÁO: Pixabay ảnh lỗi cho {query!r}: {exc}", file=sys.stderr)
    return None


def _query_hash(query: str) -> str:
    return hashlib.sha1(query.encode("utf-8")).hexdigest()[:16]


def get_or_fetch_stock_image(query: str, orientation: str = "portrait") -> Path | None:
    """Trả đường dẫn ảnh đã cache, hoặc tải mới. None nếu không tìm được.

    Nghi thức an toàn giống hệt `asset_generation.get_or_fetch_stock_video`:
    cache-hit cũng phải assert lại -- một ảnh đã bị gắn cờ không được lặng lẽ
    quay lại qua cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    # Khoá cache gồm cả hướng ảnh: video dài 16:9 xin ảnh ngang, cùng query
    # với short dọc. Chung khoá thì bản dọc đã cache bị cắt còn dải giữa --
    # con dê chỉ còn cái lưng. Dọc giữ khoá cũ để cache sẵn có vẫn dùng được.
    key = query if orientation == "portrait" else f"{query}|{orientation}"
    cache_path = CACHE_DIR / f"img_{_query_hash(key)}.jpg"
    meta_path = cache_path.with_suffix(".source.json")
    if cache_path.exists():
        asset_safety.assert_asset_safe_for_assembly(cache_path)
        return cache_path

    hit = search(query, orientation)
    if hit is None:
        return None
    try:
        req = urllib.request.Request(hit["url"], headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            data = resp.read()
    except Exception as exc:  # noqa: BLE001
        print(f"CẢNH BÁO: tải ảnh lỗi ({exc})", file=sys.stderr)
        return None
    if len(data) < 4096:
        print(f"CẢNH BÁO: ảnh trả về quá nhỏ ({len(data)} byte) cho {query!r}", file=sys.stderr)
        return None

    cache_path.write_bytes(data)
    meta_path.write_text(json.dumps({**hit, "query": query}, ensure_ascii=False, indent=1),
                         encoding="utf-8")

    asset_safety.assert_asset_safe_for_assembly(cache_path)
    asset_safety.write_asset_safety_record(
        cache_path, asset_safety.AssetSafetyStatus.SAFE,
        reason=f"fetched via {hit['provider']} for query {query!r} (id {hit['id']})",
        source="fetched_stock_image_no_content_review",
    )
    asset_safety.assert_asset_safe_for_assembly(cache_path)
    return cache_path


def credit_line(image_path: Path) -> str:
    """Dòng ghi nguồn cho phần mô tả video. Pexels/Pixabay không bắt buộc
    ghi công, nhưng kênh công khai thì nên ghi."""
    meta = image_path.with_suffix(".source.json")
    try:
        d = json.loads(meta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    who = d.get("author") or "(không rõ)"
    return f"Ảnh: {who} — {d.get('provider', '').title()} ({d.get('page', '')})"
