"""Draws a Netrunner ID badge. Coordinates are 128 x 64 badge units on a 960 x 480 canvas.

This file mirrors the browser preview (docs/netrunner-lab.html) line for line; keep them in sync.
"""

from __future__ import annotations

import math

from .canvas import Canvas
from .spec import STATUS_WORDS, Features
from .themes import Theme

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
                    bars=[dict(ids=list(range(8)), x0=x0, x1=x1, y0=14.6, y1=25.6)],
                    code=[dict(groups=[0, 1, 2, 3], x=x0, y=34.2, w=x1 - x0, align="left", size=6.2, lines=1)],
                    detail=[dict(groups=[0, 1, 2, 3], x0=x0, y0=38.6, x1=x1, y1=59.6, gc=4, gr=1)])

    def grid(x0, x1):
        mid = x0 + (x1 - x0) * .485
        return dict(handle=[dict(text="both", x=x0, y=11.8, w=x1 - x0, align="left", size=8.4)],
                    detail=[dict(groups=[0, 1, 2, 3], x0=x0, y0=15, x1=mid, y1=59.6, gc=2, gr=2)],
                    bars=[dict(ids=list(range(8)), x0=mid + 2.6, x1=x1, y0=15, y1=36)],
                    code=[dict(groups=[0, 1, 2, 3], x=mid + 2.6, y=46, w=x1 - mid - 2.6, align="left", size=6.2, lines=2)])

    def split(detail_top):
        def col(x0, x1, side):
            cx, g, b = (x0 + x1) / 2, ([2, 3] if side else [0, 1]), ([4, 5, 6, 7] if side else [0, 1, 2, 3])
            hd = dict(text="w2" if side else "w1", x=cx, y=11.4, w=x1 - x0, align="center", size=7.8)
            if detail_top:
                return dict(handle=hd, detail=dict(groups=g, x0=x0, y0=14, x1=x1, y1=36.4, gc=2, gr=1),
                            code=dict(groups=g, x=cx, y=42.4, w=x1 - x0, align="center", size=6, lines=1),
                            bars=dict(ids=b, x0=x0, x1=x1, y0=46, y1=59.6))
            return dict(handle=hd, bars=dict(ids=b, x0=x0, x1=x1, y0=14, y1=24.6),
                        code=dict(groups=g, x=cx, y=32, w=x1 - x0, align="center", size=6, lines=1),
                        detail=dict(groups=g, x0=x0, y0=35.4, x1=x1, y1=59.6, gc=2, gr=1))
        a, c = col(3.5, 40.5, 0), col(87.5, 124.5, 1)
        return dict(face=(64, 31, 1), div=[(43, 6, 43, 58), (85, 6, 85, 58)],
                    **{k: [a[k], c[k]] for k in ("handle", "bars", "code", "detail")})

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
                    bars=[dict(ids=list(range(8)), x0=41, x1=123.4, y0=16.6, y1=27)],
                    code=[dict(groups=[0, 1, 2, 3], x=41, y=35, w=82.4, align="left", size=6.4, lines=1)],
                    detail=[dict(groups=[0, 1, 2, 3], x0=41, y0=38.8, x1=123.4, y1=59.6, gc=4, gr=1)])
    if L == 6:
        return dict(face=(108.5, 26.5, .74), div=[(6, 50.6, 122, 50.6), (89, 5, 89, 48)],
                    handle=[dict(text="both", x=64, y=59.4, w=112, align="center", size=8.6)],
                    detail=[dict(groups=[0, 1, 2, 3], x0=4.6, y0=4.6, x1=86, y1=25, gc=4, gr=1)],
                    code=[dict(groups=[0, 1, 2, 3], x=4.6, y=32.8, w=81.4, align="left", size=6.4, lines=1)],
                    bars=[dict(ids=list(range(8)), x0=4.6, x1=86, y0=36, y1=48)])
    return split(True)


