"""Original geometric ornaments. Compass-and-rule constructions, not traced drawings.

One cover gets one motif, so the line logic stays consistent: a lattice cover is
orthogonal, a cloud cover is arcs, a frame cover is corners, a meander cover is
a fret band. None of these paths come from a scan of Tao Yuanqing's covers.
"""

from __future__ import annotations

import math

from luxun_cover.geom import Box, jitter, num
from luxun_cover.palette import Palette
from luxun_cover.svgdoc import SvgDoc

MOTIF_NAMES = ("lattice", "cloud", "frame", "meander")


def draw_motif(
    name: str,
    doc: SvgDoc,
    field: Box,
    palette: Palette,
    seed: int,
    *,
    anchor: str,
    plant: float,
) -> list[Box]:
    if name not in MOTIF_NAMES:
        known = ", ".join(MOTIF_NAMES)
        raise ValueError(f"未知纹样 {name!r}。可选：{known}")
    drawer = {
        "lattice": _lattice,
        "cloud": _cloud,
        "frame": _frame,
        "meander": _meander,
    }[name]
    return drawer(doc, field, palette, seed, anchor=anchor, plant=plant)


def _lattice(
    doc: SvgDoc,
    field: Box,
    palette: Palette,
    seed: int,
    *,
    anchor: str,
    plant: float,
) -> list[Box]:
    variant = seed % 3
    width = 256 + jitter(seed, 1, 8)
    height = 292 + jitter(seed, 2, 8)
    width = min(width, max(80.0, field.w - 48))
    height = min(height, max(80.0, field.h * 0.46))
    x = field.x + 30 + jitter(seed, 3, 6)
    if anchor == "bottom":
        # `plant` drops the mass a short way into the bottom band, still on the page.
        y = field.bottom - height + min(max(plant, 0.0), 26.0)
    else:
        y = field.y + 18 + jitter(seed, 4, 6)
    x = _clamp(x, field.x + 8, field.right - width - 8)
    y_hi = field.bottom - height + min(max(plant, 0.0), 26.0)
    y = _clamp(y, field.y + 8, max(field.y + 8, y_hi))
    ink = palette.ink
    if variant == 0:
        _lattice_bar(doc, x, y, width, height, ink)
    elif variant == 1:
        _lattice_panes(doc, x, y, width, height, ink)
    else:
        _lattice_concentric(doc, x, y, width, height, ink)
    return [Box(x, y, width, height)]


def _lattice_bar(doc: SvgDoc, x: float, y: float, w: float, h: float, ink: str) -> None:
    """A solid vertical mass and three open panels. Weight, not a figure and not a table."""
    doc.rect(x, y, w, h, fill="none", stroke=ink, sw=8)
    bar = w * 0.40
    doc.rect(x, y, bar, h, fill=ink)
    rx = x + bar
    rw = w - bar
    for index, (a, b) in enumerate(((0.0, 0.34), (0.34, 0.67), (0.67, 1.0))):
        pad = 9
        y0 = y + h * a + pad
        y1 = y + h * b - pad
        doc.rect(rx + pad, y0, rw - pad * 2, max(8.0, y1 - y0), fill="none", stroke=ink, sw=2.4)


def _lattice_panes(doc: SvgDoc, x: float, y: float, w: float, h: float, ink: str) -> None:
    """Two by three. One cell is solid ink; the rest is paper."""
    doc.rect(x, y, w, h, fill="none", stroke=ink, sw=8)
    xs = (0.0, 0.46, 1.0)
    ys = (0.0, 0.38, 0.70, 1.0)
    _grid_lines(doc, x, y, w, h, xs, ys, ink, 3.0)
    cx, cy, cw, ch = _cell_box(x, y, w, h, xs, ys, col=0, row=1)
    doc.rect(cx, cy, cw, ch, fill=ink)
    _cell_diagonals(doc, x, y, w, h, xs, ys, col=1, row=0, ink=ink, sw=2.0)


def _lattice_concentric(doc: SvgDoc, x: float, y: float, w: float, h: float, ink: str) -> None:
    doc.rect(x, y, w, h, fill="none", stroke=ink, sw=7)
    m1 = 22
    doc.rect(x + m1, y + m1, w - m1 * 2, h - m1 * 2, fill="none", stroke=ink, sw=2.2)
    m2 = 44
    doc.rect(x + m2, y + m2, w - m2 * 2, h - m2 * 2, fill="none", stroke=ink, sw=2.2)
    cx = x + w / 2
    cy = y + h / 2
    arm = min(w, h) * 0.18
    doc.line(cx - arm, cy, cx + arm, cy, stroke=ink, sw=2.2)
    doc.line(cx, cy - arm, cx, cy + arm, stroke=ink, sw=2.2)


def _grid_lines(
    doc: SvgDoc,
    x: float,
    y: float,
    w: float,
    h: float,
    xs: tuple[float, ...],
    ys: tuple[float, ...],
    ink: str,
    sw: float,
) -> None:
    for fx in xs[1:-1]:
        xx = x + w * fx
        doc.line(xx, y, xx, y + h, stroke=ink, sw=sw)
    for fy in ys[1:-1]:
        yy = y + h * fy
        doc.line(x, yy, x + w, yy, stroke=ink, sw=sw)


