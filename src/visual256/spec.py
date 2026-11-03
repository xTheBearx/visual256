"""The Netrunner ID bit layout: how a checksum becomes badge features.

Development version 0.1: the layout and drawings may still change before the first release.

Step 1, mixing. The checksum is never drawn directly. Each 256-bit badge shows
    SHA-256(MIX_TAG || part number || whole checksum)
so flipping any single bit of the checksum changes every part of every badge (about half of all
badge bits). Two different checksums give different badges unless SHA-256 collides. The picture
is a fingerprint: it cannot be turned back into the checksum (the BIP-39 spoken backup can).

Step 2, drawing. The 256 mixed bits are read most significant first:

    bits    0-88   headline features (see HEADLINE_FIELDS)
    bits   89-103  5 signal bars, 3 bits each (1-8 lit segments)
    bits  104-115  3 chip colors, 4 bits each
    bits  116-175  12 printed characters, 5 bits each, 4 per chip
    bits  176-255  10 detail cells, 8 bits each (cell k is badge byte 22 + k), drawn as tiles,
                   gems, hex pairs or arrows (chosen by the `display` field)

Every badge bit is drawn: `encode(decode(b)) == b` for every 32-byte value.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, fields as dc_fields

from . import bip39
from .bits import BitReader, BitWriter, to_alphabet

SPEC_VERSION = "0.1"
MIX_TAG = b"visual256/netrunner/0.1"

# (name, bits, label, what it controls)
HEADLINE_FIELDS: tuple[tuple[str, int, str, str], ...] = (
    ("theme", 3, "Theme", "8 looks: background, pattern, fonts and the 16-color palette"),
    ("gradient", 2, "Background gradient", "left to right, top to bottom, diagonal or radial"),
    ("gtone", 1, "Gradient tone", "theme color into the hue, or the hue from light to dark"),
    ("tint", 3, "Gradient color", "red, orange, yellow, green, cyan, blue, violet or magenta"),
    ("layout", 3, "Card layout", "8 arrangements of face, handle, bars, chips and detail"),
    ("display", 2, "Detail display", "tiles, gems, hex pairs or arrows"),
    ("corners", 2, "Frame corners", "which corners of the frame are cut"),
    ("framestyle", 2, "Frame style", "single, double, dashed or corner brackets"),
    ("barstyle", 2, "Bar style", "segmented, solid, lollipops or chevrons"),
    ("frame", 4, "Frame color", "frame and dividers"),
    ("visor", 4, "Visor color", "visor, lit windows, eyes, blooms, fabric, toppings or print"),
    ("trim", 4, "Trim color", "outlines, roofs, doors, mouths, marks and decal"),
    ("accent", 4, "Accent color", "signal bars and handle effects"),
    ("subject", 6, "Subject", "3 android heads; 10 buildings, animals, vehicles or plants; 8 furniture, 8 foods or 5 sports gear"),
    ("vstyle", 3, "Subject detail A", "visor, windows, eyes, vehicle windows, blooms, fabric, toppings or print (8 each)"),
    ("grille", 3, "Subject detail B", "mouth, door, nose, trail, pot, companion object, serving or gear (8 each)"),
    ("mod", 2, "Subject detail C", "head mod, roof add-on, accessory, vehicle add-on, visitor, wall item, topper or motion (4 each)"),
    ("decal", 4, "Subject symbol", "decal, sign, forehead mark, emblem, pot label, plaque, food label or team badge (16 symbols)"),
    ("cheek", 2, "Subject detail D", "cheeks, grounds, markings, livery, ground extras, floor, side item or pitch (4 each)"),
    ("status", 4, "Status word", "one of 16 words"),
    ("scolor", 4, "Status color", "status chip"),
    ("hstyle", 3, "Handle style", "clean, split, vertical split, slice, inverted, underline, boxed or shadow"),
    ("word1", 11, "Handle word 1", "BIP-39 word, 1 of 2048"),
    ("word2", 11, "Handle word 2", "BIP-39 word, 1 of 2048"),
)
HEADLINE_BITS = sum(f[1] for f in HEADLINE_FIELDS)
N_BARS = 5
assert HEADLINE_BITS == 89 and HEADLINE_BITS + N_BARS * 3 == 104

THEME_IDS = ("cyberpunk", "daylight", "paper", "blueprint", "candy", "mint", "ember", "jungle")
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
GRADIENTS = ("left to right", "top to bottom", "diagonal", "radial")
BAR_STYLES = ("segmented", "solid", "lollipops", "chevrons")
DISPLAYS = ("tiles", "gems", "hex pairs", "arrows")
ARROW_DIRS = ("up", "up-right", "right", "down-right", "down", "down-left", "left", "up-left")
GRADIENT_TONES = ("theme color into the hue", "light to dark")
HEAD_SHAPES = ("dome", "bucket", "skull")
BUILDINGS = ("house", "skyscraper", "castle", "pagoda", "observatory", "lighthouse", "factory", "temple",
             "windmill", "needle tower")
ANIMALS = ("cat", "dog", "rabbit", "fox", "owl", "mouse", "frog", "penguin", "lion", "panda")
VEHICLES = ("car", "bus", "bicycle", "locomotive", "sailboat", "submarine", "helicopter", "hot-air balloon",
            "rocket", "flying saucer")
PLANTS = ("pine", "oak", "palm", "cactus", "sunflower", "bonsai", "fern", "bamboo", "cherry blossom", "lotus")
FURNITURE = ("armchair", "sofa", "bed", "bookshelf", "grandfather clock", "floor lamp", "piano", "bathtub")
FOODS = ("pizza slice", "burger", "ice cream cone", "cupcake", "donut", "popsicle", "ramen bowl", "hot dog")
SPORTS = ("soccer ball", "tennis racket", "skateboard", "bowling pin", "boxing glove")
SUBJECT_KINDS = (("face", HEAD_SHAPES), ("building", BUILDINGS), ("animal", ANIMALS), ("vehicle", VEHICLES),
                 ("plant", PLANTS), ("furniture", FURNITURE), ("food", FOODS), ("sports", SPORTS))
SUBJECT_START: dict[str, int] = {}
_n = 0
for _kind, _names in SUBJECT_KINDS:
    SUBJECT_START[_kind] = _n
    _n += len(_names)
SUBJECTS = tuple(f"android, {s} head" for s in HEAD_SHAPES) + BUILDINGS + ANIMALS + VEHICLES + PLANTS + FURNITURE + FOODS + SPORTS
assert len(SUBJECTS) == _n == 64
WINDOWS = ("square grid", "portholes", "arches", "bands", "strips", "picture window", "diamonds", "checker lights")
DOORS = ("plain door", "arched door", "double door", "round door", "garage door", "gate", "glass door", "awning door")
ROOFS = ("antenna", "flag", "chimney", "satellite dish")
GROUNDS = ("steps", "fence", "bushes", "lamp posts")
EYES = ("dots", "glossy", "sleepy", "happy", "stern", "slit", "sparkle", "hearts")
SNOUTS = ("button nose", "round nose", "heart nose", "open mouth", "tongue out", "buck teeth", "cat mouth", "fangs")
ACCESSORIES = ("collar and tag", "bow", "bow tie", "scarf")
# Animals that skip the bow tie (accessory 2) so they differ from their closest look-alike
# (panda vs cat, owl vs fox); they show no accessory instead.
NO_BOW_TIE = ("owl", "panda")
MARKINGS = ("whiskers", "spots", "blush", "stripes")
TRAILS = ("smoke puffs", "flames", "speed lines", "sparks", "bubbles", "vapor trail", "stars", "zigzag")
VEHICLE_MODS = ("antenna", "flag", "siren", "fin")
LIVERIES = ("stripe", "double stripe", "checker band", "zigzag stripe")
BLOOMS = ("berries", "blossoms", "stars", "hearts", "apples", "lemons", "sparkles", "bells")
POTS = ("terracotta pot", "square planter", "round bowl", "tall vase", "wooden crate", "soil mound", "glass jar", "teacup")
VISITORS = ("butterfly", "bee", "bird", "ladybug")
GROUND_EXTRAS = ("grass tufts", "pebbles", "fallen petals", "seedlings")
FABRICS = ("stripes", "bands", "polka dots", "checks", "diamonds", "zigzag", "plaid", "scales")
COMPANIONS = ("cat", "book stack", "potted plant", "teapot", "radio", "globe", "candle", "gift box")
WALL_ITEMS = ("picture frame", "round mirror", "window", "bunting")
FLOORS = ("oval rug", "floorboards", "checker tiles", "fringed rug")
TOPPINGS = ("sprinkles", "seeds", "dots", "stars", "hearts", "drizzle", "chips", "rings")
SERVINGS = ("round plate", "wooden board", "napkin", "tray", "cake stand", "picnic cloth", "leaf", "bento box")
TOPPERS = ("cherry", "candle", "flag pick", "mint leaf")
SIDES = ("fork", "spoon", "chopsticks", "cup")
GEAR = ("whistle", "water bottle", "trophy", "medal", "stopwatch", "cone", "cap", "corner flag")
MOTIONS = ("speed lines", "sparks", "stars", "dust puffs")
PITCHES = ("grass", "court lines", "wood floor", "ice")


def subject_kind(subject: int) -> str:
    for kind, names in SUBJECT_KINDS:
        if subject < SUBJECT_START[kind] + len(names):
            return kind
    raise ValueError(subject)
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


def mix(checksum: bytes) -> list[bytes]:
    """Badge bits for a checksum: one 32-byte value per 256-bit part of the checksum.

    Every part depends on the whole checksum, so a single flipped input bit changes all badges.
    """
    if len(checksum) not in (32, 64):
        raise ValueError("visual256 draws 256-bit (32-byte) or 512-bit (64-byte) checksums")
    return [hashlib.sha256(MIX_TAG + bytes([i]) + checksum).digest() for i in range(len(checksum) // 32)]


@dataclass(frozen=True)
class Features:
    """Every feature of one Netrunner ID badge. Together they hold exactly 256 bits."""

    theme: int
    gradient: int
    gtone: int
    tint: int
    layout: int
    display: int
    corners: int
    framestyle: int
    barstyle: int
    frame: int
    visor: int
    trim: int
    accent: int
    subject: int
    vstyle: int
    grille: int
    mod: int
    decal: int
    cheek: int
    status: int
    scolor: int
    hstyle: int
    word1: int
    word2: int
    bars: tuple[int, ...]    # 5 values, 0-7 (drawn as 1-8 lit segments)
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


def decode(bits: bytes) -> Features:
    """Turn 32 badge bytes (the output of `mix`) into features."""
    if len(bits) != 32:
        raise ValueError("a badge encodes exactly 32 bytes")
    r = BitReader(bits)
    head = {name: r.read(n) for name, n, _, _ in HEADLINE_FIELDS}
    bars = tuple(r.read(3) for _ in range(N_BARS))
    chips = tuple(r.read(4) for _ in range(3))
    chars = tuple(r.read(5) for _ in range(12))
    cells = tuple(r.read(8) for _ in range(10))
    return Features(**head, bars=bars, chips=chips, chars=chars, cells=cells)


def encode(f: Features) -> bytes:
    """Inverse of decode: rebuild the exact 32 badge bytes from a badge's features."""
    if (len(f.bars), len(f.chips), len(f.chars), len(f.cells)) != (N_BARS, 3, 12, 10):
        raise ValueError(f"bars, chips, chars and cells must have {N_BARS}, 3, 12 and 10 entries")
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