# ---------------------------------------------------------------- badge
def draw_badge(ctx: Canvas, f: Features, theme: Theme) -> None:
    """Draw one badge into ctx, occupying (0, 0)-(960, 480) in ctx's current transform."""
    ctx.save()
    ctx.scale(U, U)
    acc, vis, trim = theme.color(f.frame), theme.color(f.visor), theme.color(f.trim)
    glow = Glow(ctx, theme)
    fr = frame_poly(f.corners)
    ctx.begin_path()
    poly(ctx, fr)
    ctx.fill_style = theme.bg
    ctx.fill()
    ctx.save()
    ctx.clip()
    background(ctx, theme)
    ctx.restore()
    glow(acc, 1.5)
    ctx.begin_path()
    poly(ctx, fr)
    ctx.line_width, ctx.stroke_style, ctx.line_join = .8, acc, "miter"
    ctx.stroke()
    glow.off()
    if f.frameline:
        ctx.begin_path()
        poly(ctx, frame_poly(f.corners, 1.7))
        ctx.line_width, ctx.stroke_style = .35, acc
        ctx.stroke()
    spec = layout_spec(f.layout)
    ctx.line_width, ctx.stroke_style, ctx.global_alpha = .3, acc, .55
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
    draw_face(ctx, f, 21.5, glow, vis, trim, theme)
    ctx.restore()
    w1, w2 = (w.upper() for w in f.words)
    for h in spec["handle"]:
        text = f"{w1}·{w2}" if h["text"] == "both" else (w1 if h["text"] == "w1" else w2)
        handle_text(ctx, text, h["x"], h["y"], h["w"], h["align"], f.glitch, acc, h["size"], glow, theme)
    for b in spec["bars"]:
        draw_bars(ctx, [f.bars[i] for i in b["ids"]], b["x0"], b["x1"], b["y0"], b["y1"], acc, glow, theme)
    cg = f.char_groups
    for c in spec["code"]:
        draw_code(ctx, [cg[g] for g in c["groups"]], c, acc, glow)
    for g in spec["detail"]:
        draw_detail(ctx, f, g["groups"], g["x0"], g["y0"], g["x1"], g["y1"], g["gc"], g["gr"], vis, glow, theme)
    ctx.restore()


def background(ctx: Canvas, theme: Theme) -> None:
    ctx.begin_path()
    if theme.grid_kind == "grid":
        for x in range(2, 128, 4):
            ctx.move_to(x, 0)
            ctx.line_to(x, 64)
        for y in range(2, 64, 4):
            ctx.move_to(0, y)
            ctx.line_to(128, y)
        ctx.line_width, ctx.stroke_style = .15, theme.grid_color
        ctx.stroke()
    elif theme.grid_kind == "hatch":
        k = -64.0
        while k < 128:
            ctx.move_to(k, 64)
            ctx.line_to(k + 64, 0)
            k += 3.2
        ctx.line_width, ctx.stroke_style = .18, theme.grid_color
        ctx.stroke()
    else:
        y = 1.5
        while y < 64:
            x = 1.5
            while x < 128:
                ctx.rect(x - .25, y - .25, .5, .5)
                x += 3
            y += 3
        ctx.fill_style = theme.grid_color
        ctx.fill()


