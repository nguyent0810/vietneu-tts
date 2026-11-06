"""Chọn model Agy cho một ticket theo loại việc và hạn mức còn lại (`agy -p /quota`).

    python scripts/agents/agy_route.py quota            # in hạn mức (cache 10 phút)
    python scripts/agents/agy_route.py pick TICKET.md   # in "<model> <effort>", exit 3 nếu mọi pool cạn

Agy có 3 pool hạn mức riêng: Gemini (tuần + 5 giờ), Claude/GPT (tuần + 5 giờ), Gemini 4 Argon (tuần).
Mỗi loại ticket có danh sách model ưu tiên; lấy model đầu tiên mà pool của nó còn đủ.
Ticket ghim model bằng dòng `> Model: <id>` trong 15 dòng đầu.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

CACHE = Path(__file__).resolve().parents[2] / "output/cl_staging/grok/heartbeat/agy_quota.json"
CACHE_TTL = 600

# Ưu tiên theo loại ticket (06/11). Lý do:
# - media/render: chạy builder có sẵn, lặp nhiều bước -> Flash nhanh, pool Gemini rộng.
# - code_fix/code_small: sửa đúng chỗ, ít lan -> Sonnet; Flash từng để lọt lỗi (003b TTS cũ, 138g2 failed).
# - code_shared/code: nhiều file, rủi ro hồi quy -> Opus.
# - research/review/audit: đọc nhiều, cần tổng hợp -> Argon (pool riêng, không ăn pool Gemini/Claude).
# - content: lời Việt, kể truyện -> Opus medium.
ROUTES = {
    "media": [("gemini-3.8-flash-high", "high"), ("claude-sonnet-5-5-medium", "medium"), ("gemini-4-argon-medium", "medium")],
    "code_fix": [("claude-sonnet-5-5-high", "high"), ("gemini-4-argon-high", "high"), ("gemini-3.8-flash-high", "high")],
    "code_small": [("claude-sonnet-5-5-high", "high"), ("gemini-4-argon-high", "high"), ("gemini-3.8-flash-high", "high")],
    "code_shared": [("claude-opus-5-5-high", "high"), ("claude-sonnet-5-5-high", "high"), ("gemini-4-argon-high", "high")],
    "code": [("claude-opus-5-5-high", "high"), ("claude-sonnet-5-5-high", "high"), ("gemini-4-argon-high", "high")],
    "research": [("gemini-4-argon-high", "high"), ("claude-opus-5-5-medium", "medium"), ("gemini-3.8-flash-high", "high")],
    "review": [("gemini-4-argon-high", "high"), ("claude-opus-5-5-medium", "medium"), ("gemini-3.8-flash-high", "high")],
    "content": [("claude-opus-5-5-medium", "medium"), ("claude-sonnet-5-5-high", "high"), ("gemini-4-argon-high", "high")],
    "default": [("gemini-3.8-flash-high", "high"), ("claude-sonnet-5-5-medium", "medium"), ("gemini-4-argon-medium", "medium")],
}
# Ngưỡng tối thiểu (%) để dùng pool; Opus tốn nhiều nên giữ dự trữ cao hơn.
MIN_5H, MIN_WEEK, MIN_WEEK_OPUS = 15, 20, 40


def pool_of(model: str) -> str:
    if model.startswith("gemini-4-argon"):
        return "argon"
    if model.startswith("gemini"):
        return "gemini"
    return "claude_gpt"


def parse_quota(text: str) -> dict:
    """Dòng dạng `Gemini Models<TAB>Weekly Limit Remaining<TAB>100%<TAB>reset`."""
    pools: dict = {}
    for line in text.splitlines():
        parts = [p.strip() for p in line.split("\t")]
        if len(parts) < 3 or not re.fullmatch(r"\d+(?:\.\d+)?%", parts[2]):
            continue
        name, kind, pct = parts[0].lower(), parts[1].lower(), float(parts[2][:-1])
        key = "argon" if "argon" in name else "gemini" if name.startswith("gemini") else "claude_gpt"
        slot = "5h" if "five hour" in kind else "week"
        pools.setdefault(key, {})[slot] = min(pct, pools.get(key, {}).get(slot, 100.0))
        if len(parts) > 3:
            pools[key][slot + "_reset"] = parts[3]
    return pools


def quota(fresh: bool = False) -> dict:
    if not fresh and CACHE.exists() and time.time() - CACHE.stat().st_mtime < CACHE_TTL:
        return json.loads(CACHE.read_text())
    out = subprocess.run(["agy", "-p", "/quota"], capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    pools = parse_quota(out.stdout)
    if pools:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(pools, indent=1))
    return pools


def usable(model: str, pools: dict) -> bool:
    p = pools.get(pool_of(model))
    if p is None:  # không đọc được pool -> không chặn
        return True
    week_min = MIN_WEEK_OPUS if "opus" in model else MIN_WEEK
    return p.get("5h", 100) >= MIN_5H and p.get("week", 100) >= week_min


def ticket_type(text: str) -> str:
    head = "\n".join(text.splitlines()[:15])
    m = re.search(r"^type:\s*([^\s#]+)", head, re.M)
    t = (m.group(1) if m else "").lower()
    for key in ("code_shared", "code_small", "code_fix", "media", "research", "review", "content", "code"):
        if key in t or (key == "media" and "render" in t) or (key == "code_fix" and "fix" in t):
            return key
    return "default"


def pick(text: str, pools: dict) -> tuple[str, str] | None:
    head = "\n".join(text.splitlines()[:15])
    pin = re.search(r"^>\s*Model:\s*(\S+)", head, re.M)
    if pin:
        return pin.group(1), "high" if pin.group(1).endswith("high") else "medium"
    for model, effort in ROUTES[ticket_type(text)]:
        if usable(model, pools):
            return model, effort
    return None


def main(argv: list[str]) -> int:
    if argv[:1] == ["quota"]:
        print(json.dumps(quota(fresh="--fresh" in argv), indent=1))
        return 0
    if argv[:1] == ["pick"] and len(argv) > 1:
        try:
            pools = quota()
        except Exception:
            pools = {}
        got = pick(Path(argv[1]).read_text(encoding="utf-8"), pools)
        if got is None:
            return 3
        print(*got)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
