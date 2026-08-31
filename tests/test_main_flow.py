import unittest

from evoforge.config import AppConfig, EvolutionConfig, WorldConfig
from evoforge.evolution.genome import Direction, Genome
from evoforge.evolution.population import Population
from evoforge.main import all_agents_finished, finish_generation, spawn_agents
from evoforge.simulation.target import Target
from evoforge.simulation.world import World


class MainFlowTest(unittest.TestCase):
    def test_finish_generation_returns_agents_for_evolved_genomes(self) -> None:
        config = AppConfig(
            world=WorldConfig(width=40, height=40, spawn_position=(5.0, 5.0)),
            evolution=EvolutionConfig(
                population_size=2,
                genome_length=2,
                elite_count=1,
                random_agent_count=0,
                mutation_rate=0.0,
                random_seed=3,
            ),
            target_position=(30.0, 5.0),
            target_radius=3.0,
        )
        world = World(
            config=config.world,
            agent_config=config.agent,
            target=Target(config.target_position, config.target_radius),
            obstacles=[],
        )
        population = Population.create(config.evolution)
        population.genomes = [
            Genome([Direction.RIGHT, Direction.RIGHT]),
            Genome([Direction.LEFT, Direction.LEFT]),
        ]
        agents = spawn_agents(world, population)
        agents[0].position = (20.0, 5.0)
        agents[1].position = (1.0, 5.0)

        next_agents, best_index = finish_generation(world, population, agents)

        self.assertEqual(population.generation, 2)
        self.assertEqual(best_index, 0)
        self.assertEqual(list(next_agents[0].genome.actions), [Direction.RIGHT, Direction.RIGHT])
        self.assertEqual(next_agents[0].position, config.world.spawn_position)

    def test_all_agents_finished_when_every_agent_has_collided_or_reached_target(self) -> None:
        config = AppConfig(
            world=WorldConfig(width=40, height=40, spawn_position=(5.0, 5.0)),
            evolution=EvolutionConfig(
                population_size=2,
                genome_length=2,
                elite_count=1,
                random_agent_count=0,
            ),
            target_position=(30.0, 5.0),
            target_radius=3.0,
        )
        world = World(
            config=config.world,
            agent_config=config.agent,
            target=Target(config.target_position, config.target_radius),
            obstacles=[],
        )
        agents = [
            world.spawn_agent(Genome([Direction.RIGHT])),
            world.spawn_agent(Genome([Direction.LEFT])),
        ]
        agents[0].collided = True
        agents[1].reached_target = True

        self.assertTrue(all_agents_finished(agents))

    def test_spawn_agents_uses_curriculum_frontier_after_stagnation(self) -> None:
        config = AppConfig(
            world=WorldConfig(width=120, height=40, spawn_position=(10.0, 10.0)),
            evolution=EvolutionConfig(
                population_size=4,
                genome_length=20,
                elite_count=1,
                random_agent_count=0,
                stagnation_generations=2,
            ),
            target_position=(110.0, 10.0),
            target_radius=3.0,
        )
        world = World(
            config=config.world,
            agent_config=config.agent,
            target=Target(config.target_position, config.target_radius),
            obstacles=[],
            checkpoints=[(30.0, 10.0), (60.0, 10.0), (90.0, 10.0)],
        )
        population = Population.create(config.evolution)
        population.best_progress_score = 2
        population.best_progress_step_index = 7
        population.stagnant_generations = 2

        agents = spawn_agents(world, population)

        curriculum_agents = [agent for agent in agents if agent.step_index == 7]
        self.assertGreaterEqual(len(curriculum_agents), 1)
        self.assertEqual(curriculum_agents[0].position, (60.0, 10.0))
        self.assertEqual(curriculum_agents[0].checkpoints_reached, 2)


if __name__ == "__main__":
    unittest.main()
