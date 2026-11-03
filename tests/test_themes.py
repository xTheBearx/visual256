from visual256.canvas import parse_color
from visual256.spec import THEME_IDS
from visual256.themes import THEMES_LIST, luminance


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def test_sixteen_themes_in_spec_order():
    assert tuple(t.id for t in THEMES_LIST) == THEME_IDS
    assert len(THEMES_LIST) == 16


def test_half_dark_half_light():
    dark = [t.id for t in THEMES_LIST if luminance(t.bg) < 0.2]
    assert len(dark) == 8


def test_backgrounds_are_distinct():
    for i, a in enumerate(THEMES_LIST):
        for b in THEMES_LIST[i + 1:]:
            assert a.bg != b.bg


def _over(bg: str, rgba: str) -> str:
    fg, a = parse_color(rgba)
    mix = [int(bg[i:i + 2], 16) * (1 - a) + int(fg[i:i + 2], 16) * a for i in (1, 3, 5)]
    return "#" + "".join(f"{round(v):02X}" for v in mix)


def test_every_palette_color_is_visible_on_its_background_and_gradients():
    for t in THEMES_LIST:
        assert len({c for _, c in t.palette}) == 16, t.id
        grounds = [t.bg, *(c for _, c in t.gradients)]
        for bg in grounds:
            for name, c in t.palette:
                assert contrast(c, bg) >= 2.0, f"{t.id}: {name} {c} is too faint on {bg}"
        for bg in grounds:
            streak = _over(bg, t.sheen)
            for name, c in t.palette:
                assert contrast(c, streak) >= 1.8, f"{t.id}: {name} {c} is too faint under the streak"


def test_eight_distinct_gradient_colors_per_theme():
    for t in THEMES_LIST:
        assert [n for n, _ in t.gradients] == ["red", "orange", "yellow", "green", "cyan", "blue", "violet", "magenta"]
        assert len({c for _, c in t.gradients}) == 8, t.id


def test_dark_themes_have_a_visible_streak():
    for t in THEMES_LIST:
        if luminance(t.bg) < 0.2:
            assert parse_color(t.sheen)[1] >= 0.15, t.id


def test_handle_text_is_readable():
    for t in THEMES_LIST:
        assert contrast(t.handle, t.bg) >= 7, t.id
        for _, c in t.gradients:
            assert contrast(t.handle, c) >= 4.5, t.id
            assert contrast(t.handle, _over(c, t.sheen)) >= 4.0, t.id


def test_light_to_dark_tones_are_readable():
    for t in THEMES_LIST:
        assert len(t.tones) == 8, t.id
        for light, dark in t.tones:
            assert luminance(light) > luminance(dark), t.id
            for c in (light, dark):
                for name, p in t.palette:
                    assert contrast(p, c) >= 2.0, f"{t.id}: {name} on tone {c}"
