from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Obstacle:
    x: float
    y: float
    width: float
    height: float

    def contains_circle(self, position: tuple[float, float], radius: float) -> bool:
        x, y = position
        closest_x = min(max(x, self.x), self.x + self.width)
        closest_y = min(max(y, self.y), self.y + self.height)
        return (x - closest_x) ** 2 + (y - closest_y) ** 2 <= radius**2

