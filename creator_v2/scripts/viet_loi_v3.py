"""Viết lời Long bằng khuôn Gemini v3 (docs/prompts/long-v3/, #546) rồi gắn mốc chương (#548).

    python scripts/viet_loi_v3.py <KÊNH> <slug> [--loai dai|vua] [--cach <MÃ>] [--max-turns 6] [--write-prose]
    python scripts/viet_loi_v3.py <KÊNH> <slug> --dry-run      # chỉ in prompt đã điền, không mở trình duyệt

Luồng: điền khuôn (KENH_LUAT, GIONG, CACH_TRIEN_KHAI xoay vòng, TRANH_LAP, DU_KIEN, DAN_HOI) -> `gemini_chat.py ask`
-> các lượt "viết tiếp" trong cùng chat (mỗi lượt lưu `v3_partNN.md`) -> một lượt gắn mốc `## CHnn · Tên`
(kiểm máy: bỏ dòng ## thì phải trùng bản gốc; lệch thì dùng bộ chia cục bộ) -> `output/script_inbox/<KÊNH>_<slug>_<ngày>_v3.md`;
với --write-prose còn ghi `data/long/<slug>/prose.md` và chạy `prose_to_script.py` ra `script.md`.
Chạy lại cùng lệnh thì viết tiếp từ state (`output/viet_loi/<KÊNH>_<slug>/state.json`, khoá "v3").
Giọng mẫu `docs/pm/giong-mau/` KHÔNG dùng ở v3. `viet_loi.py` (khuôn cũ) giữ làm dự phòng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from flow_viet_loi import tidy  # noqa: E402
from gemini_chat import chat_id  # noqa: E402
from viet_loi import ask, normalize  # noqa: E402

TEMPLATES = ROOT.parent / "docs" / "prompts" / "long-v3"
LONG = ROOT / "data" / "long"
STATE = ROOT / "output" / "viet_loi"
INBOX = ROOT / "output" / "script_inbox"
ROTATION = STATE / "_v3_rotation.json"
PROFILES = ROOT / "docs" / "pm" / "prompt-viet-loi.md"
PREFIX = {"CL": "cl-", "MIM": "mim-", "CK": "ck-", "FS": "fs-", "BUD": "bud-"}
MIN_NEW_WORDS = 150
PLACEHOLDER = re.compile(r"\{([A-Z_]+)\}")
CHAPTER = re.compile(r"^## CH(\d\d) · .+$")
DEFAULT_CONTINUE = ("Viết tiếp ngay từ câu cuối bạn vừa viết, cùng giọng, cùng quy tắc, không viết lại phần đã có và "
                    "không tóm tắt. Nếu bài đã đủ ý thì đi tới phần gần cuối và đóng vòng như đã nói.")

# Cách triển khai riêng từng kênh (kenh_luat.md), mô tả 2 dòng theo mẫu của 6 cách gốc.
EXTRA = {
    "HAI_NGUOI_CUNG_TUOI": "Hai người cùng tuổi nhưng hoàn cảnh khác nhau; dùng dữ kiện để lý giải chỗ khác; nhân vật là ví dụ giả định, nói rõ.",
    "KIEM_TRA_TRUOC_QUYET_DINH": "Người nghe sắp chốt một việc; mỗi lớp là một thứ cần tự kiểm trước khi tin nhãn truyền thống.",
    "CAU_CHUYEN_DOI_NGUOI": "Một người (trong kinh hoặc nhân vật giả định nói rõ) đi qua một cơ cực; lời dạy chỉ xuất hiện đúng lúc người ấy cần, không đọc trước.",
    "HAI_CAU_CHUYEN_SOI_NHAU": "Kể một câu chuyện trong kinh, rồi một cảnh đời thường hôm nay, để cảnh sau làm sáng nghĩa cảnh trước; nối bằng \"nhưng\" hoặc \"vì vậy\".",
    "CAI_GIA_TUNG_BUOC": "Mỗi đoạn là một quyết định và một thứ nhân vật mất đi; nối bằng \"nhưng\" và \"vì vậy\".",
    "HAI_PHIA": "Kể song song kẻ gây án và người truy tìm rồi cho hai mạch gặp nhau.",
    "TAI_SAO_LAI_SAI": "Mở bằng kết quả hỏng, đi ngược từng quyết định tới gốc, mỗi lớp lật nghĩa lớp trước.",
    "MOT_NGUOI_MOT_QUYET_DINH": "Một người giả định đứng trước một lựa chọn, mỗi lớp là một thứ phải cân; kết trả bằng câu \"cái cân của bạn nằm ở đâu\".",
}
CACH_KENH = {
    "FS": ["HANH_TRINH", "VONG_MO", "THOI_GIAN", "HOI_DAP", "VAT_XUYEN_SUOT", "NGHICH_LY", "HAI_NGUOI_CUNG_TUOI", "KIEM_TRA_TRUOC_QUYET_DINH"],
    "BUD": ["VONG_MO", "VAT_XUYEN_SUOT", "NGHICH_LY", "HOI_DAP", "CAU_CHUYEN_DOI_NGUOI", "HAI_CAU_CHUYEN_SOI_NHAU"],
    "CL": ["HANH_TRINH", "THOI_GIAN", "VONG_MO", "NGHICH_LY", "VAT_XUYEN_SUOT", "CAI_GIA_TUNG_BUOC", "HAI_PHIA"],
    "MIM": ["NGHICH_LY", "VONG_MO", "THOI_GIAN", "HOI_DAP", "VAT_XUYEN_SUOT", "HANH_TRINH", "TAI_SAO_LAI_SAI"],
    "CK": ["HOI_DAP", "NGHICH_LY", "VONG_MO", "VAT_XUYEN_SUOT", "MOT_NGUOI_MOT_QUYET_DINH"],
}


# ---------------------------------------------------------------- khuôn và chỗ điền

def template_parts(loai: str) -> tuple[str, str]:
    """(thân prompt sau đường --- đầu tiên và trước khối LƯỢT HAI, lời nhắn viết tiếp)."""
    text = (TEMPLATES / f"khuon_long_{loai}.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == "---")
    rest = lines[start + 1:]
    stop = next((i for i, l in enumerate(rest) if l.lstrip(" -").startswith("LƯỢT HAI")), None)
    body = "\n".join(rest[:stop] if stop is not None else rest)
    body = re.sub(r"\n+---\s*$", "", body.rstrip()).strip()
    cont = DEFAULT_CONTINUE
    if stop is not None:
        after = "\n".join(rest[stop + 1:]).strip()
        cont = after or DEFAULT_CONTINUE
    return body, cont


def fill_template(body: str, values: dict[str, str]) -> str:
    """Điền một lượt (không điền lại vào chữ đã chèn). Còn {TÊN} chưa có giá trị thì báo lỗi."""
    missing = sorted({m for m in PLACEHOLDER.findall(body) if m not in values})
    if missing:
        raise ValueError(f"khuôn còn chỗ chưa có giá trị: {', '.join(missing)}")
    return PLACEHOLDER.sub(lambda m: values[m.group(1)], body)


def channel_rules(channel: str) -> tuple[str, str]:
    """(KENH_LUAT, GIONG) từ kenh_luat.md, mục `## <KÊNH> (`."""
    text = (TEMPLATES / "kenh_luat.md").read_text(encoding="utf-8")
    m = re.search(rf"(?ms)^## {re.escape(channel)} \(.*?\n(.*?)(?=^## |\Z)", text)
    if not m:
        raise SystemExit(f"kenh_luat.md chưa có mục kênh {channel}")
    sec = m.group(1)
    luat = re.search(r"(?ms)^Luật kênh:\s*\n(.*?)(?=^Giọng:)", sec)
    giong = re.search(r"(?m)^Giọng:\s*(.+)$", sec)
    if not luat or not giong:
        raise SystemExit(f"mục {channel} trong kenh_luat.md thiếu 'Luật kênh:' hoặc 'Giọng:'")
    return luat.group(1).strip(), giong.group(1).strip()


def cach_descriptions() -> dict[str, str]:
    """{MÃ: mô tả} của 6 cách gốc (kenh_luat.md, dòng '- MÃ: ...' trong mục mô tả) + cách riêng kênh."""
    text = (TEMPLATES / "kenh_luat.md").read_text(encoding="utf-8")
    m = re.search(r"(?ms)^## Mô tả 6 cách.*?\n(.*?)(?=^## |\Z)", text)
    out = {k: v.strip() for k, v in re.findall(r"(?m)^- ([A-Z_]+): (.+)$", m.group(1))} if m else {}
    out.update(EXTRA)
    return out


def pick_cach(channel: str, rotation: dict, override: str | None = None, rng: random.Random | None = None) -> str:
    """Cách triển khai chính: --cach nếu có, không thì ngẫu nhiên trong cách hợp kênh, khác cách bài gần nhất cùng kênh."""
    if override:
        return override.upper()
    pool = CACH_KENH.get(channel, CACH_KENH["MIM"])
    last = (rotation.get(channel) or {}).get("last")
    opts = [c for c in pool if c != last] or pool
    return (rng or random).choice(opts)


def cach_text(main: str, loai: str, channel: str, rng: random.Random) -> tuple[str, list[str]]:
    """Nội dung {CACH_TRIEN_KHAI}: Long vừa một cách; Long dài một cách chính + một cách phụ lồng vào."""
    desc = cach_descriptions()
    if main not in desc:
        extra = (TEMPLATES / "cach_trien_khai.md").read_text(encoding="utf-8")
        desc.update({k: v.strip() for k, v in re.findall(r"(?m)^- ([A-Z_]+): (.+)$", extra)})
    if main not in desc:
        raise SystemExit(f"không biết cách triển khai '{main}'; có: {', '.join(sorted(desc))}")
    text, used = f"{main}: {desc[main]}", [main]
    if loai == "dai":
        pool = [c for c in CACH_KENH.get(channel, []) if c != main and c in desc]
        if pool:
            sec = rng.choice(pool)
            text += f"\nCách phụ lồng vào (một đoạn, không thành xương sống): {sec}: {desc[sec]}"
            used.append(sec)
    return text, used


def strip_data(text: str) -> str:
    """DU_KIEN cho Gemini web: bỏ URL, tên file, mã ticket (Gemini không đọc được file)."""
    text = re.sub(r"\[([^\]]*)\]\(https?://[^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"(?<![\w/])[\w\-./\\]+\.(?:md|json|py|txt|pdf|csv|png|jpe?g|html|yml|yaml)\b", "", text, flags=re.I)
    text = re.sub(r"(?<!\w)#\d{2,5}\b", "", text)
    text = re.sub(r"\(\s*[,;]?\s*\)", "", text)                 # ngoặc rỗng sau khi bỏ URL
    text = re.sub(r"[ \t]+([,;:.)])", r"\1", text)
    text = re.sub(r"(?m)[:;,][ \t]*$", ".", text)                  # "…: " cụt cuối dòng
    text = re.sub(r"[ \t]{2,}", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def compact_outline(text: str, limit: int = 380) -> str:
    """DAN_HOI: mỗi dòng dàn chương một dòng gọn (cắt ở cuối câu nếu quá dài)."""
    out = []
    for line in strip_data(text).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if len(line) > limit:
            cut = line[:limit]
            k = max(cut.rfind("; "), cut.rfind(". "), cut.rfind(", "))
            line = (cut[:k] if k > limit // 2 else cut.rsplit(" ", 1)[0]) + "…"
        out.append(line)
    return "\n".join(out)


def opening_lines(script: str, n: int = 2) -> str:
    """Hai câu đầu của CH00 trong script.md / prose.md, bỏ dấu máy ({pd}, ‖, », [PD])."""
    m = re.search(r"(?ms)^##\s*CH00\b[^\n]*\n(.*?)(?=^##\s|\Z)", script)
    if not m:
        return ""
    body = re.sub(r"\{/?pd\}|\[/?PD\]|[‖»]", " ", m.group(1), flags=re.I)
    body = re.sub(r"\s+", " ", body).strip()
    sents = re.split(r"(?<=[.!?…])\s+", body)
    return " ".join(s for s in sents[:n] if s).strip()


def tranh_lap(channel: str, slug: str, root: Path | None = None, limit: int = 5) -> str:
    """Câu mở của các Long gần nhất cùng kênh (theo ngày sửa script.md), trừ bài đang viết."""
    root = root or LONG
    prefix = PREFIX.get(channel, channel.lower() + "-")
    files = [f for f in root.glob(f"{prefix}*/script.md") if f.parent.name != slug]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    items = []
    for f in files:
        s = opening_lines(f.read_text(encoding="utf-8"))
        if s:
            items.append(s)
        if len(items) >= limit:
            break
    if not items:
        return "(chưa có bài nào để tránh)"
    return " ".join(f'({i}) "{s}"' for i, s in enumerate(items, 1))


def topic_inputs(slug: str, channel: str, inputs: Path | None = None) -> dict[str, str]:
    d = inputs or LONG / slug / "viet_loi_in"
    def rd(*names: str) -> str:
        for n in names:
            if (d / n).is_file():
                return (d / n).read_text(encoding="utf-8")
        return ""
    ho_so = rd("1_ho_so.md", "../plan.md")
    du_kien, dan = rd("2_du_kien.md"), rd("4_dan_chuong.md")
    if not ho_so or not du_kien:
        raise SystemExit(f"{d}: cần 1_ho_so.md (hoặc plan.md) và 2_du_kien.md")
    head = next((l for l in ho_so.splitlines() if l.startswith("#")), slug)
    chu_de = re.sub(r"^#+\s*(Hồ sơ truyện\s*[—-]\s*)?", "", head).strip()
    m = re.search(r"(?mi)^\W*(?:người nghe|đối tượng(?: nghe)?)\s*:\s*(.+)$", ho_so)
    if not m and PROFILES.is_file():
        m = re.search(rf"(?ms)^### {re.escape(channel)}\s*\n.*?Người nghe:\s*(.+?)(?:\n\n|\n###|\Z)", PROFILES.read_text(encoding="utf-8"))
    doi_tuong = m.group(1).strip() if m else "người nghe phổ thông, nghe lúc rảnh tay"
    return {"CHU_DE": chu_de, "DOI_TUONG": doi_tuong, "DU_KIEN": strip_data(du_kien), "DAN_HOI": compact_outline(dan) or "(không có dàn gợi ý)"}


def build_prompt(channel: str, slug: str, loai: str, main_cach: str, inputs: Path | None = None,
                 root: Path | None = None, rng: random.Random | None = None) -> tuple[str, str, list[str]]:
    """(prompt lượt đầu, lời viết tiếp, các cách đã dùng)."""
    body, cont = template_parts(loai)
    luat, giong = channel_rules(channel)
    ct, used = cach_text(main_cach, loai, channel, rng or random.Random(slug))
    vals = {"KENH_LUAT": luat, "GIONG": giong, "CACH_TRIEN_KHAI": ct, "TRANH_LAP": tranh_lap(channel, slug, root),
            **topic_inputs(slug, channel, inputs)}
    return fill_template(body, vals), cont, used


# ---------------------------------------------------------------- lượt viết tiếp

def words(text: str) -> int:
    return len(text.split())


def has_dangling_hook(text: str) -> bool:
    """Đoạn cuối còn câu móc dở (câu hỏi, dấu ba chấm, 'lát nữa', 'sắp', 'nhưng'…) hay đã đóng vòng."""
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n", text.strip()) if p.strip() and not p.startswith("#")]
    if not paras:
        return False
    tail = " ".join(paras[-2:])[-420:]
    if not re.search(r"[.!?…\"”»)]\s*$", tail):
        return True
    if re.search(r"\?|…|\.\.\.", tail):
        return True
    return bool(re.search(r"(?i)\b(lát nữa|sắp tới|sắp gặp|chưa hết|còn một|tiếp theo|ở phía sau|phía sau)\b|\bnhưng\b[^.!?]*[.!?]\s*$", tail))


def stop_reason(parts: list[str]) -> str:
    """Lý do dừng sau lượt vừa xong, rỗng nếu còn viết tiếp."""
    if len(parts) > 1 and words(parts[-1]) < MIN_NEW_WORDS:
        return f"lượt cuối chỉ {words(parts[-1])} chữ mới"
    if not has_dangling_hook(parts[-1]):
        return "lượt cuối không còn câu móc dở"
    return ""


# ---------------------------------------------------------------- gắn mốc chương

def _ws(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


def strip_marks(text: str) -> str:
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("## "))


def same_text(original: str, marked: str) -> bool:
    """Bỏ các dòng `## ` đi và chuẩn hoá khoảng trắng thì hai văn bản phải trùng."""
    return _ws(strip_marks(original)) == _ws(strip_marks(marked))


def valid_headings(text: str) -> bool:
    """Có tiêu đề, đúng dạng `## CHnn · Tên`, đánh số liên tiếp từ CH00, và dòng đầu bài là tiêu đề."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    heads = [l for l in lines if l.startswith("## ")]
    if not heads or lines[0] != heads[0]:
        return False
    nums = []
    for h in heads:
        m = CHAPTER.match(h)
        if not m:
            return False
        nums.append(int(m.group(1)))
    return nums == list(range(len(nums)))


