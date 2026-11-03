"""Render themes. A theme changes how a badge looks, never which bits it shows.

Two badges can only be compared when they use the same theme, so pick one per deployment.
Each theme has 16 named colors; a color feature (frame, visor, trim, status) picks one by index.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    bg: str            # card background
    panel: str         # head fill
    grid_kind: str     # background pattern: grid, dots or hatch
    grid_color: str
    glow: bool         # neon glow (blur filter)
    handle: str        # handle text
    chroma: tuple[str, str]  # glitch split colors
    peak: str          # top lit segment of each signal bar
    unlit: str         # unlit bar and hex segments
    off: str           # unset dots
    bracket: str       # detail group corner brackets
    handle_font: str   # cyber, mono or serif
    palette: tuple[tuple[str, str], ...]
    pair_bg: str
    pair_fg: str

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(n for n, _ in self.palette)

    def color(self, i: int) -> str:
        return self.palette[i & 15][1]


CYBERPUNK = Theme(
    id="cyberpunk", name="Cyberpunk", bg="#0A0913", panel="#16132C", grid_kind="grid", grid_color="rgba(120,140,255,.12)",
    glow=True, handle="#F4F7FF", chroma=("rgba(0,229,255,.8)", "rgba(255,43,241,.8)"), peak="#FFFFFF",
    unlit="rgba(255,255,255,.07)", off="rgba(255,255,255,.08)", bracket="rgba(255,255,255,.35)", handle_font="cyber",
    palette=(("Hot pink", "#FF2E88"), ("Magenta", "#FF2BF1"), ("Violet", "#B04DFF"), ("Ultraviolet", "#6E5BFF"),
             ("Electric blue", "#2F7BFF"), ("Cyan", "#00E5FF"), ("Aqua", "#00FFC3"), ("Neon green", "#39FF14"),
             ("Acid", "#C6FF00"), ("Yellow", "#FFF200"), ("Amber", "#FFB000"), ("Orange", "#FF6A00"),
             ("Red", "#FF2A3D"), ("Rose", "#FF8FB8"), ("Ice", "#A8E6FF"), ("White", "#F4F7FF")),
    pair_bg="#0A0913", pair_fg="#00E5FF",
)

DAYLIGHT = Theme(
    id="daylight", name="Daylight", bg="#F5F6F9", panel="#FFFFFF", grid_kind="dots", grid_color="rgba(30,40,70,.16)",
    glow=False, handle="#14161C", chroma=("rgba(27,163,198,.85)", "rgba(194,24,91,.85)"), peak="#14161C",
    unlit="rgba(20,24,40,.08)", off="rgba(20,24,40,.10)", bracket="rgba(20,24,40,.35)", handle_font="cyber",
    palette=(("Red", "#D7263D"), ("Orange", "#F26419"), ("Amber", "#E3A008"), ("Lime", "#7CB518"),
             ("Green", "#2E9E44"), ("Teal", "#0F8B8D"), ("Cyan", "#1BA3C6"), ("Blue", "#2563EB"),
             ("Navy", "#1E3A8A"), ("Indigo", "#5B4BD8"), ("Purple", "#8E3FC0"), ("Magenta", "#C2185B"),
             ("Pink", "#EC6FA6"), ("Brown", "#8D5524"), ("Slate", "#64748B"), ("Black", "#111318")),
    pair_bg="#F5F6F9", pair_fg="#1E3A8A",
)

PAPER = Theme(
    id="paper", name="Paper", bg="#F3ECD9", panel="#FBF6E9", grid_kind="hatch", grid_color="rgba(90,60,30,.10)",
    glow=False, handle="#1E1B16", chroma=("rgba(35,70,184,.75)", "rgba(200,32,47,.75)"), peak="#1E1B16",
    unlit="rgba(60,40,20,.09)", off="rgba(60,40,20,.12)", bracket="rgba(60,40,20,.4)", handle_font="serif",
    palette=(("Navy", "#1F3A6B"), ("Oxblood", "#7A1F2B"), ("Forest", "#23573A"), ("Plum", "#6B2A6E"),
             ("Teal", "#1F6E73"), ("Sepia", "#6B4A2B"), ("Slate", "#55606E"), ("Crimson", "#C0272F"),
             ("Royal", "#2F55C8"), ("Olive", "#6B7022"), ("Ochre", "#B07A12"), ("Indigo", "#4A2F9A"),
             ("Moss", "#4F8A2B"), ("Rust", "#B5501F"), ("Charcoal", "#232323"), ("Rose", "#B8426E")),
    pair_bg="#F3ECD9", pair_fg="#1F3A6B",
)

BLUEPRINT = Theme(
    id="blueprint", name="Blueprint", bg="#0F3A68", panel="#164A80", grid_kind="grid", grid_color="rgba(255,255,255,.14)",
    glow=False, handle="#F4F8FF", chroma=("rgba(143,211,255,.85)", "rgba(255,158,207,.85)"), peak="#FFFFFF",
    unlit="rgba(255,255,255,.10)", off="rgba(255,255,255,.13)", bracket="rgba(255,255,255,.45)", handle_font="mono",
    palette=(("White", "#F4F8FF"), ("Silver", "#B9C6D8"), ("Sky", "#8FD3FF"), ("Cyan", "#3FE0E8"),
             ("Teal", "#2EC4B6"), ("Mint", "#8DF5B5"), ("Lime", "#C6F25A"), ("Yellow", "#FFE45E"),
             ("Sand", "#E9D7A5"), ("Amber", "#FFB547"), ("Orange", "#FF8A4C"), ("Coral", "#FF6B6B"),
             ("Pink", "#FF9ECF"), ("Peach", "#FFC9A3"), ("Lilac", "#C9A7FF"), ("Violet", "#9D8CFF")),
    pair_bg="#0F3A68", pair_fg="#F4F8FF",
)

THEMES: dict[str, Theme] = {t.id: t for t in (CYBERPUNK, DAYLIGHT, PAPER, BLUEPRINT)}


def get(theme: str | Theme) -> Theme:
    if isinstance(theme, Theme):
        return theme
    try:
        return THEMES[theme]
    except KeyError:
        raise ValueError(f"unknown theme {theme!r}; choose from {', '.join(THEMES)}") from None
