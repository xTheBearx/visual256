"""The theme collection. The hash picks the theme (bits 0-2), so a theme is the strongest
headline feature: it sets the background, its pattern, the fonts and the 16-color palette that
every color feature indexes into.

The collection is small on purpose: 4 dark and 4 light backgrounds, each a clearly different hue
with its own pattern and font, so the theme alone is recognizable at a glance. Several themes share a palette; the palette only has
to read well on its background.

Development version 0.1: themes may still change. After a release, add themes only with a new
spec version, and never reorder existing entries, or old badges would change.
"""

from __future__ import annotations

import math

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    bg: str            # card background
    panel: str         # head fill
    grid_kind: str     # background pattern (see draw.background)
    grid_color: str
    glow: bool         # neon glow (blur filter)
    handle: str        # handle text
    chroma: tuple[str, str]  # glitch split colors
    peak: str          # top lit segment of each signal bar
    unlit: str         # unlit bar and hex segments
    bracket: str       # detail cell corner brackets
    handle_font: str   # key into fonts.FONT_FILES
    code_font: str     # font for chip characters
    palette: tuple[tuple[str, str], ...]
    pair_bg: str
    pair_fg: str
    ink_dark: str = "#111318"
    ink_light: str = "#FFFFFF"
    gradients: tuple[tuple[str, str], ...] = ()  # 8 (hue name, color) the background can fade to
    sheen: str = "rgba(255,255,255,.09)"          # highlight streak along the gradient direction
    tones: tuple[tuple[str, str], ...] = ()       # 8 (light, dark) pairs for light-to-dark gradients

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(n for n, _ in self.palette)

    def color(self, i: int) -> str:
        return self.palette[i & 15][1]


def lab(hex_color: str) -> tuple[float, float, float]:
    """CIELAB (D65) of an sRGB hex color."""
    r, g, b = (int(hex_color[k:k + 2], 16) / 255 for k in (1, 3, 5))
    lin = [((v + .055) / 1.055) ** 2.4 if v > .04045 else v / 12.92 for v in (r, g, b)]
    x = (lin[0] * .4124 + lin[1] * .3576 + lin[2] * .1805) / .95047
    y = lin[0] * .2126 + lin[1] * .7152 + lin[2] * .0722
    z = (lin[0] * .0193 + lin[1] * .1192 + lin[2] * .9505) / 1.08883
    f = lambda t: t ** (1 / 3) if t > .008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def delta_e(c1, c2) -> float:
    """CIEDE2000 color difference between two CIELAB colors; below about 10 two swatches are hard
    to tell apart at badge size."""
    L1, a1, b1 = c1
    L2, a2, b2 = c2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = .5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p, h2p = math.degrees(math.atan2(b1, a1p)) % 360, math.degrees(math.atan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dh = h2p - h1p
    if C1p * C2p == 0:
        dh = 0
    elif dh > 180:
        dh -= 360
    elif dh < -180:
        dh += 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    else:
        hbp = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = (1 - .17 * math.cos(math.radians(hbp - 30)) + .24 * math.cos(math.radians(2 * hbp))
         + .32 * math.cos(math.radians(3 * hbp + 6)) - .2 * math.cos(math.radians(4 * hbp - 63)))
    SL = 1 + .015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2)
    SC, SH = 1 + .045 * Cbp, 1 + .015 * Cbp * T
    RT = -2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) * math.sin(math.radians(60 * math.exp(-((hbp - 275) / 25) ** 2)))
    return math.sqrt((dLp / SL) ** 2 + (dCp / SC) ** 2 + (dHp / SH) ** 2 + RT * (dCp / SC) * (dHp / SH))


def luminance(hex_color: str) -> float:
    n = int(hex_color[1:7], 16)
    ch = []
    for v in ((n >> 16) & 255, (n >> 8) & 255, n & 255):
        v /= 255
        ch.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def _p(spec: str) -> tuple[tuple[str, str], ...]:
    out = tuple(tuple(item.split(":")) for item in spec.split("|"))
    assert len(out) == 16
    return out  # type: ignore[return-value]


# Palettes for dark backgrounds
NEON = _p("Hot pink:#FF2685|Magenta:#FA6ADF|Violet:#C12BFC|Ultraviolet:#7170FF|Electric blue:#469BFD|"
          "Cyan:#0AC4D0|Aqua:#00FFC3|Neon green:#13ED27|Acid:#D0FD07|Yellow:#F6D31A|Amber:#FFA80C|"
          "Orange:#FF6A00|Red:#FF2A3D|Rose:#FDA6C4|Ice:#B9F3FF|White:#F0F3FF")
