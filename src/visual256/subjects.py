"""Buildings, animals, vehicles, plants, furniture, food and sports gear: the portrait kinds besides heads.

Coordinates are badge units in the face slot: center x = hx, ground at y = 50 (the status chip
sits below at 52.4). The same bit fields as the android face pick the details:

    field   building     animal          vehicle   plant          furniture         food       sports
    vstyle  windows      eyes            windows   blooms         fabric            toppings   print
    grille  door         nose and mouth  trail     pot            companion object  serving    gear
    mod     roof add-on  accessory       add-on    visitor        wall item         topper     motion
    cheek   grounds      markings        livery    ground extras  floor             side item  pitch
    decal   sign         forehead mark   emblem    pot label      plaque            label      team badge

Mirrored line for line in docs/lab-template.html; keep them in sync.
"""

from __future__ import annotations

import math

from .canvas import Canvas
from .icons import icon_spec, shifted
from .spec import (ANIMALS, BUILDINGS, FOODS, FURNITURE, NO_BOW_TIE, PLANTS, SPORTS, SUBJECT_KINDS, SUBJECT_START,
                   VEHICLES)
from .themes import Theme

TAU = math.tau


def _poly(ctx: Canvas, pts) -> None:
    for i, (x, y) in enumerate(pts):
        (ctx.line_to if i else ctx.move_to)(x, y)
    ctx.close_path()


# ---------------------------------------------------------------- buildings
def building_spec(b: str, c: float) -> dict:
    """Shape and anchor points of the building named b, centered on x = c."""
    if b == "house":
        return dict(body=[[(c - 11, 28), (c + 11, 28), (c + 11, 50), (c - 11, 50)]],
                    roof=[[(c - 13.5, 28.5), (c, 15), (c + 13.5, 28.5)]],
                    win=(c - 9, 30.5, c + 9, 38.5), door=(c, 5, 8.5), top=(c + 6, 21), sign=(c - 7.5, 45))
    if b == "skyscraper":
        return dict(body=[[(c - 9, 50), (c - 9, 20), (c - 6, 20), (c - 6, 12), (c + 6, 12), (c + 6, 20), (c + 9, 20), (c + 9, 50)]],
                    roof=[[(c - 1, 12), (c + 1, 12), (c, 5)]],
                    win=(c - 7, 22, c + 7, 40), door=(c, 6, 5), top=(c + 4, 12), sign=(c, 16))
    if b == "castle":
        return dict(body=[[(c - 15, 50), (c - 15, 20), (c - 13, 20), (c - 13, 22), (c - 11, 22), (c - 11, 20), (c - 9, 20),
                           (c - 9, 28), (c - 6, 28), (c - 6, 30), (c - 3, 30), (c - 3, 28), (c + 3, 28), (c + 3, 30), (c + 6, 30),
                           (c + 6, 28), (c + 9, 28), (c + 9, 20), (c + 11, 20), (c + 11, 22), (c + 13, 22), (c + 13, 20),
                           (c + 15, 20), (c + 15, 50)]],
                    roof=[], win=(c - 7, 32, c + 7, 38.5), door=(c, 6, 8), top=(c - 12, 20), sign=(c + 12, 30))
    if b == "pagoda":
        return dict(body=[[(c - 9, 40), (c + 9, 40), (c + 9, 50), (c - 9, 50)], [(c - 7, 31), (c + 7, 31), (c + 7, 37), (c - 7, 37)],
                          [(c - 5, 22), (c + 5, 22), (c + 5, 28), (c - 5, 28)]],
                    roof=[[(c - 13, 40), (c + 13, 40), (c + 9, 37), (c - 9, 37)], [(c - 11, 31), (c + 11, 31), (c + 7, 28), (c - 7, 28)],
                          [(c - 9, 22), (c + 9, 22), (c, 15)]],
                    win=(c - 5, 31.8, c + 5, 36.4), door=(c, 4, 6.5), top=(c, 15), sign=(c, 25))
    if b == "observatory":
        return dict(body=[[(c - 12, 33), (c + 12, 33), (c + 12, 50), (c - 12, 50)]], roof=[], dome=(c, 33, 10),
                    win=(c - 10, 35.5, c + 10, 41), door=(c, 5, 7), top=(c, 23), sign=(c - 8.5, 45.5))
    if b == "lighthouse":
        return dict(body=[[(c - 5, 18), (c + 5, 18), (c + 8, 50), (c - 8, 50)], [(c - 4, 11), (c + 4, 11), (c + 4, 18), (c - 4, 18)]],
                    roof=[[(c - 5.5, 11.5), (c + 5.5, 11.5), (c, 6)], [(c - 6.2, 40), (c + 6.2, 40), (c + 6.6, 42.6), (c - 6.6, 42.6)]],
                    win=(c - 2.5, 20, c + 2.5, 28), door=(c, 4, 5.5), top=(c + 4, 11), sign=(c, 32.5))
    if b == "factory":
        return dict(body=[[(c - 14, 50), (c - 14, 30), (c - 9, 25), (c - 9, 30), (c - 4, 25), (c - 4, 30), (c + 1, 25), (c + 1, 30),
                           (c + 12, 30), (c + 12, 50)], [(c + 7, 14), (c + 11, 14), (c + 11, 30), (c + 7, 30)]],
                    roof=[], win=(c - 12, 33, c + 5, 40), door=(c + 8, 5, 8), top=(c - 9, 25), sign=(c - 8, 45))
    if b == "temple":
        body = [[(c - 13, 24), (c + 13, 24), (c + 13, 27), (c - 13, 27)],
                [(c - 14, 46), (c + 14, 46), (c + 14, 48), (c - 14, 48)], [(c - 15, 48), (c + 15, 48), (c + 15, 50), (c - 15, 50)]]
        for x in (c - 11, c - 7, c + 7, c + 11):
            body.append([(x - 1.3, 27), (x + 1.3, 27), (x + 1.3, 46), (x - 1.3, 46)])
        return dict(body=body, roof=[[(c - 14, 24), (c, 15), (c + 14, 24)]],
                    win=(c - 5, 29, c + 5, 36), door=(c, 5, 7.5), top=(c + 8, 19.5), sign=(c, 20.8))
    if b == "windmill":
        return dict(body=[[(c - 5, 22), (c + 5, 22), (c + 8, 50), (c - 8, 50)]], roof=[], dome=(c, 22, 5), blades=(c, 19),
                    win=(c - 3, 26, c + 3, 35), door=(c, 4, 6), top=(c + 4, 18), sign=(c, 39.5))
    # needle tower
    return dict(body=[[(c - 2.5, 18), (c + 2.5, 18), (c + 2.5, 50), (c - 2.5, 50)]], roof=[[(c - .5, 12), (c + .5, 12), (c, 4)]],
                saucer=(c, 16, 12, 4), legs=True, win=(c - 9, 14.6, c + 9, 17.4), door=(c, 3, 5), top=(c + 6, 15), sign=(c, 27))


def draw_building(ctx: Canvas, f, c: float, glow, vis: str, trim: str, t: Theme) -> None:
    sp = building_spec(BUILDINGS[f.subject - SUBJECT_START["building"]], c)
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
ANIMAL_SPECS = {  # head y, head rx, ry, eye dx, eye y, eye scale, nose y, head top
    "cat": (31, 11.4, 12.4, 4.6, 29, 1, 34.5, 18.6),
    "dog": (29, 11, 12, 4.5, 27, 1, 34.5, 17),
    "rabbit": (32, 11, 11, 4.5, 30, 1, 35.5, 21),
    "fox": (30, 14, 12, 5, 27, 1, 38, 22),
    "owl": (30, 14, 13, 5.5, 28, 1.35, 38.4, 17),
    "mouse": (32, 10, 10, 4, 30, 1, 35, 22),
    "frog": (31, 14, 10, 7, 20.5, 1.1, 33, 21),
    "penguin": (30, 12, 13, 4, 29, 1, 37.5, 17),
    "lion": (31, 11, 11, 4.5, 28, 1, 34.5, 20),
    "panda": (31.6, 14.8, 11.2, 5.6, 29.6, 1, 35, 20.4),
}


def draw_animal(ctx: Canvas, f, c: float, glow, vis: str, trim: str, t: Theme) -> None:
    a = ANIMALS[f.subject - SUBJECT_START["animal"]]
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
    if a == "cat":
        for s in (-1, 1):
            _poly(ctx, [(c + s * 10.6, 23), (c + s * 10.4, 6.6), (c + s * 3, 18.4)])
        fill_out(panel)
        ctx.begin_path()
        for s in (-1, 1):
            _poly(ctx, [(c + s * 9.2, 20.4), (c + s * 9.1, 10.8), (c + s * 5.4, 18.4)])
        ctx.fill_style = trim
        ctx.fill()
    elif a == "panda":
        for s in (-1, 1):
            ctx.move_to(c + s * 11.6 + 5, 20.4)
            ctx.arc(c + s * 11.6, 20.4, 5, 0, TAU)
        fill_out(trim)
    elif a == "rabbit":
        for s in (-1, 1):
            ctx.begin_path()
            ctx.ellipse(c + s * 4.5, 12, 3, 9.5, s * .12, 0, TAU)
            fill_out(panel)
        ctx.fill_style = trim
        for s in (-1, 1):
            ctx.begin_path()
            ctx.ellipse(c + s * 4.5, 13, 1.2, 6.5, s * .12, 0, TAU)
            ctx.fill()
    elif a == "fox":
        for s in (-1, 1):
            _poly(ctx, [(c + s * 12.5, 23), (c + s * 11.5, 8.5), (c + s * 4, 17)])
        fill_out(panel)
        ctx.begin_path()
        for s in (-1, 1):
            _poly(ctx, [(c + s * 10.8, 20), (c + s * 10.6, 12), (c + s * 6.4, 17.4)])
        ctx.fill_style = trim
        ctx.fill()
    elif a == "owl":
        for s in (-1, 1):
            _poly(ctx, [(c + s * 12, 20), (c + s * 13, 10), (c + s * 6, 17.5)])
        fill_out(trim)
    elif a == "mouse":
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
    elif a == "frog":
        for s in (-1, 1):
            ctx.move_to(c + s * 7 + 4.6, 21)
            ctx.arc(c + s * 7, 21, 4.6, 0, TAU)
        fill_out(panel)
    elif a == "lion":
        pts = []
        for k in range(120):
            th = TAU * k / 120
            r = 16 + 1.6 * abs(math.cos(th * 7))
            pts.append((c + r * math.cos(th), hy + r * math.sin(th)))
        _poly(ctx, pts)
        fill_out(trim)

    # the head
    ctx.begin_path()
    if a == "fox":
        _poly(ctx, [(c - 14, 22), (c + 14, 22), (c + 9, 34), (c, 42), (c - 9, 34)])
    else:
        ctx.ellipse(c, hy, rx, ry, 0, 0, TAU)
    fill_out(trim if a == "penguin" else panel)

    # in front of the head
    if a == "dog":
        ctx.begin_path()
        for s in (-1, 1):
            ctx.begin_path()
            ctx.ellipse(c + s * 11.5, 29, 4, 9, -s * .35, 0, TAU)
            fill_out(trim)
    if a in ("dog", "lion"):
        ctx.begin_path()
        ctx.ellipse(c, 36, 5.8 if a == "dog" else 5.4, 4.4 if a == "dog" else 3.9, 0, 0, TAU)
        fill_out(panel, .5)
    if a == "owl":
        ctx.begin_path()
        for s in (-1, 1):
            ctx.move_to(c + s * 5.5 + 5.4, 28)
            ctx.arc(c + s * 5.5, 28, 5.4, 0, TAU)
        fill_out(panel, .5)
    if a == "penguin":
        ctx.begin_path()
        for s in (-1, 1):
            ctx.move_to(c + s * 4 + 6, 30)
            ctx.arc(c + s * 4, 30, 6, 0, TAU)
        ctx.move_to(c + 7, 35)
        ctx.ellipse(c, 35, 7, 6, 0, 0, TAU)
        ctx.fill_style = panel
        ctx.fill()
    if a == "panda":
        ctx.fill_style = trim
        for s in (-1, 1):
            ctx.begin_path()
            ctx.ellipse(c + s * 5.6, 29.8, 4.4, 5.2, s * .45, 0, TAU)
            ctx.fill()
    if a in ("owl", "penguin"):
        ctx.begin_path()
        _poly(ctx, [(c - 1.6, 32.5 if a == "owl" else 33), (c + 1.6, 32.5 if a == "owl" else 33), (c, 36.5 if a == "owl" else 36)])
        ctx.fill_style = trim
        ctx.fill()

    mark_color = panel if a == "penguin" else trim
    _symbol(ctx, f.decal, c, top + 3.6, 2, mark_color)
    draw_markings(ctx, f.cheek, c, ny, rx, trim)
    eye_y = ey
    for s in (-1, 1):
        draw_eye(ctx, f.vstyle, c + s * edx, eye_y, ek, -s, vis, trim, glow)
    draw_snout(ctx, f.grille, c, ny, vis, trim, panel, glow)
    if not (f.mod == 2 and a in NO_BOW_TIE):
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
    elif style == 2:  # bow tie at the neck
        _poly(ctx, [(c, 43.4), (c - 5, 40.6), (c - 5, 46.2)])
        _poly(ctx, [(c, 43.4), (c + 5, 40.6), (c + 5, 46.2)])
        ctx.fill()
        glow.off()
        ctx.line_width, ctx.stroke_style = .4, trim
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(c, 43.4, 1.2, 0, TAU)
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


