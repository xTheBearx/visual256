"""Draws a Netrunner ID badge. Coordinates are 128 x 64 badge units on a 960 x 480 canvas.

This file mirrors the browser preview (docs/netrunner-lab.html) line for line; keep them in sync.
"""

from __future__ import annotations

import math

from .canvas import Canvas, LinearGradient, RadialGradient, parse_color
from .spec import STATUS_WORDS, Features, subject_kind
from .subjects import draw_animal, draw_building
from .themes import Theme, chip_ink, get as get_theme

S = 480.0          # canvas height
U = S / 64         # canvas pixels per badge unit
W, H = 2 * S, S    # badge canvas size
TAU = math.tau


# ---------------------------------------------------------------- primitives
def poly(ctx: Canvas, pts) -> None:
    for i, (x, y) in enumerate(pts):
        (ctx.line_to if i else ctx.move_to)(x, y)
    ctx.close_path()


def rr(ctx: Canvas, x, y, w, h, r) -> None:
    r = min(r, w / 2, h / 2)
    ctx.move_to(x + r, y)
    ctx.line_to(x + w - r, y)
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.line_to(x + w, y + h - r)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.line_to(x + r, y + h)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.line_to(x, y + r)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def star_pts(n, big, small):
    out = []
    for k in range(2 * n):
        a = -math.pi / 2 + math.pi * k / n
        q = small if k % 2 else big
        out.append((math.cos(a) * q, math.sin(a) * q))
    return out


_W = .34
PLUS = [(-_W, -1), (_W, -1), (_W, -_W), (1, -_W), (1, _W), (_W, _W), (_W, 1), (-_W, 1), (-_W, _W), (-1, _W), (-1, -_W), (-_W, -_W)]
SALT = [((x - y) * math.sqrt(.5), (x + y) * math.sqrt(.5)) for x, y in PLUS]


def sym_path(ctx: Canvas, i: int) -> None:
    ctx.begin_path()
    i &= 15
    if i == 0:
        ctx.arc(0, 0, .92, 0, TAU)
    elif i == 1:
        ctx.rect(-.8, -.8, 1.6, 1.6)
    elif i == 2:
        poly(ctx, [(0, -1), (.98, .78), (-.98, .78)])
    elif i == 3:
        poly(ctx, [(0, -1.05), (.78, 0), (0, 1.05), (-.78, 0)])
    elif i == 4:
        poly(ctx, star_pts(5, 1.05, .44))
    elif i == 5:
        poly(ctx, PLUS)
    elif i == 6:
        poly(ctx, SALT)
    elif i == 7:
        ctx.move_to(0, .95)
        ctx.bezier_curve_to(-1.35, .05, -.8, -1.1, 0, -.42)
        ctx.bezier_curve_to(.8, -1.1, 1.35, .05, 0, .95)
        ctx.close_path()
    elif i == 8:
        phi, psi = math.atan2(.8496, .5275), math.atan2(.8496, .0275)
        ctx.arc(.1, 0, 1, phi, TAU - phi, False)
        ctx.arc(.6, 0, .85, -psi, psi, True)
        ctx.close_path()
    elif i == 9:
        poly(ctx, star_pts(12, 1.02, .74))
    elif i == 10:
        ctx.move_to(0, -1.05)
        ctx.bezier_curve_to(.2, -.6, .72, -.15, .72, .3)
        ctx.arc(0, .3, .72, 0, math.pi, False)
        ctx.bezier_curve_to(-.72, -.15, -.2, -.6, 0, -1.05)
        ctx.close_path()
    elif i == 11:
        poly(ctx, [(.2, -1.05), (-.62, .14), (-.04, .14), (-.24, 1.05), (.62, -.2), (.06, -.2)])
    elif i == 12:
        poly(ctx, [(math.cos(-math.pi / 2 + k * math.pi / 3) * .98, math.sin(-math.pi / 2 + k * math.pi / 3) * .98) for k in range(6)])
    elif i == 13:
        ctx.arc(0, 0, .95, 0, TAU)
        ctx.move_to(.5, 0)
        ctx.arc(0, 0, .5, 0, TAU, True)
    elif i == 14:
        poly(ctx, [(0, -1.05), (.88, -.08), (.34, -.08), (.34, 1), (-.34, 1), (-.34, -.08), (-.88, -.08)])
    else:
        for x, y in ((0, -.5), (.5, 0), (0, .5), (-.5, 0)):
            ctx.move_to(x + .46, y)
            ctx.arc(x, y, .46, 0, TAU)
        ctx.move_to(.4, 0)
        ctx.arc(0, 0, .4, 0, TAU)


def draw_symbol(ctx: Canvas, i, x, y, r, fill) -> None:
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(r, r)
    sym_path(ctx, i)
    ctx.fill_style = fill
    ctx.fill()
    ctx.restore()


def fit_font(ctx: Canvas, text, max_w, key, size) -> float:
    s = size
    ctx.set_font(key, s)
    while s > 3 and ctx.measure_text(text) > max_w:
        s -= .25
        ctx.set_font(key, s)
    return s


def frame_poly(kind: int, inset: float = 0.0):
    c, a, x1, y1 = 5, .6 + inset, 127.4 - inset, 63.4 - inset
    cut = ((1, 0, 1, 0), (0, 1, 0, 1), (1, 1, 1, 1), (1, 1, 0, 0))[kind]
    p = []
    p += [(a, a + c), (a + c, a)] if cut[0] else [(a, a)]
    p += [(x1 - c, a), (x1, a + c)] if cut[1] else [(x1, a)]
    p += [(x1, y1 - c), (x1 - c, y1)] if cut[2] else [(x1, y1)]
    p += [(a + c, y1), (a, y1 - c)] if cut[3] else [(a, y1)]
    return p


