from __future__ import annotations

from dataclasses import dataclass
import math

from evoforge.config import AgentConfig, WorldConfig
from evoforge.evolution.genome import Genome
from evoforge.simulation.agent import Agent
from evoforge.simulation.obstacle import Obstacle
from evoforge.simulation.target import Target


@dataclass
class World:
    config: WorldConfig
    agent_config: AgentConfig
    target: Target
    obstacles: list[Obstacle]
    checkpoints: list[tuple[float, float]] | None = None
    checkpoint_radius: float = 9.0

    def spawn_agent(self, genome: Genome) -> Agent:
        agent = Agent.spawn(genome, self.config.spawn_position, self.agent_config)
        self._update_target_distance(agent)
        self._update_checkpoint_progress(agent)
        agent.start_distance_to_target = agent.closest_distance_to_target
        return agent

    def spawn_agent_at_checkpoint(
        self,
        genome: Genome,
        *,
        checkpoint_index: int,
        step_index: int,
    ) -> Agent:
        checkpoints = self.checkpoints or []
        if checkpoint_index < 0 or checkpoint_index >= len(checkpoints):
            raise ValueError("checkpoint_index must point at an existing checkpoint.")

        agent = Agent.spawn(
            genome,
            checkpoints[checkpoint_index],
            self.agent_config,
            step_index=step_index,
        )
        agent.next_checkpoint_index = checkpoint_index + 1
        agent.checkpoints_reached = checkpoint_index + 1
        agent.last_checkpoint_step_index = step_index
        self._update_target_distance(agent)
        self._update_checkpoint_progress(agent)
        agent.start_distance_to_target = agent.closest_distance_to_target
        return agent

    def step_agent(self, agent: Agent) -> None:
        if agent.collided or agent.reached_target:
            return

        previous_position = agent.position
        agent.step()
        self._apply_boundaries(agent, previous_position)
        self._update_target_distance(agent)
        self._update_checkpoint_progress(agent)

        if any(
            obstacle.contains_circle(agent.position, agent.config.radius)
            for obstacle in self.obstacles
        ):
            agent.collided = True

        if self.target.contains_circle(agent.position, agent.config.radius):
            agent.reached_target = True

    def reset_agent(self, agent: Agent) -> None:
        agent.reset(self.config.spawn_position)
        self._update_target_distance(agent)
        self._update_checkpoint_progress(agent)
        agent.start_distance_to_target = agent.closest_distance_to_target

    def _apply_boundaries(
        self,
        agent: Agent,
        previous_position: tuple[float, float],
    ) -> None:
        x, y = agent.position
        radius = agent.config.radius
        clamped_x = min(max(x, radius), self.config.width - radius)
        clamped_y = min(max(y, radius), self.config.height - radius)
        if (clamped_x, clamped_y) != (x, y):
            agent.position = (clamped_x, clamped_y)
            agent.collided = True
            if previous_position[0] == clamped_x or previous_position[1] == clamped_y:
                agent.position = (clamped_x, clamped_y)

    def _update_target_distance(self, agent: Agent) -> None:
        distance = math.dist(agent.position, self.target.position)
        if agent.closest_distance_to_target is None:
            agent.closest_distance_to_target = distance
        else:
            agent.closest_distance_to_target = min(
                agent.closest_distance_to_target,
                distance,
            )

    def _update_checkpoint_progress(self, agent: Agent) -> None:
        checkpoints = self.checkpoints or []
        if agent.next_checkpoint_index >= len(checkpoints):
            agent.distance_to_next_checkpoint = None
            return

        next_checkpoint = checkpoints[agent.next_checkpoint_index]
        distance = math.dist(agent.position, next_checkpoint)
        agent.distance_to_next_checkpoint = distance
        if distance <= self.checkpoint_radius + agent.config.radius:
            agent.next_checkpoint_index += 1
            agent.checkpoints_reached += 1
            agent.last_checkpoint_step_index = agent.step_index
            self._update_checkpoint_progress(agent)
