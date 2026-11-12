"""Deterministic Long text selection; input scenes are already planned."""
from collections import Counter
import hashlib
import re
import unicodedata

EFFECTS = ("depth-parallax-words", "kinetic-center-build", "mask-reveal-up",
           "shimmer-sweep", "focus-blur-resolve", "per-word-crossfade",
           "stagger-from-center", "flip", "rise", "blur", "drop", "pop")
# "marker" tạm bỏ (Lead 12/11): vệt nền trải cả khối .kin, nhìn như gạch ngang chữ -> đổi nghĩa câu.
STYLES = ("solid", "duo", "editorial", "poster", "outline", "gold")


def _seed(topic, chapter, index, value):
    return hashlib.sha256(f"{topic}|{chapter}|{index}|{value}".encode()).digest()


def _negative(text):
    text = unicodedata.normalize("NFC", text).upper()
    # Chỉ dạng đối lập "KHÔNG PHẢI X · Y": câu đơn như "ĐỪNG TIN LỜI ĐỒN" mà gạch thì ngược nghĩa (Lead 12/11).
    if "·" not in text:
        return False
    text = text.split("·")[0]
    return bool(re.search(r"(?<!\w)(?:KH\u00d4NG\s+PH\u1ea2I|CH\u1eb2NG\s+PH\u1ea2I|\u0110\u1eeaNG|SAI)(?!\w)", text))


def _items(scene):
    return scene.get("items", []) if scene.get("type") == "kinetic" else scene.get("kin", []) or []


def apply(topic, chapter, scenes, original, lines, look="classic", enabled=True, counts=None):
    """Mutate planned kinetic/overlay lines. Explicit source fields always win."""
    if not enabled:
        return Counter(), Counter()
    from beatfx import SyncCursor, _per_token
    effects, styles = counts if counts is not None else (Counter(), Counter())
    chfx, chstyles = Counter(), Counter()
    words = sorted((w for line in lines for w in line.get("words", [])), key=lambda w: w["t"])
    previous_fx = previous_style = None
    for i, scene in enumerate(scenes):
        source = original[i] if i < len(original) else {}
        src_items = _items(source)
        cursor = SyncCursor(words, scene.get("t0", 0), scene.get("t1", 0))
        for j, item in enumerate(_items(scene)):
            src = src_items[j] if j < len(src_items) else {}
            if not item.get("text"):
                continue
            manual_fx = "fx" in src
            manual_style = "style" in src or "typestyle" in src
            if not manual_fx:
                wt = None
                if not item.get("sm") and item.get("at", 0) >= .3:
                    wt = cursor.take(item["text"], item.get("at", 0))
                    if wt and wt[0] - scene.get("t0", 0) > 1.2:
                        wt = None
                opts = list(EFFECTS) + (["sync"] if wt else [])
                # beat2 can wrap an exact word without replacing animated spans.
                if item.get("em") and str(item["em"]) not in item["text"].split(" "):
                    opts = [v for v in opts if v in ("pop", "blur", "shimmer-sweep")]
                eligible = [v for v in opts if v != previous_fx]
                # Prefer unused styles within the chapter as well as a balanced film.
                fx = min(eligible, key=lambda v: (effects[v], chfx[v], _seed(topic, chapter, i, f"{j}|{v}")))
                item["fx"] = fx
                item.pop("wt", None); item.pop("t0", None)
                if fx == "sync":
                    item["wt"] = [round(t, 3) for t in _per_token(item["text"], wt)]
                    item["t0"] = scene.get("t0", 0)
                    item["syncExact"] = True
                    tokens = item["text"].split(" ")
                    emphasis = item.get("em")
                    if emphasis:
                        item["emw"] = [k for k, w in enumerate(tokens) if w.casefold().strip(".,!?;:") == str(emphasis).casefold().strip(".,!?;:")]
            if _negative(item["text"]) and item.get("fx") != "strike" and "autoStrike" not in src:
                item["autoStrike"] = True
            fx = item.get("fx", "pop")
            effects[fx] += 1; chfx[fx] += 1; previous_fx = fx
            if not manual_style:
                # Gold only on explicitly dark background or scenes whose engine darkens the background.
                opts = [v for v in STYLES if v != previous_style and (v != "gold" or scene.get("type") == "kinetic")]
                style = min(opts, key=lambda v: (styles[v], chstyles[v], _seed(topic, chapter, i, f"style|{j}|{look}|{v}")))
                item["typestyle"] = style
            style = item.get("typestyle") or item.get("style") or "solid"
            if isinstance(style, str):
                styles[style] += 1; chstyles[style] += 1; previous_style = style
        if scene.get("type") == "slam" and scene.get("text"):
            if "fx" not in source:
                candidates = [v for v in EFFECTS[:8] if v != previous_fx]
                scene["fx"] = min(candidates, key=lambda v: (effects[v], chfx[v], _seed(topic, chapter, i, v)))
                if _negative(scene["text"]):
                    scene["autoStrike"] = True
            fx = scene.get("fx", "punch")
            effects[fx] += 1; chfx[fx] += 1; previous_fx = fx
            # Existing slam effects are not intercepted; only new effects can apply a style.
            if scene.get("fx") in EFFECTS[:8] and "style" not in source and "typestyle" not in source:
                options = [v for v in STYLES if v != previous_style]
                scene["typestyle"] = min(options, key=lambda v: (styles[v], chstyles[v], _seed(topic, chapter, i, "slam|" + look + "|" + v)))
            style = scene.get("typestyle")
            if isinstance(style, str):
                styles[style] += 1; chstyles[style] += 1; previous_style = style
    return chfx, chstyles
