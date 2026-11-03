"""The theme collection. The hash picks the theme (bits 0-3), so a theme is the strongest
headline feature: it sets the background, its pattern, the fonts and the 16-color palette that
every color feature indexes into.

The collection is balanced: 8 dark and 8 light backgrounds, each with a different hue, so the
theme alone is recognizable at a glance. Several themes share a palette; the palette only has
to read well on its background.

Development version 0.1: themes may still change. After a release, add themes only with a new
spec version, and never reorder existing entries, or old badges would change.
"""

from __future__ import annotations

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

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(n for n, _ in self.palette)

    def color(self, i: int) -> str:
        return self.palette[i & 15][1]


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
NEON = _p("Hot pink:#FF2E88|Magenta:#FF2BF1|Violet:#B04DFF|Ultraviolet:#6E5BFF|Electric blue:#2F7BFF|Cyan:#00E5FF|"
          "Aqua:#00FFC3|Neon green:#39FF14|Acid:#C6FF00|Yellow:#FFF200|Amber:#FFB000|Orange:#FF6A00|Red:#FF2A3D|"
          "Rose:#FF8FB8|Ice:#A8E6FF|White:#F4F7FF")
PASTEL = _p("White:#F4F8FF|Silver:#B9C6D8|Sky:#8FD3FF|Cyan:#3FE0E8|Teal:#2EC4B6|Mint:#8DF5B5|Lime:#C6F25A|"
            "Yellow:#FFE45E|Sand:#E9D7A5|Amber:#FFB547|Orange:#FF8A4C|Coral:#FF6B6B|Pink:#FF9ECF|Peach:#FFC9A3|"
            "Lilac:#C9A7FF|Violet:#9D8CFF")
PICO = _p("Red:#FF004D|Orange:#FFA300|Yellow:#FFEC27|Green:#00E436|Blue:#29ADFF|Lavender:#9C8CD8|Pink:#FF77A8|"
          "Peach:#FFCCAA|Cream:#FFF1E8|Silver:#C2C3C7|Brown:#C2683C|Plum:#B03A78|Forest:#1FA35A|Cyan:#00F5FF|"
          "Purple:#B65CFF|Lime:#A8E61D")
HIVIS = _p("Blaze:#FF6A13|Safety yellow:#FFD300|Signal red:#E5322D|Lime:#9BE22D|Mint:#7FE7C4|Sky:#7FC8F8|"
           "Cobalt:#4D7CFE|Violet:#A98BFF|Pink:#FF8FC8|Sand:#D9C9A3|Khaki:#B8B07A|Rust:#C8642D|Teal:#2FB5A5|"
           "Ivory:#F2EFE3|Steel:#9AA7B0|Amber:#FFB000")
FIRE = _p("Gold:#FFD54F|Lemon:#FFF176|Amber:#FFB300|Orange:#FF8F00|Flame:#FF5722|Red:#FF3D3D|Coral:#FF8A80|"
          "Pink:#F48FB1|Orchid:#EA80FC|Violet:#B39DDB|Sky:#81D4FA|Cyan:#4DD0E1|Mint:#A5D6A7|Lime:#C5E1A5|"
          "Peach:#FFCCBC|White:#FFFFFF")
JEWEL = _p("Gold:#F2C14E|Ruby:#FF3B7F|Emerald:#2ECC71|Sapphire:#4D8BFF|Amethyst:#B57BFF|Topaz:#FFB347|"
           "Pearl:#F4F1EA|Rose quartz:#FF9EC0|Turquoise:#40E0D0|Coral:#FF7F50|Citrine:#E4D00A|Jade:#00C27A|"
           "Aquamarine:#7FFFD4|Garnet:#FF5A4F|Silver:#C8C8D0|Peridot:#B4D335")
TROPIC = _p("Parrot red:#FF4040|Mango:#FFA62B|Banana:#FFE14D|Lime:#B6F23C|Leaf:#4CD964|Lagoon:#2ED8C3|"
            "Sky:#5AC8FA|Blue:#4F8BFF|Orchid:#DA70D6|Hibiscus:#FF7EB6|Coral:#FF7F66|Papaya:#FFC8A2|Sand:#E8D8A8|"
            "Bone:#F5F5F0|Lilac:#C3A6FF|Toucan:#FF7A00")
# Palettes for light backgrounds
DAY = _p("Red:#D7263D|Orange:#F26419|Amber:#C78A00|Lime:#5E9A0E|Green:#2E9E44|Teal:#0F8B8D|Cyan:#1BA3C6|"
         "Blue:#2563EB|Navy:#1E3A8A|Indigo:#5B4BD8|Purple:#8E3FC0|Magenta:#C2185B|Pink:#EC6FA6|Brown:#8D5524|"
         "Slate:#64748B|Black:#111318")
