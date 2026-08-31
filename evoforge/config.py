from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorldConfig:
    width: int = 900
    height: int = 620
    spawn_position: tuple[float, float] = (60.0, 60.0)
    ticks_per_generation: int = 2200


@dataclass(frozen=True)
class AgentConfig:
    radius: float = 5.0
    speed: float = 4.0


@dataclass(frozen=True)
class EvolutionConfig:
    population_size: int = 120
    genome_length: int = 2200
    elite_count: int = 8
    random_agent_count: int = 12
    mutation_rate: float = 0.08
    burst_mutation_rate: float = 0.25
    stagnation_generations: int = 35
    random_seed: int | None = 12345

    def __post_init__(self) -> None:
        if self.population_size <= 0:
            raise ValueError("population_size must be greater than zero.")
        if self.genome_length <= 0:
            raise ValueError("genome_length must be greater than zero.")
        if self.elite_count < 0:
            raise ValueError("elite_count cannot be negative.")
        if self.random_agent_count < 0:
            raise ValueError("random_agent_count cannot be negative.")
        if self.elite_count + self.random_agent_count > self.population_size:
            raise ValueError("elite_count and random_agent_count cannot exceed population_size.")
        if not 0.0 <= self.mutation_rate <= 1.0:
            raise ValueError("mutation_rate must be between 0.0 and 1.0.")
        if not 0.0 <= self.burst_mutation_rate <= 1.0:
            raise ValueError("burst_mutation_rate must be between 0.0 and 1.0.")
        if self.stagnation_generations <= 0:
            raise ValueError("stagnation_generations must be greater than zero.")


@dataclass(frozen=True)
class AppConfig:
    world: WorldConfig = WorldConfig()
    agent: AgentConfig = AgentConfig()
    evolution: EvolutionConfig = EvolutionConfig()
    target_position: tuple[float, float] = (820.0, 580.0)
    target_radius: float = 18.0


@dataclass(frozen=True)
class MazeConfig:
    columns: int = 21
    rows: int = 15
    cell_size: int = 40
    seed: int = 12345

    def __post_init__(self) -> None:
        if self.columns < 3 or self.rows < 3:
            raise ValueError("Maze must have at least 3 columns and 3 rows.")
        if self.columns % 2 == 0 or self.rows % 2 == 0:
            raise ValueError("Maze dimensions must be odd.")
        if self.cell_size < 16:
            raise ValueError("Maze cell_size must leave enough room for agents.")
