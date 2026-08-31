from __future__ import annotations

from dataclasses import dataclass

from evoforge.config import AgentConfig
from evoforge.evolution.genome import Direction, Genome


@dataclass
class Agent:
    genome: Genome
    position: tuple[float, float]
    config: AgentConfig
    step_index: int = 0
    collided: bool = False
    reached_target: bool = False
    start_distance_to_target: float | None = None
    closest_distance_to_target: float | None = None
    next_checkpoint_index: int = 0
    checkpoints_reached: int = 0
    last_checkpoint_step_index: int = 0
    distance_to_next_checkpoint: float | None = None

    @classmethod
    def spawn(
        cls,
        genome: Genome,
        position: tuple[float, float],
        config: AgentConfig,
        step_index: int = 0,
    ) -> Agent:
        return cls(
            genome=genome,
            position=position,
            config=config,
            step_index=step_index,
        )

    def step(self) -> None:
        if self.reached_target or self.collided:
            return

        action = self.next_action()
        dx, dy = action.value
        x, y = self.position
        self.position = (x + dx * self.config.speed, y + dy * self.config.speed)
        self.step_index += 1

    def next_action(self) -> Direction:
        if self.step_index >= len(self.genome):
            return Direction.STILL
        return self.genome.actions[self.step_index]

    def reset(self, position: tuple[float, float]) -> None:
        self.position = position
        self.step_index = 0
        self.collided = False
        self.reached_target = False
        self.start_distance_to_target = None
        self.closest_distance_to_target = None
        self.next_checkpoint_index = 0
        self.checkpoints_reached = 0
        self.last_checkpoint_step_index = 0
        self.distance_to_next_checkpoint = None
