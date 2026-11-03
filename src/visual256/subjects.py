"""Buildings and animals: the two portrait kinds besides android heads.

Coordinates are badge units in the face slot: center x = hx, ground at y = 50 (the status chip
sits below at 52.4). The same bit fields as the android face pick the details:

    vstyle  windows (building) or eyes (animal)
    grille  door or nose and mouth
    mod     roof add-on or accessory
    cheek   ground details or markings
    decal   sign plaque or forehead mark

Mirrored line for line in docs/lab-template.html; keep them in sync.
"""

from __future__ import annotations

import math

from .canvas import Canvas
from .themes import Theme

TAU = math.tau


def _poly(ctx: Canvas, pts) -> None:
    for i, (x, y) in enumerate(pts):
        (ctx.line_to if i else ctx.move_to)(x, y)
    ctx.close_path()


# ---------------------------------------------------------------- buildings
def building_spec(b: int, c: float) -> dict:
    """Shape and anchor points of building b (0-11) centered on x = c."""
    if b == 0:  # house
        return dict(body=[[(c - 11, 28), (c + 11, 28), (c + 11, 50), (c - 11, 50)]],
                    roof=[[(c - 13.5, 28.5), (c, 15), (c + 13.5, 28.5)]],
                    win=(c - 9, 30.5, c + 9, 38.5), door=(c, 5, 8.5), top=(c + 6, 21), sign=(c - 7.5, 45))
    if b == 1:  # tower
        return dict(body=[[(c - 6, 50), (c - 6, 12), (c - 3.6, 12), (c - 3.6, 14), (c - 1.2, 14), (c - 1.2, 12), (c + 1.2, 12),
                           (c + 1.2, 14), (c + 3.6, 14), (c + 3.6, 12), (c + 6, 12), (c + 6, 50)]],
                    roof=[], win=(c - 4, 17, c + 4, 33), door=(c, 4, 6), top=(c, 12), sign=(c, 38.5))
    if b == 2:  # skyscraper
        return dict(body=[[(c - 9, 50), (c - 9, 20), (c - 6, 20), (c - 6, 12), (c + 6, 12), (c + 6, 20), (c + 9, 20), (c + 9, 50)]],
                    roof=[[(c - 1, 12), (c + 1, 12), (c, 5)]],
                    win=(c - 7, 22, c + 7, 40), door=(c, 6, 5), top=(c + 4, 12), sign=(c, 16))
    if b == 3:  # castle
        return dict(body=[[(c - 15, 50), (c - 15, 20), (c - 13, 20), (c - 13, 22), (c - 11, 22), (c - 11, 20), (c - 9, 20),
                           (c - 9, 28), (c - 6, 28), (c - 6, 30), (c - 3, 30), (c - 3, 28), (c + 3, 28), (c + 3, 30), (c + 6, 30),
                           (c + 6, 28), (c + 9, 28), (c + 9, 20), (c + 11, 20), (c + 11, 22), (c + 13, 22), (c + 13, 20),
                           (c + 15, 20), (c + 15, 50)]],
                    roof=[], win=(c - 7, 32, c + 7, 38.5), door=(c, 6, 8), top=(c - 12, 20), sign=(c + 12, 30))
    if b == 4:  # pagoda
        return dict(body=[[(c - 9, 40), (c + 9, 40), (c + 9, 50), (c - 9, 50)], [(c - 7, 31), (c + 7, 31), (c + 7, 37), (c - 7, 37)],
                          [(c - 5, 22), (c + 5, 22), (c + 5, 28), (c - 5, 28)]],
                    roof=[[(c - 13, 40), (c + 13, 40), (c + 9, 37), (c - 9, 37)], [(c - 11, 31), (c + 11, 31), (c + 7, 28), (c - 7, 28)],
                          [(c - 9, 22), (c + 9, 22), (c, 15)]],
                    win=(c - 5, 31.8, c + 5, 36.4), door=(c, 4, 6.5), top=(c, 15), sign=(c, 25))
    if b == 5:  # observatory
        return dict(body=[[(c - 12, 33), (c + 12, 33), (c + 12, 50), (c - 12, 50)]], roof=[], dome=(c, 33, 10),
                    win=(c - 10, 35.5, c + 10, 41), door=(c, 5, 7), top=(c, 23), sign=(c - 8.5, 45.5))
    if b == 6:  # lighthouse
        return dict(body=[[(c - 5, 18), (c + 5, 18), (c + 8, 50), (c - 8, 50)], [(c - 4, 11), (c + 4, 11), (c + 4, 18), (c - 4, 18)]],
                    roof=[[(c - 5.5, 11.5), (c + 5.5, 11.5), (c, 6)], [(c - 6.2, 40), (c + 6.2, 40), (c + 6.6, 42.6), (c - 6.6, 42.6)]],
                    win=(c - 2.5, 20, c + 2.5, 28), door=(c, 4, 5.5), top=(c + 4, 11), sign=(c, 32.5))
    if b == 7:  # factory
        return dict(body=[[(c - 14, 50), (c - 14, 30), (c - 9, 25), (c - 9, 30), (c - 4, 25), (c - 4, 30), (c + 1, 25), (c + 1, 30),
                           (c + 12, 30), (c + 12, 50)], [(c + 7, 14), (c + 11, 14), (c + 11, 30), (c + 7, 30)]],
                    roof=[], win=(c - 12, 33, c + 5, 40), door=(c + 8, 5, 8), top=(c - 9, 25), sign=(c - 8, 45))
    if b == 8:  # chapel
        return dict(body=[[(c - 3, 15), (c + 3, 15), (c + 3, 26), (c - 3, 26)], [(c - 9, 31), (c + 9, 31), (c + 9, 50), (c - 9, 50)]],
                    roof=[[(c - 10.5, 31.5), (c, 23), (c + 10.5, 31.5)], [(c - 3.8, 15.5), (c, 6), (c + 3.8, 15.5)]],
                    win=(c - 7, 33.5, c + 7, 40), door=(c, 5, 8), top=(c + 6.5, 28), sign=(c, 19.5))
    if b == 9:  # temple
        body = [[(c - 13, 24), (c + 13, 24), (c + 13, 27), (c - 13, 27)],
                [(c - 14, 46), (c + 14, 46), (c + 14, 48), (c - 14, 48)], [(c - 15, 48), (c + 15, 48), (c + 15, 50), (c - 15, 50)]]
        for x in (c - 11, c - 7, c + 7, c + 11):
            body.append([(x - 1.3, 27), (x + 1.3, 27), (x + 1.3, 46), (x - 1.3, 46)])
        return dict(body=body, roof=[[(c - 14, 24), (c, 15), (c + 14, 24)]],
                    win=(c - 5, 29, c + 5, 36), door=(c, 5, 7.5), top=(c + 8, 19.5), sign=(c, 20.8))
    if b == 10:  # windmill
        return dict(body=[[(c - 5, 22), (c + 5, 22), (c + 8, 50), (c - 8, 50)]], roof=[], dome=(c, 22, 5), blades=(c, 19),
                    win=(c - 3, 26, c + 3, 35), door=(c, 4, 6), top=(c + 4, 18), sign=(c, 39.5))
    # needle tower
    return dict(body=[[(c - 2.5, 18), (c + 2.5, 18), (c + 2.5, 50), (c - 2.5, 50)]], roof=[[(c - .5, 12), (c + .5, 12), (c, 4)]],
                saucer=(c, 16, 12, 4), legs=True, win=(c - 9, 14.6, c + 9, 17.4), door=(c, 3, 5), top=(c + 6, 15), sign=(c, 27))


