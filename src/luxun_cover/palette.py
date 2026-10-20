"""Restrained Republican palettes: paper, ink, and at most one accent.

These are not color-matches of any surviving impression. Early descriptions of
the 1926 *Panghuang* cover speak of orange ground and deep blue; later
printings drifted, and Lu Xun objected. The sets below are a working grammar:
warm paper, black, one accent (often cinnabar).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    name: str
    paper: str
    ink: str
    accent: str
    # "bands": full-bleed top and bottom edges (the book block).
    # "rules": inset hairlines, the monochrome series-page grammar.
    structure: str

    def colors(self) -> frozenset[str]:
        return frozenset({self.paper, self.ink, self.accent})

    def band_color(self) -> str:
        if self.accent == self.ink:
            return self.ink
        return self.accent


# Values sit darker than a screen swatch so a thumbnail still separates
# paper, ink, and the book edge. They are not a match to any one printing.
PALETTES: dict[str, Palette] = {
    "cinnabar": Palette(
        name="cinnabar",
        paper="#E4CBA8",
        ink="#14110E",
        accent="#8C2F28",
        structure="bands",
    ),
    "ochre": Palette(
        name="ochre",
        paper="#E09A2C",
        ink="#14110C",
        accent="#B43316",
        structure="bands",
    ),
    "indigo": Palette(
        name="indigo",
        paper="#E3D0B0",
        ink="#141311",
        accent="#1A3142",
        structure="bands",
    ),
    "ink": Palette(
        name="ink",
        paper="#F0E2C6",
        ink="#12110F",
        accent="#12110F",
        structure="rules",
    ),
}

PALETTE_NAMES = tuple(PALETTES)


def get_palette(name: str) -> Palette:
    try:
        return PALETTES[name]
    except KeyError as exc:
        known = ", ".join(PALETTE_NAMES)
        raise ValueError(f"未知色板 {name!r}。可选：{known}") from exc
