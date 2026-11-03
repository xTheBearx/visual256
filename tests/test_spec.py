import hashlib
import os
import random

import pytest

from visual256 import ALPHABET, Badge, decode, describe, encode, mix, with_changes
from visual256.bits import from_alphabet, to_alphabet
from visual256.spec import HEADLINE_BITS, HEADLINE_FIELDS, N_BARS


def test_headline_is_89_bits_and_total_is_256():
    assert HEADLINE_BITS == 89
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
    assert f.theme_id == "jungle"
    assert f.handle == "FORTUNE·PREVENT"
    assert f.char_groups == ["4Q7Z", "VGAT", "6W8W"]
    assert len(f.bars) == 5


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
    assert rows[0][0] == "0-2" and rows[-1][0] == "176-255"


def test_encode_rejects_out_of_range_values():
    f = decode(bytes(32))
    with pytest.raises(ValueError):
        encode(with_changes(f, theme=8))


def test_subjects_cover_all_eight_kinds():
    from visual256.spec import SUBJECTS, subject_kind
    kinds = [subject_kind(i) for i in range(64)]
    counts = [kinds.count(k) for k in ("face", "building", "animal", "vehicle", "plant", "furniture", "food", "sports")]
    assert counts == [3, 10, 10, 10, 10, 8, 8, 5]
    assert kinds == sorted(kinds, key=kinds.index)  # each kind is one contiguous range
    assert len(set(SUBJECTS)) == 64


def _rows(**changes):
    f = with_changes(decode(bytes(32)), **changes)
    return dict((label, value) for _, label, value in describe(f, tuple("c" * 16)))


def test_furniture_details_are_named():
    rows = _rows(subject=50, vstyle=6, grille=3, mod=3, cheek=2)
    assert rows["Subject"] == "bathtub"
    assert (rows["Subject detail A"], rows["Subject detail B"]) == ("plaid", "teapot")
    assert (rows["Subject detail C"], rows["Subject detail D"]) == ("bunting", "checker tiles")


def test_food_details_are_named():
    rows = _rows(subject=51, vstyle=0, grille=4, mod=0, cheek=2)
    assert rows["Subject"] == "pizza slice"
    assert (rows["Subject detail A"], rows["Subject detail B"]) == ("sprinkles", "cake stand")
    assert (rows["Subject detail C"], rows["Subject detail D"]) == ("cherry", "chopsticks")
    assert _rows(subject=58)["Subject"] == "hot dog"


def test_sports_details_are_named():
    rows = _rows(subject=59, vstyle=2, grille=2, mod=1, cheek=3)
    assert rows["Subject"] == "soccer ball"
    assert (rows["Subject detail A"], rows["Subject detail B"]) == ("polka dots", "trophy")
    assert (rows["Subject detail C"], rows["Subject detail D"]) == ("sparks", "ice")
    assert _rows(subject=63)["Subject"] == "boxing glove"


def test_three_android_heads_remain():
    assert [_rows(subject=i)["Subject"] for i in range(3)] == ["android, dome head", "android, bucket head", "android, skull head"]


def test_animals_wear_nothing_on_top_of_the_head():
    from visual256.spec import ACCESSORIES
    assert "party hat" not in ACCESSORIES and "bow tie" in ACCESSORIES


def test_look_alike_animals_differ_where_others_wear_a_bow_tie():
    from visual256.spec import ANIMALS, NO_BOW_TIE, SUBJECT_START
    for name in ANIMALS:
        accessory = _rows(subject=SUBJECT_START["animal"] + ANIMALS.index(name), mod=2)["Subject detail C"]
        assert accessory == ("no accessory" if name in NO_BOW_TIE else "bow tie")
    assert set(NO_BOW_TIE) == {"owl", "panda"}


def test_describe_names_subject_details_by_kind():
    f = decode(bytes(32))
    house = dict((label, value) for _, label, value in describe(with_changes(f, subject=3), tuple("c" * 16)))
    cat = dict((label, value) for _, label, value in describe(with_changes(f, subject=13), tuple("c" * 16)))
    car = dict((label, value) for _, label, value in describe(with_changes(f, subject=23), tuple("c" * 16)))
    pine = dict((label, value) for _, label, value in describe(with_changes(f, subject=33), tuple("c" * 16)))
    assert house["Subject"] == "house" and house["Subject detail A"] == "square grid"
    assert cat["Subject"] == "cat" and cat["Subject detail B"] == "button nose"
    assert car["Subject"] == "car" and car["Subject detail B"] == "smoke puffs"
    assert pine["Subject"] == "pine" and pine["Subject detail B"] == "terracotta pot"