def _subject_values(f: Features) -> dict:
    kind = subject_kind(f.subject)
    if kind == "face":
        return {"vstyle": VISORS[f.vstyle], "grille": MOUTHS[f.grille], "mod": MODS[f.mod], "cheek": CHEEKS[f.cheek]}
    if kind == "building":
        return {"vstyle": WINDOWS[f.vstyle], "grille": DOORS[f.grille], "mod": ROOFS[f.mod], "cheek": GROUNDS[f.cheek]}
    if kind == "vehicle":
        return {"vstyle": WINDOWS[f.vstyle], "grille": TRAILS[f.grille], "mod": VEHICLE_MODS[f.mod], "cheek": LIVERIES[f.cheek]}
    if kind == "plant":
        return {"vstyle": BLOOMS[f.vstyle], "grille": POTS[f.grille], "mod": VISITORS[f.mod], "cheek": GROUND_EXTRAS[f.cheek]}
    if kind == "furniture":
        return {"vstyle": FABRICS[f.vstyle], "grille": COMPANIONS[f.grille], "mod": WALL_ITEMS[f.mod], "cheek": FLOORS[f.cheek]}
    if kind == "food":
        return {"vstyle": TOPPINGS[f.vstyle], "grille": SERVINGS[f.grille], "mod": TOPPERS[f.mod], "cheek": SIDES[f.cheek]}
    if kind == "sports":
        return {"vstyle": FABRICS[f.vstyle], "grille": GEAR[f.grille], "mod": MOTIONS[f.mod], "cheek": PITCHES[f.cheek]}
    animal = ANIMALS[f.subject - SUBJECT_START["animal"]]
    accessory = "no accessory" if f.mod == 2 and animal in NO_BOW_TIE else ACCESSORIES[f.mod]
    return {"vstyle": EYES[f.vstyle], "grille": SNOUTS[f.grille], "mod": accessory, "cheek": MARKINGS[f.cheek]}


