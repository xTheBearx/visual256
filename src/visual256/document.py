"""The Document style: a flat, print-friendly badge for engineering documents.

It shows the same kind of 256 badge bits as the Netrunner ID style, with its own mixing tag and its
own layout (MSB first):

    bits    0-48   headline features (see DOC_FIELDS)
    bits   49-108  12 printed characters, 5 bits each: a 2-character monogram, then two groups of 5
    bits  109-115  the mark: one larger colored glyph beside the characters (3-bit color, 4-bit shape)
    bit   116      which of the two bottom rows holds the 3-wide bar (the other holds the 2-wide bar)
    bits  117-150  2 horizontal bars, 17 bits each: position in its row (3), style (3), color (3),
                   second color (3), level (4), round or square ends (1)
    bits  151-255  15 colored glyphs, 7 bits each, filling the two rows around the bars

The badge is a fingerprint of the checksum, not a way to carry it. All 256 badge bits are drawn
(`doc_encode(doc_decode(b)) == b`), but they are a SHA-256 mix of the checksum, which cannot be
turned back. The badge also prints the first and last 8 hex digits of the checksum part itself, so
it can be cross-checked against a written checksum.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, fields as dc_fields

from . import bip39
from .bits import BitReader, BitWriter, to_alphabet
from .canvas import Canvas
from .draw import PAIR_GAP, PAIR_H, PAIR_PAD, PAIR_FOOT, PAIR_W, H, S, U, draw_symbol
from .icons import COMPUTER, ENGINEERING, FLAGS, INSIGNIA, INSTRUMENTS, PIECES, SHAPES, SIGNS, SPACE, TOOLS, WEATHER, icon_spec
from .spec import SYMBOLS
from .subjects import _shape, _strokes
from .themes import luminance

DOC_MIX_TAG = b"visual256/document/0.1"
TAU = math.tau

# (name, bits, label, what it controls)
DOC_FIELDS: tuple[tuple[str, int, str, str], ...] = (
    ("theme", 4, "Theme", "16 sheets: paper, ink and the 8-color palette"),
    ("key", 3, "Key color", "subject, monogram box and background motif"),
    ("outline", 3, "Outline", "8 badge outlines"),
    ("motif", 3, "Background motif", "8 large shapes behind the subject, in a pale tint of the key color"),
    ("side", 1, "Subject side", "subject on the left or on the right"),
    ("subject", 7, "Subject", "128 subjects in 11 kinds (listed below)"),
    ("code", 4, "Code word", "one of 16 spelling-alphabet words"),
    ("gstyle", 2, "Glyph style", "plain, square tiles, round tiles or framed"),
    ("word1", 11, "Handle word 1", "BIP-39 word, 1 of 2048"),
    ("word2", 11, "Handle word 2", "BIP-39 word, 1 of 2048"),
)
DOC_HEADLINE_BITS = sum(f[1] for f in DOC_FIELDS)
N_GLYPHS, GLYPH_COLS = 16, 10  # the mark, then 15 glyphs sharing two rows of 10 slots with a 3-wide and a 2-wide bar
# (name, bits) of one bar
BAR_FIELDS = (("pos", 3), ("style", 3), ("color", 3), ("color2", 3), ("level", 4), ("cap", 1))
BAR_BITS = sum(n for _, n in BAR_FIELDS)
assert DOC_HEADLINE_BITS == 49 and DOC_HEADLINE_BITS + 12 * 5 + 1 + 2 * BAR_BITS + N_GLYPHS * 7 == 256

OUTLINES = ("square", "rounded", "top-right and bottom-left cut", "top-left and bottom-right cut", "all four cut",
            "side notches", "rounded outer end", "top and bottom notches")
MOTIFS = ("panel", "diagonal band", "disc", "corner block", "none", "horizontal band", "rings", "hatched panel")
SIDES = ("left", "right")
GLYPH_STYLES = ("plain", "square tiles", "round tiles", "framed")
BAR_STYLES = ("progress", "two-tone", "slider", "striped", "segments", "dashed", "offset pair", "marker")
BAR_CAPS = ("square", "round")
CODE_WORDS = ("ALFA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT", "GOLF", "HOTEL", "INDIA", "JULIETT", "KILO",
              "LIMA", "MIKE", "NOVEMBER", "OSCAR", "PAPA")
# the insignia cog is left out: it looks like the engineering gear
DOC_SUBJECT_KINDS = (("engineering", ENGINEERING), ("tool", TOOLS), ("shape", SHAPES), ("sign", SIGNS),
                     ("instrument", INSTRUMENTS), ("computer", COMPUTER),
                     ("insignia", tuple(n for n in INSIGNIA if n != "cog")), ("piece", PIECES), ("space", SPACE),
                     ("weather", WEATHER), ("flag", FLAGS))
DOC_SUBJECTS = tuple((k, n) for k, names in DOC_SUBJECT_KINDS for n in names)
assert len(DOC_SUBJECTS) == 128


def _p(text: str) -> tuple[tuple[str, str], ...]:
    return tuple(tuple(e.split(":")) for e in text.split("|"))


@dataclass(frozen=True)
class Sheet:
    """One Document theme. `palette` is 8 (name, color) pairs; `grid` is a faint square grid color."""

    id: str
    name: str
    bg: str
    ink: str
    rule: str
    palette: tuple[tuple[str, str], ...]
    grid: str | None = None

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(n for n, _ in self.palette)


# palettes for white and near-white sheets, for mid-tone sheets, and for dark sheets
_LIGHT = _p("Red:#C1272D|Orange:#D55E00|Ochre:#A87900|Green:#2E7D32|Teal:#00838F|Blue:#1565C0|Purple:#6A1B9A|Magenta:#AD1457")
_DEEP = _p("Brick:#9C1F1F|Rust:#B34700|Olive:#6E5200|Green:#1F5F2A|Teal:#00606A|Blue:#0F4C92|Purple:#531680|Wine:#8B0F45")
_DARK = _p("Coral:#FF7B7B|Orange:#FFA94D|Yellow:#FFE066|Green:#8CE99A|Cyan:#66D9E8|Blue:#8EC5FF|Violet:#C0A8FF|Pink:#F9A0C4")
SHEETS = (
    Sheet("drawing", "Drawing sheet", "#FFFFFF", "#14171A", "#14171A", _LIGHT),
    Sheet("blueprint", "Blueprint", "#123E6E", "#EEF5FF", "#9DBDE2", _DARK, grid="#1D4F86"),
    Sheet("whiteprint", "Whiteprint", "#D6E2FA", "#1B3C8C", "#1B3C8C",
          _p("Navy:#1B3C8C|Azure:#0277BD|Teal:#00838F|Violet:#7B2FBF|Red:#C1272D|Orange:#D55E00|Green:#2E7D32|Magenta:#AD1457")),
    Sheet("graph", "Graph paper", "#E2F2CC", "#1C2A20", "#3E6B4A", _LIGHT, grid="#C0DBA6"),
    Sheet("manila", "Manila", "#EAD9AE", "#35260F", "#6B5326", _DEEP),
    Sheet("slate", "Slate", "#242930", "#E8EBEF", "#8A93A0", _DARK),
    Sheet("hivis", "Hi-vis", "#FFD500", "#111111", "#111111",
          _p("Black:#111111|Red:#A8001C|Blue:#0B3C8F|Green:#14531B|Purple:#45107A|Brown:#5A3A22|Teal:#00595E|Grey:#5C6470")),
    Sheet("redline", "Redline", "#6E1620", "#FFF1EC", "#E3A29B", _DARK),
    Sheet("forest", "Forest", "#14452C", "#F0FAEF", "#9CCBA9", _DARK),
    Sheet("plum", "Plum", "#42205F", "#F6EEFF", "#BFA3DB", _DARK),
    Sheet("orange", "Safety orange", "#FF7A1A", "#111111", "#111111",
          _p("Black:#111111|Navy:#0B3C8F|Green:#0F4A1E|Purple:#5E1590|Maroon:#6E0A1E|Brown:#4A2C12|White:#FFFFFF|Teal:#004A52")),
    Sheet("sky", "Sky", "#9FD8F5", "#0E2A3D", "#3D6F8E", _DEEP),
    Sheet("rose", "Rose", "#F7BFCD", "#3A1420", "#9A5566", _DEEP),
    Sheet("mint", "Mint", "#9FE0C0", "#10301F", "#4C8565", _DEEP),
    Sheet("teal", "Teal", "#0B5560", "#EAFBFB", "#8FC9CF", _DARK, grid="#136673"),
    Sheet("lilac", "Lilac", "#CDBBEE", "#261540", "#7A62A6", _DEEP),
)
SHEET_IDS = tuple(s.id for s in SHEETS)
assert len(SHEETS) == 16


def doc_mix(checksum: bytes) -> list[bytes]:
    """Badge bits for a checksum in the Document style: one 32-byte value per 256-bit part."""
    if len(checksum) not in (32, 64):
        raise ValueError("visual256 draws 256-bit (32-byte) or 512-bit (64-byte) checksums")
    return [hashlib.sha256(DOC_MIX_TAG + bytes([i]) + checksum).digest() for i in range(len(checksum) // 32)]


@dataclass(frozen=True)
class DocFeatures:
    """Every feature of one Document badge. Together they hold exactly 256 bits."""

    theme: int
    key: int
    outline: int
    motif: int
    side: int
    subject: int
    code: int
    gstyle: int
    word1: int
    word2: int
    chars: tuple[int, ...]     # 12 values, 0-31 (alphabet indices)
    glyphs: tuple[int, ...]    # 16 values, 0-127: color (3 bits) then shape (4 bits); the first is the mark
    wide: int                  # 0: the top row holds the 3-wide bar, 1: the bottom row does
    bars: tuple[tuple[int, ...], ...]  # top and bottom bar, each (pos, style, color, color2, level, cap)

    @property
    def theme_id(self) -> str:
        return SHEET_IDS[self.theme]

    @property
    def words(self) -> tuple[str, str]:
        return bip39.word(self.word1), bip39.word(self.word2)

    @property
    def handle(self) -> str:
        return "·".join(w.upper() for w in self.words)

    @property
    def monogram(self) -> str:
        return to_alphabet(self.chars[:2])

    @property
    def char_groups(self) -> list[str]:
        return [to_alphabet(self.chars[2:7]), to_alphabet(self.chars[7:])]


def doc_decode(bits: bytes) -> DocFeatures:
    """Turn 32 badge bytes (the output of `doc_mix`) into features."""
    if len(bits) != 32:
        raise ValueError("a badge encodes exactly 32 bytes")
    r = BitReader(bits)
    head = {name: r.read(n) for name, n, _, _ in DOC_FIELDS}
    chars = tuple(r.read(5) for _ in range(12))
    mark = r.read(7)
    wide = r.read(1)
    bars = tuple(tuple(r.read(n) for _, n in BAR_FIELDS) for _ in range(2))
    glyphs = (mark,) + tuple(r.read(7) for _ in range(N_GLYPHS - 1))
    return DocFeatures(**head, chars=chars, glyphs=glyphs, wide=wide, bars=bars)


def doc_encode(f: DocFeatures) -> bytes:
    """Inverse of doc_decode: rebuild the exact 32 badge bytes from a badge's features."""
    if (len(f.chars), len(f.glyphs), len(f.bars)) != (12, N_GLYPHS, 2):
        raise ValueError(f"chars, glyphs and bars must have 12, {N_GLYPHS} and 2 entries")
    w = BitWriter()
    for name, n, _, _ in DOC_FIELDS:
        w.write(getattr(f, name), n)
    for v in f.chars:
        w.write(v, 5)
    w.write(f.glyphs[0], 7)
    w.write(f.wide, 1)
    for bar in f.bars:
        for v, (_, n) in zip(bar, BAR_FIELDS):
            w.write(v, n)
    for v in f.glyphs[1:]:
        w.write(v, 7)
    return w.to_bytes()