INK = _p("Navy:#1F3A6B|Oxblood:#7A1F2B|Forest:#23573A|Plum:#6B2A6E|Teal:#1F6E73|Sepia:#6B4A2B|Slate:#55606E|"
         "Crimson:#C0272F|Royal:#2F55C8|Olive:#6B7022|Ochre:#B07A12|Indigo:#4A2F9A|Moss:#4F8A2B|Rust:#B5501F|"
         "Charcoal:#232323|Rose:#B8426E")
CANDY = _p("Raspberry:#C2185B|Cherry:#E53935|Tangerine:#F4511E|Honey:#B87700|Lime:#689F38|Mint:#00A884|"
           "Teal:#00796B|Sky:#0288D1|Blueberry:#3949AB|Grape:#7B1FA2|Lavender:#9575CD|Bubblegum:#F06292|"
           "Chocolate:#6D4C41|Licorice:#212121|Slate:#546E7A|Forest:#2E6B30")
GARDEN = _p("Red:#D32F2F|Orange:#EF6C00|Gold:#C98A00|Olive:#827717|Green:#2E7D32|Teal:#00796B|Cyan:#0097A7|"
            "Blue:#1565C0|Navy:#1A237E|Indigo:#4527A0|Purple:#6A1B9A|Magenta:#AD1457|Pink:#E91E63|Brown:#5D4037|"
            "Gray:#546E7A|Black:#1B1B1B")
BOLD = _p("Red:#B71C1C|Orange:#C43E00|Mustard:#8A6500|Moss:#3E6B1F|Green:#1B5E20|Teal:#00594F|Cyan:#006672|"
          "Blue:#0D47A1|Navy:#0D1B4C|Purple:#5B1A8A|Magenta:#9C1050|Maroon:#5E1424|Brown:#4E342E|Black:#111111|"
          "Olive:#555A16|Slate:#2F3E46")


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
    "arcade": "rgba(255,255,255,0.155)",
    "stealth": "rgba(255,255,255,0.175)",
    "ember": "rgba(255,255,255,0.22)",
    "abyss": "rgba(255,255,255,0.19)",
    "sky": "rgba(255,255,255,0.6)",
    "royal": "rgba(255,255,255,0.22)",
    "citrus": "rgba(255,255,255,0.6)",
    "jungle": "rgba(255,255,255,0.22)",
    "lilac": "rgba(255,255,255,0.6)",
    "concrete": "rgba(255,255,255,0.6)",
}
PARTNERS = {
    "cyberpunk": ("#550404", "#301803", "#1F1C02", "#022405", "#022124", "#041D49", "#35066B", "#4B0436"),
    "daylight": ("#FCCFCF", "#FBD1AD", "#F8E777", "#77F882", "#77EDF8", "#C7DBFC", "#E5D1FD", "#FCCAED"),
    "paper": ("#FBAAAA", "#F8B377", "#F8E777", "#77F882", "#77EDF8", "#9EC0FA", "#D4B1FB", "#FAA3E0"),
    "blueprint": ("#B30909", "#743A06", "#524804", "#05570B", "#055057", "#0945AC", "#720CE6", "#A50976"),
    "candy": ("#FCC5C5", "#FAC99E", "#F8E777", "#77F882", "#77EDF8", "#BED4FC", "#E1CAFC", "#FCC2EB"),
    "mint": ("#FCCACA", "#FACDA5", "#F8E777", "#77F882", "#77EDF8", "#C0D6FC", "#E3CCFC", "#FCC5EB"),
    "arcade": ("#550404", "#301803", "#221E02", "#022705", "#022427", "#041E4B", "#340568", "#4B0436"),
    "stealth": ("#770606", "#4B2504", "#332C03", "#033807", "#033338", "#062C6D", "#4A0896", "#6B064C"),
    "ember": ("#880707", "#552A04", "#3A3303", "#033F08", "#033A3F", "#07327E", "#5609AE", "#790657"),
    "abyss": ("#680505", "#3D1E03", "#2C2602", "#033006", "#022A2E", "#05255C", "#410783", "#5C0542"),
    "sky": ("#FCCACA", "#FACDA5", "#F8E777", "#77F882", "#77EDF8", "#C0D6FC", "#E3CCFC", "#FCC5EB"),
    "royal": ("#8F0808", "#5A2C05", "#3D3503", "#034109", "#043E44", "#073585", "#5909B3", "#80075C"),
    "citrus": ("#FCC5C5", "#FAC99E", "#F8E777", "#77F882", "#77EDF8", "#BED4FC", "#E1CAFC", "#FCC2EB"),
    "jungle": ("#8A0707", "#552A04", "#3D3503", "#034109", "#033C41", "#073380", "#5709B1", "#7E075A"),
    "lilac": ("#FCCACA", "#FACDA5", "#F8E777", "#77F882", "#77EDF8", "#C0D6FC", "#E3CCFC", "#FCC5EB"),
    "concrete": ("#F87C7C", "#F8B377", "#F8E777", "#77F882", "#77EDF8", "#77A6F8", "#BE8BF9", "#F877D1"),
}


