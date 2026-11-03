"""Geometry for the icon-style subjects: musical instruments, computer symbols, large basic shapes,
sci-fi insignia (an original set), weather, space, flags, holidays, game icons, tools, game pieces,
road signs, clothing and the 32 characters of the badge alphabet.

Every icon is plain data at x = 0 (centered on y = 28), in the same part format as furniture and
food: `body` parts are filled with the panel color, pattern-filled when flagged and outlined in trim;
`solid` parts are filled in trim; `lines` are stroked behind the body and `front` lines over it.
`docs/build_lab.py` exports this data to the browser lab, so the lab draws exactly these shapes.
"""

from __future__ import annotations

import math
from functools import lru_cache

TAU = math.tau
CY = 28

INSTRUMENTS = ("guitar", "drum", "trumpet", "saxophone", "harp", "xylophone", "maracas", "tambourine", "accordion",
               "handbell", "metronome")
COMPUTER = ("floppy disk", "monitor", "computer mouse", "power button", "wifi", "cursor", "folder", "game controller",
            "padlock", "hourglass", "magnifier")
SHAPES = ("circle", "square", "triangle", "diamond", "star", "hexagon", "heart", "plus", "arrow", "ring", "chevron")
INSIGNIA = ("winged orb", "triple chevron", "ringed star", "crossed blades", "banded shield", "crown", "trident", "atom",
            "anchor", "cog", "laurel")
WEATHER = ("sun", "rain cloud", "thunderstorm", "snowflake", "rainbow", "tornado", "umbrella", "thermometer",
           "windsock", "snowman")
SPACE = ("ringed planet", "crescent moon", "comet", "spiral galaxy", "astronaut helmet", "satellite", "telescope",
         "constellation", "asteroid", "lunar lander")


# ---------- point helpers (all rounded so the exported data stays small and exact) ----------

def _r(pts):
    return [(round(x, 2), round(y, 2)) for x, y in pts]


def arc_pts(cx, cy, rx, ry, a0, a1, n=24, rot=0.0):
    out = []
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return _r(out)


def reg(n, r, cx=0.0, cy=CY, rot=-math.pi / 2):
    return _r([(cx + r * math.cos(rot + k * TAU / n), cy + r * math.sin(rot + k * TAU / n)) for k in range(n)])


def star(n, R, r, cx=0.0, cy=CY, rot=-math.pi / 2):
    return _r([(cx + (R if k % 2 == 0 else r) * math.cos(rot + k * math.pi / n),
                cy + (R if k % 2 == 0 else r) * math.sin(rot + k * math.pi / n)) for k in range(2 * n)])


def rot_rect(x0, y0, x1, y1, w):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    px, py = -dy / L * w / 2, dx / L * w / 2
    return _r([(x0 + px, y0 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (x0 - px, y0 - py)])


def ring(cx, cy, R, r, n=40):
    outer = [(cx + R * math.cos(k * TAU / n), cy + R * math.sin(k * TAU / n)) for k in range(n)]
    inner = [(cx + r * math.cos(-k * TAU / n), cy + r * math.sin(-k * TAU / n)) for k in range(n)]
    return ("multi", [_r(outer), _r(inner)])


def mirror(pts):
    return [(-x, y) for x, y in reversed(pts)]


def _inside(parts, x, y):
    for p in parts:
        k = p[0]
        if k == "circle" and (x - p[1]) ** 2 + (y - p[2]) ** 2 <= p[3] ** 2:
            return True
        if k == "ellipse" and ((x - p[1]) / p[3]) ** 2 + ((y - p[2]) / p[4]) ** 2 <= 1:
            return True
        if k == "rect" and p[1] <= x <= p[1] + p[3] and p[2] <= y <= p[2] + p[4]:
            return True
    return False


def union_poly(parts, cx, cy, n=96):
    """Outline of a union of circles, ellipses and rects that is star-shaped around (cx, cy)."""
    out = []
    for k in range(n):
        a = k * TAU / n
        t = 30.0
        while t > 0 and not _inside(parts, cx + t * math.cos(a), cy + t * math.sin(a)):
            t -= .05
        out.append((cx + t * math.cos(a), cy + t * math.sin(a)))
    return _r(out)


def heart(cx, cy, s, n=48):
    pts = []
    for k in range(n):
        t = k * TAU / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s, cy - y * s))
    return _r(pts)


def drop(cx, cy, r, n=40):
    pts = [(cx, cy - r * 2.1)]
    for k in range(n + 1):
        a = -math.pi * .17 + k * math.pi * 1.34 / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return _r(pts)


def B(kind, args, fab=False):
    return (kind, args, fab)


def icon(body, solid=(), lines=(), front=(), emblem=(0, CY)):
    return dict(body=list(body), solid=list(solid), lines=list(lines), front=list(front), emblem=emblem)


# ---------- musical instruments ----------

def _instrument(name):
    if name == "guitar":
        body = union_poly([("circle", 0, 26.5, 5.6), ("circle", 0, 36, 7.6)], 0, 32)
        return icon([B("rect", (-1.2, 8, 2.4, 22)), B("poly", body, True)],
                    solid=[("rr", (-2, 4.5, 4, 5, 1)), ("circle", (0, 31.5, 2)), ("rect", (-2.6, 37.4, 5.2, 1))],
                    front=[([(-.6, 9), (-.6, 37.4)], .25), ([(.6, 9), (.6, 37.4)], .25)], emblem=(0, 41.4))
    if name == "drum":
        return icon([B("rect", (-11, 26, 22, 13), True), B("ellipse", (0, 26, 11, 3, 0)), B("lowerellipse", (0, 39, 11, 3))],
                    solid=[("circle", (-9.4, 13.2, 1.3)), ("circle", (9.4, 13.2, 1.3))],
                    lines=[([(-9, 13), (3, 25)], .9), ([(9, 13), (-3, 25)], .9)],
                    front=[([(-11 + k * 2.75, 29 + (0 if k % 2 else 9)) for k in range(9)], .45)], emblem=(0, 33.5))
    if name == "trumpet":
        return icon([B("rr", (-9, 28, 13, 7.5, 3.6), True), B("rect", (-13, 24.6, 19, 3.2)),
                     B("poly", [(5, 25), (12.5, 19), (12.5, 34.4), (5, 27.8)])],
                    solid=[("rect", (-6.6, 20.4, 1.8, 4.2)), ("rect", (-3.6, 20.4, 1.8, 4.2)), ("rect", (-.6, 20.4, 1.8, 4.2)),
                           ("rect", (-14.5, 25, 1.8, 2.4))], emblem=(-2.5, 31.7))
    if name == "saxophone":
        sax = [(-3, 13), (-3, 37), (-1, 41.6), (3, 43), (7, 41.4), (9.2, 36), (11.6, 28.4), (4.2, 28.4), (5, 34.6), (3.4, 37.6),
               (1.2, 37.4), (1, 15), (3, 11.6), (1, 10)]
        return icon([B("poly", sax, True)], solid=[("circle", (-1, y, .9)) for y in (18, 22, 26, 30)],
                    lines=[([(-1, 11), (-6.5, 7.5)], 1)], emblem=(4.6, 39.4))
    if name == "harp":
        frame = [(-11, 9), (-6.6, 9), (10, 20.5), (9, 44), (-11, 44)]
        return icon([B("poly", frame, True)], solid=[("rect", (-12, 43, 22, 2.2))],
                    front=[([(x, 12 + (x + 7) * 8.5 / 16), (x, 42.5)], .3) for x in (-5, -2, 1, 4, 7)], emblem=(-7, 38))
    if name == "xylophone":
        bars = [B("rr", (-12 + k * 4.2, 14 + k * 2, 3.2, 22 - k * 3, 1), True) for k in range(6)]
        return icon([B("rect", (-13.5, 37.5, 27, 3))] + bars,
                    lines=[([(-14, 40.5), (-16, 45)], .7), ([(13.5, 40.5), (15.5, 45)], .7)],
                    solid=[("circle", (-4, 9, 1.4)), ("circle", (6, 9.6, 1.4))],
                    front=[([(-4, 9), (2, 18)], .5), ([(6, 9.6), (9, 19)], .5)], emblem=(0, 39))
    if name == "maracas":
        return icon([B("poly", rot_rect(-6, 26, -9, 42, 2.2)), B("poly", rot_rect(5, 27, 9, 43, 2.2)),
                     B("ellipse", (-4, 19, 5.2, 7.4, -.35), True), B("ellipse", (5, 20.5, 5.2, 7.4, .35), True)],
                    emblem=(-4, 19))
    if name == "tambourine":
        jingles = [("ellipse", (11.4 * math.cos(a), CY + 11.4 * math.sin(a), 1.7, 1.1, a + math.pi / 2)) for a in
                   [k * TAU / 6 + .3 for k in range(6)]]
        return icon([B("circle", (0, CY, 11)), B("circle", (0, CY, 8), True)], solid=jingles,
                    lines=[([(8, 36), (12, 44), (15, 42)], .6)], emblem=(0, CY))
    if name == "accordion":
        return icon([B("rect", (-5, 17, 10, 22), True), B("rr", (-13, 15, 8.5, 26, 1.5)), B("rr", (4.5, 15, 8.5, 26, 1.5))],
                    solid=[("rect", (7, 17.5 + k * 3.1, 4, 1.8)) for k in range(7)] + [("circle", (-10.6, 19 + k * 3.4, .8)) for k in range(4)],
                    front=[([(-5 + k * 2.5, 17), (-5 + k * 2.5, 39)], .3) for k in range(1, 4)], emblem=(-8.75, 35.2))
    if name == "handbell":
        bell = [(-3.6, 19)] + arc_pts(0, 21, 4, 4, math.pi, TAU, 10)[1:-1] + [(3.6, 19), (5, 30), (11, 38.6), (-11, 38.6), (-5, 30)]
        return icon([B("rr", (-1.6, 7, 3.2, 12, 1.2)), B("poly", bell, True)],
                    solid=[("circle", (0, 41, 2.2)), ("rr", (-3, 6, 6, 2.6, 1))], emblem=(0, 31))
    # metronome
    return icon([B("poly", [(-8, 44), (8, 44), (4.6, 10), (-4.6, 10)], True)],
                solid=[("rect", (-10, 43.5, 20, 2.2)), ("rect", (1.6, 20, 3.4, 2.4))],
                front=[([(0, 40), (5, 14)], .8)], emblem=(0, 37.6))


