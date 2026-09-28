"""Compose a cover: paper, book-edge, one motif, then the title.

The title is reserved first, and the ornament has to live in what remains.
That is the whole rule. A short title stays in the upper right (vertical) or
in the lower measure (horizontal); it is not scaled up to fill the sheet.
"""

from __future__ import annotations

from dataclasses import dataclass

from luxun_cover.geom import Box, intersects, jitter
from luxun_cover.motifs import MOTIF_NAMES, draw_motif
from luxun_cover.palette import PALETTE_NAMES, Palette, get_palette
from luxun_cover.svgdoc import SvgDoc
from luxun_cover.typography import (
    FONT_FAMILY,
    BASELINE,
    TypeLayout,
    plan_below,
    plan_between_rules,
    plan_horizontal,
    plan_vertical,
)

WIDTH = 640
HEIGHT = 920
BAND_TOP = 62
BAND_BOTTOM = 38
MARGIN_RIGHT = 48

NATURAL_LAYOUT = {
    "lattice": "vertical",
    "frame": "vertical",
    "cloud": "horizontal",
    "meander": "horizontal",
}


class CoverError(ValueError):
    """The request can't be set as a cover in this grammar."""


@dataclass(frozen=True)
class CoverPlan:
    svg: str
    motif: str
    palette: str
    layout: str
    seed: int
    text_box: Box
    field: Box
    footprints: tuple[Box, ...]
    bands: tuple[Box, ...]
    notes: tuple[str, ...]


def render_cover(
    title: str,
    author: str = "鲁迅",
    subtitle: str = "",
    motif: str = "lattice",
    palette: str = "cinnabar",
    layout: str = "auto",
    seed: int = 1,
    outline_text: bool = True,
) -> str:
    return compose(
        title=title,
        author=author,
        subtitle=subtitle,
        motif=motif,
        palette=palette,
        layout=layout,
        seed=seed,
        outline_text=outline_text,
    ).svg


def compose(
    *,
    title: str,
    author: str = "鲁迅",
    subtitle: str = "",
    motif: str = "lattice",
    palette: str = "cinnabar",
    layout: str = "auto",
    seed: int = 1,
    outline_text: bool = True,
) -> CoverPlan:
    title_text = _label(title, "书名", 16, required=True)
    author_text = _label(author, "著者", 12, required=False)
    subtitle_text = _label(subtitle, "副题", 18, required=False)
    if motif not in MOTIF_NAMES:
        known = ", ".join(MOTIF_NAMES)
        raise CoverError(f"未知纹样 {motif!r}。可选：{known}")
    if palette not in PALETTE_NAMES:
        known = ", ".join(PALETTE_NAMES)
        raise CoverError(f"未知色板 {palette!r}。可选：{known}")
    if layout not in {"auto", "vertical", "horizontal"}:
        raise CoverError("layout 只能是 auto、vertical 或 horizontal")

    pal = get_palette(palette)
    resolved = NATURAL_LAYOUT[motif] if layout == "auto" else layout
    seed_n = int(seed)
    shift = jitter(seed_n, 21, 7)

    doc = SvgDoc(
        WIDTH,
        HEIGHT,
        title=f"{title_text} · {author_text}" if author_text else title_text,
        desc=(
            f"{title_text} / {author_text}。致敬式书衣，not a facsimile。"
            "几何纹样为程序原创，不是陶元庆原作的复刻或扫描。"
        ),
    )
    doc.comment("homage layout. original geometry. not a facsimile of a Tao Yuanqing cover.")
    doc.rect(0, 0, WIDTH, HEIGHT, fill=pal.paper)

    if resolved == "vertical":
        text, field, bands, rules = _vertical_regions(
            title_text, author_text, subtitle_text, pal, seed_n
        )
    else:
        text, field, bands, rules = _horizontal_regions(
            title_text, author_text, subtitle_text, pal, shift
        )

    for band in bands:
        doc.rect(band.x, band.y, band.w, band.h, fill=pal.band_color())
    _paint_rules(doc, rules, pal.ink)

    anchor = "bottom" if resolved == "vertical" else "top"
    # Sit the lower mass a few pixels into the bottom band, still inside the trim.
    plant = 20.0 if resolved == "vertical" and pal.structure == "bands" else 0.0
    footprints = draw_motif(
        motif, doc, field, pal, seed_n, anchor=anchor, plant=plant
    )
    footprints.extend(_balance(doc, field, footprints, pal, motif, resolved, seed_n))
    face = _paint_type(doc, text, pal, outline_text=outline_text)
    if face:
        doc.desc += (
            f" 书名与著者已用 {face} 转成轮廓路径，"
            "打开 SVG 或导出 PNG 都不依赖查看器字体。字体文件未嵌入。"
        )

    notes = _review(title_text, text.box, footprints)
    return CoverPlan(
        svg=doc.tostring(),
        motif=motif,
        palette=pal.name,
        layout=resolved,
        seed=seed_n,
        text_box=text.box,
        field=field,
        footprints=tuple(footprints),
        bands=tuple(bands),
        notes=tuple(notes),
    )


