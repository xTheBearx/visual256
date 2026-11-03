"""A small subset of the HTML canvas 2D API that records drawing as SVG.

The badge drawing code is written once against this API, the same way it is written against a
real canvas in the browser preview, so both draw the same geometry. Paths are transformed to
device coordinates as they are built (as a canvas does), arcs become cubic Béziers, text becomes
outlines, and canvas shadows become an SVG blur filter.
"""

from __future__ import annotations

import math
import re
from html import escape

from .fonts import OutlinePen, face

TAU = math.tau


def fmt(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


_RGBA = re.compile(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)")


def parse_color(c: str) -> tuple[str, float]:
    """Accept '#rrggbb' or 'rgba(r,g,b,a)'; return ('#rrggbb', alpha)."""
    c = c.strip()
    if c.startswith("#"):
        return c.upper(), 1.0
    m = _RGBA.fullmatch(c)
    if not m:
        raise ValueError(f"unsupported color {c!r}")
    r, g, b = (int(float(x)) for x in m.groups()[:3])
    a = float(m.group(4)) if m.group(4) is not None else 1.0
    return f"#{r:02X}{g:02X}{b:02X}", a


def _adjust_end(start: float, end: float, ccw: bool) -> float:
    # Same normalization browsers use for canvas arcs.
    if not ccw and end - start >= TAU:
        return start + TAU
    if ccw and start - end >= TAU:
        return start - TAU
    if not ccw and start > end:
        return start + (TAU - math.fmod(start - end, TAU))
    if ccw and start < end:
        return start - (TAU - math.fmod(end - start, TAU))
    return end


class LinearGradient:
    """Like canvas createLinearGradient: coordinates are read in the transform current at fill time."""

    def __init__(self, x0, y0, x1, y1, stops):
        self.x0, self.y0, self.x1, self.y1, self.stops = x0, y0, x1, y1, list(stops)


class RadialGradient:
    """Like canvas createRadialGradient with a shared center."""

    def __init__(self, cx, cy, r0, r1, stops):
        self.cx, self.cy, self.r0, self.r1, self.stops = cx, cy, r0, r1, list(stops)


_STATE_KEYS = ("fill_style", "stroke_style", "line_width", "line_cap", "line_join", "global_alpha",
               "shadow_color", "shadow_blur", "font_key", "font_size", "text_align", "text_baseline", "dash")


class Canvas:
    def __init__(self, width: float, height: float):
        self.width, self.height = width, height
        self._root: list = []
        self._stack: list[list] = [self._root]
        self._defs: list[str] = []
        self._filters: dict[tuple, str] = {}
        self._ids = 0
        self._saved: list[tuple] = []
        self.m = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        self.fill_style = "#000000"
        self.stroke_style = "#000000"
        self.line_width = 1.0
        self.line_cap = "butt"
        self.line_join = "miter"
        self.global_alpha = 1.0
        self.shadow_color = "#000000"
        self.shadow_blur = 0.0
        self.font_key = "mono"
        self.font_size = 10.0
        self.text_align = "left"
        self.text_baseline = "alphabetic"
        self.dash: tuple[float, ...] = ()
        self._d: list[str] = []
        self._has_point = False
        self._last = (0.0, 0.0)
        self._sub_start = (0.0, 0.0)

    # ---- state ----
    def save(self) -> None:
        self._saved.append((self.m, {k: getattr(self, k) for k in _STATE_KEYS}, len(self._stack)))

    def restore(self) -> None:
        if not self._saved:
            return
        self.m, values, depth = self._saved.pop()
        for k, v in values.items():
            setattr(self, k, v)
        del self._stack[depth:]

    def set_line_dash(self, dash) -> None:
        self.dash = tuple(dash)

    def set_font(self, key: str, size: float) -> None:
        self.font_key, self.font_size = key, size

    # ---- transforms ----
    def _mul(self, n) -> None:
        a, b, c, d, e, f = self.m
        a2, b2, c2, d2, e2, f2 = n
        self.m = (a * a2 + c * b2, b * a2 + d * b2, a * c2 + c * d2, b * c2 + d * d2,
                  a * e2 + c * f2 + e, b * e2 + d * f2 + f)

    def set_transform(self, a, b, c, d, e, f) -> None:
        self.m = (a, b, c, d, e, f)

    def translate(self, x, y) -> None:
        self._mul((1, 0, 0, 1, x, y))

    def scale(self, sx, sy=None) -> None:
        self._mul((sx, 0, 0, sx if sy is None else sy, 0, 0))

    def rotate(self, a) -> None:
        self._mul((math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0, 0))

    def _tp(self, x, y):
        a, b, c, d, e, f = self.m
        return a * x + c * y + e, b * x + d * y + f

    def _scale_factor(self) -> float:
        a, b, c, d, _, _ = self.m
        return math.sqrt(abs(a * d - b * c))

    # ---- paths ----
    def begin_path(self) -> None:
        self._d = []
        self._has_point = False

    def move_to(self, x, y) -> None:
        px, py = self._tp(x, y)
        self._d.append(f"M{fmt(px)} {fmt(py)}")
        self._has_point = True
        self._last = self._sub_start = (x, y)

    def line_to(self, x, y) -> None:
        if not self._has_point:
            return self.move_to(x, y)
        px, py = self._tp(x, y)
        self._d.append(f"L{fmt(px)} {fmt(py)}")
        self._last = (x, y)

    def quadratic_curve_to(self, cx, cy, x, y) -> None:
        if not self._has_point:
            self.move_to(cx, cy)
        p1, p2 = self._tp(cx, cy), self._tp(x, y)
        self._d.append(f"Q{fmt(p1[0])} {fmt(p1[1])} {fmt(p2[0])} {fmt(p2[1])}")
        self._last = (x, y)

    def bezier_curve_to(self, c1x, c1y, c2x, c2y, x, y) -> None:
        if not self._has_point:
            self.move_to(c1x, c1y)
        pts = [self._tp(c1x, c1y), self._tp(c2x, c2y), self._tp(x, y)]
        self._d.append("C" + " ".join(f"{fmt(p[0])} {fmt(p[1])}" for p in pts))
        self._last = (x, y)

    def close_path(self) -> None:
        if self._has_point:
            self._d.append("Z")
            self._last = self._sub_start

    def rect(self, x, y, w, h) -> None:
        self.move_to(x, y)
        self.line_to(x + w, y)
        self.line_to(x + w, y + h)
        self.line_to(x, y + h)
        self.close_path()

    def ellipse(self, cx, cy, rx, ry, rot, a0, a1, ccw=False) -> None:
        a1 = _adjust_end(a0, a1, ccw)
        cr, sr = math.cos(rot), math.sin(rot)

        def pt(t, dx=0.0, dy=0.0):
            ux, uy = math.cos(t) + dx, math.sin(t) + dy
            return cx + rx * ux * cr - ry * uy * sr, cy + rx * ux * sr + ry * uy * cr

        sx, sy = pt(a0)
        if self._has_point:
            self.line_to(sx, sy)
        else:
            self.move_to(sx, sy)
        sweep = a1 - a0
        n = max(1, int(math.ceil(abs(sweep) / (math.pi / 2) - 1e-9)))
        step = sweep / n
        k = 4 / 3 * math.tan(step / 4)
        t = a0
        for _ in range(n):
            t2 = t + step
            c1 = pt(t, -k * math.sin(t), k * math.cos(t))
            c2 = pt(t2, k * math.sin(t2), -k * math.cos(t2))
            self.bezier_curve_to(*c1, *c2, *pt(t2))
            t = t2

    def arc(self, cx, cy, r, a0, a1, ccw=False) -> None:
        self.ellipse(cx, cy, r, r, 0.0, a0, a1, ccw)

    # ---- painting ----
    def _filter_attr(self, alpha: float) -> str:
        if self.shadow_blur <= 0:
            return ""
        color, a = parse_color(self.shadow_color)
        std = round(self.shadow_blur / 2, 2)
        key = (color, a, std)
        if key not in self._filters:
            fid = f"g{len(self._filters)}"
            self._filters[key] = fid
            self._defs.append(
                f'<filter id="{fid}" filterUnits="userSpaceOnUse" x="0" y="0" width="{fmt(self.width)}" '
                f'height="{fmt(self.height)}" color-interpolation-filters="sRGB">'
                f'<feGaussianBlur in="SourceAlpha" stdDeviation="{fmt(std)}" result="b"/>'
                f'<feFlood flood-color="{color}" flood-opacity="{fmt(a)}"/>'
                f'<feComposite in2="b" operator="in" result="s"/>'
                f'<feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
        return f' filter="url(#{self._filters[key]})"'

    def _emit(self, s: str) -> None:
        self._stack[-1].append(s)

    def _gradient_ref(self, g) -> str:
        gid = f"lg{self._ids}"
        self._ids += 1
        stops = "".join(f'<stop offset="{fmt(o)}" stop-color="{parse_color(c)[0]}"'
                        + (f' stop-opacity="{fmt(parse_color(c)[1])}"' if parse_color(c)[1] < 0.999 else "") + "/>"
                        for o, c in g.stops)
        if isinstance(g, LinearGradient):
            (x0, y0), (x1, y1) = self._tp(g.x0, g.y0), self._tp(g.x1, g.y1)
            self._defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{fmt(x0)}" y1="{fmt(y0)}" '
                              f'x2="{fmt(x1)}" y2="{fmt(y1)}">{stops}</linearGradient>')
        else:
            cx, cy = self._tp(g.cx, g.cy)
            k = self._scale_factor()
            r0 = g.r0 / g.r1 if g.r1 else 0
            stops = "".join(f'<stop offset="{fmt(r0 + (1 - r0) * o)}" stop-color="{parse_color(c)[0]}"'
                            + (f' stop-opacity="{fmt(parse_color(c)[1])}"' if parse_color(c)[1] < 0.999 else "") + "/>"
                            for o, c in g.stops)
            self._defs.append(f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{fmt(cx)}" cy="{fmt(cy)}" '
                              f'r="{fmt(g.r1 * k)}">{stops}</radialGradient>')
        return f"url(#{gid})"

    def _paint_attrs(self, color, prefix: str) -> str:
        if isinstance(color, (LinearGradient, RadialGradient)):
            out = f' {prefix}="{self._gradient_ref(color)}"'
            if self.global_alpha < 0.999:
                out += f' {prefix}-opacity="{fmt(self.global_alpha)}"'
            return out
        hexc, a = parse_color(color)
        alpha = a * self.global_alpha
        out = f' {prefix}="{hexc}"'
        if alpha < 0.999:
            out += f' {prefix}-opacity="{fmt(alpha)}"'
        return out

    def fill(self, rule: str = "nonzero") -> None:
        if not self._d:
            return
        rule_attr = ' fill-rule="evenodd"' if rule == "evenodd" else ""
        self._emit(f'<path d="{"".join(self._d)}"{self._paint_attrs(self.fill_style, "fill")}{rule_attr}'
                   f'{self._filter_attr(1)}/>')

    def stroke(self) -> None:
        if not self._d:
            return
        k = self._scale_factor()
        attrs = (f' fill="none"{self._paint_attrs(self.stroke_style, "stroke")}'
                 f' stroke-width="{fmt(self.line_width * k)}"')
        if self.line_cap != "butt":
            attrs += f' stroke-linecap="{self.line_cap}"'
        if self.line_join != "miter":
            attrs += f' stroke-linejoin="{self.line_join}"'
        if self.dash:
            attrs += f' stroke-dasharray="{" ".join(fmt(max(v * k, 0.01)) for v in self.dash)}"'
        self._emit(f'<path d="{"".join(self._d)}"{attrs}{self._filter_attr(1)}/>')

    def clip(self) -> None:
        cid = f"c{self._ids}"
        self._ids += 1
        self._defs.append(f'<clipPath id="{cid}"><path d="{"".join(self._d)}"/></clipPath>')
        group: list = []
        self._emit((f'<g clip-path="url(#{cid})">', group))
        self._stack.append(group)

    def fill_rect(self, x, y, w, h) -> None:
        saved = (self._d, self._has_point, self._last, self._sub_start)
        self.begin_path()
        self.rect(x, y, w, h)
        self.fill()
        self._d, self._has_point, self._last, self._sub_start = saved

    def stroke_rect(self, x, y, w, h) -> None:
        saved = (self._d, self._has_point, self._last, self._sub_start)
        self.begin_path()
        self.rect(x, y, w, h)
        self.stroke()
        self._d, self._has_point, self._last, self._sub_start = saved

    # ---- text ----
    def measure_text(self, text: str) -> float:
        return face(self.font_key).measure(text, self.font_size)

    def fill_text(self, text: str, x: float, y: float) -> None:
        fc = face(self.font_key)
        size = self.font_size
        k = size / fc.upm
        width = fc.measure(text, size)
        if self.text_align == "center":
            x -= width / 2
        elif self.text_align in ("right", "end"):
            x -= width
        if self.text_baseline == "middle":
            y += (fc.ascent + fc.descent) / 2 * k
        elif self.text_baseline == "top":
            y += fc.ascent * k
        d: list[str] = []
        pen_x = x
        for ch in text:
            gx = pen_x

            def xf(p, gx=gx):
                return self._tp(gx + p[0] * k, y - p[1] * k)

            pen = OutlinePen(fc.glyphs, xf, fmt)
            fc.glyphs[fc.glyph_name(ch)].draw(pen)
            d.extend(pen.d)
            pen_x += fc.advance(ch) * k
        if d:
            self._emit(f'<path d="{"".join(d)}"{self._paint_attrs(self.fill_style, "fill")}{self._filter_attr(1)}/>')

    # ---- output ----
    def _serialize(self, items) -> list[str]:
        out = []
        for it in items:
            if isinstance(it, tuple):
                out.append(it[0])
                out.extend(self._serialize(it[1]))
                out.append("</g>")
            else:
                out.append(it)
        return out

    def to_svg(self, width: float | None = None, height: float | None = None, title: str | None = None) -> str:
        w = width if width is not None else self.width
        h = height if height is not None else self.height
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(self.width)} {fmt(self.height)}" '
                 f'width="{fmt(w)}" height="{fmt(h)}">']
        if title:
            parts.append(f"<title>{escape(title)}</title>")
        if self._defs:
            parts.append("<defs>" + "".join(self._defs) + "</defs>")
        parts.extend(self._serialize(self._root))
        parts.append("</svg>")
        return "".join(parts)