def draw_face(ctx: Canvas, f: Features, hx: float, glow: Glow, vis: str, trim: str, theme: Theme) -> None:
    shape, vst = f.shape, f.vstyle

    def head_path():
        ctx.begin_path()
        if shape == 0:
            ctx.ellipse(hx, 30, 13, 17, 0, 0, TAU)
        elif shape == 1:
            poly(ctx, [(hx, 12), (hx + 13, 19), (hx + 12, 42), (hx, 49), (hx - 12, 42), (hx - 13, 19)])
        elif shape == 2:
            poly(ctx, [(hx - 8, 13), (hx + 8, 13), (hx + 13, 18), (hx + 13, 42), (hx + 8, 47), (hx - 8, 47), (hx - 13, 42), (hx - 13, 18)])
        else:
            ctx.move_to(hx - 13, 27)
            ctx.arc(hx, 27, 13, math.pi, TAU)
            ctx.line_to(hx + 13, 38)
            ctx.line_to(hx + 6, 48)
            ctx.line_to(hx - 6, 48)
            ctx.line_to(hx - 13, 38)
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
    ctx.fill_style = theme.panel
    ctx.fill()
    glow(trim, 1)
    ctx.line_width, ctx.stroke_style, ctx.line_join = .7, trim, "round"
    ctx.stroke()
    glow.off()
    if f.mod == 1:
        for s in (-1, 1):
            ctx.begin_path()
            ctx.arc(hx + s * 13.6, 30, 3.2, 0, TAU)
            ctx.fill_style = theme.panel
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
        ctx.fill_style = theme.bg
        ctx.fill()
    elif vst == 2:
        ctx.fill_rect(hx - 10, 27, 20, 1.9)
        glow.off()
        ctx.fill_style = "#FFFFFF"
        ctx.fill_rect(hx - 1.2, 27, 2.4, 1.9)
    else:
        ctx.begin_path()
        ctx.arc(hx, 28, 5.6, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.arc(hx, 28, 2.7, 0, TAU)
        ctx.fill_style = theme.bg
        ctx.fill()
        ctx.begin_path()
        ctx.arc(hx, 28, 1.2, 0, TAU)
        ctx.fill_style = vis
        ctx.fill()
    glow.off()
    ctx.stroke_style = ctx.fill_style = trim
    ctx.line_width = .6
    if f.grille == 0:
        ctx.begin_path()
        for y in (37.5, 39.6, 41.7):
            ctx.move_to(hx - 6, y)
            ctx.line_to(hx + 6, y)
        ctx.stroke()
    elif f.grille == 1:
        ctx.begin_path()
        for k in range(6):
            x = -6 + k * 2.4
            ctx.move_to(hx + x, 37)
            ctx.line_to(hx + x, 43)
        ctx.stroke()
    elif f.grille == 2:
        ctx.begin_path()
        for y in (38.3, 41.3):
            for k in range(5):
                x = -6 + k * 3
                ctx.move_to(hx + x + .6, y)
                ctx.arc(hx + x, y, .6, 0, TAU)
        ctx.fill()
    else:
        glow(vis, 1.5)
        ctx.fill_style = vis
        ctx.fill_rect(hx - 7, 39, 14, 1.7)
        glow.off()
    ctx.line_cap = "butt"
    st, sc = STATUS_WORDS[f.status], theme.color(f.scolor)
    ctx.set_font("mono", 4.6)
    stw = ctx.measure_text(st)
    ctx.begin_path()
    ctx.rect(hx - stw / 2 - 1.8, 52.4, stw + 3.6, 6)
    glow(sc, 1)
    ctx.line_width, ctx.stroke_style = .45, sc
    ctx.stroke()
    glow.off()
    ctx.fill_style, ctx.text_align, ctx.text_baseline = sc, "center", "middle"
    ctx.fill_text(st, hx, 55.6)


def handle_text(ctx: Canvas, text, x, y, max_w, align, glitch, acc, size, glow: Glow, theme: Theme) -> None:
    fs = fit_font(ctx, text, max_w, theme.handle_font, size)
    ctx.text_align, ctx.text_baseline = align, "alphabetic"
    o = .55
    if glitch == 1:
        ctx.fill_style = theme.chroma[0]
        ctx.fill_text(text, x - o, y)
        ctx.fill_style = theme.chroma[1]
        ctx.fill_text(text, x + o, y)
    elif glitch == 2:
        ctx.fill_style = theme.chroma[0]
        ctx.fill_text(text, x, y - o)
        ctx.fill_style = theme.chroma[1]
        ctx.fill_text(text, x, y + o)
    glow(acc, 1.4)
    ctx.fill_style = theme.handle
    ctx.fill_text(text, x, y)
    glow.off()
    if glitch == 3:
        w = ctx.measure_text(text)
        left = x if align == "left" else (x - w / 2 if align == "center" else x - w)
        ctx.save()
        ctx.begin_path()
        ctx.rect(left - 2, y - fs * .56, w + 4, fs * .24)
        ctx.clip()
        ctx.fill_style = theme.bg
        ctx.fill_rect(left - 2, y - fs, w + 4, fs * 1.2)
        ctx.fill_style = acc
        ctx.fill_text(text, x + 1.4, y)
        ctx.restore()


def draw_bars(ctx: Canvas, vals, x0, x1, y0, y1, acc, glow: Glow, theme: Theme) -> None:
    n, gap = len(vals), 1.4
    bw, bh = (x1 - x0 - (n - 1) * gap) / n, y1 - y0
    seg = bh / 16
    for i, v in enumerate(vals):
        x = x0 + i * (bw + gap)
        for s in range(16):
            y = y0 + bh - (s + 1) * seg
            lit = s <= v
            ctx.fill_style = (theme.peak if s == v else acc) if lit else theme.unlit
            if lit:
                glow(acc, .8)
            ctx.fill_rect(x, y + .1, bw, seg - .22)
            glow.off()


def draw_code(ctx: Canvas, groups, c, acc, glow: Glow) -> None:
    if c["lines"] == 2:
        half = len(groups) // 2
        lines = ["·".join(groups[:half]), "·".join(groups[half:])]
    else:
        lines = ["·".join(groups)]
    size = c["size"]
    for line in lines:
        size = min(size, fit_font(ctx, line, c["w"], "mono", c["size"]))
    ctx.set_font("mono", size)
    ctx.text_align, ctx.text_baseline = c["align"], "alphabetic"
    glow(acc, .7)
    ctx.fill_style = acc
    for i, line in enumerate(lines):
        ctx.fill_text(line, c["x"], c["y"] + i * size * 1.25)
    glow.off()


# ---------------------------------------------------------------- detail block (4 displays)
def draw_detail(ctx: Canvas, f: Features, ids, x0, y0, x1, y1, gcols, grows, vis, glow: Glow, theme: Theme) -> None:
    """Each 20-bit group in its own box with corner brackets, drawn in the badge's display type."""
    gap, t = 2.2, 1.6
    gw, gh = (x1 - x0 - (gcols - 1) * gap) / gcols, (y1 - y0 - (grows - 1) * gap) / grows
    for j, g in enumerate(ids):
        gx, gy = x0 + (j % gcols) * (gw + gap), y0 + (j // gcols) * (gh + gap)
        ctx.begin_path()
        for cx, cy, dx, dy in ((gx, gy, 1, 1), (gx + gw, gy, -1, 1), (gx + gw, gy + gh, -1, -1), (gx, gy + gh, 1, -1)):
            ctx.move_to(cx + dx * t, cy)
            ctx.line_to(cx, cy)
            ctx.line_to(cx, cy + dy * t)
        ctx.line_width, ctx.stroke_style = .3, theme.bracket
        ctx.stroke()
        bx0, by0, bx1, by1 = gx + .7, gy + .7, gx + gw - .7, gy + gh - .7
        if f.display == 0:
            dot_grid(ctx, f.detail_group(g), bx0, by0, bx1, by1, 5, 4, vis, glow, theme)
        elif f.display == 1:
            shape_group(ctx, f.detail_nibbles(g), bx0, by0, bx1, by1, vis, glow)
        elif f.display == 2:
            barcode_group(ctx, f.detail_group(g), bx0, by0, bx1, by1, vis, glow)
        else:
            segment_group(ctx, f.detail_nibbles(g), bx0, by0, bx1, by1, vis, glow, theme)


def dot_grid(ctx: Canvas, bits, x0, y0, x1, y1, cols, rows, vis, glow: Glow, theme: Theme) -> None:
    px, py = (x1 - x0) / cols, (y1 - y0) / rows
    ds = min(px, py) * .66
    for i, on in enumerate(bits):
        x, y = x0 + (i % cols) * px + (px - ds) / 2, y0 + (i // cols) * py + (py - ds) / 2
        if on:
            glow(vis, .8)
            ctx.fill_style = vis
        else:
            ctx.fill_style = theme.off
        ctx.fill_rect(x, y, ds, ds)
        glow.off()


# Quincunx positions (reading order: top-left, top-right, center, bottom-left, bottom-right).
QUINCUNX = ((.2, .24), (.8, .24), (.5, .5), (.2, .76), (.8, .76))


def shape_group(ctx: Canvas, nibbles, x0, y0, x1, y1, vis, glow: Glow) -> None:
    """5 shapes per group; each nibble = shape (circle, square, triangle, diamond) x fill (solid, outline, dotted, half)."""
    w, h = x1 - x0, y1 - y0
    r = min(w, h) * .17
    for (u, v), n in zip(QUINCUNX, nibbles):
        cx, cy, kind, fill = x0 + u * w, y0 + v * h, n >> 2, n & 3

        def path():
            ctx.begin_path()
            if kind == 0:
                ctx.arc(cx, cy, r, 0, TAU)
            elif kind == 1:
                ctx.rect(cx - r * .86, cy - r * .86, r * 1.72, r * 1.72)
            elif kind == 2:
                poly(ctx, [(cx, cy - r * 1.05), (cx + r * 1.05, cy + r * .8), (cx - r * 1.05, cy + r * .8)])
            else:
                poly(ctx, [(cx, cy - r * 1.15), (cx + r * 1.0, cy), (cx, cy + r * 1.15), (cx - r * 1.0, cy)])

        glow(vis, .8)
        ctx.fill_style = ctx.stroke_style = vis
        ctx.line_width, ctx.line_join = r * .28, "round"
        path()
        if fill == 0:
            ctx.fill()
        else:
            ctx.stroke()
        glow.off()
        if fill == 2:
            ctx.begin_path()
            ctx.arc(cx, cy + (r * .12 if kind == 2 else 0), r * .3, 0, TAU)
            ctx.fill()
        elif fill == 3:
            ctx.save()
            ctx.begin_path()
            ctx.rect(cx - r * 1.3, cy, r * 2.6, r * 1.4)
            ctx.clip()
            path()
            ctx.fill()
            ctx.restore()


def barcode_group(ctx: Canvas, bits, x0, y0, x1, y1, vis, glow: Glow) -> None:
    """2 rows of 10 ticks; 1 = full height, 0 = short (bottom aligned), like a postal barcode."""
    w, h = x1 - x0, y1 - y0
    rg = h * .12
    rh = (h - rg) / 2
    px = w / 10
    tw = px * .5
    glow(vis, .8)
    ctx.fill_style = vis
    for i, b in enumerate(bits):
        row, col = divmod(i, 10)
        x = x0 + col * px + (px - tw) / 2
        bottom = y0 + row * (rh + rg) + rh
        th = rh if b else rh * .42
        ctx.fill_rect(x, bottom - th, tw, th)
    glow.off()


# a b c d e f g for hex digits 0-F
SEGMENTS = ("abcdef", "bc", "abdeg", "abcdg", "bcfg", "acdfg", "acdefg", "abc",
            "abcdefg", "abcdfg", "abcefg", "cdefg", "adef", "bcdeg", "adefg", "aefg")


def segment_group(ctx: Canvas, nibbles, x0, y0, x1, y1, vis, glow: Glow, theme: Theme) -> None:
    """5 hex digits on a seven-segment display: 3 on the top row, 2 below."""
    w, h = x1 - x0, y1 - y0
    cw, ch = w / 3, h / 2
    for i, n in enumerate(nibbles):
        row = 0 if i < 3 else 1
        col = i if i < 3 else i - 3 + .5
        dh = ch * .8
        dw = min(cw * .72, dh * .58)
        cx, cy = x0 + col * cw + cw / 2, y0 + row * ch + ch / 2
        seven_seg(ctx, n, cx - dw / 2, cy - dh / 2, dw, dh, vis, glow, theme)


def seven_seg(ctx: Canvas, n, x, y, w, h, vis, glow: Glow, theme: Theme) -> None:
    t = w * .2
    hh = h / 2
    rects = {
        "a": (x + t * .6, y, w - t * 1.2, t),
        "g": (x + t * .6, y + hh - t / 2, w - t * 1.2, t),
        "d": (x + t * .6, y + h - t, w - t * 1.2, t),
        "f": (x, y + t * .6, t, hh - t * .9),
        "b": (x + w - t, y + t * .6, t, hh - t * .9),
        "e": (x, y + hh + t * .3, t, hh - t * .9),
        "c": (x + w - t, y + hh + t * .3, t, hh - t * .9),
    }
    on = SEGMENTS[n]
    for name, (rx, ry, rw, rh_) in rects.items():
        if name in on:
            glow(vis, .8)
            ctx.fill_style = vis
        else:
            ctx.fill_style = theme.unlit
        ctx.fill_rect(rx, ry, rw, rh_)
        glow.off()


# ---------------------------------------------------------------- 512-bit pair frame
PAIR_PAD, PAIR_GAP, PAIR_FOOT = S * .22, S * .15, S * .26
PAIR_W = W + 2 * PAIR_PAD
PAIR_H = 2 * H + PAIR_GAP + 2 * PAIR_PAD + PAIR_FOOT


def draw_pair(ctx: Canvas, parts: list[Features], theme: Theme) -> None:
    """Both halves of a 512-bit hash in one frame, numbered 1 and 2 and joined by a rail."""
    fg = theme.pair_fg
    ctx.begin_path()
    rr(ctx, 0, 0, PAIR_W, PAIR_H, S * .1)
    ctx.fill_style = theme.pair_bg
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
        draw_badge(ctx, f, theme)
        ctx.restore()
    for i, (x, y) in enumerate(badges):
        ctx.begin_path()
        ctx.arc(x, y, S * .075, 0, TAU)
        ctx.fill_style = fg
        ctx.fill()
        ctx.fill_style = theme.pair_bg
        ctx.set_font("mono", S * .1)
        ctx.text_align, ctx.text_baseline = "center", "middle"
        ctx.fill_text(str(i + 1), x, y + S * .006)
    ctx.fill_style = fg
    ctx.set_font("mono", S * .11)
    ctx.text_align, ctx.text_baseline = "center", "middle"
    ctx.fill_text("SHA-512 · 2 PARTS · READ 1 THEN 2", PAIR_W / 2, PAIR_H - PAIR_PAD * .35 - PAIR_FOOT / 2)


__all__ = ["draw_badge", "draw_pair", "layout_spec", "W", "H", "PAIR_W", "PAIR_H"]