# ---------- computer symbols ----------

def _computer(name):
    if name == "floppy disk":
        return icon([B("poly", [(-11, 16), (8, 16), (11, 19), (11, 40), (-11, 40)], True), B("rect", (-6, 16, 12, 8)),
                     B("rr", (-7.5, 28.5, 15, 11.5, 1))], solid=[("rect", (1.6, 17.6, 2.6, 4.8))], emblem=(0, 34.2))
    if name == "monitor":
        return icon([B("rr", (-13, 12, 26, 19, 1.6), True)], solid=[("rect", (-2, 31, 4, 6)), ("rr", (-8, 37, 16, 2.6, 1))],
                    front=[([(-11, 29), (11, 29)], .4)], emblem=(0, 21.5))
    if name == "computer mouse":
        return icon([B("ellipse", (0, 31, 8.4, 12.4, 0), True)], solid=[("rr", (-1.1, 20.4, 2.2, 4.4, 1.1))],
                    lines=[([(0, 19), (1, 14), (4.4, 10.4), (9, 9.4)], .7)],
                    front=[([(-8.1, 26), (8.1, 26)], .5), ([(0, 18.6), (0, 26)], .5)], emblem=(0, 34.6))
    if name == "power button":
        return icon([B("circle", (0, CY + 1, 12.4), True)],
                    front=[(arc_pts(0, CY + 1, 7, 7, -math.pi / 2 + .7, 1.5 * math.pi - .7, 28), 2.2), ([(0, 19.4), (0, CY + 1)], 2.2)],
                    emblem=(9, 38.6))
    if name == "wifi":
        return icon([B("rr", (-13, 14, 26, 28, 6), True)], solid=[("circle", (0, 36.4, 2))],
                    front=[(arc_pts(0, 37, r, r, -math.pi * .76, -math.pi * .24, 14), 2) for r in (5, 9, 13)], emblem=(9, 36.4))
    if name == "cursor":
        return icon([B("poly", [(-6, 11), (-6, 38.6), (.2, 32.4), (4.4, 41.6), (8, 40), (3.8, 31), (11.4, 30.6)], True)],
                    emblem=(-2.4, 26.6))
    if name == "folder":
        return icon([B("poly", [(-12.5, 15), (-4.4, 15), (-2, 18.4), (12.5, 18.4), (12.5, 40), (-12.5, 40)]),
                     B("poly", [(-12.5, 23.6), (12.5, 23.6), (12.5, 40), (-12.5, 40)], True)], emblem=(0, 32))
    if name == "game controller":
        pad = [(-8, 25.4), (-6, 25.4), (-6, 27.4), (-4, 27.4), (-4, 29.4), (-6, 29.4), (-6, 31.4), (-8, 31.4), (-8, 29.4),
               (-10, 29.4), (-10, 27.4), (-8, 27.4)]
        return icon([B("ellipse", (-8.4, 33.6, 4.2, 6.4, .35)), B("ellipse", (8.4, 33.6, 4.2, 6.4, -.35)),
                     B("rr", (-13, 21.6, 26, 12, 6), True)],
                    solid=[("poly", pad), ("circle", (7, 24.8, 1.1)), ("circle", (9.6, 27.4, 1.1)), ("circle", (4.4, 27.4, 1.1)),
                           ("circle", (7, 30, 1.1))], emblem=(-.4, 29.6))
    if name == "padlock":
        return icon([B("rr", (-9.6, 24.4, 19.2, 16, 2.2), True)], solid=[("circle", (0, 30, 2)), ("poly", [(-1, 31), (1, 31), (1.6, 35), (-1.6, 35)])],
                    lines=[(arc_pts(0, 24.4, 6, 8.6, math.pi, TAU, 18), 2.4)], emblem=(5.4, 37))
    if name == "hourglass":
        return icon([B("poly", [(-7.4, 14.4), (7.4, 14.4), (1.2, 28), (7.4, 41.6), (-7.4, 41.6), (-1.2, 28)]),
                     B("poly", [(-5, 18), (5, 18), (.6, 26.4), (-.6, 26.4)], True), B("poly", [(0, 34), (6, 41.6), (-6, 41.6)], True)],
                    solid=[("rr", (-9.6, 12, 19.2, 2.6, 1)), ("rr", (-9.6, 41.4, 19.2, 2.6, 1))],
                    lines=[([(-8.6, 14), (-8.6, 42)], .8), ([(8.6, 14), (8.6, 42)], .8)], emblem=(0, 20.6))
    # magnifier
    return icon([B("circle", (-2.6, 24.6, 9.2), True)], solid=[ring(-2.6, 24.6, 10.6, 8.6), ("poly", rot_rect(4.6, 32, 12, 41.4, 3.4))],
                emblem=(-2.6, 24.6))


# ---------- large basic shapes ----------

def _shape(name):
    if name == "circle":
        return icon([B("circle", (0, CY, 13), True)])
    if name == "square":
        return icon([B("rect", (-11.5, 16.5, 23, 23), True)])
    if name == "triangle":
        return icon([B("poly", reg(3, 15, 0, CY + 3), True)], emblem=(0, CY + 4))
    if name == "diamond":
        return icon([B("poly", [(0, 12), (11.5, CY), (0, 44), (-11.5, CY)], True)])
    if name == "star":
        return icon([B("poly", star(5, 15, 6.4, 0, CY + 1.4), True)], emblem=(0, CY + 2))
    if name == "hexagon":
        return icon([B("poly", reg(6, 14), True)])
    if name == "heart":
        return icon([B("poly", heart(0, CY - .6, .82), True)], emblem=(0, CY + 1))
    if name == "plus":
        return icon([B("poly", [(-4.4, 14), (4.4, 14), (4.4, 23.6), (14, 23.6), (14, 32.4), (4.4, 32.4), (4.4, 42), (-4.4, 42),
                                (-4.4, 32.4), (-14, 32.4), (-14, 23.6), (-4.4, 23.6)], True)])
    if name == "arrow":
        return icon([B("poly", [(0, 12), (13, 26), (5.4, 26), (5.4, 44), (-5.4, 44), (-5.4, 26), (-13, 26)], True)], emblem=(0, 34))
    if name == "ring":
        r = ring(0, CY, 13.4, 7.4)
        return icon([B(r[0], r[1], True)])
    # chevron
    return icon([B("poly", [(-14, 33), (0, 17), (14, 33), (14, 41.4), (0, 25.4), (-14, 41.4)], True)], emblem=(0, 31))


# ---------- sci-fi insignia (original designs) ----------

def _insignia(name):
    if name == "winged orb":
        wing = [(-4, 25), (-16.4, 17), (-14.6, 22), (-16.4, 25.6), (-13.6, 28.8), (-14.6, 32.4), (-4.6, 31.4)]
        return icon([B("poly", wing), B("poly", mirror(wing)), B("circle", (0, CY, 6.6), True)])
    if name == "triple chevron":
        chev = lambda y: [(-12.4, y + 7), (0, y), (12.4, y + 7), (12.4, y + 11), (0, y + 4), (-12.4, y + 11)]
        return icon([B("poly", chev(y), True) for y in (12, 20.4, 28.8)], emblem=(0, 44))
    if name == "ringed star":
        return icon([B("poly", star(5, 9.4, 3.8), True)], solid=[ring(0, CY, 13.6, 11)], emblem=(0, CY + .6))
    if name == "crossed blades":
        return icon([B("poly", rot_rect(-10.6, 41, 9, 13, 3.4), True), B("poly", rot_rect(10.6, 41, -9, 13, 3.4), True)],
                    solid=[("poly", rot_rect(-9.6, 33, -3, 38, 1.6)), ("poly", rot_rect(9.6, 33, 3, 38, 1.6)),
                           ("circle", (-11.4, 42.2, 1.6)), ("circle", (11.4, 42.2, 1.6))], emblem=(0, 30.6))
    if name == "banded shield":
        return icon([B("poly", [(-11.4, 13), (11.4, 13), (11.4, 28), (0, 44), (-11.4, 28)], True)],
                    solid=[("poly", [(-11.4, 21.4), (11.4, 21.4), (11.4, 25.4), (-11.4, 25.4)])], emblem=(0, 32.4))
    if name == "crown":
        return icon([B("poly", [(-12.6, 38), (-12.6, 18), (-6.4, 27), (0, 14), (6.4, 27), (12.6, 18), (12.6, 38)], True)],
                    solid=[("rect", (-12.6, 37, 25.2, 4)), ("circle", (-12.6, 16.6, 1.8)), ("circle", (0, 12.6, 1.8)),
                           ("circle", (12.6, 16.6, 1.8))], emblem=(0, 31))
    if name == "trident":
        head = [(-10.4, 11), (-7.6, 15), (-7.6, 22), (-1.4, 22), (-1.4, 13), (0, 9), (1.4, 13), (1.4, 22), (7.6, 22), (7.6, 15),
                (10.4, 11), (10.4, 26.4), (-10.4, 26.4)]
        return icon([B("rect", (-1.4, 26, 2.8, 19)), B("poly", head, True)], emblem=(0, 30.6))
    if name == "atom":
        orbits = [(arc_pts(0, CY, 14, 5, 0, TAU, 36, rot=a), .8) for a in (0, math.pi / 3, -math.pi / 3)]
        return icon([B("circle", (0, CY, 4.8), True)], lines=orbits, emblem=(0, CY))
    if name == "anchor":
        return icon([B("circle", (0, 14.4, 4.4), True)],
                    lines=[([(0, 18.6), (0, 42)], 2.2), ([(-7.4, 23.6), (7.4, 23.6)], 1.6),
                           (arc_pts(0, 30, 12, 12, math.pi * .1, math.pi * .9, 20), 2.2)],
                    solid=[("poly", [(-12.6, 29), (-14.6, 37), (-8.6, 35)]), ("poly", [(12.6, 29), (14.6, 37), (8.6, 35)])],
                    emblem=(0, 14.4))
    if name == "cog":
        teeth = []
        for k in range(8):
            a = k * TAU / 8
            for da, r in ((-.24, 10.4), (-.16, 13.6), (.16, 13.6), (.24, 10.4)):
                teeth.append((r * math.cos(a + da), CY + r * math.sin(a + da)))
        return icon([B("poly", _r(teeth), True)], solid=[ring(0, CY, 5.4, 3.6)], emblem=(0, CY))
    # laurel
    leaves = []
    for s in (-1, 1):
        for k in range(6):
            a = math.pi / 2 + s * (.55 + k * .36)
            leaves.append(("ellipse", (round(13 * math.cos(a), 2), round(CY + 2 + 13 * math.sin(a), 2), 1.4, 3, round(a, 2))))
    return icon([B("circle", (0, CY, 7), True)], solid=leaves, emblem=(0, CY))


