from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    position: tuple[float, float]
    radius: float

    def contains_circle(self, position: tuple[float, float], radius: float) -> bool:
        return math.dist(position, self.position) <= self.radius + radius

