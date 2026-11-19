"""Viết lời Long bằng Gemini web (gemini_chat.py, #500), thay tool Flow "Viết lời đọc" (#497).

    python scripts/viet_loi.py <KÊNH> <slug> <thư-mục-4-file> --phase ch00-01   # lượt 1: chat mới, CH00 + CH01
    python scripts/viet_loi.py <KÊNH> <slug> <thư-mục-4-file> --phase rest      # lượt 2: viết tiếp trong cùng chat

- Thư mục input có 4 file, xếp theo tên: hồ sơ truyện, bảng dữ kiện, giọng mẫu, dàn chương
  (dàn chương: mỗi chương một dòng, nên có `CHnn`).
- Prompt = `docs/pm/prompt-viet-loi.md` (phần sau `---`) + hồ sơ kênh + 4 input. Sửa cách viết ở file đó.
- Lượt `rest` viết `--batch` chương mỗi tin nhắn (mặc định 3) trong cùng cuộc chat để Gemini giữ giọng CH00–CH01
  và không bị cắt câu trả lời dài.
- Trạng thái (link chat, các phần đã viết) ở `output/viet_loi/<KÊNH>_<slug>/`; bản ghép ở
  `output/script_inbox/<KÊNH>_<slug>_<ngày>_<phase>.md`, đã làm sạch định dạng, rồi kiểm bằng `prose_to_script.py`.
- Thiếu chương (không có tiêu đề hoặc thân < 40 chữ): lưu kèm `_partial`, thoát mã 3.
- Cần đăng nhập Gemini một lần: `python scripts/gemini_chat.py login`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from flow_viet_loi import tidy  # noqa: E402

PROMPT = ROOT / "docs" / "pm" / "prompt-viet-loi.md"
STATE = ROOT / "output" / "viet_loi"
INBOX = ROOT / "output" / "script_inbox"
LABELS = ["Hồ sơ truyện", "Bảng dữ kiện", "Giọng mẫu", "Dàn chương"]
MIN_WORDS = 40


def outline_chapters(text: str) -> list[str]:
    """Chương mong đợi: các `CHnn` trong dàn chương; không có thì đếm dòng không trống."""
    nums = re.findall(r"(?im)^\W*CH\s*(\d{1,2})\b", text)
    if nums:
        return sorted({f"CH{int(n):02d}" for n in nums})
    lines = [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    return [f"CH{i:02d}" for i in range(len(lines))]


def normalize(text: str) -> str:
    """Khi Gemini không cho chép Markdown, tiêu đề mất `##` (còn "CH00 · Tên"): thêm lại."""
    return re.sub(r"(?m)^[ \t]*(?:#+[ \t]*)?\**CH[ \t]*(\d{1,2})\**[ \t]*[·:.\-–—][ \t]*",
                  lambda m: f"## CH{int(m.group(1)):02d} · ", text)


def chapters(text: str) -> dict[str, str]:
    """{CHnn: khối từ dòng `## CHnn` tới trước chương kế}."""
    text = normalize(text)
    out = {}
    for m in re.finditer(r"(?ms)^##\s*CH(\d{1,2})\b.*?(?=^##\s*CH\d|\Z)", text):
        out[f"CH{int(m.group(1)):02d}"] = m.group(0).strip() + "\n"
    return out


def missing_chapters(text: str, want: list[str]) -> list[str]:
    have = {k: len(v.split("\n", 1)[1].split()) if "\n" in v else 0 for k, v in chapters(text).items()}
    return [c for c in want if have.get(c, 0) < MIN_WORDS]


def instructions(channel: str) -> str:
    doc = PROMPT.read_text(encoding="utf-8")
    head, _, body = doc.partition("\n---\n")
    m = re.search(rf"(?ms)^### {re.escape(channel)}\s*\n(.*?)(?=^### |^## |\Z)", head)
    if not m:
        raise SystemExit(f"{PROMPT.name} chưa có hồ sơ kênh {channel}")
    return body.strip() + f"\n\nHồ sơ kênh {channel}: {m.group(1).strip()}\n"


def first_prompt(channel: str, texts: list[str]) -> str:
    blocks = "\n\n".join(f"===== {lab} =====\n{t.strip()}" for lab, t in zip(LABELS, texts))
    return (instructions(channel) + "\n" + blocks +
            "\n\n===== Lượt này =====\nChỉ viết CH00 và CH01 theo dàn chương, rồi dừng.\n")


def rest_prompt(batch: list[str], last: str) -> str:
    return (f"Viết tiếp {', '.join(batch)} theo dàn chương, nối liền mạch sau {last} và giữ đúng giọng các chương "
            "đã viết. Cùng mọi luật và định dạng như trên. Chỉ trả về các chương này.\n")


def ask(prompt: str, out: Path, chat: str | None, a) -> str:
    """Gọi gemini_chat.py ask; trả link chat."""
    pf = out.with_suffix(".prompt.md")
    pf.write_text(prompt, encoding="utf-8")
    cmd = [sys.executable, str(ROOT / "scripts" / "gemini_chat.py"), "ask", str(pf), "--out", str(out),
           "--model", a.model, "--thinking", a.thinking, "--timeout", str(a.timeout)]
    if chat:
        cmd += ["--chat", chat]
    if a.headless:
        cmd.append("--headless")
    for attempt in (1, 2):  # Gemini đôi khi không nhận tin nhắn: thử lại một lần
        out.unlink(missing_ok=True)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        print((r.stdout + r.stderr).strip()[-600:])
        if not r.returncode and out.is_file():
            break
        if attempt == 2:
            raise SystemExit(f"gemini_chat lỗi (mã {r.returncode}); chạy lại lệnh để viết bù")
        print("thử lại sau 60 giây…", flush=True)
        time.sleep(60)
    m = re.search(r"^chat: (\S+)", r.stdout, re.M)
    return m.group(1) if m else (chat or "")


def save(channel: str, slug: str, phase: str, text: str) -> Path:
    INBOX.mkdir(parents=True, exist_ok=True)
    base = f"{channel}_{slug}_{dt.date.today().isoformat()}_{phase}"
    out, n = INBOX / f"{base}.md", 1
    while out.exists():
        n += 1
        out = INBOX / f"{base}_v{n}.md"
    out.write_text(text, encoding="utf-8")
    return out


def main() -> int:
    from factory.console import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("channel")
    ap.add_argument("slug")
    ap.add_argument("inputs")
    ap.add_argument("--phase", choices=["ch00-01", "rest"], default="ch00-01")
    ap.add_argument("--batch", type=int, default=3, help="số chương mỗi tin nhắn ở lượt rest")
    ap.add_argument("--model", default="Neon")
    ap.add_argument("--thinking", default="High")
    ap.add_argument("--timeout", type=int, default=1500)
    ap.add_argument("--headless", action="store_true")
    a = ap.parse_args()
    ch = a.channel.upper()
    files = sorted(p for p in Path(a.inputs).iterdir() if p.is_file())
    if len(files) < 4:
        raise SystemExit(f"{a.inputs}: cần 4 file (hồ sơ, dữ kiện, giọng mẫu, dàn chương), có {len(files)}")
    texts = [f.read_text(encoding="utf-8") for f in files[:4]]
    want = outline_chapters(texts[3])
    sd = STATE / f"{ch}_{a.slug}"
    sd.mkdir(parents=True, exist_ok=True)
    sf = sd / "state.json"
    st = json.loads(sf.read_text(encoding="utf-8")) if sf.is_file() else {}

    if a.phase == "ch00-01":
        out = sd / "ch00-01.md"
        st = {"chat": ask(first_prompt(ch, texts), out, None, a), "parts": [out.name]}
        sf.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
        want = ["CH00", "CH01"]
    else:
        if not st.get("chat"):
            raise SystemExit("chưa có lượt ch00-01 cho đề tài này (không thấy link chat)")
        done = chapters("\n".join((sd / p).read_text(encoding="utf-8") for p in st["parts"]))
        todo = [c for c in want if c not in done or missing_chapters(done[c], [c])]
        for i in range(0, len(todo), a.batch):
            batch = todo[i:i + a.batch]
            last = max(done) if done else "CH01"
            out = sd / f"{batch[0].lower()}-{batch[-1][2:]}.md"
            print(f"viết {', '.join(batch)}…", flush=True)
            st["chat"] = ask(rest_prompt(batch, last), out, st["chat"], a)
            st["parts"].append(out.name)
            sf.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
            done.update(chapters(out.read_text(encoding="utf-8")))

    allch = {}
    for p in st["parts"]:
        allch.update(chapters((sd / p).read_text(encoding="utf-8")))
    text = tidy("\n".join(allch[k] for k in sorted(allch)).replace("\r\n", "\n"))
    miss = missing_chapters(text, want)
    phase = ("ch00-01" if a.phase == "ch00-01" else "full") + ("_partial" if miss else "")
    out = save(ch, a.slug, phase, text)
    print(f"đã lưu {out.relative_to(ROOT)} ({len(text.split())} chữ, {len(allch)} chương)")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "prose_to_script.py"), str(out), str(sd / "check_script.md")],
                       capture_output=True, text=True, encoding="utf-8")
    print((r.stdout + r.stderr).strip()[-1200:])
    if miss:
        print(f"!! thiếu {', '.join(miss)} — chạy lại `--phase rest` để viết bù")
        return 3
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
