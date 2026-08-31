import unittest

from evoforge.config import AgentConfig, WorldConfig
from evoforge.evolution.genome import Direction, Genome
from evoforge.simulation.agent import Agent
from evoforge.simulation.obstacle import Obstacle
from evoforge.simulation.target import Target
from evoforge.simulation.world import World


class SimulationWorldTest(unittest.TestCase):
    def test_agent_applies_genome_actions_in_order(self) -> None:
        agent = Agent.spawn(
            genome=Genome([Direction.RIGHT, Direction.DOWN]),
            position=(10.0, 10.0),
            config=AgentConfig(speed=5.0),
        )

        agent.step()
        agent.step()

        self.assertEqual(agent.position, (15.0, 15.0))

    def test_agent_can_start_from_genome_step_offset(self) -> None:
        agent = Agent.spawn(
            genome=Genome([Direction.LEFT, Direction.RIGHT]),
            position=(10.0, 10.0),
            config=AgentConfig(speed=5.0),
            step_index=1,
        )

        agent.step()

        self.assertEqual(agent.position, (15.0, 10.0))
        self.assertEqual(agent.step_index, 2)

    def test_world_clamps_agent_at_boundaries_and_marks_collision(self) -> None:
        world = World(
            config=WorldConfig(width=20, height=20, spawn_position=(2.0, 5.0)),
            agent_config=AgentConfig(radius=3.0, speed=5.0),
            target=Target(position=(18.0, 18.0), radius=4.0),
            obstacles=[],
        )
        agent = world.spawn_agent(Genome([Direction.LEFT]))

        world.step_agent(agent)

        self.assertEqual(agent.position, (3.0, 5.0))
        self.assertTrue(agent.collided)

    def test_world_marks_agent_that_reaches_target(self) -> None:
        world = World(
            config=WorldConfig(width=40, height=40, spawn_position=(10.0, 10.0)),
            agent_config=AgentConfig(radius=2.0, speed=5.0),
            target=Target(position=(15.0, 10.0), radius=3.0),
            obstacles=[],
        )
        agent = world.spawn_agent(Genome([Direction.RIGHT]))

        world.step_agent(agent)

        self.assertTrue(agent.reached_target)

    def test_world_tracks_closest_distance_to_target(self) -> None:
        world = World(
            config=WorldConfig(width=40, height=40, spawn_position=(10.0, 10.0)),
            agent_config=AgentConfig(radius=2.0, speed=5.0),
            target=Target(position=(30.0, 10.0), radius=3.0),
            obstacles=[],
        )
        agent = world.spawn_agent(Genome([Direction.RIGHT]))

        self.assertEqual(agent.closest_distance_to_target, 20.0)

        world.step_agent(agent)

        self.assertEqual(agent.closest_distance_to_target, 15.0)

        world.reset_agent(agent)

        self.assertEqual(agent.closest_distance_to_target, 20.0)

    def test_world_tracks_ordered_checkpoints(self) -> None:
        world = World(
            config=WorldConfig(width=80, height=40, spawn_position=(10.0, 10.0)),
            agent_config=AgentConfig(radius=2.0, speed=5.0),
            target=Target(position=(70.0, 10.0), radius=3.0),
            obstacles=[],
            checkpoints=[(15.0, 10.0), (20.0, 10.0)],
            checkpoint_radius=3.0,
        )
        agent = world.spawn_agent(Genome([Direction.RIGHT, Direction.RIGHT]))

        world.step_agent(agent)
        world.step_agent(agent)

        self.assertEqual(agent.checkpoints_reached, 2)
        self.assertEqual(agent.next_checkpoint_index, 2)
        self.assertEqual(agent.last_checkpoint_step_index, 1)

    def test_world_can_spawn_agent_at_frontier_checkpoint(self) -> None:
        world = World(
            config=WorldConfig(width=120, height=40, spawn_position=(10.0, 10.0)),
            agent_config=AgentConfig(radius=2.0, speed=5.0),
            target=Target(position=(110.0, 10.0), radius=3.0),
            obstacles=[],
            checkpoints=[(30.0, 10.0), (60.0, 10.0), (90.0, 10.0)],
            checkpoint_radius=3.0,
        )

        agent = world.spawn_agent_at_checkpoint(
            Genome([Direction.RIGHT] * 20),
            checkpoint_index=1,
            step_index=7,
        )

        self.assertEqual(agent.position, (60.0, 10.0))
        self.assertEqual(agent.step_index, 7)
        self.assertEqual(agent.checkpoints_reached, 2)
        self.assertEqual(agent.next_checkpoint_index, 2)
        self.assertEqual(agent.last_checkpoint_step_index, 7)

    def test_world_marks_obstacle_collision(self) -> None:
        world = World(
            config=WorldConfig(width=40, height=40, spawn_position=(10.0, 10.0)),
            agent_config=AgentConfig(radius=2.0, speed=5.0),
            target=Target(position=(35.0, 35.0), radius=3.0),
            obstacles=[Obstacle(x=14.0, y=8.0, width=4.0, height=4.0)],
        )
        agent = world.spawn_agent(Genome([Direction.RIGHT]))

        world.step_agent(agent)

        self.assertTrue(agent.collided)

    def test_world_does_not_process_terminal_agent_again(self) -> None:
        world = World(
            config=WorldConfig(width=40, height=40, spawn_position=(10.0, 10.0)),
            agent_config=AgentConfig(radius=2.0, speed=5.0),
            target=Target(position=(35.0, 35.0), radius=3.0),
            obstacles=[],
            checkpoints=[(25.0, 10.0)],
            checkpoint_radius=3.0,
        )
        agent = world.spawn_agent(Genome([Direction.RIGHT]))
        agent.collided = True

        world.step_agent(agent)

        self.assertEqual(agent.position, (10.0, 10.0))
        self.assertEqual(agent.step_index, 0)
        self.assertEqual(agent.checkpoints_reached, 0)

    def test_world_reset_agent_returns_to_spawn_and_first_gene(self) -> None:
        world = World(
            config=WorldConfig(width=40, height=40, spawn_position=(10.0, 10.0)),
            agent_config=AgentConfig(radius=2.0, speed=5.0),
            target=Target(position=(35.0, 35.0), radius=3.0),
            obstacles=[],
        )
        agent = world.spawn_agent(Genome([Direction.RIGHT]))
        world.step_agent(agent)

        world.reset_agent(agent)

        self.assertEqual(agent.position, (10.0, 10.0))
        self.assertEqual(agent.step_index, 0)


if __name__ == "__main__":
    unittest.main()