# ---------- weather ----------

def _cloud(dy=0.0):
    return union_poly([("circle", -6, 24 + dy, 5.6), ("circle", 1, 19.6 + dy, 7.2), ("circle", 7.6, 24.6 + dy, 4.8),
                       ("rect", -11.6, 24.4 + dy, 23.2, 6.6)], 0, 25 + dy)


def band(cx, cy, r1, r2, n=24):
    """Upper half annulus between radii r1 > r2."""
    return arc_pts(cx, cy, r1, r1, math.pi, TAU, n) + arc_pts(cx, cy, r2, r2, TAU, math.pi, n)


def _weather(name):
    if name == "sun":
        rays = [([(10.6 * math.cos(a), CY + 10.6 * math.sin(a)), (15.4 * math.cos(a), CY + 15.4 * math.sin(a))], 1.8)
                for a in [k * TAU / 8 + math.pi / 8 for k in range(8)]]
        return icon([B("circle", (0, CY, 8.4), True)], lines=rays)
    if name == "rain cloud":
        return icon([B("poly", _cloud(), True)], solid=[("poly", drop(x, y, 1.7)) for x, y in ((-6, 39), (0, 43), (6, 39))],
                    emblem=(1, 25.4))
    if name == "thunderstorm":
        return icon([B("poly", _cloud(), True)],
                    solid=[("poly", [(1.4, 31), (-4.4, 39.4), (-.6, 39.4), (-2.6, 46.6), (4.6, 36.6), (1, 36.6), (3.8, 31)])],
                    emblem=(1, 25.4))
    if name == "snowflake":
        arms = []
        for k in range(6):
            a = k * TAU / 6 - math.pi / 2
            ux, uy = math.cos(a), math.sin(a)
            arms.append(([(4 * ux, CY + 4 * uy), (14 * ux, CY + 14 * uy)], 1.8))
            for s in (-1, 1):
                b = a + s * .7
                arms.append(([(9.4 * ux, CY + 9.4 * uy), (9.4 * ux + 4 * math.cos(b), CY + 9.4 * uy + 4 * math.sin(b))], 1.2))
        return icon([B("poly", reg(6, 5.6, rot=0), True)], lines=arms)
    if name == "rainbow":
        return icon([B("poly", band(0, 37, 15.4, 12.4), True), B("poly", band(0, 37, 9.6, 7), True),
                     B("ellipse", (-11.6, 37.6, 5, 3, 0)), B("ellipse", (11.6, 37.6, 5, 3, 0))],
                    solid=[("poly", band(0, 37, 12.4, 9.6))], emblem=(0, 34))
    if name == "tornado":
        rings = [(0, 13.6, 13.4, 2.8), (1.4, 19.6, 10.4, 2.6), (2.6, 25.4, 7.8, 2.4), (3, 31, 5.6, 2.1), (2.4, 36.4, 3.8, 1.8),
                 (1, 41.4, 2.4, 1.4)]
        return icon([B("ellipse", (x, y, rx, ry, 0), True) for x, y, rx, ry in rings], emblem=(2.6, 25.4))
    if name == "umbrella":
        canopy = arc_pts(0, 26, 14, 12.6, math.pi, TAU, 24)
        for k in range(4):
            x1 = 14 - k * 7
            canopy += arc_pts(x1 - 3.5, 26, 3.5, 1.8, 0, -math.pi, 8)[1:]
        return icon([B("poly", canopy, True)],
                    lines=[([(0, 26), (0, 40.4)], 1.2), (arc_pts(2.6, 40.4, 2.6, 2.6, math.pi, 0, 10, ), 1.2), ([(0, 13.4), (0, 10)], 1.2)],
                    emblem=(0, 19.6))
    if name == "thermometer":
        return icon([B("rr", (-3.2, 8, 6.4, 30, 3.2)), B("circle", (0, 38, 5.8), True)],
                    solid=[("rect", (-1.3, 18, 2.6, 18))],
                    front=[([(3.2, y), (5.6, y)], .6) for y in (12, 16, 20, 24, 28)], emblem=(0, 38))
    if name == "windsock":
        return icon([B("poly", [(-11, 12.6), (13.6, 17.6), (13.6, 22.4), (-11, 26.4)], True)],
                    solid=[("poly", [(-3.4, 14.2), (1.6, 15.2), (1.6, 24.6), (-3.4, 25.2)]), ("poly", [(6.6, 16.2), (9.6, 16.8), (9.6, 23.2), (6.6, 23.6)])],
                    lines=[([(-12.4, 10), (-12.4, 46)], 1.4)],
                    front=[([(-6, 33), (9, 33)], .8), ([(-2, 37.6), (13, 37.6)], .8)], emblem=(-6.8, 19.6))
    # snowman
    return icon([B("circle", (0, 37, 8.6), True), B("circle", (0, 25, 6.2)), B("circle", (0, 15, 4.6))],
                solid=[("circle", (-1.6, 14, .7)), ("circle", (1.6, 14, .7)), ("poly", [(0, 15.4), (5.4, 16.6), (0, 17)]),
                       ("circle", (0, 23, .8)), ("circle", (0, 27, .8)), ("rect", (-5.4, 19.4, 10.8, 1.8))],
                lines=[([(-5.6, 24), (-13, 18), (-14.6, 15.4)], .8), ([(5.6, 24), (13, 18), (14.6, 15.4)], .8)], emblem=(0, 38))


# ---------- space ----------

