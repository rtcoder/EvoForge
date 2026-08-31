from __future__ import annotations

import random
from dataclasses import dataclass
from statistics import median

from evoforge.config import EvolutionConfig
from evoforge.evolution.crossover import single_point_crossover
from evoforge.evolution.genome import Genome
from evoforge.evolution.mutation import mutate_genome, randomize_genome_suffix


@dataclass(frozen=True)
class PopulationStats:
    generation: int
    best_fitness: float
    average_fitness: float
    median_fitness: float
    worst_fitness: float
    success_count: int = 0


@dataclass
class Population:
    config: EvolutionConfig
    genomes: list[Genome]
    rng: random.Random
    generation: int = 1
    last_stats: PopulationStats | None = None
    history: list[PopulationStats] | None = None
    best_progress_score: int = 0
    best_progress_step_index: int = 0
    stagnant_generations: int = 0
    burst_active: bool = False
    suffix_randomizations: int = 0

    @property
    def curriculum_active(self) -> bool:
        return (
            self.best_progress_score > 0
            and self.best_progress_step_index > 0
            and self.stagnant_generations >= self.config.stagnation_generations
        )

    @classmethod
    def create(cls, config: EvolutionConfig) -> Population:
        rng = random.Random(config.random_seed)
        genomes = [Genome.random(config.genome_length, rng) for _ in range(config.population_size)]
        return cls(config=config, genomes=genomes, rng=rng, history=[])

    def evolve(
        self,
        fitnesses: list[float],
        success_count: int = 0,
        protected_prefix_lengths: list[int] | None = None,
        progress_scores: list[int] | None = None,
    ) -> None:
        if len(fitnesses) != len(self.genomes):
            raise ValueError("Fitness count must match population size.")
        if not fitnesses:
            raise ValueError("Fitnesses cannot be empty.")
        if protected_prefix_lengths is None:
            protected_prefix_lengths = [0] * len(self.genomes)
        if len(protected_prefix_lengths) != len(self.genomes):
            raise ValueError("Protected prefix count must match population size.")
        if progress_scores is None:
            progress_scores = [0] * len(self.genomes)
        if len(progress_scores) != len(self.genomes):
            raise ValueError("Progress score count must match population size.")

        ranked = sorted(
            zip(
                fitnesses,
                self.genomes,
                protected_prefix_lengths,
                progress_scores,
                strict=True,
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        generation_progress = max(progress_scores)
        if generation_progress > self.best_progress_score:
            self.best_progress_score = generation_progress
            best_progress_index = progress_scores.index(generation_progress)
            self.best_progress_step_index = protected_prefix_lengths[best_progress_index]
            self.stagnant_generations = 0
        else:
            self.stagnant_generations += 1
        self.burst_active = self.stagnant_generations >= self.config.stagnation_generations
        self.suffix_randomizations = 0
        mutation_rate = (
            self.config.burst_mutation_rate
            if self.burst_active
            else self.config.mutation_rate
        )
        stats = PopulationStats(
            generation=self.generation,
            best_fitness=ranked[0][0],
            average_fitness=sum(fitnesses) / len(fitnesses),
            median_fitness=median(fitnesses),
            worst_fitness=ranked[-1][0],
            success_count=success_count,
        )
        self.last_stats = stats
        assert self.history is not None
        self.history.append(stats)

        elites = [
            genome
            for _, genome, _prefix, _progress in ranked[: self.config.elite_count]
        ]
        next_genomes = list(elites)
        parent_pool = [
            (genome, prefix)
            for _, genome, prefix, _progress in ranked[: max(1, len(ranked) // 2)]
        ]

        descendants_needed = (
            self.config.population_size
            - self.config.random_agent_count
            - len(next_genomes)
        )
        for index in range(max(0, descendants_needed)):
            parent, protected_prefix = parent_pool[index % len(parent_pool)]
            if len(parent_pool) > 1 and index % 3 == 2:
                mate, mate_prefix = parent_pool[(index + 1) % len(parent_pool)]
                parent = single_point_crossover(parent, mate, rng=self.rng)
                protected_prefix = min(protected_prefix, mate_prefix)
            if self.burst_active and index % 2 == 0:
                child = randomize_genome_suffix(
                    parent,
                    self.rng,
                    protected_prefix_length=protected_prefix,
                )
                self.suffix_randomizations += 1
            else:
                child = mutate_genome(
                    parent,
                    mutation_rate,
                    self.rng,
                    protected_prefix_length=protected_prefix,
                )
            next_genomes.append(child)

        while len(next_genomes) < self.config.population_size:
            next_genomes.append(Genome.random(self.config.genome_length, self.rng))

        self.genomes = next_genomes[: self.config.population_size]
        self.generation += 1