def _vertical_regions(
    title: str, author: str, subtitle: str, pal: Palette, seed: int
) -> tuple[TypeLayout, Box, list[Box], list[tuple[float, float, float]]]:
    del seed
    bands = _bands(pal)
    rules: list[tuple[float, float, float]] = []
    if pal.structure == "bands":
        y_top = BAND_TOP + 46
        y_limit = HEIGHT - BAND_BOTTOM - 24
    else:
        rules = [(40, 36, WIDTH - 36), (HEIGHT - 72, 36, WIDTH - 36), (HEIGHT - 56, 36, WIDTH - 36)]
        y_top = 78
        y_limit = HEIGHT - 96
    avail_h = y_limit - y_top
    text = plan_vertical(
        title,
        author,
        subtitle,
        col_right=WIDTH - MARGIN_RIGHT,
        y_top=y_top,
        avail_h=avail_h,
        avail_w=150,
    )
    # Stop the field at the top of the bottom band. Lattice may plant past it.
    if pal.structure == "bands":
        field_bottom = HEIGHT - BAND_BOTTOM
    else:
        field_bottom = y_limit
    field = Box(0, y_top - 18, text.box.x - 24, field_bottom - (y_top - 18))
    return text, field, bands, rules


def _horizontal_regions(
    title: str,
    author: str,
    subtitle: str,
    pal: Palette,
    shift: float,
) -> tuple[TypeLayout, Box, list[Box], list[tuple[float, float, float]]]:
    bands = _bands(pal)
    rules: list[tuple[float, float, float]] = []
    avail_w = WIDTH - 96
    center = WIDTH / 2
    if pal.structure == "rules":
        text, rules = _horizontal_rules(title, author, subtitle, center, avail_w, shift)
        field_bottom = rules[1][0] - 18  # the upper of the title rules
        field = Box(0, 52, WIDTH, max(80, field_bottom - 52))
        return text, field, bands, rules

    bottom = HEIGHT - BAND_BOTTOM - 26
    text = plan_horizontal(
        title,
        author,
        subtitle,
        center_x=center,
        bottom=bottom,
        avail_w=avail_w,
        shift=shift,
    )
    field_bottom = text.box.y - 22
    field = Box(0, BAND_TOP, WIDTH, max(80, field_bottom - BAND_TOP))
    return text, field, bands, rules


def _horizontal_rules(
    title: str,
    author: str,
    subtitle: str,
    center: float,
    avail_w: float,
    shift: float,
) -> tuple[TypeLayout, list[tuple[float, float, float]]]:
    author_size = 22.0
    sub_size = 16.0
    below = 0.0
    if author:
        below += author_size
    if subtitle:
        below += (10.0 if author else 0.0) + sub_size
    lower = HEIGHT - 42 - below - (12 if below else 0)
    slot = 108.0 if len(title) <= 3 else 92.0
    upper = lower - slot
    title_layout = plan_between_rules(
        title,
        center_x=center,
        gap_top=upper,
        gap_bottom=lower,
        avail_w=avail_w,
        shift=shift,
    )
    glyphs = list(title_layout.glyphs)
    y = lower + 14
    author_left = title_layout.box.x + title_layout.box.w * 0.4
    if author:
        piece = plan_below(author, left=author_left, y_top=y, size=author_size, tracking=0.16)
        glyphs.extend(piece.glyphs)
        y = piece.box.bottom + 8
    if subtitle:
        piece = plan_below(subtitle, left=author_left, y_top=y, size=sub_size, tracking=0.08)
        glyphs.extend(piece.glyphs)
    left = min(g.x for g in glyphs)
    right = max(g.x + g.size for g in glyphs)
    top = min(g.y_top for g in glyphs)
    bottom = max(g.y_top + g.size for g in glyphs)
    text = TypeLayout(tuple(glyphs), (), Box(left, top, right - left, bottom - top))
    inset = 36.0
    rules = [
        (40.0, inset, WIDTH - inset),
        (upper, inset, WIDTH - inset),
        (lower, inset, WIDTH - inset),
    ]
    return text, rules