class Glow:
    def __init__(self, ctx: Canvas, theme: Theme):
        self.ctx, self.on = ctx, theme.glow

    def __call__(self, color, blur=2.0):
        if self.on:
            self.ctx.shadow_color, self.ctx.shadow_blur = color, blur * U

    def off(self):
        self.ctx.shadow_blur = 0


# ---------------------------------------------------------------- layouts
def layout_spec(L: int) -> dict:
    """Regions for each of the 8 layouts, in badge units."""
    def stacked(x0, x1):
        return dict(handle=[dict(text="both", x=x0, y=11.8, w=x1 - x0, align="left", size=8.4)],
                    bars=[dict(ids=list(range(5)), x0=x0, x1=x1, y0=14.2, y1=24.2)],
                    chips=[dict(ids=[0, 1, 2], x0=x0, y0=26.2, x1=x1, y1=34.6, col=False)],
                    cells=[dict(ids=list(range(10)), x0=x0, y0=36.8, x1=x1, y1=60, gc=5, gr=2)])

    def grid(x0, x1):
        mid = x0 + (x1 - x0) * .5
        return dict(handle=[dict(text="both", x=x0, y=11.8, w=x1 - x0, align="left", size=8.4)],
                    cells=[dict(ids=list(range(10)), x0=x0, y0=15, x1=mid - 1.3, y1=60, gc=2, gr=5)],
                    bars=[dict(ids=list(range(5)), x0=mid + 1.3, x1=x1, y0=15, y1=30.5)],
                    chips=[dict(ids=[0, 1, 2], x0=mid + 1.3, y0=33, x1=x1, y1=60, col=True)])

    def split(detail_top):
        def col(x0, x1, side):
            cx = (x0 + x1) / 2
            hd = dict(text="w2" if side else "w1", x=cx, y=11.4, w=x1 - x0, align="center", size=7.8)
            b = [3, 4] if side else [0, 1, 2]
            ch = [2] if side else [0]
            cl = [5, 6, 7, 8, 9] if side else [0, 1, 2, 3, 4]
            if detail_top:
                return dict(handle=hd, cells=dict(ids=cl, x0=x0, y0=13.8, x1=x1, y1=36.2, gc=3, gr=2),
                            chips=dict(ids=ch, x0=x0, y0=38.2, x1=x1, y1=45.6, col=False),
                            bars=dict(ids=b, x0=x0, x1=x1, y0=47.6, y1=60, slots=3))
            return dict(handle=hd, bars=dict(ids=b, x0=x0, x1=x1, y0=13.8, y1=23.4, slots=3),
                        chips=dict(ids=ch, x0=x0, y0=25.4, x1=x1, y1=32.8, col=False),
                        cells=dict(ids=cl, x0=x0, y0=35, x1=x1, y1=60, gc=3, gr=2))
        a, c = col(3.5, 40.5, 0), col(87.5, 124.5, 1)
        top_chip = dict(ids=[1], x0=47, y0=2.6, x1=81, y1=9.8, col=False)
        return dict(face=(64, 34, .88), div=[(43, 6, 43, 58), (85, 6, 85, 58)],
                    handle=[a["handle"], c["handle"]], bars=[a["bars"], c["bars"]],
                    chips=[a["chips"], top_chip, c["chips"]], cells=[a["cells"], c["cells"]])

    if L == 0:
        return dict(face=(21.5, 31, 1), div=[(42.5, 6, 42.5, 58)], **stacked(45.6, 123.4))
    if L == 1:
        return dict(face=(106.5, 31, 1), div=[(85.5, 6, 85.5, 58)], **stacked(4.4, 82.6))
    if L == 2:
        return split(False)
    if L == 3:
        return dict(face=(21.5, 31, 1), div=[(42.5, 6, 42.5, 58)], **grid(45.6, 123.4))
    if L == 4:
        return dict(face=(106.5, 31, 1), div=[(85.5, 6, 85.5, 58)], **grid(4.4, 82.6))
    if L == 5:
        return dict(face=(19.5, 39.5, .74), div=[(6, 13.6, 122, 13.6), (38, 17, 38, 60)],
                    handle=[dict(text="both", x=64, y=10.6, w=112, align="center", size=8.6)],
                    bars=[dict(ids=list(range(5)), x0=41, x1=123.4, y0=16.4, y1=24.6)],
                    chips=[dict(ids=[0, 1, 2], x0=41, y0=26.6, x1=123.4, y1=34.4, col=False)],
                    cells=[dict(ids=list(range(10)), x0=41, y0=36.6, x1=123.4, y1=60, gc=5, gr=2)])
    if L == 6:
        return dict(face=(108.5, 26.5, .74), div=[(6, 50.6, 122, 50.6), (89, 5, 89, 48)],
                    handle=[dict(text="both", x=64, y=59.4, w=112, align="center", size=8.6)],
                    cells=[dict(ids=list(range(10)), x0=4.6, y0=4.6, x1=86, y1=25.6, gc=5, gr=2)],
                    chips=[dict(ids=[0, 1, 2], x0=4.6, y0=27.6, x1=86, y1=35.2, col=False)],
                    bars=[dict(ids=list(range(5)), x0=4.6, x1=86, y0=37.4, y1=48)])
    return split(True)


