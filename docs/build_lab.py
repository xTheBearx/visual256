"""Build docs/netrunner-lab.html from docs/lab-template.html.

Injects the BIP-39 word list and the theme collection from the Python package, so the browser
preview always uses the same data as the package. Run after changing themes.py:

    python docs/build_lab.py
"""

import json
from pathlib import Path

from visual256 import bip39
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
        })
    return json.dumps(out, separators=(",", ":"))


def main() -> None:
    template = (HERE / "lab-template.html").read_text(encoding="utf-8")
    page = template.replace("__BIP39__", " ".join(bip39.wordlist())).replace("__THEMES_JSON__", theme_json())
    (HERE / "netrunner-lab.html").write_text(page, encoding="utf-8")
    print(HERE / "netrunner-lab.html")


if __name__ == "__main__":
    main()
