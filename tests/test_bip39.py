import json
from pathlib import Path

import pytest

from visual256 import Badge, bip39

VECTORS = json.loads((Path(__file__).parent / "data" / "bip39_vectors_256.json").read_text())["vectors"]


def test_wordlist_is_official():
    words = bip39.wordlist()
    assert len(words) == 2048
    assert words[0] == "abandon" and words[-1] == "zoo"
    assert len({w[:4] for w in words}) == 2048


@pytest.mark.parametrize("vec", VECTORS, ids=[v["entropy"][:8] for v in VECTORS])
def test_official_vectors(vec):
    entropy = bytes.fromhex(vec["entropy"])
    assert " ".join(bip39.to_mnemonic(entropy)) == vec["mnemonic"]
    assert bip39.from_mnemonic(vec["mnemonic"]) == entropy


def test_four_letter_prefixes_are_accepted():
    words = bip39.to_mnemonic(bytes(range(32)))
    short = [w[:4] for w in words]
    assert bip39.from_mnemonic(short) == bytes(range(32))


def test_bad_checksum_is_rejected():
    words = bip39.to_mnemonic(bytes(32))
    words[0], words[1] = words[1], "zoo"
    with pytest.raises(ValueError):
        bip39.from_mnemonic(words)


def test_sha512_gives_two_lists():
    b = Badge.from_text("x", "sha512")
    lists = b.mnemonic()
    assert len(lists) == 2 and all(len(ws) == 24 for ws in lists)
    assert b"".join(bip39.from_mnemonic(ws) for ws in lists) == b.digest
