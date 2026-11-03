# visual256

Turn a 256-bit checksum into a small picture people can recognize and compare at a glance, and a
512-bit checksum into a numbered pair of them.

> **Development version 0.1.** The bit layout, themes and drawings may still change. Every
> change stays at 0.1 until the first release, so badges are not yet stable between commits.

The first style is the **Netrunner ID**: a 128 × 64 badge with a portrait, a two-word handle, a
status chip, signal bars, 12 printed characters on colored chips and 10 detail cells. The portrait
is one of 128 subjects: android heads, buildings, animals, vehicles, plants, furniture, food, sports
equipment, musical instruments, computer symbols, large shapes and sci-fi insignia. The badge bits
pick one of eight themes, 4 dark and 4 light, each with its own background hue, pattern, fonts and
palette, and a background gradient (theme color into one of 8 hues, or that hue from light to dark)
in one of four directions:

| | | | |
|---|---|---|---|
| ![cyberpunk](docs/examples/cyberpunk.svg)<br>Cyberpunk · `release-1.2.tar.gz` | ![daylight](docs/examples/daylight.svg)<br>Daylight · `release-1.0.tar.gz` | ![paper](docs/examples/paper.svg)<br>Paper · `release-1.15.tar.gz` | ![blueprint](docs/examples/blueprint.svg)<br>Blueprint · `release-1.17.tar.gz` |
| ![candy](docs/examples/candy.svg)<br>Candy · `release-1.30.tar.gz` | ![mint](docs/examples/mint.svg)<br>Mint · `release-1.6.tar.gz` | ![ember](docs/examples/ember.svg)<br>Ember · `release-1.9.tar.gz` | ![jungle](docs/examples/jungle.svg)<br>Jungle · `release-1.1.tar.gz` |

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
| 0–2 | Theme | 8 looks: background, pattern, fonts and the 16-color palette |
| 3–4 | Background gradient | left to right, top to bottom, diagonal or radial |
| 5 | Gradient tone | theme color into the hue, or the hue from light to dark |
| 6–8 | Gradient color | red, orange, yellow, green, cyan, blue, violet or magenta |
| 9–11 | Card layout | 8 arrangements of face, handle, bars, chips and detail |
| 12–13 | Detail display | tiles, gems, hex pairs or arrows |
| 14–15 | Frame corners | which corners of the frame are cut |
| 16–17 | Frame style | single, double, dashed or corner brackets |
| 18–19 | Bar style | segmented, solid, lollipops or chevrons |
| 20–23 | Frame color | frame and dividers |
| 24–27 | Visor color | visor, lit windows, eyes, blooms and fill patterns |
| 28–31 | Trim color | outlines, roofs, doors, mouths, marks and decal |
| 32–35 | Accent color | signal bars and handle effects |
| 36–42 | Subject | 128 subjects in 12 kinds (listed below) |
| 43–45 | Subject detail A | visor, windows, eyes, blooms, or a fill pattern (8 each) |
| 46–48 | Subject detail B | mouth, door, nose, trail, pot, companion, serving, gear or backdrop (8 each) |
| 49–50 | Subject detail C | head mod, roof add-on, accessory, visitor, wall item, topper, motion or effect (4 each) |
| 51–54 | Subject symbol | decal, sign, mark, emblem, label or badge (16 symbols) |
| 55–56 | Subject detail D | cheeks, grounds, markings, livery, ground extras, floor, side item, pitch or base (4 each) |
| 57–59 | Status word | one of 8 words |
| 60–63 | Status color | status chip |
| 64–66 | Handle style | clean, split, vertical split, slice, inverted, underline, boxed or shadow |
| 67–77 | Handle word 1 | BIP-39 word, 1 of 2048 |
| 78–88 | Handle word 2 | BIP-39 word, 1 of 2048 |
| 89–103 | Signal bars | 5 bars, 1–8 levels each |
| 104–115 | Chip colors | 3 chips, 16 theme colors each |
| 116–175 | Characters | 12 characters, 4 per chip |
| 176–255 | Detail cells | 10 cells, one badge byte each |

The first 89 bits are headline features people remember. The other 167 bits are detail for a
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

**Subjects.** Bits 36–42 pick the portrait from 128 subjects in twelve kinds:

- 3 android heads: dome, bucket, skull
- 10 buildings: house, skyscraper, castle, pagoda, observatory, lighthouse, factory, temple, windmill,
  needle tower
- 10 animals: cat, dog, rabbit, fox, owl, mouse, frog, penguin, lion, panda
- 10 vehicles: car, bus, bicycle, locomotive, sailboat, submarine, helicopter, hot-air balloon, rocket,
  flying saucer
