"""Review storytelling Long theo từng chương; không tự sửa kịch bản."""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from motion.long import script_lines

NO_SHELL = "KHÔNG chạy lệnh shell (run_command bị cấm và sẽ làm hỏng phiên). Chỉ dùng công cụ tìm kiếm và đọc web có sẵn. URL nào không mở được thì ghi 'không mở được'."
MODEL = "gemini-4-argon-high"
PROMPT_FILE = ROOT / "docs" / "pm" / "prompts" / "long-story-review.md"
AGENTS = ("c", "local", "grok")


def line_text(line):
    return line if isinstance(line, str) else line["t"]


GUIDE = ROOT / "docs" / "pm" / "storytelling-guide.md"


def flow_rules(guide=None) -> str:
    """Bảng 6 luật §13 "Mạch kể Long" của guide (Lead thêm 11/11: review thật trên máy C bỏ sót luật 4, 5, 6 khi chỉ có prompt)."""
    text = (guide or GUIDE).read_text(encoding="utf-8")
    m = re.search(r"## 13\. Mạch kể Long.*?\n(\|.*?)\n\n", text, re.DOTALL)
    return m.group(1) if m else ""


def make_prompt(chapters, index, factcheck, prompt_file=None):
    template = (prompt_file or PROMPT_FILE).read_text(encoding="utf-8")
    match = re.search(r"```text\s*\n(.*?)\n```", template, re.DOTALL)
    if not match:
        raise ValueError("Không tìm thấy khối text trong prompt review")
    chapter = chapters[index]
    previous = line_text(chapters[index - 1]["lines"][-1]) if index > 0 and chapters[index - 1]["lines"] else "(không có)"
    following = line_text(chapters[index + 1]["lines"][0]) if index + 1 < len(chapters) and chapters[index + 1]["lines"] else "(không có)"
    numbered = "\n".join(f"{i}. {line_text(line)}" for i, line in enumerate(chapter["lines"]))
    return (f"{match.group(1)}\n\n"
            f"Sáu luật mạch kể của kênh (kiểm từng luật, ví dụ chỉ để minh họa, không phải dữ kiện của bài này):\n{flow_rules()}\n\n"
            f"Chương: {chapter['name'].upper()} · {chapter['title']}\n"
            f"Câu cuối chương trước: {previous}\nCâu đầu chương sau: {following}\n\n"
            f"Lời đọc (chỉ số câu từ 0):\n{numbered}\n\n"
            f"Factcheck (tối đa 12.000 ký tự):\n{factcheck[:12000]}\n\n"
            "Trả lời bằng ba mục: Review (4–6 đoạn, mỗi đoạn có vấn đề và bản sửa); "
            "Bản viết lại (toàn chương); Cần xác minh (gạch đầu dòng).\n")


def ask(agent, prompt) -> str:
    if agent in ("c", "local"):
        prompt = NO_SHELL + "\n\n" + prompt
    stream = json.dumps({"event": "user", "message": {"role": "user", "content": prompt}}, ensure_ascii=False) + "\n"
    agy = ["agy", "--model", MODEL, "--input-format", "stream-json", "--output-format", "stream-json", "--print-timeout", "1800s", "-p="]
    if agent == "c":
        remote = 'agy --model gemini-4-argon-high --input-format stream-json --output-format stream-json --print-timeout 1800s "-p="'
        cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-l", "du bi", "100.65.218.98", remote]
    elif agent == "local":
        cmd = agy
    else:
        cmd = ["grok", "-p"]
    result = subprocess.run(cmd, input=stream if agent != "grok" else prompt, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=1860, check=False)
    if result.returncode:
        raise RuntimeError(f"{agent} thoát mã {result.returncode}")
    if agent == "grok":
        response = result.stdout.strip()
    else:
        events = []
        for line in result.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict) and event.get("event") == "result":
                events.append(event)
        if not events or not isinstance(events[-1].get("result"), dict):
            raise RuntimeError(f"{agent} không có result hợp lệ")
        final = events[-1]["result"]
        response = final.get("response", "")
        response = response.strip() if isinstance(response, str) else ""
        if not response and final.get("denied_actions"):
            raise RuntimeError(f"{agent} bị từ chối action: {json.dumps(final['denied_actions'], ensure_ascii=False)}")
        if final.get("status") != "SUCCESS":
            raise RuntimeError(f"{agent} không thành công")
    if not response:
        raise RuntimeError(f"{agent} trả kết quả rỗng")
    return response


def run_agent(agent, prompt):
    return ask(agent, prompt)


def review(prompt, start_agent):
    errors = []
    for agent in AGENTS[AGENTS.index(start_agent):]:
        try:
            return agent, run_agent(agent, prompt)
        except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
            errors.append(f"{agent}: {type(exc).__name__}: {exc}")
    raise RuntimeError("Không agent nào thành công: " + ", ".join(errors))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic")
    parser.add_argument("chapters", nargs="*", metavar="chNN")
    parser.add_argument("--agent", choices=AGENTS, default="c")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.topic):
        parser.error("topic không hợp lệ")
    directory = ROOT / "data" / "long" / args.topic
    chapters = script_lines.parse((directory / "script.md").read_text(encoding="utf-8"))
    names = {c["name"] for c in chapters}
    selected = {name.lower() for name in args.chapters} if args.chapters else names
    if selected - names:
        parser.error("Không có chương: " + ", ".join(sorted(selected - names)))
    factcheck = (directory / "factcheck.md").read_text(encoding="utf-8")
    out_dir = directory / "story_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    failures = []
    for i, chapter in enumerate(chapters):
        if chapter["name"] not in selected:
            continue
        prompt = make_prompt(chapters, i, factcheck)
        if args.dry_run:
            path = out_dir / f"{chapter['name']}.prompt.md"
            path.write_text(prompt, encoding="utf-8")
        else:
            try:
                agent, response = review(prompt, args.agent)
            except RuntimeError as exc:
                failures.append(f"{chapter['name']}: {exc}")
                continue
            model = MODEL if agent in ("c", "local") else "mặc định của grok"
            path = out_dir / f"{chapter['name']}.md"
            path.write_text(f"Agent: {agent}\nModel: {model}\nNgày: {date.today().isoformat()}\n\n{response}\n", encoding="utf-8")
        print(path)
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    from factory.console import utf8_console
    utf8_console()
    main()
