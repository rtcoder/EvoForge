import random
import unittest

from evoforge.config import EvolutionConfig
from evoforge.evolution.crossover import single_point_crossover
from evoforge.evolution.fitness import distance_to_target_fitness
from evoforge.evolution.genome import Direction, Genome
from evoforge.evolution.mutation import mutate_genome
from evoforge.evolution.population import Population


class EvolutionCoreTest(unittest.TestCase):
    def test_mutation_rate_zero_keeps_genome_identical(self) -> None:
        genome = Genome([Direction.RIGHT, Direction.UP, Direction.LEFT])

        mutated = mutate_genome(genome, mutation_rate=0.0, rng=random.Random(123))

        self.assertEqual(mutated, genome)

    def test_mutation_rate_one_replaces_every_gene_with_non_matching_directions(
        self,
    ) -> None:
        genome = Genome([Direction.RIGHT, Direction.RIGHT, Direction.RIGHT])

        mutated = mutate_genome(genome, mutation_rate=1.0, rng=random.Random(2))

        self.assertEqual(len(mutated.actions), len(genome.actions))
        self.assertTrue(all(action != Direction.RIGHT for action in mutated.actions))

    def test_mutation_preserves_protected_prefix(self) -> None:
        genome = Genome(
            [
                Direction.RIGHT,
                Direction.RIGHT,
                Direction.UP,
                Direction.UP,
                Direction.LEFT,
            ]
        )

        mutated = mutate_genome(
            genome,
            mutation_rate=1.0,
            rng=random.Random(2),
            protected_prefix_length=3,
        )

        self.assertEqual(
            list(mutated.actions[:3]),
            [Direction.RIGHT, Direction.RIGHT, Direction.UP],
        )
        self.assertNotEqual(list(mutated.actions[3:]), [Direction.UP, Direction.LEFT])

    def test_single_point_crossover_combines_prefix_and_suffix(self) -> None:
        parent_a = Genome([Direction.RIGHT, Direction.RIGHT, Direction.UP, Direction.UP])
        parent_b = Genome([Direction.LEFT, Direction.LEFT, Direction.DOWN, Direction.DOWN])

        child = single_point_crossover(parent_a, parent_b, crossover_point=2)

        self.assertEqual(
            list(child.actions),
            [
                Direction.RIGHT,
                Direction.RIGHT,
                Direction.DOWN,
                Direction.DOWN,
            ],
        )

    def test_distance_to_target_fitness_rewards_closeness(self) -> None:
        fitness = distance_to_target_fitness(
            (0.0, 0.0), (3.0, 4.0), reached_target=False
        )

        self.assertAlmostEqual(fitness, 200.0)

    def test_distance_to_target_fitness_rewards_progress_and_best_approach(self) -> None:
        fitness = distance_to_target_fitness(
            (300.0, 0.0),
            (500.0, 0.0),
            reached_target=False,
            start_distance=500.0,
            closest_distance=100.0,
        )

        self.assertAlmostEqual(fitness, 810.8960149746317)

    def test_distance_to_target_fitness_rewards_goal(self) -> None:
        fitness = distance_to_target_fitness(
            (10.0, 10.0), (10.0, 10.0), reached_target=True
        )

        self.assertAlmostEqual(fitness, 6200.0)

    def test_distance_to_target_fitness_penalizes_wall_collision(self) -> None:
        safe = distance_to_target_fitness(
            (100.0, 0.0),
            (200.0, 0.0),
            reached_target=False,
            collided=False,
            start_distance=200.0,
            closest_distance=100.0,
        )
        crashed = distance_to_target_fitness(
            (100.0, 0.0),
            (200.0, 0.0),
            reached_target=False,
            collided=True,
            start_distance=200.0,
            closest_distance=100.0,
        )

        self.assertLess(crashed, safe * 0.2)

    def test_distance_to_target_fitness_rewards_checkpoints(self) -> None:
        no_checkpoint = distance_to_target_fitness(
            (300.0, 0.0),
            (500.0, 0.0),
            reached_target=False,
            checkpoints_reached=0,
            distance_to_next_checkpoint=120.0,
        )
        with_checkpoints = distance_to_target_fitness(
            (300.0, 0.0),
            (500.0, 0.0),
            reached_target=False,
            checkpoints_reached=2,
            distance_to_next_checkpoint=20.0,
        )

        self.assertGreater(with_checkpoints - no_checkpoint, 750.0)

    def test_population_next_generation_preserves_elite_and_mutates_descendants(
        self,
    ) -> None:
        config = EvolutionConfig(
            population_size=4,
            genome_length=3,
            elite_count=1,
            random_agent_count=1,
            mutation_rate=1.0,
            random_seed=7,
        )
        population = Population.create(config)
        population.genomes = [
            Genome([Direction.RIGHT, Direction.RIGHT, Direction.RIGHT]),
            Genome([Direction.UP, Direction.UP, Direction.UP]),
            Genome([Direction.LEFT, Direction.LEFT, Direction.LEFT]),
            Genome([Direction.DOWN, Direction.DOWN, Direction.DOWN]),
        ]

        population.evolve([10.0, 2.0, 1.0, 0.5])

        self.assertEqual(population.generation, 2)
        self.assertEqual(
            list(population.genomes[0].actions),
            [Direction.RIGHT, Direction.RIGHT, Direction.RIGHT],
        )
        self.assertEqual(len(population.genomes), 4)
        self.assertEqual(population.last_stats.best_fitness, 10.0)
        self.assertAlmostEqual(population.last_stats.average_fitness, 3.375)

    def test_population_mutates_descendants_after_protected_prefix(self) -> None:
        config = EvolutionConfig(
            population_size=3,
            genome_length=5,
            elite_count=1,
            random_agent_count=0,
            mutation_rate=1.0,
            random_seed=2,
        )
        population = Population.create(config)
        population.genomes = [
            Genome(
                [
                    Direction.RIGHT,
                    Direction.RIGHT,
                    Direction.UP,
                    Direction.UP,
                    Direction.LEFT,
                ]
            ),
            Genome([Direction.DOWN] * 5),
            Genome([Direction.LEFT] * 5),
        ]

        population.evolve([10.0, 1.0, 0.5], protected_prefix_lengths=[3, 0, 0])

        self.assertEqual(
            list(population.genomes[1].actions[:3]),
            [Direction.RIGHT, Direction.RIGHT, Direction.UP],
        )

    def test_population_uses_burst_mutation_after_checkpoint_stagnation(self) -> None:
        config = EvolutionConfig(
            population_size=3,
            genome_length=5,
            elite_count=1,
            random_agent_count=0,
            mutation_rate=0.0,
            burst_mutation_rate=1.0,
            stagnation_generations=2,
            random_seed=2,
        )
        population = Population.create(config)
        population.genomes = [
            Genome([Direction.RIGHT] * 5),
            Genome([Direction.UP] * 5),
            Genome([Direction.LEFT] * 5),
        ]

        population.evolve([10.0, 1.0, 0.5], progress_scores=[4, 1, 0])
        population.evolve([10.0, 1.0, 0.5], progress_scores=[4, 1, 0])

        self.assertEqual(population.stagnant_generations, 1)
        self.assertFalse(population.burst_active)

        population.evolve([10.0, 1.0, 0.5], progress_scores=[4, 1, 0])

        self.assertEqual(population.stagnant_generations, 2)
        self.assertTrue(population.burst_active)
        self.assertNotEqual(
            list(population.genomes[1].actions),
            [Direction.RIGHT] * 5,
        )

    def test_population_randomizes_suffix_during_deep_stagnation(self) -> None:
        config = EvolutionConfig(
            population_size=3,
            genome_length=8,
            elite_count=1,
            random_agent_count=0,
            mutation_rate=0.0,
            burst_mutation_rate=0.0,
            stagnation_generations=1,
            random_seed=4,
        )
        population = Population.create(config)
        population.genomes = [
            Genome(
                [
                    Direction.RIGHT,
                    Direction.RIGHT,
                    Direction.UP,
                    Direction.UP,
                    Direction.UP,
                    Direction.UP,
                    Direction.UP,
                    Direction.UP,
                ]
            ),
            Genome([Direction.LEFT] * 8),
            Genome([Direction.DOWN] * 8),
        ]

        population.evolve([10.0, 1.0, 0.5], progress_scores=[3, 1, 0])
        population.evolve(
            [10.0, 1.0, 0.5],
            protected_prefix_lengths=[3, 0, 0],
            progress_scores=[3, 1, 0],
        )

        self.assertTrue(population.burst_active)
        self.assertEqual(
            list(population.genomes[1].actions[:3]),
            [Direction.RIGHT, Direction.RIGHT, Direction.UP],
        )
        self.assertNotEqual(
            list(population.genomes[1].actions[3:]),
            [Direction.UP, Direction.UP, Direction.UP, Direction.UP, Direction.UP],
        )

    def test_population_resets_stagnation_when_checkpoint_progress_improves(self) -> None:
        config = EvolutionConfig(
            population_size=3,
            genome_length=5,
            elite_count=1,
            random_agent_count=0,
            mutation_rate=0.0,
            burst_mutation_rate=1.0,
            stagnation_generations=2,
            random_seed=2,
        )
        population = Population.create(config)

        population.evolve([10.0, 1.0, 0.5], progress_scores=[3, 1, 0])
        population.evolve([10.0, 1.0, 0.5], progress_scores=[3, 1, 0])
        population.evolve([10.0, 1.0, 0.5], progress_scores=[4, 1, 0])

        self.assertEqual(population.best_progress_score, 4)
        self.assertEqual(population.stagnant_generations, 0)
        self.assertFalse(population.burst_active)

    def test_single_gene_crossover_returns_parent_prefix_without_crashing(self) -> None:
        parent_a = Genome([Direction.RIGHT])
        parent_b = Genome([Direction.LEFT])

        child = single_point_crossover(parent_a, parent_b)

        self.assertEqual(list(child.actions), [Direction.RIGHT])

    def test_explicit_crossover_point_must_be_inside_genome(self) -> None:
        parent_a = Genome([Direction.RIGHT, Direction.UP])
        parent_b = Genome([Direction.LEFT, Direction.DOWN])

        with self.assertRaises(ValueError):
            single_point_crossover(parent_a, parent_b, crossover_point=0)

        with self.assertRaises(ValueError):
            single_point_crossover(parent_a, parent_b, crossover_point=2)

    def test_invalid_evolution_config_is_rejected_early(self) -> None:
        with self.assertRaises(ValueError):
            EvolutionConfig(population_size=0)

        with self.assertRaises(ValueError):
            EvolutionConfig(genome_length=0)

        with self.assertRaises(ValueError):
            EvolutionConfig(population_size=4, elite_count=3, random_agent_count=2)

        with self.assertRaises(ValueError):
            EvolutionConfig(mutation_rate=1.5)

    def test_population_evolve_rejects_empty_fitnesses_with_clear_error(self) -> None:
        population = Population.create(
            EvolutionConfig(
                population_size=1,
                genome_length=1,
                elite_count=1,
                random_agent_count=0,
            )
        )

        with self.assertRaises(ValueError):
            population.evolve([])


if __name__ == "__main__":
    unittest.main()
