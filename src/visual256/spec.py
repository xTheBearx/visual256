"""The Netrunner ID bit layout (spec v2): how 256 bits become badge features.

Bits are read most significant first.

    bits    0-79   headline features (see HEADLINE_FIELDS): theme, layout, colors, face,
                   status, handle style and two BIP-39 handle words
    bits   80-103  8 signal bars, 3 bits each (1-8 lit segments)
    bits  104-115  3 chip colors, 4 bits each
    bits  116-175  12 printed characters, 5 bits each, 4 per chip
    bits  176-255  10 detail cells, 8 bits each (cell k is byte 22 + k), drawn as tiles,
                   gems, hex pairs or arrows (chosen by the `display` field)

Every bit is drawn, so `encode(decode(b)) == b` for every 32-byte input.
Spec v2 moves bits out of small marks into larger features: fewer, bigger detail elements
that each carry more bits through color, shape and fill.
"""

from __future__ import annotations

from dataclasses import dataclass, fields as dc_fields

from . import bip39
from .bits import BitReader, BitWriter, to_alphabet

SPEC_VERSION = 2

# (name, bits, label, what it controls)
HEADLINE_FIELDS: tuple[tuple[str, int, str, str], ...] = (
    ("theme", 3, "Theme", "8 looks: background, fonts and the 16-color palette"),
    ("layout", 3, "Card layout", "8 arrangements of face, handle, bars, chips and detail"),
    ("display", 2, "Detail display", "tiles, gems, hex pairs or arrows"),
    ("corners", 2, "Frame corners", "which corners of the frame are cut"),
    ("framestyle", 2, "Frame style", "single, double, dashed or corner brackets"),
    ("frame", 4, "Frame color", "frame and dividers"),
    ("visor", 4, "Visor color", "visor"),
    ("trim", 4, "Trim color", "head outline, mods, mouth, cheek marks and decal"),
    ("accent", 4, "Accent color", "signal bars and handle effects"),
    ("shape", 3, "Head shape", "round, angular, boxy, dome, capsule, bucket, shield or skull"),
    ("vstyle", 3, "Visor style", "band, twin-lens, slit, mono-eye, goggles, chevron, triple-lens or grid"),
    ("grille", 3, "Mouth", "vents, teeth, dots, LED, zigzag, speaker, fangs or stitches"),
    ("mod", 2, "Head mod", "antenna, ear discs, cable or fin"),
    ("decal", 4, "Forehead decal", "one of 16 symbols"),
    ("cheek", 2, "Cheek marks", "stripes, dots, circuit or bolts"),
    ("status", 4, "Status word", "one of 16 words"),
    ("scolor", 4, "Status color", "status chip"),
    ("rank", 2, "Rank", "1 to 4 chevrons on the status chip"),
    ("hstyle", 3, "Handle style", "clean, split, vertical split, slice, inverted, underline, boxed or shadow"),
    ("word1", 11, "Handle word 1", "BIP-39 word, 1 of 2048"),
    ("word2", 11, "Handle word 2", "BIP-39 word, 1 of 2048"),
)
HEADLINE_BITS = sum(f[1] for f in HEADLINE_FIELDS)
assert HEADLINE_BITS == 80
BARS_OFFSET, CHIPS_OFFSET, CHARS_OFFSET, DETAIL_OFFSET = 80, 104, 116, 176

THEME_IDS = ("cyberpunk", "daylight", "paper", "blueprint", "synthwave", "terminal", "arcade", "stealth")
LAYOUTS = (
    "face left, stacked",
    "face right, stacked",
    "face center, bars on top",
    "face left, grid",
    "face right, grid",
    "banner on top, face left",
    "banner at bottom, face right",
    "face center, detail on top",
)
CORNERS = ("top-left and bottom-right cut", "top-right and bottom-left cut", "all four cut", "both top corners cut")
FRAME_STYLES = ("single", "double", "dashed", "corner brackets")
DISPLAYS = ("tiles", "gems", "hex pairs", "arrows")
ARROW_DIRS = ("up", "up-right", "right", "down-right", "down", "down-left", "left", "up-left")
HEAD_SHAPES = ("round", "angular", "boxy", "dome", "capsule", "bucket", "shield", "skull")
VISORS = ("band", "twin-lens", "slit", "mono-eye", "goggles", "chevron", "triple-lens", "grid")
MOUTHS = ("vents", "teeth", "dots", "LED", "zigzag", "speaker", "fangs", "stitches")
MODS = ("antenna", "ear discs", "cable", "fin")
CHEEKS = ("stripes", "dots", "circuit", "bolts")
HANDLE_STYLES = ("clean", "horizontal split", "vertical split", "slice shift", "inverted", "underline", "boxed", "shadow")
SYMBOLS = ("circle", "square", "triangle", "diamond", "star", "plus", "saltire", "heart",
           "crescent", "sun", "drop", "bolt", "hexagon", "ring", "arrow", "clover")
STATUS_WORDS = ("ONLINE", "GHOST", "ROGUE", "SYNCED", "ROOTED", "DARK", "LIVE", "BURNED",
                "CLEAN", "HOT", "ZERO", "LOCKED", "SPOOFED", "MIRROR", "IDLE", "VOID")
GEM_SHAPES = ("circle", "square", "triangle", "diamond")
GEM_FILLS = ("solid", "outline", "dotted", "half")