# ---------------------------------------------------------------- badge
def draw_badge(ctx: Canvas, f: Features, theme: Theme | None = None) -> None:
    """Draw one badge into ctx, occupying (0, 0)-(960, 480) in ctx's current transform.
    The theme comes from the badge's own bits unless one is passed (for previews)."""
    t = theme or get_theme(f.theme)
    ctx.save()
    ctx.scale(U, U)
    acc, vis, trim, fcol = t.color(f.accent), t.color(f.visor), t.color(f.trim), t.color(f.frame)
    glow = Glow(ctx, t)
    fr = frame_poly(f.corners)
    ctx.begin_path()
    poly(ctx, fr)
    ctx.fill_style = background_gradient(t, f.gradient, f.tint, f.gtone)
    ctx.fill()
    ctx.save()
    ctx.clip()
    draw_streak(ctx, t, f.gradient)
    background(ctx, t)
    ctx.restore()
    draw_frame(ctx, f, fr, fcol, glow)
    spec = layout_spec(f.layout)
    ctx.line_width, ctx.stroke_style, ctx.global_alpha = .3, fcol, .55
    ctx.begin_path()
    for a, b, c, d in spec["div"]:
        ctx.move_to(a, b)
        ctx.line_to(c, d)
    ctx.stroke()
    ctx.global_alpha = 1
    fx, fy, fs = spec["face"]
    ctx.save()
    ctx.translate(fx, fy)
    ctx.scale(fs, fs)
    ctx.translate(-21.5, -31)
    draw_face(ctx, f, 21.5, glow, vis, trim, t)
    ctx.restore()
    w1, w2 = (w.upper() for w in f.words)
    for h in spec["handle"]:
        text = f"{w1}·{w2}" if h["text"] == "both" else (w1 if h["text"] == "w1" else w2)
        handle_text(ctx, text, h["x"], h["y"], h["w"], h["align"], f.hstyle, acc, h["size"], glow, t)
    for b in spec["bars"]:
        draw_bars(ctx, [f.bars[i] for i in b["ids"]], b["x0"], b["x1"], b["y0"], b["y1"], b.get("slots", 0),
                  f.barstyle, acc, glow, t)
    for c in spec["chips"]:
        draw_chips(ctx, f, c, t)
    for c in spec["cells"]:
        draw_cells(ctx, f, c, vis, glow, t)
    ctx.restore()


def background_gradient(t: Theme, kind: int, tint: int, tone: int = 0):
    """The card fill: the theme color fading into a hue, or that hue from light to dark."""
    if tone:
        light, dark = t.tones[tint]
        stops = [(0, light), (1, dark)]
    else:
        stops = [(0, t.bg), (1, t.gradients[tint][1])]
    if kind == 0:
        return LinearGradient(0, 32, 128, 32, stops)
    if kind == 1:
        return LinearGradient(64, 0, 64, 64, stops)
    if kind == 2:
        return LinearGradient(0, 0, 128, 64, stops)
    return RadialGradient(64, 32, 0, 72, stops)


def draw_streak(ctx: Canvas, t: Theme, kind: int) -> None:
    """A faint highlight band along the gradient direction (a ring for radial gradients)."""
    color, a = parse_color(t.sheen)
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    clear = f"rgba({r},{g},{b},0)"
    band = [(0, clear), (.5, t.sheen), (1, clear)]
    if kind == 0:
        ctx.fill_style = LinearGradient(0, 23, 0, 41, band)
        ctx.fill_rect(0, 23, 128, 18)
    elif kind == 1:
        ctx.fill_style = LinearGradient(52, 0, 76, 0, band)
        ctx.fill_rect(52, 0, 24, 64)
    elif kind == 2:
        L = math.hypot(128, 64)
        dx, dy = 128 / L, 64 / L
        nx, ny, hw = -dy, dx, 10
        ctx.fill_style = LinearGradient(64 - hw * nx, 32 - hw * ny, 64 + hw * nx, 32 + hw * ny, band)
        ctx.begin_path()
        poly(ctx, [(64 - 100 * dx - hw * nx, 32 - 100 * dy - hw * ny), (64 + 100 * dx - hw * nx, 32 + 100 * dy - hw * ny),
                   (64 + 100 * dx + hw * nx, 32 + 100 * dy + hw * ny), (64 - 100 * dx + hw * nx, 32 - 100 * dy + hw * ny)])
        ctx.fill()
    else:
        ctx.fill_style = RadialGradient(64, 32, 0, 72, [(0, clear), (.3, clear), (.42, t.sheen), (.54, clear), (1, clear)])
        ctx.fill_rect(0, 0, 128, 64)


