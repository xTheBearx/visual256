# visual256

Turn a 256-bit checksum into a small picture people can recognize and compare at a glance, and a
512-bit checksum into a numbered pair of them.

> **Development version 0.1.** The bit layout, themes and drawings may still change. Every
> change stays at 0.1 until the first release, so badges are not yet stable between commits.

The first style is the **Netrunner ID**: a 128 × 64 badge with an android head, a two-word
handle, a status chip, signal bars, 12 printed characters on colored chips and 10 detail cells.
The badge bits pick one of sixteen themes, 8 dark and 8 light, each on a different background hue,
and a background gradient toward one of two partner colors in one of four directions:

| | | | |
|---|---|---|---|
| ![cyberpunk](docs/examples/cyberpunk.svg)<br>Cyberpunk · `release-1.2.tar.gz` | ![daylight](docs/examples/daylight.svg)<br>Daylight · `release-1.3.tar.gz` | ![paper](docs/examples/paper.svg)<br>Paper · `release-1.7.tar.gz` | ![blueprint](docs/examples/blueprint.svg)<br>Blueprint · `release-1.0.tar.gz` |
| ![candy](docs/examples/candy.svg)<br>Candy · `release-1.15.tar.gz` | ![mint](docs/examples/mint.svg)<br>Mint · `release-1.4.tar.gz` | ![arcade](docs/examples/arcade.svg)<br>Arcade · `release-1.14.tar.gz` | ![stealth](docs/examples/stealth.svg)<br>Stealth · `release-1.25.tar.gz` |
| ![ember](docs/examples/ember.svg)<br>Ember · `release-1.5.tar.gz` | ![abyss](docs/examples/abyss.svg)<br>Abyss · `release-1.23.tar.gz` | ![sky](docs/examples/sky.svg)<br>Sky · `release-1.6.tar.gz` | ![royal](docs/examples/royal.svg)<br>Royal · `release-1.10.tar.gz` |
| ![citrus](docs/examples/citrus.svg)<br>Citrus · `release-1.18.tar.gz` | ![jungle](docs/examples/jungle.svg)<br>Jungle · `release-1.9.tar.gz` | ![lilac](docs/examples/lilac.svg)<br>Lilac · `release-1.1.tar.gz` | ![concrete](docs/examples/concrete.svg)<br>Concrete · `release-1.12.tar.gz` |

Each example is the real SHA-256 badge of the file name shown.

## Install

```bash
pip install "visual256[all] @ git+https://github.com/xTheBearx/visual256"
```

The core package needs only `fonttools`. The extras add output formats:

| Extra | Adds | Uses |
|---|---|---|
| `png` | PNG output | `resvg-py` |
| `pdf` | PDF output (no neon glow) | `cairosvg` |
| `all` | both | |

## Command line

```bash
visual256 release.tar.gz --format svg,png --width 256
```

```bash
visual256 --text "hello" --algo sha512 --format svg
```

```bash
visual256 --hex 5a725ab992a13c91274e2cc90248be7fe397a725a8a530ea09312bbd5d78e18e --format describe,words
```

Formats: `svg`, `png`, `pdf`, `datauri`, `html` (an `<img>` tag), `words` (24-word spoken backup)
and `describe` (every feature in plain language). Files are written next to the input, or to the
path given with `-o` (without extension).

## Python

```python
from visual256 import Badge

badge = Badge.from_file("release.tar.gz")   # or from_text, from_hex, from_bytes
svg = badge.svg(width=256)                   # str
png = badge.png(width=512)                   # bytes, needs resvg-py
tag = badge.html_img(width=128)              # <img> with an embedded SVG
words = badge.mnemonic()                     # [[24 BIP-39 words]] per 256-bit part
for bits, label, value in badge.describe()[0]:
    print(bits, label, value)
```

`badge.parts` holds the mixed badge bits (`visual256.mix(checksum)`). `visual256.decode(bits)`
returns a badge's `Features`; `visual256.encode(features)` turns them back into the same 32 bytes.

## How a checksum becomes a badge

**1. Mixing.** The checksum is not drawn directly. Each badge shows
`SHA-256("visual256/netrunner/0.1" || part number || whole checksum)`. Flipping any single bit of
the checksum changes about half of the badge bits, so the new badge looks unrelated: usually a
different theme, layout, face and handle. Two different checksums give different badges unless
SHA-256 itself collides. The picture is a fingerprint and cannot be turned back into the
checksum; the spoken backup below encodes the checksum itself.

**2. Drawing.** The 256 badge bits are read most significant first.

