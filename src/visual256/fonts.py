"""Bundled fonts, text measurement and text-to-outline conversion.

Text is drawn as filled outlines, so an SVG looks identical everywhere, with no font installed.
Fonts are subset copies of Chakra Petch Bold, JetBrains Mono SemiBold and Spectral SemiBold,
all under the SIL Open Font License (see the OFL-*.txt files next to them).
"""

from __future__ import annotations

from functools import lru_cache
from importlib import resources
from io import BytesIO

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

FONT_FILES = {
    "cyber": "ChakraPetch-Bold.ttf",
    "mono": "JetBrainsMono-SemiBold.ttf",
    "serif": "Spectral-SemiBold.ttf",
}


class Face:
    def __init__(self, key: str):
        data = resources.files(__package__).joinpath("fonts/" + FONT_FILES[key]).read_bytes()
        self.font = TTFont(BytesIO(data))
        self.upm = self.font["head"].unitsPerEm
        self.ascent = self.font["hhea"].ascent
        self.descent = self.font["hhea"].descent
        self.cmap = self.font.getBestCmap()
        self.hmtx = self.font["hmtx"]
        self.glyphs = self.font.getGlyphSet()
        self.fallback = self.cmap.get(ord("?"), ".notdef")

    def glyph_name(self, ch: str) -> str:
        return self.cmap.get(ord(ch), self.fallback)

    def advance(self, ch: str) -> int:
        return self.hmtx[self.glyph_name(ch)][0]

    def measure(self, text: str, size: float) -> float:
        return sum(self.advance(ch) for ch in text) * size / self.upm


@lru_cache(maxsize=None)
def face(key: str) -> Face:
    return Face(key)


class OutlinePen(BasePen):
    """Collects glyph outlines as SVG path commands, mapped through `xf`."""

    def __init__(self, glyphset, xf, fmt):
        super().__init__(glyphset)
        self.xf, self.fmt, self.d = xf, fmt, []

    def _p(self, p):
        x, y = self.xf(p)
        return f"{self.fmt(x)} {self.fmt(y)}"

    def _moveTo(self, p):
        self.d.append("M" + self._p(p))

    def _lineTo(self, p):
        self.d.append("L" + self._p(p))

    def _curveToOne(self, p1, p2, p3):
        self.d.append("C" + " ".join(self._p(p) for p in (p1, p2, p3)))

    def _qCurveToOne(self, p1, p2):
        self.d.append("Q" + " ".join(self._p(p) for p in (p1, p2)))

    def _closePath(self):
        self.d.append("Z")
