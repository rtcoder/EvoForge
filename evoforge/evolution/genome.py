from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    UP = (0.0, -1.0)
    DOWN = (0.0, 1.0)
    LEFT = (-1.0, 0.0)
    RIGHT = (1.0, 0.0)
    STILL = (0.0, 0.0)


MOVING_DIRECTIONS: tuple[Direction, ...] = (
    Direction.UP,
    Direction.DOWN,
    Direction.LEFT,
    Direction.RIGHT,
)


@dataclass(frozen=True)
class Genome:
    actions: tuple[Direction, ...]

    def __init__(self, actions: list[Direction] | tuple[Direction, ...]) -> None:
        object.__setattr__(self, "actions", tuple(actions))

    @classmethod
    def random(cls, length: int, rng: random.Random) -> Genome:
        return cls([rng.choice(MOVING_DIRECTIONS) for _ in range(length)])

    def __len__(self) -> int:
        return len(self.actions)
