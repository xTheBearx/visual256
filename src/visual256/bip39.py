"""BIP-39 English word list and mnemonic encoding.

The word list is the official ``english.txt`` from https://github.com/bitcoin/bips
(BIP-0039, MIT licensed). Its SHA-256 is checked on first use.
"""

from __future__ import annotations

import hashlib
from functools import lru_cache
from importlib import resources

from .bits import BitReader, BitWriter

WORDLIST_SHA256 = "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"


@lru_cache(maxsize=1)
def wordlist() -> tuple[str, ...]:
    raw = resources.files(__package__).joinpath("data/bip39_english.txt").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != WORDLIST_SHA256:
        raise RuntimeError(f"BIP-39 word list is corrupted (sha256 {digest})")
    words = tuple(raw.decode("ascii").split())
    if len(words) != 2048:
        raise RuntimeError("BIP-39 word list must have 2048 words")
    return words


@lru_cache(maxsize=1)
def _index() -> dict[str, int]:
    return {w: i for i, w in enumerate(wordlist())}


def word(index: int) -> str:
    return wordlist()[index]


def index_of(w: str) -> int:
    """Look up a word, accepting any unique 4-letter prefix as BIP-39 allows."""
    w = w.strip().lower()
    idx = _index()
    if w in idx:
        return idx[w]
    if len(w) >= 4:
        matches = [i for name, i in idx.items() if name.startswith(w[:4])]
        if len(matches) == 1:
            return matches[0]
    raise ValueError(f"{w!r} is not a BIP-39 word")


def to_mnemonic(entropy: bytes) -> list[str]:
    """Standard BIP-39 encoding: entropy plus a SHA-256 checksum, 11 bits per word.

    32 bytes of entropy give 24 words (256 bits + 8-bit checksum).
    """
    n = len(entropy)
    if n not in (16, 20, 24, 28, 32):
        raise ValueError("BIP-39 entropy must be 16, 20, 24, 28 or 32 bytes")
    cs_bits = n * 8 // 32
    checksum = hashlib.sha256(entropy).digest()
    reader = BitReader(entropy + checksum[:1 + (cs_bits - 1) // 8])
    total = n * 8 + cs_bits
    return [word(reader.read(11)) for _ in range(total // 11)]


def from_mnemonic(words: list[str] | str) -> bytes:
    """Decode a BIP-39 mnemonic back to its entropy, verifying the checksum."""
    if isinstance(words, str):
        words = words.split()
    total = len(words) * 11
    if len(words) not in (12, 15, 18, 21, 24):
        raise ValueError("a BIP-39 mnemonic has 12, 15, 18, 21 or 24 words")
    writer = BitWriter()
    for w in words:
        writer.write(index_of(w), 11)
    cs_bits = total // 33
    ent_bits = total - cs_bits
    bits = writer.bits
    entropy = BitWriter()
    entropy.bits = bits[:ent_bits]
    data = entropy.to_bytes()
    expected = BitReader(hashlib.sha256(data).digest()).read(cs_bits)
    got = 0
    for b in bits[ent_bits:]:
        got = (got << 1) | b
    if got != expected:
        raise ValueError("BIP-39 checksum does not match; a word is wrong or out of order")
    return data
