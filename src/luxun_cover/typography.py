"""Title, author, subtitle. Hierarchy is size and position, not a fake bold.

Republican lead type was usually a Song/Ming face. Outlined covers trace a
face found on the machine (see fonts.py). Live ``<text>`` uses the stack below.
"""

from __future__ import annotations

from dataclasses import dataclass

from luxun_cover.geom import Box

# Live <text> only (--no-outline-text). Song/Ming first; gothic last.
# Quoted families must match fontconfig / the OS. serif is the final fallback.
FONT_FAMILY = ", ".join(
    [
        '"Songti SC"',
        '"Songti TC"',
        '"STSong"',
        '"SimSun"',
        '"Noto Serif CJK SC"',
        '"Noto Serif SC"',
        '"Source Han Serif SC"',
        '"Source Han Serif CN"',
        '"Source Han Serif"',
        '"AR PL UMing CN"',
        '"AR PL UMing TW"',
        '"PingFang SC"',
        '"Hiragino Mincho ProN"',
        '"Noto Sans CJK SC"',
        '"Noto Sans SC"',
        '"Source Han Sans SC"',
        '"Source Han Sans CN"',
        '"Microsoft YaHei"',
        '"WenQuanYi Zen Hei"',
        '"WenQuanYi Micro Hei"',
        '"Droid Sans Fallback"',
        "serif",
    ]
)

# Alphabetic baseline sits near the bottom of a CJK em box. Tuned for UMing / Song.
BASELINE = 0.88


@dataclass(frozen=True)
class Glyph:
    char: str
    x: float
    y_top: float
    size: float


@dataclass(frozen=True)
class Mark:
    """A short rule between title and the smaller lines. Accent when the palette has one."""

    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class TypeLayout:
    glyphs: tuple[Glyph, ...]
    marks: tuple[Mark, ...]
    box: Box


def em_of(char: str) -> float:
    if char.isspace():
        return 0.35
    if ord(char) < 128:
        return 0.56
    return 1.0


def _advance(size: float, tracking: float) -> float:
    return size * (1.0 + tracking)


def _stack_height(text: str, size: float, tracking: float) -> float:
    if not text:
        return 0.0
    return _advance(size, tracking) * (len(text) - 1) + size


def _run_width(text: str, size: float, tracking: float) -> float:
    if not text:
        return 0.0
    widths = [em_of(ch) * size for ch in text]
    gaps = tracking * size * (len(text) - 1)
    return sum(widths) + gaps


def vertical_tracking(n: int) -> float:
    if n <= 2:
        return 0.28
    if n <= 4:
        return 0.12
    return 0.06


def horizontal_tracking(n: int) -> float:
    if n <= 1:
        return 0.0
    if n == 2:
        return 0.62
    if n == 3:
        return 0.36
    if n <= 5:
        return 0.18
    return 0.06


def _preferred_vertical_size(n: int) -> float:
    table = {1: 100, 2: 84, 3: 70, 4: 60, 5: 52, 6: 46, 7: 42, 8: 38}
    return float(table.get(n, 34))


def _preferred_horizontal_size(n: int) -> float:
    table = {1: 76, 2: 64, 3: 54, 4: 46, 5: 40, 6: 36}
    return float(table.get(n, 32))


def plan_vertical(
    title: str,
    author: str,
    subtitle: str,
    *,
    col_right: float,
    y_top: float,
    avail_h: float,
    avail_w: float,
) -> TypeLayout:
    """Upper-right column. Author is smaller and shares the column's right edge."""
    size = min(_preferred_vertical_size(len(title)), avail_w)
    while size > 26:
        if _vertical_height(title, author, subtitle, size) <= avail_h:
            break
        size -= 2

    glyphs: list[Glyph] = []
    marks: list[Mark] = []
    y = y_top
    col_left = col_right - size

    y = _stack_vertical(glyphs, title, col_right, y, size, vertical_tracking(len(title)))

    if author or subtitle:
        gap = size * 0.34
        y += gap
        rule_w = size * 0.62
        marks.append(Mark(col_right - rule_w, y, rule_w, 3.0))
        y += 3.0 + size * 0.30

    if author:
        author_size = max(16.0, round(size * 0.34))
        y = _stack_vertical(
            glyphs, author, col_right, y, author_size, vertical_tracking(len(author))
        )
    if subtitle:
        if author:
            y += size * 0.22
        sub_size = max(14.0, round(size * 0.26))
        y = _stack_vertical(
            glyphs, subtitle, col_right, y, sub_size, vertical_tracking(len(subtitle))
        )

    box = Box(col_left, y_top, size, max(size, y - y_top))
    return TypeLayout(tuple(glyphs), tuple(marks), box)