def _bands(pal: Palette) -> list[Box]:
    if pal.structure != "bands":
        return []
    return [
        Box(0, 0, WIDTH, BAND_TOP),
        Box(0, HEIGHT - BAND_BOTTOM, WIDTH, BAND_BOTTOM),
    ]


def _paint_rules(doc: SvgDoc, rules: list[tuple[float, float, float]], ink: str) -> None:
    for y, x0, x1 in rules:
        doc.line(x0, y, x1, y, stroke=ink, sw=2.4, cap="butt")


def _balance(
    doc: SvgDoc,
    field: Box,
    footprints: list[Box],
    pal: Palette,
    motif: str,
    layout: str,
    seed: int,
) -> list[Box]:
    extra: list[Box] = []
    if pal.name == "ochre" and motif in {"lattice", "frame"} and layout == "vertical":
        sun = _place_sun(field, footprints, seed)
        if sun is not None:
            extra.append(_draw_sun(doc, *sun, pal.accent))
    elif pal.name == "cinnabar" and motif in {"lattice", "frame"} and layout == "vertical":
        seal = _place_seal(field, footprints, seed)
        if seal is not None:
            extra.append(_draw_seal(doc, *seal, pal.accent))
    if motif in {"lattice", "frame"} and layout == "vertical":
        lines = _place_lines(field, footprints, seed)
        if lines is not None:
            extra.append(_draw_lines(doc, *lines, pal.ink))
    return extra


def _place_sun(
    field: Box, footprints: list[Box], seed: int
) -> tuple[float, float, float] | None:
    radius = 16.0
    candidates = (
        (field.x + field.w * 0.68, field.y + field.h * 0.15),
        (field.x + field.w * 0.46, field.y + field.h * 0.18),
        (field.x + field.w * 0.58, field.y + min(220.0, field.h * 0.36)),
    )
    reach = radius + 22
    for index, (cx, cy) in enumerate(candidates):
        cx += jitter(seed, 30 + index, 8)
        cy += jitter(seed, 40 + index, 6)
        box = Box(cx - reach, cy - reach, reach * 2, reach * 2)
        if not _inside(box, field, pad=4):
            continue
        if any(intersects(box, item, gap=8) for item in footprints):
            continue
        return cx, cy, radius
    return None


def _draw_sun(doc: SvgDoc, cx: float, cy: float, radius: float, color: str) -> Box:
    """A true circle. The period joke was that the sun had been drawn with a compass."""
    import math

    doc.circle(cx, cy, radius, fill=color)
    rays = 18
    gap = radius * 0.28
    length = radius * 0.55
    for index in range(rays):
        angle = -math.pi / 2 + index * (2 * math.pi / rays)
        inner = radius + gap
        outer = inner + length
        doc.line(
            cx + math.cos(angle) * inner,
            cy + math.sin(angle) * inner,
            cx + math.cos(angle) * outer,
            cy + math.sin(angle) * outer,
            stroke=color,
            sw=1.6,
            cap="butt",
        )
    reach = radius + gap + length
    return Box(cx - reach, cy - reach, reach * 2, reach * 2)


def _place_seal(
    field: Box, footprints: list[Box], seed: int
) -> tuple[float, float] | None:
    if not footprints:
        return None
    host = max(footprints, key=lambda item: item.area())
    cx = host.right + 30 + jitter(seed, 50, 4)
    cy = host.y + min(36.0, host.h * 0.18) + jitter(seed, 51, 4)
    box = Box(cx - 14, cy - 14, 28, 28)
    if not _inside(box, field, pad=2):
        return None
    if any(intersects(box, item, gap=6) for item in footprints):
        return None
    return cx, cy