# ---------------------------------------------------------------- vehicles
def _wheel(x, y, r):
    return (x, y, r)


def vehicle_spec(v: str, c: float) -> dict:
    """Shape and anchors of the vehicle named v, centered on x = c. Trails point away along `dir`."""
    L = (-1, 0)
    if v == "car":
        return dict(body=[[(c - 15, 44), (c - 15, 38), (c - 10, 37), (c - 6, 31), (c + 5, 31), (c + 10, 37), (c + 15, 38), (c + 15, 44)]],
                    wheels=[(c - 9, 44.5, 3), (c + 9, 44.5, 3)], win=(c - 5.5, 32.5, c + 4.5, 36.5), band=(c - 15, 39, c + 15, 41.5),
                    emblem=(c + 12, 41.6), top=(c, 31), trail=(c - 15, 41, L))
    if v == "bus":
        return dict(body=[[(c - 16, 45), (c - 16, 28), (c + 15, 28), (c + 16, 31), (c + 16, 45)]],
                    wheels=[(c - 10, 45.5, 2.8), (c + 10, 45.5, 2.8)], win=(c - 14, 30, c + 14, 35.5), band=(c - 16, 38, c + 16, 40.5),
                    emblem=(c + 12.5, 42.4), top=(c - 6, 28), trail=(c - 16, 43, L))
    if v == "bicycle":
        return dict(body=[[(c - 6, 43), (c - 1, 35.5), (c + 5.5, 35.5), (c + 2.5, 43)], [(c + 7, 31), (c + 13, 31), (c + 12, 36), (c + 8, 36)]],
                    wheels=[(c - 9, 44, 5), (c + 9, 44, 5)], rings=True, win=(c + 7.6, 31.6, c + 12.4, 35.4),
                    band=(c - 6, 38, c + 6, 40), emblem=(c + 1, 39.4), top=(c - 3, 34), trail=(c - 15, 44, L),
                    bars=[(c - 9, 44), (c - 3.5, 34.5), (c + 6, 33), (c + 9, 44)])
    if v == "locomotive":
        return dict(body=[[(c - 16, 45), (c - 16, 30), (c - 8, 30), (c - 8, 26), (c - 2, 26), (c - 2, 33), (c + 10, 33), (c + 16, 40), (c + 16, 45)],
                          [(c + 5, 27), (c + 8, 27), (c + 8, 33), (c + 5, 33)]],
                    wheels=[(c - 11, 45.5, 3), (c - 4, 45.5, 3), (c + 4, 45.5, 3), (c + 11, 45.5, 2.4)],
                    win=(c - 14.5, 31.5, c - 9.5, 36), band=(c - 16, 39, c + 16, 41), emblem=(c + 2, 36.5), top=(c - 12, 30),
                    trail=(c + 6.5, 26, (0, -1)))
    if v == "sailboat":
        return dict(body=[[(c - 15, 40), (c + 15, 40), (c + 11, 46), (c - 11, 46)], [(c + 1, 13), (c + 1, 38), (c + 13, 38)],
                          [(c - 1, 16), (c - 1, 38), (c - 11, 38)]],
                    wheels=[], win=(c - 9, 41.4, c + 9, 44.6), band=(c - 11, 30, c + 13, 32.4), emblem=(c + 5, 34.5),
                    top=(c, 12), trail=(c - 15, 44, L), bars=[(c, 40), (c, 12)], water=True)
    if v == "submarine":
        return dict(body=[[(c - 3, 27), (c + 5, 27), (c + 5, 33), (c - 3, 33)]], hull=(c, 38, 15, 6.5), wheels=[],
                    win=(c - 9, 36, c + 9, 39.5), band=(c - 15, 40.5, c + 15, 42.5), emblem=(c + 1, 30), top=(c + 3, 27),
                    trail=(c - 15, 38, L), bars=[(c - 1, 27), (c - 1, 22), (c + 2, 22)])
    if v == "helicopter":
        return dict(body=[[(c - 6, 34), (c - 16, 33), (c - 16, 35.5), (c - 6, 37.5)]], cabin=(c + 3, 36, 9, 6), wheels=[],
                    win=(c + 4, 32, c + 10.5, 36.5), band=(c - 6, 38, c + 12, 40), emblem=(c - 1.5, 35.6), top=(c + 9, 30.5),
                    trail=(c - 16, 38, L), bars=[(c - 12, 28), (c + 16, 28), (c + 3, 28), (c + 3, 30)], skids=True)
    if v == "hot-air balloon":
        return dict(body=[[(c - 4, 42), (c + 4, 42), (c + 4, 47), (c - 4, 47)]], envelope=(c, 22, 12, 13), wheels=[],
                    win=(c - 8, 17, c + 8, 25), band=(c - 12, 26, c + 12, 29), emblem=(c, 12.5), top=(c + 5, 10.5),
                    trail=(c, 48, (0, 1)), bars=[(c - 9, 31), (c - 4, 42), (c + 9, 31), (c + 4, 42)])
    if v == "rocket":
        return dict(body=[[(c, 6), (c + 5, 14), (c + 5, 38), (c - 5, 38), (c - 5, 14)], [(c - 5, 30), (c - 10, 40), (c - 5, 38)],
                          [(c + 5, 30), (c + 10, 40), (c + 5, 38)], [(c - 3, 38), (c + 3, 38), (c + 3, 41), (c - 3, 41)]],
                    wheels=[], win=(c - 2.5, 15, c + 2.5, 26), band=(c - 5, 28, c + 5, 30.5), emblem=(c, 33.6), top=(c + 4, 14),
                    trail=(c, 42, (0, 1)))
    return dict(body=[], saucer=(c, 34, 15, 4.5), dome=(c, 32, 7), wheels=[],  # flying saucer
                win=(c - 12, 33.6, c + 12, 35.6), band=(c - 15, 35.8, c + 15, 37.6), emblem=(c, 28.4), top=(c + 4, 26),
                trail=(c, 40, (0, 1)), bars=[(c - 8, 37.5), (c - 11, 44), (c + 8, 37.5), (c + 11, 44)])


def _vehicle_body_path(ctx: Canvas, sp) -> None:
    ctx.begin_path()
    for pts in sp["body"]:
        _poly(ctx, pts)
    if "hull" in sp:
        x, y, rx, ry = sp["hull"]
        ctx.move_to(x + rx, y)
        ctx.ellipse(x, y, rx, ry, 0, 0, TAU)
    if "fuselage" in sp:
        x, y, w, h = sp["fuselage"]
        r = h / 2
        ctx.move_to(x + r, y)
        ctx.line_to(x + w - r, y)
        ctx.arc(x + w - r, y + r, r, -math.pi / 2, math.pi / 2)
        ctx.line_to(x + r, y + h)
        ctx.arc(x + r, y + r, r, math.pi / 2, 1.5 * math.pi)
        ctx.close_path()
    if "cabin" in sp:
        x, y, rx, ry = sp["cabin"]
        ctx.move_to(x + rx, y)
        ctx.ellipse(x, y, rx, ry, 0, 0, TAU)
    if "envelope" in sp:
        x, y, rx, ry = sp["envelope"]
        ctx.move_to(x + rx, y)
        ctx.ellipse(x, y, rx, ry, 0, 0, TAU)
    if "saucer" in sp:
        x, y, r = sp["dome"]
        ctx.move_to(x - r, y)
        ctx.arc(x, y, r, math.pi, TAU)
        ctx.close_path()
        x, y, rx, ry = sp["saucer"]
        ctx.move_to(x + rx, y)
        ctx.ellipse(x, y, rx, ry, 0, 0, TAU)


def draw_vehicle(ctx: Canvas, f, c: float, glow, vis: str, trim: str, t: Theme) -> None:
    v = VEHICLES[f.subject - SUBJECT_START["vehicle"]]
    sp = vehicle_spec(v, c)
    ctx.line_join, ctx.line_cap = "round", "round"
    draw_trail(ctx, f.grille, *sp["trail"], vis, trim, glow)
    if sp.get("water"):
        ctx.begin_path()
        for k in range(9):
            x = c - 16 + k * 4
            (ctx.line_to if k else ctx.move_to)(x, 47.5 + (.7 if k % 2 else -.7))
        ctx.line_width, ctx.stroke_style = .5, trim
        ctx.stroke()
    bars = sp.get("bars")
    if bars:
        ctx.begin_path()
        if v in ("helicopter", "hot-air balloon", "flying saucer"):
            ctx.move_to(*bars[0])
            ctx.line_to(*bars[1])
            ctx.move_to(*bars[2])
            ctx.line_to(*bars[3])
        else:
            for i, p in enumerate(bars):
                (ctx.line_to if i else ctx.move_to)(*p)
        ctx.line_width, ctx.stroke_style = 1 if v == "helicopter" else .8, trim
        ctx.stroke()
    if sp.get("skids"):
        ctx.begin_path()
        ctx.move_to(c - 6, 45)
        ctx.line_to(c + 12, 45)
        ctx.move_to(c - 1, 41.5)
        ctx.line_to(c - 2, 45)
        ctx.move_to(c + 7, 41.5)
        ctx.line_to(c + 8, 45)
        ctx.line_width = .7
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(c - 16, 34.2, 2, 0, TAU)
        ctx.line_width = .5
        ctx.stroke()
    _vehicle_body_path(ctx, sp)
    ctx.fill_style = t.panel
    ctx.fill()
    glow(trim, 1)
    ctx.line_width, ctx.stroke_style = .7, trim
    ctx.stroke()
    glow.off()
    x0, y0, x1, y1 = sp["band"]
    ctx.save()
    _vehicle_body_path(ctx, sp)
    ctx.clip()
    draw_livery(ctx, f.cheek, x0, y0, x1, y1, trim)
    ctx.restore()
    draw_windows(ctx, f.vstyle, *sp["win"], vis, glow, t)
    for x, y, r in sp["wheels"]:
        ctx.begin_path()
        ctx.arc(x, y, r, 0, TAU)
        if sp.get("rings"):
            ctx.line_width, ctx.stroke_style = .8, trim
            ctx.stroke()
            ctx.begin_path()
            ctx.arc(x, y, .7, 0, TAU)
            ctx.fill_style = trim
            ctx.fill()
        else:
            ctx.fill_style = trim
            ctx.fill()
            ctx.begin_path()
            ctx.arc(x, y, r * .4, 0, TAU)
            ctx.fill_style = t.panel
            ctx.fill()
    ex, ey = sp["emblem"]
    ctx.begin_path()
    ctx.arc(ex, ey, 2.2, 0, TAU)
    ctx.fill_style = t.panel
    ctx.fill()
    ctx.line_width, ctx.stroke_style = .45, trim
    ctx.stroke()
    _symbol(ctx, f.decal, ex, ey, 1.5, trim)
    draw_vehicle_mod(ctx, f.mod, *sp["top"], vis, trim, glow)