def _cell_box(
    x: float,
    y: float,
    w: float,
    h: float,
    xs: tuple[float, ...],
    ys: tuple[float, ...],
    *,
    col: int,
    row: int,
) -> tuple[float, float, float, float]:
    x0 = x + w * xs[col]
    x1 = x + w * xs[col + 1]
    y0 = y + h * ys[row]
    y1 = y + h * ys[row + 1]
    return x0, y0, x1 - x0, y1 - y0


def _cell_diagonals(
    doc: SvgDoc,
    x: float,
    y: float,
    w: float,
    h: float,
    xs: tuple[float, ...],
    ys: tuple[float, ...],
    *,
    col: int,
    row: int,
    ink: str,
    sw: float,
) -> None:
    x0, y0, cw, ch = _cell_box(x, y, w, h, xs, ys, col=col, row=row)
    pad = 6
    doc.line(x0 + pad, y0 + pad, x0 + cw - pad, y0 + ch - pad, stroke=ink, sw=sw, cap="butt")
    doc.line(x0 + cw - pad, y0 + pad, x0 + pad, y0 + ch - pad, stroke=ink, sw=sw, cap="butt")


def _cloud(
    doc: SvgDoc,
    field: Box,
    palette: Palette,
    seed: int,
    *,
    anchor: str,
    plant: float,
) -> list[Box]:
    """A scalloped frieze: identical circular caps in a row, pinched to one baseline.

    Repetition keeps it a border. The caps are compass segments, not a drawing of clouds.
    """
    del anchor, plant
    ink = palette.ink
    count = 4 if seed % 2 == 0 else 5
    radius = 86 if count == 4 else 70
    drop = radius * 0.26
    left = field.x + 36 + jitter(seed, 6, 5)
    usable = max(120.0, field.right - left - 28)
    half = math.sqrt(max(1.0, radius * radius - drop * drop))
    natural = half * 2 * count
    scale = min(1.0, usable / natural)
    radius *= scale
    drop *= scale
    cap = radius - drop
    pad = 26 + jitter(seed, 5, 3)
    baseline = field.y + pad + cap
    plinth = 12 * scale + 3
    if baseline + plinth > field.bottom - 8:
        baseline = field.bottom - 8 - plinth
    path, right = _scallop_path(left, baseline, radius, drop, count)
    doc.path(path, fill=ink)
    doc.rect(left, baseline - 0.5, right - left, plinth, fill=ink)
    return [Box(left, baseline - cap - 2, right - left, cap + plinth + 4)]


def _scallop_path(
    x: float, baseline: float, radius: float, drop: float, count: int
) -> tuple[str, float]:
    half = math.sqrt(max(1.0, radius * radius - drop * drop))
    points: list[tuple[float, float]] = [(x, baseline)]
    for index in range(count):
        cx = x + half + index * half * 2
        cy = baseline + drop
        a0 = math.atan2(-drop, -half)
        a1 = math.atan2(-drop, half)
        points.extend(_arc_upward(cx, cy, radius, a0, a1))
    right = x + half * 2 * count
    points.append((right, baseline))
    points.append((x, baseline))
    cmds = [f"M {num(points[0][0])} {num(points[0][1])}"]
    cmds.extend(f"L {num(px)} {num(py)}" for px, py in points[1:])
    cmds.append("Z")
    return " ".join(cmds), right


def _arc_upward(
    cx: float, cy: float, radius: float, a0: float, a1: float, steps: int = 10
) -> list[tuple[float, float]]:
    """Points along the arc from a0 to a1 whose midpoint sits higher on the page."""
    forward = (a1 - a0) % (2 * math.pi) or (2 * math.pi)
    backward = forward - 2 * math.pi
    mid_f = a0 + forward / 2
    mid_b = a0 + backward / 2
    y_f = cy + radius * math.sin(mid_f)
    y_b = cy + radius * math.sin(mid_b)
    delta = forward if y_f <= y_b else backward
    points = []
    for step in range(1, steps + 1):
        angle = a0 + delta * step / steps
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def _frame(
    doc: SvgDoc,
    field: Box,
    palette: Palette,
    seed: int,
    *,
    anchor: str,
    plant: float,
) -> list[Box]:
    del anchor, plant
    ink = palette.ink
    accent = palette.accent
    variant = seed % 2
    left = field.x + 26 + jitter(seed, 7, 5)
    top = field.y + 26 + jitter(seed, 8, 5)
    right = field.right - 18 + jitter(seed, 9, 4)
    bottom = field.bottom - 22
    outer = 8.0
    inner = 2.2
    channel = 13.0
    leg_x = min(230 + jitter(seed, 10, 12), (right - left) * 0.62)
    leg_y = min(168 + jitter(seed, 11, 10), (bottom - top) * 0.34)
    boxes = []
    boxes.append(_corner(doc, left, top, leg_x, leg_y, outer, inner, channel, ink, right=True, down=True))
    if accent != ink:
        _jewel(doc, left, top, outer, channel, accent, right=True, down=True)
    # The second corner stays at the bottom. A top-right corner collides with a vertical title.
    if variant == 0:
        sx, sy = min(120.0, leg_x * 0.55), min(86.0, leg_y * 0.52)
    else:
        sx, sy = min(72.0, leg_x * 0.34), min(120.0, leg_y * 0.72)
    boxes.append(
        _corner(doc, right, bottom, sx, sy, 6.0, 1.8, 10.0, ink, right=False, down=False)
    )
    return boxes


