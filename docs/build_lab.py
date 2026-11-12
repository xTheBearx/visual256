"""Build docs/netrunner-lab.html from docs/lab-template.html.

Injects the BIP-39 word list, the theme collection, the icon geometry and the Document style's
data from the Python package, so the browser preview always uses the same data
as the package. Run after changing themes.py or icons.py:

    python docs/build_lab.py
"""

import json
from pathlib import Path

from visual256 import bip39, document, icons
from visual256.fonts import glyph_path
from visual256.themes import THEMES_LIST

HERE = Path(__file__).parent


def theme_json() -> str:
    out = []
    for t in THEMES_LIST:
        out.append({
            "id": t.id, "name": t.name, "bg": t.bg, "panel": t.panel, "grid": t.grid_kind, "gridColor": t.grid_color,
            "glow": t.glow, "handle": t.handle, "chroma": list(t.chroma), "peak": t.peak, "unlit": t.unlit,
            "bracket": t.bracket, "font": t.handle_font, "code": t.code_font, "palette": [list(p) for p in t.palette],
            "pairBg": t.pair_bg, "pairFg": t.pair_fg, "inkDark": t.ink_dark, "inkLight": t.ink_light,
            "gradients": [list(g) for g in t.gradients],
            "sheen": t.sheen,
            "tones": [list(x) for x in t.tones],
        })
    return json.dumps(out, separators=(",", ":"))


def _with_glyph(sp: dict) -> dict:
    """Character and emoji tiles carry their glyph as path data, so the lab draws exactly the
    bundled font's outline (and never a color-emoji fallback)."""
    if "text" not in sp:
        return sp
    ch, x, y, size, inverted, font = sp["text"]
    return sp | {"glyph": glyph_path(font, ch, x, y, size)}


def icons_json() -> str:
    out = {kind: {"names": list(names), "specs": {n: _with_glyph(icons.icon_spec(kind, n)) for n in names}}
           for kind, (names, _) in icons.KINDS.items()}
    return json.dumps(out, separators=(",", ":"))


def doc_json() -> str:
    out = {
        "fields": [list(f) for f in document.DOC_FIELDS],
        "sheets": [{"id": s.id, "name": s.name, "bg": s.bg, "ink": s.ink, "rule": s.rule, "grid": s.grid,
                    "palette": [list(p) for p in s.palette]} for s in document.SHEETS],
        "outlines": list(document.OUTLINES), "motifs": list(document.MOTIFS), "codeWords": list(document.CODE_WORDS),
        "glyphStyles": list(document.GLYPH_STYLES), "barStyles": list(document.BAR_STYLES),
        "barFields": [list(f) for f in document.BAR_FIELDS], "subjects": [list(x) for x in document.DOC_SUBJECTS],
    }
    return json.dumps(out, separators=(",", ":"))


def main() -> None:
    template = (HERE / "lab-template.html").read_text(encoding="utf-8")
    page = template.replace("__BIP39__", " ".join(bip39.wordlist())).replace("__THEMES_JSON__", theme_json())
    page = page.replace("__ICONS_JSON__", icons_json()).replace("__DOC_JSON__", doc_json())
    (HERE / "netrunner-lab.html").write_text(page, encoding="utf-8")
    print(HERE / "netrunner-lab.html")


if __name__ == "__main__":
    main()
