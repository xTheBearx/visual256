"""visual256: turn a 256-bit or 512-bit checksum into a small, memorable, exact picture.

    >>> from visual256 import Badge
    >>> badge = Badge.from_text("hello")
    >>> svg = badge.svg(width=256)
    >>> badge.mnemonic()[0][:3]
    ['coconut', 'mystery', 'hub']
"""

from . import bip39
from .bits import ALPHABET
from .render import Badge
from .spec import SPEC_VERSION, Features, decode, describe, encode, with_changes
from .themes import THEMES, Theme

__version__ = "0.2.0"
__all__ = ["Badge", "Features", "decode", "encode", "describe", "with_changes", "bip39", "ALPHABET",
           "THEMES", "Theme", "SPEC_VERSION", "__version__"]
