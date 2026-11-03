"""Public API: hash something, then render it as SVG, PNG, PDF, a data URI or an <img> tag."""

from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass
from pathlib import Path

from . import bip39
from .canvas import Canvas
from .draw import H, PAIR_H, PAIR_W, W, draw_badge, draw_pair
from .spec import Features, decode, describe
from .themes import Theme, get as get_theme

BADGE_ASPECT = W / H  # 2:1, drawn at 128 x 64 units


@dataclass(frozen=True)
class Badge:
    """A 256-bit or 512-bit digest and the badge(s) that show it."""

    digest: bytes

    def __post_init__(self):
        if len(self.digest) not in (32, 64):
            raise ValueError("visual256 draws 256-bit (32-byte) or 512-bit (64-byte) digests")

    # ---- constructors ----
    @classmethod
    def from_bytes(cls, digest: bytes) -> "Badge":
        return cls(bytes(digest))

    @classmethod
    def from_hex(cls, text: str) -> "Badge":
        clean = "".join(ch for ch in text if ch not in " :-\n\t")
        try:
            return cls(bytes.fromhex(clean))
        except ValueError:
            raise ValueError("expected 64 or 128 hex characters") from None

    @classmethod
    def from_data(cls, data: bytes, algo: str = "sha256") -> "Badge":
        return cls(_hash(algo).__call__(data).digest())

    @classmethod
    def from_text(cls, text: str, algo: str = "sha256") -> "Badge":
        return cls.from_data(text.encode("utf-8"), algo)

    @classmethod
    def from_file(cls, path: str | Path, algo: str = "sha256") -> "Badge":
        h = _hash(algo)()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return cls(h.digest())

    # ---- data ----
    @property
    def parts(self) -> list[bytes]:
        return [self.digest[i:i + 32] for i in range(0, len(self.digest), 32)]

    @property
    def features(self) -> list[Features]:
        return [decode(p) for p in self.parts]

    @property
    def hex(self) -> str:
        return self.digest.hex()

    def mnemonic(self) -> list[list[str]]:
        """Spoken backup: 24 standard BIP-39 words per 256-bit part."""
        return [bip39.to_mnemonic(p) for p in self.parts]

    def describe(self, theme: str | Theme = "cyberpunk") -> list[list[tuple[str, str, str]]]:
        t = get_theme(theme)
        return [describe(f, t.names) for f in self.features]

    # ---- rendering ----
    def canvas(self, theme: str | Theme = "cyberpunk") -> Canvas:
        t = get_theme(theme)
        feats = self.features
        if len(feats) == 1:
            c = Canvas(W, H)
            draw_badge(c, feats[0], t)
        else:
            c = Canvas(PAIR_W, PAIR_H)
            draw_pair(c, feats, t)
        return c

    def size_for(self, width: float) -> tuple[float, float]:
        if len(self.digest) == 32:
            return width, width / BADGE_ASPECT
        return width, width * PAIR_H / PAIR_W

    def svg(self, theme: str | Theme = "cyberpunk", width: float = 256) -> str:
        """SVG markup. `width` sets the width/height attributes; the drawing scales cleanly to any size."""
        w, h = self.size_for(width)
        title = "visual256 badge " + self.hex[:16] + "…"
        return self.canvas(theme).to_svg(w, h, title=title)

    def png(self, theme: str | Theme = "cyberpunk", width: int = 256) -> bytes:
        """PNG bytes at `width` pixels. Needs the `resvg-py` package (pip install visual256[png])."""
        try:
            import resvg_py
        except ImportError:
            raise RuntimeError("PNG output needs resvg-py: pip install 'visual256[png]'") from None
        svg = self.svg(theme, width)
        return bytes(resvg_py.svg_to_bytes(svg_string=svg))

    def pdf(self, theme: str | Theme = "cyberpunk", width: float = 256) -> bytes:
        """PDF bytes (vector). Needs cairosvg (pip install visual256[pdf]). Neon glow is not drawn in PDF."""
        try:
            import cairosvg
        except ImportError:
            raise RuntimeError("PDF output needs cairosvg: pip install 'visual256[pdf]'") from None
        return cairosvg.svg2pdf(bytestring=self.svg(theme, width).encode("utf-8"))

    def data_uri(self, theme: str | Theme = "cyberpunk", width: int = 256, fmt: str = "svg") -> str:
        if fmt == "svg":
            return "data:image/svg+xml;base64," + base64.b64encode(self.svg(theme, width).encode()).decode()
        if fmt == "png":
            return "data:image/png;base64," + base64.b64encode(self.png(theme, width * 2)).decode()
        raise ValueError("fmt must be 'svg' or 'png'")

    def html_img(self, theme: str | Theme = "cyberpunk", width: int = 128, fmt: str = "svg") -> str:
        """An <img> tag for a web page. PNGs are rendered at 2x for sharp display on high-density screens."""
        w, h = self.size_for(width)
        alt = "Checksum badge for " + self.hex[:16] + "…"
        return (f'<img src="{self.data_uri(theme, width, fmt)}" width="{round(w)}" height="{round(h)}" '
                f'alt="{alt}">')


def _hash(algo: str):
    algo = algo.lower().replace("-", "")
    if algo not in ("sha256", "sha512"):
        raise ValueError("algo must be sha256 or sha512")
    return getattr(hashlib, algo)
