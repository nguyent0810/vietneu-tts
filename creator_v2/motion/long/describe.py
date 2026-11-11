"""Mô tả YouTube cho video dài: tóm tắt + mốc chương (tính từ timing thật) + nguồn + ghi công ảnh/nhạc/video.

    python motion/long/describe.py <topic>   -> output/long/<topic>/description.txt
Chỉ ghi công ảnh THỰC SỰ xuất hiện trong cảnh (không phải mọi ảnh đã tải).
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import variety  # noqa: E402


def music_credit(music):
    """Ghi đủ tác giả, nguồn và từng giấy phép; giữ khuôn MacLeod cũ khi có thể."""
    tracks = {m["file"]: m for m in variety.catalog()["tracks"].values()}
    selected = [tracks[f] for f in music if f in tracks]
    groups = {}
    sources = {"Kevin MacLeod": "incompetech.com", "Scott Buckley": "scottbuckley.com.au",
               "Chris Zabriskie": "chriszabriskie.com"}
    for m in selected:
        author, lic = m["author"], m["license"]
        source = sources.get(author, m.get("source_url", ""))
        url = m.get("license_url") or _lic_url(lic)
        title = m["title"]
        # Hai tựa trong bảng credit cũ dùng chữ thường ở giới từ, khác cách viết trong danh mục.
        if author == "Kevin MacLeod":
            if title == "Despair And Triumph":
                title = "Despair and Triumph"
            elif title == "Heart Of Nowhere":
                title = "Heart of Nowhere"
        groups.setdefault((author, lic, url, source), []).append(title)
    lines = []
    legacy = bool(groups) and len(groups) == 1 and selected[0]["author"] == "Kevin MacLeod"
    for (author, lic, url, source), titles in groups.items():
        names = ", ".join(f'"{title}"' for title in titles)
        if legacy and lic in ("CC BY 3.0", "CC BY 4.0"):
            version = lic.removeprefix("CC BY ")
            lines.extend([f"{names} by {author} ({source})",
                          f"Licensed under Creative Commons: By Attribution {version} License — http://creativecommons.org/licenses/by/{version}/"])
        else:
            lines.append(f"{names} by {author} ({source}), licensed under {lic} ({url})")
    return lines


def _lic_url(lic):
    m = re.match(r"CC BY(-SA)? (\d\.\d)", lic)
    return f"https://creativecommons.org/licenses/{'by-sa' if m.group(1) else 'by'}/{m.group(2)}/" if m else ""


FOOTER = {"MIM": "Mind in the Machine — AI và công nghệ, kể dễ hiểu bằng tiếng Việt.",
          "CK": "Biểu Đồ Biết Nói — tiền bạc, giải thích bằng dữ liệu. Mỗi tuần một câu hỏi tiền bạc thật."}
DATA_CREDIT = {"CK": "📊 DỮ LIỆU BIỂU ĐỒ: VN-Index — HOSE; vàng miếng — SJC (sjc.com.vn); truy xuất qua Vnstock. Bitcoin — CoinGecko."}


def mim_lines(spec, meta, chapters, used, vids, music, od):
    """Kênh MIM / CK: nguồn gốc (không phải Wikipedia), ảnh CC BY ghi đủ tác giả + giấy phép + link trang Commons, ghi tên
    người quay clip; kênh CK thêm nguồn dữ liệu biểu đồ (giấy phép Vnstock yêu cầu trích dẫn công cụ)."""
    ch = spec.get("channel", "MIM")
    L = [meta.get("summary", ""), "", *meta.get("more", []), "", "⏱ CHƯƠNG", *chapters, "",
         "📚 NGUỒN (tài liệu gốc, bài báo, trang chính thức)", SRC_SLOT, "",
         *([meta.get("data_credit") or DATA_CREDIT[ch], ""] if ch in DATA_CREDIT else []),   # spec youtube.data_credit: ghi đè theo video
         "Lời dẫn là bản viết mới dựa trên các nguồn trên; câu có nhãn TRÍCH DỊCH là bản dịch tiếng Việt của nguyên văn.",
         "Hình ảnh/video có nhãn MINH HỌA hoặc MÔ PHỎNG chỉ để minh họa, không phải tư liệu gốc của sự kiện."]
    if used:
        L += ["", "🖼 ẢNH (Wikimedia Commons)"]
    pd = 0
    for k in sorted(used):
        f = spec["imgs"][k]
        if str(f).startswith("EXT:ai:"):   # 29/10: ảnh AI (Grok Bot) không ghi công, không đếm vào "phạm vi công cộng"
            continue
        m = json.loads((od / "img" / f"{k}.json").read_text(encoding="utf-8"))
        if m["license"].lower().startswith(("public", "pd", "cc0", "no restr")):
            pd += 1
            continue
        by = re.sub(r"\s*\d\d:\d\d, .*UTC\)", "", m["artist"].split("\n")[0]).strip() or "không rõ tác giả"
        by = re.sub(r"^(.+?)\1$", r"\1", by).replace("Unknown author", "không rõ tác giả")   # Commons hay lặp "Unknown author"
        name = re.sub(r"\s*\(\d{6,}\)|\.(jpe?g|png|tif)$", "", f[5:], flags=re.I)[:80].strip()
        page = quote(f.replace(" ", "_"), safe=":()',")
        L.append(f"• {name} — {by[:40].strip()} — {m['license']} {_lic_url(m['license'])} — "
                 f"https://commons.wikimedia.org/wiki/{page}")
    if pd:
        L.append(f"• Và {pd} ảnh thuộc phạm vi công cộng (Public domain / CC0).")
    idx_p = od / "broll" / "index.json"
    idx = json.loads(idx_p.read_text(encoding="utf-8")) if idx_p.exists() else {}
    users = sorted({idx[v]["user"] for v in vids if v in idx})
    if vids:   # 23/10/2026: chỉ ghi dòng Pexels khi video thật sự có clip Pexels
        L += ["", "🎬 VIDEO: Pexels (pexels.com), giấy phép Pexels" + (" — quay bởi " + ", ".join(users) if users else "")]
    if music:
        L += ["", "🎵 NHẠC NỀN"]
    L += music_credit(music)
    L += ["", FOOTER.get(ch, ""), "", " ".join("#" + x for x in meta.get("hashtags", []))]
    return sources_for_description(L, meta.get("sources", []))


SRC_SLOT = object()
DESC_CAP = 5000   # YouTube: mô tả tối đa 5.000 byte; chỉ rút nguồn khi thực sự vượt ngưỡng


def fit_sources(src: list[str], budget: int) -> list[str]:
    """Danh sách nguồn vừa ngân sách ký tự của mô tả (D1 07/10/2026: 32 nguồn = 5.079 ký tự -> mô tả 8.199 > 5.000, upload
    bị chặn). Thứ tự: đủ nguyên văn -> bỏ tên bài ("Báo dd/mm — tên bài: URL" -> "Báo dd/mm: URL") -> giữ các nguồn đầu (spec
    xếp theo thứ tự xuất hiện) + một dòng nói phần còn lại ghi trên màn hình ở từng cảnh."""
    size = lambda xs: len(("\n".join(xs) + "\n").encode("utf-8"))
    if size(src) <= budget:
        return list(src)
    short = [re.sub(r"^(.+?) — .+?: (https?://\S+)$", r"\1: \2", x) for x in src]
    if size(short) <= budget:
        return short
    out = []
    for k, x in enumerate(short):
        tail = f"…và {len(short) - k - 1} nguồn khác: tên báo và ngày đăng ghi trên màn hình ở từng cảnh."
        if size(out + [x, tail]) > budget:
            return out + [f"…và {len(short) - k} nguồn khác: tên báo và ngày đăng ghi trên màn hình ở từng cảnh."]
        out.append(x)
    return out


def sources_for_description(lines: list, src: list[str], limit: int = DESC_CAP) -> list:
    """Chỉ rút nguồn khi *toàn bộ* mô tả vượt 5.000 byte.

    Nhờ vậy mọi nguồn (đặc biệt nguồn được nêu thẳng trong lời đọc) giữ nguyên
    trong mô tả bình thường; fit_sources chỉ là phương án khi YouTube sẽ từ chối.
    """
    i = lines.index(SRC_SLOT)
    full = lines[:i] + list(src) + lines[i + 1:]
    if len(("\n".join(full).strip() + "\n").encode("utf-8")) <= limit:
        return full
    fixed = lines[:i] + lines[i + 1:]
    budget = limit - len(("\n".join(fixed).strip() + "\n").encode("utf-8"))
    return lines[:i] + fit_sources(src, max(0, budget)) + lines[i + 1:]


LIMIT = 4900   # YouTube cắt mô tả ở 5.000 byte; tiếng Việt có dấu tốn 2–3 byte mỗi ký tự


def broll_lines(od, vids) -> list[str]:
    """Dòng ghi nguồn b-roll theo sidecar <vid>.json: clip AI (Grok Bot/Flow, kho chung) không phải Pexels.
    07/11/2026: Hòa Thân chỉ dùng clip AI mà mô tả vẫn ghi "Pexels"."""
    ai = pex = 0
    for v in vids:
        sc = od / "broll" / f"{v}.json"
        meta = json.loads(sc.read_text(encoding="utf-8")) if sc.exists() else {}
        if meta.get("ai_generated"):
            ai += 1
        else:
            pex += 1
    out = []
    if pex:
        out.append("🎬 VIDEO B-ROLL: Pexels (pexels.com) — giấy phép Pexels, dùng tự do.")
    if ai:
        out.append("🎬 Một số clip và hình bối cảnh là minh họa tạo bằng AI, không phải tư liệu gốc.")
    return out


def main(topic, shrink=0):
    sd, od = ROOT / "data" / "long" / topic, ROOT / "output" / "long" / topic
    spec = json.loads((sd / "spec.json").read_text(encoding="utf-8"))
    meta = dict(spec.get("youtube", {}))
    if shrink:   # mô tả quá dài (video nhiều ảnh): bỏ tên ảnh, ghi tác giả đầy đủ + số ảnh theo từng giấy phép (CC cần tác giả và giấy phép)
        meta["credit_by_len"] = max(16, 44 - 8 * shrink)
    used, music, chapters, t, vids = set(), [], [], 0.0, set()
    mim = spec.get("channel") in FOOTER          # kênh MIM / CK: mô tả kiểu "nguồn gốc"
    for c in spec["chapters"]:
        ch = json.loads((sd / f"{c}.json").read_text(encoding="utf-8"))
        for s in ch["scenes"]:
            for k in (s.get("img"), s.get("bg"), (s.get("a") or {}).get("img"), (s.get("b") or {}).get("img"), *[q.get("img") for q in s.get("pins") or []]):
                if k:
                    used.add(k)
            if s.get("vid"):
                vids.add(str(s["vid"]))
        bg = ch.get("bgm") or []
        picks = variety._picks(topic)   # bgm chọn theo mood: file nằm trong bgm_picks.json
        for b in [q.get("file") or picks.get(f"{c}.{k}") for k, q in enumerate([bg] if isinstance(bg, dict) else bg)]:
            if b and b not in music:
                music.append(b)
        title = ch["hud"]["t"].title() if c != "ch00" else meta.get("ch00_title", "Mở đầu")
        if mim:                                      # tiêu đề chương viết tay (.title() làm hỏng chữ hoa kiểu "AI")
            title = meta.get("chapter_titles", {}).get(c, title)
        elif c == spec["chapters"][-1]:
            title = "Kết: " + title
        chapters.append(f"{int(t // 60):02d}:{int(t % 60):02d} {title}")
        t += json.loads((od / c / "timing.json").read_text(encoding="utf-8"))["duration"]
    lines = [meta.get("summary", ""), "", *meta.get("more", []), "", "⏱ CHƯƠNG", *chapters, "", "📚 NGUỒN THAM KHẢO (Wikipedia tiếng Anh và các nguồn được trích trong đó)",
             SRC_SLOT, "và các bài Wikipedia liên quan.", "",
             "Lời dẫn là bản viết mới dựa trên tư liệu công khai; những câu có nhãn DIỄN Ý là diễn đạt lại, không phải nguyên văn.",
             "Hình ảnh/video có nhãn MINH HỌA chỉ mang tính minh họa bối cảnh.", "", "🖼 ẢNH (Wikimedia Commons và các kho tư liệu mở)"]
    pd, bylic, pdsrc = 0, {}, set()
    INST = {"wellcome": "Wellcome Collection", "artic": "Art Institute of Chicago"}
    for k in sorted(used):
        f = spec["imgs"][k]
        if str(f).startswith("EXT:ai:"):   # 29/10: ảnh AI không ghi công, không đếm vào "phạm vi công cộng"
            continue
        mp = od / "img" / f"{k}.json"
        m = json.loads(mp.read_text(encoding="utf-8"))
        if m["license"].lower().startswith(("public", "pd", "cc0", "no restr")):
            pd += 1
            if m.get("source", "").split(":")[0] in INST:   # PD từ kho bảo tàng: vẫn ghi tên kho (lịch sự, không bắt buộc)
                pdsrc.add(INST[m["source"].split(":")[0]])
            continue
        by = re.sub(r"\s*\d\d:\d\d, .*UTC\)", "", m["artist"].split("\n")[0]).strip() or "không rõ tác giả"
        src = {"wellcome": " · Wellcome Collection", "artic": " · Art Institute of Chicago"}.get(m.get("source", "").split(":")[0], "")
        if m.get("source", "").startswith("europeana:"):
            src = " · " + m["source"].split(":", 1)[1]
        if m.get("source") == "sentinel2":                        # Copernicus: ghi đúng câu bắt buộc
            bylic.setdefault("Copernicus Sentinel data", []).append(m["artist"])
            continue
        name = re.sub(r"\s*\(\d{6,}\)|\.(jpe?g|png|tif)$|, Sicily, Italy| - panoramio", "", m.get("title") or f[5:], flags=re.I)[:meta.get("credit_name_len", 48)]
        by = re.sub(r"^The original uploader was |No machine-readable author provided\. ", "", by)
        bylic.setdefault(m["license"], []).append(by[:meta["credit_by_len"]].strip() + src if shrink else f"{name.strip()} ({by[:meta.get('credit_by_len', 40)].strip()}{src})")
    if not any(str(spec["imgs"][k]).startswith("EXT:") for k in used):   # chỉ Commons -> giữ tiêu đề cũ
        lines = [x.replace("🖼 ẢNH (Wikimedia Commons và các kho tư liệu mở)", "🖼 ẢNH (Wikimedia Commons)") if isinstance(x, str) else x for x in lines]   # SRC_SLOT là object, không phải chuỗi
    if shrink:   # gộp tác giả trùng: "Tên (3 ảnh)"
        bylic = {lic: [a + (f" ({v.count(a)} ảnh)" if v.count(a) > 1 else "") for a in dict.fromkeys(v)] for lic, v in bylic.items()}
    lines += [f"• {lic}: " + "; ".join(v) for lic, v in sorted(bylic.items())]   # gom theo giấy phép: đủ tác giả + giấy phép, ít byte hơn
    lines += [f"• Và {pd} ảnh tư liệu thuộc phạm vi công cộng (Public domain / CC0)" + (f", gồm ảnh từ {', '.join(sorted(pdsrc))}." if pdsrc else "."), "",
              *broll_lines(od, vids)]
    if music:
        lines += ["", "🎵 NHẠC NỀN"]
    lines += music_credit(music)
    catalog_files = {m["file"] for m in variety.catalog()["tracks"].values()}
    for b in music:   # bản thu tự do từ Commons: ghi tên file + giấy phép (json cạnh file nhạc)
        mj = od / "bgm" / (Path(b).stem + ".json")
        if b not in catalog_files and mj.exists():
            m = json.loads(mj.read_text(encoding="utf-8"))
            name = re.sub(r"\.(flac|ogg|oga|wav|mp3)$", "", m["file"][5:], flags=re.I)
            lines.append(f"Mascagni — Intermezzo (Cavalleria rusticana) · {m.get('short', name[:40])} — Wikimedia Commons — {m['license']}")
    lines += ["", " ".join("#" + x for x in meta.get("hashtags", []))]
    if mim:
        lines = mim_lines(spec, meta, chapters, used, vids, music, od)
    else:
        lines = sources_for_description(lines, meta.get("sources", []), LIMIT)
    text = "\n".join(lines).strip() + "\n"
    if not mim and len(text.encode("utf-8")) > LIMIT and shrink < 8:
        return main(topic, shrink + 1)
    (od / "description.txt").write_text(text, encoding="utf-8")
    print(text)
    n = len(text.encode("utf-8"))
    print(f"[{n} byte" + (", ghi công rút gọn theo tác giả" if shrink else "") + ("" if n <= LIMIT else " — VẪN QUÁ 5.000 BYTE, phải bớt tay") + "]")


if __name__ == "__main__":
    import pathlib, sys  # noqa: E401
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
    from factory.console import utf8_console  # noqa: E402
    utf8_console()  # console Windows cp1252 không in được tiếng Việt (retro 2 mục 7)
    main(sys.argv[1])