def background(ctx: Canvas, t: Theme) -> None:
    k = t.grid_kind
    ctx.begin_path()
    if k == "grid":
        for x in range(2, 128, 4):
            ctx.move_to(x, 0)
            ctx.line_to(x, 64)
        for y in range(2, 64, 4):
            ctx.move_to(0, y)
            ctx.line_to(128, y)
        ctx.line_width, ctx.stroke_style = .15, t.grid_color
        ctx.stroke()
    elif k == "hatch":
        x = -64.0
        while x < 128:
            ctx.move_to(x, 64)
            ctx.line_to(x + 64, 0)
            x += 3.2
        ctx.line_width, ctx.stroke_style = .18, t.grid_color
        ctx.stroke()
    elif k == "dots":
        y = 1.5
        while y < 64:
            x = 1.5
            while x < 128:
                ctx.rect(x - .25, y - .25, .5, .5)
                x += 3
            y += 3
        ctx.fill_style = t.grid_color
        ctx.fill()
    elif k == "horizon":
        for i in range(7):
            y = 30 + i * i * .85
            ctx.move_to(0, y)
            ctx.line_to(128, y)
        for xb in range(-56, 185, 12):
            ctx.move_to(64 + (xb - 64) * .15, 30)
            ctx.line_to(xb, 64)
        ctx.line_width, ctx.stroke_style = .25, t.grid_color
        ctx.stroke()
    elif k == "scanlines":
        y = .6
        while y < 64:
            ctx.move_to(0, y)
            ctx.line_to(128, y)
            y += 1.3
        ctx.line_width, ctx.stroke_style = .35, t.grid_color
        ctx.stroke()
    elif k == "pixels":
        s = 7
        for _ in range(70):
            s = (s * 75 + 74) % 65537
            x = s % 1280 / 10
            s = (s * 75 + 74) % 65537
            y = s % 640 / 10
            ctx.rect(x, y, .7, .7)
        ctx.fill_style = t.grid_color
        ctx.fill()
    elif k == "polka":
        for j, y in enumerate(range(3, 64, 5)):
            for x in range(3 + (3 if j % 2 else 0), 128, 6):
                ctx.move_to(x + .7, y)
                ctx.arc(x, y, .7, 0, TAU)
        ctx.fill_style = t.grid_color
        ctx.fill()
    elif k == "waves":
        for y0 in range(3, 66, 5):
            for i in range(65):
                x = i * 2
                (ctx.line_to if i else ctx.move_to)(x, y0 + .8 * math.sin(x / 6))
        ctx.line_width, ctx.stroke_style = .3, t.grid_color
        ctx.stroke()
    elif k == "zigzag":
        for y0 in range(3, 66, 5):
            for i in range(33):
                (ctx.line_to if i else ctx.move_to)(i * 4, y0 + (1 if i % 2 else -1))
        ctx.line_width, ctx.stroke_style = .3, t.grid_color
        ctx.stroke()
    elif k == "rays":
        for i in range(16):
            a = -math.pi / 2 + i * math.pi / 30
            ctx.move_to(0, 64)
            ctx.line_to(170 * math.cos(a), 64 + 170 * math.sin(a))
        ctx.line_width, ctx.stroke_style = .5, t.grid_color
        ctx.stroke()
    elif k == "lattice":
        x = -64.0
        while x < 128:
            ctx.move_to(x, 64)
            ctx.line_to(x + 64, 0)
            ctx.move_to(x, 0)
            ctx.line_to(x + 64, 64)
            x += 6
        ctx.line_width, ctx.stroke_style = .2, t.grid_color
        ctx.stroke()
    elif k == "bubbles":
        s = 11
        for _ in range(40):
            s = (s * 75 + 74) % 65537
            x = s % 1280 / 10
            s = (s * 75 + 74) % 65537
            y = s % 640 / 10
            s = (s * 75 + 74) % 65537
            r = .6 + (s % 10) / 10
            ctx.move_to(x + r, y)
            ctx.arc(x, y, r, 0, TAU)
        ctx.line_width, ctx.stroke_style = .25, t.grid_color
        ctx.stroke()
    else:  # crosses
        for y in range(3, 64, 6):
            for x in range(3, 128, 6):
                ctx.rect(x - .8, y - .1, 1.6, .2)
                ctx.rect(x - .1, y - .8, .2, 1.6)
        ctx.fill_style = t.grid_color
        ctx.fill()


def draw_frame(ctx: Canvas, f: Features, fr, fcol, glow: Glow) -> None:
    st = f.framestyle
    glow(fcol, 1.5)
    ctx.begin_path()
    poly(ctx, fr)
    ctx.stroke_style, ctx.line_join = fcol, "miter"
    if st == 2:
        ctx.set_line_dash((3, 1.6))
        ctx.line_width = .9
        ctx.stroke()
        ctx.set_line_dash(())
    elif st == 3:
        ctx.line_width, ctx.global_alpha = .3, .7
        ctx.stroke()
        ctx.global_alpha = 1
        ctx.begin_path()
        n = len(fr)
        for i, (x, y) in enumerate(fr):
            for j in (i - 1, (i + 1) % n):
                px, py = fr[j]
                d = math.hypot(px - x, py - y)
                L = min(7, d / 2.5)
                ctx.move_to(x, y)
                ctx.line_to(x + (px - x) / d * L, y + (py - y) / d * L)
        ctx.line_width = 1.6
        ctx.stroke()
    else:
        ctx.line_width = .8
        ctx.stroke()
    glow.off()
    if st == 1:
        ctx.begin_path()
        poly(ctx, frame_poly(f.corners, 1.7))
        ctx.line_width = .35
        ctx.stroke()


def draw_face(ctx: Canvas, f: Features, hx: float, glow: Glow, vis: str, trim: str, t: Theme) -> None:
    """The portrait: an android head, a building or an animal, then the status chip."""
    kind = subject_kind(f.subject)
    if kind == "face":
        draw_android(ctx, f, hx, glow, vis, trim, t)
    elif kind == "building":
        draw_building(ctx, f, hx, glow, vis, trim, t)
    else:
        draw_animal(ctx, f, hx, glow, vis, trim, t)
    ctx.line_cap, ctx.line_join = "butt", "miter"
    draw_status(ctx, f, hx, glow, t)