def draw_building(ctx: Canvas, f, c: float, glow, vis: str, trim: str, t: Theme) -> None:
    sp = building_spec(f.subject - 8, c)
    ctx.line_join, ctx.line_cap = "round", "round"
    ctx.begin_path()
    ctx.move_to(c - 16, 50)
    ctx.line_to(c + 16, 50)
    ctx.line_width, ctx.stroke_style = .6, trim
    ctx.stroke()
    if sp.get("legs"):
        ctx.begin_path()
        ctx.move_to(c - 8, 50)
        ctx.line_to(c, 34)
        ctx.line_to(c + 8, 50)
        ctx.line_width = .7
        ctx.stroke()
    ctx.begin_path()
    for pts in sp["body"]:
        _poly(ctx, pts)
    ctx.fill_style = t.panel
    ctx.fill()
    glow(trim, 1)
    ctx.line_width, ctx.stroke_style = .7, trim
    ctx.stroke()
    glow.off()
    if "dome" in sp:
        dx, dy, r = sp["dome"]
        ctx.begin_path()
        ctx.move_to(dx - r, dy)
        ctx.arc(dx, dy, r, math.pi, TAU)
        ctx.close_path()
        ctx.fill_style = trim
        ctx.fill()
        if "blades" not in sp:
            ctx.begin_path()
            ctx.move_to(dx + r * .2, dy - r * .95)
            ctx.line_to(dx + r * .2, dy)
            ctx.line_width, ctx.stroke_style = 1, t.panel
            ctx.stroke()
    if "saucer" in sp:
        sx, sy, rx, ry = sp["saucer"]
        ctx.begin_path()
        ctx.ellipse(sx, sy, rx, ry, 0, 0, TAU)
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.line_width, ctx.stroke_style = .7, trim
        ctx.stroke()
    if sp["roof"]:
        ctx.begin_path()
        for pts in sp["roof"]:
            _poly(ctx, pts)
        ctx.fill_style = trim
        ctx.fill()
    draw_windows(ctx, f.vstyle, *sp["win"], vis, glow, t)
    draw_door(ctx, f.grille, *sp["door"], vis, trim, glow, t)
    if "blades" in sp:
        bx, by = sp["blades"]
        ctx.begin_path()
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            ctx.move_to(bx, by)
            ctx.line_to(bx + 15 * math.cos(a), by + 15 * math.sin(a))
        ctx.line_width, ctx.stroke_style = .8, trim
        ctx.stroke()
        ctx.begin_path()
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            ca, sa = math.cos(a), math.sin(a)
            px, py = -sa, ca
            pts = [(bx + 5 * ca, by + 5 * sa), (bx + 14 * ca, by + 14 * sa),
                   (bx + 14 * ca + 3 * px, by + 14 * sa + 3 * py), (bx + 5 * ca + 3 * px, by + 5 * sa + 3 * py)]
            _poly(ctx, pts)
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.line_width = .5
        ctx.stroke()
    sx, sy = sp["sign"]
    ctx.begin_path()
    ctx.rect(sx - 2.4, sy - 2.4, 4.8, 4.8)
    ctx.fill_style = t.panel
    ctx.fill()
    ctx.line_width, ctx.stroke_style = .45, trim
    ctx.stroke()
    _symbol(ctx, f.decal, sx, sy, 1.8, trim)
    draw_roof_mod(ctx, f.mod, *sp["top"], vis, trim, glow)
    draw_ground(ctx, f.cheek, c, sp["door"], vis, trim, glow, t)


