"""Minimal SVG writer. Strings only, so the core install stays dependency-free."""

from __future__ import annotations

from luxun_cover.geom import num


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


class SvgDoc:
    def __init__(self, width: int, height: int, title: str, desc: str) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.desc = desc
        self._parts: list[str] = []

    def comment(self, text: str) -> None:
        safe = text.replace("--", " — ")
        self._parts.append(f"<!-- {safe} -->")

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        *,
        fill: str | None = None,
        stroke: str | None = None,
        sw: float | None = None,
    ) -> None:
        attrs: dict[str, str] = {
            "x": num(x),
            "y": num(y),
            "width": num(w),
            "height": num(h),
            "fill": fill if fill is not None else "none",
        }
        if stroke is not None:
            attrs["stroke"] = stroke
        if sw is not None:
            attrs["stroke-width"] = num(sw)
        self._el("rect", attrs)

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        stroke: str,
        sw: float,
        cap: str = "square",
    ) -> None:
        self._el(
            "line",
            {
                "x1": num(x1),
                "y1": num(y1),
                "x2": num(x2),
                "y2": num(y2),
                "stroke": stroke,
                "stroke-width": num(sw),
                "stroke-linecap": cap,
                "fill": "none",
            },
        )

    def circle(
        self,
        cx: float,
        cy: float,
        r: float,
        *,
        fill: str = "none",
        stroke: str | None = None,
        sw: float | None = None,
    ) -> None:
        attrs = {"cx": num(cx), "cy": num(cy), "r": num(r), "fill": fill}
        if stroke is not None:
            attrs["stroke"] = stroke
        if sw is not None:
            attrs["stroke-width"] = num(sw)
        self._el("circle", attrs)

    def path(
        self,
        d: str,
        *,
        fill: str = "none",
        stroke: str | None = None,
        sw: float | None = None,
        cap: str = "butt",
        join: str = "miter",
        fill_rule: str | None = None,
    ) -> None:
        attrs = {"d": d, "fill": fill}
        if fill_rule is not None:
            attrs["fill-rule"] = fill_rule
        if stroke is not None:
            attrs["stroke"] = stroke
            attrs["stroke-width"] = num(sw if sw is not None else 1)
            attrs["stroke-linecap"] = cap
            attrs["stroke-linejoin"] = join
        self._el("path", attrs)

    def group_open(self, attrs: dict[str, str]) -> None:
        self._parts.append(f"<g {_fmt(attrs)}>")

    def group_close(self) -> None:
        self._parts.append("</g>")

    def text(self, content: str, x: float, y: float, size: float) -> None:
        body = xml_escape(content)
        self._parts.append(
            f'<text x="{num(x)}" y="{num(y)}" font-size="{num(size)}">{body}</text>'
        )

    def _el(self, tag: str, attrs: dict[str, str]) -> None:
        self._parts.append(f"<{tag} {_fmt(attrs)}/>")

    def tostring(self) -> str:
        body = "\n  ".join(self._parts)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" '
            f'role="img" xml:lang="zh-Hans">\n'
            f"  <title>{xml_escape(self.title)}</title>\n"
            f"  <desc>{xml_escape(self.desc)}</desc>\n"
            f"  {body}\n"
            "</svg>\n"
        )


def _fmt(attrs: dict[str, str]) -> str:
    return " ".join(f'{key}="{xml_escape(value)}"' for key, value in attrs.items())
