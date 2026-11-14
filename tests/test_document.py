import hashlib
import os
import re

import pytest

from visual256 import Badge, document as doc
from visual256.canvas import Canvas
from visual256.themes import delta_e, lab, luminance


def bits_for(i: int) -> bytes:
    return doc.doc_mix(hashlib.sha256(f"doc-{i}".encode()).digest())[0]


def render(f, hx="ab" * 32) -> str:
    c = Canvas(128, 64)
    doc.draw_document(c, f, hx)
    return c.to_svg()


def test_layout_adds_up_to_256_bits():
    head = sum(n for _, n, _, _ in doc.DOC_FIELDS)
    assert head + 12 * 5 + 2 * 3 + 7 + doc.N_BANDS * 3 + doc.N_GLYPHS * doc.GLYPH_BITS == 256
    assert (doc.N_GLYPHS, doc.N_BANDS, doc.GLYPH_BITS) == (6, 12, 14)
    assert len(doc.DOC_SUBJECTS) == 128 and len(set(doc.DOC_SUBJECTS)) == 128
    assert len(doc.SHEETS) == 16 and len(doc.OUTLINES) == len(doc.MOTIFS) == 8
    assert len(doc.FRAME_STYLES) == len(doc.BOX_SHAPES) == len(doc.BACKINGS) == len(doc.GLYPH_FILLS) == 4
    assert sum(k == "engineering" for k, _ in doc.DOC_SUBJECTS) == 17
    assert len(doc.CODE_WORDS) == 16 and len({w[0] for w in doc.CODE_WORDS}) == 16


def test_round_trip_for_random_and_edge_values():
    for b in [bytes(32), b"\xff" * 32] + [os.urandom(32) for _ in range(300)]:
        assert doc.doc_encode(doc.doc_decode(b)) == b


def test_every_bit_changes_a_feature_and_the_drawing():
    base = bits_for(1)
    f0, svg0 = doc.doc_decode(base), render(doc.doc_decode(base))
    for bit in range(256):
        flipped = bytearray(base)
        flipped[bit >> 3] ^= 0x80 >> (bit & 7)
        f = doc.doc_decode(bytes(flipped))
        assert f != f0, bit
        assert render(f) != svg0, bit


def test_document_bits_differ_from_netrunner_bits():
    d = hashlib.sha256(b"x").digest()
    assert Badge(d, "document").parts != Badge(d).parts
    assert len(doc.doc_mix(d + d)) == 2
    with pytest.raises(ValueError):
        Badge(d, "poster")


def test_every_subject_outline_motif_and_sheet_renders():
    f = doc.doc_decode(bits_for(2))
    seen = set()
    for s in range(128):
        seen.add(render(doc.doc_with_changes(f, subject=s, theme=s % 16, key=(s // 16) % 8, side=s % 2)))
    assert len(seen) == 128
    fields = {name: 1 << bits for name, bits, _, _ in doc.DOC_FIELDS if not name.startswith("word")}
    assert fields["theme"] == 16 and fields["mtint"] == fields["fcolor"] == fields["bcolor"] == fields["ccolor"] == 8
    for field, n in fields.items():
        for motif in range(8) if field == "mtint" else (f.motif,):  # the motif color shows on every motif
            g = doc.doc_with_changes(f, motif=motif) if field != "motif" else f
            assert len({render(doc.doc_with_changes(g, **{field: v})) for v in range(n)}) == n, field


def test_every_glyph_mark_band_and_chip_value_shows():
    f = doc.doc_decode(bits_for(5))
    # every backing, color pair and fill of a large glyph looks different (with 2 of the 16 shapes) ...
    values = [v << 4 | shape for v in range(1 << 10) for shape in (4, 13)]
    assert len({render(doc.doc_with_changes(f, glyphs=(v,) + f.glyphs[1:])) for v in values}) == len(values)
    for slot in (0, 5):  # ... and so does every shape in every fill, on a tile and in a frame
        values = [back << 12 | 3 << 9 | fill << 7 | 5 << 4 | shape for back in (0, 3) for fill in range(4) for shape in range(16)]
        glyphs = lambda v: f.glyphs[:slot] + (v,) + f.glyphs[slot + 1:]
        assert len({render(doc.doc_with_changes(f, glyphs=glyphs(v))) for v in values}) == len(values)
    assert doc.glyph_parts(0b10_011_01_110_0101) == (2, 3, 1, 6, 5)
    assert len({render(doc.doc_with_changes(f, mark=v)) for v in range(128)}) == 128
    for i in range(doc.N_BANDS):
        spine = lambda v: f.spine[:i] + (v,) + f.spine[i + 1:]
        assert len({render(doc.doc_with_changes(f, spine=spine(v))) for v in range(8)}) == 8
    assert len({render(doc.doc_with_changes(f, chips=(a, b))) for a in range(8) for b in range(8)}) == 64


def test_describe_covers_all_bits_in_order():
    rows = doc.doc_describe(doc.doc_decode(bits_for(3)))
    pos = 0
    for rng, _label, value in rows:
        a, b = map(int, rng.split("-"))
        assert a == pos and value
        pos = b + 1
    assert pos == 256


def test_palettes_are_distinct_and_readable():
    for sheet in doc.SHEETS:
        assert len(set(sheet.names)) == 8
        colors = [c for _, c in sheet.palette]
        labs = [lab(c) for c in colors]
        closest = min(delta_e(labs[i], labs[j]) for i in range(8) for j in range(i))
        assert closest >= 15, (sheet.name, closest)
        for c in colors + [sheet.ink]:
            hi, lo = sorted((luminance(c), luminance(sheet.bg)), reverse=True)
            assert (hi + .05) / (lo + .05) >= 2, (sheet.name, c)


def test_sheets_are_told_apart_by_their_paper_color():
    labs = [lab(s.bg) for s in doc.SHEETS]
    assert len({s.name for s in doc.SHEETS}) == 16
    assert min(delta_e(labs[i], labs[j]) for i in range(16) for j in range(i)) >= 11


def test_badge_api_and_checksum_digits():
    b = Badge.from_text("hello", style="document")
    svg = b.svg()
    assert 'width="256"' in svg and 'height="128"' in svg
    assert "filter" not in svg and "Gradient" not in svg  # flat: no glow, no gradients
    assert b.describe()[0][0] == ("0-3", "Theme", doc.SHEETS[b.features[0].theme].name)
    assert b.svg() != Badge.from_text("hellp", style="document").svg()
    pair = Badge.from_text("hello", "sha512", "document")
    assert len(pair.features) == 2 and pair.svg(300).startswith("<svg")
    assert b.png(256)[:4] == b"\x89PNG" and b.pdf()[:4] == b"%PDF"


def test_cli_style_option(tmp_path, capsys):
    from visual256.cli import main
    assert main(["--text", "hello", "--style", "document", "--format", "describe,svg", "-o", str(tmp_path / "b")]) == 0
    assert "Glyph 6" in capsys.readouterr().out and (tmp_path / "b.svg").exists()