def draw_windows(ctx: Canvas, style, x0, y0, x1, y1, vis, glow, t: Theme) -> None:
    w, h = x1 - x0, y1 - y0
    cols = max(1, min(4, int(w / 4.2)))
    rows = max(1, min(3, int(h / 4.2)))
    cw, ch = w / cols, h / rows
    ww, wh = cw * .62, ch * .66
    glow(vis, 1)
    ctx.fill_style = vis
    ctx.begin_path()
    if style == 3:
        for r in range(rows):
            ctx.rect(x0 + .3, y0 + r * ch + (ch - wh * .7) / 2, w - .6, wh * .7)
    elif style == 4:
        for k in range(cols):
            ctx.rect(x0 + k * cw + (cw - ww * .7) / 2, y0 + .3, ww * .7, h - .6)
    elif style == 5:
        ctx.rect(x0 + .4, y0 + .4, w - .8, h - .8)
    else:
        for r in range(rows):
            for k in range(cols):
                cx, cy = x0 + k * cw + cw / 2, y0 + r * ch + ch / 2
                if style == 0 or (style == 7 and (r + k) % 2 == 0):
                    ctx.rect(cx - ww / 2, cy - wh / 2, ww, wh)
                elif style == 1:
                    rad = min(ww, wh) / 2
                    ctx.move_to(cx + rad, cy)
                    ctx.arc(cx, cy, rad, 0, TAU)
                elif style == 2:
                    ctx.move_to(cx - ww / 2, cy + wh / 2)
                    ctx.line_to(cx - ww / 2, cy - wh / 2 + ww / 2)
                    ctx.arc(cx, cy - wh / 2 + ww / 2, ww / 2, math.pi, TAU)
                    ctx.line_to(cx + ww / 2, cy + wh / 2)
                    ctx.close_path()
                elif style == 6:
                    rad = min(ww, wh) / 2 * 1.15
                    _poly(ctx, [(cx, cy - rad), (cx + rad, cy), (cx, cy + rad), (cx - rad, cy)])
    ctx.fill()
    glow.off()
    if style == 5:
        ctx.begin_path()
        ctx.move_to((x0 + x1) / 2, y0 + .4)
        ctx.line_to((x0 + x1) / 2, y1 - .4)
        ctx.move_to(x0 + .4, (y0 + y1) / 2)
        ctx.line_to(x1 - .4, (y0 + y1) / 2)
        ctx.line_width, ctx.stroke_style = .5, t.panel
        ctx.stroke()
    elif style == 7:
        ctx.begin_path()
        for r in range(rows):
            for k in range(cols):
                if (r + k) % 2:
                    cx, cy = x0 + k * cw + cw / 2, y0 + r * ch + ch / 2
                    ctx.rect(cx - ww / 2, cy - wh / 2, ww, wh)
        ctx.fill_style = t.unlit
        ctx.fill()