def draw_android(ctx: Canvas, f: Features, hx: float, glow: Glow, vis: str, trim: str, t: Theme) -> None:
    shape, vst = f.subject, f.vstyle

    def head_path():
        ctx.begin_path()
        if shape == 0:
            ctx.ellipse(hx, 30, 13, 17, 0, 0, TAU)
        elif shape == 1:
            poly(ctx, [(hx, 12), (hx + 13, 19), (hx + 12, 42), (hx, 49), (hx - 12, 42), (hx - 13, 19)])
        elif shape == 2:
            poly(ctx, [(hx - 8, 13), (hx + 8, 13), (hx + 13, 18), (hx + 13, 42), (hx + 8, 47), (hx - 8, 47), (hx - 13, 42), (hx - 13, 18)])
        elif shape == 3:
            ctx.move_to(hx - 13, 27)
            ctx.arc(hx, 27, 13, math.pi, TAU)
            ctx.line_to(hx + 13, 38)
            ctx.line_to(hx + 6, 48)
            ctx.line_to(hx - 6, 48)
            ctx.line_to(hx - 13, 38)
            ctx.close_path()
        elif shape == 4:
            rr(ctx, hx - 12, 12, 24, 36, 10)
        elif shape == 5:
            poly(ctx, [(hx - 9, 13), (hx + 9, 13), (hx + 14, 46), (hx - 14, 46)])
        elif shape == 6:
            poly(ctx, [(hx - 13, 13), (hx + 13, 13), (hx + 13, 34), (hx, 50), (hx - 13, 34)])
        else:
            ctx.arc(hx, 25, 14, math.pi * .72, math.pi * 2.28)
            ctx.line_to(hx + 7.5, 43)
            ctx.line_to(hx + 6.5, 49)
            ctx.line_to(hx - 6.5, 49)
            ctx.line_to(hx - 7.5, 43)
            ctx.close_path()

    ctx.line_cap = "round"
    glow(trim, 1.2)
    ctx.stroke_style = ctx.fill_style = trim
    if f.mod == 0:
        ctx.begin_path()
        ctx.move_to(hx + 7, 18)
        ctx.line_to(hx + 14, 5.5)
        ctx.line_width = .7
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(hx + 14, 5.5, 1.4, 0, TAU)
        ctx.fill()
    elif f.mod == 2:
        ctx.begin_path()
        ctx.move_to(hx - 11, 36)
        ctx.bezier_curve_to(hx - 17, 40, hx - 12, 50, hx - 17.5, 53)
        ctx.line_width = 1.1
        ctx.stroke()
    elif f.mod == 3:
        ctx.begin_path()
        poly(ctx, [(hx - 3.5, 15), (hx + 3.5, 15), (hx + 1.5, 4)])
        ctx.fill()
    glow.off()
    head_path()
    ctx.fill_style = t.panel
    ctx.fill()
    glow(trim, 1)
    ctx.line_width, ctx.stroke_style, ctx.line_join = .7, trim, "round"
    ctx.stroke()
    glow.off()
    if f.mod == 1:
        for s in (-1, 1):
            ctx.begin_path()
            ctx.arc(hx + s * 13.6, 30, 3.2, 0, TAU)
            ctx.fill_style = t.panel
            ctx.fill()
            glow(trim, 1)
            ctx.line_width, ctx.stroke_style = .6, trim
            ctx.stroke()
            glow.off()
            ctx.begin_path()
            ctx.arc(hx + s * 13.6, 30, 1, 0, TAU)
            ctx.fill_style = trim
            ctx.fill()
    draw_symbol(ctx, f.decal, hx, 19.6, 2.7, trim)
    draw_visor(ctx, vst, hx, head_path, glow, vis, t)
    draw_mouth(ctx, f.grille, hx, glow, vis, trim)
    draw_cheeks(ctx, f.cheek, hx, trim)