def _space(name):
    if name == "ringed planet":
        return icon([B("circle", (0, CY, 9.2), True)],
                    lines=[(arc_pts(0, CY, 16, 4.4, math.pi, TAU, 24, rot=-.3), 1.6)],
                    front=[(arc_pts(0, CY, 16, 4.4, 0, math.pi, 24, rot=-.3), 1.6)], emblem=(-2.6, 24))
    if name == "crescent moon":
        outer = arc_pts(1, CY, 14, 14, math.pi * .3, math.pi * 1.7, 30)
        inner = arc_pts(7.4, CY - 1, 11, 11, math.pi * 1.47, math.pi * .53, 30)
        return icon([B("poly", outer + inner, True)],
                    solid=[("circle", (-6, 18.4, 1.5)), ("circle", (-10.4, 33, 1.2)), ("circle", (-4.6, 39.6, 1)),
                           ("poly", star(4, 3.4, 1, 10, 16))], emblem=(-9, 26.6))
    if name == "comet":
        return icon([B("poly", [(2, 16.6), (-14.6, 43), (9.6, 23.4)]), B("circle", (6, 19.6, 5.6), True)],
                    front=[([(-1, 27.6), (-9.6, 38.4)], .5), ([(3, 28.4), (-5, 41)], .5)], emblem=(6, 19.6))
    if name == "spiral galaxy":
        arms = []
        for s in (0, math.pi):
            pts = [(3.2 * math.cos(s + t) * (1 + .55 * t), CY + 2.2 * math.sin(s + t) * (1 + .55 * t)) for t in
                   [k * .2 for k in range(40)]]
            arms.append((_r(pts), 2))
        return icon([B("ellipse", (0, CY, 5.4, 3.8, -.3), True)], lines=arms, emblem=(0, CY))
    if name == "astronaut helmet":
        return icon([B("circle", (0, 25.4, 12.2)), B("ellipse", (0, 25.4, 8.6, 6.6, 0), True)],
                    solid=[("rr", (-8.6, 37, 17.2, 3.4, 1.6)), ("circle", (-11.4, 25.4, 1.4)), ("circle", (11.4, 25.4, 1.4))],
                    lines=[([(7, 15), (10, 9)], .8)], emblem=(0, 25.4))
    if name == "satellite":
        return icon([B("rect", (-15.4, 23.4, 10.2, 9.2), True), B("rect", (5.2, 23.4, 10.2, 9.2), True), B("rect", (-4, 21, 8, 14))],
                    solid=[("halfellipse", (0, 20.6, 4.4, 2.8))],
                    lines=[([(-5.2, 28), (5.2, 28)], .8), ([(0, 18), (0, 12.6)], .7)],
                    front=[([(-10.3, 23.4), (-10.3, 32.6)], .5), ([(10.3, 23.4), (10.3, 32.6)], .5)], emblem=(0, 29))
    if name == "telescope":
        return icon([B("poly", rot_rect(-11, 34, 11, 17, 6.4), True)],
                    solid=[("poly", rot_rect(-13.6, 36, -10.4, 33.6, 3.6)), ("poly", rot_rect(11, 17, 12.6, 15.8, 7.4))],
                    lines=[([(0, 26), (-8, 45)], 1), ([(0, 26), (0, 45)], 1), ([(0, 26), (8, 45)], 1)], emblem=(0, 25.6))
    if name == "constellation":
        pts = [(-12, 36), (-7, 20), (2, 26.6), (9, 13), (12.6, 31), (4.6, 41)]
        small = [B("poly", star(5, 2.6, 1.1, x, y)) for i, (x, y) in enumerate(pts) if i != 2]
        return icon(small + [B("poly", star(5, 7.6, 3.4, 2, 26.6), True)],
                    lines=[(pts[:3] + [pts[3]], .6), ([pts[2], pts[4], pts[5]], .6)], emblem=(2, 27.4))
    if name == "asteroid":
        rock = _r([(11.4 * (1 + .14 * math.sin(3 * a) + .09 * math.cos(5 * a)) * math.cos(a),
                    CY + 11.4 * (1 + .14 * math.sin(3 * a) + .09 * math.cos(5 * a)) * math.sin(a)) for a in [k * TAU / 48 for k in range(48)]])
        return icon([B("poly", rock, True)],
                    solid=[("ellipse", (-4, 23, 2.2, 1.6, 0)), ("ellipse", (5, 33, 1.6, 1.2, 0)), ("ellipse", (5, 21, 1.2, .9, 0)),
                           ("circle", (13.4, 13.4, 1.6)), ("circle", (-13, 41, 1.2))], emblem=(-2, 31))
    # lunar lander
    return icon([B("rect", (-8.4, 27.4, 16.8, 5)), B("poly", reg(6, 7.4, 0, 22, rot=0), True)],
                solid=[("rect", (-14.6, 41.6, 5, 1.6)), ("rect", (9.6, 41.6, 5, 1.6)), ("poly", [(-2.4, 32.4), (2.4, 32.4), (3.6, 37), (-3.6, 37)])],
                lines=[([(-6, 32), (-12, 42)], 1.1), ([(6, 32), (12, 42)], 1.1), ([(3, 15.6), (6, 10)], .7)], emblem=(0, 22))


KINDS = {"instrument": (INSTRUMENTS, _instrument), "computer": (COMPUTER, _computer),
         "shape": (SHAPES, _shape), "insignia": (INSIGNIA, _insignia), "weather": (WEATHER, _weather),
         "space": (SPACE, _space)}


@lru_cache(maxsize=None)
def icon_spec(kind: str, name: str) -> dict:
    return KINDS[kind][1](name)


def all_specs() -> dict:
    """Every icon at x = 0, for the browser lab."""
    return {kind: {n: icon_spec(kind, n) for n in names} for kind, (names, _) in KINDS.items()}


def _shift_args(kind, a, c):
    if kind == "poly":
        return [(x + c, y) for x, y in a]
    if kind == "multi":
        return [[(x + c, y) for x, y in pts] for pts in a]
    return (a[0] + c,) + tuple(a[1:])


def shifted(sp: dict, c: float) -> dict:
    out = {}
    if "text" in sp:  # a character subject: (char, x, baseline y, font size)
        ch, x, y, size = sp["text"]
        out["text"] = (ch, x + c, y, size)
    return out | dict(body=[(k, _shift_args(k, a, c), fab) for k, a, fab in sp["body"]],
                solid=[(k, _shift_args(k, a, c)) for k, a in sp["solid"]],
                lines=[([(x + c, y) for x, y in pts], w) for pts, w in sp["lines"]],
                front=[([(x + c, y) for x, y in pts], w) for pts, w in sp["front"]],
                emblem=(sp["emblem"][0] + c, sp["emblem"][1]))


# ================= 8-bit expansion: flags, holidays, game icons, tools, game pieces, road signs,
# clothing and characters =================

FLAGS = ("waving flag", "pennant", "swallowtail", "checkered flag", "pirate flag", "hanging banner", "signal flag",
         "cross flag", "star flag", "striped flag", "crossed flags", "golf flag", "bunting", "tattered flag", "disc flag",
         "summit flag")
HOLIDAYS = ("decorated tree", "jack-o-lantern", "gift", "easter egg", "candy cane", "ornament", "menorah", "fireworks",
            "birthday cake", "valentine heart", "shamrock", "paper lantern", "dreidel", "snow globe", "wreath", "jingle bells")
GAME_ICONS = ("bullet", "crosshair", "fire", "water", "lightning", "ice crystal", "leaf", "health pack", "potion", "coin",
              "key", "bomb", "sword", "buckler", "bow", "treasure chest")
TOOLS = ("hammer", "wrench", "screwdriver", "saw", "scissors", "paintbrush", "light bulb", "pliers", "axe", "magnet",
         "drill", "ruler")
PIECES = ("pawn", "rook", "knight", "bishop", "queen", "king", "die", "puzzle piece", "playing card", "domino", "meeple",
          "dartboard")
SIGNS = ("stop sign", "yield sign", "traffic light", "warning sign", "one-way sign", "railroad crossing", "no entry",
         "speed limit", "roundabout", "traffic cone", "parking sign", "curve ahead")
CLOTHING = ("t-shirt", "sneaker", "sunglasses", "mitten", "sock", "dress", "necktie", "boot", "trousers", "handbag",
            "wristwatch", "backpack")
CHAR_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CHARACTERS = tuple(("letter " if c.isalpha() else "digit ") + c for c in CHAR_ALPHABET)

POLE = [([(-11, 8), (-11, 46)], 1.4)]
FLAG_RECT = (-10, 10, 24, 18)


def _pole_flag(body, solid=(), front=(), emblem=(1, 19)):
    return icon(body, solid=[("circle", (-11, 7.4, 1.5))] + list(solid), lines=POLE, front=front, emblem=emblem)


def _flag(name):
    if name == "waving flag":
        top = [(-10 + k * 2, 10 + 1.4 * math.sin(k * .55)) for k in range(13)]
        bot = [(14 - k * 2, 28 + 1.4 * math.sin((12 - k) * .55)) for k in range(13)]
        return _pole_flag([B("poly", _r(top + bot), True)], emblem=(1, 19.6))
    if name == "pennant":
        return _pole_flag([B("poly", [(-10, 10), (15, 19), (-10, 28)], True)], emblem=(-3, 19))
    if name == "swallowtail":
        return _pole_flag([B("poly", [(-10, 10), (14, 10), (6.4, 19), (14, 28), (-10, 28)], True)], emblem=(-1, 19))
    if name == "checkered flag":
        checks = [("rect", (-10 + i * 6, 10 + j * 6, 6, 6)) for i in range(4) for j in range(3) if (i + j) % 2 == 0]
        return _pole_flag([B("rect", FLAG_RECT, True)], solid=checks, emblem=(5, 19))
    if name == "pirate flag":
        return _pole_flag([B("rect", FLAG_RECT, True)],
                          solid=[("poly", rot_rect(-4, 25.6, 6, 18.6, 1.6)), ("poly", rot_rect(6, 25.6, -4, 18.6, 1.6)),
                                 ("circle", (1, 16.4, 4)), ("rect", (-1.4, 18.6, 4.8, 3))], emblem=(1, 16.4))
    if name == "hanging banner":
        return icon([B("poly", [(-9, 9), (9, 9), (9, 42), (0, 35), (-9, 42)], True)], lines=[([(-13, 9), (13, 9)], 1.6)],
                    solid=[("circle", (-13, 9, 1.4)), ("circle", (13, 9, 1.4))], emblem=(0, 22))
    if name == "signal flag":
        return _pole_flag([B("poly", [(-10, 10), (14, 10), (-10, 28)], True), B("poly", [(14, 10), (14, 28), (-10, 28)])],
                          solid=[("poly", [(14, 12.4), (14, 28), (-6.8, 28)])], emblem=(-3, 16))
    if name == "cross flag":
        return _pole_flag([B("rect", FLAG_RECT, True)], solid=[("rect", (-3.4, 10, 3.8, 18)), ("rect", (-10, 17.1, 24, 3.8))],
                          emblem=(7, 23.6))
    if name == "star flag":
        return _pole_flag([B("rect", FLAG_RECT, True)], solid=[("poly", star(5, 7, 2.9, 2, 19.6))], emblem=(2, 20))
    if name == "striped flag":
        return _pole_flag([B("rect", FLAG_RECT, True)], solid=[("rect", (-10, y, 24, 2.6)) for y in (12.6, 17.7, 22.8)])
    if name == "crossed flags":
        return icon([B("poly", [(7.2, 11.4), (15.8, 9.4), (14.8, 18), (4.6, 17)], True), B("poly", [(-7.2, 11.4), (-15.8, 9.4), (-14.8, 18), (-4.6, 17)], True)],
                    lines=[([(-12, 45), (7.6, 10)], 1.3), ([(12, 45), (-7.6, 10)], 1.3)], emblem=(0, 27.4))
    if name == "golf flag":
        return icon([B("poly", [(0, 9), (13, 14), (0, 19.4)], True)], lines=[([(0, 8), (0, 42)], 1.1)],
                    solid=[("ellipse", (0, 42.6, 8, 2.2, 0)), ("circle", (-8, 39.8, 1.8))], emblem=(4.4, 14.2))
    if name == "bunting":
        tri = lambda x, y: [(x - 3, y), (x + 3, y), (x, y + 6.4)]
        body = []
        for y0 in (11, 27):
            for k, x in enumerate((-10.4, -3.6, 3.6, 10.4)):
                y = y0 + 3.2 * (1 - (x / 15) ** 2)
                body.append(B("poly", _r(tri(x, y)), k % 2 == 0))
        return icon(body, lines=[([(-15, y0), (0, y0 + 4), (15, y0)], .6) for y0 in (11, 27)], emblem=(-3.6, 34))
    if name == "tattered flag":
        edge = [(14, 10), (11, 12.6), (14.6, 15), (10.4, 18), (13.4, 21), (9.6, 23.6), (12.6, 26), (10, 28)]
        return _pole_flag([B("poly", [(-10, 10)] + edge + [(-10, 28)], True)], solid=[("circle", (4, 15, 1)), ("circle", (-2, 23.4, .8))],
                          emblem=(0, 19))
    if name == "disc flag":
        return _pole_flag([B("rect", FLAG_RECT, True)], solid=[("circle", (2, 19, 5.6))], emblem=(2, 19))
    # summit flag
    return icon([B("poly", [(-15.6, 44), (-2, 22), (3, 30), (7.6, 25), (16, 44)], True)],
                lines=[([(-2, 22), (-2, 8)], 1.2)], solid=[("poly", [(-2, 8), (9, 11.4), (-2, 15)])],
                front=[([(-6, 28.4), (-2, 31), (1, 28)], .6)], emblem=(1, 37))