def draw_door(ctx: Canvas, style, cx, w, h, vis, trim, glow, t: Theme) -> None:
    x, y = cx - w / 2, 50 - h
    ctx.begin_path()
    if style == 1:
        ctx.move_to(x, 50)
        ctx.line_to(x, y + w / 2)
        ctx.arc(cx, y + w / 2, w / 2, math.pi, TAU)
        ctx.line_to(x + w, 50)
        ctx.close_path()
    elif style == 3:
        r = w * .58
        ctx.move_to(cx + r, 50 - r)
        ctx.arc(cx, 50 - r, r, 0, TAU)
    else:
        ctx.rect(x, y, w, h)
    if style == 5:
        ctx.line_width, ctx.stroke_style = .5, trim
        ctx.stroke()
        ctx.begin_path()
        for k in range(1, 4):
            ctx.move_to(x + k * w / 4, y)
            ctx.line_to(x + k * w / 4, 50)
        ctx.stroke()
        return
    if style == 6:
        glow(vis, 1)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
        ctx.line_width, ctx.stroke_style = .5, trim
        ctx.stroke()
        return
    ctx.fill_style = trim
    ctx.fill()
    ctx.begin_path()
    if style == 2:
        ctx.move_to(cx, y + .4)
        ctx.line_to(cx, 50)
    elif style == 4:
        for k in range(1, 4):
            ctx.move_to(x + .4, y + k * h / 4)
            ctx.line_to(x + w - .4, y + k * h / 4)
    elif style == 7:
        ctx.fill_style = trim
        _poly(ctx, [(cx - w * .85, y - .3), (cx + w * .85, y - .3), (cx + w * .55, y - 2.6), (cx - w * .55, y - 2.6)])
        ctx.fill()
        return
    elif style == 0:
        ctx.move_to(x + w * .78, y + h * .55)
        ctx.arc(x + w * .78 - .35, y + h * .55, .35, 0, TAU)
    else:
        ctx.move_to(x + w * .25, y + h * .25)
        ctx.line_to(x + w * .75, y + h * .25)
    ctx.line_width, ctx.stroke_style = .4, t.panel
    ctx.stroke()


def draw_roof_mod(ctx: Canvas, style, tx, ty, vis, trim, glow) -> None:
    ctx.line_width, ctx.stroke_style, ctx.fill_style = .6, trim, trim
    ctx.begin_path()
    if style == 0:
        ctx.move_to(tx, ty)
        ctx.line_to(tx, ty - 6)
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(tx, ty - 6.6, 1, 0, TAU)
        ctx.fill()
    elif style == 1:
        ctx.move_to(tx, ty)
        ctx.line_to(tx, ty - 7)
        ctx.stroke()
        ctx.begin_path()
        _poly(ctx, [(tx, ty - 7), (tx + 4.2, ty - 5.8), (tx, ty - 4.6)])
        glow(vis, .8)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
    elif style == 2:
        ctx.rect(tx + 1, ty - 5, 2.4, 5)
        ctx.fill()
        ctx.begin_path()
        ctx.move_to(tx + 3.3, ty - 7)
        ctx.arc(tx + 2.2, ty - 7, 1.1, 0, TAU)
        ctx.move_to(tx + 4.2, ty - 9.2)
        ctx.arc(tx + 3.4, ty - 9.2, .8, 0, TAU)
        ctx.global_alpha = .55
        ctx.fill()
        ctx.global_alpha = 1
    else:
        ctx.move_to(tx, ty)
        ctx.line_to(tx, ty - 2.5)
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(tx, ty - 4.6, 2.6, math.pi * .15, math.pi * 1.15)
        ctx.close_path()
        ctx.fill()
        ctx.begin_path()
        ctx.move_to(tx, ty - 4.6)
        ctx.line_to(tx + 2, ty - 6.8)
        ctx.stroke()