- 10 plants: pine, oak, palm, cactus, sunflower, bonsai, fern, bamboo, cherry blossom, lotus
- 8 pieces of furniture: armchair, sofa, bed, bookshelf, grandfather clock, floor lamp, piano,
  bathtub
- 8 foods: pizza slice, burger, ice cream cone, cupcake, donut, popsicle, ramen bowl, hot dog
- 5 pieces of sports equipment: soccer ball, tennis racket, skateboard, bowling pin, boxing glove
- 16 musical instruments: guitar, violin, drum, trumpet, saxophone, flute, harp, xylophone, maracas,
  tambourine, accordion, harmonica, handbell, french horn, cymbals, metronome
- 16 computer symbols: floppy disk, monitor, computer mouse, keyboard, power button, wifi, cursor,
  folder, battery, game controller, chip, padlock, cloud, envelope, hourglass, magnifier
- 16 large basic shapes: circle, square, triangle, diamond, star, hexagon, heart, crescent, plus,
  x-cross, arrow, bolt, drop, ring, semicircle, chevron
- 16 sci-fi insignia (an original set): winged orb, triple chevron, ringed star, spread wings, crossed
  blades, banded shield, crown, rising sun, trident, bolt hexagon, atom, ringed planet, anchor,
  compass star, cog, laurel

The five subject detail fields mean different things for each kind:

| Field | Android head | Building | Animal | Vehicle | Plant | Furniture | Food | Sports |
|---|---|---|---|---|---|---|---|---|
| Detail A (8) | visor | window pattern | eye style | window pattern | blooms: berries, blossoms, stars, hearts, apples, lemons, sparkles, bells | fabric: stripes, bands, polka dots, checks, diamonds, zigzag, plaid, scales | toppings: sprinkles, seeds, dots, stars, hearts, drizzle, chips, rings | print: the same 8 patterns as fabric |
| Detail B (8) | mouth | door | nose and mouth | trail: smoke, flames, speed lines, sparks, bubbles, vapor, stars, zigzag | pot: terracotta, planter, bowl, vase, crate, mound, jar, teacup | companion: cat, book stack, potted plant, teapot, radio, globe, candle, gift box | serving: round plate, wooden board, napkin, tray, cake stand, picnic cloth, leaf, bento box | gear: whistle, water bottle, trophy, medal, stopwatch, cone, cap, corner flag |
| Detail C (4) | antenna, ear discs, cable, fin | antenna, flag, chimney, satellite dish | collar, bow, bow tie, scarf | antenna, flag, siren, fin | butterfly, bee, bird, ladybug | picture frame, round mirror, window, bunting | cherry, candle, flag pick, mint leaf | motion: speed lines, sparks, stars, dust puffs |
| Symbol (16) | forehead decal | sign plaque | forehead mark | emblem | pot label | plaque | label | team badge |
| Detail D (4) | stripes, dots, circuit, bolts | steps, fence, bushes, lamp posts | whiskers, spots, blush, stripes | stripe, double stripe, checker band, zigzag stripe | grass tufts, pebbles, fallen petals, seedlings | oval rug, floorboards, checker tiles, fringed rug | fork, spoon, chopsticks, cup | pitch: grass, court lines, wood floor, ice |

The four icon kinds (instruments, computer symbols, shapes and insignia) share their details: a fill
pattern (the same 8 as fabric), a backdrop (circle, square, diamond, hexagon, shield, starburst, ring
or banner), an effect (music notes, sparkles, rays or orbit dots), a base (underline, brackets,
dotted line or pedestal) and a badge symbol. Their geometry lives in `icons.py` as plain data, which
`docs/build_lab.py` exports to the browser lab.

The owl and the panda never wear the bow tie: where other animals would get one, they get no
accessory. They are the closest look-alikes of the fox and the cat, so this keeps each pair apart.

**Themes** set the background, its pattern, the fonts and the 16 colors that every color feature
indexes into. The badge bits then pick one of 8 hues (red, orange, yellow, green, cyan, blue,
violet or magenta) and a tone: either the theme color fading into the hue, or the hue itself from
light to dark. The gradient runs left to right, top to bottom, diagonally or radially, with a
highlight streak along the same direction (a ring for radial gradients). That gives 64
backgrounds per theme. `tools/tune_gradients.py` picks each theme's streak strength, its 8
gradient colors and its 8 light-to-dark tone pairs as strong as the palette allows: every palette color keeps at least 2:1 contrast
against the background and every gradient color, and 1.8:1 inside the narrow streak band
(checked by the tests).

**512-bit checksums** (SHA-512) are drawn as two badges in one frame, numbered 1 and 2. Both
badges depend on the whole checksum. The frame takes its colors from badge 1's theme.

![SHA-512 of "hello"](docs/examples/sha512-pair.svg)

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