def doc_with_changes(f: DocFeatures, **changes) -> DocFeatures:
    values = {fld.name: getattr(f, fld.name) for fld in dc_fields(f)}
    values.update(changes)
    return DocFeatures(**values)


def subject_name(subject: int) -> str:
    kind, name = DOC_SUBJECTS[subject]
    return f"large {name}" if kind == "shape" else name


def bar_width(f: DocFeatures, row: int) -> int:
    """Slots taken by the bar in row 0 (top) or 1 (bottom): 3 in the wide row, 2 in the other."""
    return 3 if f.wide == row else 2


def doc_describe(f: DocFeatures) -> list[tuple[str, str, str]]:
    """Plain-language readout: (bit range, label, value) for every feature."""
    sheet = SHEETS[f.theme]
    n = sheet.names
    values = {
        "theme": sheet.name, "key": n[f.key], "outline": OUTLINES[f.outline], "motif": MOTIFS[f.motif],
        "side": SIDES[f.side], "subject": subject_name(f.subject), "code": CODE_WORDS[f.code],
        "gstyle": GLYPH_STYLES[f.gstyle],
        "word1": f"{f.words[0]} (#{f.word1 + 1})", "word2": f"{f.words[1]} (#{f.word2 + 1})",
    }
    out, pos = [], 0
    for name, bits, label, _ in DOC_FIELDS:
        out.append((f"{pos}-{pos + bits - 1}", label, values[name]))
        pos += bits
    out.append(("49-108", "Characters", " ".join([f.monogram] + f.char_groups)))
    glyph = lambda g: f"{n[g >> 4]} {SYMBOLS[g & 15]}"
    out.append(("109-115", "Mark", glyph(f.glyphs[0])))
    out.append(("116-116", "Wide bar row", ("top", "bottom")[f.wide]))
    for i, (pos, style, color, color2, level, cap) in enumerate(f.bars):
        out.append((f"{117 + i * BAR_BITS}-{116 + (i + 1) * BAR_BITS}", ("Top bar", "Bottom bar")[i],
                    f"{bar_width(f, i)} wide after {pos} glyphs, {BAR_STYLES[style]}, {n[color]} and {n[color2]}, "
                    f"level {level + 1}, {BAR_CAPS[cap]} ends"))
    out.append(("151-255", "Glyphs", ", ".join(glyph(g) for g in f.glyphs[1:])))
    return out