| Bits | Feature | Values |
|---|---|---|
| 0–3 | Theme | 16 looks: background, pattern, fonts and the 16-color palette |
| 4–5 | Background gradient | left to right, top to bottom, diagonal or radial |
| 6 | Gradient color | which of the theme's two partner colors the background fades to |
| 7–9 | Card layout | 8 arrangements of face, handle, bars, chips and detail |
| 10–11 | Detail display | tiles, gems, hex pairs or arrows |
| 12–13 | Frame corners | which corners of the frame are cut |
| 14–15 | Frame style | single, double, dashed or corner brackets |
| 16–17 | Bar style | segmented, solid, lollipops or chevrons |
| 18–21 | Frame color | frame and dividers |
| 22–25 | Visor color | visor |
| 26–29 | Trim color | head outline, mods, mouth, cheek marks and decal |
| 30–33 | Accent color | signal bars and handle effects |
| 34–36 | Head shape | round, angular, boxy, dome, capsule, bucket, shield or skull |
| 37–39 | Visor style | band, twin-lens, slit, mono-eye, goggles, chevron, triple-lens or grid |
| 40–42 | Mouth | vents, teeth, dots, LED, zigzag, speaker, fangs or stitches |
| 43–44 | Head mod | antenna, ear discs, cable or fin |
| 45–48 | Forehead decal | one of 16 symbols |
| 49–50 | Cheek marks | stripes, dots, circuit or bolts |
| 51–54 | Status word | one of 16 words |
| 55–58 | Status color | status chip |
| 59–60 | Rank | 1 to 4 chevrons on the status chip |
| 61–63 | Handle style | clean, split, vertical split, slice, inverted, underline, boxed or shadow |
| 64–74 | Handle word 1 | BIP-39 word, 1 of 2048 |
| 75–85 | Handle word 2 | BIP-39 word, 1 of 2048 |
| 86–103 | Signal bars | 6 bars, 1–8 levels each |
| 104–115 | Chip colors | 3 chips, 16 theme colors each |
| 116–175 | Characters | 12 characters, 4 per chip |
| 176–255 | Detail cells | 10 cells, one badge byte each |

The first 86 bits are headline features people remember. The other 170 bits are detail for a
careful side-by-side check. Detail elements are kept large on purpose: each detail cell carries a
whole byte through color, shape and fill instead of many tiny marks. Every badge bit is drawn:
`encode(decode(bits)) == bits`.

**Characters** use a 32-letter alphabet with no I, O, 0 or 1: `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`.

**Detail displays** draw each byte as one of:

- **tiles**: a colored tile (high 4 bits) with a symbol (low 4 bits)
- **gems**: a colored shape; color (4 bits) × circle, square, triangle or diamond × solid, outline,
  dotted or half-filled
- **hex pairs**: two hex digits on a seven-segment display
- **arrows**: 8 directions × 16 colors × solid or outline

**Themes** set the background, its pattern, the fonts and the 16 colors that every color feature
indexes into. Each theme also has two partner colors; the card fades from the theme color to one
of them left to right, top to bottom, diagonally or radially. Every palette color has at least
2:1 contrast against the background and both partners (checked by the tests).

**512-bit checksums** (SHA-512) are drawn as two badges in one frame, numbered 1 and 2. Both
badges depend on the whole checksum. The frame takes its colors from badge 1's theme.

## Spoken backup

`badge.mnemonic()` and `--format words` give the standard BIP-39 encoding of the checksum itself,
per 256-bit part:
24 words, where the last word also carries an 8-bit checksum. It is useful for reading a checksum
over the phone. `visual256.bip39.from_mnemonic(words)` turns the words back into bytes and checks
the checksum; the first four letters of each word are enough.

## Browser preview

[`docs/netrunner-lab.html`](docs/netrunner-lab.html) is a self-contained page that draws the same
badges in the browser, with every layout, display and theme side by side, a one-bit-flip test and
a readout of every feature. It is built from `docs/lab-template.html` by `python docs/build_lab.py`,
which injects the theme collection and word list from the package. Its drawing code mirrors
`src/visual256/draw.py`; change both together.

## Development

```bash
pip install -e ".[dev]"
```

```bash
pytest
```

The tests check that every badge value survives `encode(decode(x))`, that flipping any single
checksum bit changes more than a quarter of the bits of every badge, the official BIP-39 test
vectors, palette contrast in every theme, and that every theme × layout × display combination and
every value of each face feature draws valid SVG.

## License

MIT, see [LICENSE](LICENSE). Bundled third-party material keeps its own license:

## Third-party material

- `src/visual256/data/bip39_english.txt`: the BIP-39 English word list from
  [bitcoin/bips](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt), MIT license.
  Its SHA-256 is checked at load time.
- `src/visual256/fonts/`: subsets of Chakra Petch, JetBrains Mono, Spectral, Audiowide,
  Silkscreen and Saira Stencil One, under the SIL Open Font License 1.1 (license texts
  alongside). Text in every output is drawn as outlines, so no fonts need to be installed.
- `tests/data/bip39_vectors_256.json`: the 256-bit English entries from
  [trezor/python-mnemonic](https://github.com/trezor/python-mnemonic/blob/master/vectors.json),
  MIT license.
