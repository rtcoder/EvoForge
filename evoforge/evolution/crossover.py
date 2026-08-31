from __future__ import annotations

import random

from evoforge.evolution.genome import Genome


def single_point_crossover(
    parent_a: Genome,
    parent_b: Genome,
    crossover_point: int | None = None,
    rng: random.Random | None = None,
) -> Genome:
    if len(parent_a) != len(parent_b):
        raise ValueError("Parent genomes must have the same length.")
    if len(parent_a) <= 1:
        return Genome(parent_a.actions)

    if crossover_point is None:
        source = rng if rng is not None else random
        crossover_point = source.randint(1, len(parent_a) - 1)

    if crossover_point <= 0 or crossover_point >= len(parent_a):
        raise ValueError("Crossover point must be inside genome bounds.")

    return Genome(parent_a.actions[:crossover_point] + parent_b.actions[crossover_point:])
