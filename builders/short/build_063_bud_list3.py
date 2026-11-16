"""Build 6 BUD list3 shorts (ticket 063, khuôn hỏi-đếm-3 / kinh nói-dân gian thêm). Lead viết lại 15/11.

Writes only under output/cl_staging/bud and output/cl_staging/grok.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import hf_batch_render as HBR  # noqa: E402
from shortbuild import validate  # noqa: E402
import hyperframes_bridge as HB  # noqa: E402

BUD = ROOT / "output/cl_staging/bud"
OUT = BUD / "out"
COMPS = BUD / "compositions"
PLAN = BUD / "plan_063.json"

SN3 = "https://suttacentral.net/sn3.13/en/sujato"
SN7 = "https://suttacentral.net/sn7.10/en/sujato"
DB_SOURCE = ("Chú Đại Bi (Nīlakaṇṭha Dhāraṇī), bản Già Phạm Đạt Ma (Bhagavaddharma, T.1060). "
             "Nghĩa theo bản tiếng Phạn phục hồi của Lokesh Chandra (1988), tóm tại "
             "https://en.wikipedia.org/wiki/N%C4%ABlaka%E1%B9%87%E1%B9%ADha_Dh%C4%81ra%E1%B9%87%C4%AB — "
             "'namo ratna-trayāya' (Chandra: 'Homage to the Three Jewels').")

IMG = "output/cl_staging/long/research/ai_media/bud_list3/"
MN123 = "https://suttacentral.net/mn123/en/sujato"
TTS = {"engine": "v3", "voice": "Thanh Bình", "style": "tu_nhien", "temperature": 0.9, "text_mode": "production", "tempo": 1.05}
CREDIT = [{"kind": "AI illustration", "credit": "Minh họa AI, không phải tư liệu lịch sử."}]


def item(i, day, slot, khuon, title, anchor, script, imgs, caps, insight, source, novelty):
    return {"id": f"budl_{i}", "day": day, "slot": slot, "lane": "tuong", "style": "ai_cards", "series": "bud",
            "batch_id": "bud_list3_w48", "test_cell": "bud_list3_w48", "img_kind": "ai",
            "format_subtag": f"list3_{khuon}", "hook_type": "cau_hoi_dem_3" if khuon == "A" else "kinh_noi_dan_gian_them",
            "narrative_structure": "hoi_dem_3_insight" if khuon == "A" else "quen_doi_chieu_kinh",
            "title": title, "anchor": anchor, "script": script, "scene_img": [IMG + x + ".png" for x in imgs],
            "visual_caption": caps, "insight": insight, "source": source, "media_credits": CREDIT,
            "media": {"1": {"kind": "local", "path": IMG + imgs[0] + ".png"}}, "novelty_ok": novelty, "tts": dict(TTS)}


ITEMS = [
 item(1, "2026-11-26", "06:00", "A", "Vừa chào đời, Đức Phật làm 3 việc gì?", "bảy bước",
      ["Vừa chào đời, Ngài đã **đứng dậy**.",
       "Kinh Trung Bộ kể ba việc liền nhau.",
       "Một, Ngài **đứng vững** trên mặt đất.",
       "Hai, quay về phương bắc, bước **bảy bước**, có lọng trắng che trên đầu.",
       "Ba, nhìn khắp các phương, và nói: đây là **lần sinh cuối cùng**.",
       "Kinh ghi lời ấy: ta là bậc **đứng đầu thế gian**.",
       "Ngài A Nan kể lại chuyện này, như một điều **hiếm có**, chưa từng có.",
       "Bạn từng nghe chuyện này kể khác đi chưa?"],
      ["l1_dung", "l1_nhin", "l1_dung", "l1_bay_buoc", "l1_nhin", "l1_dung", "l1_bay_buoc", "l1_nhin"],
      ["Vừa chào đời", "Trung Bộ 123", "Một · đứng vững", "Hai · bảy bước", "Ba · lời tuyên bố", "Lời trong kinh", "Ngài A Nan kể", "Câu hỏi"],
      "Theo Trung Bộ 123, vừa sinh ra Bồ Tát đứng vững, bước bảy bước về phương bắc dưới lọng trắng, nhìn khắp các phương và nói đây là lần sinh cuối.",
      f"Trung Bộ 123 Acchariyaabbhutasutta (mn123:20.2), bản Bhikkhu Sujato (CC0): {MN123}",
      "Khuôn list3 PO duyệt 14/11; khác b11_b (tượng chỉ tay) — đây là ba hành động theo MN 123."),
 item(2, "2026-11-26", "19:30", "B", "Bốn cảnh già, bệnh, chết, tu sĩ: kinh kể về vị Phật nào?", "Tỳ Bà Thi",
      ["Bốn cảnh này, ai cũng tưởng là của **Thái tử Tất Đạt Đa**.",
       "Một người già. Một người bệnh. Một người chết. Một vị tu sĩ.",
       "Nhưng trong kinh **Trường Bộ** số mười bốn,",
       "bốn cảnh ấy được kể về **Bồ Tát Tỳ Bà Thi**, một vị Phật thời rất xa xưa.",
       "Người đánh xe nói: gọi là già, vì **không còn sống được bao lâu**.",
       "Chuyện Thái tử Tất Đạt Đa là cách kể của **truyền thống** về sau."],
      ["l2_xe", "l2_gia", "l2_tu_si", "l2_xe", "l2_gia", "l2_tu_si"],
      ["Bốn cảnh quen", "Già · bệnh · chết · tu sĩ", "Trường Bộ 14", "Bồ Tát Tỳ Bà Thi", "Lời người đánh xe", "Kinh và truyền thống"],
      "Trường Bộ 14 kể bốn cảnh già, bệnh, chết, tu sĩ về Bồ Tát Tỳ Bà Thi; chuyện Thái tử Tất Đạt Đa gặp bốn cảnh là cách kể của truyền thống về sau.",
      "Trường Bộ 14 Mahāpadānasutta (dn14:2.1–2.14), bản Bhikkhu Sujato (CC0): https://suttacentral.net/dn14/en/sujato",
      "Khuôn B 'kinh nói, dân gian thêm' (list3)."),
 item(3, "2026-11-27", "06:00", "A", "Người tu tâm từ được 3 điều gì khi ngủ?", "tâm từ",
      ["Có một cách để **ngủ ngon** mà kinh đã ghi.",
       "Kinh Tăng Chi kể lợi ích của người tu **tâm từ**.",
       "Một, **ngủ an**.",
       "Hai, **thức dậy** an vui.",
       "Ba, **không gặp ác mộng**.",
       "Đó mới là ba điều đầu, trong **mười một** điều kinh nói.",
       "Kinh còn kể: được người thương, được **chư thiên che chở**.",
       "Mười một điều ấy đến với người tu tâm từ, giữ gìn và thực hành **thường xuyên**.",
       "Tối nay, trước khi ngủ, thử nghĩ tốt về một người?"],
      ["l3_ngu", "l3_mong", "l3_ngu", "l3_thuc", "l3_mong", "l3_thuc", "l3_mong", "l3_thuc", "l3_ngu"],
      ["Ngủ ngon", "Tăng Chi 11.15", "Một · ngủ an", "Hai · thức vui", "Ba · không ác mộng", "Mười một lợi ích", "Còn nữa", "Tu tập thường xuyên", "Câu hỏi"],
      "Theo Tăng Chi 11.15, người tu tâm từ ngủ an, thức dậy an vui và không gặp ác mộng; đó là ba trong mười một lợi ích.",
      "Tăng Chi 11.15 Mettāsutta (an11.15:2.2), bản Bhikkhu Sujato (CC0): https://suttacentral.net/an11.15/en/sujato",
      "Khuôn list3; khác các bài tâm từ dạng niệm (tn1)."),
 item(4, "2026-11-27", "19:30", "A", "Đức Phật dặn 4 nơi nào nên đến chiêm bái?", "bốn nơi",
      ["Gần lúc **nhập Niết Bàn**, Đức Phật dặn bốn nơi.",
       "Kinh Trường Bộ số mười sáu ghi lại.",
       "Ngài A Nan lo: sau này, các thầy biết đến đâu để được **gặp Ngài**?",
       "Một, nơi Như Lai **đản sinh**. Hai, nơi Như Lai **giác ngộ**.",
       "Ba, nơi **chuyển bánh xe Pháp**. Bốn, nơi **nhập Niết Bàn**.",
       "Kinh gọi đó là những nơi khơi dậy **niềm cảm hứng**.",
       "Người sau gọi là **Lâm Tỳ Ni**, Bồ Đề Đạo Tràng,",
       "Lộc Uyển, và **Câu Thi Na**.",
       "Bạn đã đến được nơi nào trong bốn nơi ấy?"],
      ["l4_niet_ban", "l4_sinh", "l4_niet_ban", "l4_giac_ngo", "l4_loc_uyen", "l4_sinh", "l4_giac_ngo", "l4_niet_ban", "l4_loc_uyen"],
      ["Bốn nơi", "Trường Bộ 16", "Nỗi lo của A Nan", "Đản sinh · Giác ngộ", "Chuyển pháp · Niết Bàn", "Nơi khơi cảm hứng", "Tên đời sau", "Tên đời sau", "Câu hỏi"],
      "Trường Bộ 16 nêu bốn nơi người có lòng tin nên đến: nơi đản sinh, nơi giác ngộ, nơi chuyển bánh xe Pháp và nơi nhập Niết Bàn.",
      "Trường Bộ 16 Mahāparinibbānasutta (dn16:5.8.1–5.8.7), bản Bhikkhu Sujato (CC0): https://suttacentral.net/dn16/en/sujato",
      "Khuôn list3; không trùng bài chiêm bái cũ."),
 item(5, "2026-11-28", "12:30", "A", "Người trúng tên độc đòi biết 3 điều gì trước khi rút tên?", "mũi tên độc",
      ["Một người trúng **tên tẩm độc**.",
       "Thầy thuốc đến. Nhưng anh ta nói: **khoan đã**.",
       "Một, người bắn tôi thuộc **tầng lớp** nào?",
       "Hai, người đó **tên gì, họ gì**?",
       "Ba, người ấy **cao, thấp**, hay vừa?",
       "Đức Phật nói: người ấy sẽ **chết** trước khi biết hết.",
       "Ngài kể ví dụ này cho một vị tỳ kheo, người đòi Ngài trả lời mọi câu hỏi về **thế giới**, rồi mới chịu tu.",
       "Có câu hỏi nào bạn đang đợi trả lời, mới chịu bắt đầu?"],
      ["l5_ten", "l5_thay_thuoc", "l5_cung", "l5_ten", "l5_cung", "l5_thay_thuoc", "l5_cung", "l5_ten"],
      ["Tên tẩm độc", "Khoan đã", "Một · tầng lớp", "Hai · tên họ", "Ba · cao hay thấp", "Trung Bộ 63", "Vì sao Ngài kể", "Câu hỏi"],
      "Trong Trung Bộ 63, Đức Phật ví người đòi biết hết mọi điều mới chịu tu như kẻ trúng tên độc đòi biết về người bắn: chưa biết đủ đã chết.",
      "Trung Bộ 63 Cūḷamālukyasutta (mn63:5.9–5.13), bản Bhikkhu Sujato (CC0): https://suttacentral.net/mn63/en/sujato",
      "Khuôn list3; ví dụ mũi tên MN 63 chưa làm Short."),
 item(6, "2026-11-28", "19:30", "B", "Chín rồng phun nước tắm Phật: kinh kể mấy dòng nước?", "hai dòng nước",
      ["Tranh Phật Đản quen thuộc: **chín con rồng** phun nước.",
       "Nhưng kinh Pāli lại kể khác hẳn.",
       "Ngài A Nan kể những điều **hiếm có** khi Bồ Tát ra đời.",
       "Trung Bộ số một trăm hai mươi ba ghi, khi Bồ Tát ra đời,",
       "có **hai dòng nước** từ trời xuống, một dòng **mát**, một dòng **ấm**,",
       "tắm cho Bồ Tát và cả **mẹ Ngài**.",
       "Chín rồng là hình ảnh của **truyền thống Bắc truyền**, đoạn kinh này không nhắc."],
      ["l6_rong", "l6_hai_dong", "l6_me", "l6_hai_dong", "l6_me", "l6_hai_dong", "l6_rong"],
      ["Chín con rồng", "Kinh kể khác", "Điều hiếm có", "Trung Bộ 123", "Hai dòng nước", "Bồ Tát và mẹ", "Kinh và truyền thống"],
      "Trung Bộ 123 kể hai dòng nước, một mát một ấm, từ trời tắm cho Bồ Tát và mẹ; chín rồng là hình ảnh của truyền thống Bắc truyền.",
      f"Trung Bộ 123 Acchariyaabbhutasutta (mn123:19.2), bản Bhikkhu Sujato (CC0): {MN123}",
      "Khuôn B list3."),
]


def b64_image(path: Path) -> str:
    import base64
    from io import BytesIO
    im = Image.open(path).convert("RGB")
    im.thumbnail((1080, 1500), Image.Resampling.LANCZOS)
    bio = BytesIO()
    im.save(bio, "WEBP", quality=84)
    return "data:image/webp;base64," + base64.b64encode(bio.getvalue()).decode("ascii")


def composition(it: dict) -> str:
    """Mỗi câu một ảnh (scene_img), chữ và ảnh đổi đúng giây giọng đọc (scene_times)."""
    imgs = [b64_image(ROOT / p) for p in it["scene_img"]]
    T = list(it.get("scene_times") or [round(i * 3.6 + .5, 3) for i in range(len(it["script"]))] + [it.get("dur", 28) - .3])
    title = it["title"].replace("&", "&amp;")
    pics, scenes = [], []
    for i, (line, cap, im) in enumerate(zip(it["script"], it["visual_caption"], imgs), 1):
        line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line).replace("&", "&amp;")
        tag = '<div class="pdtag">PHỎNG DỰNG</div>' if i in set(it.get("pd_scenes") or []) else ""   # PO 16/11: cảnh phỏng dựng có nhãn
        pics.append(f'<div class="pic" id="p{i}"><img src="{im}">{tag}</div>')
        scenes.append(f'<section class="scene" id="s{i}"><div class="label">{cap}</div><p>{line}</p></section>')
    n = len(it["script"])
    js = "".join(
        f'tl.fromTo("#p{i}",{{opacity:0,scale:1.08}},{{opacity:1,scale:1.0,duration:.5}},{T[i-1]});'
        f'tl.to("#p{i}",{{scale:1.04,duration:{max(.5, T[i]-T[i-1]):.2f},ease:"none"}},{T[i-1]+.5});'
        f'tl.fromTo("#s{i}",{{opacity:0,y:28}},{{opacity:1,y:0,duration:.4}},{T[i-1]});'
        + (f'tl.to(["#s{i}","#p{i}"],{{opacity:0,duration:.25}},{T[i]-.25});' if i < n else "")
        for i in range(1, n + 1))
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=1080,height=1920">
<title>{it['id']}</title><style>
@font-face{{font-family:BV;src:url("../../../../hyperframes_short/studio/fonts/BeVietnamPro-ExtraBold.woff2")}}*{{box-sizing:border-box}}body{{margin:0;background:#110d08;color:#fff8ec;font-family:BV,"Arial",sans-serif}}
.frame{{width:1080px;height:1920px;position:relative;overflow:hidden;background:#17100b}}
.pic{{position:absolute;inset:0;opacity:0}}.pic img{{width:100%;height:100%;object-fit:cover}}
.pdtag{{position:absolute;top:330px;right:56px;background:rgba(16,11,8,.72);color:#f4cf6b;font-size:24px;letter-spacing:.16em;padding:8px 16px;border:1px solid #f4cf6b;border-radius:8px}}
.shade{{position:absolute;inset:0;background:linear-gradient(rgba(16,11,8,.88) 0 14%,transparent 30%,transparent 52%,rgba(16,11,8,.92) 74%)}}
header{{position:absolute;top:80px;left:64px;right:64px;text-align:center}}.chip{{font-size:28px;letter-spacing:.14em;color:#f4cf6b}}h1{{font-size:56px;line-height:1.18;margin:14px 0 0}}
.scene{{position:absolute;left:70px;right:70px;top:1330px;text-align:center;opacity:0}}.label{{display:inline-block;background:#f4cf6b;color:#21170d;font-size:32px;padding:8px 22px;border-radius:12px;margin-bottom:22px}}
.scene p{{font-size:52px;line-height:1.3;margin:0;text-shadow:0 3px 14px rgba(0,0,0,.8)}}.scene b{{color:#f4cf6b}}
footer{{position:absolute;bottom:70px;left:70px;right:70px;text-align:center;color:#e5c991;font-size:24px;opacity:.85}}
</style><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script></head><body><main class="frame" data-composition-id="main" data-start="0" data-duration="{it.get('dur',28):.2f}" data-width="1080" data-height="1920">
{''.join(pics)}<div class="shade"></div><header><div class="chip">PHẬT PHÁP · BA ĐIỀU</div><h1>{title}</h1></header>{''.join(scenes)}<footer>{it["source"].split(",")[0].split("(")[0].strip()}</footer></main>
<script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});window.__timelines.main=tl;{js}</script></body></html>'''


def tts_and_pad(it: dict) -> float:
    OUT.mkdir(parents=True, exist_ok=True)
    lines = [re.sub(r"\*\*(.*?)\*\*", r"\1", x) for x in it["script"]]
    txt = OUT / f"{it['id']}.txt"
    raw = OUT / f"{it['id']}.raw.wav"
    raw_json = raw.with_suffix(".json")
    final_wav = OUT / f"{it['id']}.wav"
    final_json = final_wav.with_suffix(".json")
    txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not (raw.is_file() and raw_json.is_file()):
        if not HBR.render_tts(txt, raw, lines, "Thanh Bình", mode="v3turbo", device="cpu"):
            raise RuntimeError(f"TTS failed for {it['id']}")
    data, sr = sf.read(raw, dtype="float32")
    man = json.loads(raw_json.read_text(encoding="utf-8"))
    pieces = [np.zeros((round(.5 * sr),) + data.shape[1:], dtype=np.float32)]
    segs, cursor = [], .5
    for i, seg in enumerate(man["segments"]):
        chunk = data[round(seg["start"] * sr):round(seg["end"] * sr)]
        from hf_voice import tempo as adjust_tempo
        chunk = adjust_tempo(chunk, sr, float(it["tts"]["tempo"]))
        start = cursor
        pieces.append(chunk)
        cursor += len(chunk) / sr
        segs.append({"start": round(start, 3), "end": round(cursor, 3), "text": lines[i]})
        if i + 1 < len(man["segments"]):
            gap = .6 if i == 0 else .8
            pieces.append(np.zeros((round(gap * sr),) + data.shape[1:], dtype=np.float32))
            cursor += gap
    hold = 3.3
    pieces.append(np.zeros((round(hold * sr),) + data.shape[1:], dtype=np.float32))
    cursor += hold
    sf.write(final_wav, np.concatenate(pieces), sr)
    final_json.write_text(json.dumps({**man, "duration_s": round(cursor, 3), "segments": segs}, ensure_ascii=False), encoding="utf-8")
    # Match hf_batch_render's cache stamp so Lead's render reuses this exact TTS.
    digest = hashlib.sha1(("\n".join(it["script"]) + json.dumps(it["tts"], sort_keys=True)).encode("utf-8")).hexdigest()
    (OUT / f"{it['id']}.script.sha1").write_text(digest + "\n", encoding="utf-8")
    return round(cursor, 2)


def main() -> None:
    plan = []
    for it in ITEMS:
        it["dur"] = 28.0
        validate([it], composition(it))
        it["dur"] = tts_and_pad(it)
        seg = json.loads((OUT / f"{it['id']}.json").read_text(encoding="utf-8"))["segments"]
        it["scene_times"] = [s["start"] for s in seg] + [round(it["dur"] - .3, 3)]
        assert len(it["scene_times"]) == len(it["script"]) + 1, f"{it['id']}: scene_times lệch số câu"
        html = composition(it)
        validate([it], html)
        COMPS.mkdir(parents=True, exist_ok=True)
        (COMPS / f"{it['id']}.html").write_text(html, encoding="utf-8")
        plan.append(it)
        print(f"[{it['id']}] {it['day']} {it['slot']} UTC | {it['dur']}s | M7: ĐẠT")
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