def _draw_seal(doc: SvgDoc, cx: float, cy: float, color: str) -> Box:
    """A geometric chop: two circles, no forged characters."""
    doc.circle(cx, cy, 11, fill="none", stroke=color, sw=1.6)
    doc.circle(cx, cy, 6.5, fill="none", stroke=color, sw=1.1)
    return Box(cx - 13, cy - 13, 26, 26)


def _place_lines(
    field: Box, footprints: list[Box], seed: int
) -> tuple[float, float, float] | None:
    length = 118 + jitter(seed, 60, 8)
    x = field.x + 78 + jitter(seed, 61, 6)
    candidates = (
        field.y + field.h * 0.34,
        field.y + 48,
        field.y + field.h * 0.48,
    )
    height = 3 * 8 + 2
    for cy in candidates:
        box = Box(x, cy, length, height)
        if not _inside(box, field, pad=2):
            continue
        if any(intersects(box, item, gap=10) for item in footprints):
            continue
        return x, cy, length
    return None


def _draw_lines(doc: SvgDoc, x: float, y: float, length: float, color: str) -> Box:
    gap = 8.0
    for index in range(4):
        yy = y + index * gap
        doc.line(x, yy, x + length, yy, stroke=color, sw=1.5, cap="butt")
    return Box(x, y, length, gap * 3 + 2)


def _inside(box: Box, field: Box, pad: float) -> bool:
    return (
        box.x >= field.x + pad
        and box.y >= field.y + pad
        and box.right <= field.right - pad
        and box.bottom <= field.bottom - pad
    )


def _paint_type(
    doc: SvgDoc, text: TypeLayout, pal: Palette, *, outline_text: bool
) -> str | None:
    face_name: str | None = None
    if outline_text and text.glyphs:
        from luxun_cover.fonts import FontError, glyph_path, outline_transform, resolve_face

        try:
            face = resolve_face()
        except FontError as exc:
            raise CoverError(str(exc)) from exc
        doc.comment(
            f"outlined with {face.family} ({face.path} #{face.index}). "
            "glyph paths only; the font file is not embedded."
        )
        for glyph in text.glyphs:
            try:
                data = glyph_path(face, glyph.char)
            except FontError as exc:
                raise CoverError(str(exc)) from exc
            doc.group_open(
                {
                    "data-char": glyph.char,
                    "transform": outline_transform(face, glyph.x, glyph.y_top, glyph.size),
                }
            )
            # TrueType nonzero winding keeps counters (口、鲁) open.
            doc.path(data, fill=pal.ink, fill_rule="nonzero")
            doc.group_close()
        face_name = face.family
    else:
        doc.group_open({"font-family": FONT_FAMILY, "fill": pal.ink, "font-weight": "400"})
        for glyph in text.glyphs:
            doc.text(glyph.char, glyph.x, glyph.y_top + glyph.size * BASELINE, glyph.size)
        doc.group_close()
    for mark in text.marks:
        doc.rect(mark.x, mark.y, mark.w, mark.h, fill=pal.accent)
    return face_name


def _review(title: str, text_box: Box, footprints: list[Box]) -> list[str]:
    notes: list[str] = []
    page = WIDTH * HEIGHT
    used = sum(item.area() for item in footprints)
    if page and used / page > 0.42:
        notes.append("纹样占地偏多。这一语法要先看见纸，再看见纹样。换更疏的 seed，或改用 frame。")
    for item in footprints:
        if intersects(text_box, item, gap=8):
            notes.append("书名和纹样贴得太近。换 seed，或改 layout。")
            break
    if len(title) > 8:
        notes.append("书名偏长。这一语法适合短题，后半可以改放到副题。")
    return notes


def _label(value: str, field: str, limit: int, *, required: bool) -> str:
    text = "".join(str(value).split())
    if required and not text:
        raise CoverError(f"{field}不能为空")
    if len(text) > limit:
        raise CoverError(f"{field}过长（最多 {limit} 个字）。这一书衣语法只排短题。")
    return text