@dataclass(frozen=True)
class Features:
    """Every feature of one Netrunner ID badge. Together they hold exactly 256 bits."""

    theme: int
    layout: int
    display: int
    corners: int
    framestyle: int
    frame: int
    visor: int
    trim: int
    accent: int
    shape: int
    vstyle: int
    grille: int
    mod: int
    decal: int
    cheek: int
    status: int
    scolor: int
    rank: int
    hstyle: int
    word1: int
    word2: int
    bars: tuple[int, ...]    # 8 values, 0-7 (drawn as 1-8 lit segments)
    chips: tuple[int, ...]   # 3 colors, 0-15
    chars: tuple[int, ...]   # 12 values, 0-31 (alphabet indices)
    cells: tuple[int, ...]   # 10 bytes, 0-255

    @property
    def theme_id(self) -> str:
        return THEME_IDS[self.theme]

    @property
    def words(self) -> tuple[str, str]:
        return bip39.word(self.word1), bip39.word(self.word2)

    @property
    def handle(self) -> str:
        return "·".join(w.upper() for w in self.words)

    @property
    def char_groups(self) -> list[str]:
        return [to_alphabet(self.chars[g * 4:g * 4 + 4]) for g in range(3)]


def decode(data: bytes) -> Features:
    """Turn 32 bytes (one SHA-256 digest, or one half of a SHA-512 digest) into features."""
    if len(data) != 32:
        raise ValueError("a badge encodes exactly 32 bytes")
    r = BitReader(data)
    head = {name: r.read(n) for name, n, _, _ in HEADLINE_FIELDS}
    bars = tuple(r.read(3) for _ in range(8))
    chips = tuple(r.read(4) for _ in range(3))
    chars = tuple(r.read(5) for _ in range(12))
    cells = tuple(r.read(8) for _ in range(10))
    return Features(**head, bars=bars, chips=chips, chars=chars, cells=cells)


def encode(f: Features) -> bytes:
    """Inverse of decode: rebuild the exact 32 bytes from a badge's features."""
    if (len(f.bars), len(f.chips), len(f.chars), len(f.cells)) != (8, 3, 12, 10):
        raise ValueError("bars, chips, chars and cells must have 8, 3, 12 and 10 entries")
    w = BitWriter()
    for name, n, _, _ in HEADLINE_FIELDS:
        w.write(getattr(f, name), n)
    for v in f.bars:
        w.write(v, 3)
    for v in f.chips:
        w.write(v, 4)
    for v in f.chars:
        w.write(v, 5)
    for v in f.cells:
        w.write(v, 8)
    return w.to_bytes()


def with_changes(f: Features, **changes) -> Features:
    """Copy of `f` with some features replaced (for previews, e.g. forcing a layout)."""
    values = {fld.name: getattr(f, fld.name) for fld in dc_fields(f)}
    values.update(changes)
    return Features(**values)


def describe_cells(f: Features, names: tuple[str, ...]) -> str:
    if f.display == 0:
        return ", ".join(f"{names[c >> 4]} {SYMBOLS[c & 15]}" for c in f.cells)
    if f.display == 1:
        return ", ".join(f"{names[c >> 4]} {GEM_FILLS[c & 3]} {GEM_SHAPES[(c >> 2) & 3]}" for c in f.cells)
    if f.display == 3:
        return ", ".join(f"{names[(c >> 1) & 15]} {ARROW_DIRS[c >> 5]}{' outline' if c & 1 else ''}" for c in f.cells)
    return " ".join(f"{c:02X}" for c in f.cells)


def describe(f: Features, palette_names: tuple[str, ...], theme_name: str = "") -> list[tuple[str, str, str]]:
    """Plain-language readout: (bit range, label, value) for every feature."""
    n = palette_names
    values = {
        "theme": theme_name or THEME_IDS[f.theme],
        "layout": f"{f.layout} · {LAYOUTS[f.layout]}",
        "display": DISPLAYS[f.display], "corners": CORNERS[f.corners], "framestyle": FRAME_STYLES[f.framestyle],
        "frame": n[f.frame], "visor": n[f.visor], "trim": n[f.trim], "accent": n[f.accent], "scolor": n[f.scolor],
        "shape": HEAD_SHAPES[f.shape], "vstyle": VISORS[f.vstyle], "grille": MOUTHS[f.grille],
        "mod": MODS[f.mod], "decal": SYMBOLS[f.decal], "cheek": CHEEKS[f.cheek],
        "status": STATUS_WORDS[f.status], "rank": f"{f.rank + 1} chevron{'s' if f.rank else ''}",
        "hstyle": HANDLE_STYLES[f.hstyle],
        "word1": f"{f.words[0]} (#{f.word1 + 1})", "word2": f"{f.words[1]} (#{f.word2 + 1})",
    }
    out = []
    pos = 0
    for name, bits, label, _ in HEADLINE_FIELDS:
        out.append((f"{pos}-{pos + bits - 1}", label, values[name]))
        pos += bits
    out.append(("80-103", "Signal bars", " ".join(str(v + 1) for v in f.bars)))
    out.append(("104-115", "Chip colors", ", ".join(n[c] for c in f.chips)))
    out.append(("116-175", "Characters", " ".join(f.char_groups)))
    out.append(("176-255", f"Detail cells ({DISPLAYS[f.display]})", describe_cells(f, n)))
    return out