def draw_livery(ctx: Canvas, style, x0, y0, x1, y1, trim) -> None:
    h = y1 - y0
    ctx.fill_style = ctx.stroke_style = trim
    ctx.begin_path()
    if style == 0:
        ctx.rect(x0, y0, x1 - x0, h)
        ctx.fill()
    elif style == 1:
        ctx.rect(x0, y0, x1 - x0, h * .35)
        ctx.rect(x0, y1 - h * .35, x1 - x0, h * .35)
        ctx.fill()
    elif style == 2:
        k, x = 0, x0
        while x < x1:
            ctx.rect(x, y0 + (0 if k % 2 else h / 2), h / 2, h / 2)
            x += h / 2
            k += 1
        ctx.fill()
    else:
        x, k = x0, 0
        while x <= x1 + 1:
            (ctx.line_to if k else ctx.move_to)(x, y0 + (h * .15 if k % 2 else h * .85))
            x += 1.6
            k += 1
        ctx.line_width = h * .32
        ctx.stroke()


def draw_trail(ctx: Canvas, style, x, y, d, vis, trim, glow) -> None:
    dx, dy = d
    px, py = -dy, dx

    def at(s, o=0.0):
        return x + dx * s + px * o, y + dy * s + py * o

    ctx.line_width, ctx.stroke_style, ctx.fill_style = .5, trim, trim
    ctx.begin_path()
    if style == 0:
        for s, r in ((1.6, .9), (3.6, 1.2), (5.8, 1.5)):
            cx, cy = at(s, .4 * s)
            ctx.move_to(cx + r, cy)
            ctx.arc(cx, cy, r, 0, TAU)
        ctx.global_alpha = .55
        ctx.fill()
        ctx.global_alpha = 1
    elif style == 1:
        glow(vis, 1)
        for o in (-1.4, 0, 1.4):
            _poly(ctx, [at(.2, o - .7), at(.2, o + .7), at(5.6 if o == 0 else 4, o)])
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
    elif style == 2:
        for o in (-1.6, 0, 1.6):
            ctx.move_to(*at(.8, o))
            ctx.line_to(*at(5.5 - abs(o), o))
        ctx.stroke()
    elif style == 3:
        for s, o in ((1.8, -1.2), (3.8, 1), (5.4, -.4)):
            _symbol(ctx, 4, *at(s, o), .9, vis)
    elif style == 4:
        for s, o, r in ((1.4, .6, .6), (3.2, -.6, .8), (5.2, .4, 1)):
            cx, cy = at(s, o)
            ctx.move_to(cx + r, cy)
            ctx.arc(cx, cy, r, 0, TAU)
        ctx.stroke()
    elif style == 5:
        for o in (-.8, .8):
            ctx.move_to(*at(.6, o))
            ctx.line_to(*at(6, o))
        ctx.global_alpha = .6
        ctx.line_width = .8
        ctx.stroke()
        ctx.global_alpha = 1
    elif style == 6:
        for s, o in ((1.6, .8), (3.4, -1), (5.4, .6)):
            _symbol(ctx, 9, *at(s, o), .8, vis)
    else:
        for k in range(7):
            (ctx.line_to if k else ctx.move_to)(*at(.6 + k * .85, .9 if k % 2 else -.9))
        glow(vis, .8)
        ctx.line_width, ctx.stroke_style = .6, vis
        ctx.stroke()
        glow.off()


def draw_vehicle_mod(ctx: Canvas, style, tx, ty, vis, trim, glow) -> None:
    if style in (0, 1):
        draw_roof_mod(ctx, style, tx, ty, vis, trim, glow)
        return
    ctx.begin_path()
    if style == 2:
        ctx.move_to(tx - 1.6, ty)
        ctx.arc(tx, ty, 1.6, math.pi, TAU)
        ctx.close_path()
        glow(vis, 1.4)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
        ctx.line_width, ctx.stroke_style = .4, trim
        ctx.stroke()
    else:
        _poly(ctx, [(tx - 2, ty), (tx + 1.2, ty), (tx - 1.4, ty - 4.2)])
        ctx.fill_style = trim
        ctx.fill()


# ---------------------------------------------------------------- plants
def plant_spec(p: str, c: float) -> dict:
    """Foliage (filled), stems (stroked) and bloom points of the plant named p, centered on x = c."""
    E = []
    if p == "pine":
        fol = [("poly", [(c - 10, 38), (c + 10, 38), (c, 26)]), ("poly", [(c - 8, 31), (c + 8, 31), (c, 19)]),
               ("poly", [(c - 6, 24), (c + 6, 24), (c, 12)])]
        stems = [("rect", (c - 1.2, 38, 2.4, 2))]
        blooms = [(c - 5, 35.5), (c + 4, 34), (c - 2, 28.5), (c + 3, 22.5), (c - 1, 17)]
    elif p == "oak":
        fol = [("circle", (c, 21, 8.5)), ("circle", (c - 6.5, 26, 6)), ("circle", (c + 6.5, 26, 6))]
        stems = [("rect", (c - 1.5, 30, 3, 10))]
        blooms = [(c - 4.5, 18.5), (c + 4, 17.5), (c, 25), (c + 8, 26), (c - 8, 26.5)]
    elif p == "palm":
        fol = [("ellipse", (c + 2 + 6 * math.cos(a), 17 + 4 * math.sin(a), 7, 1.8, a)) for a in (-2.8, -2.0, -1.2, -.4, .4)]
        stems = [("curve", [(c - 1, 40), (c - 2, 30), (c + 2, 17)], 2)]
        blooms = [(c + .6, 19.6), (c + 3.4, 19.6), (c + 2, 21.6)]
    elif p == "cactus":
        fol = [("rr", (c - 3, 14, 6, 26, 3)), ("rr", (c - 9, 21, 3, 9, 1.5)), ("rr", (c - 9, 27.5, 7, 3, 1.5)),
               ("rr", (c + 6, 17, 3, 11, 1.5)), ("rr", (c + 2, 25.5, 7, 3, 1.5))]
        stems = []
        blooms = [(c, 14), (c - 7.5, 21), (c + 7.5, 17), (c, 24.5), (c, 33)]
    elif p == "sunflower":
        fol = [("ellipse", (c + 5.2 * math.cos(a), 16 + 5.2 * math.sin(a), 2.6, 1.1, a)) for a in [k * math.pi / 6 for k in range(12)]]
        fol += [("ellipse", (c - 3.4, 32, 1.8, 5, .6)), ("ellipse", (c + 3.4, 29, 1.8, 5, -.6))]
        stems = [("line", [(c, 40), (c, 20)], .9)]
        blooms = [(c, 16), (c - 1.2, 15), (c + 1.2, 17)]
        E = [("center", (c, 16, 3))]
    elif p == "bonsai":
        fol = [("ellipse", (c - 6, 24, 6, 3, 0)), ("ellipse", (c + 5, 18, 7, 3.5, 0)), ("ellipse", (c + 1, 30, 5, 2.5, 0))]
        stems = [("curve", [(c, 40), (c - 4, 33), (c + 3, 26), (c - 2, 20), (c + 4, 18)], 1.8)]
        blooms = [(c - 8, 23.5), (c - 4, 23), (c + 3, 17), (c + 8, 18), (c + 2, 29.5)]
    elif p == "fern":
        fol = [("ellipse", (c + 10 * math.sin(a), 40 - 13 * math.cos(a) - 2, 2.6, 9, a)) for a in (-1.1, -.55, 0, .55, 1.1)]
        stems = []
        blooms = [(c - 9, 33), (c - 5, 26), (c, 25), (c + 5, 26), (c + 9, 33)]
    elif p == "bamboo":
        fol = [("rect", (c - 6, 12, 2.6, 28)), ("rect", (c - 1.3, 8, 2.6, 32)), ("rect", (c + 4, 15, 2.6, 25)),
               ("ellipse", (c - 8, 16, 3, 1, -.5)), ("ellipse", (c + 3, 11, 3, 1, -.5)), ("ellipse", (c + 8.5, 19, 3, 1, .5))]
        stems = []
        blooms = [(c - 4.7, 20), (c, 14), (c + 5.3, 24), (c, 30), (c - 4.7, 34)]
        E = [("nodes", [(c - 6, 2.6, (20, 28, 35)), (c - 1.3, 2.6, (16, 24, 32)), (c + 4, 2.6, (22, 30, 36))])]
    elif p == "cherry blossom":
        fol = [("circle", (c + x, y, r)) for x, y, r in ((-10, 20, 4), (-5, 15, 4.5), (2, 13, 4.5), (8, 17, 4), (11, 23, 3.5), (-11, 26, 3))]
        stems = [("curve", [(c, 40), (c, 30), (c - 9, 22)], 1.4), ("curve", [(c, 30), (c + 2, 22), (c + 10, 21)], 1.1),
                 ("curve", [(c + 1, 24), (c - 3, 16)], .9)]
        blooms = [(c - 10, 19), (c - 5, 14), (c + 2, 12), (c + 8, 16), (c + 11, 22)]
    else:  # lotus
        fol = [("ellipse", (c - 8, 38, 6, 1.8, 0)), ("ellipse", (c + 8, 38.5, 6, 1.8, 0))]
        fol += [("ellipse", (c + 5 * math.sin(a), 30 - 4 * math.cos(a), 1.8, 4.6, a)) for a in (-1.3, -.65, 0, .65, 1.3)]
        stems = []
        blooms = [(c, 26), (c - 4, 28), (c + 4, 28), (c - 8, 36), (c + 8, 36)]
    return dict(fol=fol, stems=stems, blooms=blooms, extra=E)


def _shape(ctx: Canvas, kind, a) -> None:
    if kind == "poly":
        _poly(ctx, a)
    elif kind == "multi":  # several polygons in one path (a reversed inner one cuts a hole)
        for pts in a:
            _poly(ctx, pts)
    elif kind == "circle":
        x, y, r = a
        ctx.move_to(x + r, y)
        ctx.arc(x, y, r, 0, TAU)
    elif kind == "ellipse":
        x, y, rx, ry, rot = a
        ctx.move_to(x + rx * math.cos(rot), y + rx * math.sin(rot))
        ctx.ellipse(x, y, rx, ry, rot, 0, TAU)
    elif kind == "rect":
        ctx.rect(*a)
    elif kind == "rr":
        x, y, w, h, r = a
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
    elif kind == "halfellipse":
        x, y, rx, ry = a
        ctx.move_to(x - rx, y)
        ctx.ellipse(x, y, rx, ry, 0, math.pi, TAU)
        ctx.close_path()
    elif kind == "lowerellipse":
        x, y, rx, ry = a
        ctx.move_to(x + rx, y)
        ctx.ellipse(x, y, rx, ry, 0, 0, math.pi)
        ctx.close_path()


def draw_plant(ctx: Canvas, f, c: float, glow, vis: str, trim: str, t: Theme) -> None:
    sp = plant_spec(PLANTS[f.subject - SUBJECT_START["plant"]], c)
    ctx.line_join, ctx.line_cap = "round", "round"
    draw_ground_extras(ctx, f.cheek, c, vis, trim)
    for st in sp["stems"]:
        kind, a = st[0], st[1]
        ctx.begin_path()
        if kind in ("rect", "rr"):
            _shape(ctx, kind, a)
            ctx.fill_style = trim
            ctx.fill()
            continue
        if kind == "curve" and len(a) == 3:
            ctx.move_to(*a[0])
            ctx.quadratic_curve_to(*a[1], *a[2])
        else:
            for i, pt in enumerate(a):
                (ctx.line_to if i else ctx.move_to)(*pt)
        ctx.line_width, ctx.stroke_style = st[2], trim
        ctx.stroke()
    ctx.begin_path()
    for kind, a in sp["fol"]:
        _shape(ctx, kind, a)
    glow(trim, 1)
    ctx.fill_style = trim
    ctx.fill()
    glow.off()
    for kind, a in sp["extra"]:
        if kind == "center":
            x, y, r = a
            ctx.begin_path()
            ctx.arc(x, y, r, 0, TAU)
            ctx.fill_style = t.panel
            ctx.fill()
            ctx.line_width, ctx.stroke_style = .5, trim
            ctx.stroke()
        elif kind == "nodes":
            ctx.begin_path()
            for x, w, ys in a:
                for y in ys:
                    ctx.move_to(x, y)
                    ctx.line_to(x + w, y)
            ctx.line_width, ctx.stroke_style = .5, t.panel
            ctx.stroke()
    for x, y in sp["blooms"]:
        draw_bloom(ctx, f.vstyle, x, y, vis, trim, glow)
    draw_pot(ctx, f.grille, c, f.decal, trim, t)
    draw_visitor(ctx, f.mod, c + 11, 12, vis, trim, glow)