def _dark(**kw) -> Theme:
    base = dict(glow=False, peak="#FFFFFF", unlit="rgba(255,255,255,.09)", bracket="rgba(255,255,255,.38)",
                code_font="mono", ink_dark=kw.get("bg", "#111318"), ink_light="#FFFFFF", sheen="rgba(255,255,255,.10)")
    base.update(kw)
    base.setdefault("pair_bg", base["bg"])
    base["sheen"] = SHEEN.get(base["id"], base["sheen"])
    base["gradients"] = tuple(zip(HUE_NAMES, PARTNERS.get(base["id"], (base["bg"],) * len(HUE_NAMES))))
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
    _dark(id="arcade", name="Arcade", bg="#17175A", panel="#24247A", grid_kind="pixels",
          grid_color="rgba(255,255,255,.35)", handle="#FFFFFF", chroma=("#FF004D", "#29ADFF"),
          handle_font="pixel", code_font="pixel", palette=PICO, pair_fg="#FFEC27", unlit="rgba(255,255,255,.11)",
          bracket="rgba(255,255,255,.45)"),
    _dark(id="stealth", name="Stealth", bg="#2C2C2A", panel="#3B3B38", grid_kind="crosses",
          grid_color="rgba(230,230,220,.13)", handle="#ECE9DA", chroma=("rgba(255,140,0,.8)", "rgba(120,200,255,.8)"),
          handle_font="stencil", palette=HIVIS, pair_fg="#FFD300", unlit="rgba(236,233,218,.10)",
          bracket="rgba(236,233,218,.4)"),
    _dark(id="ember", name="Ember", bg="#2A0C0C", panel="#3A1414", grid_kind="scanlines",
          grid_color="rgba(255,120,60,.10)", glow=True, handle="#FFF1E0",
          chroma=("rgba(255,213,79,.8)", "rgba(255,61,61,.8)"), handle_font="stencil", palette=FIRE, pair_fg="#FF8F00",
          unlit="rgba(255,220,200,.09)", bracket="rgba(255,200,170,.38)"),
    _dark(id="abyss", name="Abyss", bg="#052B30", panel="#0B3B42", grid_kind="bubbles",
          grid_color="rgba(120,255,240,.18)", glow=True, handle="#E8FFFD",
          chroma=("rgba(0,229,255,.8)", "rgba(198,255,0,.8)"), handle_font="retro", palette=NEON, pair_fg="#00FFC3"),
    _light(id="sky", name="Sky", bg="#E1EEFA", panel="#F8FBFF", grid_kind="zigzag",
           grid_color="rgba(20,60,120,.15)", handle="#0B1F3A", chroma=("rgba(233,30,99,.75)", "rgba(0,151,167,.75)"),
           handle_font="cyber", palette=GARDEN, pair_fg="#1565C0"),
    _dark(id="royal", name="Royal", bg="#2B1145", panel="#3A1A5C", grid_kind="lattice",
          grid_color="rgba(242,193,78,.15)", handle="#F8EED0", chroma=("rgba(242,193,78,.8)", "rgba(255,59,127,.8)"),
          handle_font="serif", palette=JEWEL, pair_fg="#F2C14E", bracket="rgba(242,193,78,.45)"),
    _light(id="citrus", name="Citrus", bg="#FFF5D1", panel="#FFFDF2", grid_kind="rays",
           grid_color="rgba(200,140,0,.14)", handle="#2E2200", chroma=("rgba(0,121,107,.75)", "rgba(229,57,53,.75)"),
           handle_font="pixel", palette=CANDY, pair_fg="#E65100"),
    _dark(id="jungle", name="Jungle", bg="#0B3A1C", panel="#134A28", grid_kind="waves",
          grid_color="rgba(180,255,180,.12)", handle="#F1FFE8", chroma=("rgba(255,166,43,.8)", "rgba(218,112,214,.8)"),
          handle_font="cyber", palette=TROPIC, pair_fg="#B6F23C"),
    _light(id="lilac", name="Lilac", bg="#EDE7FA", panel="#FBF9FF", grid_kind="hatch",
           grid_color="rgba(80,50,160,.12)", handle="#1F1438", chroma=("rgba(0,121,107,.75)", "rgba(194,24,91,.75)"),
           handle_font="serif", palette=GARDEN, pair_fg="#5B4BD8"),
    _light(id="concrete", name="Concrete", bg="#C9CCD1", panel="#E4E6E9", grid_kind="pixels",
           grid_color="rgba(30,30,30,.22)", handle="#111111", chroma=("rgba(198,40,40,.8)", "rgba(21,101,192,.8)"),
           handle_font="mono", palette=BOLD, pair_fg="#111111"),
)
THEMES: dict[str, Theme] = {t.id: t for t in THEMES_LIST}
assert len(THEMES_LIST) == 16


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
