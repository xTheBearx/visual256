"""The Netrunner ID bit layout: how 256 bits become badge features.

Bits are read most significant first. The first 64 bits are headline features (big and
memorable); the remaining 192 bits are detail (signal bars, printed characters and a
detail block whose display type is itself a headline feature).

    bits    0-63   headline features (see FIELDS)
    bits   64-95   8 signal bars, 4 bits each (1-16 lit segments)
    bits  96-175   16 printed characters, 5 bits each, in 4 groups of 4
    bits 176-255   detail block: 4 groups of 20 bits, drawn as dots, shapes,
                   barcode ticks or hex segment digits (chosen by the `display` field)

Every bit is drawn, so `encode(decode(b)) == b` for every 32-byte input.
"""

from __future__ import annotations

from dataclasses import dataclass, fields as dc_fields

from . import bip39
from .bits import ALPHABET, BitReader, BitWriter, to_alphabet

SPEC_VERSION = 1

# (name, bits, label, what it controls)
HEADLINE_FIELDS: tuple[tuple[str, int, str, str], ...] = (
    ("layout", 3, "Card layout", "8 arrangements of face, handle, bars, characters and detail"),
    ("corners", 2, "Frame corners", "which corners of the frame are cut"),
    ("frameline", 1, "Frame line", "single or double frame line"),
    ("display", 2, "Detail display", "dots, shapes, barcode or hex segments"),
    ("frame", 4, "Frame color", "frame, signal bars and printed characters"),
    ("visor", 4, "Visor color", "visor and detail block"),
    ("shape", 2, "Head shape", "round, angular, boxy or dome"),
    ("trim", 4, "Trim color", "head outline, mods and decal"),
    ("vstyle", 2, "Visor style", "band, twin-lens, slit or mono-eye"),
    ("grille", 2, "Grille", "vent, tooth, dot or LED"),
    ("mod", 2, "Head mod", "antenna, ear discs, cable or fin"),
    ("decal", 4, "Forehead decal", "one of 16 symbols"),
    ("status", 4, "Status word", "one of 16 words"),
    ("scolor", 4, "Status color", "status chip"),
    ("glitch", 2, "Handle glitch", "clean, horizontal split, vertical split or slice"),
    ("word1", 11, "Handle word 1", "BIP-39 word, 1 of 2048"),
    ("word2", 11, "Handle word 2", "BIP-39 word, 1 of 2048"),
)
HEADLINE_BITS = sum(f[1] for f in HEADLINE_FIELDS)
BARS_OFFSET, CHARS_OFFSET, DETAIL_OFFSET = 64, 96, 176
assert HEADLINE_BITS == 64

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
DISPLAYS = ("dots", "shapes", "barcode", "hex segments")
HEAD_SHAPES = ("round", "angular", "boxy", "dome")
VISORS = ("band", "twin-lens", "slit", "mono-eye")
GRILLES = ("vent grille", "tooth grille", "dot grille", "LED mouth")
MODS = ("antenna", "ear discs", "cable", "fin")
GLITCHES = ("clean", "horizontal split", "vertical split", "slice shift")
SYMBOLS = ("circle", "square", "triangle", "diamond", "star", "plus", "saltire", "heart",
           "crescent", "sun", "drop", "bolt", "hexagon", "ring", "arrow", "clover")
STATUS_WORDS = ("ONLINE", "GHOST", "ROGUE", "SYNCED", "ROOTED", "DARK", "LIVE", "BURNED",
                "CLEAN", "HOT", "ZERO", "LOCKED", "SPOOFED", "MIRROR", "IDLE", "VOID")
SHAPE_KINDS = ("circle", "square", "triangle", "diamond")
SHAPE_FILLS = ("solid", "outline", "dotted", "half")


