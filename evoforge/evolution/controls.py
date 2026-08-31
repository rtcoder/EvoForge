from __future__ import annotations

from dataclasses import replace

from evoforge.config import EvolutionConfig


def adjust_mutation_rate(
    config: EvolutionConfig,
    delta: float,
    *,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> EvolutionConfig:
    value = min(max(config.mutation_rate + delta, minimum), maximum)
    return replace(config, mutation_rate=round(value, 4))

