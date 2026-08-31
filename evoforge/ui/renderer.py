from __future__ import annotations

from evoforge.simulation.agent import Agent
from evoforge.simulation.world import World
from evoforge.ui.dashboard import dashboard_lines
from evoforge.ui.charts import history_chart_series


class Renderer:
    def __init__(self, screen, font) -> None:
        self.screen = screen
        self.font = font

    def draw(
        self,
        world: World,
        agents: list[Agent],
        best_agent: Agent | None,
        population,
        *,
        speed_label: str,
        paused: bool,
        show_best_only: bool,
        status_message: str = "",
    ) -> None:
        import pygame

        self.screen.fill((18, 22, 28))
        pygame.draw.rect(
            self.screen,
            (72, 82, 96),
            pygame.Rect(0, 0, world.config.width, world.config.height),
            width=2,
        )
        for obstacle in world.obstacles:
            pygame.draw.rect(
                self.screen,
                (92, 92, 92),
                pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height),
            )
        pygame.draw.circle(
            self.screen,
            (245, 196, 66),
            world.target.position,
            world.target.radius,
        )
        self._draw_checkpoints(pygame, world, best_agent)

        visible_agents = [best_agent] if show_best_only and best_agent else agents
        for agent in visible_agents:
            if agent is None:
                continue
            color = (80, 220, 140) if agent is best_agent else (86, 150, 235)
            if agent.collided:
                color = (220, 96, 96)
            if agent.reached_target:
                color = (245, 226, 90)
            pygame.draw.circle(self.screen, color, agent.position, agent.config.radius)
            if agent is best_agent:
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    agent.position,
                    agent.config.radius + 3,
                    width=1,
                )

        panel_x = world.config.width + 16
        lines = dashboard_lines(
            population,
            speed_label=speed_label,
            paused=paused,
            show_best_only=show_best_only,
            checkpoints_label=self._checkpoint_label(world, best_agent),
            status_message=status_message,
        )
        for index, line in enumerate(lines):
            surface = self.font.render(line, True, (225, 230, 235))
            self.screen.blit(surface, (panel_x, 18 + index * 22))

        self._draw_history_chart(
            pygame,
            population,
            x=panel_x,
            y=18 + len(lines) * 22 + 16,
            width=210,
            height=130,
        )

    def _draw_history_chart(self, pygame, population, *, x: int, y: int, width: int, height: int) -> None:
        history = population.history or []
        if not history:
            return

        pygame.draw.rect(
            self.screen,
            (54, 62, 72),
            pygame.Rect(x, y, width, height),
            width=1,
        )
        title = self.font.render("HISTORY", True, (225, 230, 235))
        self.screen.blit(title, (x, y - 18))

        for line_y in (y + height // 3, y + (height * 2) // 3):
            pygame.draw.line(
                self.screen,
                (38, 44, 52),
                (x + 1, line_y),
                (x + width - 1, line_y),
                width=1,
            )

        for series in history_chart_series(history, width=width - 2, height=height - 2):
            points = [(x + 1 + px, y + 1 + py) for px, py in series.points]
            if len(points) == 1:
                pygame.draw.circle(self.screen, series.color, points[0], 2)
            else:
                pygame.draw.lines(self.screen, series.color, False, points, width=2)

        legend = [
            ("best", (80, 220, 140)),
            ("avg", (86, 150, 235)),
            ("reached", (245, 196, 66)),
        ]
        for index, (label, color) in enumerate(legend):
            legend_y = y + height + 12 + index * 18
            pygame.draw.rect(self.screen, color, pygame.Rect(x, legend_y + 4, 10, 4))
            surface = self.font.render(label, True, (205, 211, 219))
            self.screen.blit(surface, (x + 16, legend_y))

    def _draw_checkpoints(self, pygame, world: World, best_agent: Agent | None) -> None:
        checkpoints = world.checkpoints or []
        if not checkpoints:
            return

        reached = best_agent.checkpoints_reached if best_agent is not None else 0
        next_index = best_agent.next_checkpoint_index if best_agent is not None else 0
        for index, checkpoint in enumerate(checkpoints):
            if index < reached:
                color = (70, 170, 105)
                radius = 4
            elif index == next_index:
                color = (255, 255, 180)
                radius = 7
            else:
                color = (88, 96, 106)
                radius = 4
            pygame.draw.circle(self.screen, color, checkpoint, radius)

    def _checkpoint_label(self, world: World, best_agent: Agent | None) -> str:
        total = len(world.checkpoints or [])
        if total == 0 or best_agent is None:
            return ""
        return f"{best_agent.checkpoints_reached}/{total}"