def draw_ground(ctx: Canvas, style, c, door, vis, trim, glow, t: Theme) -> None:
    dcx, dw, _ = door
    ctx.line_width, ctx.stroke_style, ctx.fill_style = .5, trim, trim
    ctx.begin_path()
    if style == 0:
        ctx.rect(dcx - dw * .85, 48.8, dw * 1.7, 1.2)
        ctx.rect(dcx - dw * .65, 47.6, dw * 1.3, 1.2)
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.stroke()
    elif style == 1:
        for s in (-1, 1):
            for k in range(4):
                x = c + s * (12 + k * 1.3)
                ctx.move_to(x, 50)
                ctx.line_to(x, 46.6)
            ctx.move_to(c + s * 11.5, 48)
            ctx.line_to(c + s * 16.4, 48)
        ctx.stroke()
    elif style == 2:
        for s in (-1, 1):
            for dx, r in ((13.8, 1.8), (11.4, 1.4), (15.6, 1.2)):
                ctx.move_to(c + s * dx + r, 50 - r * .8)
                ctx.arc(c + s * dx, 50 - r * .8, r, 0, TAU)
        ctx.fill()
    else:
        for s in (-1, 1):
            ctx.move_to(c + s * 14, 50)
            ctx.line_to(c + s * 14, 43)
        ctx.stroke()
        ctx.begin_path()
        for s in (-1, 1):
            ctx.move_to(c + s * 14 + 1, 42.4)
            ctx.arc(c + s * 14, 42.4, 1, 0, TAU)
        glow(vis, 1)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()


# ---------------------------------------------------------------- animals
# (head center y, head rx, ry, eye dx, eye y, eye scale, nose y, top of head)
ANIMAL_SPECS = (
    (31, 13, 12, 5, 29, 1, 34.5, 19),     # cat
    (29, 11, 12, 4.5, 27, 1, 34.5, 17),   # dog
    (31, 13, 12, 5, 28, 1, 34.5, 19),     # bear
    (32, 11, 11, 4.5, 30, 1, 35.5, 21),   # rabbit
    (30, 14, 12, 5, 27, 1, 38, 22),       # fox
    (30, 14, 13, 5.5, 28, 1.35, 38.4, 17),  # owl
    (32, 10, 10, 4, 30, 1, 35, 22),       # mouse
    (31, 13, 12, 5.5, 28, 1, 40, 19),     # pig
    (31, 14, 10, 7, 20.5, 1.1, 33, 21),   # frog
    (30, 12, 13, 4, 29, 1, 37.5, 17),     # penguin
    (31, 11, 11, 4.5, 28, 1, 34.5, 20),   # lion
    (31, 13, 12, 5, 29, 1, 34.5, 19),     # panda
)