@dataclass(frozen=True)
class Features:
    """Every feature of one Netrunner ID badge. Together they hold exactly 256 bits."""

    layout: int
    corners: int
    frameline: int
    display: int
    frame: int
    visor: int
    shape: int
    trim: int
    vstyle: int
    grille: int
    mod: int
    decal: int
    status: int
    scolor: int
    glitch: int
    word1: int
    word2: int
    bars: tuple[int, ...]    # 8 values, 0-15 (drawn as 1-16 lit segments)
    chars: tuple[int, ...]   # 16 values, 0-31 (alphabet indices)
    detail: tuple[int, ...]  # 80 bits, 0 or 1, in 4 groups of 20

    @property
    def words(self) -> tuple[str, str]:
        return bip39.word(self.word1), bip39.word(self.word2)

    @property
    def handle(self) -> str:
        return "·".join(w.upper() for w in self.words)

    @property
    def char_groups(self) -> list[str]:
        return [to_alphabet(self.chars[g * 4:g * 4 + 4]) for g in range(4)]

    def detail_group(self, g: int) -> tuple[int, ...]:
        return self.detail[g * 20:g * 20 + 20]

    def detail_nibbles(self, g: int) -> list[int]:
        bits = self.detail_group(g)
        return [int("".join(map(str, bits[i * 4:i * 4 + 4])), 2) for i in range(5)]

    @property
    def detail_groups(self) -> list[str]:
        """Each 20-bit detail group read as 4 alphabet characters."""
        out = []
        for g in range(4):
            bits = self.detail_group(g)
            out.append("".join(ALPHABET[int("".join(map(str, bits[i * 5:i * 5 + 5])), 2)] for i in range(4)))
        return out


def decode(data: bytes) -> Features:
    """Turn 32 bytes (one SHA-256 digest, or one half of a SHA-512 digest) into features."""
    if len(data) != 32:
        raise ValueError("a badge encodes exactly 32 bytes")
    r = BitReader(data)
    head = {name: r.read(n) for name, n, _, _ in HEADLINE_FIELDS}
    bars = tuple(r.read(4) for _ in range(8))
    chars = tuple(r.read(5) for _ in range(16))
    detail = tuple(r.read(1) for _ in range(80))
    return Features(**head, bars=bars, chars=chars, detail=detail)


def encode(f: Features) -> bytes:
    """Inverse of decode: rebuild the exact 32 bytes from a badge's features."""
    w = BitWriter()
    for name, n, _, _ in HEADLINE_FIELDS:
        w.write(getattr(f, name), n)
    if len(f.bars) != 8 or len(f.chars) != 16 or len(f.detail) != 80:
        raise ValueError("bars, chars and detail must have 8, 16 and 80 entries")
    for v in f.bars:
        w.write(v, 4)
    for v in f.chars:
        w.write(v, 5)
    for v in f.detail:
        w.write(v, 1)
    return w.to_bytes()


def with_changes(f: Features, **changes) -> Features:
    """Copy of `f` with some features replaced (for previews, e.g. forcing a layout)."""
    values = {fld.name: getattr(f, fld.name) for fld in dc_fields(f)}
    values.update(changes)
    return Features(**values)


def describe(f: Features, palette_names: tuple[str, ...]) -> list[tuple[str, str, str]]:
    """Plain-language readout: (bit range, label, value) for every feature."""
    names = palette_names
    values = {
        "layout": f"{f.layout} · {LAYOUTS[f.layout]}",
        "corners": CORNERS[f.corners],
        "frameline": ("single", "double")[f.frameline],
        "display": DISPLAYS[f.display],
        "frame": names[f.frame], "visor": names[f.visor], "trim": names[f.trim], "scolor": names[f.scolor],
        "shape": HEAD_SHAPES[f.shape], "vstyle": VISORS[f.vstyle], "grille": GRILLES[f.grille],
        "mod": MODS[f.mod], "decal": SYMBOLS[f.decal], "status": STATUS_WORDS[f.status],
        "glitch": GLITCHES[f.glitch],
        "word1": f"{f.words[0]} (#{f.word1 + 1})", "word2": f"{f.words[1]} (#{f.word2 + 1})",
    }
    out = []
    pos = 0
    for name, n, label, _ in HEADLINE_FIELDS:
        out.append((f"{pos}-{pos + n - 1}", label, values[name]))
        pos += n
    out.append(("64-95", "Signal bars", " ".join(str(v + 1) for v in f.bars)))
    out.append(("96-175", "Characters", " ".join(f.char_groups)))
    if f.display == 3:
        detail = " ".join("".join(f"{n:X}" for n in f.detail_nibbles(g)) for g in range(4))
    else:
        detail = " ".join(f.detail_groups)
    out.append(("176-255", f"Detail ({DISPLAYS[f.display]})", detail))
    return out
