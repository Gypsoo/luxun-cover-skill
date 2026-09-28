"""Command line: ``luxun-cover`` and ``python -m luxun_cover``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from luxun_cover.layout import CoverError, compose
from luxun_cover.motifs import MOTIF_NAMES
from luxun_cover.palette import PALETTE_NAMES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="luxun-cover",
        description="生成民国几何书衣 SVG。纹样是原创的，不是陶元庆原封面的复刻。",
        epilog="示例：luxun-cover --title 彷徨 --palette ochre --motif lattice --out panghuang.svg",
    )
    parser.add_argument("--title", required=True, help="书名，短题为宜")
    parser.add_argument("--author", default="鲁迅", help="著者，默认「鲁迅」；空字符串表示不署名")
    parser.add_argument("--subtitle", default="", help="副题，可空")
    parser.add_argument("--motif", default="lattice", choices=MOTIF_NAMES, help="纹样族")
    parser.add_argument("--palette", default="cinnabar", choices=PALETTE_NAMES, help="色板")
    parser.add_argument(
        "--layout",
        default="auto",
        choices=("auto", "vertical", "horizontal"),
        help="书名直排或横排。auto：窗格与角框直排，云头与回纹横排",
    )
    parser.add_argument("--seed", type=int, default=1, help="整数种子。相同种子得到相同 SVG")
    parser.add_argument(
        "--outline-text",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="把汉字转成轮廓路径（默认开启），SVG 与 PNG 不依赖查看器字体。--no-outline-text 改写 <text>",
    )
    parser.add_argument("--out", required=True, help="输出 .svg 路径")
    parser.add_argument(
        "--png",
        action="store_true",
        help="同时写 PNG。需要可选依赖 cairosvg（pip install 'luxun-cover-skill[png]'）",
    )
    args = parser.parse_args(argv)

    try:
        plan = compose(
            title=args.title,
            author=args.author,
            subtitle=args.subtitle,
            motif=args.motif,
            palette=args.palette,
            layout=args.layout,
            seed=args.seed,
            outline_text=args.outline_text,
        )
    except CoverError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(plan.svg, encoding="utf-8")
    for note in plan.notes:
        print(f"note: {note}", file=sys.stderr)

    if args.png:
        png_path = out.with_suffix(".png")
        try:
            _write_png(out, png_path)
        except SystemExit as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(png_path)
    print(out)
    return 0


def _write_png(svg_path: Path, png_path: Path) -> None:
    try:
        import cairosvg
    except ImportError as exc:
        raise SystemExit(
            "未安装 PNG 支持。v0.1 默认只保证 SVG。"
            "需要时再装：pip install 'luxun-cover-skill[png]'（系统要有 cairo）。"
        ) from exc
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=1280)


if __name__ == "__main__":
    raise SystemExit(main())
