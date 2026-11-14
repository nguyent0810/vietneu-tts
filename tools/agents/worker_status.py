"""Điều phối thợ (Agy, Grok, Codex) theo hạn mức THẬT, không gọi lặp thợ đang cạn.

    python worker_status.py available agy        # exit 0 nếu nên giao việc cho thợ này
    python worker_status.py record agy LOGFILE   # sau khi giao task: đọc lỗi ở CUỐI log, cập nhật trạng thái
    python worker_status.py probe grok           # ép thử ngay (bỏ qua lịch chờ)
    python worker_status.py reset grok           # người dùng vừa nạp tiền / đổi gói -> dùng lại ngay
    python worker_status.py status               # bảng trạng thái + lần thử kế tiếp

Ba loại cạn, ba cách chờ (bản 23/10; bản 22/10 thử lại mỗi giờ nên Agy bị giao 3 task trượt, Grok bị thử
mỗi 30 phút dù đã hết tiền):
- "reset"   : lỗi có giờ reset (Agy "Resets in 75h18m"). TIN giờ đó, không gọi thợ trước giờ reset -- lệnh thử
              nhẹ của Agy từng báo OK trong khi task thật vẫn cạn, nên thử nhẹ vô nghĩa. Qua giờ reset: giao
              task thật luôn (task chính là lần thử).
- "balance" : hết tiền / hết gói, không tự hồi (Grok 402 "usage balance exhausted"). Thử nhẹ giãn dần
              1h -> 2h -> 4h -> 8h -> 12h (thử nhẹ của Grok đi cùng đường thanh toán nên đáng tin). Người dùng nạp
              tiền thì chạy `reset grok`.
- "rate"    : 429 tạm thời, không có giờ reset -> chờ 15 phút.
Codex: đọc hạn mức thật từ ~/.codex/sessions (rate_limits), không cần thử.
Nhận diện cạn CHỈ bằng chữ ký lỗi của CLI ở 60 dòng cuối log -- không quét cả log (log chứa nội dung ticket).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

G = Path(__file__).resolve().parent
ROOT = G.parents[1]
STATE = ROOT / "output/cl_staging/grok/worker_state.json"
PROBE_TIMEOUT = 120
RATE_WAIT = 15 * 60
BALANCE_BACKOFF = [3600, 2 * 3600, 4 * 3600, 8 * 3600, 12 * 3600]

PROBE_CMD = {
    "agy": ["agy", "-p", "Trả lời đúng một chữ: OK", "--model", "gemini-3.8-flash-high"],
    "grok": ["grok", "-p", "Trả lời đúng một chữ: OK", "--max-turns", "1"],
    "codex": ["codex", "exec", "--skip-git-repo-check", "Trả lời đúng một chữ: OK"],
}
QUOTA_SIG = {
    "agy": r"RESOURCE_EXHAUSTED|Individual quota reached|AGY_ERROR.*\b429\b",
    "grok": r"Payment Required|usage balance exhausted|insufficient credit|credit balance"
            r"|(?:HTTP|status|error|Error)[^\n]{0,30}\b402\b",
    "codex": r"usage limit|You've hit your usage limit|rate_limit_exceeded|quota exceeded",
}
BALANCE_SIG = r"Payment Required|balance exhausted|insufficient credit|credit balance|\b402\b|upgrade your plan"
# tạm thời -> chờ ngắn. Chỉ nhận khi có ngữ cảnh lỗi (không khớp chữ "429" trong nội dung ticket/báo cáo)
RATE_SIG = r"(?:HTTP|status|error|Error|ERROR)[^\n]{0,30}\b429\b|Too Many Requests|rate limit(?:ed)? exceeded"

CODEX_SESS = Path.home() / ".codex" / "sessions"
CODEX_MAX_USED = 90     # % -- chừa lại cho người dùng tự dùng Codex
CODEX_STALE = 6 * 3600  # nhật ký phiên cũ hơn mức này thì không tin (20/10 ghi "free" dù đã lên Go)


def codex_limits() -> dict | None:
    """Đọc hạn mức Codex từ nhật ký phiên gần nhất (~/.codex/sessions/**.jsonl, sự kiện có "rate_limits").
    Không gọi API, không tốn lượt. Chỉ đọc khối rate_limits -- không đọc auth.json."""
    if not CODEX_SESS.exists():
        return None
    files = sorted(CODEX_SESS.rglob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)[:5]
    for f in files:
        last = None
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if '"rate_limits"' in line:
                last = line
        if last:
            m = re.search(r'"rate_limits":(\{.*?"plan_type":"[^"]*"[^}]*\})', last)
            if m:
                try:
                    rl = json.loads(m.group(1))
                    rl["_file_mtime"] = f.stat().st_mtime
                    return rl
                except json.JSONDecodeError:
                    pass
    return None


def load() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def save(st: dict) -> None:
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def parse_reset(text: str, base: float | None = None) -> float | None:
    base = base or time.time()
    m = re.search(r"[Rr]esets? in\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*(?:(\d+)\s*s)?", text)
    if m and any(m.groups()):
        h, mi, s = (int(x or 0) for x in m.groups())
        return base + h * 3600 + mi * 60 + s
    m = re.search(r"try again in\s*(\d+)\s*(hour|minute|second)", text, re.I)
    if m:
        return base + int(m.group(1)) * {"hour": 3600, "minute": 60, "second": 1}[m.group(2).lower()]
    return None


def classify(worker: str, text: str, base: float | None = None) -> tuple[str, str | None, float | None, str]:
    """-> (state, kind, until, note). state: ok | quota. kind: reset | balance | rate."""
    base = base or time.time()
    tail = "\n".join(text.strip().splitlines()[-60:])
    m = re.search(QUOTA_SIG[worker], tail, re.I)
    if m:
        until = parse_reset(tail, base)
        if until:
            return "quota", "reset", until, m.group(0)
        if re.search(BALANCE_SIG, tail, re.I):
            return "quota", "balance", None, m.group(0)
        return "quota", "rate", base + RATE_WAIT, m.group(0)
    if worker != "grok" and re.search(RATE_SIG, tail, re.I):
        return "quota", "rate", base + RATE_WAIT, "rate limit"
    return "ok", None, None, ""


def set_quota(worker: str, kind: str | None, until: float | None, note: str, now: float | None = None) -> dict:
    """Ghi trạng thái cạn + giờ được thử lại (next_try)."""
    now = now or time.time()
    st = load()
    prev = st.get(worker) or {}
    if kind == "balance":
        n = prev.get("fails", 0) if prev.get("kind") == "balance" else 0
        nxt = now + BALANCE_BACKOFF[min(n, len(BALANCE_BACKOFF) - 1)]
        rec = {"state": "quota", "kind": kind, "until": None, "next_try": nxt, "fails": n + 1}
    else:
        rec = {"state": "quota", "kind": kind, "until": until, "next_try": until or now + RATE_WAIT, "fails": 0}
    rec.update(checked=now, note=note[:200])
    st[worker] = rec
    save(st)
    return rec


def set_ok(worker: str, note: str, now: float | None = None, **extra) -> None:
    st = load()
    st[worker] = {"state": "ok", "checked": now or time.time(), "note": note[:200], **extra}
    save(st)


def probe(worker: str) -> bool:
    try:
        r = subprocess.run(PROBE_CMD[worker], cwd=ROOT, capture_output=True, text=True, timeout=PROBE_TIMEOUT,
                           stdin=subprocess.DEVNULL)
        out = (r.stdout or "") + "\n" + (r.stderr or "")
    except FileNotFoundError:
        set_quota(worker, "balance", None, "CLI không có trên máy"); return False
    except subprocess.TimeoutExpired:
        set_quota(worker, "rate", None, "thử nhẹ quá thời gian"); return False
    state, kind, until, note = classify(worker, out)
    if state == "ok" and "OK" not in out:
        set_quota(worker, "rate", None, out.strip().splitlines()[-1][:200] if out.strip() else "không có phản hồi")
        return False
    if state == "quota":
        set_quota(worker, kind, until, note); return False
    set_ok(worker, "thử nhẹ: OK"); return True


def codex_available() -> bool | None:
    rl = codex_limits()
    if not rl or time.time() - rl["_file_mtime"] > CODEX_STALE:
        probe("codex")          # nhật ký cũ (vd. trước khi đổi gói) -> chạy thử nhẹ để Codex ghi hạn mức mới
        rl = codex_limits()
    if not rl:
        return None
    used = max((rl.get(k) or {}).get("used_percent", 0) for k in ("primary", "secondary"))
    until = max([(rl.get(k) or {}).get("resets_at") or 0 for k in ("primary", "secondary")]) or None
    note = f"đã dùng {used:.0f}% (gói {rl.get('plan_type')})"
    if rl.get("rate_limit_reached_type") or used >= CODEX_MAX_USED:
        set_quota("codex", "reset", until, note); return False
    set_ok("codex", note, reset_at=until); return True


def agy_any_pool(now: float | None = None) -> bool:
    """Còn pool Agy nào đủ dùng (agy_route chọn model theo pool)? Lỗi đọc /quota -> False (giữ hành vi cũ)."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("agy_route", ROOT / "scripts/agents/agy_route.py")
        R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
        pools = R.quota(fresh=True)
        return any(R.usable(m, pools) for routes in R.ROUTES.values() for m, _ in routes)
    except Exception:
        return False


def available(worker: str, now: float | None = None) -> bool:
    now = now or time.time()
    if worker == "codex":
        r = codex_available()
        if r is not None:
            return r
    w = load().get(worker)
    if not w or w["state"] == "ok":
        return True
    if worker == "agy" and agy_any_pool(now):
        return True                        # 06/11: Agy có 3 pool riêng; một pool cạn không chặn cả thợ
    nxt = w.get("next_try") or w.get("until") or 0
    if now < nxt:
        return False                       # chưa tới giờ -> KHÔNG gọi thợ, kể cả thử nhẹ
    if w.get("kind") == "reset":
        set_ok(worker, "qua giờ reset -- giao task thật", now)
        return True                        # thử nhẹ không đáng tin với loại này; task thật là lần thử
    return probe(worker)                   # balance / rate: thử nhẹ rồi mới giao


def record(worker: str, logfile: str) -> None:
    lf = Path(logfile)
    text = lf.read_text(encoding="utf-8", errors="replace") if lf.exists() else ""
    base = lf.stat().st_mtime if lf.exists() else None
    state, kind, until, note = classify(worker, text, base)
    if state == "quota":
        set_quota(worker, kind, until, note, base)
    else:
        set_ok(worker, "task chạy xong")


def reset(worker: str) -> None:
    set_ok(worker, "người dùng báo đã nạp / đổi gói")


def fmt(t: float | None) -> str:
    return time.strftime("%d/%m %H:%M", time.localtime(t)) if t else "-"


def status() -> None:
    st = load()
    for w in PROBE_CMD:
        s = st.get(w)
        if not s:
            print(f"{w:6} chưa có dữ liệu (coi như dùng được)"); continue
        if s["state"] == "ok":
            print(f"{w:6} ok       {'':24} kiểm {fmt(s['checked'])} | {s.get('note', '')}")
            continue
        kind = {"reset": "chờ reset", "balance": "hết tiền", "rate": "429 tạm"}.get(s.get("kind"), s.get("kind"))
        extra = " (nạp xong: worker_status.py reset " + w + ")" if s.get("kind") == "balance" else ""
        print(f"{w:6} {kind:9} thử lại ≥ {fmt(s.get('next_try')):12} kiểm {fmt(s['checked'])} | {s.get('note', '')}{extra}")


if __name__ == "__main__":
    if "--help" in sys.argv:
        import argparse
        argparse.ArgumentParser(description=__doc__).print_help()
        raise SystemExit(0)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "available":
        sys.exit(0 if available(sys.argv[2]) else 1)
    elif cmd == "record":
        record(sys.argv[2], sys.argv[3])
    elif cmd == "probe":
        print("OK" if probe(sys.argv[2]) else "KHÔNG"); status()
    elif cmd == "reset":
        reset(sys.argv[2]); status()
    else:
        status()
