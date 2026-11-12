"""Public API: hash something, then render it as SVG, PNG, PDF, a data URI or an <img> tag."""

from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass
from pathlib import Path

from . import bip39
from .canvas import Canvas
from .document import DocFeatures, doc_decode, doc_describe, doc_mix, draw_document_badge, draw_document_pair
from .draw import H, PAIR_H, PAIR_W, W, draw_badge, draw_pair
from .spec import Features, decode, describe, mix
from .themes import get as get_theme

STYLES = ("netrunner", "document")
BADGE_ASPECT = W / H  # 2:1, drawn on a 128 x 64 unit grid; design (true) size 256 x 128 pixels


@dataclass(frozen=True)
class Badge:
    """A 256-bit or 512-bit checksum and the badge(s) that show it.

    The badges show `mix(digest)`, a SHA-256 of the whole checksum per part, so a one-bit change in
    the checksum changes everything. The spoken backup (`mnemonic`) encodes the checksum itself.

    `style` picks the look: "netrunner" (the neon ID card) or "document" (flat and print-friendly,
    for engineering documents). The two styles use different bits, so their badges are unrelated."""

    digest: bytes
    style: str = "netrunner"

    def __post_init__(self):
        if self.style not in STYLES:
            raise ValueError("style must be one of: " + ", ".join(STYLES))
        if len(self.digest) not in (32, 64):
            raise ValueError("visual256 draws 256-bit (32-byte) or 512-bit (64-byte) digests")

    # ---- constructors ----
    @classmethod
    def from_bytes(cls, digest: bytes, style: str = "netrunner") -> "Badge":
        return cls(bytes(digest), style)

    @classmethod
    def from_hex(cls, text: str, style: str = "netrunner") -> "Badge":
        clean = "".join(ch for ch in text if ch not in " :-\n\t")
        try:
            return cls(bytes.fromhex(clean), style)
        except ValueError:
            raise ValueError("expected 64 or 128 hex characters") from None

    @classmethod
    def from_data(cls, data: bytes, algo: str = "sha256", style: str = "netrunner") -> "Badge":
        return cls(_hash(algo).__call__(data).digest(), style)

    @classmethod
    def from_text(cls, text: str, algo: str = "sha256", style: str = "netrunner") -> "Badge":
        return cls.from_data(text.encode("utf-8"), algo, style)

    @classmethod
    def from_file(cls, path: str | Path, algo: str = "sha256", style: str = "netrunner") -> "Badge":
        h = _hash(algo)()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return cls(h.digest(), style)

    # ---- data ----
    @property
    def checksum_parts(self) -> list[bytes]:
        """The checksum split into 256-bit parts."""
        return [self.digest[i:i + 32] for i in range(0, len(self.digest), 32)]

    @property
    def parts(self) -> list[bytes]:
        """Badge bits, one 32-byte value per badge (see spec.mix and document.doc_mix)."""
        return doc_mix(self.digest) if self.style == "document" else mix(self.digest)

    @property
    def features(self) -> list[Features] | list[DocFeatures]:
        dec = doc_decode if self.style == "document" else decode
        return [dec(p) for p in self.parts]

    @property
    def hex(self) -> str:
        return self.digest.hex()

    def mnemonic(self) -> list[list[str]]:
        """Spoken backup of the checksum itself: 24 standard BIP-39 words per 256-bit part."""
        return [bip39.to_mnemonic(p) for p in self.checksum_parts]

    def describe(self) -> list[list[tuple[str, str, str]]]:
        """Every feature in plain language, per 256-bit part. Color names come from the badge's theme."""
        if self.style == "document":
            return [doc_describe(f) for f in self.features]
        out = []
        for f in self.features:
            t = get_theme(f.theme)
            out.append(describe(f, t.names, t.name, tuple(n for n, _ in t.gradients)))
        return out

    # ---- rendering ----
    def canvas(self) -> Canvas:
        feats = self.features
        if self.style == "document":
            hexes = tuple(p.hex() for p in self.checksum_parts)
            if len(feats) == 1:
                c = Canvas(W, H)
                draw_document_badge(c, feats[0], hexes[0])
            else:
                c = Canvas(PAIR_W, PAIR_H)
                draw_document_pair(c, feats, hexes)
            return c
        if len(feats) == 1:
            c = Canvas(W, H)
            draw_badge(c, feats[0])
        else:
            c = Canvas(PAIR_W, PAIR_H)
            draw_pair(c, feats)
        return c

    def size_for(self, width: float) -> tuple[float, float]:
        if len(self.digest) == 32:
            return width, width / BADGE_ASPECT
        return width, width * PAIR_H / PAIR_W

    def svg(self, width: float = 256) -> str:
        """SVG markup. `width` sets the width/height attributes; the drawing scales cleanly to any size."""
        w, h = self.size_for(width)
        title = "visual256 badge " + self.hex[:16] + "…"
        return self.canvas().to_svg(w, h, title=title)

    def png(self, width: int = 256) -> bytes:
        """PNG bytes at `width` pixels. Needs the `resvg-py` package (pip install visual256[png])."""
        try:
            import resvg_py
        except ImportError:
            raise RuntimeError("PNG output needs resvg-py: pip install 'visual256[png]'") from None
        svg = self.svg(width)
        return bytes(resvg_py.svg_to_bytes(svg_string=svg))

    def pdf(self, width: float = 256) -> bytes:
        """PDF bytes (vector). Needs cairosvg (pip install visual256[pdf]). Neon glow is not drawn in PDF."""
        try:
            import cairosvg
        except ImportError:
            raise RuntimeError("PDF output needs cairosvg: pip install 'visual256[pdf]'") from None
        return cairosvg.svg2pdf(bytestring=self.svg(width).encode("utf-8"))

    def data_uri(self, width: int = 256, fmt: str = "svg") -> str:
        if fmt == "svg":
            return "data:image/svg+xml;base64," + base64.b64encode(self.svg(width).encode()).decode()
        if fmt == "png":
            return "data:image/png;base64," + base64.b64encode(self.png(width * 2)).decode()
        raise ValueError("fmt must be 'svg' or 'png'")

    def html_img(self, width: int = 256, fmt: str = "svg") -> str:
        """An <img> tag for a web page. PNGs are rendered at 2x for sharp display on high-density screens."""
        w, h = self.size_for(width)
        alt = "Checksum badge for " + self.hex[:16] + "…"
        return (f'<img src="{self.data_uri(width, fmt)}" width="{round(w)}" height="{round(h)}" '
                f'alt="{alt}">')


def _hash(algo: str):
    algo = algo.lower().replace("-", "")
    if algo not in ("sha256", "sha512"):
        raise ValueError("algo must be sha256 or sha512")
    return getattr(hashlib, algo)