# ---------------------------------------------------------------- drawing (128 x 64 badge units)
X0, Y0, X1, Y1 = 1.0, 1.0, 127.0, 63.0
SUBJECT_W = 55.0   # width of the subject half; the text block takes the rest
BLOCK_W = 65.0     # text block width
CUT, ROUND, NOTCH = 5.5, 8.0, 3.0


def _mix_color(a: str, b: str, k: float) -> str:
    pa, pb = ([int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in (a, b))
    return "#" + "".join(f"{round(x + (y - x) * k):02X}" for x, y in zip(pa, pb))


def _contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _geometry(side: int) -> tuple[float, float, float]:
    """(subject center x, divider x, text block left x)."""
    if side == 0:
        return X0 + SUBJECT_W / 2, X0 + SUBJECT_W, X0 + SUBJECT_W + 2.6
    return X1 - SUBJECT_W / 2, X1 - SUBJECT_W, X0 + 4.5


def outline_path(ctx: Canvas, kind: int, side: int) -> None:
    """One closed path for the badge outline, clockwise from the top-left corner."""
    cut = {2: (0, 1, 0, 1), 3: (1, 0, 1, 0), 4: (1, 1, 1, 1)}.get(kind, (0, 0, 0, 0))  # TL, TR, BR, BL
    rnd = (1, 1, 1, 1) if kind == 1 else (((0, 1, 1, 0) if side else (1, 0, 0, 1)) if kind == 6 else (0, 0, 0, 0))
    inset = [CUT if c else ROUND if r else 0 for c, r in zip(cut, rnd)]
    div, mid, n, r = _geometry(side)[1], (Y0 + Y1) / 2, NOTCH, ROUND
    ctx.begin_path()
    ctx.move_to(X0 + inset[0], Y0)
    if kind == 7:
        ctx.line_to(div - n, Y0)
        ctx.arc(div, Y0, n, math.pi, 0, True)
    ctx.line_to(X1 - inset[1], Y0)
    if rnd[1]:
        ctx.arc(X1 - r, Y0 + r, r, -math.pi / 2, 0)
    else:
        ctx.line_to(X1, Y0 + inset[1])
    if kind == 5:
        ctx.line_to(X1, mid - n)
        ctx.arc(X1, mid, n, -math.pi / 2, -1.5 * math.pi, True)
    ctx.line_to(X1, Y1 - inset[2])
    if rnd[2]:
        ctx.arc(X1 - r, Y1 - r, r, 0, math.pi / 2)
    else:
        ctx.line_to(X1 - inset[2], Y1)
    if kind == 7:
        ctx.line_to(div + n, Y1)
        ctx.arc(div, Y1, n, 0, -math.pi, True)
    ctx.line_to(X0 + inset[3], Y1)
    if rnd[3]:
        ctx.arc(X0 + r, Y1 - r, r, math.pi / 2, math.pi)
    else:
        ctx.line_to(X0, Y1 - inset[3])
    if kind == 5:
        ctx.line_to(X0, mid + n)
        ctx.arc(X0, mid, n, math.pi / 2, -math.pi / 2, True)
    ctx.line_to(X0, Y0 + inset[0])
    if rnd[0]:
        ctx.arc(X0 + r, Y0 + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def _hatch(ctx: Canvas, x0, y0, x1, y1, color: str, step: float, width: float) -> None:
    """Diagonal hatching over the box (the caller clips)."""
    ctx.stroke_style, ctx.line_width, ctx.line_cap = color, width, "butt"
    h, d = y1 - y0, step * 1.3
    ctx.begin_path()
    k = math.ceil((x0 + y0) / d)
    while k * d <= x1 + y1:
        ctx.move_to(k * d - y0, y0)
        ctx.line_to(k * d - y0 - h, y1)
        k += 1
    ctx.stroke()


def _poly(ctx: Canvas, pts) -> None:
    for i, p in enumerate(pts):
        (ctx.line_to if i else ctx.move_to)(*p)
    ctx.close_path()


def _draw_motif(ctx: Canvas, f: DocFeatures, sheet: Sheet, tint: str, cx: float) -> None:
    """Large pale shape behind the subject, clipped to the subject half."""
    x0, x1 = cx - SUBJECT_W / 2, cx + SUBJECT_W / 2
    m = -1 if f.side else 1  # mirror with the subject side
    name = MOTIFS[f.motif]
    ctx.save()
    ctx.begin_path()
    ctx.rect(x0, 0, SUBJECT_W, 64)
    ctx.clip()
    ctx.fill_style = tint
    if name == "panel":
        ctx.fill_rect(x0, 0, SUBJECT_W, 64)
    elif name == "diagonal band":
        ctx.begin_path()
        _poly(ctx, [(cx - m * 22, 64), (cx + m * 4, 64), (cx + m * 22, 0), (cx - m * 4, 0)])
        ctx.fill()
    elif name == "disc":
        ctx.begin_path()
        ctx.arc(cx, 32.5, 24.5, 0, TAU)
        ctx.fill()
    elif name == "corner block":
        ctx.begin_path()
        _poly(ctx, [(cx - m * 28, 64), (cx - m * 28, 12), (cx + m * 24, 64)])
        ctx.fill()
    elif name == "horizontal band":
        ctx.fill_rect(x0, 21, SUBJECT_W, 23)
    elif name == "rings":
        ctx.stroke_style, ctx.line_width = tint, 2.6
        for r in (9, 16.5, 24):
            ctx.begin_path()
            ctx.arc(cx, 32.5, r, 0, TAU)
            ctx.stroke()
    elif name == "hatched panel":
        _hatch(ctx, x0, 0, x1, 64, tint, 3.4, 1.3)
    ctx.restore()


def _draw_subject(ctx: Canvas, f: DocFeatures, sheet: Sheet, cx: float) -> None:
    sp = icon_spec(*DOC_SUBJECTS[f.subject])
    ink, key = sheet.ink, sheet.palette[f.key][1]
    # where the body is filled with the ink color itself, details on top are drawn in the paper color
    over = sheet.bg if key == ink and sp["body"] else ink
    ctx.save()
    ctx.translate(cx, 33.2)
    ctx.scale(1.27, 1.27)
    ctx.translate(0, -28)
    ctx.line_cap = ctx.line_join = "round"
    _strokes(ctx, sp["lines"], ink)
    for kind, a, _fab in sp["body"]:
        ctx.begin_path()
        _shape(ctx, kind, a)
        ctx.fill_style = key
        ctx.fill()
        ctx.line_width, ctx.stroke_style = .8, ink
        ctx.stroke()
    if sp["solid"]:
        ctx.begin_path()
        for kind, a in sp["solid"]:
            _shape(ctx, kind, a)
        ctx.fill_style = over
        ctx.fill()
        if over != ink:
            ctx.line_width, ctx.stroke_style = .5, ink
            ctx.stroke()
    _strokes(ctx, sp.get("front", ()), over)
    ctx.restore()


def _draw_glyph(ctx: Canvas, sheet: Sheet, style: int, g: int, x: float, y: float, k: float = 1.0) -> None:
    """One colored glyph centered on (x, y); k scales it."""
    color, shape = sheet.palette[g >> 4][1], g & 15
    name = GLYPH_STYLES[style]
    if name == "plain":
        draw_symbol(ctx, shape, x, y, 2.75 * k, color)
        return
    ctx.begin_path()
    if name == "round tiles":
        ctx.arc(x, y, 3.05 * k, 0, TAU)
    else:
        ctx.rect(x - 2.9 * k, y - 2.9 * k, 5.8 * k, 5.8 * k)
    if name == "framed":
        ctx.line_width, ctx.stroke_style = .5 * k, color
        ctx.stroke()
        draw_symbol(ctx, shape, x, y, 2 * k, color)
    else:
        ctx.fill_style = color
        ctx.fill()
        draw_symbol(ctx, shape, x, y, (1.9 if name == "round tiles" else 2.1) * k, sheet.bg)


def _bar_path(ctx: Canvas, x, y, w, h, cap) -> None:
    r = min(h, w) / 2 if cap else min(.5, h / 2)
    ctx.begin_path()
    ctx.move_to(x + r, y)
    ctx.line_to(x + w - r, y)
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.line_to(x + w, y + h - r)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.line_to(x + r, y + h)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.line_to(x, y + r)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def _draw_bar(ctx: Canvas, sheet: Sheet, bar, x: float, cy: float, w: float) -> None:
    """A horizontal bar w wide, centered on cy. `level` (0-15) sets where its two colors meet,
    or which of 4 segments are filled."""
    _pos, style, color, color2, level, cap = bar
    c1, c2, name = sheet.palette[color][1], sheet.palette[color2][1], BAR_STYLES[style]
    h = 5.2
    y = cy - h / 2
    xs = x + 1.2 + (level + .5) / 16 * (w - 2.4)  # where the two parts meet
    ctx.save()
    if name == "progress":
        ctx.save()
        _bar_path(ctx, x, y, w, h, cap)
        ctx.clip()
        ctx.fill_style = c1
        ctx.fill_rect(x, y, xs - x, h)
        ctx.restore()
        _bar_path(ctx, x + .25, y + .25, w - .5, h - .5, cap)
        ctx.line_width, ctx.stroke_style = .5, c2
        ctx.stroke()
    elif name in ("two-tone", "striped", "marker"):
        _bar_path(ctx, x, y, w, h, cap)
        ctx.clip()
        if name == "two-tone":
            ctx.fill_style = c1
            ctx.fill_rect(x, y, xs - .25 - x, h)
            ctx.fill_style = c2
            ctx.fill_rect(xs + .25, y, x + w - xs - .25, h)
        elif name == "striped":
            ctx.fill_style = c2
            ctx.fill_rect(xs, y, x + w - xs, h)
            ctx.begin_path()
            ctx.rect(x, y, xs - x, h)
            ctx.clip()
            _hatch(ctx, x, y, xs, y + h, c1, 1.5, .95)
        else:
            ctx.fill_style = c1
            ctx.fill_rect(x, y, w, h)
            ctx.fill_style = sheet.bg
            ctx.fill_rect(xs - 1.5, y, 3, h)
            ctx.fill_style = c2
            ctx.fill_rect(xs - .95, y, 1.9, h)
    elif name == "slider":
        ctx.begin_path()
        ctx.move_to(x + .7, cy)
        ctx.line_to(x + w - .7, cy)
        ctx.line_width, ctx.stroke_style, ctx.line_cap = 1.3, c2, "round" if cap else "butt"
        ctx.stroke()
        xk = x + 2.5 + (level + .5) / 16 * (w - 5)
        ctx.begin_path()
        if cap:
            ctx.arc(xk, cy, 2.5, 0, TAU)
        else:
            ctx.rect(xk - 2.2, cy - 2.5, 4.4, 5)
        ctx.fill_style = c1
        ctx.fill()
        ctx.line_width, ctx.stroke_style = .45, sheet.bg
        ctx.stroke()
    elif name == "segments":
        seg = (w + .7) / 4
        for k in range(4):
            _bar_path(ctx, x + k * seg + .25, y + .25, seg - 1.2, h - .5, cap)
            on = level >> (3 - k) & 1
            if on:
                ctx.fill_style = c1
                ctx.fill()
            ctx.line_width, ctx.stroke_style = .5, c2
            ctx.stroke()
            if not on:  # an empty segment keeps a dot of the first color
                ctx.begin_path()
                ctx.arc(x + k * seg + .25 + (seg - 1.2) / 2, cy, .75, 0, TAU)
                ctx.fill_style = c1
                ctx.fill()
    elif name == "dashed":
        ctx.line_width, ctx.line_cap = 2.2, "round" if cap else "butt"
        ctx.begin_path()
        ctx.move_to(x + 1.1, cy)
        xd = x + 2.2 + (level + .5) / 16 * (w - 6.4)  # leaves room for at least one dash after it
        ctx.line_to(xd, cy)
        ctx.stroke_style = c1
        ctx.stroke()
        ctx.begin_path()
        px = xd + 2.2
        while px <= x + w - 1.1:  # dots (round ends) or short dashes (square ends)
            ctx.move_to(px - (0 if cap else .5), cy)
            ctx.line_to(px + (.01 if cap else .5), cy)
            px += 2.9
        ctx.stroke_style = c2
        ctx.stroke()
    else:  # offset pair
        _bar_path(ctx, x, y, xs - x, 2.3, cap)
        ctx.fill_style = c1
        ctx.fill()
        _bar_path(ctx, xs, y + 2.9, x + w - xs, 2.3, cap)
        ctx.fill_style = c2
        ctx.fill()
    ctx.restore()


def draw_document(ctx: Canvas, f: DocFeatures, checksum_hex: str = "", theme: Sheet | None = None) -> None:
    """Draw one Document badge in 128 x 64 units at the origin of ctx's current transform.
    `checksum_hex` is the 64-digit checksum part printed for cross-checking (left out when empty)."""
    sheet = theme or SHEETS[f.theme]
    bg, ink, rule = sheet.bg, sheet.ink, sheet.rule
    key = sheet.palette[f.key][1]
    tint = _mix_color(bg, key, .17)
    cx, div, L = _geometry(f.side)
    R = L + BLOCK_W
    ctx.save()
    ctx.line_join = "round"

    ctx.save()
    outline_path(ctx, f.outline, f.side)
    ctx.fill_style = bg
    ctx.fill()
    ctx.clip()
    if sheet.grid:
        ctx.line_width, ctx.stroke_style = .15, sheet.grid
        ctx.begin_path()
        for x in range(4, 128, 4):
            ctx.move_to(x, 0)
            ctx.line_to(x, 64)
        for y in range(4, 64, 4):
            ctx.move_to(0, y)
            ctx.line_to(128, y)
        ctx.stroke()
    _draw_motif(ctx, f, sheet, tint, cx)
    ctx.restore()

    _draw_subject(ctx, f, sheet, cx)

    def line(xa, ya, xb, yb):
        ctx.begin_path()
        ctx.move_to(xa, ya)
        ctx.line_to(xb, yb)
        ctx.line_width, ctx.stroke_style = .35, rule
        ctx.stroke()

    line(div, 6, div, 58)
    # handle and monogram
    w1, w2 = (w.upper() for w in f.words)
    size = 8.6
    ctx.set_font("cyber", size)
    widest = max(ctx.measure_text(w1), ctx.measure_text(w2))
    if widest > 43.5:
        size *= 43.5 / widest
        ctx.set_font("cyber", size)
    ctx.fill_style, ctx.text_align, ctx.text_baseline = ink, "left", "alphabetic"
    ctx.fill_text(w1, L, 12.4)
    ctx.fill_text(w2, L, 21.6)
    ctx.fill_style = key
    ctx.fill_rect(R - 18, 5.2, 18, 17.6)
    ctx.fill_style = max((bg, ink), key=lambda c: _contrast(c, key))
    ctx.set_font("mono", 11.6)
    ctx.text_align = "center"
    ctx.fill_text(f.monogram, R - 9, 18.2)
    line(L, 25.4, R, 25.4)
    # checksum digits and code word
    ctx.fill_style = ink
    if checksum_hex:
        ctx.set_font("mono", 3.9)
        ctx.text_align = "left"
        first, last = checksum_hex[:8].upper(), checksum_hex[-8:].upper()
        ctx.fill_text(first, L, 32.6)
        x = L + ctx.measure_text(first)
        ctx.begin_path()
        for k in range(3):  # ellipsis between the first and last digits
            ctx.rect(x + .75 + k * 1.05, 32, .55, .6)
        ctx.fill()
        ctx.fill_text(last, x + 4.2, 32.6)
        line(R - 21.6, 25.4, R - 21.6, 36)
    ctx.set_font("mono", 4.1)
    ctx.text_align = "right"
    ctx.fill_text(CODE_WORDS[f.code], R, 32.6)
    line(L, 36, R, 36)
    # characters and the mark glyph
    ctx.set_font("mono", 5.8)
    ctx.text_align = "left"
    ctx.fill_text(" ".join(f.char_groups), L, 43.8)
    _draw_glyph(ctx, sheet, f.gstyle, f.glyphs[0], R - 3.9, 41.4, 1.2)
    line(L, 46.8, R, 46.8)
    # two rows of 10 slots: glyphs, with one bar mixed into each row
    pitch = BLOCK_W / GLYPH_COLS
    rest = iter(f.glyphs[1:])
    for row in range(2):
        y, width, slot = 50.5 + 6.6 * row, bar_width(f, row), 0
        for i in range(GLYPH_COLS - width + 1):
            if i == f.bars[row][0]:
                _draw_bar(ctx, sheet, f.bars[row], L + pitch * slot + .45, y, pitch * width - .9)
                slot += width
            if i < GLYPH_COLS - width:
                _draw_glyph(ctx, sheet, f.gstyle, next(rest), L + pitch * (slot + .5), y)
                slot += 1

    outline_path(ctx, f.outline, f.side)
    ctx.line_width, ctx.stroke_style = 1.1, ink
    ctx.stroke()
    ctx.restore()


def draw_document_badge(ctx: Canvas, f: DocFeatures, checksum_hex: str = "", theme: Sheet | None = None) -> None:
    """One Document badge on the package's 960 x 480 badge canvas."""
    ctx.save()
    ctx.scale(U, U)
    draw_document(ctx, f, checksum_hex, theme)
    ctx.restore()


PAIR_BG, PAIR_FG = "#FFFFFF", "#14171A"


def draw_document_pair(ctx: Canvas, parts: list[DocFeatures], checksum_hex: tuple[str, ...] = ("", "")) -> None:
    """Both halves of a 512-bit hash on one plain sheet, numbered 1 and 2 and joined by a rail."""
    ctx.begin_path()
    ctx.rect(0, 0, PAIR_W, PAIR_H)
    ctx.fill_style = PAIR_BG
    ctx.fill()
    ctx.line_width, ctx.stroke_style = S * .012, PAIR_FG
    ctx.stroke_rect(S * .04, S * .04, PAIR_W - S * .08, PAIR_H - S * .08)
    pos = [(PAIR_PAD, PAIR_PAD), (PAIR_PAD, PAIR_PAD + H + PAIR_GAP)]
    marks = [(PAIR_PAD / 2, y + S * .2) for _, y in pos]
    ctx.begin_path()
    ctx.move_to(*marks[0])
    ctx.line_to(*marks[1])
    ctx.line_width = S * .02
    ctx.stroke()
    for (x, y), f, hx in zip(pos, parts, checksum_hex):
        ctx.save()
        ctx.translate(x, y)
        draw_document_badge(ctx, f, hx)
        ctx.restore()
    for i, (x, y) in enumerate(marks):
        ctx.begin_path()
        ctx.arc(x, y, S * .075, 0, TAU)
        ctx.fill_style = PAIR_FG
        ctx.fill()
        ctx.fill_style = PAIR_BG
        ctx.set_font("mono", S * .1)
        ctx.text_align, ctx.text_baseline = "center", "middle"
        ctx.fill_text(str(i + 1), x, y + S * .006)
    ctx.fill_style = PAIR_FG
    ctx.set_font("mono", S * .11)
    ctx.text_align, ctx.text_baseline = "center", "middle"
    ctx.fill_text("SHA-512 · 2 PARTS · READ 1 THEN 2", PAIR_W / 2, PAIR_H - PAIR_PAD * .35 - PAIR_FOOT / 2)


__all__ = ["DocFeatures", "Sheet", "SHEETS", "DOC_FIELDS", "doc_mix", "doc_decode", "doc_encode", "doc_describe",
           "doc_with_changes", "draw_document", "draw_document_badge", "draw_document_pair", "DOC_SUBJECTS", "DOC_SUBJECT_KINDS", "OUTLINES", "MOTIFS", "CODE_WORDS",
           "GLYPH_STYLES", "BAR_STYLES", "bar_width"]