def _holiday(name):
    if name == "decorated tree":
        tiers = [B("poly", [(-12, 38), (12, 38), (0, 25)], True), B("poly", [(-9.6, 30), (9.6, 30), (0, 17.6)], True),
                 B("poly", [(-7, 22.4), (7, 22.4), (0, 11.4)], True)]
        return icon(tiers, solid=[("rect", (-2, 38, 4, 5)), ("poly", star(5, 4.2, 1.8, 0, 10.4))] +
                    [("circle", (x, y, 1.3)) for x, y in ((-5, 35), (6, 33), (-3, 27.6), (4, 25.4), (1, 19.6))], emblem=(0, 31))
    if name == "jack-o-lantern":
        body = union_poly([("ellipse", -6, 30, 7, 10.6), ("ellipse", 6, 30, 7, 10.6), ("ellipse", 0, 29.6, 7.6, 11.6)], 0, 30)
        return icon([B("poly", body, True)],
                    solid=[("rect", (-1.4, 15, 2.8, 4.6)), ("poly", [(-7.6, 29), (-3, 29), (-5.3, 24.6)]), ("poly", [(3, 29), (7.6, 29), (5.3, 24.6)]),
                           ("poly", [(-8, 33), (8, 33), (6, 37.6), (3, 35.6), (0, 38), (-3, 35.6), (-6, 37.6)])], emblem=(0, 22.4))
    if name == "gift":
        return icon([B("rect", (-11, 24, 22, 18), True), B("rect", (-12.6, 19, 25.2, 5.6))],
                    solid=[("rect", (-1.7, 19, 3.4, 23)), ("ellipse", (-4, 16.6, 4, 2.2, -.4)), ("ellipse", (4, 16.6, 4, 2.2, .4))],
                    emblem=(-6, 33.4))
    if name == "easter egg":
        return icon([B("ellipse", (0, 29, 9.6, 13, 0), True)],
                    solid=[("poly", [(-9.4, 26), (-4.6, 23), (0, 26), (4.6, 23), (9.4, 26), (9.6, 29), (4.6, 26), (0, 29), (-4.6, 26), (-9.6, 29)])],
                    emblem=(0, 34))
    if name == "candy cane":
        stripes = [("poly", [(1.6, y), (6.6, y - 2.6), (6.6, y - 1), (1.6, y + 1.6)]) for y in (24, 30, 36, 42)]
        return icon([B("rect", (1.6, 16, 5, 28), True), B("poly", band(-1.4, 16, 8, 3), True), B("rect", (-9.4, 16, 5, 6), True)],
                    solid=stripes, emblem=(4.1, 33))
    if name == "ornament":
        return icon([B("circle", (0, 30, 11.4), True)],
                    solid=[("rect", (-3, 15.4, 6, 3.6)), ("poly", [(-11.2, 28), (-6, 26), (0, 28.6), (6, 26), (11.2, 28), (11.4, 30.6), (6, 28.6), (0, 31.2), (-6, 28.6), (-11.4, 30.6)])],
                    lines=[(arc_pts(0, 13.4, 2.2, 2.2, math.pi * 1.1, math.pi * 1.9, 8), .6)], emblem=(0, 36))
    if name == "menorah":
        arms = [(arc_pts(0, 21, r, r * .9, math.pi, 0, 14), 1.1) for r in (3.4, 6.8, 10.2, 13.6)]
        candles = [B("rect", (x - .8, 15.4 if x == 0 else 16.6, 1.6, 5.6 if x == 0 else 4.4)) for x in (-13.6, -10.2, -6.8, -3.4, 0, 3.4, 6.8, 10.2, 13.6)]
        return icon(candles + [B("poly", [(-8, 46), (8, 46), (3, 40.4), (-3, 40.4)], True)],
                    lines=arms + [([(0, 21), (0, 41)], 1.4)],
                    solid=[("ellipse", (x, 14.6 if x else 13.6, .8, 1.3, 0)) for x in (-13.6, -10.2, -6.8, -3.4, 0, 3.4, 6.8, 10.2, 13.6)],
                    emblem=(0, 43.4))
    if name == "fireworks":
        def burst(cx, cy, r0, r1, n):
            return [([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], 1.1)
                    for a in [k * TAU / n for k in range(n)]]
        return icon([B("circle", (0, 21, 3.4), True), B("circle", (-9, 36, 2), True), B("circle", (9.4, 36.6, 2), True)],
                    lines=burst(0, 21, 4.6, 12, 12) + burst(-9, 36, 3, 7, 8) + burst(9.4, 36.6, 3, 7, 8), emblem=(0, 21))
    if name == "birthday cake":
        return icon([B("rect", (-12, 32, 24, 10), True), B("rect", (-8, 23, 16, 9))],
                    solid=[("rr", (-14, 42, 28, 2.4, 1)), ("rect", (-4.8, 16, 1.6, 7)), ("rect", (-.8, 16, 1.6, 7)), ("rect", (3.2, 16, 1.6, 7)),
                           ("ellipse", (-4, 14, .8, 1.4, 0)), ("ellipse", (0, 14, .8, 1.4, 0)), ("ellipse", (4, 14, .8, 1.4, 0))],
                    front=[([(-8, 25), (-5, 27), (-2, 25), (1, 27), (4, 25), (8, 27)], .6)], emblem=(0, 37))
    if name == "valentine heart":
        return icon([B("poly", heart(0, 27.4, .7), True)],
                    solid=[("poly", [(13, 14.4), (15.8, 13), (14.4, 16)]), ("poly", [(-13, 39.6), (-15.8, 41), (-14.4, 38)])],
                    lines=[([(-14, 40.6), (-9, 36.6)], 1)], front=[([(9.6, 18.6), (14.4, 14.6)], 1)], emblem=(0, 28))
    if name == "shamrock":
        body = union_poly([("circle", 0, 19.6, 6.2), ("circle", -7.4, 29, 6.2), ("circle", 7.4, 29, 6.2), ("circle", 0, 27, 4)], 0, 26)
        return icon([B("poly", body, True)], lines=[([(0, 31), (2, 38), (5, 44)], 1.6)], emblem=(0, 26.4))
    if name == "paper lantern":
        return icon([B("ellipse", (0, 28, 10.6, 12, 0), True)],
                    solid=[("rr", (-5.4, 14, 10.8, 3, 1)), ("rr", (-5.4, 39, 10.8, 3, 1))],
                    lines=[([(0, 14), (0, 8)], .7), ([(0, 42), (0, 47)], .9)],
                    front=[(arc_pts(0, 28, 5.6, 12, -math.pi / 2, math.pi / 2, 14), .4), (arc_pts(0, 28, 5.6, 12, math.pi / 2, math.pi * 1.5, 14), .4)],
                    emblem=(0, 28))
    if name == "dreidel":
        return icon([B("poly", [(-8.4, 16), (8.4, 16), (8.4, 32), (0, 42), (-8.4, 32)], True)],
                    solid=[("rect", (-1.6, 9, 3.2, 7)), ("rect", (-8.4, 16, 16.8, 2))], emblem=(0, 27))
    if name == "snow globe":
        return icon([B("circle", (0, 23.6, 11.4), True)],
                    solid=[("poly", [(-10, 33.6), (10, 33.6), (12.6, 43.6), (-12.6, 43.6)]), ("poly", [(-3.6, 30), (3.6, 30), (0, 21)])] +
                    [("circle", (x, y, .8)) for x, y in ((-6, 18), (5, 16.6), (-2, 14.4), (7, 24), (-7.6, 26))], emblem=(0, 38.6))
    if name == "wreath":
        r = ring(0, 27, 13, 7.6)
        return icon([B(r[0], r[1], True)],
                    solid=[("poly", [(0, 38), (-6, 34.6), (-6, 42.4)]), ("poly", [(0, 38), (6, 34.6), (6, 42.4)])] +
                    [("circle", (10.3 * math.cos(a), 27 + 10.3 * math.sin(a), 1.2)) for a in (-2.4, -1.6, -.8, 0, 3.1)], emblem=(0, 27))
    # jingle bells
    def bell(cx, cy, rot):
        pts = arc_pts(0, -4, 4, 4, math.pi, TAU, 8)[1:-1] + [(4, -4), (5, 3), (8.4, 8)] + [(-8.4, 8), (-5, 3), (-4, -4)]
        return _r([(cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)) for x, y in pts])
    return icon([B("poly", bell(-6.4, 29, -.35), True), B("poly", bell(6.4, 29, .35), True)],
                solid=[("circle", (-3.2, 39, 2)), ("circle", (3.2, 39, 2)), ("ellipse", (-3, 16.6, 3.4, 2, -.5)), ("ellipse", (3, 16.6, 3.4, 2, .5))],
                emblem=(-6.4, 29))


