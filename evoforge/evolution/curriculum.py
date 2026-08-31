from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CurriculumState:
    best_checkpoint: int
    best_step_index: int
    stagnant_generations: int
    activation_generations: int = 35
    fraction: float = 0.35


@dataclass(frozen=True)
class CurriculumStart:
    enabled: bool
    checkpoint_index: int
    step_index: int


def select_curriculum_start(
    state: CurriculumState,
    *,
    agent_index: int,
    population_size: int,
) -> CurriculumStart:
    if (
        state.best_checkpoint <= 0
        or state.best_step_index <= 0
        or state.stagnant_generations < state.activation_generations
    ):
        return CurriculumStart(enabled=False, checkpoint_index=-1, step_index=0)

    curriculum_count = max(1, round(population_size * state.fraction))
    if agent_index >= curriculum_count:
        return CurriculumStart(enabled=False, checkpoint_index=-1, step_index=0)

    return CurriculumStart(
        enabled=True,
        checkpoint_index=state.best_checkpoint - 1,
        step_index=state.best_step_index,
    )