PASTEL = _p("White:#F4F8FF|Silver:#ADB7CA|Sky:#82D4F9|Cyan:#30F9F8|Teal:#25B4AD|Mint:#8DF5B5|Lime:#C6F25A|"
            "Yellow:#FADB54|Sand:#EADFBD|Amber:#FFAD2D|Orange:#FF8A4C|Coral:#FF6B6B|Pink:#FD90CE|Peach:#FFC9B4|"
            "Lilac:#E5CBFD|Violet:#9D8CFF")
FIRE = _p("Gold:#FBC736|Lemon:#F3FE92|Amber:#AE9511|Orange:#D57D09|Flame:#FC5510|Red:#FF475D|Coral:#FF9988|"
          "Pink:#F494BB|Orchid:#EF75FF|Violet:#C0ABDE|Sky:#94D2FF|Cyan:#4AD8E1|Mint:#77D07D|Sage:#D4E9CA|"
          "Peach:#FED4BD|White:#FFFFFF")
TROPIC = _p("Parrot red:#FF4047|Mango:#FFAF23|Banana:#FFE033|Lime:#C2F539|Leaf:#4CD964|Lagoon:#2ED8C3|"
            "Sky:#5AC8FA|Blue:#4F8BFF|Orchid:#D663D9|Hibiscus:#FF8BB4|Coral:#FB9787|Papaya:#FFCCA8|Sand:#E0DCAA|"
            "Bone:#F9F9F6|Lilac:#C3A6FF|Toucan:#DF7305")
# Palettes for light backgrounds
DAY = _p("Red:#DE2937|Orange:#F26419|Amber:#C78A00|Lime:#6AA00A|Green:#2D8246|Teal:#0A8282|Cyan:#1BA3C6|"
         "Blue:#3075F1|Navy:#1E387A|Indigo:#4A25DB|Purple:#9850C1|Magenta:#BA1A5D|Pink:#EC6FA6|Brown:#8D5524|"
         "Slate:#636E80|Black:#111318")
INK = _p("Navy:#152A5F|Oxblood:#7A1F2B|Forest:#204B31|Plum:#5B1E5A|Teal:#1F6E73|Sepia:#694824|Slate:#5D636C|"
         "Crimson:#D42536|Royal:#3663C7|Olive:#5A5E18|Ochre:#B07A12|Indigo:#5524CA|Moss:#558D2D|Rust:#AD4A13|"
         "Charcoal:#232323|Rose:#B34876")
CANDY = _p("Raspberry:#B91155|Cherry:#DB3C41|Tangerine:#EC6421|Honey:#B87700|Lime:#689F38|Mint:#00A884|"
           "Teal:#00796B|Sky:#0288D1|Blueberry:#38459E|Grape:#8117A1|Lavender:#9575CD|Bubblegum:#F06292|"
           "Chocolate:#6D4C41|Licorice:#212121|Slate:#546E7A|Forest:#2B5E2B")
GARDEN = _p("Red:#E0281B|Orange:#EF6C00|Gold:#C98A00|Olive:#827717|Green:#2E7D32|Teal:#008B7B|Cyan:#00839D|"
            "Blue:#156BC0|Navy:#0F144F|Indigo:#3C3BDB|Purple:#841695|Magenta:#9D1556|Pink:#F50964|Brown:#5D4037|"
            "Gray:#415B5E|Black:#1B1B1B")