def _game(name):
    if name == "bullet":
        return icon([B("rect", (-5, 24, 10, 16)), B("halfellipse", (0, 24, 5, 11), True)],
                    solid=[("rect", (-5.8, 40, 11.6, 2.6)), ("rect", (-5, 30, 10, 1.2))], emblem=(0, 35))
    if name == "crosshair":
        return icon([B("circle", (0, CY, 10.4), True)], solid=[ring(0, CY, 12.4, 10.4)],
                    front=[([(0, 11), (0, 21)], 1.6), ([(0, 35), (0, 45)], 1.6), ([(-17, CY), (-7, CY)], 1.6), ([(7, CY), (17, CY)], 1.6)])
    if name == "fire":
        flame = [(0, 9), (4, 16.4), (9, 21.6), (11.4, 30), (9.4, 38), (4, 43), (-4, 43), (-9.4, 38), (-11.4, 30), (-8.4, 22.6), (-5, 26), (-4, 17.6)]
        return icon([B("poly", flame, True)], solid=[("poly", [(0, 25), (3.4, 31), (4.4, 37), (0, 40.4), (-4.4, 37), (-3.4, 31.6)])], emblem=(0, 35.4))
    if name == "water":
        return icon([B("poly", drop(0, 33, 10.4), True)], front=[([(-6.6, 35), (-3.3, 33), (0, 35), (3.3, 33), (6.6, 35)], .9)], emblem=(0, 39))
    if name == "lightning":
        return icon([B("poly", [(3, 9), (-9.6, 30), (-1.4, 30), (-4.4, 46), (10, 24), (1.6, 24), (6.8, 9)], True)],
                    solid=[("poly", star(4, 2.6, .7, -11, 16)), ("poly", star(4, 2, .6, 11, 36))], emblem=(0, 27))
    if name == "ice crystal":
        shard = lambda cx, cy, w, h, rot: _r([(cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot))
                                             for x, y in ((0, -h), (w, -h * .6), (w, h * .7), (0, h), (-w, h * .7), (-w, -h * .6))])
        return icon([B("poly", shard(-7, 32, 2.6, 8, -.5)), B("poly", shard(7, 32, 2.6, 8, .5)), B("poly", shard(0, 26, 4.4, 16, 0), True)],
                    emblem=(0, 28))
    if name == "leaf":
        return icon([B("ellipse", (1, 25, 8.4, 14.6, .6), True)], lines=[([(-6.6, 36.6), (-12, 44)], 1.3)],
                    front=[([(-6.6, 36.6), (9, 13.6)], .7)] + [([(x, y), (x + dx, y - 5)], .5) for x, y, dx in ((-2.6, 30.6, -4), (1, 25.4, -4.4), (-2.6, 30.6, 5), (1, 25.4, 5.4))],
                    emblem=(3.4, 22))
    if name == "health pack":
        return icon([B("rr", (-12.6, 18, 25.2, 21, 3), True)],
                    solid=[("poly", [(-2, 21), (2, 21), (2, 26.6), (7.6, 26.6), (7.6, 30.6), (2, 30.6), (2, 36), (-2, 36), (-2, 30.6), (-7.6, 30.6),
                                     (-7.6, 26.6), (-2, 26.6)])],
                    lines=[(arc_pts(0, 18, 5, 4, math.pi, TAU, 10), 1.3)], emblem=(8.6, 35))
    if name == "potion":
        return icon([B("rect", (-2.6, 15, 5.2, 10)), B("circle", (0, 33, 9.4), True)],
                    solid=[("rr", (-3.6, 11, 7.2, 4.6, 1.2)), ("circle", (-3, 30, 1.1)), ("circle", (3.6, 35, .9))], emblem=(0, 36))
    if name == "coin":
        return icon([B("circle", (0, CY, 12.4), True)], solid=[ring(0, CY, 10, 8.6)])
    if name == "key":
        r = ring(-6, 19, 6.6, 3.2)
        teeth = [("rect", (x, y, 3.4, 2.2)) for x, y in ((4, 33), (7, 37))]
        return icon([B(r[0], r[1], True)], solid=[("poly", rot_rect(-2, 24, 11.4, 42, 3.2))] + teeth, emblem=(-6, 19))
    if name == "bomb":
        return icon([B("circle", (-1, 31, 10.6), True)],
                    solid=[("poly", rot_rect(4.4, 22.6, 7.4, 18.4, 4)), ("poly", star(4, 3.4, 1, 12.6, 9.6))],
                    lines=[([(7, 19), (8.4, 15), (11.6, 11.4)], .8)], emblem=(-1, 31))
    if name == "sword":
        return icon([B("poly", [(0, 7), (3, 11.6), (3, 34), (-3, 34), (-3, 11.6)], True)],
                    solid=[("rr", (-8.6, 34, 17.2, 2.8, 1.2)), ("rect", (-1.4, 36.8, 2.8, 7)), ("circle", (0, 45, 2.1))], emblem=(0, 23))
    if name == "buckler":
        return icon([B("circle", (0, CY, 13.4)), B("circle", (0, CY, 10.6), True)],
                    solid=[("circle", (12 * math.cos(a), CY + 12 * math.sin(a), .9)) for a in [k * TAU / 8 for k in range(8)]])
    if name == "bow":
        limb = arc_pts(-8, CY, 17, 17, -.95, .95, 20) + arc_pts(-8, CY, 14, 14, .95, -.95, 20)
        return icon([B("poly", limb, True)],
                    solid=[("poly", [(14.6, CY), (10, CY - 2.6), (10, CY + 2.6)])],
                    front=[([(1.8, 14), (1.8, 42)], .5), ([(-13, CY), (11, CY)], .9), ([(-13, CY), (-15.6, CY - 2.6)], .6), ([(-13, CY), (-15.6, CY + 2.6)], .6)],
                    emblem=(6.6, 22))
    # treasure chest
    return icon([B("rect", (-12.4, 27, 24.8, 15), True), B("poly", arc_pts(0, 27, 12.4, 8, math.pi, TAU, 16))],
                solid=[("rect", (-8.6, 19.4, 2.6, 22.6)), ("rect", (6, 19.4, 2.6, 22.6)), ("rr", (-2.6, 24.4, 5.2, 5.6, 1))], emblem=(0, 36))


