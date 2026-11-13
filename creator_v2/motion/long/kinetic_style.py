"""Deterministic Long text selection; input scenes are already planned."""
from collections import Counter
import hashlib
import re
import unicodedata

EFFECTS = ("depth-parallax-words", "kinetic-center-build", "mask-reveal-up",
           "shimmer-sweep", "focus-blur-resolve", "per-word-crossfade",
           "stagger-from-center", "flip", "rise", "blur", "drop", "pop", "marker", "soft-fade", "soft-rise", "soft-zoom", "soft-drift", "soft-blur")
QUOTE_EFFECTS = ("soft-fade", "blur", "shimmer-sweep", "per-word-crossfade", "mask-reveal-up",
                 "soft-rise", "soft-zoom", "soft-drift", "soft-blur")
EM_EFFECTS = ("pop", "blur", "shimmer-sweep", "marker", "soft-fade",
              "soft-rise", "soft-zoom", "soft-drift", "soft-blur")
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


def _auto_plan(topic, chapter, scenes, original, words, effects):
    """Assign automatic text effects with per-effect capacity, using augmenting paths."""
    from beatfx import SyncCursor
    tasks = []
    for i, scene in enumerate(scenes):
        source = original[i] if i < len(original) else {}
        src_items = _items(source)
        cursor = SyncCursor(words, scene.get("t0", 0), scene.get("t1", 0))
        for j, item in enumerate(_items(scene)):
            src = src_items[j] if j < len(src_items) else {}
            if not item.get("text") or "fx" in src:
                continue
            wt = None
            if not item.get("sm") and item.get("at", 0) >= .3:
                wt = cursor.take(item["text"], item.get("at", 0))
                if wt and wt[0] - scene.get("t0", 0) > 1.2:
                    wt = None
            opts = list(EFFECTS) + (["sync"] if wt else [])
            if item.get("em") and str(item["em"]) not in item["text"].split(" "):
                opts = list(EM_EFFECTS)
            tasks.append(((i, j), opts))
        if scene.get("type") in ("slam", "quote") and scene.get("text") and "fx" not in source:
            opts = EFFECTS[:8] if scene["type"] == "slam" else QUOTE_EFFECTS
            tasks.append(((i, -1), list(opts)))
    # A scene counts once: all automatically selected text in it shares an effect.
    grouped = {}
    for key, opts in tasks:
        if key[0] not in grouped:
            grouped[key[0]] = [[], set(opts)]
        grouped[key[0]][0].append(key)
        grouped[key[0]][1].intersection_update(opts)
    if len(grouped) < 5 or any(not opts for _, opts in grouped.values()):
        return {}
    tasks = [((i, -2), sorted(opts)) for i, (_, opts) in grouped.items()]
    cap = len(tasks) // 5
    assigned = {}
    occupants = {effect: [] for effect in EFFECTS + ("sync",)}
    def place(key, options, seen):
        choices = sorted(options, key=lambda fx: (len(occupants[fx]), effects[fx], _seed(topic, chapter, key[0], f"{key[1]}|{fx}")))
        for fx in choices:
            if fx in seen:
                continue
            seen.add(fx)
            if len(occupants[fx]) < cap:
                occupants[fx].append(key); assigned[key] = fx
                return True
            for other in list(occupants[fx]):
                if place(other, dict(tasks)[other], seen):
                    occupants[fx].remove(other); occupants[fx].append(key); assigned[key] = fx
                    return True
        return False
    for key, options in sorted(tasks, key=lambda task: (len(task[1]), task[0])):
        if not place(key, options, set()):
            return {}  # constraints are infeasible; caller uses balanced fallback
    return {key: assigned[(i, -2)] for i, (keys, _) in grouped.items() for key in keys}


