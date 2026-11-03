"""The theme collection. In spec v2 the hash picks the theme (bits 0-2), so a theme is a
headline feature: it sets the background, fonts and the 16-color palette that every color
feature indexes into.

To add a theme later, append it here and widen the `theme` field in spec.py; never reorder
existing entries, or old badges would change.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    bg: str            # card background
    panel: str         # head fill
    grid_kind: str     # background pattern: grid, dots, hatch, horizon, scanlines, pixels or crosses
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


THEMES_LIST = (
    Theme(id="cyberpunk", name="Cyberpunk", bg="#0A0913", panel="#16132C", grid_kind="grid",
          grid_color="rgba(120,140,255,.12)", glow=True, handle="#F4F7FF",
          chroma=("rgba(0,229,255,.8)", "rgba(255,43,241,.8)"), peak="#FFFFFF", unlit="rgba(255,255,255,.08)",
          bracket="rgba(255,255,255,.35)", handle_font="cyber", code_font="mono",
          palette=(("Hot pink", "#FF2E88"), ("Magenta", "#FF2BF1"), ("Violet", "#B04DFF"), ("Ultraviolet", "#6E5BFF"),
                   ("Electric blue", "#2F7BFF"), ("Cyan", "#00E5FF"), ("Aqua", "#00FFC3"), ("Neon green", "#39FF14"),
                   ("Acid", "#C6FF00"), ("Yellow", "#FFF200"), ("Amber", "#FFB000"), ("Orange", "#FF6A00"),
                   ("Red", "#FF2A3D"), ("Rose", "#FF8FB8"), ("Ice", "#A8E6FF"), ("White", "#F4F7FF")),
          pair_bg="#0A0913", pair_fg="#00E5FF"),
    Theme(id="daylight", name="Daylight", bg="#F5F6F9", panel="#FFFFFF", grid_kind="dots",
          grid_color="rgba(30,40,70,.16)", glow=False, handle="#14161C",
          chroma=("rgba(27,163,198,.85)", "rgba(194,24,91,.85)"), peak="#14161C", unlit="rgba(20,24,40,.09)",
          bracket="rgba(20,24,40,.35)", handle_font="cyber", code_font="mono",
          palette=(("Red", "#D7263D"), ("Orange", "#F26419"), ("Amber", "#E3A008"), ("Lime", "#7CB518"),
                   ("Green", "#2E9E44"), ("Teal", "#0F8B8D"), ("Cyan", "#1BA3C6"), ("Blue", "#2563EB"),
                   ("Navy", "#1E3A8A"), ("Indigo", "#5B4BD8"), ("Purple", "#8E3FC0"), ("Magenta", "#C2185B"),
                   ("Pink", "#EC6FA6"), ("Brown", "#8D5524"), ("Slate", "#64748B"), ("Black", "#111318")),
          pair_bg="#F5F6F9", pair_fg="#1E3A8A"),
    Theme(id="paper", name="Paper", bg="#F3ECD9", panel="#FBF6E9", grid_kind="hatch",
          grid_color="rgba(90,60,30,.10)", glow=False, handle="#1E1B16",
          chroma=("rgba(35,70,184,.75)", "rgba(200,32,47,.75)"), peak="#1E1B16", unlit="rgba(60,40,20,.10)",
          bracket="rgba(60,40,20,.4)", handle_font="serif", code_font="mono",
          palette=(("Navy", "#1F3A6B"), ("Oxblood", "#7A1F2B"), ("Forest", "#23573A"), ("Plum", "#6B2A6E"),
                   ("Teal", "#1F6E73"), ("Sepia", "#6B4A2B"), ("Slate", "#55606E"), ("Crimson", "#C0272F"),
                   ("Royal", "#2F55C8"), ("Olive", "#6B7022"), ("Ochre", "#B07A12"), ("Indigo", "#4A2F9A"),
                   ("Moss", "#4F8A2B"), ("Rust", "#B5501F"), ("Charcoal", "#232323"), ("Rose", "#B8426E")),
          pair_bg="#F3ECD9", pair_fg="#1F3A6B", ink_dark="#1E1B16", ink_light="#FBF6E9"),
    Theme(id="blueprint", name="Blueprint", bg="#0F3A68", panel="#164A80", grid_kind="grid",
          grid_color="rgba(255,255,255,.14)", glow=False, handle="#F4F8FF",
          chroma=("rgba(143,211,255,.85)", "rgba(255,158,207,.85)"), peak="#FFFFFF", unlit="rgba(255,255,255,.12)",
          bracket="rgba(255,255,255,.45)", handle_font="mono", code_font="mono",
          palette=(("White", "#F4F8FF"), ("Silver", "#B9C6D8"), ("Sky", "#8FD3FF"), ("Cyan", "#3FE0E8"),
                   ("Teal", "#2EC4B6"), ("Mint", "#8DF5B5"), ("Lime", "#C6F25A"), ("Yellow", "#FFE45E"),
                   ("Sand", "#E9D7A5"), ("Amber", "#FFB547"), ("Orange", "#FF8A4C"), ("Coral", "#FF6B6B"),
                   ("Pink", "#FF9ECF"), ("Peach", "#FFC9A3"), ("Lilac", "#C9A7FF"), ("Violet", "#9D8CFF")),
          pair_bg="#0F3A68", pair_fg="#F4F8FF", ink_dark="#0F3A68"),
    Theme(id="synthwave", name="Synthwave", bg="#1A0B2E", panel="#2A1347", grid_kind="horizon",
          grid_color="rgba(255,90,200,.22)", glow=True, handle="#FFE9FF",
          chroma=("rgba(0,229,255,.8)", "rgba(255,214,0,.8)"), peak="#FFFFFF", unlit="rgba(255,255,255,.09)",
          bracket="rgba(255,200,255,.4)", handle_font="retro", code_font="mono",
          palette=(("Hot pink", "#FF3CAC"), ("Orchid", "#E040FB"), ("Lavender", "#C3A6FF"), ("Periwinkle", "#7C8CFF"),
                   ("Sky", "#4FC3F7"), ("Cyan", "#18FFFF"), ("Mint", "#64FFDA"), ("Lime", "#B2FF59"),
                   ("Yellow", "#FFEA00"), ("Gold", "#FFC400"), ("Tangerine", "#FF9100"), ("Coral", "#FF6E6E"),
                   ("Red", "#FF1744"), ("Peach", "#FFD3B6"), ("Rose", "#FF9ACD"), ("White", "#FFFFFF")),
          pair_bg="#1A0B2E", pair_fg="#FF3CAC", ink_dark="#1A0B2E"),
    Theme(id="terminal", name="Terminal", bg="#0C0C0C", panel="#171717", grid_kind="scanlines",
          grid_color="rgba(255,255,255,.05)", glow=True, handle="#E6E6E6",
          chroma=("rgba(0,255,255,.7)", "rgba(255,0,255,.7)"), peak="#FFFFFF", unlit="rgba(255,255,255,.09)",
          bracket="rgba(255,255,255,.35)", handle_font="mono", code_font="mono",
          palette=(("Red", "#FF5555"), ("Orange", "#FFB86C"), ("Yellow", "#F1FA8C"), ("Lime", "#A6E22E"),
                   ("Green", "#50FA7B"), ("Teal", "#2AC3A2"), ("Cyan", "#8BE9FD"), ("Blue", "#61AFEF"),
                   ("Indigo", "#7C83FD"), ("Purple", "#BD93F9"), ("Magenta", "#FF79C6"), ("Pink", "#FFB3D9"),
                   ("Tan", "#C89F6D"), ("Gray", "#9DA5B4"), ("White", "#F8F8F2"), ("Amber", "#FFC857")),
          pair_bg="#0C0C0C", pair_fg="#50FA7B", ink_dark="#0C0C0C"),
    Theme(id="arcade", name="Arcade", bg="#101030", panel="#1C1C4A", grid_kind="pixels",
          grid_color="rgba(255,255,255,.35)", glow=False, handle="#FFFFFF",
          chroma=("#FF004D", "#29ADFF"), peak="#FFFFFF", unlit="rgba(255,255,255,.11)",
          bracket="rgba(255,255,255,.45)", handle_font="pixel", code_font="pixel",
          palette=(("Red", "#FF004D"), ("Orange", "#FFA300"), ("Yellow", "#FFEC27"), ("Green", "#00E436"),
                   ("Blue", "#29ADFF"), ("Lavender", "#9C8CD8"), ("Pink", "#FF77A8"), ("Peach", "#FFCCAA"),
                   ("Cream", "#FFF1E8"), ("Silver", "#C2C3C7"), ("Brown", "#C2683C"), ("Plum", "#B03A78"),
                   ("Forest", "#1FA35A"), ("Cyan", "#00F5FF"), ("Purple", "#B65CFF"), ("Lime", "#A8E61D")),
          pair_bg="#101030", pair_fg="#FFEC27", ink_dark="#101030"),
    Theme(id="stealth", name="Stealth", bg="#2B2E26", panel="#3A3E33", grid_kind="crosses",
          grid_color="rgba(220,230,200,.13)", glow=False, handle="#ECE9DA",
          chroma=("rgba(255,140,0,.8)", "rgba(120,200,255,.8)"), peak="#FFFFFF", unlit="rgba(236,233,218,.10)",
          bracket="rgba(236,233,218,.4)", handle_font="stencil", code_font="mono",
          palette=(("Blaze", "#FF6A13"), ("Safety yellow", "#FFD300"), ("Signal red", "#E5322D"), ("Lime", "#9BE22D"),
                   ("Mint", "#7FE7C4"), ("Sky", "#7FC8F8"), ("Cobalt", "#4D7CFE"), ("Violet", "#A98BFF"),
                   ("Pink", "#FF8FC8"), ("Sand", "#D9C9A3"), ("Khaki", "#B8B07A"), ("Rust", "#C8642D"),
                   ("Teal", "#2FB5A5"), ("Ivory", "#F2EFE3"), ("Steel", "#9AA7B0"), ("Amber", "#FFB000")),
          pair_bg="#2B2E26", pair_fg="#FFD300", ink_dark="#2B2E26"),
)
THEMES: dict[str, Theme] = {t.id: t for t in THEMES_LIST}


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