def _tool(name):
    if name == "hammer":
        return icon([B("rect", (-1.8, 19, 3.6, 26)), B("poly", [(-12, 11), (7, 11), (12.6, 14), (7, 20), (-12, 20)], True)], emblem=(-4, 15.6))
    if name == "wrench":
        jaw = arc_pts(8, 15, 6.4, 6.4, .9, TAU - .9 + 1.6, 20) + arc_pts(8, 15, 3, 3, TAU - .9 + 1.6, .9, 10)
        r = ring(-9, 41, 4.4, 2.2)
        return icon([B("poly", rot_rect(-8, 38, 6, 19, 4.6), True)], solid=[("poly", jaw), r], emblem=(-1, 28.6))
    if name == "screwdriver":
        return icon([B("rr", (-3.8, 25, 7.6, 20, 3.2), True)], solid=[("rect", (-2.2, 21, 4.4, 4)), ("rect", (-1, 8.6, 2, 12.6)), ("rect", (-1.8, 8, 3.6, 1.6))],
                    front=[([(x, 28), (x, 42)], .4) for x in (-1.8, 1.8)], emblem=(0, 36))
    if name == "saw":
        teeth = [(10 - k * 2.3, 31.6 if k % 2 else 29.4) for k in range(11)]
        return icon([B("poly", [(-13.6, 21.6), (9, 15)] + teeth + [(-13.6, 29.4)], True), B("rr", (8, 12, 7.4, 20, 3))],
                    solid=[("rr", (10.2, 16, 3, 10, 1.4))], emblem=(-3, 24))
    if name == "scissors":
        return icon([B("poly", rot_rect(-3.6, 35, 6, 9, 3.4), True), B("poly", rot_rect(3.6, 35, -6, 9, 3.4), True)],
                    solid=[ring(-5.6, 39.6, 4.8, 2.6), ring(5.6, 39.6, 4.8, 2.6)], emblem=(0, 25.6))
    if name == "paintbrush":
        return icon([B("poly", rot_rect(-10, 45, 0.6, 27, 3.6)), B("poly", [(0, 24), (4.6, 26.6), (11.6, 13), (6.4, 9)], True)],
                    solid=[("poly", rot_rect(0, 27.6, 2.6, 23, 5.4))], emblem=(5.6, 17.6))
    if name == "light bulb":
        return icon([B("poly", [(-5, 29), (5, 29), (4, 36), (-4, 36)]), B("circle", (0, 22, 10.4), True)],
                    solid=[("rr", (-4.4, 36, 8.8, 2, .8)), ("rr", (-4, 38.6, 8, 2, .8)), ("rr", (-2.4, 41.2, 4.8, 2, .8))],
                    front=[([(-3, 30), (-3, 25), (-1.5, 23), (0, 25), (1.5, 23), (3, 25), (3, 30)], .5)], emblem=(0, 18))
    if name == "pliers":
        return icon([B("poly", rot_rect(-1.6, 28, -8, 45, 3.6), True), B("poly", rot_rect(1.6, 28, 8, 45, 3.6), True), B("circle", (0, 27, 2.8))],
                    solid=[("poly", [(-.6, 27), (-3.4, 13), (-1, 10.6), (1.2, 26)]), ("poly", [(.6, 27), (3.4, 13), (1, 10.6), (-1.2, 26)])],
                    emblem=(0, 27))
    if name == "axe":
        return icon([B("poly", rot_rect(-6, 45, 3.4, 10, 3.2)), B("poly", [(1.6, 11.4), (12.6, 7), (15.4, 22.6), (4, 20.6)], True)], emblem=(8.4, 15))
    if name == "magnet":
        u = [(-12.4, 10), (-12.4, 24)] + arc_pts(0, 24, 12.4, 12.4, math.pi, 0, 20)[1:-1] + [(12.4, 24), (12.4, 10), (5.6, 10), (5.6, 24)] + \
            arc_pts(0, 24, 5.6, 5.6, 0, math.pi, 12)[1:-1] + [(-5.6, 24), (-5.6, 10)]
        return icon([B("poly", u, True)], solid=[("rect", (-12.4, 10, 6.8, 5)), ("rect", (5.6, 10, 6.8, 5))],
                    lines=[([(-9, 7), (-9, 3)], .6), ([(9, 7), (9, 3)], .6)], emblem=(0, 33))
    if name == "drill":
        return icon([B("poly", [(-12.6, 15), (6, 15), (6, 26.6), (-1.6, 26.6), (-1.6, 40), (-8.6, 40), (-10, 26.6), (-12.6, 26.6)], True)],
                    solid=[("rect", (6, 17.4, 4.4, 7)), ("rr", (-11, 39, 11, 5, 1.4))], lines=[([(10, 21), (16.4, 21)], 1.4)], emblem=(-4, 21))
    # ruler
    ticks = []
    for k in range(13):
        t_ = -12 + k * 2
        x0, y0 = t_ * .87, CY - t_ * .5 - 4.4 * .87
        L = 3 if k % 2 == 0 else 1.6
        ticks.append(([(round(x0, 2), round(y0, 2)), (round(x0 + .5 * L, 2), round(y0 + .87 * L, 2))], .45))
    return icon([B("poly", rot_rect(-14, CY + 7, 14, CY - 7, 8.8), True)], front=ticks, emblem=(2, 29))


def _piece(name):
    base = [("rr", (-9.6, 40, 19.2, 4.4, 1.6))]
    if name == "pawn":
        return icon([B("poly", [(-3, 23), (3, 23), (7.4, 40), (-7.4, 40)], True), B("circle", (0, 17.6, 5.4))],
                    solid=base + [("rr", (-5.4, 22.4, 10.8, 2.4, 1))], emblem=(0, 33))
    if name == "rook":
        top = [(-8, 10), (-5, 10), (-5, 13), (-1.6, 13), (-1.6, 10), (1.6, 10), (1.6, 13), (5, 13), (5, 10), (8, 10), (8, 17), (5, 19.6),
               (6.4, 40), (-6.4, 40), (-5, 19.6), (-8, 17)]
        return icon([B("poly", top, True)], solid=base + [("rect", (-5.4, 19.6, 10.8, 1.6))], emblem=(0, 30))
    if name == "knight":
        horse = [(-7, 40), (-6, 30), (-9.6, 24), (-8.4, 18), (-3, 12), (1, 8.6), (3, 12), (9, 17), (10.4, 22.6), (7, 23.6), (4, 20.6),
                 (3, 24.6), (6.6, 31), (7.4, 40)]
        return icon([B("poly", horse, True)], solid=base + [("circle", (1, 15.4, 1.1))], front=[([(-3, 13), (-7, 18), (-7.4, 24)], .6)],
                    emblem=(0, 33))
    if name == "bishop":
        return icon([B("poly", [(-3, 28), (3, 28), (7.4, 40), (-7.4, 40)]), B("ellipse", (0, 20, 6, 9, 0), True)],
                    solid=base + [("circle", (0, 9.6, 1.9)), ("rr", (-5.4, 27.6, 10.8, 2.4, 1))], front=[([(-2.6, 17), (2.6, 21.6)], .7)],
                    emblem=(0, 22))
    if name == "queen":
        crown = [(-8.6, 11), (-5, 18), (-2.6, 10), (0, 17), (2.6, 10), (5, 18), (8.6, 11), (6.4, 24), (-6.4, 24)]
        return icon([B("poly", [(-5, 24), (5, 24), (8, 40), (-8, 40)]), B("poly", crown, True)],
                    solid=base + [("circle", (x, y, 1.3)) for x, y in ((-8.6, 10.4), (-2.6, 9.4), (2.6, 9.4), (8.6, 10.4))] + [("rr", (-6.6, 23.4, 13.2, 2.4, 1))],
                    emblem=(0, 32))
    if name == "king":
        return icon([B("poly", [(-5, 24), (5, 24), (8, 40), (-8, 40)]), B("poly", [(-7.6, 14), (7.6, 14), (6.4, 24), (-6.4, 24)], True)],
                    solid=base + [("rect", (-1.2, 5, 2.4, 9)), ("rect", (-3.8, 7.6, 7.6, 2.4)), ("rr", (-6.6, 23.4, 13.2, 2.4, 1))], emblem=(0, 32))
    if name == "die":
        pips = [("circle", (x, y, 1.3)) for x, y in ((-9, 25), (-4, 33), (-9, 34.6), (-4, 23.4), (-6.5, 29))] + \
               [("ellipse", (0, 18, 2.2, 1.2, 0))] + [("circle", (x, y, 1.2)) for x, y in ((4.4, 34), (9.2, 25))]
        return icon([B("poly", [(0, 12), (13, 18.4), (0, 24.8), (-13, 18.4)]), B("poly", [(-13, 18.4), (0, 24.8), (0, 43), (-13, 36.6)], True),
                     B("poly", [(13, 18.4), (0, 24.8), (0, 43), (13, 36.6)])], solid=pips, emblem=(6.6, 30.6))
    if name == "puzzle piece":
        body = union_poly([("rect", -10, 18, 20, 20), ("circle", 0, 15.4, 4.4), ("circle", 12.6, 28, 4.4)], 0, 28)
        return icon([B("poly", body, True)], emblem=(-1, 29))
    if name == "playing card":
        h = heart(0, 0, .42)
        spade = _r([(x, 30.6 - y) for x, y in h])
        return icon([B("rr", (-9.6, 11, 19.2, 32, 2.2), True)], solid=[("poly", spade), ("poly", [(0, 31), (2.4, 37), (-2.4, 37)])],
                    emblem=(5.4, 15.4))
    if name == "domino":
        pips = [("circle", (x, y, 1.3)) for x, y in ((-3.4, 14.6), (0, 19), (3.4, 23.4), (-3.4, 32.4), (3.4, 32.4), (-3.4, 40.8), (3.4, 40.8))]
        return icon([B("rr", (-7.6, 10, 15.2, 36, 2.4), True)], solid=[("rect", (-6.4, 27.4, 12.8, 1.4))] + pips, emblem=(0, 36.6))
    if name == "meeple":
        m = [(0, 9), (4, 11), (5.4, 16.4), (3.6, 20), (12.4, 23), (13.4, 27.6), (6, 28.6), (8.4, 43), (2, 43), (0, 36), (-2, 43), (-8.4, 43),
             (-6, 28.6), (-13.4, 27.6), (-12.4, 23), (-3.6, 20), (-5.4, 16.4), (-4, 11)]
        return icon([B("poly", m, True)], emblem=(0, 27))
    # dartboard
    r = ring(0, CY, 10.6, 7.4)
    return icon([B("circle", (0, CY, 13.2)), B(r[0], r[1], True), B("circle", (0, CY, 4.6))],
                solid=[("circle", (0, CY, 1.6)), ("poly", [(11.6, 14), (15.6, 12), (13.6, 16.6)])],
                lines=[([(1.6, 26.4), (12.4, 15.4)], 1)], emblem=(-6.4, 34.6))


