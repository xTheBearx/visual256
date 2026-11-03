import hashlib
import xml.etree.ElementTree as ET

import pytest

from visual256 import THEMES, Badge, decode, with_changes
from visual256.canvas import Canvas
from visual256.cli import main
from visual256.draw import H, W, draw_badge

BASE = decode(hashlib.sha256(b"render").digest())


@pytest.mark.parametrize("theme", list(THEMES))
@pytest.mark.parametrize("layout", range(8))
@pytest.mark.parametrize("display", range(4))
def test_every_layout_display_and_theme_draws_valid_svg(theme, layout, display):
    c = Canvas(W, H)
    draw_badge(c, with_changes(BASE, layout=layout, display=display), THEMES[theme])
    root = ET.fromstring(c.to_svg(256, 128))
    assert root.tag.endswith("svg")
    assert len(root.findall(".//{http://www.w3.org/2000/svg}path")) > 50


def test_svg_has_no_text_elements_or_external_references():
    svg = Badge.from_text("abc").svg()
    assert "<text" not in svg and "href" not in svg and "@font-face" not in svg


def test_pair_svg_for_sha512():
    b = Badge.from_text("abc", "sha512")
    w, h = b.size_for(256)
    assert w == 256 and h > 256
    ET.fromstring(b.svg(width=256))


def test_png_output():
    pytest.importorskip("resvg_py")
    png = Badge.from_text("abc").png(width=256)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_pdf_output():
    pytest.importorskip("cairosvg")
    assert Badge.from_text("abc").pdf()[:5] == b"%PDF-"


def test_data_uri_and_img_tag():
    b = Badge.from_text("abc")
    assert b.data_uri().startswith("data:image/svg+xml;base64,")
    tag = b.html_img(width=128)
    assert tag.startswith("<img ") and 'width="128"' in tag and 'height="64"' in tag


def test_rendering_is_deterministic():
    b = Badge.from_text("same input")
    assert b.svg("daylight") == b.svg("daylight")


def test_cli_writes_files(tmp_path, capsys):
    target = tmp_path / "file.bin"
    target.write_bytes(b"hello world")
    out = tmp_path / "badge"
    assert main([str(target), "--format", "svg,words,describe", "-o", str(out), "--theme", "paper"]) == 0
    assert (tmp_path / "badge.svg").exists()
    printed = capsys.readouterr().out
    assert len(printed.splitlines()[1].split()) == 24
    assert "Handle word 1" in printed


def test_cli_hex_input_and_errors(capsys):
    digest = hashlib.sha256(b"x").hexdigest()
    assert main(["--hex", digest, "--format", "words"]) == 0
    assert main(["--hex", "abc", "--format", "words"]) == 2
    assert main(["--text", "x", "--format", "gif"]) == 2
