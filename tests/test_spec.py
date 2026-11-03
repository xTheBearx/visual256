import hashlib
import os
import random

import pytest

from visual256 import ALPHABET, Badge, decode, describe, encode, mix, with_changes
from visual256.bits import from_alphabet, to_alphabet
from visual256.spec import HEADLINE_BITS, HEADLINE_FIELDS, N_BARS


def test_headline_is_83_bits_and_total_is_256():
    assert HEADLINE_BITS == 83
    assert HEADLINE_BITS + N_BARS * 3 + 3 * 4 + 12 * 5 + 10 * 8 == 256


@pytest.mark.parametrize("seed", range(5))
def test_roundtrip_random_digests(seed):
    rng = random.Random(seed)
    for _ in range(400):
        data = bytes(rng.getrandbits(8) for _ in range(32))
        assert encode(decode(data)) == data


def test_roundtrip_edge_cases():
    for data in (bytes(32), b"\xff" * 32, b"\x80" * 32, b"\x01" * 32, os.urandom(32)):
        assert encode(decode(data)) == data


def test_every_badge_bit_changes_the_features():
    base = hashlib.sha256(b"visual256").digest()
    f0 = decode(base)
    for bit in range(256):
        flipped = bytearray(base)
        flipped[bit >> 3] ^= 1 << (7 - (bit & 7))
        assert decode(bytes(flipped)) != f0, f"bit {bit} is not drawn"


def test_known_digest_matches_browser_preview():
    # The same values appear in the lab page for this input.
    b = Badge.from_text("release-2.4.1.tar.gz")
    assert b.parts[0].hex() == "f2924e11c5dab2f02b72a9423cdfad3bb799811e53d4da75de2cccbde7008c80"
    f = b.features[0]
    assert f.theme_id == "concrete"
    assert f.handle == "AIR·INCREASE"
    assert f.char_groups == ["4Q7Z", "VGAT", "6W8W"]
    assert [v + 1 for v in f.bars] == [3, 3, 5, 2, 1, 8, 5]
    assert f.layout == 1


def test_detail_cells_are_the_last_ten_badge_bytes():
    bits = mix(hashlib.sha256(b"cells").digest())[0]
    assert decode(bits).cells == tuple(bits[22:])


def _hamming(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))


@pytest.mark.parametrize("size", [32, 64])
def test_one_flipped_checksum_bit_changes_every_badge(size):
    rng = random.Random(size)
    checksum = bytes(rng.getrandbits(8) for _ in range(size))
    base = mix(checksum)
    for bit in range(size * 8):
        flipped = bytearray(checksum)
        flipped[bit >> 3] ^= 1 << (7 - (bit & 7))
        for before, after in zip(base, mix(bytes(flipped))):
            assert 64 < _hamming(before, after) < 192, f"input bit {bit} did not avalanche"


def test_mixing_changes_most_features():
    checksum = hashlib.sha256(b"avalanche").digest()
    f0 = decode(mix(checksum)[0])
    flipped = bytes([checksum[0] ^ 1]) + checksum[1:]
    f1 = decode(mix(flipped)[0])
    changed = sum(getattr(f0, name) != getattr(f1, name) for name, *_ in HEADLINE_FIELDS)
    assert changed >= len(HEADLINE_FIELDS) // 2


def test_parts_of_a_512_bit_checksum_differ():
    a, b = mix(hashlib.sha512(b"x").digest())
    assert a != b and len(a) == len(b) == 32


def test_alphabet_has_32_unambiguous_characters():
    assert len(ALPHABET) == len(set(ALPHABET)) == 32
    assert not set("IO01") & set(ALPHABET)
    vals = list(range(32))
    assert from_alphabet(to_alphabet(vals)) == vals
    assert from_alphabet("akem·699d") == from_alphabet("AKEM699D")
    with pytest.raises(ValueError):
        from_alphabet("O")


def test_with_changes_only_changes_named_fields():
    f = decode(hashlib.sha256(b"x").digest())
    g = with_changes(f, layout=(f.layout + 1) % 8)
    assert g.layout != f.layout and g.bars == f.bars and g.word1 == f.word1


def test_describe_covers_every_field():
    f = decode(hashlib.sha256(b"x").digest())
    rows = describe(f, tuple(f"c{i}" for i in range(16)))
    assert len(rows) == len(HEADLINE_FIELDS) + 4
    assert rows[0][0] == "0-3" and rows[-1][0] == "176-255"


def test_encode_rejects_out_of_range_values():
    f = decode(bytes(32))
    with pytest.raises(ValueError):
        encode(with_changes(f, theme=16))
