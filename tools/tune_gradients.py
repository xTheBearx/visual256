"""Find the most pronounced gradient partner colors each theme can take.

For each partner, mix from the theme background toward a vivid target color and keep the
largest mix where every palette color still has 2:1 contrast (and handle text 4.5:1) against the
partner and against the partner under the highlight streak. Prints a PARTNERS table to paste into
src/visual256/themes.py.

    python tools/tune_gradients.py
"""

from visual256.canvas import parse_color
from visual256.themes import THEMES_LIST, luminance

TARGETS = {
    "cyberpunk": (("violet haze", "#8A2BE2"), ("deep teal", "#008C9E")),
    "daylight": (("ice blue", "#7FB2FF"), ("peach", "#FFB08A")),
    "paper": (("parchment", "#D9A955"), ("rose paper", "#E8A08A")),
    "blueprint": (("midnight", "#00040F"), ("sea blue", "#1A8FB8")),
    "candy": (("lavender", "#B395FF"), ("vanilla", "#FFC24D")),
    "mint": (("aqua", "#7FD6F0"), ("pistachio", "#B8E05A")),
    "arcade": (("purple", "#3D0078"), ("cobalt", "#00287A")),
    "stealth": (("olive", "#4A4A1A"), ("gunmetal", "#0A1424")),
    "ember": (("rust glow", "#A03A06"), ("plum", "#5A0848")),
    "abyss": (("trench blue", "#000C4A"), ("kelp", "#0A5030")),
    "sky": (("lavender", "#C2A8FF"), ("aqua", "#6FDCC6")),
    "royal": (("wine", "#A0185E"), ("indigo", "#2A1AB0")),
    "citrus": (("peach", "#FFB070"), ("lime", "#B0E050")),
    "jungle": (("lagoon", "#06606E"), ("moss", "#5A7A08")),
    "lilac": (("pink", "#F4A6D0"), ("periwinkle", "#9FB8F2")),
    "concrete": (("sandstone", "#D9A050"), ("steel", "#7F9CBB")),
}


def rgb(h):
    return [int(h[i:i + 2], 16) for i in (1, 3, 5)]


def hexc(c):
    return "#" + "".join(f"{round(max(0, min(255, v))):02X}" for v in c)


def mix(a, b, t):
    return hexc([x + (y - x) * t for x, y in zip(rgb(a), rgb(b))])


def over(bg, color):
    """Composite an rgba() color over a hex background."""
    fg, a = parse_color(color)
    return mix(bg, fg, a)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def ok(theme, color):
    for c in (color, over(color, theme.sheen)):
        if any(contrast(p, c) < 2.0 for _, p in theme.palette) or contrast(theme.handle, c) < 4.5:
            return False
    return True


def main():
    print("PARTNERS = {")
    for t in THEMES_LIST:
        out = []
        for name, target in TARGETS[t.id]:
            best = t.bg
            for i in range(101):
                c = mix(t.bg, target, i / 100)
                if ok(t, c):
                    best = c
                else:
                    break
            out.append((name, best))
        print(f'    "{t.id}": (("{out[0][0]}", "{out[0][1]}"), ("{out[1][0]}", "{out[1][1]}")),')
    print("}")


if __name__ == "__main__":
    main()