def distribution_warning(scenes, original, fx_dist):
    total = sum(1 for scene in scenes if any(item.get("text") for item in _items(scene)) or
                (scene.get("type") in ("slam", "quote") and scene.get("text")))
    if not total or (len(fx_dist) >= 4 and max(fx_dist.values()) * 5 <= total):
        return None
    manual = any((any("fx" in src for src in _items(original[i] if i < len(original) else {})) or
                  (scene.get("type") in ("slam", "quote") and "fx" in (original[i] if i < len(original) else {})))
                 for i, scene in enumerate(scenes))
    if manual:
        return "manual effects contribute to a chapter distribution below four effects or above 20%"
    if total < 5:
        return "chapter has fewer than five text lines; the 20% limit is impossible"
    return "effect eligibility prevents the chapter distribution from meeting the 20% limit"


def apply(topic, chapter, scenes, original, lines, look="classic", enabled=True, counts=None):
    """Mutate planned kinetic/overlay lines. Explicit source fields always win."""
    if not enabled:
        return Counter(), Counter()
    from beatfx import SyncCursor, _per_token
    effects, styles = counts if counts is not None else (Counter(), Counter())
    chfx, chstyles = Counter(), Counter()
    words = sorted((w for line in lines for w in line.get("words", [])), key=lambda w: w["t"])
    plan = _auto_plan(topic, chapter, scenes, original, words, effects)
    auto_fx = Counter()
    previous_fx = previous_style = None
    for i, scene in enumerate(scenes):
        source = original[i] if i < len(original) else {}
        src_items = _items(source)
        scene_fx = set()
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
                    opts = list(EM_EFFECTS)
                eligible = [v for v in opts if v != previous_fx]
                # Prefer unused styles within the chapter as well as a balanced film.
                fx = plan.get((i, j)) or min(eligible, key=lambda v: (auto_fx[v], effects[v], _seed(topic, chapter, i, f"{j}|{v}")))
                item["fx"] = fx
                auto_fx[fx] += 1
                item.pop("wt", None); item.pop("t0", None)
                if fx == "sync":
                    item["wt"] = [round(t, 3) for t in _per_token(item["text"], wt)]
                    item["t0"] = scene.get("t0", 0)
                    item["syncExact"] = True
                    tokens = item["text"].split(" ")
                    emphasis = item.get("em")
                    if emphasis:
                        item["emw"] = [k for k, w in enumerate(tokens) if w.casefold().strip(".,!?;:") == str(emphasis).casefold().strip(".,!?;:")]
            if item.get("fx") == "marker":
                item["markerUnderline"] = True
            if _negative(item["text"]) and item.get("fx") != "strike" and "autoStrike" not in src:
                item["autoStrike"] = True
            fx = item.get("fx", "pop")
            effects[fx] += 1; scene_fx.add(fx); previous_fx = fx
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
                scene["fx"] = plan.get((i, -1)) or min(candidates, key=lambda v: (auto_fx[v], effects[v], _seed(topic, chapter, i, v)))
                auto_fx[scene["fx"]] += 1
                if _negative(scene["text"]):
                    scene["autoStrike"] = True
            fx = scene.get("fx", "punch")
            effects[fx] += 1; scene_fx.add(fx); previous_fx = fx
            # Existing slam effects are not intercepted; only new effects can apply a style.
            if scene.get("fx") in EFFECTS[:8] and "style" not in source and "typestyle" not in source:
                options = [v for v in STYLES if v != previous_style]
                scene["typestyle"] = min(options, key=lambda v: (styles[v], chstyles[v], _seed(topic, chapter, i, "slam|" + look + "|" + v)))
            style = scene.get("typestyle")
            if isinstance(style, str):
                styles[style] += 1; chstyles[style] += 1; previous_style = style
        if scene.get("type") == "quote" and scene.get("text"):
            if "fx" not in source:
                scene["fx"] = plan.get((i, -1)) or min(QUOTE_EFFECTS, key=lambda v: (auto_fx[v], effects[v], _seed(topic, chapter, i, v)))
                auto_fx[scene["fx"]] += 1
            scene["quoteKinetic"] = True
            fx = scene.get("fx", "soft-fade")
            effects[fx] += 1; scene_fx.add(fx); previous_fx = fx
        chfx.update(scene_fx)
    return chfx, chstyles