def draw_animal(ctx: Canvas, f, c: float, glow, vis: str, trim: str, t: Theme) -> None:
    a = f.subject - 20
    hy, rx, ry, edx, ey, ek, ny, top = ANIMAL_SPECS[a]
    panel = t.panel
    ctx.line_join, ctx.line_cap = "round", "round"

    def outline(width=.7):
        glow(trim, 1)
        ctx.line_width, ctx.stroke_style = width, trim
        ctx.stroke()
        glow.off()

    def fill_out(color, width=.7):
        ctx.fill_style = color
        ctx.fill()
        outline(width)

    # behind the head
    ctx.begin_path()
    if a == 0:
        for s in (-1, 1):
            _poly(ctx, [(c + s * 11, 22), (c + s * 9.5, 9.5), (c + s * 3, 18)])
        fill_out(panel)
        ctx.begin_path()
        for s in (-1, 1):
            _poly(ctx, [(c + s * 9.4, 19.5), (c + s * 9, 13), (c + s * 5.6, 18)])
        ctx.fill_style = trim
        ctx.fill()
    elif a in (2, 11):
        for s in (-1, 1):
            ctx.move_to(c + s * 9.5 + 4, 19)
            ctx.arc(c + s * 9.5, 19, 4, 0, TAU)
        fill_out(trim if a == 11 else panel)
        if a == 2:
            ctx.begin_path()
            for s in (-1, 1):
                ctx.move_to(c + s * 9.5 + 2, 19)
                ctx.arc(c + s * 9.5, 19, 2, 0, TAU)
            ctx.fill_style = trim
            ctx.fill()
    elif a == 3:
        for s in (-1, 1):
            ctx.begin_path()
            ctx.ellipse(c + s * 4.5, 12, 3, 9.5, s * .12, 0, TAU)
            fill_out(panel)
        ctx.fill_style = trim
        for s in (-1, 1):
            ctx.begin_path()
            ctx.ellipse(c + s * 4.5, 13, 1.2, 6.5, s * .12, 0, TAU)
            ctx.fill()
    elif a == 4:
        for s in (-1, 1):
            _poly(ctx, [(c + s * 12.5, 23), (c + s * 11.5, 8.5), (c + s * 4, 17)])
        fill_out(panel)
        ctx.begin_path()
        for s in (-1, 1):
            _poly(ctx, [(c + s * 10.8, 20), (c + s * 10.6, 12), (c + s * 6.4, 17.4)])
        ctx.fill_style = trim
        ctx.fill()
    elif a == 5:
        for s in (-1, 1):
            _poly(ctx, [(c + s * 12, 20), (c + s * 13, 10), (c + s * 6, 17.5)])
        fill_out(trim)
    elif a == 6:
        for s in (-1, 1):
            ctx.move_to(c + s * 10 + 6.5, 19)
            ctx.arc(c + s * 10, 19, 6.5, 0, TAU)
        fill_out(panel)
        ctx.begin_path()
        for s in (-1, 1):
            ctx.move_to(c + s * 10 + 4, 19)
            ctx.arc(c + s * 10, 19, 4, 0, TAU)
        ctx.fill_style = trim
        ctx.fill()
    elif a == 7:
        for s in (-1, 1):
            _poly(ctx, [(c + s * 12, 22), (c + s * 11, 12.5), (c + s * 5, 19.5)])
        fill_out(trim)
    elif a == 8:
        for s in (-1, 1):
            ctx.move_to(c + s * 7 + 4.6, 21)
            ctx.arc(c + s * 7, 21, 4.6, 0, TAU)
        fill_out(panel)
    elif a == 10:
        pts = []
        for k in range(120):
            th = TAU * k / 120
            r = 16 + 1.6 * abs(math.cos(th * 7))
            pts.append((c + r * math.cos(th), hy + r * math.sin(th)))
        _poly(ctx, pts)
        fill_out(trim)

    # the head
    ctx.begin_path()
    if a == 4:
        _poly(ctx, [(c - 14, 22), (c + 14, 22), (c + 9, 34), (c, 42), (c - 9, 34)])
    else:
        ctx.ellipse(c, hy, rx, ry, 0, 0, TAU)
    fill_out(trim if a == 9 else panel)

    # in front of the head
    if a == 1:
        ctx.begin_path()
        for s in (-1, 1):
            ctx.begin_path()
            ctx.ellipse(c + s * 11.5, 29, 4, 9, -s * .35, 0, TAU)
            fill_out(trim)
    if a in (1, 2, 10):
        ctx.begin_path()
        ctx.ellipse(c, 36, 5.8 if a == 1 else 5.4, 4.4 if a == 1 else 3.9, 0, 0, TAU)
        fill_out(panel, .5)
    if a == 5:
        ctx.begin_path()
        for s in (-1, 1):
            ctx.move_to(c + s * 5.5 + 5.4, 28)
            ctx.arc(c + s * 5.5, 28, 5.4, 0, TAU)
        fill_out(panel, .5)
    if a == 7:
        ctx.begin_path()
        ctx.ellipse(c, 35, 5, 3.5, 0, 0, TAU)
        fill_out(panel, .5)
        ctx.fill_style = trim
        for s in (-1, 1):
            ctx.begin_path()
            ctx.ellipse(c + s * 1.8, 35, .8, 1.3, 0, 0, TAU)
            ctx.fill()
    if a == 9:
        ctx.begin_path()
        for s in (-1, 1):
            ctx.move_to(c + s * 4 + 6, 30)
            ctx.arc(c + s * 4, 30, 6, 0, TAU)
        ctx.move_to(c + 7, 35)
        ctx.ellipse(c, 35, 7, 6, 0, 0, TAU)
        ctx.fill_style = panel
        ctx.fill()
    if a == 11:
        ctx.fill_style = trim
        for s in (-1, 1):
            ctx.begin_path()
            ctx.ellipse(c + s * 5, 29, 3.6, 4.4, s * .4, 0, TAU)
            ctx.fill()
    if a in (5, 9):
        ctx.begin_path()
        _poly(ctx, [(c - 1.6, 32.5 if a == 5 else 33), (c + 1.6, 32.5 if a == 5 else 33), (c, 36.5 if a == 5 else 36)])
        ctx.fill_style = trim
        ctx.fill()

    mark_color = panel if a == 9 else trim
    _symbol(ctx, f.decal, c, top + 3.6, 2, mark_color)
    draw_markings(ctx, f.cheek, c, ny, rx, trim)
    eye_y = ey
    for s in (-1, 1):
        draw_eye(ctx, f.vstyle, c + s * edx, eye_y, ek, -s, vis, trim, glow)
    draw_snout(ctx, f.grille, c, ny, vis, trim, panel, glow)
    draw_accessory(ctx, f.mod, c, top, vis, trim, glow)