# The background fades from the theme color to one of 8 hues (chosen by the `tint` bits). SHEEN and
# PARTNERS are generated by tools/tune_gradients.py: each is as strong as the theme's palette allows
# while every palette color keeps 2:1 contrast and handle text 4.5:1 (1.8:1 and 4:1 inside the
# narrow streak band).
HUE_NAMES = ("red", "orange", "yellow", "green", "cyan", "blue", "violet", "magenta")
SHEEN = {
    "cyberpunk": "rgba(255,255,255,0.22)",
    "daylight": "rgba(255,255,255,0.6)",
    "paper": "rgba(255,255,255,0.6)",
    "blueprint": "rgba(255,255,255,0.22)",
    "candy": "rgba(255,255,255,0.6)",
    "mint": "rgba(255,255,255,0.6)",
    "ember": "rgba(255,255,255,0.22)",
    "jungle": "rgba(255,255,255,0.22)",
}
PARTNERS = {
    "cyberpunk": ("#680505", "#3A1D03", "#292402", "#022E06", "#022A2E", "#05245A", "#400780", "#5C0542"),
    "daylight": ("#FCCFCF", "#FBD1AD", "#F8E777", "#77F882", "#77EDF8", "#C7DBFC", "#E5D1FD", "#FCCAED"),
    "paper": ("#FBAAAA", "#F8B377", "#F8E777", "#77F882", "#77EDF8", "#9EC0FA", "#D4B1FB", "#FAA3E0"),
    "blueprint": ("#B30909", "#743A06", "#524804", "#05570B", "#055057", "#0945AC", "#720CE6", "#A50976"),
    "candy": ("#FCC5C5", "#FAC99E", "#F8E777", "#77F882", "#77EDF8", "#BED4FC", "#E1CAFC", "#FCC2EB"),
    "mint": ("#FCCACA", "#FACDA5", "#F8E777", "#77F882", "#77EDF8", "#C0D6FC", "#E3CCFC", "#FCC5EB"),
    "ember": ("#910808", "#5A2C05", "#3F3703", "#044409", "#043E44", "#073688", "#5C0ABB", "#85075F"),
    "jungle": ("#8A0707", "#552A04", "#3D3503", "#034109", "#033C41", "#073380", "#5709B1", "#7E075A"),
}
TONES = {
    "cyberpunk": (("#680505", "#050000"), ("#3A1D03", "#050200"), ("#292402", "#050400"), ("#022E06", "#000501"), ("#022A2E", "#000405"), ("#05245A", "#000205"), ("#400780", "#020005"), ("#5C0542", "#050003")),
    "daylight": (("#FFFAFA", "#FCCFCF"), ("#FFFCFA", "#FBD1AD"), ("#FFFEFA", "#F5DC3D"), ("#FAFFFB", "#58F665"), ("#FAFEFF", "#66EBF7"), ("#FAFCFF", "#C7DBFC"), ("#FCFAFF", "#E5D1FD"), ("#FFFAFD", "#FCCAED")),
    "paper": (("#FFFAFA", "#FBAAAA"), ("#FFFCFA", "#F7AF70"), ("#FFFEFA", "#F5DC3D"), ("#FAFFFB", "#3DF54D"), ("#FAFEFF", "#3DE6F5"), ("#FAFCFF", "#9EC0FA"), ("#FCFAFF", "#D4B1FB"), ("#FFFAFD", "#FAA3E0")),
    "blueprint": (("#B30909", "#050000"), ("#743A06", "#050200"), ("#524804", "#050400"), ("#05570B", "#000501"), ("#055057", "#000405"), ("#0945AC", "#000205"), ("#720CE6", "#020005"), ("#A50976", "#050003")),
    "candy": (("#FFFAFA", "#FCC5C5"), ("#FFFCFA", "#FAC99E"), ("#FFFEFA", "#F5DC3D"), ("#FAFFFB", "#3DF54D"), ("#FAFEFF", "#42E6F5"), ("#FAFCFF", "#BED4FC"), ("#FCFAFF", "#E1CAFC"), ("#FFFAFD", "#FCC2EB")),
    "mint": (("#FFFAFA", "#FCCACA"), ("#FFFCFA", "#FACDA5"), ("#FFFEFA", "#F5DC3D"), ("#FAFFFB", "#3DF54D"), ("#FAFEFF", "#53E8F6"), ("#FAFCFF", "#C0D6FC"), ("#FCFAFF", "#E3CCFC"), ("#FFFAFD", "#FCC5EB")),
    "ember": (("#910808", "#050000"), ("#5A2C05", "#050200"), ("#3F3703", "#050400"), ("#044409", "#000501"), ("#043E44", "#000405"), ("#073688", "#000205"), ("#5C0ABB", "#020005"), ("#85075F", "#050003")),
    "jungle": (("#8A0707", "#050000"), ("#552A04", "#050200"), ("#3D3503", "#050400"), ("#034109", "#000501"), ("#033C41", "#000405"), ("#073380", "#000205"), ("#5709B1", "#020005"), ("#7E075A", "#050003")),
}


def _dark(**kw) -> Theme:
    base = dict(glow=False, peak="#FFFFFF", unlit="rgba(255,255,255,.09)", bracket="rgba(255,255,255,.38)",
                code_font="mono", ink_dark=kw.get("bg", "#111318"), ink_light="#FFFFFF", sheen="rgba(255,255,255,.10)")
    base.update(kw)
    base.setdefault("pair_bg", base["bg"])
    base["sheen"] = SHEEN.get(base["id"], base["sheen"])
    base["gradients"] = tuple(zip(HUE_NAMES, PARTNERS.get(base["id"], (base["bg"],) * len(HUE_NAMES))))
    base["tones"] = TONES.get(base["id"], ((base["bg"], base["bg"]),) * len(HUE_NAMES))
    return Theme(**base)


