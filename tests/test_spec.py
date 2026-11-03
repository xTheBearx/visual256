import hashlib
import os
import random

import pytest

from visual256 import ALPHABET, Badge, decode, describe, encode, with_changes
from visual256.bits import from_alphabet, to_alphabet
from visual256.spec import HEADLINE_FIELDS, HEADLINE_BITS


def test_headline_is_80_bits_and_total_is_256():
    assert HEADLINE_BITS == 80
    assert HEADLINE_BITS + 8 * 3 + 3 * 4 + 12 * 5 + 10 * 8 == 256


@pytest.mark.parametrize("seed", range(5))
def test_roundtrip_random_digests(seed):
    rng = random.Random(seed)
    for _ in range(400):
        data = bytes(rng.getrandbits(8) for _ in range(32))
        assert encode(decode(data)) == data


def test_roundtrip_edge_cases():
    for data in (bytes(32), b"\xff" * 32, b"\x80" * 32, b"\x01" * 32, os.urandom(32)):
        assert encode(decode(data)) == data


def test_every_bit_changes_the_features():
    base = hashlib.sha256(b"visual256").digest()
    f0 = decode(base)
    for bit in range(256):
        flipped = bytearray(base)
        flipped[bit >> 3] ^= 1 << (7 - (bit & 7))
        assert decode(bytes(flipped)) != f0, f"bit {bit} is not drawn"


def test_known_digest_matches_browser_preview():
    # The same values appear in the lab page for this input.
    f = Badge.from_text("release-2.4.1.tar.gz").features[0]
    assert f.theme_id == "paper"
    assert f.handle == "DUTY·TRUTH"
    assert f.char_groups == ["699D", "U8VU", "MLFF"]
    assert [v + 1 for v in f.bars] == [2, 4, 2, 5, 5, 5, 1, 3]
    assert f.cells == tuple(bytes.fromhex("30ea09312bbd5d78e18e"))
    assert f.layout == 6


def test_detail_cells_are_the_last_ten_bytes():
    digest = hashlib.sha256(b"cells").digest()
    assert decode(digest).cells == tuple(digest[22:])


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
    assert rows[0][0] == "0-2" and rows[-1][0] == "176-255"


def test_encode_rejects_out_of_range_values():
    f = decode(bytes(32))
    with pytest.raises(ValueError):
        encode(with_changes(f, layout=8))