def draw_bloom(ctx: Canvas, style, x, y, vis, trim, glow) -> None:
    glow(vis, .8)
    ctx.fill_style = vis
    ctx.begin_path()
    if style == 0:
        ctx.arc(x, y, .9, 0, TAU)
        ctx.fill()
    elif style == 1:
        for k in range(5):
            a = -math.pi / 2 + k * TAU / 5
            ctx.move_to(x + .8 * math.cos(a) + .65, y + .8 * math.sin(a))
            ctx.arc(x + .8 * math.cos(a), y + .8 * math.sin(a), .65, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.arc(x, y, .4, 0, TAU)
        ctx.fill_style = trim
        ctx.fill()
    elif style in (2, 3, 6):
        _symbol(ctx, {2: 4, 3: 7, 6: 9}[style], x, y, 1.3 if style != 3 else 1.15, vis)
    elif style == 4:
        ctx.arc(x, y + .2, 1.15, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.move_to(x, y - .9)
        ctx.line_to(x + .7, y - 1.6)
        ctx.line_width, ctx.stroke_style = .35, trim
        ctx.stroke()
    elif style == 5:
        ctx.ellipse(x, y, 1.4, .9, .3, 0, TAU)
        ctx.fill()
    else:
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(math.pi)
        _symbol(ctx, 10, 0, 0, 1.2, vis)
        ctx.restore()
    glow.off()


def draw_pot(ctx: Canvas, style, c, decal, trim, t: Theme) -> None:
    ctx.begin_path()
    lx, ly = c, 45.2
    if style == 0:
        _poly(ctx, [(c - 6, 42), (c + 6, 42), (c + 4.6, 50), (c - 4.6, 50)])
        ctx.rect(c - 6.8, 40, 13.6, 2.2)
    elif style == 1:
        ctx.rect(c - 6.5, 40.5, 13, 9.5)
    elif style == 2:
        ctx.move_to(c - 7.5, 41)
        ctx.ellipse(c, 41, 7.5, 9, 0, 0, math.pi)
        ctx.close_path()
        ly = 44.5
    elif style == 3:
        _poly(ctx, [(c - 3, 40), (c + 3, 40), (c + 2, 42), (c + 4.5, 46), (c + 3, 50), (c - 3, 50), (c - 4.5, 46), (c - 2, 42)])
        ly = 46
    elif style == 4:
        ctx.rect(c - 7, 41, 14, 9)
    elif style == 5:
        ctx.move_to(c - 10, 50)
        ctx.ellipse(c, 50, 10, 5, 0, math.pi, TAU)
        ctx.close_path()
        ly = 47.2
    elif style == 6:
        ctx.rect(c - 6, 40.5, 12, 9.5)
    else:
        ctx.move_to(c - 7, 41)
        ctx.ellipse(c, 41, 7, 7.5, 0, 0, math.pi)
        ctx.close_path()
        ly = 44.2
    ctx.fill_style = t.panel
    ctx.fill()
    ctx.line_width, ctx.stroke_style = .7, trim
    ctx.stroke()
    ctx.begin_path()
    if style == 4:
        for y in (44, 47):
            ctx.move_to(c - 7, y)
            ctx.line_to(c + 7, y)
        ctx.line_width = .45
        ctx.stroke()
    elif style == 6:
        ctx.rect(c - 6.6, 39.2, 13.2, 1.4)
        ctx.fill_style = trim
        ctx.fill()
    elif style == 7:
        ctx.move_to(c + 7, 42.5)
        ctx.arc(c + 7.6, 44, 1.6, -math.pi / 2, math.pi / 2)
        ctx.line_width = .7
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(c - 9, 49.6)
        ctx.line_to(c + 9, 49.6)
        ctx.stroke()
    elif style == 1:
        ctx.move_to(c - 6.5, 42.5)
        ctx.line_to(c + 6.5, 42.5)
        ctx.line_width = .45
        ctx.stroke()
    _symbol(ctx, decal, lx, ly, 1.7, trim)


def draw_visitor(ctx: Canvas, style, x, y, vis, trim, glow) -> None:
    glow(vis, .8)
    ctx.fill_style = vis
    ctx.begin_path()
    if style == 0:
        for s in (-1, 1):
            ctx.move_to(x + s * 1.8 + 1.6, y - 1)
            ctx.ellipse(x + s * 1.8, y - 1, 1.6, 1.9, s * .5, 0, TAU)
            ctx.move_to(x + s * 1.4 + 1.1, y + 1.4)
            ctx.ellipse(x + s * 1.4, y + 1.4, 1.1, 1.2, -s * .5, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.move_to(x, y - 2)
        ctx.line_to(x, y + 2.4)
        ctx.line_width, ctx.stroke_style = .55, trim
        ctx.stroke()
    elif style == 1:
        ctx.ellipse(x, y, 2.2, 1.5, 0, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        for dx in (-.6, .6):
            ctx.move_to(x + dx, y - 1.4)
            ctx.line_to(x + dx, y + 1.4)
        ctx.line_width, ctx.stroke_style = .45, trim
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(x + 1.2, y - 1.3)
        ctx.ellipse(x - .2, y - 2.1, 1.4, .8, -.3, 0, TAU)
        ctx.global_alpha = .6
        ctx.fill_style = trim
        ctx.fill()
        ctx.global_alpha = 1
    elif style == 2:
        ctx.ellipse(x, y, 2.4, 1.6, 0, 0, TAU)
        ctx.move_to(x + 3.4, y - 1.6)
        ctx.arc(x + 2.2, y - 1.6, 1.2, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        _poly(ctx, [(x + 3.3, y - 1.9), (x + 4.6, y - 1.5), (x + 3.3, y - 1.1)])
        ctx.fill_style = trim
        ctx.fill()
        ctx.begin_path()
        _poly(ctx, [(x - 1.4, y - .4), (x + .8, y - .4), (x - .6, y - 2.6)])
        ctx.fill()
    else:
        ctx.arc(x, y, 1.9, 0, TAU)
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.move_to(x, y - 1.9)
        ctx.line_to(x, y + 1.9)
        ctx.line_width, ctx.stroke_style = .4, trim
        ctx.stroke()
        ctx.begin_path()
        for dx, dy in ((-.9, -.5), (.9, -.5), (-.8, .9), (.8, .9)):
            ctx.move_to(x + dx + .35, y + dy)
            ctx.arc(x + dx, y + dy, .35, 0, TAU)
        ctx.move_to(x + 1.2, y - 2.2)
        ctx.arc(x, y - 2.2, 1.2, 0, TAU)
        ctx.fill_style = trim
        ctx.fill()
    glow.off()


def draw_ground_extras(ctx: Canvas, style, c, vis, trim) -> None:
    ctx.line_width, ctx.stroke_style, ctx.fill_style = .5, trim, trim
    ctx.begin_path()
    ctx.move_to(c - 16, 50)
    ctx.line_to(c + 16, 50)
    ctx.stroke()
    ctx.begin_path()
    if style == 0:
        for s in (-1, 1):
            for x in (11, 13.5, 16):
                ctx.move_to(c + s * x, 50)
                ctx.line_to(c + s * (x - .8), 46.8)
                ctx.move_to(c + s * x, 50)
                ctx.line_to(c + s * (x + .8), 47.4)
        ctx.stroke()
    elif style == 1:
        for s in (-1, 1):
            for x, rx in ((10.5, 1.3), (13, 1), (15.2, 1.4)):
                ctx.move_to(c + s * x + rx, 49.2)
                ctx.ellipse(c + s * x, 49.2, rx, .8, 0, 0, TAU)
        ctx.fill()
    elif style == 2:
        for s in (-1, 1):
            for x, a in ((10.5, .4), (12.8, -.5), (15, .2)):
                ctx.move_to(c + s * x + 1, 49.3)
                ctx.ellipse(c + s * x, 49.3, 1, .55, a, 0, TAU)
        ctx.fill_style = vis
        ctx.fill()
    else:
        for s in (-1, 1):
            for x in (11.5, 15):
                ctx.move_to(c + s * x, 50)
                ctx.line_to(c + s * x, 47)
                ctx.move_to(c + s * x + 1.1, 46.6)
                ctx.ellipse(c + s * x + .6, 46.6, .7, .4, -.5, 0, TAU)
                ctx.move_to(c + s * x - .1, 46.6)
                ctx.ellipse(c + s * x - .6, 46.6, .7, .4, .5, 0, TAU)
        ctx.stroke()
        ctx.fill()


# ---------- furniture ----------

def furniture_spec(name: str, c: float) -> dict:
    """Parts of the furniture named `name`, standing on the floor at y = 46, centered near x = c.

    body    (shape, args, fabric) drawn in order: panel fill, fabric pattern if flagged, trim outline
    lines   (points, width) stroked in trim: legs, poles, frames
    solid   shapes filled in trim: books, keys, feet
    emblem  plaque center; wall: wall item center; obj: base point of the companion object
    """
    lines, solid = [], []
    if name == "armchair":
        a = c - 3
        body = [("rr", (a - 9, 20, 18, 16, 3), True), ("rr", (a - 12, 28, 5, 13, 2), False),
                ("rr", (a + 7, 28, 5, 13, 2), False), ("rr", (a - 7, 34, 14, 6, 1.5), False)]
        lines = [([(a - 10, 41), (a - 10, 46)], 1.2), ([(a + 10, 41), (a + 10, 46)], 1.2)]
        emblem, wall, obj = (a, 26), (a, 12), (c + 12.5, 46)
    elif name == "sofa":
        body = [("rr", (c - 14, 24, 28, 12, 3), True), ("rr", (c - 17, 30, 6, 12, 2.5), False),
                ("rr", (c + 11, 30, 6, 12, 2.5), False), ("rr", (c - 11, 35, 11, 6, 1.5), False),
                ("rr", (c, 35, 11, 6, 1.5), False)]
        lines = [([(c - 14, 42), (c - 14, 46)], 1.2), ([(c + 14, 42), (c + 14, 46)], 1.2)]
        emblem, wall, obj = (c - 5.5, 29.5), (c, 14), (c + 5.5, 35)
    elif name == "bed":
        body = [("rr", (c - 17, 22, 5, 24, 2), False), ("rect", (c - 12, 34, 24, 6), False),
                ("ellipse", (c - 8, 32.6, 3.6, 2, 0), False), ("poly", [(c - 4, 31.5), (c + 12, 31.5), (c + 12, 40), (c - 4, 40)], True),
                ("rr", (c + 12, 30, 5, 16, 2), False)]
        lines = [([(c - 12, 41), (c + 12, 41)], 1.4)]
        emblem, wall, obj = (c + 3, 36.5), (c, 14), (c + 8.5, 31.5)
    elif name == "bookshelf":
        body = [("rect", (c - 8, 10, 16, 36), False), ("rect", (c - 6.6, 37.5, 13.2, 7.5), True)]
        lines = [([(c - 8, 19), (c + 8, 19)], .7), ([(c - 8, 28), (c + 8, 28)], .7), ([(c - 8, 37), (c + 8, 37)], .7),
                 ([(c, 37.5), (c, 45)], .5)]
        for y0, books in ((19, ((-6.6, 1.6, 7), (-4.6, 1.2, 6), (-3, 1.8, 7.5), (1.5, 1.4, 6.5), (3.4, 1.6, 7.5))),
                          (28, ((-6.6, 1.4, 6.5), (-4.8, 1.8, 7.5), (-2.6, 1.2, 6), (-.2, 1.6, 7), (2, 1.4, 6.5), (4.6, 1.8, 7.5))),
                          (37, ((-6.6, 1.8, 7.5), (-4.4, 1.4, 6.5)))):
            solid += [("rect", (c + x, y0 - h, w, h)) for x, w, h in books]
        solid.append(("poly", [(c - 2.6, 37), (c - 1.2, 37), (c + 1.8, 31), (c + .6, 30.4)]))
        emblem, wall, obj = (c, 41.2), (c - 13, 17), (c + 13, 46)
    elif name == "grandfather clock":
        body = [("rect", (c - 6, 38, 12, 8), True), ("rect", (c - 4.5, 21, 9, 17), False),
                ("rr", (c - 6, 7, 12, 14.5, 4), False), ("circle", (c, 14, 4), False), ("rr", (c - 2.6, 23, 5.2, 13, 1.4), False)]
        lines = [([(c, 14), (c, 11)], .6), ([(c, 14), (c + 2.2, 15.2)], .6), ([(c, 23.5), (c, 32)], .6)]
        solid = [("circle", (c, 32.6, 1.6))]
        emblem, wall, obj = (c, 42), (c - 12.5, 16), (c + 12.5, 46)
    elif name == "floor lamp":
        L = c - 7
        body = [("poly", [(L - 7, 22), (L + 7, 22), (L + 4, 11), (L - 4, 11)], True), ("rect", (c + 3, 35.5, 12, 10.5), False)]
        lines = [([(L, 22), (L, 44.5)], 1.2)]
        solid = [("ellipse", (L, 45, 5, 1.4, 0)), ("rect", (c + 2, 33.6, 14, 1.9))]
        emblem, wall, obj = (c + 9, 40.6), (c + 9, 15), (c + 9, 33.6)
    elif name == "piano":
        P = c - 3
        body = [("rect", (P - 12, 20, 24, 26), False), ("rect", (P - 10, 22.2, 20, 7.6), True), ("rect", (P - 13.5, 31, 27, 3.6), False),
                ("rr", (c + 10, 37, 7, 2.2, 1), False)]
        solid = [("rect", (P - 13.5, 18.4, 27, 2.2))] + [("rect", (P - 11.6 + k * 3.2, 31, 1.4, 2)) for k in range(8)]
        lines = [([(c + 11.5, 39.2), (c + 11.5, 46)], .9), ([(c + 15.5, 39.2), (c + 15.5, 46)], .9)]
        emblem, wall, obj = (P, 40), (P + 6, 11), (P - 6.5, 18.4)
    else:  # bathtub
        body = [("poly", [(c - 15, 30), (c + 15, 30), (c + 13.5, 37), (c + 9, 41.5), (c - 9, 41.5), (c - 13.5, 37)], True),
                ("rr", (c - 16.5, 28.4, 33, 2.6, 1.2), False)]
        lines = [([(c - 12.5, 28.4), (c - 12.5, 22), (c - 8.6, 22), (c - 8.6, 24.2)], 1)]
        solid = [("ellipse", (c - 9.5, 43.6, 1.6, 2.4, -.3)), ("ellipse", (c + 9.5, 43.6, 1.6, 2.4, .3))]
        emblem, wall, obj = (c, 35.4), (c, 12), (c + 10.5, 28.4)
    return dict(body=body, lines=lines, solid=solid, emblem=emblem, wall=wall, obj=obj)


def _bbox(kind, a):
    if kind in ("poly", "multi"):
        pts = a if kind == "poly" else [p for ring in a for p in ring]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)
    if kind == "circle":
        return a[0] - a[2], a[1] - a[2], a[0] + a[2], a[1] + a[2]
    if kind == "ellipse":
        r = max(a[2], a[3])
        return a[0] - r, a[1] - r, a[0] + r, a[1] + r
    if kind == "halfellipse":
        return a[0] - a[2], a[1] - a[3], a[0] + a[2], a[1]
    if kind == "lowerellipse":
        return a[0] - a[2], a[1], a[0] + a[2], a[1] + a[3]
    return a[0], a[1], a[0] + a[2], a[1] + a[3]


def _strokes(ctx: Canvas, lines, trim) -> None:
    for pts, w in lines:
        ctx.begin_path()
        for i, p in enumerate(pts):
            (ctx.line_to if i else ctx.move_to)(*p)
        ctx.line_width, ctx.stroke_style = w, trim
        ctx.stroke()


def _draw_parts(ctx: Canvas, sp, pattern, style, decal, glow, vis, trim, t: Theme) -> None:
    """Shared by furniture and food: back lines, body parts (pattern-filled when flagged), solid
    parts, front lines, then the symbol plaque."""
    _strokes(ctx, sp["lines"], trim)
    for kind, a, fab in sp["body"]:
        ctx.begin_path()
        _shape(ctx, kind, a)
        ctx.fill_style = t.panel
        ctx.fill()
        if fab:
            ctx.save()
            ctx.clip()
            pattern(ctx, style, *_bbox(kind, a), vis)
            ctx.restore()
            ctx.begin_path()
            _shape(ctx, kind, a)
        glow(trim, 1)
        ctx.line_width, ctx.stroke_style = .7, trim
        ctx.stroke()
        glow.off()
    ctx.begin_path()
    for kind, a in sp["solid"]:
        _shape(ctx, kind, a)
    ctx.fill_style = trim
    ctx.fill()
    _strokes(ctx, sp.get("front", ()), trim)
    ex, ey = sp["emblem"]
    ctx.begin_path()
    ctx.arc(ex, ey, 2.2, 0, TAU)
    ctx.fill_style = t.panel
    ctx.fill()
    ctx.line_width, ctx.stroke_style = .45, trim
    ctx.stroke()
    _symbol(ctx, decal, ex, ey, 1.5, trim)


def draw_furniture(ctx: Canvas, f, c: float, glow, vis: str, trim: str, t: Theme) -> None:
    sp = furniture_spec(FURNITURE[f.subject - SUBJECT_START["furniture"]], c)
    ctx.line_join, ctx.line_cap = "round", "round"
    draw_floor(ctx, f.cheek, c, vis, trim)
    _draw_parts(ctx, sp, draw_fabric, f.vstyle, f.decal, glow, vis, trim, t)
    draw_wall_item(ctx, f.mod, *sp["wall"], vis, trim, glow, t)
    draw_companion(ctx, f.grille, *sp["obj"], vis, trim, glow, t)


def draw_fabric(ctx: Canvas, style, x0, y0, x1, y1, vis) -> None:
    ctx.fill_style, ctx.stroke_style = vis, vis
    ctx.begin_path()
    if style == 0:  # stripes
        x = x0 + .6
        while x < x1:
            ctx.rect(x, y0, 1.1, y1 - y0)
            x += 2.6
        ctx.fill()
    elif style == 1:  # bands
        y = y0 + 1
        while y < y1:
            ctx.rect(x0, y, x1 - x0, 1.2)
            y += 3
        ctx.fill()
    elif style == 2:  # polka dots
        row, y = 0, y0 + 1.4
        while y < y1 + 1:
            x = x0 + (1.4 if row % 2 else 0)
            while x < x1 + 1:
                ctx.move_to(x + .75, y)
                ctx.arc(x, y, .75, 0, TAU)
                x += 2.8
            row, y = row + 1, y + 2.4
        ctx.fill()
    elif style == 3:  # checks
        row, y = 0, y0
        while y < y1:
            x = x0 + (1.8 if row % 2 else 0)
            while x < x1:
                ctx.rect(x, y, 1.8, 1.8)
                x += 3.6
            row, y = row + 1, y + 1.8
        ctx.fill()
    elif style == 4:  # diamonds
        row, y = 0, y0 + 1.6
        while y < y1 + 1.6:
            x = x0 + (1.6 if row % 2 else 0)
            while x < x1 + 1.6:
                _poly(ctx, [(x, y - 1.5), (x + 1.1, y), (x, y + 1.5), (x - 1.1, y)])
                x += 3.2
            row, y = row + 1, y + 3
        ctx.fill()
    elif style == 5:  # zigzag
        y = y0 + 1.4
        while y < y1 + 1:
            x, k = x0 - 1, 0
            while x < x1 + 1.6:
                (ctx.line_to if k else ctx.move_to)(x, y + (.8 if k % 2 else -.8))
                x, k = x + 1.6, k + 1
            y += 3
        ctx.line_width = .7
        ctx.stroke()
    elif style == 6:  # plaid
        y = y0 + 1.2
        while y < y1:
            ctx.rect(x0, y, x1 - x0, .9)
            y += 3.4
        x = x0 + 1.2
        while x < x1:
            ctx.rect(x, y0, .9, y1 - y0)
            x += 3.4
        ctx.global_alpha = .75
        ctx.fill()
        ctx.global_alpha = 1
    else:  # scales
        row, y = 0, y0 + 1.6
        while y < y1 + 1.6:
            x = x0 + (1.4 if row % 2 else 0)
            while x < x1 + 1.4:
                ctx.move_to(x - 1.4, y)
                ctx.arc(x, y, 1.4, math.pi, TAU, True)
                x += 2.8
            row, y = row + 1, y + 1.8
        ctx.line_width = .5
        ctx.stroke()


def draw_floor(ctx: Canvas, style, c, vis, trim) -> None:
    ctx.line_width, ctx.stroke_style, ctx.fill_style = .5, trim, trim
    ctx.begin_path()
    ctx.move_to(c - 17, 50)
    ctx.line_to(c + 17, 50)
    ctx.stroke()
    ctx.begin_path()
    if style == 0:  # oval rug
        ctx.move_to(c + 14, 47.8)
        ctx.ellipse(c, 47.8, 14, 1.9, 0, 0, TAU)
        ctx.fill_style = vis
        ctx.global_alpha = .55
        ctx.fill()
        ctx.global_alpha = 1
        ctx.begin_path()
        ctx.move_to(c + 11, 47.8)
        ctx.ellipse(c, 47.8, 11, 1.1, 0, 0, TAU)
        ctx.line_width = .4
        ctx.stroke()
    elif style == 1:  # floorboards
        for y in (46.8, 48.4):
            ctx.move_to(c - 17, y)
            ctx.line_to(c + 17, y)
        for x, y in ((-12, 46.8), (-3, 46.8), (7, 46.8), (14, 46.8), (-15, 48.4), (-7, 48.4), (2, 48.4), (11, 48.4)):
            ctx.move_to(c + x, y)
            ctx.line_to(c + x, y + 1.6)
        ctx.line_width = .4
        ctx.stroke()
    elif style == 2:  # checker tiles
        for k in range(17):
            ctx.rect(c - 17 + k * 2, 46 + (k % 2) * 2, 2, 2)
        ctx.global_alpha = .6
        ctx.fill()
        ctx.global_alpha = 1
    else:  # fringed rug
        ctx.rect(c - 12, 46.6, 24, 2.6)
        ctx.fill_style = vis
        ctx.global_alpha = .55
        ctx.fill()
        ctx.global_alpha = 1
        ctx.begin_path()
        for s in (-1, 1):
            for k in range(4):
                y = 46.9 + k * .7
                ctx.move_to(c + s * 12, y)
                ctx.line_to(c + s * 13.6, y)
        ctx.line_width = .35
        ctx.stroke()


def draw_wall_item(ctx: Canvas, style, x, y, vis, trim, glow, t: Theme) -> None:
    ctx.line_width, ctx.stroke_style = .6, trim
    ctx.begin_path()
    if style == 0:  # picture frame with a landscape
        ctx.rect(x - 3.6, y - 2.8, 7.2, 5.6)
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.stroke()
        ctx.begin_path()
        _poly(ctx, [(x - 2.8, y + 2), (x - .8, y - 1.2), (x + .4, y + .4), (x + 1.4, y - .6), (x + 2.8, y + 2)])
        ctx.fill_style = vis
        ctx.fill()
    elif style == 1:  # round mirror
        ctx.arc(x, y, 3.2, 0, TAU)
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.line_width = .8
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(x - 1.6, y + .2)
        ctx.line_to(x - .2, y - 1.4)
        ctx.move_to(x - .6, y + 1.2)
        ctx.line_to(x + 1.2, y - .6)
        glow(vis, .8)
        ctx.line_width, ctx.stroke_style = .5, vis
        ctx.stroke()
        glow.off()
    elif style == 2:  # window
        ctx.rect(x - 3, y - 3, 6, 6)
        glow(vis, .8)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(x, y - 3)
        ctx.line_to(x, y + 3)
        ctx.move_to(x - 3, y)
        ctx.line_to(x + 3, y)
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(x - 3.8, y + 3.4)
        ctx.line_to(x + 3.8, y + 3.4)
        ctx.line_width = .8
        ctx.stroke()
    else:  # bunting
        ctx.move_to(x - 6, y - 2)
        ctx.quadratic_curve_to(x, y + 1, x + 6, y - 2)
        ctx.line_width = .4
        ctx.stroke()
        for k, dx in enumerate((-4.2, -1.4, 1.4, 4.2)):
            yy = y - 2 + 3 * (1 - (dx / 6) ** 2) / 2
            ctx.begin_path()
            _poly(ctx, [(x + dx - 1.1, yy), (x + dx + 1.1, yy), (x + dx, yy + 2.6)])
            ctx.fill_style = vis if k % 2 == 0 else trim
            ctx.fill()


def draw_companion(ctx: Canvas, style, x, y, vis, trim, glow, t: Theme) -> None:
    ctx.fill_style, ctx.stroke_style, ctx.line_width = trim, trim, .6
    ctx.begin_path()
    if style == 0:  # cat
        ctx.move_to(x + 2.8, y - 2)
        ctx.ellipse(x, y - 2, 2.8, 2, 0, 0, TAU)
        ctx.move_to(x + 3.8, y - 4.8)
        ctx.arc(x + 2, y - 4.8, 1.8, 0, TAU)
        _poly(ctx, [(x + .5, y - 5.6), (x + .7, y - 7.6), (x + 1.9, y - 6.4)])
        _poly(ctx, [(x + 2.3, y - 6.5), (x + 3.4, y - 7.6), (x + 3.6, y - 5.6)])
        ctx.fill()
        ctx.begin_path()
        ctx.move_to(x - 2.6, y - 1)
        ctx.quadratic_curve_to(x - 4.4, y - 2, x - 3.6, y - 4.4)
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(x + 2.2, y - 4.8)
        ctx.arc(x + 1.6, y - 4.8, .45, 0, TAU)
        ctx.fill_style = vis
        ctx.fill()
    elif style == 1:  # book stack
        for k, (dx, w) in enumerate(((-3, 6), (-2.6, 5.2), (-3.2, 5.8))):
            ctx.begin_path()
            ctx.rect(x + dx, y - 1.7 * (k + 1), w, 1.6)
            ctx.fill_style = vis if k % 2 else trim
            ctx.fill()
    elif style == 2:  # potted plant
        _poly(ctx, [(x - 2, y - 3.4), (x + 2, y - 3.4), (x + 1.4, y), (x - 1.4, y)])
        ctx.fill()
        ctx.begin_path()
        for dx, a in ((-1.4, -.5), (0, 0), (1.4, .5)):
            ctx.move_to(x + dx + .9 * math.cos(a), y - 5.6 + .9 * math.sin(a))
            ctx.ellipse(x + dx, y - 5.6, .9, 2, a, 0, TAU)
        glow(vis, .8)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
    elif style == 3:  # teapot
        ctx.move_to(x + 2.8, y - 2.4)
        ctx.ellipse(x, y - 2.4, 2.8, 2.4, 0, 0, TAU)
        _poly(ctx, [(x + 2, y - 2.6), (x + 4.4, y - 4.6), (x + 4.6, y - 4), (x + 2.4, y - 1.2)])
        ctx.move_to(x + .9, y - 5)
        ctx.arc(x, y - 5, .9, 0, TAU)
        ctx.fill()
        ctx.begin_path()
        ctx.arc(x - 3, y - 2.6, 1.3, math.pi * .5, math.pi * 1.5)
        ctx.stroke()
        ctx.begin_path()
        ctx.rect(x - 2.6, y - 2.8, 5.2, .8)
        ctx.fill_style = vis
        ctx.fill()
    elif style == 4:  # radio
        ctx.move_to(x - 2, y - 4.6)
        ctx.line_to(x + .6, y - 8)
        ctx.stroke()
        ctx.begin_path()
        _shape(ctx, "rr", (x - 3.6, y - 4.8, 7.2, 4.8, 1))
        ctx.fill()
        ctx.begin_path()
        ctx.arc(x - 1.2, y - 2.4, 1.4, 0, TAU)
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.begin_path()
        ctx.rect(x + 1, y - 3.6, 1.8, .8)
        ctx.rect(x + 1, y - 2, 1.8, .8)
        ctx.fill_style = vis
        ctx.fill()
    elif style == 5:  # globe
        ctx.move_to(x - 2.4, y)
        ctx.line_to(x + 2.4, y)
        ctx.move_to(x, y)
        ctx.line_to(x, y - 1.6)
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(x, y - 5, 3.3, math.pi * .6, math.pi * 1.6)
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(x, y - 5, 2.6, 0, TAU)
        glow(vis, .8)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
        ctx.begin_path()
        ctx.move_to(x - 2.6, y - 5)
        ctx.line_to(x + 2.6, y - 5)
        ctx.move_to(x + 1.1, y - 5)
        ctx.ellipse(x, y - 5, 1.1, 2.6, 0, 0, TAU)
        ctx.line_width = .4
        ctx.stroke()
    elif style == 6:  # candle
        ctx.move_to(x + 2.6, y - .5)
        ctx.ellipse(x, y - .5, 2.6, .7, 0, 0, TAU)
        ctx.fill()
        ctx.begin_path()
        ctx.rect(x - 1, y - 5.6, 2, 5)
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.line_width = .5
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(x + .9, y - 7.2)
        ctx.ellipse(x, y - 7.2, .9, 1.5, 0, 0, TAU)
        glow(vis, 1.4)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
    else:  # gift box
        ctx.rect(x - 3, y - 5, 6, 5)
        ctx.fill_style = vis
        ctx.fill()
        ctx.begin_path()
        ctx.rect(x - .6, y - 5, 1.2, 5)
        ctx.rect(x - 3, y - 3, 6, 1.1)
        ctx.move_to(x, y - 5)
        ctx.ellipse(x - 1.2, y - 5.8, 1.3, .8, .4, 0, TAU)
        ctx.move_to(x + 2.5, y - 5.8)
        ctx.ellipse(x + 1.2, y - 5.8, 1.3, .8, -.4, 0, TAU)
        ctx.fill_style = trim
        ctx.fill()


# ---------- food ----------

def food_spec(name: str, c: float) -> dict:
    """Parts of the food named `name`, resting on its serving at y = 45, centered on x = c + 2.

    Same keys as furniture_spec plus `front` (lines drawn over the body) and `top` (topper base).
    """
    F = c + 2
    lines, solid, front = [], [], []
    if name == "pizza slice":
        body = [("poly", [(F - 10, 19), (F + 10, 19), (F, 43)], True), ("rr", (F - 11, 16, 22, 4, 2), False)]
        emblem, top = (F, 28.5), (F + 5, 16)
    elif name == "burger":
        body = [("halfellipse", (F, 28, 12, 9), True), ("rr", (F - 12, 35.5, 24, 5, 2.5), False)]
        solid = [("rr", (F - 12.5, 30.8, 25, 4.2, 2))]
        front = [([(F - 12 + k * 2, 29.4 + (.9 if k % 2 else -.9)) for k in range(13)], .9)]
        emblem, top = (F, 38), (F, 19)
    elif name == "ice cream cone":
        body = [("poly", [(F - 6, 29), (F + 6, 29), (F, 45)], False), ("circle", (F, 15.5, 5), True),
                ("circle", (F, 23.5, 6.5), True)]
        front = [([(F - 4.6, 31.5), (F + 1.2, 41)], .4), ([(F + 4.6, 31.5), (F - 1.2, 41)], .4)]
        emblem, top = (F, 34), (F, 10.5)
    elif name == "cupcake":
        body = [("poly", [(F - 7, 33), (F + 7, 33), (F + 5.5, 45), (F - 5.5, 45)], False), ("halfellipse", (F, 33, 8.5, 6), True),
                ("circle", (F, 25.5, 4.5), True)]
        front = [([(F - 4.4, 34), (F - 3.6, 44.5)], .4), ([(F + 4.4, 34), (F + 3.6, 44.5)], .4)]
        emblem, top = (F, 39.4), (F, 21)
    elif name == "donut":
        body = [("ellipse", (F, 37, 11.5, 6.5, 0), False), ("ellipse", (F, 36, 10, 5, 0), True)]
        solid = [("ellipse", (F, 36, 3, 1.5, 0))]
        emblem, top = (F, 41), (F + 5.5, 33.4)
    elif name == "ramen bowl":
        lines = [([(F + 2, 32), (F + 10, 17)], .9), ([(F + 4.5, 32), (F + 12.5, 18.4)], .9)]
        body = [("lowerellipse", (F, 32, 13, 11), False), ("ellipse", (F, 32, 13, 2.6, 0), True),
                ("ellipse", (F - 5, 31.4, 3, 1.5, 0), False)]
        solid = [("rect", (F - 4, 42.6, 8, 1.6))]
        emblem, top = (F, 38), (F + 1, 31)
    else:  # hot dog
        body = [("rr", (F - 12, 28.5, 24, 4.5, 2.2), False), ("rr", (F - 14.5, 30.2, 29, 4.4, 2.2), True),
                ("rr", (F - 13, 33, 26, 7, 3.5), False)]
        emblem, top = (F, 36.6), (F, 30.2)
    return dict(body=body, lines=lines, solid=solid, front=front, emblem=emblem, top=top)


def draw_food(ctx: Canvas, f, c: float, glow, vis: str, trim: str, t: Theme) -> None:
    sp = food_spec(FOODS[f.subject - SUBJECT_START["food"]], c)
    ctx.line_join, ctx.line_cap = "round", "round"
    ctx.line_width, ctx.stroke_style = .5, trim
    ctx.begin_path()
    ctx.move_to(c - 17, 50)
    ctx.line_to(c + 17, 50)
    ctx.stroke()
    draw_serving(ctx, f.grille, c + 2, vis, trim, t)
    draw_side(ctx, f.cheek, c - 14, 46, vis, trim, t)
    _draw_parts(ctx, sp, draw_topping, f.vstyle, f.decal, glow, vis, trim, t)
    draw_topper(ctx, f.mod, *sp["top"], vis, trim, glow, t)


def draw_topping(ctx: Canvas, style, x0, y0, x1, y1, vis) -> None:
    ctx.fill_style, ctx.stroke_style = vis, vis
    ctx.begin_path()
    step = 3.2 if style in (3, 4) else 2.8
    row, y = 0, y0 + 1.4
    while y < y1 + 1:
        x = x0 + (step / 2 if row % 2 else 0)
        k = row
        while x < x1 + 1:
            if style == 0:  # sprinkles
                a = .7 if k % 2 else -.7
                ctx.move_to(x - .7 * math.cos(a), y - .7 * math.sin(a))
                ctx.line_to(x + .7 * math.cos(a), y + .7 * math.sin(a))
            elif style == 1:  # seeds
                ctx.move_to(x + .4, y)
                ctx.ellipse(x, y, .4, .75, 0, 0, TAU)
            elif style == 2:  # dots
                ctx.move_to(x + .75, y)
                ctx.arc(x, y, .75, 0, TAU)
            elif style in (3, 4):  # stars, hearts
                _symbol(ctx, 4 if style == 3 else 7, x, y, .95, vis)
            elif style == 6:  # chips
                ctx.rect(x - .55, y - .45, 1.1, .9)
            elif style == 7:  # rings
                ctx.move_to(x + .8, y)
                ctx.arc(x, y, .8, 0, TAU)
            x, k = x + step, k + 1
        row, y = row + 1, y + (3.2 if style == 5 else 2.6)
    if style == 5:  # drizzle
        y = y0 + 1.4
        while y < y1 + 1:
            x, k = x0 - 1, 0
            while x < x1 + 1.6:
                (ctx.line_to if k else ctx.move_to)(x, y + (1.1 if k % 2 else -1.1))
                x, k = x + 1.6, k + 1
            y += 3.2
    if style in (0, 5, 7):
        ctx.line_width = .55 if style == 0 else .6 if style == 5 else .4
        ctx.stroke()
    elif style not in (3, 4):
        ctx.fill()


def draw_serving(ctx: Canvas, style, x, vis, trim, t: Theme) -> None:
    ctx.line_width, ctx.stroke_style, ctx.fill_style = .6, trim, t.panel
    ctx.begin_path()
    if style == 0:  # round plate
        ctx.move_to(x + 13.5, 45.6)
        ctx.ellipse(x, 45.6, 13.5, 2.2, 0, 0, TAU)
        ctx.fill()
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(x + 9, 45.4)
        ctx.ellipse(x, 45.4, 9, 1.2, 0, 0, TAU)
        ctx.line_width = .35
        ctx.stroke()
    elif style == 1:  # wooden board
        _shape(ctx, "rr", (x - 13, 44.4, 26, 2.6, 1))
        ctx.fill()
        ctx.stroke()
        ctx.begin_path()
        _shape(ctx, "rr", (x + 13, 44.9, 3.5, 1.6, .8))
        ctx.fill_style = trim
        ctx.fill()
        ctx.begin_path()
        for x0, x1 in ((-10, -4), (-1, 6), (8, 11)):
            ctx.move_to(x + x0, 45.7)
            ctx.line_to(x + x1, 45.7)
        ctx.line_width = .3
        ctx.stroke()
    elif style == 2:  # napkin
        _poly(ctx, [(x - 11, 44.2), (x + 13, 44.2), (x + 11, 47.6), (x - 13, 47.6)])
        ctx.fill_style = vis
        ctx.global_alpha = .5
        ctx.fill()
        ctx.global_alpha = 1
        ctx.line_width = .4
        ctx.stroke()
    elif style == 3:  # tray
        ctx.move_to(x - 13, 44.4)
        ctx.line_to(x - 15, 42.6)
        ctx.move_to(x + 13, 44.4)
        ctx.line_to(x + 15, 42.6)
        ctx.line_width = .8
        ctx.stroke()
        ctx.begin_path()
        ctx.rect(x - 13, 44.2, 26, 1.8)
        ctx.fill()
        ctx.line_width = .6
        ctx.stroke()
    elif style == 4:  # cake stand
        ctx.rect(x - 1, 46, 2, 2.6)
        ctx.move_to(x + 4.5, 49.2)
        ctx.ellipse(x, 49.2, 4.5, .8, 0, 0, TAU)
        ctx.fill_style = trim
        ctx.fill()
        ctx.begin_path()
        ctx.move_to(x + 12.5, 45)
        ctx.ellipse(x, 45, 12.5, 1.5, 0, 0, TAU)
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.stroke()
    elif style == 5:  # picnic cloth
        for k in range(15):
            ctx.rect(x - 15 + k * 2, 45 + (k % 2) * 2, 2, 2)
        ctx.fill_style = trim
        ctx.global_alpha = .6
        ctx.fill()
        ctx.global_alpha = 1
    elif style == 6:  # leaf
        ctx.move_to(x + 14, 45.8)
        ctx.ellipse(x, 45.8, 14, 2.2, 0, 0, TAU)
        ctx.fill_style = vis
        ctx.global_alpha = .7
        ctx.fill()
        ctx.global_alpha = 1
        ctx.begin_path()
        ctx.move_to(x - 13, 45.8)
        ctx.line_to(x + 13, 45.8)
        ctx.line_width = .4
        ctx.stroke()
    else:  # bento box
        ctx.rect(x - 13.5, 43.8, 27, 3.6)
        ctx.fill()
        ctx.stroke()
        ctx.begin_path()
        for dx in (-4.5, 4.5):
            ctx.move_to(x + dx, 43.8)
            ctx.line_to(x + dx, 47.4)
        ctx.line_width = .4
        ctx.stroke()


def draw_side(ctx: Canvas, style, x, y, vis, trim, t: Theme) -> None:
    ctx.line_width, ctx.stroke_style, ctx.fill_style = .7, trim, trim
    ctx.begin_path()
    if style == 0:  # fork
        ctx.move_to(x, y)
        ctx.line_to(x, y - 6)
        ctx.stroke()
        ctx.begin_path()
        ctx.rect(x - 1.3, y - 8.4, 2.6, 1)
        ctx.fill()
        ctx.begin_path()
        for dx in (-1.2, 0, 1.2):
            ctx.move_to(x + dx, y - 8.4)
            ctx.line_to(x + dx, y - 11.2)
        ctx.line_width = .45
        ctx.stroke()
    elif style == 1:  # spoon
        ctx.move_to(x, y)
        ctx.line_to(x, y - 6.4)
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(x + 1.4, y - 8.6)
        ctx.ellipse(x, y - 8.6, 1.4, 2.2, 0, 0, TAU)
        ctx.fill()
    elif style == 2:  # chopsticks
        ctx.move_to(x - 1.5, y)
        ctx.line_to(x + .5, y - 13)
        ctx.move_to(x + .2, y)
        ctx.line_to(x + 2, y - 12.7)
        ctx.line_width = .6
        ctx.stroke()
    else:  # cup with a straw
        ctx.move_to(x + .6, y - 6)
        ctx.line_to(x + 1.8, y - 10.4)
        ctx.line_width = .5
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(x - 2.6, y - 3.6, 1.5, math.pi * .5, math.pi * 1.5)
        ctx.stroke()
        ctx.begin_path()
        _shape(ctx, "rr", (x - 2.6, y - 7, 5.2, 7, 1))
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.stroke()
        ctx.begin_path()
        ctx.rect(x - 2, y - 6, 4, 1.2)
        ctx.fill_style = vis
        ctx.fill()


def draw_topper(ctx: Canvas, style, x, y, vis, trim, glow, t: Theme) -> None:
    ctx.line_width, ctx.stroke_style = .45, trim
    ctx.begin_path()
    if style == 0:  # cherry
        ctx.move_to(x, y - 3.4)
        ctx.quadratic_curve_to(x + .4, y - 5.6, x + 1.8, y - 6.4)
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(x, y - 1.8, 1.8, 0, TAU)
        glow(vis, 1)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
    elif style == 1:  # candle
        ctx.rect(x - .7, y - 5.5, 1.4, 5.5)
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(x + .7, y - 6.8)
        ctx.ellipse(x, y - 6.8, .7, 1.2, 0, 0, TAU)
        glow(vis, 1.4)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
    elif style == 2:  # flag pick
        ctx.move_to(x, y)
        ctx.line_to(x, y - 8)
        ctx.line_width = .5
        ctx.stroke()
        ctx.begin_path()
        _poly(ctx, [(x, y - 8), (x + 3.6, y - 7), (x, y - 6)])
        ctx.fill_style = vis
        ctx.fill()
    else:  # mint leaves
        for s in (-1, 1):
            ctx.move_to(x + s * 1.3 + 1.6 * math.cos(s * .6), y - 1.4 + 1.6 * math.sin(s * .6))
            ctx.ellipse(x + s * 1.3, y - 1.4, 1.6, .8, s * .6, 0, TAU)
        ctx.fill_style = vis
        ctx.fill()


# ---------- sports equipment ----------

def sport_spec(name: str, c: float) -> dict:
    """Parts of the sports equipment named `name` on the pitch at y = 46, near x = c.

    Same keys as food_spec plus `gear` (base of the gear item) and `motion` (x, y, direction).
    """
    lines, solid, front = [], [], []
    if name == "soccer ball":
        B = c - 2
        pent = [(B + 3.6 * math.cos(-math.pi / 2 + k * TAU / 5), 32 + 3.6 * math.sin(-math.pi / 2 + k * TAU / 5)) for k in range(5)]
        body = [("circle", (B, 33, 11), True)]
        solid = [("poly", pent)]
        front = [([(x, y), (B + (x - B) * 2.1, 32 + (y - 32) * 2.1)], .5) for x, y in pent]
        emblem, gear, motion = (B + 5.5, 39.5), (c + 13.5, 46), (c - 13.5, 30, (-1, 0))
    elif name == "tennis racket":
        ux, uy, px, py = -.479, .878, 1.14, .62
        x0, y0 = c - 2.8, 30.8
        x1, y1 = x0 + 14 * ux, y0 + 14 * uy
        body = [("poly", [(x0 + px, y0 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (x0 - px, y0 - py)], False),
                ("ellipse", (c + 2, 22, 7.5, 10, .5), True), ("circle", (c + 8, 42.6, 2.8), False)]
        xm, ym = x0 + 8 * ux, y0 + 8 * uy
        solid = [("poly", [(xm + px, ym + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (xm - px, ym - py)])]
        front = [([(c + 5.6, 40.4), (c + 7.6, 42.6), (c + 10.4, 43.4)], .4)]
        emblem, gear, motion = (c + 2, 22), (c + 14.5, 46), (c + 10.5, 13, (.86, -.5))
    elif name == "skateboard":
        K = c - 4
        body = [("poly", [(K - 12, 33.5), (K - 10, 36), (K + 10, 36), (K + 12, 33.5), (K + 13, 34.5), (K + 11, 40),
                          (K - 11, 40), (K - 13, 34.5)], True)]
        solid = [("rect", (K - 8, 40, 4, 1.6)), ("rect", (K + 4, 40, 4, 1.6)), ("circle", (K - 6, 43.2, 2.4)), ("circle", (K + 6, 43.2, 2.4))]
        emblem, gear, motion = (K, 38), (c + 13, 46), (K - 13, 38, (-1, 0))
    elif name == "bowling pin":
        P = c - 6
        prof = ((13, 0), (14, 2.2), (16, 3.3), (19, 3.2), (22, 2.2), (24, 2), (27, 3.5), (31, 5.6), (35, 6.3), (39, 5.6), (43, 4.2), (45, 3.4))
        pin = [(P + w, y) for y, w in prof] + [(P - w, y) for y, w in reversed(prof)]
        body = [("poly", pin, True), ("circle", (c + 7.5, 40.5, 5.5), False)]
        solid = [("rect", (P - 2.3, 21.6, 4.6, 1)), ("rect", (P - 2.1, 23.6, 4.2, 1)),
                 ("circle", (c + 6, 38, .8)), ("circle", (c + 8.6, 37.6, .8)), ("circle", (c + 7.6, 40.2, .9))]
        emblem, gear, motion = (P, 35), (c - 14.5, 46), (c + 7.5, 33.5, (0, -1))
    else:  # boxing glove
        G = c - 2
        body = [("rr", (G - 6, 35, 12, 9, 2), False), ("ellipse", (G, 25, 9.5, 11, 0), True), ("ellipse", (G + 8, 29, 3, 5.5, .35), False)]
        solid = [("rr", (G - 6.5, 34, 13, 2.4, 1))]
        front = [([(G - 2, 37.5), (G + 2, 41)], .5), ([(G + 2, 37.5), (G - 2, 41)], .5)]
        emblem, gear, motion = (G - 1, 24), (c + 13.5, 46), (c - 13.5, 25, (-1, 0))
    return dict(body=body, lines=lines, solid=solid, front=front, emblem=emblem, gear=gear, motion=motion)


def draw_sport(ctx: Canvas, f, c: float, glow, vis: str, trim: str, t: Theme) -> None:
    sp = sport_spec(SPORTS[f.subject - SUBJECT_START["sports"]], c)
    ctx.line_join, ctx.line_cap = "round", "round"
    draw_pitch(ctx, f.cheek, c, vis, trim)
    x, y, d = sp["motion"]
    draw_trail(ctx, (2, 3, 6, 0)[f.mod], x, y, d, vis, trim, glow)
    _draw_parts(ctx, sp, draw_fabric, f.vstyle, f.decal, glow, vis, trim, t)
    draw_gear(ctx, f.grille, *sp["gear"], vis, trim, glow, t)


def draw_pitch(ctx: Canvas, style, c, vis, trim) -> None:
    if style == 2:  # wood floor
        draw_floor(ctx, 1, c, vis, trim)
        return
    ctx.line_width, ctx.stroke_style, ctx.fill_style = .5, trim, trim
    ctx.begin_path()
    ctx.move_to(c - 17, 50)
    ctx.line_to(c + 17, 50)
    ctx.stroke()
    ctx.begin_path()
    if style == 0:  # grass
        for k in range(12):
            x = c - 16.5 + k * 3
            ctx.move_to(x - .8, 47.6)
            ctx.line_to(x, 50)
            ctx.line_to(x + .8, 47.4)
        ctx.line_width = .45
        ctx.stroke()
        return
    ctx.rect(c - 17, 46.4, 34, 3.6)
    ctx.fill_style = trim if style == 1 else vis
    ctx.global_alpha = .3
    ctx.fill()
    ctx.global_alpha = 1
    ctx.begin_path()
    if style == 1:  # court lines
        ctx.move_to(c - 17, 48.2)
        ctx.line_to(c + 17, 48.2)
        ctx.move_to(c, 46.4)
        ctx.line_to(c, 50)
        ctx.line_width, ctx.stroke_style = .5, vis
    else:  # ice
        ctx.move_to(c - 12, 49)
        ctx.line_to(c - 6, 47.4)
        ctx.move_to(c + 3, 49.2)
        ctx.line_to(c + 10, 47.6)
        ctx.line_width = .3
    ctx.stroke()


def draw_gear(ctx: Canvas, style, x, y, vis, trim, glow, t: Theme) -> None:
    ctx.fill_style, ctx.stroke_style, ctx.line_width = trim, trim, .5
    ctx.begin_path()
    if style == 0:  # whistle
        ctx.move_to(x + 1.7, y - 2.2)
        ctx.arc(x - .5, y - 2.2, 2.2, 0, TAU)
        ctx.rect(x + .6, y - 4.4, 3, 1.6)
        ctx.fill()
        ctx.begin_path()
        ctx.arc(x - 1.6, y - 6, 1.8, 0, TAU)
        ctx.stroke_style = vis
        ctx.stroke()
    elif style == 1:  # water bottle
        _shape(ctx, "rr", (x - 1.8, y - 7, 3.6, 7, 1))
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.stroke()
        ctx.begin_path()
        ctx.rect(x - 1, y - 8.6, 2, 1.6)
        ctx.fill_style = trim
        ctx.fill()
        ctx.begin_path()
        ctx.rect(x - 1.8, y - 4.6, 3.6, 1.6)
        ctx.fill_style = vis
        ctx.fill()
    elif style == 2:  # trophy
        ctx.rect(x - .6, y - 4.6, 1.2, 3)
        ctx.rect(x - 2.4, y - 1.6, 4.8, 1.6)
        ctx.fill()
        ctx.begin_path()
        for s in (-1, 1):
            ctx.move_to(x + s * 2.6, y - 7.4)
            ctx.arc(x + s * 3, y - 6.6, 1.1, -math.pi / 2, math.pi / 2, s < 0)
        ctx.stroke()
        ctx.begin_path()
        _poly(ctx, [(x - 3, y - 8.4), (x + 3, y - 8.4), (x + 2, y - 4.6), (x - 2, y - 4.6)])
        glow(vis, 1)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
    elif style == 3:  # medal
        ctx.move_to(x - 2.2, y - 8.6)
        ctx.line_to(x, y - 4.6)
        ctx.line_to(x + 2.2, y - 8.6)
        ctx.line_width, ctx.stroke_style = 1, vis
        ctx.stroke()
        ctx.begin_path()
        ctx.arc(x, y - 2.6, 2.4, 0, TAU)
        glow(vis, 1)
        ctx.fill_style = vis
        ctx.fill()
        glow.off()
        ctx.line_width, ctx.stroke_style = .5, trim
        ctx.stroke()
    elif style == 4:  # stopwatch
        ctx.rect(x - .7, y - 7.6, 1.4, 1.2)
        ctx.fill()
        ctx.begin_path()
        ctx.arc(x, y - 3.4, 3, 0, TAU)
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.stroke()
        ctx.begin_path()
        ctx.move_to(x, y - 3.4)
        ctx.line_to(x + 1.4, y - 4.8)
        ctx.line_width, ctx.stroke_style = .5, vis
        ctx.stroke()
    elif style == 5:  # cone
        _poly(ctx, [(x - 3, y), (x + 3, y), (x + .8, y - 7), (x - .8, y - 7)])
        ctx.fill_style = vis
        ctx.fill()
        ctx.begin_path()
        ctx.rect(x - 1.9, y - 4, 3.8, 1.2)
        ctx.fill_style = trim
        ctx.fill()
    elif style == 6:  # cap
        _shape(ctx, "halfellipse", (x - .6, y - 1.2, 3, 3.2))
        ctx.rect(x - .6, y - 1.8, 4.4, .8)
        ctx.fill()
        ctx.begin_path()
        ctx.arc(x - .6, y - 4.6, .6, 0, TAU)
        ctx.fill_style = vis
        ctx.fill()
    else:  # corner flag
        ctx.move_to(x, y)
        ctx.line_to(x, y - 9)
        ctx.stroke()
        ctx.begin_path()
        _poly(ctx, [(x, y - 9), (x + 4, y - 7.6), (x, y - 6.2)])
        ctx.fill_style = vis
        ctx.fill()


# ---------- icon kinds: instruments, computer symbols, large shapes, insignia ----------

def draw_icon(ctx: Canvas, f, c: float, kind: str, glow, vis: str, trim: str, t: Theme) -> None:
    """Backdrop (grille), base (cheek), the icon with its fill pattern (vstyle) and badge symbol
    (decal), then an effect (mod)."""
    names = dict(SUBJECT_KINDS)[kind]
    sp = shifted(icon_spec(kind, names[f.subject - SUBJECT_START[kind]]), c)
    ctx.line_join, ctx.line_cap = "round", "round"
    draw_backdrop(ctx, f.grille, c, vis, trim)
    draw_base(ctx, f.cheek, c, trim, t)
    _draw_parts(ctx, sp, draw_fabric, f.vstyle, f.decal, glow, vis, trim, t)
    if "text" in sp:
        ch, x, y, size, inverted, font = sp["text"]
        ctx.set_font(font, size)
        ctx.text_align, ctx.text_baseline = "center", "alphabetic"
        ctx.fill_style = t.panel if inverted else trim
        ctx.fill_text(ch, x, y)
    draw_effect(ctx, f.mod, c, vis, trim, glow)


def backdrop_shape(style, c):
    if style == 0:
        return "circle", (c, 28, 16.5)
    if style == 1:
        return "rr", (c - 15.5, 12.5, 31, 31, 3)
    if style == 2:
        return "poly", [(c, 9.6), (c + 18, 28), (c, 46.4), (c - 18, 28)]
    if style == 3:
        return "poly", [(c + 17.5 * math.cos(k * TAU / 6), 28 + 17.5 * math.sin(k * TAU / 6)) for k in range(6)]
    if style == 4:
        return "poly", [(c - 15, 11), (c + 15, 11), (c + 15, 30), (c, 46.6), (c - 15, 30)]
    if style == 5:
        return "poly", [(c + (18 if k % 2 == 0 else 14) * math.cos(k * math.pi / 12), 28 + (18 if k % 2 == 0 else 14) * math.sin(k * math.pi / 12))
                        for k in range(24)]
    if style == 6:
        return "multi", [[(c + 18 * math.cos(k * TAU / 40), 28 + 18 * math.sin(k * TAU / 40)) for k in range(40)],
                         [(c + 14.6 * math.cos(-k * TAU / 40), 28 + 14.6 * math.sin(-k * TAU / 40)) for k in range(40)]]
    return "poly", [(c - 17.5, 21), (c + 17.5, 21), (c + 14, 28), (c + 17.5, 35), (c - 17.5, 35), (c - 14, 28)]


def draw_backdrop(ctx: Canvas, style, c, vis, trim) -> None:
    kind, a = backdrop_shape(style, c)
    ctx.begin_path()
    _shape(ctx, kind, a)
    ctx.fill_style = vis
    ctx.global_alpha = .24
    ctx.fill()
    ctx.global_alpha = .6
    ctx.line_width, ctx.stroke_style = .5, trim
    ctx.stroke()
    ctx.global_alpha = 1


def draw_base(ctx: Canvas, style, c, trim, t: Theme) -> None:
    ctx.line_width, ctx.stroke_style, ctx.fill_style = 1.2, trim, trim
    ctx.begin_path()
    if style == 0:  # underline
        ctx.move_to(c - 12, 48.4)
        ctx.line_to(c + 12, 48.4)
        ctx.stroke()
    elif style == 1:  # corner brackets
        for sx in (-1, 1):
            for y0, dy in ((8, 1), (49, -1)):
                ctx.move_to(c + sx * 13, y0)
                ctx.line_to(c + sx * 17, y0)
                ctx.line_to(c + sx * 17, y0 + dy * 4)
        ctx.line_width = .8
        ctx.stroke()
    elif style == 2:  # dotted line
        for k in range(9):
            x = c - 12 + k * 3
            ctx.move_to(x + .7, 48.4)
            ctx.arc(x, 48.4, .7, 0, TAU)
        ctx.fill()
    else:  # pedestal
        _shape(ctx, "rr", (c - 8, 45.6, 16, 2.6, 1))
        ctx.fill_style = t.panel
        ctx.fill()
        ctx.line_width = .5
        ctx.stroke()
        ctx.begin_path()
        ctx.rect(c - 11, 48.2, 22, 1.6)
        ctx.fill_style = trim
        ctx.fill()


def draw_effect(ctx: Canvas, style, c, vis, trim, glow) -> None:
    glow(vis, .8)
    ctx.fill_style, ctx.stroke_style = vis, vis
    ctx.begin_path()
    if style == 0:  # music notes
        for x, y in ((c + 13.4, 13), (c - 14.6, 9.6)):
            ctx.move_to(x + 1.2, y)
            ctx.ellipse(x, y, 1.2, .9, -.4, 0, TAU)
        ctx.fill()
        ctx.begin_path()
        for x, y in ((c + 13.4, 13), (c - 14.6, 9.6)):
            ctx.move_to(x + 1.1, y)
            ctx.line_to(x + 1.1, y - 4.4)
            ctx.line_to(x + 2.8, y - 3.2)
        ctx.line_width = .5
        ctx.stroke()
    elif style == 1:  # sparkles
        for x, y, r in ((c + 13.6, 11, 2.2), (c - 14, 14, 1.6), (c + 15.4, 18.6, 1.3)):
            _poly(ctx, [(x, y - r), (x + r * .3, y - r * .3), (x + r, y), (x + r * .3, y + r * .3), (x, y + r),
                        (x - r * .3, y + r * .3), (x - r, y), (x - r * .3, y - r * .3)])
        ctx.fill()
    elif style == 2:  # rays from the top corners
        for sx in (-1, 1):
            for a in (-.5, -.95, -1.4):
                ax, ay = math.cos(a) * sx, math.sin(a)
                ctx.move_to(c + sx * 12 + ax * 1.5, 12 + ay * 1.5)
                ctx.line_to(c + sx * 12 + ax * 4.5, 12 + ay * 4.5)
        ctx.line_width = .6
        ctx.stroke()
    else:  # orbit dots along an arc over the top
        for k in range(7):
            a = math.pi * (1.15 + k * .7 / 6)
            x, y = c + 16 * math.cos(a), 26 + 16 * math.sin(a)
            r = .5 + .12 * k
            ctx.move_to(x + r, y)
            ctx.arc(x, y, r, 0, TAU)
        ctx.fill()
    glow.off()
