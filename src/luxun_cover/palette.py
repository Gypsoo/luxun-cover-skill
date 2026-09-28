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


PALETTES: dict[str, Palette] = {
    "cinnabar": Palette(
        name="cinnabar",
        paper="#F2E4C8",
        ink="#1A1612",
        accent="#A33B32",
        structure="bands",
    ),
    "ochre": Palette(
        name="ochre",
        paper="#E2AC45",
        ink="#1C140F",
        accent="#C4482A",
        structure="bands",
    ),
    "indigo": Palette(
        name="indigo",
        paper="#EFE6D6",
        ink="#1A1916",
        accent="#2F4458",
        structure="bands",
    ),
    "ink": Palette(
        name="ink",
        paper="#F7F3EA",
        ink="#161616",
        accent="#161616",
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
