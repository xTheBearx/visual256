"""Push each theme's 16 palette colors apart so no two look alike on a small badge.

Every color feature (frame, visor, trim, accent, status, chips, detail cells) indexes a theme's
16-color palette, so two near-identical palette colors make two different bit values look the same.
This hill-climbs each palette to raise its smallest CIEDE2000 difference, nudging hue, saturation
and lightness of the colors in the closest pairs, while every color

- stays within MAX_HUE_DRIFT degrees of its original hue (so its name still fits), and
- keeps at least MIN_CONTRAST against the theme background, and
- gets no closer to the background than the palette's original closest color (on dark themes no
  darker than its darkest color, on light themes no lighter than its lightest), because the
  gradient tuner can only push the background as far as the palette's weakest color allows.

Prints the palettes to paste into src/visual256/themes.py; then re-run tools/tune_gradients.py,
because the gradient partners and tones are tuned against the palette:

    python tools/spread_palettes.py
"""

import colorsys
import itertools
import math
import random

from visual256.themes import THEMES_LIST, delta_e, lab, luminance

MAX_HUE_DRIFT = 15.0
MIN_CONTRAST = 2.08  # a little above the 2:1 rule, so the gradient tuner keeps some room
TARGET = 16.0  # stop improving a palette once its closest pair reaches this


def to_hls(hexc):
    r, g, b = (int(hexc[k:k + 2], 16) / 255 for k in (1, 3, 5))
    return colorsys.rgb_to_hls(r, g, b)


def to_hex(h, l, s):
    return "#" + "".join(f"{round(v * 255):02X}" for v in colorsys.hls_to_rgb(h % 1, l, s))


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def hue_dist(a, b):
    d = abs(a - b) % 1
    return min(d, 1 - d) * 360


def closest(colors):
    labs = [lab(c) for c in colors]
    return sorted((delta_e(labs[i], labs[j]), i, j) for i, j in itertools.combinations(range(len(colors)), 2))


def spread(theme, seed=1, steps=6000):
    rnd = random.Random(seed)
    names = [n for n, _ in theme.palette]
    colors = [c for _, c in theme.palette]
    hue0 = [to_hls(c)[0] for c in colors]
    neutral = [to_hls(c)[2] < .12 for c in colors]  # whites, greys and blacks keep their hue-free look
    dark_bg = luminance(theme.bg) < .2
    lums = [luminance(c) for c in colors]
    floor, ceiling = (min(lums), 1.0) if dark_bg else (0.0, max(lums))
    score = lambda cs: [d for d, _, _ in closest(cs)[:6]]
    best = score(colors)
    for _ in range(steps):
        if best[0] >= TARGET:
            break
        _, i, j = closest(colors)[rnd.randrange(3)]
        k = rnd.choice((i, j))
        h, l, s = to_hls(colors[k])
        h += rnd.uniform(-.012, .012) * (0 if neutral[k] else 1)
        l = min(.97, max(.04, l + rnd.uniform(-.035, .035)))
        s = min(1, max(0, s + rnd.uniform(-.06, .06) * (.2 if neutral[k] else 1)))
        cand = to_hex(h, l, s)
        if not neutral[k] and hue_dist(to_hls(cand)[0], hue0[k]) > MAX_HUE_DRIFT:
            continue
        if contrast(cand, theme.bg) < MIN_CONTRAST or not floor <= luminance(cand) <= ceiling:
            continue
        trial = colors[:k] + [cand] + colors[k + 1:]
        sc = score(trial)
        if sc > best:
            colors, best = trial, sc
    return names, colors, best[0]


def main():
    for t in THEMES_LIST:
        before = closest([c for _, c in t.palette])[0][0]
        names, colors, after = spread(t)
        print(f"# {t.name}: closest pair dE {before:.1f} -> {after:.1f}")
        body = "|".join(f"{n}:{c}" for n, c in zip(names, colors))
        print(f'{t.id} = "{body}"')


if __name__ == "__main__":
    main()