def heuristic_mark(text: str, loai: str = "dai") -> str:
    """Dự phòng: chèn `## CHnn · Phần N` ở ranh giới đoạn gần mốc ~800 âm tiết (vừa: 3–5 mốc). Tiêu đề để biên tập sửa."""
    text = strip_marks(text).strip()
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paras) < 2:
        paras = [p.strip() for p in text.splitlines() if p.strip()]
    sizes = [words(p) for p in paras]
    total = sum(sizes)
    n = max(1, round(total / 800)) if loai == "dai" else min(5, max(3, round(total / 700)))
    starts, acc = [], 0
    for s in sizes:
        starts.append(acc)
        acc += s
    cuts = {0}
    for k in range(1, n):
        target = total * k / n
        best = min(range(len(paras)), key=lambda i: (abs(starts[i] - target), i))
        cuts.add(best)
    out, num = [], 0
    for i, p in enumerate(paras):
        if i in cuts:
            out.append(f"## CH{num:02d} · Phần {num + 1}")
            num += 1
        out.append(p)
    return "\n\n".join(out) + "\n"


def marking_prompt(loai: str) -> str:
    quy = ("khoảng một mốc cho mỗi 600–1.000 âm tiết (3–5 phút nghe), tại các chỗ đổi lớp: đoạn nối, câu hỏi mới, mốc kéo lại giữa bài"
           if loai == "dai" else "3 đến 5 mốc, tại các chỗ đổi lớp: đoạn nối, câu hỏi mới")
    return ("Bây giờ hãy trả lại TOÀN BỘ bài viết trên, từ chữ đầu tiên đến chữ cuối cùng, GIỮ NGUYÊN từng chữ, từng dấu câu: "
            "không thêm, bớt, sửa, gộp hay tóm tắt. Việc duy nhất là chèn các dòng tiêu đề chương, mỗi dòng riêng, đúng dạng "
            f"`## CH00 · Tên`, `## CH01 · Tên`, … (đánh số liên tiếp từ CH00; dòng đầu của bài là `## CH00`), {quy}. "
            "Tên chương 3–8 chữ, viết như câu người xem sẽ gõ để tìm. Không thêm lời dẫn, ghi chú hay lời chào nào ngoài văn bản.\n")


