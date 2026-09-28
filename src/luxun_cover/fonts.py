"""Find a CJK face on this machine and turn characters into SVG paths.

Outlined glyphs do not depend on the viewer's fonts. The font file stays
on disk; only the path data is written into the SVG. Noto CJK and Source
Han are SIL Open Font License — install them, do not vendor them here.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

from luxun_cover.geom import num

# Song/Ming first. Gothic faces are a last resort so a bare box still has glyphs.
PREFERRED_FAMILIES: tuple[str, ...] = (
    "Noto Serif CJK SC",
    "Noto Serif SC",
    "Source Han Serif SC",
    "Source Han Serif CN",
    "Source Han Serif",
    "Songti SC",
    "Songti TC",
    "STSong",
    "SimSun",
    "AR PL UMing CN",
    "AR PL UMing TW",
    "PingFang SC",
    "Hiragino Mincho ProN",
    "Noto Sans CJK SC",
    "Noto Sans SC",
    "Source Han Sans SC",
    "Source Han Sans CN",
    "Microsoft YaHei",
    "WenQuanYi Zen Hei",
    "WenQuanYi Micro Hei",
    "Droid Sans Fallback",
)

# Used only when fontconfig has no match. Index is resolved from the name table.
_FILE_HINTS: tuple[tuple[str, str], ...] = (
    ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", "Noto Serif CJK SC"),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "Noto Sans CJK SC"),
    ("/usr/share/fonts/truetype/arphic/uming.ttc", "AR PL UMing CN"),
    ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "WenQuanYi Micro Hei"),
    ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "WenQuanYi Zen Hei"),
    ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", "Droid Sans Fallback"),
    ("/System/Library/Fonts/Supplemental/Songti.ttc", "Songti SC"),
    ("/System/Library/Fonts/Songti.ttc", "Songti SC"),
    ("/System/Library/Fonts/PingFang.ttc", "PingFang SC"),
    ("/Library/Fonts/Songti.ttc", "Songti SC"),
    ("C:/Windows/Fonts/simsun.ttc", "SimSun"),
    ("C:/Windows/Fonts/msyh.ttc", "Microsoft YaHei"),
)

INSTALL_HINT = (
    "找不到可转曲的中文字体，因此不会画出空心方框。"
    "请安装一款下面的字体后重试（本仓库不附带字体文件）。"
    "Linux：sudo apt install fonts-noto-cjk。"
    "macOS：系统自带 Songti SC / PingFang SC，或 brew install --cask font-noto-serif-cjk。"
    "Windows：系统自带宋体 SimSun、微软雅黑 Microsoft YaHei，或安装 Noto Serif CJK / 思源宋体。"
    "Noto CJK 与思源字体为 SIL Open Font License。"
    "若只要依赖查看器字体的活字，加 --no-outline-text。"
)

# A character every accepted face must have. Rejects Latin fallbacks such as Noto Sans.
_PROBE = 0x9C81  # 鲁

_STYLE_RANK = {
    "regular": 0,
    "normal": 0,
    "roman": 1,
    "book": 1,
    "light": 2,
    "medium": 3,
}

_face: "Face | None" = None
_paths: dict[tuple[str, int, str], str] = {}


class FontError(ValueError):
    """No usable CJK face, or the face has no glyph for a character."""


@dataclass
class Face:
    family: str
    path: str
    index: int
    upem: int
    ascender: int
    font: TTFont


def resolve_face() -> Face:
    """The first preferred family that fontconfig (or a known path) can open."""
    global _face
    if _face is not None:
        return _face
    found = _from_fontconfig() or _from_file_hints()
    if found is None:
        raise FontError(INSTALL_HINT)
    _face = found
    return found


def glyph_path(face: Face, char: str) -> str:
    """SVG path data in font units. Missing characters raise, they do not become boxes."""
    key = (face.path, face.index, char)
    cached = _paths.get(key)
    if cached is not None:
        return cached
    cmap = face.font.getBestCmap() or {}
    name = cmap.get(ord(char))
    if not name:
        raise FontError(
            f"字体 {face.family} 没有「{char}」这个字。"
            "换一款覆盖更全的中文字体（例如 fonts-noto-cjk），或改用 --no-outline-text。"
        )
    glyph_set = face.font.getGlyphSet()
    pen = SVGPathPen(glyph_set)
    glyph_set[name].draw(pen)
    data = pen.getCommands()
    if not data or len(data) < 8:
        raise FontError(f"字体 {face.family} 里「{char}」没有可绘制的轮廓。")
    _paths[key] = data
    return data


def outline_transform(face: Face, x: float, y_top: float, size: float) -> str:
    """Map the font em box onto the layout em box. Typographic ascender sits on y_top."""
    scale = size / face.upem
    baseline = y_top + size * (face.ascender / face.upem)
    return (
        f"translate({num(x)} {num(baseline)}) "
        f"scale({_prec(scale)} {_prec(-scale)})"
    )


def _from_fontconfig() -> Face | None:
    if shutil.which("fc-list") is None:
        return None
    for family in PREFERRED_FAMILIES:
        rows = _fc_list(family)
        if not rows:
            continue
        rows.sort(key=lambda item: _style_rank(item[2]))
        path, index, _style = rows[0]
        face = _open_face(path, index, family)
        if face is not None:
            return face
    return None


def _fc_list(family: str) -> list[tuple[str, int, str]]:
    proc = subprocess.run(
        ["fc-list", "-f", "%{file}\t%{index}\t%{family}\t%{style}\n", family],
        check=False,
        capture_output=True,
        text=True,
    )
    rows: list[tuple[str, int, str]] = []
    wanted = family.casefold()
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        file_path, index_text, fam, style = parts[0], parts[1], parts[2], parts[3]
        names = [part.strip().casefold() for part in fam.split(",")]
        if wanted not in names:
            continue
        try:
            index = int(index_text or "0")
        except ValueError:
            index = 0
        rows.append((file_path, index, style.strip()))
    return rows


def _from_file_hints() -> Face | None:
    from pathlib import Path

    for path, family in _FILE_HINTS:
        if not Path(path).is_file():
            continue
        index = _index_for_family(path, family)
        if index is None:
            continue
        face = _open_face(path, index, family)
        if face is not None:
            return face
    return None


def _index_for_family(path: str, family: str) -> int | None:
    wanted = family.casefold()
    for index in range(8):
        try:
            font = TTFont(path, fontNumber=index)
        except Exception:
            break
        try:
            if wanted in _family_names(font) and _supports_cjk(font):
                return index
        finally:
            font.close()
    return None


def _open_face(path: str, index: int, family: str) -> Face | None:
    try:
        font = TTFont(path, fontNumber=index)
    except Exception:
        return None
    if not _supports_cjk(font):
        font.close()
        return None
    # Prefer the name the file actually claims, when it matches what we asked for.
    names = _family_names(font)
    chosen = family if family.casefold() in names else family
    upem = int(font["head"].unitsPerEm)
    ascender = _ascender(font, upem)
    return Face(
        family=chosen,
        path=path,
        index=index,
        upem=upem,
        ascender=ascender,
        font=font,
    )


def _family_names(font: TTFont) -> set[str]:
    found: set[str] = set()
    for rec in font["name"].names:
        if rec.nameID not in (1, 16):
            continue
        try:
            found.add(rec.toUnicode().strip().casefold())
        except Exception:
            continue
    return found


def _supports_cjk(font: TTFont) -> bool:
    cmap = font.getBestCmap() or {}
    return _PROBE in cmap


def _ascender(font: TTFont, upem: int) -> int:
    """OS/2 typo ascender when it describes a real em box; otherwise a Song-like 0.88 em."""
    os2 = font["OS/2"]
    asc = int(os2.sTypoAscender)
    desc = int(os2.sTypoDescender)
    if asc > 0 and (asc - desc) >= int(upem * 0.9):
        return asc
    win = int(os2.usWinAscent)
    if 0 < win <= upem:
        return win
    return int(round(upem * 0.88))


def _style_rank(style: str) -> int:
    folded = style.casefold()
    if any(token in folded for token in ("bold", "black", "heavy", "semibold", "demibold")):
        return 50
    return _STYLE_RANK.get(folded, 10)


def _prec(value: float) -> str:
    text = f"{float(value):.6f}".rstrip("0").rstrip(".")
    if text in {"", "-0", "-"}:
        return "0"
    return text
