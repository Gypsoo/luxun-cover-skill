"""Small geometry helpers. Seeds are hashed, not drawn from ``random``, so a
given seed renders the same on every CPython version.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def area(self) -> float:
        return max(0.0, self.w) * max(0.0, self.h)


def intersects(a: Box, b: Box, gap: float = 0.0) -> bool:
    """True when the boxes come within ``gap`` pixels of each other."""
    return not (
        a.right + gap <= b.x
        or b.right + gap <= a.x
        or a.bottom + gap <= b.y
        or b.bottom + gap <= a.y
    )


def unit(seed: int, salt: int) -> float:
    """Stable float in ``[0, 1)`` from an integer seed."""
    n = (int(seed) * 374761393 + int(salt) * 668265263) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return n / 4294967296


def jitter(seed: int, salt: int, amount: float) -> float:
    return (unit(seed, salt) * 2.0 - 1.0) * amount


def num(value: float) -> str:
    v = float(value)
    if abs(v) < 1e-6:
        return "0"
    rounded = round(v, 2)
    if abs(rounded - round(rounded)) < 1e-6:
        return str(int(round(rounded)))
    return f"{rounded:.2f}".rstrip("0").rstrip(".")