def plan_horizontal(
    title: str,
    author: str,
    subtitle: str,
    *,
    center_x: float,
    bottom: float,
    avail_w: float,
    shift: float,
) -> TypeLayout:
    """Single-line title. Author sits under it, shifted right so the two don't stack symmetrically."""
    size = _preferred_horizontal_size(len(title))
    while size > 24:
        if _run_width(title, size, horizontal_tracking(len(title))) <= avail_w:
            break
        size -= 2

    title_w = _run_width(title, size, horizontal_tracking(len(title)))
    margin = center_x - avail_w / 2.0
    title_left = center_x - title_w / 2.0 + shift
    title_left = min(max(title_left, margin), margin + avail_w - title_w)

    author_size = max(16.0, round(size * 0.34)) if author else 0.0
    sub_size = max(14.0, round(size * 0.26)) if subtitle else 0.0
    author_track = 0.12
    sub_track = 0.08
    author_w = _run_width(author, author_size, author_track) if author else 0.0

    glyphs: list[Glyph] = []
    marks: list[Mark] = []
    y = 0.0
    _stack_horizontal(glyphs, title, title_left, y, size, horizontal_tracking(len(title)))
    y += size

    if author or subtitle:
        y += size * 0.28
        rule_w = min(title_w * 0.42, size * 1.3)
        # The rule aligns to the title's right side, not its center.
        marks.append(Mark(title_left + title_w - rule_w, y, rule_w, 3.0))
        y += 3.0 + size * 0.22

    # Author begins toward the right half of the title: 书名与著者不对称.
    author_left = title_left + title_w * 0.38
    if author and author_left + author_w > title_left + title_w + size * 0.4:
        author_left = title_left + title_w - author_w
    if author:
        _stack_horizontal(glyphs, author, author_left, y, author_size, author_track)
        y += author_size
    if subtitle:
        if author:
            y += size * 0.16
        sub_left = author_left if author else title_left + title_w * 0.38
        _stack_horizontal(glyphs, subtitle, sub_left, y, sub_size, sub_track)
        y += sub_size

    delta = bottom - y
    glyphs = [Glyph(g.char, g.x, g.y_top + delta, g.size) for g in glyphs]
    marks = [Mark(m.x, m.y + delta, m.w, m.h) for m in marks]
    left = min(g.x for g in glyphs)
    right = max(g.x + g.size * em_of(g.char) for g in glyphs)
    top = min(g.y_top for g in glyphs)
    return TypeLayout(tuple(glyphs), tuple(marks), Box(left, top, right - left, y))


def plan_between_rules(
    title: str,
    *,
    center_x: float,
    gap_top: float,
    gap_bottom: float,
    avail_w: float,
    shift: float,
) -> TypeLayout:
    """Title centered in a horizontal slot (the series-page double rule)."""
    size = _preferred_horizontal_size(len(title))
    slot_h = gap_bottom - gap_top
    size = min(size, slot_h * 0.62)
    while size > 24 and _run_width(title, size, horizontal_tracking(len(title))) > avail_w:
        size -= 2
    title_w = _run_width(title, size, horizontal_tracking(len(title)))
    title_left = center_x - title_w / 2.0 + shift
    margin = center_x - avail_w / 2.0
    title_left = min(max(title_left, margin), margin + avail_w - title_w)
    title_top = gap_top + (slot_h - size) / 2.0
    glyphs: list[Glyph] = []
    _stack_horizontal(
        glyphs, title, title_left, title_top, size, horizontal_tracking(len(title))
    )
    box = Box(title_left, title_top, title_w, size)
    return TypeLayout(tuple(glyphs), (), box)


def plan_below(
    text: str,
    *,
    left: float,
    y_top: float,
    size: float,
    tracking: float,
) -> TypeLayout:
    glyphs: list[Glyph] = []
    _stack_horizontal(glyphs, text, left, y_top, size, tracking)
    width = _run_width(text, size, tracking)
    return TypeLayout(tuple(glyphs), (), Box(left, y_top, width, size))


def _vertical_height(title: str, author: str, subtitle: str, size: float) -> float:
    h = _stack_height(title, size, vertical_tracking(len(title)))
    if author or subtitle:
        h += size * 0.34 + 3.0 + size * 0.30
    if author:
        author_size = max(16.0, round(size * 0.34))
        h += _stack_height(author, author_size, vertical_tracking(len(author)))
    if subtitle:
        if author:
            h += size * 0.22
        sub_size = max(14.0, round(size * 0.26))
        h += _stack_height(subtitle, sub_size, vertical_tracking(len(subtitle)))
    return h


def _stack_vertical(
    glyphs: list[Glyph], text: str, col_right: float, y: float, size: float, tracking: float
) -> float:
    step = _advance(size, tracking)
    for char in text:
        glyph_w = em_of(char) * size
        glyphs.append(Glyph(char, col_right - glyph_w, y, size))
        y += step
    if text:
        # The loop leaves a tracking gap after the last character. Close it.
        y -= step - size
    return y


def _stack_horizontal(
    glyphs: list[Glyph], text: str, x: float, y_top: float, size: float, tracking: float
) -> None:
    cursor = x
    gap = tracking * size
    for char in text:
        glyphs.append(Glyph(char, cursor, y_top, size))
        cursor += em_of(char) * size + gap
