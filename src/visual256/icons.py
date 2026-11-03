"""Geometry for the icon-style subjects: musical instruments, computer symbols, large basic shapes,
sci-fi insignia (an original set), weather symbols and space objects.

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
    return dict(body=[(k, _shift_args(k, a, c), fab) for k, a, fab in sp["body"]],
                solid=[(k, _shift_args(k, a, c)) for k, a in sp["solid"]],
                lines=[([(x + c, y) for x, y in pts], w) for pts, w in sp["lines"]],
                front=[([(x + c, y) for x, y in pts], w) for pts, w in sp["front"]],
                emblem=(sp["emblem"][0] + c, sp["emblem"][1]))