def _corner(
    doc: SvgDoc,
    x: float,
    y: float,
    leg_x: float,
    leg_y: float,
    outer: float,
    inner: float,
    channel: float,
    color: str,
    *,
    right: bool,
    down: bool,
) -> Box:
    _leg(doc, x, y, leg_x, leg_y, outer, color, right=right, down=down)
    shift = outer + channel
    ix = x + shift if right else x - shift
    iy = y + shift if down else y - shift
    inner_x = max(24.0, leg_x - shift * 1.35)
    inner_y = max(20.0, leg_y - shift * 1.35)
    _leg(doc, ix, iy, inner_x, inner_y, inner, color, right=right, down=down)
    width = leg_x
    height = leg_y
    box_x = x if right else x - width
    box_y = y if down else y - height
    return Box(box_x, box_y, width, height)


def _leg(
    doc: SvgDoc,
    x: float,
    y: float,
    leg_x: float,
    leg_y: float,
    thickness: float,
    color: str,
    *,
    right: bool,
    down: bool,
) -> None:
    hx = x if right else x - leg_x
    hy = y if down else y - thickness
    doc.rect(hx, hy, leg_x, thickness, fill=color)
    vx = x if right else x - thickness
    vy = y if down else y - leg_y
    doc.rect(vx, vy, thickness, leg_y, fill=color)


def _jewel(
    doc: SvgDoc,
    x: float,
    y: float,
    outer: float,
    channel: float,
    accent: str,
    *,
    right: bool,
    down: bool,
) -> None:
    side = max(5.0, channel - 4.0)
    jx = x + outer + 2 if right else x - outer - 2 - side
    jy = y + outer + 2 if down else y - outer - 2 - side
    doc.rect(jx, jy, side, side, fill=accent)


def _meander(
    doc: SvgDoc,
    field: Box,
    palette: Palette,
    seed: int,
    *,
    anchor: str,
    plant: float,
) -> list[Box]:
    del anchor, plant
    ink = palette.ink
    height = 118 + jitter(seed, 12, 4)
    top = field.y + 48 + jitter(seed, 13, 4)
    left = field.x + 34
    width = min(field.w * 0.70, field.w - 48)
    if seed % 2 == 0:
        width = min(width, field.w * 0.56)
    width = max(90.0, width)
    if top + height > field.bottom - 8:
        height = max(64.0, field.bottom - 8 - top)
    _fret(doc, left, top, width, height, ink)
    return [Box(left, top, width, height)]


def _fret(doc: SvgDoc, x: float, y: float, width: float, height: float, ink: str) -> None:
    """A row of squared spirals (回) tied by two rails. Grid construction, not a traced border."""
    stroke = max(5.0, min(8.0, height * 0.11))
    channel = stroke * 0.85
    gap = stroke * 0.7
    cell = height - stroke * 2 - channel * 2
    if cell < stroke * 4:
        return
    pitch = cell + gap
    repeats = max(1, int(width // pitch))
    used = repeats * cell + (repeats - 1) * gap
    if used > width:
        repeats = 1
        used = min(cell, width)
    x0 = x  # left-aligned: the right end of the band stays open
    doc.rect(x0, y, used, stroke, fill=ink)
    doc.rect(x0, y + height - stroke, used, stroke, fill=ink)
    cell_y = y + stroke + channel
    for index in range(repeats):
        _hui(doc, x0 + index * pitch, cell_y, cell, cell, stroke, ink)


def _hui(
    doc: SvgDoc,
    x: float,
    y: float,
    size: float,
    limit_h: float,
    stroke: float,
    ink: str,
) -> None:
    side = min(size, limit_h)
    t = stroke
    doc.rect(x, y, side, t, fill=ink)
    doc.rect(x, y + side - t, side, t, fill=ink)
    doc.rect(x, y, t, side, fill=ink)
    doc.rect(x + side - t, y, t, side, fill=ink)
    inset = t * 2.2
    inner = side - inset * 2
    if inner <= t * 2.4:
        return
    ix = x + inset
    iy = y + inset
    doc.rect(ix, iy, inner, t, fill=ink)
    doc.rect(ix, iy + inner - t, inner, t, fill=ink)
    doc.rect(ix, iy, t, inner, fill=ink)
    doc.rect(ix + inner - t, iy, t, inner, fill=ink)


def _clamp(value: float, lo: float, hi: float) -> float:
    if hi < lo:
        return lo
    return min(max(value, lo), hi)