def _sign(name):
    post = [([(0, 30), (0, 47)], 1.6)]
    if name == "stop sign":
        return icon([B("poly", reg(8, 12.4, 0, 22, rot=math.pi / 8), True)], lines=post,
                    front=[(reg(8, 10.4, 0, 22, rot=math.pi / 8) + [reg(8, 10.4, 0, 22, rot=math.pi / 8)[0]], .6)], emblem=(0, 22))
    if name == "yield sign":
        return icon([B("poly", [(-13.6, 11), (13.6, 11), (0, 34)], True)], lines=[([(0, 34), (0, 47)], 1.6)],
                    front=[([(-9.6, 13.4), (9.6, 13.4), (0, 29.6), (-9.6, 13.4)], .6)], emblem=(0, 19))
    if name == "traffic light":
        return icon([B("rr", (-6.6, 8, 13.2, 31, 2.6)), B("circle", (0, 24, 3.6), True), B("circle", (0, 33, 3.6))],
                    solid=[("circle", (0, 15, 3.6)), ("rect", (-9, 12, 2.4, 1.2)), ("rect", (6.6, 12, 2.4, 1.2))],
                    lines=[([(0, 39), (0, 47)], 1.6)], emblem=(0, 33))
    if name == "warning sign":
        return icon([B("poly", reg(3, 15.4, 0, 27), True)], lines=[([(0, 34.6), (0, 47)], 1.6)],
                    solid=[("rect", (-1.5, 16.6, 3, 9.4)), ("circle", (0, 29.6, 1.7))], emblem=(7.6, 30.4))
    if name == "one-way sign":
        return icon([B("rect", (-14.4, 15, 28.8, 11), True)], lines=post,
                    solid=[("poly", [(-4, 18.6), (5, 18.6), (5, 16.6), (12, 20.5), (5, 24.4), (5, 22.4), (-4, 22.4)])], emblem=(-9, 20.5))
    if name == "railroad crossing":
        return icon([B("poly", rot_rect(-12, 30, 12, 10, 4.6), True), B("poly", rot_rect(12, 30, -12, 10, 4.6), True)], lines=[([(0, 20), (0, 47)], 1.6)],
                    emblem=(0, 20))
    if name == "no entry":
        return icon([B("circle", (0, 22, 12.4), True)], lines=post, solid=[("rr", (-8.4, 20, 16.8, 4, 1.2))], emblem=(0, 29.6))
    if name == "speed limit":
        return icon([B("rr", (-10.4, 9, 20.8, 26, 2.4)), B("circle", (0, 22, 6.8), True)], lines=[([(0, 35), (0, 47)], 1.6)],
                    solid=[ring(0, 22, 8.6, 6.8)], emblem=(0, 22))
    if name == "roundabout":
        arrows = [(arc_pts(0, 22, 6.4, 6.4, a, a + 1.6, 10), 1.6) for a in (0, TAU / 3, 2 * TAU / 3)]
        heads = []
        for a in (1.6, 1.6 + TAU / 3, 1.6 + 2 * TAU / 3):
            x, y = 6.4 * math.cos(a), 22 + 6.4 * math.sin(a)
            tx, ty = -math.sin(a), math.cos(a)
            heads.append(("poly", _r([(x + 2.4 * tx, y + 2.4 * ty), (x - 2.2 * math.cos(a), y - 2.2 * math.sin(a)), (x + 2.2 * math.cos(a), y + 2.2 * math.sin(a))])))
        return icon([B("circle", (0, 22, 12.4), True)], lines=post, solid=heads, front=arrows, emblem=(0, 22))
    if name == "traffic cone":
        return icon([B("poly", [(-3, 10), (3, 10), (9.4, 40), (-9.4, 40)], True)],
                    solid=[("poly", [(-4.4, 17), (4.4, 17), (5.2, 21), (-5.2, 21)]), ("poly", [(-6.2, 26), (6.2, 26), (7, 30), (-7, 30)]),
                           ("rr", (-12.6, 40, 25.2, 3.6, 1))], emblem=(0, 35))
    if name == "parking sign":
        p = [(-4, 15), (2, 15), (6, 17.6), (6, 22.4), (2, 25), (-.6, 25), (-.6, 29.6), (-4, 29.6)]
        hole = [(-.6, 18.4), (-.6, 21.6), (2, 21.6), (2.8, 20.8), (2.8, 19.2), (2, 18.4)]
        return icon([B("rr", (-11, 11, 22, 22, 3), True)], lines=[([(0, 33), (0, 47)], 1.6)], solid=[("multi", [p, hole])], emblem=(6.4, 28.6))
    # curve ahead
    return icon([B("poly", [(0, 8), (14, 22), (0, 36), (-14, 22)], True)], lines=[([(0, 36), (0, 47)], 1.6)],
                front=[([(-3, 31), (-3, 24), (1, 19), (1, 16)], 1.8)], solid=[("poly", [(1, 12.4), (4.4, 17), (-2.4, 17)])], emblem=(-6, 22))


def _clothing(name):
    if name == "t-shirt":
        shirt = [(-5, 12), (-13, 16), (-16.4, 24), (-11, 26.4), (-10, 22.6), (-10, 42), (10, 42), (10, 22.6), (11, 26.4), (16.4, 24),
                 (13, 16), (5, 12), (3, 14.4), (0, 15.2), (-3, 14.4)]
        return icon([B("poly", shirt, True)], emblem=(0, 25))
    if name == "sneaker":
        shoe = [(-14.4, 37), (-14.4, 21), (-9.4, 20), (-7, 25), (-2, 25.6), (0, 21.4), (3.4, 22.4), (6.4, 27), (11.4, 29.4), (14.6, 33),
                (14.6, 37)]
        return icon([B("poly", shoe, True)], solid=[("rr", (-15, 36.4, 30.2, 3.8, 1.4))],
                    front=[([(0, 24.6), (2.4, 27.6)], .7), ([(2.4, 24), (4.8, 27.4)], .7), ([(-7, 25), (6.4, 27)], .5)], emblem=(-9.6, 31))
    if name == "sunglasses":
        return icon([B("ellipse", (-7, 27, 6.4, 4.8, 0), True), B("ellipse", (7, 27, 6.4, 4.8, 0), True)],
                    lines=[([(-13.4, 25), (-16, 22)], 1), ([(13.4, 25), (16, 22)], 1)], front=[([(-1, 25.6), (0, 24.6), (1, 25.6)], 1)],
                    emblem=(-7, 27))
    if name == "mitten":
        mit = [(-8, 40), (-8, 21), (-6, 14), (0, 11), (6, 13), (8, 19.6), (8, 26), (12, 22), (14.4, 24), (9.4, 32.6), (8, 40)]
        return icon([B("poly", mit, True)], solid=[("rr", (-9, 37.4, 18, 6.4, 1.4))], emblem=(0, 24))
    if name == "sock":
        sock = [(-6, 10), (4.4, 10), (4.4, 30), (10, 33.6), (13.4, 38), (12.4, 43), (4, 44), (-3, 40.4), (-6, 34.4)]
        return icon([B("poly", sock, True)], solid=[("rect", (-6.6, 10, 11.6, 4.2)), ("poly", [(8, 41.6), (12.6, 40), (12.4, 43), (8.6, 43.6)])],
                    emblem=(-1, 24))
    if name == "dress":
        return icon([B("poly", [(-4, 10), (4, 10), (6, 16), (4, 22), (13.6, 44), (-13.6, 44), (-4, 22), (-6, 16)], True)],
                    solid=[("rect", (-4.8, 21, 9.6, 2.2))], emblem=(0, 34))
    if name == "necktie":
        return icon([B("poly", [(-2.6, 17.4), (2.6, 17.4), (5.4, 38), (0, 44), (-5.4, 38)], True)],
                    solid=[("poly", [(-3.4, 12.4), (3.4, 12.4), (2.6, 17.4), (-2.6, 17.4)])],
                    lines=[([(-11, 8), (-3.4, 12.4)], 1), ([(11, 8), (3.4, 12.4)], 1)], emblem=(0, 31))
    if name == "boot":
        return icon([B("poly", [(-8.4, 10), (4, 10), (4, 31.6), (12, 34.6), (14.4, 39.6), (14.4, 42.6), (-8.4, 42.6)], True)],
                    solid=[("rr", (-9, 42, 24, 3.4, 1.2)), ("rect", (-9, 10, 13.6, 3))],
                    front=[([(-4, 17), (1, 17)], .6), ([(-4, 21), (1, 21)], .6), ([(-4, 25), (1, 25)], .6)], emblem=(-2, 33))
    if name == "trousers":
        return icon([B("poly", [(-10, 13), (10, 13), (12.4, 44), (3, 44), (0, 22), (-3, 44), (-12.4, 44)], True)],
                    solid=[("rect", (-10, 10, 20, 3.4))], front=[([(0, 13.4), (0, 21)], .6)], emblem=(-6.6, 31))
    if name == "handbag":
        return icon([B("poly", [(-12, 22.4), (12, 22.4), (14.4, 42), (-14.4, 42)], True)],
                    lines=[(arc_pts(0, 22.4, 8, 10, math.pi, TAU, 16), 1.6)], solid=[("rr", (-2.6, 21, 5.2, 4, 1))], emblem=(0, 33))
    if name == "wristwatch":
        return icon([B("rr", (-4.6, 8, 9.2, 40, 2.2)), B("circle", (0, CY, 8.2), True)], solid=[ring(0, CY, 9, 7.6)],
                    front=[([(0, CY), (0, CY - 5.6)], .8), ([(0, CY), (3.6, CY + 1.6)], .8)], emblem=(0, 42))
    # backpack
    return icon([B("rr", (-10.4, 14, 20.8, 30.4, 5.4), True), B("rr", (-7.4, 30, 14.8, 11, 2.4))],
                lines=[(arc_pts(0, 14.4, 5, 5, math.pi, TAU, 10), 1.6)], front=[([(-7.4, 34), (7.4, 34)], .5)], emblem=(0, 38))


def _character(name):
    ch = name.split()[-1]
    sp = icon([B("rr", (-11.4, 12, 22.8, 31, 4), True), B("rr", (-8.4, 15, 16.8, 25, 2.6))], emblem=(8.6, 40.4))
    sp["text"] = (ch, 0, 34.6, 21)
    return sp


KINDS.update({"flag": (FLAGS, _flag), "holiday": (HOLIDAYS, _holiday), "game": (GAME_ICONS, _game), "tool": (TOOLS, _tool),
              "piece": (PIECES, _piece), "sign": (SIGNS, _sign), "clothing": (CLOTHING, _clothing),
              "character": (CHARACTERS, _character)})