def _light(**kw) -> Theme:
    ink = kw.get("handle", "#14161C")
    r, g, b = int(ink[1:3], 16), int(ink[3:5], 16), int(ink[5:7], 16)
    base = dict(glow=False, peak=ink, unlit=f"rgba({r},{g},{b},.09)", bracket=f"rgba({r},{g},{b},.35)",
                code_font="mono", ink_dark=ink, ink_light="#FFFFFF", sheen="rgba(255,255,255,.6)")
    base.update(kw)
    base.setdefault("pair_bg", base["bg"])
    base["sheen"] = SHEEN.get(base["id"], base["sheen"])
    base["gradients"] = tuple(zip(HUE_NAMES, PARTNERS.get(base["id"], (base["bg"],) * len(HUE_NAMES))))
    base["tones"] = TONES.get(base["id"], ((base["bg"], base["bg"]),) * len(HUE_NAMES))
    return Theme(**base)


THEMES_LIST = (
    _dark(id="cyberpunk", name="Cyberpunk", bg="#0A0913", panel="#16132C", grid_kind="grid",
          grid_color="rgba(120,140,255,.12)", glow=True, handle="#F4F7FF",
          chroma=("rgba(0,229,255,.8)", "rgba(255,43,241,.8)"), handle_font="cyber", palette=NEON, pair_fg="#00E5FF",
          unlit="rgba(255,255,255,.08)", bracket="rgba(255,255,255,.35)", ink_dark="#111318"),
    _light(id="daylight", name="Daylight", bg="#F5F6F9", panel="#FFFFFF", grid_kind="dots",
           grid_color="rgba(30,40,70,.16)", handle="#14161C", chroma=("rgba(27,163,198,.85)", "rgba(194,24,91,.85)"),
           handle_font="cyber", palette=DAY, pair_fg="#1E3A8A", ink_dark="#111318"),
    _light(id="paper", name="Paper", bg="#F3ECD9", panel="#FBF6E9", grid_kind="hatch",
           grid_color="rgba(90,60,30,.10)", handle="#1E1B16", chroma=("rgba(35,70,184,.75)", "rgba(200,32,47,.75)"),
           handle_font="serif", palette=INK, pair_fg="#1F3A6B", ink_light="#FBF6E9"),
    _dark(id="blueprint", name="Blueprint", bg="#0F3A68", panel="#164A80", grid_kind="grid",
          grid_color="rgba(255,255,255,.14)", handle="#F4F8FF", chroma=("rgba(143,211,255,.85)", "rgba(255,158,207,.85)"),
          handle_font="mono", palette=PASTEL, pair_fg="#F4F8FF", unlit="rgba(255,255,255,.12)",
          bracket="rgba(255,255,255,.45)"),
    _light(id="candy", name="Candy", bg="#FCE6F0", panel="#FFF7FB", grid_kind="polka",
           grid_color="rgba(194,24,91,.10)", handle="#3A0F24", chroma=("rgba(0,168,132,.8)", "rgba(57,73,171,.8)"),
           handle_font="retro", palette=CANDY, pair_fg="#C2185B"),
    _light(id="mint", name="Mint", bg="#E3F4EC", panel="#F7FFFB", grid_kind="waves",
           grid_color="rgba(0,90,60,.16)", handle="#0E2E22", chroma=("rgba(211,47,47,.75)", "rgba(21,101,192,.75)"),
           handle_font="mono", palette=GARDEN, pair_fg="#00796B"),
    _dark(id="ember", name="Ember", bg="#2A0C0C", panel="#3A1414", grid_kind="scanlines",
          grid_color="rgba(255,120,60,.10)", glow=True, handle="#FFF1E0",
          chroma=("rgba(255,213,79,.8)", "rgba(255,61,61,.8)"), handle_font="stencil", palette=FIRE, pair_fg="#FF8F00",
          unlit="rgba(255,220,200,.09)", bracket="rgba(255,200,170,.38)"),
    _dark(id="jungle", name="Jungle", bg="#0B3A1C", panel="#134A28", grid_kind="zigzag",
          grid_color="rgba(180,255,180,.12)", handle="#F1FFE8", chroma=("rgba(255,166,43,.8)", "rgba(218,112,214,.8)"),
          handle_font="pixel", palette=TROPIC, pair_fg="#B6F23C"),
)
THEMES: dict[str, Theme] = {t.id: t for t in THEMES_LIST}
assert len(THEMES_LIST) == 8


def get(theme: int | str | Theme) -> Theme:
    if isinstance(theme, Theme):
        return theme
    if isinstance(theme, int):
        return THEMES_LIST[theme]
    try:
        return THEMES[theme]
    except KeyError:
        raise ValueError(f"unknown theme {theme!r}; choose from {', '.join(THEMES)}") from None


def chip_ink(theme: Theme, color: str) -> str:
    """Readable text color on a chip or tile of `color`."""
    return theme.ink_dark if luminance(color) > 0.3 else theme.ink_light
