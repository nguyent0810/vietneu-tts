"""Kiểm thử phụ đề chunk của Long (010b): gom 3–6 chữ theo nhịp đọc, không cắt từ ghép, Short giữ nguyên."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_JS = ROOT / "hyperframes_short" / "compositions" / "engine.js"
LONGFORM_CSS = ROOT / "hyperframes_short" / "compositions" / "longform.css"
WIDE_CSS = ROOT / "hyperframes_short" / "compositions" / "wide.css"


def _run_node_split(sentence: str, line_end: float = 10.0) -> list[list[str]]:
    words = sentence.split()
    script = f"""
const fs = require("fs");
const vm = require("vm");
const code = fs.readFileSync({json.dumps(str(ENGINE_JS))}, "utf8");
const ctx = {{
  window: {{}},
  document: {{ createElement: () => ({{}}), documentElement: {{ dataset: {{}} }} }}
}};
vm.createContext(ctx);
vm.runInContext(code, ctx);

const words = {json.dumps(words)}.map((w, i) => ({{ w, t: i * 0.4, d: 0.35 }}));
const chunks = ctx.window.HF.splitLongChunks(words, {line_end});
console.log(JSON.stringify(chunks.map(c => c.map(x => x.w))));
"""
    proc = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
    return json.loads(proc.stdout.strip())


def test_long_chunk_no_single_word_and_split_at_punct():
    # Câu 7 trong kịch bản mẫu từng bị lỗi hiện 1 chữ ("ăn,")
    sentence = "Một phần để hưởng dụng, hai phần để làm ăn, phần thứ tư để dành, phòng khi gặp hoạn nạn."
    chunks = _run_node_split(sentence)
    assert len(chunks) == 4
    # Mọi chunk phải có đúng 5 chữ, kết thúc bằng dấu phẩy hoặc chấm
    assert chunks[0] == ["Một", "phần", "để", "hưởng", "dụng,"]
    assert chunks[1] == ["hai", "phần", "để", "làm", "ăn,"]
    assert chunks[2] == ["phần", "thứ", "tư", "để", "dành,"]
    assert chunks[3] == ["phòng", "khi", "gặp", "hoạn", "nạn."]
    assert not any(len(c) == 1 for c in chunks), "không được có chunk 1 chữ mồ côi"


def test_long_chunk_size_within_3_to_6():
    # Kiểm tra nhiều câu có độ dài từ 6 đến 25 từ
    sentences = [
        "Đây là đồng tiền vàng của vua Vima Kadphises, triều Kushan, đúc ở Ấn Độ gần hai nghìn năm trước.",
        "Nhưng Đức Phật không dạy người tại gia chối bỏ tiền bạc. Ngài dạy cách giữ và dùng nó.",
        "Bốn phần ấy, đến hôm nay vẫn là một nguyên tắc tài chính rất vững.",
        "Một phần tư cho đời sống hằng ngày của gia đình.",
        "Một nửa để đồng vốn sinh sôi.",
        "Và một phần tư là quỹ phòng thân.",
        "Phương Đông là cha mẹ. Phương Nam là thầy dạy.",
        "Phương Tây là vợ con. Phương Bắc là bạn bè.",
        "Phương dưới là người làm công. Phương trên là các bậc tu hành.",
    ]
    for s in sentences:
        chunks = _run_node_split(s)
        for c in chunks:
            assert 3 <= len(c) <= 6, f"chunk {c} có độ dài {len(c)} ngoài khoảng [3, 6] trong câu: {s}"


def test_no_cut_across_compound_words():
    # Từ ghép 2 âm tiết không bị tách đôi sang 2 cụm khác nhau
    s = "Một nửa để đồng vốn sinh sôi."
    chunks = _run_node_split(s)
    assert chunks == [["Một", "nửa", "để"], ["đồng", "vốn", "sinh", "sôi."]]

    s2 = "Bốn phần ấy, đến hôm nay vẫn là một nguyên tắc tài chính rất vững."
    chunks2 = _run_node_split(s2)
    # nguyên tắc và tài chính phải nằm cùng chunk
    c_last = chunks2[-1]
    assert "nguyên" in c_last and "tắc" in c_last
    assert "tài" in c_last and "chính" in c_last


def test_proper_nouns_capitalized_not_cut():
    # Tên riêng viết hoa 2 âm tiết liên tiếp (Đức Phật, Ấn Độ...) không bị cắt
    s = "Đức Phật dạy chàng Thi Ca La Việt về sáu phương."
    chunks = _run_node_split(s)
    c0 = chunks[0]
    assert "Đức" in c0 and "Phật" in c0


def test_short_chunk_logic_preserved():
    # Kiểm tra trong engine.js logic của Short giữ nguyên
    src = ENGINE_JS.read_text(encoding="utf-8")
    assert "cur.length >= 4 || k === ws.length - 1" in src
    assert "fromTo(c.box.children[k], { opacity: 0, y: 14, scale: .92 }" in src


def test_css_rules_for_lit_highlight():
    # CSS có rule tô chữ đang đọc (.lit) và hiển thị cả cụm (.cw opacity .52)
    lf = LONGFORM_CSS.read_text(encoding="utf-8")
    wd = WIDE_CSS.read_text(encoding="utf-8")
    assert ".cw.lit" in lf and ".cw.lit" in wd
    assert "opacity: .52" in lf and "opacity: .52" in wd
    assert "--accent" in lf and "--accent" in wd
