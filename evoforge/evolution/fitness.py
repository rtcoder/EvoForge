from __future__ import annotations

import math


def distance_to_target_fitness(
    position: tuple[float, float],
    target: tuple[float, float],
    *,
    reached_target: bool,
    collided: bool = False,
    start_distance: float | None = None,
    closest_distance: float | None = None,
    checkpoints_reached: int = 0,
    distance_to_next_checkpoint: float | None = None,
) -> float:
    distance = math.dist(position, target)
    best_distance = distance if closest_distance is None else min(closest_distance, distance)
    score = 1000.0 / (best_distance + 1.0)

    if start_distance is not None:
        progress = max(0.0, start_distance - best_distance)
        score += progress * 2.0

    score += 200.0 / (distance + 1.0)
    score += checkpoints_reached * 1200.0
    if distance_to_next_checkpoint is not None:
        score += 1200.0 / (distance_to_next_checkpoint + 1.0)
    if reached_target:
        score += 5000.0
    if collided:
        score *= 0.1
    return score
