"""Chống trùng CHỦ ĐỀ với mọi video trên kênh (cả bài nguồn đăng khác), cho short BUD/FS.

Chuyển thể factory/lines/novelty.py của Youtube_Creator_V2 (04/10/2026). Trước đây mỗi đợt short phải grep tay
tiêu đề cũ ("tai dài", "rửa chén", "bàn thờ"...) và vẫn có thể sót bài của nguồn ngoài (V2 từng trùng nguyên
tiêu đề "Vì sao tượng Phật có dái tai dài?").

Cách so: tiếng Việt mang nghĩa ở TỪ GHÉP -> so cặp âm tiết liền nhau (bigram), GIỮ DẤU, bỏ hư từ. Trùng khi:
  - chung >= 2 cặp âm tiết
  - Jaccard âm tiết >= 0.6
  - cùng mở đầu bằng một cặp chủ thể (không phải cặp quá phổ biến trên kênh)
Bắt thừa đôi chút chấp nhận được (giá là viết lại một tiêu đề), bỏ sót là đăng lặp chủ đề.

Nguồn tiêu đề: plan của pipeline này + chunks_cache/channel_titles/<kênh>.json (mọi video trên kênh).
    python hf_novelty.py refresh            # làm mới tiêu đề kênh (videos.list, ~1 đơn vị/50 video; không dùng search.list)
    python hf_novelty.py check bud "Tiêu đề"
"""
from __future__ import annotations

import collections
import glob
import json
import re
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TITLES_DIR = ROOT / "chunks_cache" / "channel_titles"
CHANNELS = {"bud": ".youtube_channels/phat_giao.json", "fs": ".youtube_channels/phong_thuy.json"}
GENERIC_TOP = 80   # 3.300 tiêu đề: cụm như "tượng phật", "kỵ đặt", "hợp màu" là khuôn, không phải chủ đề
STOP = set("có là không và của một những các cho được với thì mà vì sao hay này đó trong khi người bạn "
           "mình phải thật chỉ lại gì ai nào đi ra vào thế như từ đến tại để lên ở nhé ơi rồi đã sẽ "
           "đang cũng rất quá nên còn nữa hơn nhất".split())


def _tokens(t: str) -> list[str | None]:
    """Âm tiết giữ dấu; số/ký hiệu thành None để NGẮT cụm ("năm 1990 Canh Ngọ" không thành "năm canh")."""
    t = unicodedata.normalize("NFC", t.lower())
    return [None if w.isdigit() else w for w in re.split(r"[^\w]+", t) if w]


def syllables(t: str) -> list[str]:
    return [w for w in _tokens(t) if w]


def bigrams(t: str) -> set[str]:
    s = _tokens(t)
    return {f"{a} {b}" for a, b in zip(s, s[1:]) if a and b and a not in STOP and b not in STOP}


def _head(t: str) -> str | None:
    s = [w if (w and w not in STOP) else None for w in _tokens(t)]
    return next((f"{a} {b}" for a, b in zip(s, s[1:]) if a and b), None)


def similar(a: str, b: str, generic: frozenset = frozenset()) -> bool:
    na, nb = set(re.findall(r"\d+", a)), set(re.findall(r"\d+", b))
    if na and nb and not na & nb:      # "Sinh năm 1990..." và "Sinh năm 1995...": cùng khuôn, khác chủ đề
        return False
    if len((bigrams(a) & bigrams(b)) - generic) >= 2:
        return True
    sa, sb = set(syllables(a)) - STOP, set(syllables(b)) - STOP
    if sa and sb and len(sa & sb) / len(sa | sb) >= 0.6:
        return True
    ha, hb = _head(a), _head(b)
    return bool(ha) and ha == hb and ha not in generic


@lru_cache(maxsize=None)
def corpus(ch: str) -> tuple[tuple[tuple[str, str], ...], frozenset]:
    """((nhãn, tiêu đề)...) của kênh: video trên YouTube + row trong plan (gồm cả row chưa đăng)."""
    items: dict[str, tuple[str, str]] = {}
    f = TITLES_DIR / f"{ch}.json"
    if f.exists():
        for v in json.loads(f.read_text(encoding="utf-8"))["videos"]:
            items["yt:" + v["id"]] = ("yt:" + v["id"], v["title"])
    led = {}
    for lane in (ch, "long"):
        p = ROOT / f"output/cl_staging/{lane}/uploaded.json"
        if p.exists():
            led.update(json.loads(p.read_text(encoding="utf-8")))
        for fp in glob.glob(str(ROOT / f"output/cl_staging/{lane}/plan_*.json")):
            for r in json.loads(Path(fp).read_text(encoding="utf-8")):
                if r.get("series") != ch:
                    continue
                vid = led.get(r["id"])
                items["yt:" + vid if vid else "plan:" + r["id"]] = ("plan:" + r["id"], r["title"])
    freq = collections.Counter(bg for _, t in items.values() for bg in bigrams(t))
    return tuple(items.values()), frozenset(bg for bg, _ in freq.most_common(GENERIC_TOP))


def duplicates(ch: str, title: str, self_id: str | None = None) -> list[tuple[str, str]]:
    """Mọi (nhãn, tiêu đề) trên kênh trùng chủ đề với `title`, trừ chính row `self_id`."""
    items, generic = corpus(ch)
    return [(k, t) for k, t in items if k != f"plan:{self_id}" and similar(title, t, generic)]


def refresh() -> None:
    sys.path.insert(0, str(ROOT))
    import hf_coverage as H  # noqa: PLC0415
    get, channels_url, _, videos_url = H._api()
    TITLES_DIR.mkdir(parents=True, exist_ok=True)
    for ch, cred in CHANNELS.items():
        cred = str(ROOT / cred)
        me = get(cred, channels_url, {"part": "id", "mine": "true"})["items"][0]["id"]
        found, _, _ = H.discover_ids(cred)
        ids = sorted(found | H.load_index(channel=me))
        vids = []
        for i in range(0, len(ids), 50):
            for v in get(cred, videos_url, {"part": "snippet", "id": ",".join(ids[i:i + 50])}).get("items", []):
                if v["snippet"].get("channelId") == me:
                    vids.append({"id": v["id"], "title": v["snippet"]["title"]})
        (TITLES_DIR / f"{ch}.json").write_text(json.dumps({"channel": me, "videos": vids}, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"{ch}: {len(vids)} tiêu đề")


if __name__ == "__main__":
    if sys.argv[1:2] == ["refresh"]:
        refresh()
    elif sys.argv[1:2] == ["check"]:
        for k, t in duplicates(sys.argv[2], " ".join(sys.argv[3:])):
            print(f"  trùng {k}: {t}")
