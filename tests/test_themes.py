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


def test_every_palette_color_is_visible_on_its_background_and_gradients():
    for t in THEMES_LIST:
        assert len({c for _, c in t.palette}) == 16, t.id
        for bg in (t.bg, *(c for _, c in t.gradients)):
            for name, c in t.palette:
                assert contrast(c, bg) >= 2.0, f"{t.id}: {name} {c} is too faint on {bg}"


def test_two_gradient_partners_per_theme():
    for t in THEMES_LIST:
        assert len(t.gradients) == 2 and t.gradients[0][1] != t.gradients[1][1], t.id


def test_handle_text_is_readable():
    for t in THEMES_LIST:
        assert contrast(t.handle, t.bg) >= 7, t.id
        for _, c in t.gradients:
            assert contrast(t.handle, c) >= 4.5, t.id
