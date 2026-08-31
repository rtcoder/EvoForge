from __future__ import annotations

import random

from evoforge.evolution.genome import MOVING_DIRECTIONS, Direction, Genome


def mutate_genome(
    genome: Genome,
    mutation_rate: float,
    rng: random.Random,
    *,
    protected_prefix_length: int = 0,
) -> Genome:
    mutated: list[Direction] = []
    protected_prefix_length = min(max(0, protected_prefix_length), len(genome))
    for index, action in enumerate(genome.actions):
        if index < protected_prefix_length:
            mutated.append(action)
            continue
        if rng.random() >= mutation_rate:
            mutated.append(action)
            continue

        candidates = [direction for direction in MOVING_DIRECTIONS if direction != action]
        mutated.append(rng.choice(candidates))

    return Genome(mutated)


def randomize_genome_suffix(
    genome: Genome,
    rng: random.Random,
    *,
    protected_prefix_length: int,
) -> Genome:
    protected_prefix_length = min(max(0, protected_prefix_length), len(genome))
    actions = list(genome.actions[:protected_prefix_length])
    actions.extend(
        rng.choice(MOVING_DIRECTIONS)
        for _ in range(len(genome) - protected_prefix_length)
    )
    return Genome(actions)