# ---------------------------------------------------------------- state và đầu ra

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def save_inbox(channel: str, slug: str, text: str) -> Path:
    INBOX.mkdir(parents=True, exist_ok=True)
    base = f"{channel}_{slug}_{dt.date.today().isoformat()}_v3"
    out, n = INBOX / f"{base}.md", 1
    while out.exists():
        n += 1
        out = INBOX / f"{base}_v{n}.md"
    out.write_text(text, encoding="utf-8")
    return out


def run_turns(a, ch: str, sd: Path, st: dict, first: str, cont: str) -> list[str]:
    """Lượt đầu + các lượt viết tiếp, lưu từng phần; chạy lại thì đi tiếp từ phần đã có."""
    def part(i: int) -> Path:
        return sd / f"v3_part{i:02d}.md"
    texts = [(sd / p).read_text(encoding="utf-8") for p in st["parts"]]
    while len(texts) < 1 + a.max_turns and not (texts and (st.get("done") or stop_reason(texts))):
        i = len(texts) + 1
        out = part(i)
        print(f"lượt {i}…", flush=True)
        link = ask(first if i == 1 else cont, out, st.get("chat") or None, a)
        if st.get("chat") and chat_id(link) and chat_id(link) != chat_id(st["chat"]):
            raise SystemExit(f"Gemini chuyển sang chat khác ({link}); bỏ {out.name}, chạy lại để viết bù")
        st["chat"] = st.get("chat") or link
        text = tidy(out.read_text(encoding="utf-8").replace("\r\n", "\n"))
        out.write_text(text, encoding="utf-8")
        texts.append(text)
        st["parts"].append(out.name)
        save_json(sd / "state.json", st["_root"])
    why = stop_reason(texts)
    print(f"dừng viết tiếp sau {len(texts)} lượt" + (f": {why}" if why else " (hết số lượt)"))
    st["done"] = True
    return texts


