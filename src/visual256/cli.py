"""Command line: visual256 FILE [options]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .render import Badge
from .themes import THEMES

FORMATS = ("svg", "png", "pdf", "datauri", "html", "words", "describe")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="visual256", description="Draw a checksum as a Netrunner ID badge.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("file", nargs="?", help="file to hash")
    src.add_argument("--text", help="hash this text instead of a file")
    src.add_argument("--hex", help="use this hex digest (64 or 128 hex characters) as-is")
    p.add_argument("--algo", default="sha256", choices=("sha256", "sha512"), help="hash algorithm (default sha256)")
    p.add_argument("--theme", default="cyberpunk", choices=tuple(THEMES), help="render theme (default cyberpunk)")
    p.add_argument("--format", default="svg",
                   help="comma-separated: " + ", ".join(FORMATS) + " (default svg)")
    p.add_argument("--width", type=int, default=256, help="output width in pixels (default 256)")
    p.add_argument("-o", "--output", help="output path without extension (default: input name or 'badge')")
    p.add_argument("--version", action="version", version=f"visual256 {__version__}")
    a = p.parse_args(argv)

    try:
        if a.hex:
            badge = Badge.from_hex(a.hex)
        elif a.text is not None:
            badge = Badge.from_text(a.text, a.algo)
        else:
            badge = Badge.from_file(a.file, a.algo)
    except (OSError, ValueError) as e:
        print(f"visual256: {e}", file=sys.stderr)
        return 2

    formats = [f.strip() for f in a.format.split(",") if f.strip()]
    bad = [f for f in formats if f not in FORMATS]
    if bad:
        print(f"visual256: unknown format {', '.join(bad)}; choose from {', '.join(FORMATS)}", file=sys.stderr)
        return 2
    stem = Path(a.output) if a.output else Path(Path(a.file).name if a.file else "badge")

    for fmt in formats:
        try:
            if fmt == "svg":
                out = stem.with_name(stem.name + ".svg")
                out.write_text(badge.svg(a.theme, a.width), encoding="utf-8")
                print(out)
            elif fmt == "png":
                out = stem.with_name(stem.name + ".png")
                out.write_bytes(badge.png(a.theme, a.width))
                print(out)
            elif fmt == "pdf":
                out = stem.with_name(stem.name + ".pdf")
                out.write_bytes(badge.pdf(a.theme, a.width))
                print(out)
            elif fmt == "datauri":
                print(badge.data_uri(a.theme, a.width))
            elif fmt == "html":
                print(badge.html_img(a.theme, a.width))
            elif fmt == "words":
                for i, words in enumerate(badge.mnemonic()):
                    prefix = f"part {i + 1}: " if len(badge.parts) > 1 else ""
                    print(prefix + " ".join(words))
            elif fmt == "describe":
                for i, rows in enumerate(badge.describe(a.theme)):
                    if len(badge.parts) > 1:
                        print(f"# part {i + 1}")
                    for bits, label, value in rows:
                        print(f"{bits:>8}  {label:<18} {value}")
        except RuntimeError as e:
            print(f"visual256: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
