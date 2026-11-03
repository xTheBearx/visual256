"""Tune each theme's highlight streak and its 8 gradient colors.

1. Streak: a white sheen, 0.6 opacity on light themes and up to 0.22 on dark themes, as bright as
   the palette allows (palette colors keep 1.8:1 contrast inside the narrow streak band).
2. Gradient colors: for each of 8 hues, the deepest color of that hue (90% saturation; on light
   themes no darker than lightness 0.72) that keeps every palette color at 2:1 contrast and
   handle text at 4.5:1, and 1.8:1 under the streak.

3. Light-to-dark tones: for each hue, the lightest and the darkest color of that hue (90%
   saturation; on light themes no darker than lightness 0.6) that pass the same checks.

Prints SHEEN, PARTNERS and TONES tables to paste into src/visual256/themes.py:

    python tools/tune_gradients.py
"""

import colorsys

from visual256.canvas import parse_color
from visual256.themes import HUE_NAMES, THEMES_LIST, luminance

HUES = (0, 28, 52, 125, 185, 218, 268, 318)  # degrees, matching HUE_NAMES
assert len(HUES) == len(HUE_NAMES)


def rgb(h):
    return [int(h[i:i + 2], 16) for i in (1, 3, 5)]


def hexc(c):
    return "#" + "".join(f"{round(max(0, min(255, v))):02X}" for v in c)


def mix(a, b, t):
    return hexc([x + (y - x) * t for x, y in zip(rgb(a), rgb(b))])


def over(bg, rgba):
    fg, a = parse_color(rgba)
    return mix(bg, fg, a)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def readable(theme, ground, minimum=2.0):
    return (all(contrast(p, ground) >= minimum for _, p in theme.palette)
            and contrast(theme.handle, ground) >= minimum * 2.25)


def is_dark(theme):
    return luminance(theme.bg) < 0.2


def best_sheen(theme):
    if not is_dark(theme):
        return 0.6
    best = 0.0
    for i in range(1, 45):
        a = i / 200
        if readable(theme, over(theme.bg, f"rgba(255,255,255,{a:.3f})"), 1.8):
            best = a
        else:
            break
    return round(best, 3)


def best_partner(theme, hue, sheen):
    """Walk lightness from the background's end of the scale toward the middle at full saturation."""
    # Light themes stop at vivid pastels (lightness 0.72) so bright hues never turn neon.
    steps = [i / 200 for i in range(2, 101)] if is_dark(theme) else [1 - i / 200 for i in range(2, 57)]
    best = theme.bg
    for light in steps:
        c = hexc([v * 255 for v in colorsys.hls_to_rgb(hue / 360, light, 0.9)])
        if readable(theme, c) and readable(theme, over(c, sheen), 1.8):
            best = c
        else:
            break
    return best


def tone_range(theme, hue, sheen):
    """Lightest and darkest passing colors of a hue, as a (light, dark) pair."""
    passing = []
    low = 2 if is_dark(theme) else 120  # light themes keep the dark end at lightness 0.6 or more
    for i in range(low, 199):
        c = hexc([v * 255 for v in colorsys.hls_to_rgb(hue / 360, i / 200, 0.9)])
        if readable(theme, c) and readable(theme, over(c, sheen), 1.8):
            passing.append(c)
    if not passing:
        return theme.bg, theme.bg
    return passing[-1], passing[0]


def main():
    sheens, partners = {}, {}
    for t in THEMES_LIST:
        a = best_sheen(t)
        sheens[t.id] = f"rgba(255,255,255,{a:g})"
        partners[t.id] = [best_partner(t, h, sheens[t.id]) for h in HUES]
    print("SHEEN = {")
    for k, v in sheens.items():
        print(f'    "{k}": "{v}",')
    print("}")
    print("PARTNERS = {")
    for k, v in partners.items():
        print(f'    "{k}": ({", ".join(chr(34) + c + chr(34) for c in v)}),')
    print("}")
    print("TONES = {")
    for t in THEMES_LIST:
        pairs = [tone_range(t, h, sheens[t.id]) for h in HUES]
        print(f'    "{t.id}": (' + ", ".join(f'("{a}", "{b}")' for a, b in pairs) + "),")
    print("}")


if __name__ == "__main__":
    main()