def mark_chapters(a, sd: Path, st: dict, full: str) -> tuple[str, str]:
    """(văn bản có mốc, 'gemini' | 'heuristic')."""
    raw_f = sd / "v3_marked.md"
    if not raw_f.is_file():
        try:
            ask(marking_prompt(a.loai), raw_f, st["chat"], a)
        except SystemExit as e:
            print(f"!! lượt gắn mốc lỗi ({e}); dùng bộ chia cục bộ")
    if raw_f.is_file():
        marked = normalize(tidy(raw_f.read_text(encoding="utf-8").replace("\r\n", "\n")))
        if same_text(full, marked) and valid_headings(marked):
            return marked.strip() + "\n", "gemini"
        print("!! bản gắn mốc của Gemini đổi chữ hoặc sai dạng tiêu đề; dùng bộ chia cục bộ")
    print("!! CẢNH BÁO: tiêu đề chương là 'Phần N' tạm, biên tập viên phải đặt lại tên (3–8 chữ, như câu tìm kiếm)")
    return heuristic_mark(full, a.loai), "heuristic"


def main() -> int:
    from factory.console import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("channel")
    ap.add_argument("slug")
    ap.add_argument("--loai", choices=["dai", "vua"], default="dai")
    ap.add_argument("--cach", help="mã cách triển khai chính (bỏ qua xoay vòng)")
    ap.add_argument("--inputs", type=Path, help="thư mục input (mặc định data/long/<slug>/viet_loi_in)")
    ap.add_argument("--max-turns", type=int, help="số lượt viết tiếp tối đa (mặc định 6; Long vừa 2)")
    ap.add_argument("--write-prose", action="store_true", help="ghi data/long/<slug>/prose.md và chạy prose_to_script.py")
    ap.add_argument("--dry-run", action="store_true", help="chỉ in prompt đã điền")
    ap.add_argument("--model", default="Neon")
    ap.add_argument("--thinking", default="High")
    ap.add_argument("--timeout", type=int, default=1500)
    ap.add_argument("--headless", action="store_true")
    a = ap.parse_args()
    if a.max_turns is None:
        a.max_turns = 6 if a.loai == "dai" else 2
    ch = a.channel.upper()
    sd = STATE / f"{ch}_{a.slug}"
    sf = sd / "state.json"
    root_st = load_json(sf)
    st = root_st.get("v3")
    resume = bool(st and st.get("parts"))
    rot = load_json(ROTATION)
    if resume:
        main_cach, cont_used = st["cach"], st.get("cach_used", [st["cach"]])
        a.loai = st.get("loai", a.loai)
    else:
        main_cach = pick_cach(ch, rot, a.cach)
    rng = random.Random(f"{ch}/{a.slug}/{main_cach}")
    first, cont, used = build_prompt(ch, a.slug, a.loai, main_cach, a.inputs, rng=rng)
    if a.dry_run:
        print(first)
        print(f"\n[cách: {', '.join(used)}; {words(first)} chữ]")
        return 0
    if not resume:
        st = {"chat": "", "parts": [], "cach": main_cach, "cach_used": used, "loai": a.loai}
        rot[ch] = {"last": main_cach, "slug": a.slug, "date": dt.date.today().isoformat()}
        save_json(ROTATION, rot)
    st["_root"] = root_st
    root_st["v3"] = st
    sd.mkdir(parents=True, exist_ok=True)
    save_json(sf, root_st)
    print(f"cách triển khai: {', '.join(st.get('cach_used', [main_cach]))}")
    texts = run_turns(a, ch, sd, st, first, cont)
    full = tidy("\n\n".join(t.strip() for t in texts)) + "\n"
    marked, mode = mark_chapters(a, sd, st, full)
    st["marking"] = mode
    save_json(sf, {k: v for k, v in root_st.items()})
    out = save_inbox(ch, a.slug, marked)
    nch = len([l for l in marked.splitlines() if l.startswith("## ")])
    print(f"đã lưu {out.relative_to(ROOT)} ({words(marked)} chữ, {nch} chương, mốc: {mode})")
    if not a.write_prose:
        return 0
    prose = LONG / a.slug / "prose.md"
    prose.parent.mkdir(parents=True, exist_ok=True)
    if prose.is_file() and not (prose.parent / "prose.prev.md").exists():
        (prose.parent / "prose.prev.md").write_text(prose.read_text(encoding="utf-8"), encoding="utf-8")
    prose.write_text(marked, encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "prose_to_script.py"), str(prose), str(prose.parent / "script.md")],
                       capture_output=True, text=True, encoding="utf-8")
    print((r.stdout + r.stderr).strip()[-1200:])
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
