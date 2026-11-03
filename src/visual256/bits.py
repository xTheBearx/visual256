"""Bit-level reading and writing, most significant bit first."""

from __future__ import annotations

# The 32-character alphabet shared by every visual256 style: A-Z and 2-9 without I, O, 0 or 1,
# so no two characters are easy to confuse when read aloud or copied by hand.
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class BitReader:
    """Reads unsigned integers of any width from a byte string, MSB first."""

    def __init__(self, data: bytes):
        self.data = bytes(data)
        self.pos = 0

    def read(self, n: int) -> int:
        v = 0
        for _ in range(n):
            if self.pos >= len(self.data) * 8:
                raise ValueError("read past end of data")
            byte = self.data[self.pos >> 3]
            v = (v << 1) | ((byte >> (7 - (self.pos & 7))) & 1)
            self.pos += 1
        return v


class BitWriter:
    """Builds a byte string from unsigned integers of any width, MSB first."""

    def __init__(self) -> None:
        self.bits: list[int] = []

    def write(self, value: int, n: int) -> None:
        if value < 0 or value >= (1 << n):
            raise ValueError(f"{value} does not fit in {n} bits")
        for i in range(n - 1, -1, -1):
            self.bits.append((value >> i) & 1)

    def to_bytes(self) -> bytes:
        if len(self.bits) % 8:
            raise ValueError("bit count is not a multiple of 8")
        out = bytearray()
        for i in range(0, len(self.bits), 8):
            b = 0
            for bit in self.bits[i:i + 8]:
                b = (b << 1) | bit
            out.append(b)
        return bytes(out)


def to_alphabet(values: list[int] | tuple[int, ...]) -> str:
    """Map 5-bit values to characters of ALPHABET."""
    return "".join(ALPHABET[v] for v in values)


def from_alphabet(text: str) -> list[int]:
    """Map characters of ALPHABET back to 5-bit values. Case-insensitive; separators are ignored."""
    out = []
    for ch in text.upper():
        if ch in " ·-_<":
            continue
        idx = ALPHABET.find(ch)
        if idx < 0:
            raise ValueError(f"{ch!r} is not in the visual256 alphabet")
        out.append(idx)
    return out