def describe_cells(f: Features, names: tuple[str, ...]) -> str:
    if f.display == 0:
        return ", ".join(f"{names[c >> 4]} {SYMBOLS[c & 15]}" for c in f.cells)
    if f.display == 1:
        return ", ".join(f"{names[c >> 4]} {GEM_FILLS[c & 3]} {GEM_SHAPES[(c >> 2) & 3]}" for c in f.cells)
    if f.display == 3:
        return ", ".join(f"{names[(c >> 1) & 15]} {ARROW_DIRS[c >> 5]}{' outline' if c & 1 else ''}" for c in f.cells)
    return " ".join(f"{c:02X}" for c in f.cells)


def describe(f: Features, palette_names: tuple[str, ...], theme_name: str = "",
             tint_names: tuple[str, ...] = ("red", "orange", "yellow", "green", "cyan", "blue", "violet", "magenta"),
             ) -> list[tuple[str, str, str]]:
    """Plain-language readout: (bit range, label, value) for every feature."""
    n = palette_names
    values = {
        "theme": theme_name or THEME_IDS[f.theme],
        "gradient": GRADIENTS[f.gradient], "gtone": GRADIENT_TONES[f.gtone], "tint": tint_names[f.tint],
        "layout": f"{f.layout} · {LAYOUTS[f.layout]}",
        "display": DISPLAYS[f.display], "corners": CORNERS[f.corners], "framestyle": FRAME_STYLES[f.framestyle],
        "barstyle": BAR_STYLES[f.barstyle],
        "frame": n[f.frame], "visor": n[f.visor], "trim": n[f.trim], "accent": n[f.accent], "scolor": n[f.scolor],
        "subject": SUBJECTS[f.subject], "decal": SYMBOLS[f.decal],
        **_subject_values(f),
        "status": STATUS_WORDS[f.status],
        "hstyle": HANDLE_STYLES[f.hstyle],
        "word1": f"{f.words[0]} (#{f.word1 + 1})", "word2": f"{f.words[1]} (#{f.word2 + 1})",
    }
    out = []
    pos = 0
    for name, bits, label, _ in HEADLINE_FIELDS:
        out.append((f"{pos}-{pos + bits - 1}", label, values[name]))
        pos += bits
    out.append((f"{pos}-103", "Signal bars", " ".join(str(v + 1) for v in f.bars)))
    out.append(("104-115", "Chip colors", ", ".join(n[c] for c in f.chips)))
    out.append(("116-175", "Characters", " ".join(f.char_groups)))
    out.append(("176-255", f"Detail cells ({DISPLAYS[f.display]})", describe_cells(f, n)))
    return out
