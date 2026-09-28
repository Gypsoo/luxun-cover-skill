"""Smoke tests: valid SVG, stable seeds, palette discipline, committed examples."""

from __future__ import annotations

import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from luxun_cover import CoverError, compose, render_cover
from luxun_cover.geom import intersects
from luxun_cover.motifs import MOTIF_NAMES
from luxun_cover.palette import PALETTE_NAMES, get_palette

ROOT = Path(__file__).resolve().parents[1]

# These arguments are the examples committed under examples/.
# README repeats the same commands.
EXAMPLES = (
    {
        "file": "panghuang.svg",
        "title": "彷徨",
        "palette": "ochre",
        "motif": "lattice",
        "layout": "vertical",
        "seed": 0,
    },
    {
        "file": "nahan.svg",
        "title": "呐喊",
        "palette": "ink",
        "motif": "cloud",
        "layout": "horizontal",
        "seed": 1,
    },
    {
        "file": "yecao.svg",
        "title": "野草",
        "palette": "indigo",
        "motif": "frame",
        "layout": "vertical",
        "seed": 1,
    },
)


def _parse(svg: str) -> ET.Element:
    return ET.fromstring(svg)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _is_meta(el: ET.Element) -> bool:
    return _local(el.tag) in {"title", "desc"}


class RenderTests(unittest.TestCase):
    def test_panghuang_is_svg(self) -> None:
        svg = render_cover(title="彷徨")
        root = _parse(svg)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn("彷徨", svg)
        self.assertIn("鲁迅", svg)
        self.assertIn("not a facsimile", svg)

    def test_seed_is_stable_and_effective(self) -> None:
        one = render_cover(title="彷徨", motif="lattice", palette="ochre", seed=1)
        again = render_cover(title="彷徨", motif="lattice", palette="ochre", seed=1)
        other = render_cover(title="彷徨", motif="lattice", palette="ochre", seed=2)
        self.assertEqual(one, again)
        self.assertNotEqual(one, other)

    def test_every_motif_and_palette_is_well_formed(self) -> None:
        for motif in MOTIF_NAMES:
            for palette in PALETTE_NAMES:
                for layout in ("vertical", "horizontal"):
                    plan = compose(
                        title="野草",
                        author="鲁迅",
                        subtitle="题辞",
                        motif=motif,
                        palette=palette,
                        layout=layout,
                        seed=1,
                    )
                    _parse(plan.svg)
                    colors = set()
                    for token in plan.svg.split('"'):
                        if token.startswith("#") and len(token) == 7:
                            colors.add(token)
                    self.assertLessEqual(colors, get_palette(palette).colors())
                    self.assertNotIn("gradient", plan.svg.lower())
                    self.assertNotIn("<image", plan.svg.lower())
                    self.assertFalse(intersects(plan.text_box, plan.field, gap=0))
                    for band in plan.bands:
                        self.assertFalse(
                            intersects(plan.text_box, band, gap=6),
                            f"{motif} {palette} {layout}",
                        )
                    for footprint in plan.footprints:
                        self.assertFalse(intersects(plan.text_box, footprint, gap=6))

    def test_custom_author_and_subtitle(self) -> None:
        svg = render_cover(title="呐喊", author="周树人", subtitle="短篇")
        self.assertIn("周树人", svg)
        for char in "周树人短篇":
            self.assertIn(f'data-char="{char}"', svg)
        self.assertNotIn('data-char="鲁"', svg)
        self.assertNotIn(">鲁迅<", svg)

    def test_empty_author_is_allowed(self) -> None:
        svg = render_cover(title="彷徨", author="")
        self.assertIn("彷徨", svg)
        self.assertNotIn(">鲁迅<", svg)

    def test_rejects_blank_or_long_title(self) -> None:
        with self.assertRaises(CoverError):
            render_cover(title="  ")
        with self.assertRaises(CoverError):
            render_cover(title="一二三四五六七八九十一二三四五六七")

    def test_escapes_markup_in_titles(self) -> None:
        svg = render_cover(title="甲&乙", author="丙<丁")
        self.assertIn("甲&amp;乙", svg)
        self.assertIn("丙&lt;丁", svg)
        _parse(svg)

    def test_long_title_still_renders_with_a_note(self) -> None:
        plan = compose(title="中国小说史略补遗编")
        _parse(plan.svg)
        self.assertTrue(any("书名偏长" in note for note in plan.notes))

    def test_title_glyphs_are_outlined_paths(self) -> None:
        """Title and author must be real contours, not only words in <title>/<desc>."""
        svg = render_cover(
            title="彷徨",
            author="鲁迅",
            motif="lattice",
            palette="ochre",
            layout="vertical",
            seed=0,
        )
        root = _parse(svg)
        body = [el for el in root if not _is_meta(el)]
        self.assertTrue(body)
        for char in "彷徨鲁迅":
            groups = [
                el
                for el in root.iter()
                if _local(el.tag) == "g" and el.get("data-char") == char
            ]
            self.assertTrue(groups, f"missing outlined glyph {char}")
            paths = [
                child.get("d") or ""
                for group in groups
                for child in group
                if _local(child.tag) == "path"
            ]
            self.assertTrue(paths, f"{char} has no path")
            data = max(paths, key=len)
            self.assertGreater(len(data), 40, char)
            self.assertTrue(any(cmd in data for cmd in "CQ"), f"{char} path is not a glyph")
            self.assertNotRegex(data, r"^M[\d.\- ]+H[\d.\- ]+V")

    def test_live_text_keeps_characters_in_text_nodes(self) -> None:
        svg = render_cover(title="彷徨", author="鲁迅", outline_text=False)
        root = _parse(svg)
        texts = [
            el.text or ""
            for el in root.iter()
            if _local(el.tag) == "text"
        ]
        for char in "彷徨鲁迅":
            self.assertIn(char, texts)
        self.assertNotIn('data-char="彷"', svg)

    def test_examples_match_the_renderer(self) -> None:
        for spec in EXAMPLES:
            svg = render_cover(
                title=spec["title"],
                author="鲁迅",
                motif=spec["motif"],
                palette=spec["palette"],
                layout=spec["layout"],
                seed=spec["seed"],
            )
            disk = (ROOT / "examples" / spec["file"]).read_text(encoding="utf-8")
            self.assertEqual(disk, svg)
            self.assertIn(spec["title"], disk)
            self.assertIn("not a facsimile", disk)
            _parse(disk)


class CliTests(unittest.TestCase):
    def test_module_writes_svg(self) -> None:
        out = ROOT / "examples" / "_cli_probe.svg"
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "luxun_cover",
                    "--title",
                    "彷徨",
                    "--seed",
                    "0",
                    "--out",
                    str(out),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            text = out.read_text(encoding="utf-8")
            self.assertIn("彷徨", text)
            _parse(text)
        finally:
            out.unlink(missing_ok=True)

    def test_missing_title_is_an_error(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "luxun_cover", "--out", "x.svg"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