def draw_eye(ctx: Canvas, style, x, y, k, side, vis, trim, glow) -> None:
    glow(vis, .8)
    ctx.fill_style = ctx.stroke_style = vis
    ctx.begin_path()
    if style == 0:
        ctx.arc(x, y, 1.5 * k, 0, TAU)
        ctx.fill()
    elif style == 1:
        ctx.arc(x, y, 2.5 * k, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.arc(x - .8 * k, y - .8 * k, .75 * k, 0, TAU)
        ctx.fill_style = "#FFFFFF"
        ctx.fill()
    elif style in (2, 3):
        a0, a1 = (0, math.pi) if style == 2 else (math.pi, TAU)
        ctx.arc(x, y, 2 * k, a0, a1)
        ctx.line_width = .75
        ctx.stroke()
    elif style == 4:
        ctx.arc(x, y + .4, 1.5 * k, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.move_to(x - 2.2 * k * side, y - 2.6 * k)
        ctx.line_to(x + 2.2 * k * side, y - 1.6 * k)
        ctx.line_width, ctx.stroke_style = .7, trim
        ctx.stroke()
    elif style == 5:
        ctx.ellipse(x, y, 1.8 * k, 2.6 * k, 0, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.ellipse(x, y, .45 * k, 2.1 * k, 0, 0, TAU)
        ctx.fill_style = trim
        ctx.fill()
    else:
        _symbol(ctx, 4 if style == 6 else 7, x, y, (2.4 if style == 6 else 2.3) * k, vis)
    glow.off()


def draw_snout(ctx: Canvas, style, c, ny, vis, trim, panel, glow) -> None:
    ctx.fill_style = ctx.stroke_style = trim
    ctx.line_width = .55

    def small_nose():
        ctx.begin_path()
        _poly(ctx, [(c - 1.1, ny - .9), (c + 1.1, ny - .9), (c, ny + .3)])
        ctx.fill()

    def mouth_line():
        ctx.begin_path()
        ctx.move_to(c, ny + .3)
        ctx.line_to(c, ny + 1.6)
        ctx.move_to(c - 2, ny + 1.6)
        ctx.line_to(c + 2, ny + 1.6)
        ctx.stroke()

    if style == 0:
        ctx.begin_path()
        _poly(ctx, [(c - 1.7, ny - 1.1), (c + 1.7, ny - 1.1), (c, ny + .9)])
        ctx.fill()
        ctx.begin_path()
        ctx.move_to(c, ny + .9)
        ctx.line_to(c, ny + 1.8)
        ctx.arc(c - 1.1, ny + 1.8, 1.1, 0, math.pi)
        ctx.move_to(c + 2.2, ny + 1.8)
        ctx.arc(c + 1.1, ny + 1.8, 1.1, 0, math.pi)
        ctx.stroke()
    elif style == 1:
        ctx.begin_path()
        ctx.arc(c, ny - .3, 1.3, 0, TAU)
        ctx.fill()
        ctx.begin_path()
        ctx.arc(c, ny + .4, 2.2, .18 * math.pi, .82 * math.pi)
        ctx.stroke()
    elif style == 2:
        _symbol(ctx, 7, c, ny - .2, 1.6, trim)
        ctx.begin_path()
        ctx.move_to(c, ny + 1.2)
        ctx.line_to(c, ny + 2.6)
        ctx.stroke()
    elif style == 3:
        small_nose()
        ctx.begin_path()
        ctx.ellipse(c, ny + 2.8, 1.8, 1.4, 0, 0, TAU)
        ctx.fill()
    elif style == 4:
        small_nose()
        mouth_line()
        ctx.begin_path()
        ctx.ellipse(c + .4, ny + 3, 1.2, 1.6, 0, 0, TAU)
        glow(vis, .6)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
    elif style == 5:
        small_nose()
        mouth_line()
        ctx.begin_path()
        ctx.rect(c - 1.3, ny + 1.6, 1.2, 1.7)
        ctx.rect(c + .1, ny + 1.6, 1.2, 1.7)
        ctx.fill_style = panel
        ctx.fill()
        ctx.line_width = .35
        ctx.stroke()
    elif style == 6:
        ctx.begin_path()
        ctx.arc(c, ny - .4, .8, 0, TAU)
        ctx.fill()
        ctx.begin_path()
        ctx.move_to(c - 2.4, ny + 1)
        ctx.arc(c - 1.2, ny + 1, 1.2, math.pi, 0, True)
        ctx.arc(c + 1.2, ny + 1, 1.2, math.pi, 0, True)
        ctx.stroke()
    else:
        small_nose()
        mouth_line()
        ctx.begin_path()
        for s in (-1, 1):
            _poly(ctx, [(c + s * 1.6 - .6, ny + 1.6), (c + s * 1.6 + .6, ny + 1.6), (c + s * 1.6, ny + 3.4)])
        ctx.fill_style = panel
        ctx.fill()
        ctx.line_width = .3
        ctx.stroke()


def draw_markings(ctx: Canvas, style, c, ny, rx, trim) -> None:
    ctx.stroke_style = ctx.fill_style = trim
    ctx.line_width = .45
    ctx.begin_path()
    if style == 0:
        for s in (-1, 1):
            for dy in (-1.2, 0, 1.2):
                ctx.move_to(c + s * 5, ny + dy * .5)
                ctx.line_to(c + s * 12.5, ny + dy * 1.6)
        ctx.stroke()
    elif style == 1:
        for s in (-1, 1):
            for dx, dy in ((7.5, -.6), (9.2, .8), (7.2, 1.6)):
                ctx.move_to(c + s * dx + .55, ny + dy)
                ctx.arc(c + s * dx, ny + dy, .55, 0, TAU)
        ctx.fill()
    elif style == 2:
        for s in (-1, 1):
            ctx.move_to(c + s * 8.2 + 2.3, ny - 1)
            ctx.ellipse(c + s * 8.2, ny - 1, 2.3, 1.3, 0, 0, TAU)
        ctx.fill_style = "rgba(255,105,140,.55)"
        ctx.fill()
    else:
        for s in (-1, 1):
            x = c + s * (rx - 1.5)
            for dy in (-3, 0, 3):
                ctx.move_to(x, ny - 6 + dy)
                ctx.line_to(x - s * 2.6, ny - 5 + dy)
        ctx.line_width = .6
        ctx.stroke()


def draw_accessory(ctx: Canvas, style, c, top, vis, trim, glow) -> None:
    glow(vis, .8)
    ctx.fill_style = vis
    ctx.begin_path()
    if style == 0:
        ctx.rect(c - 8, 42.6, 16, 1.8)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.arc(c, 45.8, 1.4, 0, TAU)
        ctx.fill_style = trim
        ctx.fill()
    elif style == 1:
        bx, by = c + 8.5, top + 1.5
        _poly(ctx, [(bx, by), (bx - 3.6, by - 2.2), (bx - 3.6, by + 2.2)])
        _poly(ctx, [(bx, by), (bx + 3.6, by - 2.2), (bx + 3.6, by + 2.2)])
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.arc(bx, by, .9, 0, TAU)
        ctx.fill_style = trim
        ctx.fill()
    elif style == 2:
        _poly(ctx, [(c - 4, top + 1.2), (c + 4, top + 1.2), (c + 1, top - 8.5)])
        ctx.fill()
        glow.off()
        ctx.line_width, ctx.stroke_style = .45, trim
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(c + 1, top - 8.8, 1.1, 0, TAU)
        ctx.fill_style = trim
        ctx.fill()
    else:
        ctx.rect(c - 9, 41.8, 18, 2.6)
        ctx.rect(c + 3.5, 43.6, 2.6, 6)
        ctx.fill()
        glow.off()
        ctx.line_width, ctx.stroke_style = .35, trim
        ctx.stroke()
    glow.off()


def _symbol(ctx: Canvas, i, x, y, r, fill) -> None:
    from .draw import draw_symbol
    draw_symbol(ctx, i, x, y, r, fill)