def draw_visor(ctx: Canvas, vst, hx, head_path, glow: Glow, vis, t: Theme) -> None:
    glow(vis, 2)
    ctx.fill_style = vis
    if vst == 0:
        ctx.save()
        head_path()
        ctx.clip()
        ctx.fill_rect(hx - 14, 25, 28, 6)
        ctx.restore()
    elif vst == 1:
        ctx.begin_path()
        ctx.arc(hx - 6, 28, 4.2, 0, TAU)
        ctx.move_to(hx + 10.2, 28)
        ctx.arc(hx + 6, 28, 4.2, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.arc(hx - 6, 28, 1.3, 0, TAU)
        ctx.move_to(hx + 7.3, 28)
        ctx.arc(hx + 6, 28, 1.3, 0, TAU)
        ctx.fill_style = t.bg
        ctx.fill()
    elif vst == 2:
        ctx.fill_rect(hx - 10, 27, 20, 1.9)
        glow.off()
        ctx.fill_style = "#FFFFFF"
        ctx.fill_rect(hx - 1.2, 27, 2.4, 1.9)
    elif vst == 3:
        ctx.begin_path()
        ctx.arc(hx, 28, 5.6, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.arc(hx, 28, 2.7, 0, TAU)
        ctx.fill_style = t.bg
        ctx.fill()
        ctx.begin_path()
        ctx.arc(hx, 28, 1.2, 0, TAU)
        ctx.fill_style = vis
        ctx.fill()
    elif vst == 4:
        ctx.begin_path()
        rr(ctx, hx - 11.5, 24.6, 9.6, 7, 2.2)
        rr(ctx, hx + 1.9, 24.6, 9.6, 7, 2.2)
        ctx.fill()
        ctx.begin_path()
        ctx.move_to(hx - 2.2, 27.4)
        ctx.line_to(hx + 2.2, 27.4)
        ctx.line_width, ctx.stroke_style = .9, vis
        ctx.stroke()
    elif vst == 5:
        ctx.save()
        head_path()
        ctx.clip()
        ctx.begin_path()
        poly(ctx, [(hx - 14, 23.5), (hx, 28.5), (hx + 14, 23.5), (hx + 14, 27.5), (hx, 32.5), (hx - 14, 27.5)])
        ctx.fill()
        ctx.restore()
    elif vst == 6:
        ctx.begin_path()
        for dx in (-7.2, 0, 7.2):
            ctx.move_to(hx + dx + 3, 28)
            ctx.arc(hx + dx, 28, 3, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        for dx in (-7.2, 0, 7.2):
            ctx.move_to(hx + dx + .9, 28)
            ctx.arc(hx + dx, 28, .9, 0, TAU)
        ctx.fill_style = t.bg
        ctx.fill()
    else:
        ctx.save()
        head_path()
        ctx.clip()
        ctx.fill_rect(hx - 14, 25, 28, 6)
        glow.off()
        ctx.fill_style = t.bg
        for dx in (-8, -4, 0, 4, 8):
            ctx.fill_rect(hx + dx - .4, 25, .8, 6)
        ctx.restore()
    glow.off()


def draw_mouth(ctx: Canvas, m, hx, glow: Glow, vis, trim) -> None:
    ctx.stroke_style = ctx.fill_style = trim
    ctx.line_width = .6
    ctx.begin_path()
    if m == 0:
        for y in (37.5, 39.6, 41.7):
            ctx.move_to(hx - 6, y)
            ctx.line_to(hx + 6, y)
        ctx.stroke()
    elif m == 1:
        for k in range(6):
            x = -6 + k * 2.4
            ctx.move_to(hx + x, 37)
            ctx.line_to(hx + x, 43)
        ctx.stroke()
    elif m == 2:
        for y in (38.3, 41.3):
            for k in range(5):
                x = -6 + k * 3
                ctx.move_to(hx + x + .6, y)
                ctx.arc(hx + x, y, .6, 0, TAU)
        ctx.fill()
    elif m == 3:
        glow(vis, 1.5)
        ctx.fill_style = vis
        ctx.fill_rect(hx - 7, 39, 14, 1.7)
        glow.off()
    elif m == 4:
        for k in range(7):
            (ctx.line_to if k else ctx.move_to)(hx - 6 + k * 2, 38.8 if k % 2 == 0 else 41.2)
        ctx.stroke()
    elif m == 5:
        ctx.arc(hx, 40, 3, 0, TAU)
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(hx, 40, 1.2, 0, TAU)
        ctx.fill()
    elif m == 6:
        ctx.move_to(hx - 6, 38.4)
        ctx.line_to(hx + 6, 38.4)
        ctx.stroke()
        ctx.begin_path()
        for c in (hx - 3, hx + 3):
            poly(ctx, [(c - 1.3, 38.4), (c + 1.3, 38.4), (c, 42.6)])
        ctx.fill()
    else:
        ctx.move_to(hx - 6, 40)
        ctx.line_to(hx + 6, 40)
        for k in range(5):
            x = hx - 5 + k * 2.5
            ctx.move_to(x, 38.4)
            ctx.line_to(x, 41.6)
        ctx.stroke()


def draw_cheeks(ctx: Canvas, c, hx, trim) -> None:
    ctx.stroke_style = ctx.fill_style = trim
    ctx.line_width = .55
    for s in (-1, 1):
        cx = hx + s * 8.8
        ctx.begin_path()
        if c == 0:
            for k in (0, 1):
                x = cx + (k - .5) * 1.6 * s
                ctx.move_to(x, 32.8)
                ctx.line_to(x - s * 1.2, 35.8)
            ctx.stroke()
        elif c == 1:
            for dx in (-1.5, 0, 1.5):
                ctx.move_to(cx + dx + .5, 34.4)
                ctx.arc(cx + dx, 34.4, .5, 0, TAU)
            ctx.fill()
        elif c == 2:
            ctx.move_to(cx - s * 1.8, 33)
            ctx.line_to(cx, 33)
            ctx.line_to(cx + s * 1.2, 35.4)
            ctx.stroke()
            ctx.begin_path()
            ctx.arc(cx + s * 1.2, 35.4, .6, 0, TAU)
            ctx.fill()
        else:
            poly(ctx, [(cx + 1.2 * math.cos(a), 34.2 + 1.2 * math.sin(a)) for a in (k * math.pi / 3 for k in range(6))])
            ctx.line_width = .45
            ctx.stroke()
            ctx.begin_path()
            ctx.arc(cx, 34.2, .35, 0, TAU)
            ctx.fill()


def draw_status(ctx: Canvas, f: Features, hx, glow: Glow, t: Theme) -> None:
    st, sc = STATUS_WORDS[f.status], t.color(f.scolor)
    ctx.set_font("mono", 4.6)
    tw = ctx.measure_text(st)
    ctx.begin_path()
    ctx.rect(hx - tw / 2 - 1.8, 52.4, tw + 3.6, 6)
    glow(sc, 1)
    ctx.line_width, ctx.stroke_style = .45, sc
    ctx.stroke()
    glow.off()
    ctx.fill_style, ctx.text_align, ctx.text_baseline = sc, "center", "middle"
    ctx.fill_text(st, hx, 55.6)


def handle_text(ctx: Canvas, text, x, y, max_w, align, style, acc, size, glow: Glow, t: Theme) -> None:
    fs = fit_font(ctx, text, max_w - (2.4 if style in (4, 6) else 0), t.handle_font, size)
    ctx.text_align, ctx.text_baseline = align, "alphabetic"
    w = ctx.measure_text(text)
    left = x if align == "left" else (x - w / 2 if align == "center" else x - w)
    if style in (4, 6) and align == "left":
        x, left = x + 1.2, left + 1.2
    o = .55
    if style == 1:
        ctx.fill_style = t.chroma[0]
        ctx.fill_text(text, x - o, y)
        ctx.fill_style = t.chroma[1]
        ctx.fill_text(text, x + o, y)
    elif style == 2:
        ctx.fill_style = t.chroma[0]
        ctx.fill_text(text, x, y - o)
        ctx.fill_style = t.chroma[1]
        ctx.fill_text(text, x, y + o)
    elif style == 4:
        ctx.fill_style = acc
        ctx.fill_rect(left - 1.2, y - fs * .82, w + 2.4, fs * 1.04)
        ctx.fill_style = chip_ink(t, acc)
        ctx.fill_text(text, x, y)
        return
    elif style == 7:
        ctx.fill_style = acc
        ctx.fill_text(text, x + .7, y + .7)
    glow(acc, 1.4)
    ctx.fill_style = t.handle
    ctx.fill_text(text, x, y)
    glow.off()
    if style == 3:
        ctx.save()
        ctx.begin_path()
        ctx.rect(left - 2, y - fs * .5, w + 4, fs * .16)
        ctx.clip()
        ctx.fill_style = t.bg
        ctx.fill_rect(left - 2, y - fs, w + 4, fs * 1.2)
        ctx.fill_style = acc
        ctx.fill_text(text, x + .9, y)
        ctx.restore()
    elif style == 5:
        ctx.fill_style = acc
        ctx.fill_rect(left, y + fs * .16, w, fs * .13)
    elif style == 6:
        ctx.begin_path()
        ctx.rect(left - 1.2, y - fs * .82, w + 2.4, fs * 1.04)
        ctx.line_width, ctx.stroke_style = .45, acc
        ctx.stroke()


def draw_bars(ctx: Canvas, vals, x0, x1, y0, y1, slots, style, acc, glow: Glow, t: Theme) -> None:
    """Signal bars, 1-8 lit levels each, in one of 4 styles. `slots` keeps bar widths equal
    when a side holds fewer bars; the bars are then centered."""
    n, gap = len(vals), 1.4
    k = max(n, slots)
    bw, bh = (x1 - x0 - (k - 1) * gap) / k, y1 - y0
    seg = bh / 8
    ox = x0 + (k - n) * (bw + gap) / 2
    for i, v in enumerate(vals):
        x = ox + i * (bw + gap)
        if style == 1:  # solid column over faint level cells, with a peak line
            for s in range(8):
                ctx.fill_style = t.unlit
                ctx.fill_rect(x, y0 + bh - (s + 1) * seg + .15, bw, seg - .35)
            top = y0 + bh - (v + 1) * seg
            glow(acc, .8)
            ctx.fill_style = acc
            ctx.fill_rect(x, top + .15, bw, (v + 1) * seg - .15)
            glow.off()
            ctx.fill_style = t.peak
            ctx.fill_rect(x, top + .15, bw, .6)
            continue
        if style == 2:  # lollipops: a stem to the level with a dot on top
            cx, top = x + bw / 2, y0 + bh - (v + .5) * seg
            sw, r = min(bw * .22, .8), min(bw * .42, 1.7)
            ctx.fill_style = t.unlit
            ctx.fill_rect(cx - sw / 2, y0, sw, bh)
            glow(acc, .8)
            ctx.fill_style = acc
            ctx.fill_rect(cx - sw / 2, top, sw, y0 + bh - top)
            ctx.begin_path()
            ctx.arc(cx, top, r, 0, TAU)
            ctx.fill_style = t.peak
            ctx.fill()
            glow.off()
            continue
        for s in range(8):
            y = y0 + bh - (s + 1) * seg
            lit = s <= v
            color = (t.peak if s == v else acc) if lit else t.unlit
            if lit:
                glow(acc, .8)
            if style == 3:  # chevrons
                ctx.begin_path()
                ctx.move_to(x + .2, y + seg - .25)
                ctx.line_to(x + bw / 2, y + .3)
                ctx.line_to(x + bw - .2, y + seg - .25)
                ctx.line_width, ctx.stroke_style, ctx.line_join = .55, color, "miter"
                ctx.stroke()
            else:  # segmented
                ctx.fill_style = color
                ctx.fill_rect(x, y + .15, bw, seg - .35)
            glow.off()


def draw_chips(ctx: Canvas, f: Features, r: dict, t: Theme) -> None:
    ids, gap = r["ids"], 1.6
    n = len(ids)
    groups = f.char_groups
    if r["col"]:
        cw, ch = r["x1"] - r["x0"], (r["y1"] - r["y0"] - (n - 1) * gap) / n
    else:
        cw, ch = (r["x1"] - r["x0"] - (n - 1) * gap) / n, r["y1"] - r["y0"]
    for j, i in enumerate(ids):
        x = r["x0"] + (0 if r["col"] else j * (cw + gap))
        y = r["y0"] + (j * (ch + gap) if r["col"] else 0)
        color = t.color(f.chips[i])
        ctx.begin_path()
        rr(ctx, x, y, cw, ch, min(1.6, ch / 3))
        ctx.fill_style = color
        ctx.fill()
        fit_font(ctx, groups[i], cw - 2.4, t.code_font, min(ch * .8, 7.6))
        ctx.fill_style, ctx.text_align, ctx.text_baseline = chip_ink(t, color), "center", "middle"
        ctx.fill_text(groups[i], x + cw / 2, y + ch / 2 + .2)


# ---------------------------------------------------------------- detail cells (4 displays)
def draw_cells(ctx: Canvas, f: Features, r: dict, vis, glow: Glow, t: Theme) -> None:
    """10 cells of 8 bits each, laid out in a grid; a short last row is centered."""
    ids, gc, gr, gap = r["ids"], r["gc"], r["gr"], 1.6
    cw = (r["x1"] - r["x0"] - (gc - 1) * gap) / gc
    ch = (r["y1"] - r["y0"] - (gr - 1) * gap) / gr
    for j, i in enumerate(ids):
        row, col = divmod(j, gc)
        in_row = min(gc, len(ids) - row * gc)
        x = r["x0"] + (gc - in_row) * (cw + gap) / 2 + col * (cw + gap)
        y = r["y0"] + row * (ch + gap)
        draw_cell(ctx, f.display, f.cells[i], x, y, cw, ch, vis, glow, t)


def brackets(ctx: Canvas, x, y, w, h, t: Theme) -> None:
    k = min(1.6, w / 4, h / 4)
    ctx.begin_path()
    for cx, cy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1), (x + w, y + h, -1, -1), (x, y + h, 1, -1)):
        ctx.move_to(cx + dx * k, cy)
        ctx.line_to(cx, cy)
        ctx.line_to(cx, cy + dy * k)
    ctx.line_width, ctx.stroke_style = .3, t.bracket
    ctx.stroke()


def draw_cell(ctx: Canvas, display, c, x, y, w, h, vis, glow: Glow, t: Theme) -> None:
    cx, cy = x + w / 2, y + h / 2
    if display == 0:  # tile: color (high nibble) + symbol (low nibble)
        color = t.color(c >> 4)
        ctx.begin_path()
        rr(ctx, x, y, w, h, min(1.2, h / 4))
        ctx.fill_style = color
        ctx.fill()
        draw_symbol(ctx, c & 15, cx, cy, min(w, h) * .32, chip_ink(t, color))
        return
    brackets(ctx, x, y, w, h, t)
    if display == 1:  # gem: color (high nibble), shape (2 bits), fill (2 bits)
        draw_gem(ctx, (c >> 2) & 3, c & 3, cx, cy, min(w, h) * .33, t.color(c >> 4), glow)
    elif display == 2:  # hex pair on a seven-segment display
        dh = h * .72
        dw = min(w * .34, dh * .58)
        for k, n in enumerate((c >> 4, c & 15)):
            sx = cx + (k - .5) * dw * 1.45
            seven_seg(ctx, n, sx - dw / 2, cy - dh / 2, dw, dh, vis, glow, t)
    else:  # arrow: direction (3 bits), color (4 bits), solid or outline (1 bit)
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate((c >> 5) * math.pi / 4)
        r = min(w, h) * .36
        ctx.scale(r, r)
        sym_path(ctx, 14)
        color = t.color((c >> 1) & 15)
        glow(color, .8)
        if c & 1:
            ctx.line_width, ctx.stroke_style, ctx.line_join = .22, color, "round"
            ctx.stroke()
        else:
            ctx.fill_style = color
            ctx.fill()
        glow.off()
        ctx.restore()


def draw_gem(ctx: Canvas, kind, fill, cx, cy, r, color, glow: Glow) -> None:
    def path():
        ctx.begin_path()
        if kind == 0:
            ctx.arc(cx, cy, r, 0, TAU)
        elif kind == 1:
            ctx.rect(cx - r * .86, cy - r * .86, r * 1.72, r * 1.72)
        elif kind == 2:
            poly(ctx, [(cx, cy - r * 1.05), (cx + r * 1.05, cy + r * .8), (cx - r * 1.05, cy + r * .8)])
        else:
            poly(ctx, [(cx, cy - r * 1.15), (cx + r, cy), (cx, cy + r * 1.15), (cx - r, cy)])

    glow(color, .8)
    ctx.fill_style = ctx.stroke_style = color
    ctx.line_width, ctx.line_join = r * .26, "round"
    path()
    if fill == 0:
        ctx.fill()
    else:
        ctx.stroke()
    glow.off()
    if fill == 2:
        ctx.begin_path()
        ctx.arc(cx, cy + (r * .12 if kind == 2 else 0), r * .32, 0, TAU)
        ctx.fill()
    elif fill == 3:
        ctx.save()
        ctx.begin_path()
        ctx.rect(cx - r * 1.3, cy, r * 2.6, r * 1.4)
        ctx.clip()
        path()
        ctx.fill()
        ctx.restore()


# a b c d e f g for hex digits 0-F
SEGMENTS = ("abcdef", "bc", "abdeg", "abcdg", "bcfg", "acdfg", "acdefg", "abc",
            "abcdefg", "abcdfg", "abcefg", "cdefg", "adef", "bcdeg", "adefg", "aefg")


def seven_seg(ctx: Canvas, n, x, y, w, h, vis, glow: Glow, t: Theme) -> None:
    k = w * .22
    hh = h / 2
    rects = {
        "a": (x + k * .6, y, w - k * 1.2, k),
        "g": (x + k * .6, y + hh - k / 2, w - k * 1.2, k),
        "d": (x + k * .6, y + h - k, w - k * 1.2, k),
        "f": (x, y + k * .6, k, hh - k * .9),
        "b": (x + w - k, y + k * .6, k, hh - k * .9),
        "e": (x, y + hh + k * .3, k, hh - k * .9),
        "c": (x + w - k, y + hh + k * .3, k, hh - k * .9),
    }
    on = SEGMENTS[n]
    for name, (rx, ry, rw, rh) in rects.items():
        if name in on:
            glow(vis, .8)
            ctx.fill_style = vis
        else:
            ctx.fill_style = t.unlit
        ctx.fill_rect(rx, ry, rw, rh)
        glow.off()


# ---------------------------------------------------------------- 512-bit pair frame
PAIR_PAD, PAIR_GAP, PAIR_FOOT = S * .22, S * .15, S * .26
PAIR_W = W + 2 * PAIR_PAD
PAIR_H = 2 * H + PAIR_GAP + 2 * PAIR_PAD + PAIR_FOOT


def draw_pair(ctx: Canvas, parts: list[Features]) -> None:
    """Both halves of a 512-bit hash in one frame, numbered 1 and 2 and joined by a rail.
    Each badge uses its own theme; the frame takes its colors from part 1's theme."""
    t = get_theme(parts[0].theme)
    fg = t.pair_fg
    ctx.begin_path()
    rr(ctx, 0, 0, PAIR_W, PAIR_H, S * .1)
    ctx.fill_style = t.pair_bg
    ctx.fill()
    ctx.begin_path()
    rr(ctx, S * .04, S * .04, PAIR_W - S * .08, PAIR_H - S * .08, S * .08)
    ctx.line_width, ctx.stroke_style, ctx.global_alpha = S * .016, fg, .6
    ctx.stroke()
    ctx.global_alpha = 1
    pos = [(PAIR_PAD, PAIR_PAD), (PAIR_PAD, PAIR_PAD + H + PAIR_GAP)]
    badges = [(PAIR_PAD / 2, y + S * .2) for _, y in pos]
    ctx.begin_path()
    ctx.move_to(*badges[0])
    ctx.line_to(*badges[1])
    ctx.line_width, ctx.stroke_style = S * .026, fg
    ctx.stroke()
    for (x, y), f in zip(pos, parts):
        ctx.save()
        ctx.translate(x, y)
        draw_badge(ctx, f)
        ctx.restore()
    for i, (x, y) in enumerate(badges):
        ctx.begin_path()
        ctx.arc(x, y, S * .075, 0, TAU)
        ctx.fill_style = fg
        ctx.fill()
        ctx.fill_style = t.pair_bg
        ctx.set_font("mono", S * .1)
        ctx.text_align, ctx.text_baseline = "center", "middle"
        ctx.fill_text(str(i + 1), x, y + S * .006)
    ctx.fill_style = fg
    ctx.set_font("mono", S * .11)
    ctx.text_align, ctx.text_baseline = "center", "middle"
    ctx.fill_text("SHA-512 · 2 PARTS · READ 1 THEN 2", PAIR_W / 2, PAIR_H - PAIR_PAD * .35 - PAIR_FOOT / 2)


__all__ = ["draw_badge", "draw_pair", "layout_spec", "W", "H", "PAIR_W", "PAIR_H"]
