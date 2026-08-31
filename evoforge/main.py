from __future__ import annotations

import argparse
import math
from dataclasses import replace
from pathlib import Path

from evoforge.config import AgentConfig, AppConfig, MazeConfig, WorldConfig
from evoforge.evolution.controls import adjust_mutation_rate
from evoforge.evolution.curriculum import CurriculumState, select_curriculum_start
from evoforge.evolution.fitness import distance_to_target_fitness
from evoforge.evolution.genome import Genome
from evoforge.evolution.population import Population
from evoforge.persistence.genome_storage import load_genome_record, save_genome_record
from evoforge.simulation.agent import Agent
from evoforge.simulation.maze import checkpoints_from_path, generate_maze, maze_to_obstacles
from evoforge.simulation.target import Target
from evoforge.simulation.world import World
from evoforge.ui.pixel_font import PixelFont
from evoforge.ui.renderer import Renderer


SPEEDS = [1, 2, 5, 10, 50]
SAVE_PATH = Path("experiments/best_genome.json")


def build_world(
    config: AppConfig | None = None,
    *,
    world_config: WorldConfig | None = None,
    agent_config: AgentConfig | None = None,
    maze_config: MazeConfig | None = None,
) -> World:
    app_config = config or AppConfig()
    maze = generate_maze(maze_config or MazeConfig())
    world_values = world_config or app_config.world
    agent_values = agent_config or app_config.agent
    spawn_position = maze.cell_center(maze.start_cell)
    target_position = maze.cell_center(maze.goal_cell)
    return World(
        config=WorldConfig(
            width=world_values.width,
            height=world_values.height,
            spawn_position=spawn_position,
            ticks_per_generation=world_values.ticks_per_generation,
        ),
        agent_config=agent_values,
        target=Target(target_position, app_config.target_radius),
        obstacles=maze_to_obstacles(maze),
        checkpoints=checkpoints_from_path(maze, maze.solution_path()),
    )


def spawn_agents(world: World, population: Population, *, use_curriculum: bool = True) -> list[Agent]:
    agents: list[Agent] = []
    state = CurriculumState(
        best_checkpoint=population.best_progress_score,
        best_step_index=population.best_progress_step_index,
        stagnant_generations=population.stagnant_generations,
        activation_generations=population.config.stagnation_generations,
    )
    for index, genome in enumerate(population.genomes):
        curriculum_start = select_curriculum_start(
            state,
            agent_index=index,
            population_size=len(population.genomes),
        )
        if use_curriculum and curriculum_start.enabled:
            agents.append(
                world.spawn_agent_at_checkpoint(
                    genome,
                    checkpoint_index=curriculum_start.checkpoint_index,
                    step_index=curriculum_start.step_index,
                )
            )
        else:
            agents.append(world.spawn_agent(genome))
    return agents


def all_agents_finished(agents: list[Agent]) -> bool:
    return all(agent.collided or agent.reached_target for agent in agents)


def agent_fitness(world: World, agent: Agent) -> float:
    return distance_to_target_fitness(
        agent.position,
        world.target.position,
        reached_target=agent.reached_target,
        collided=agent.collided,
        start_distance=agent.start_distance_to_target,
        closest_distance=agent.closest_distance_to_target,
        checkpoints_reached=agent.checkpoints_reached,
        distance_to_next_checkpoint=agent.distance_to_next_checkpoint,
    )


def finish_generation(
    world: World,
    population: Population,
    agents: list[Agent],
) -> tuple[list[Agent], int]:
    fitnesses = [agent_fitness(world, agent) for agent in agents]
    protected_prefix_lengths = [
        agent.last_checkpoint_step_index for agent in agents
    ]
    progress_scores = [agent.checkpoints_reached for agent in agents]
    success_count = sum(1 for agent in agents if agent.reached_target)
    population.evolve(
        fitnesses,
        success_count=success_count,
        protected_prefix_lengths=protected_prefix_lengths,
        progress_scores=progress_scores,
    )
    return spawn_agents(world, population), 0


def set_mutation_rate(population: Population, delta: float) -> None:
    population.config = adjust_mutation_rate(population.config, delta)


def save_best_genome(
    path: Path,
    *,
    world: World,
    population: Population,
    agents: list[Agent],
    best_agent_index: int,
) -> None:
    agent = agents[best_agent_index]
    save_genome_record(
        path,
        generation=population.generation,
        fitness=agent_fitness(world, agent),
        genome=agent.genome,
        config=population.config,
    )


def load_saved_genome_into_population(
    path: Path,
    *,
    population: Population,
) -> Genome:
    record = load_genome_record(path)
    population.config = replace(
        population.config,
        mutation_rate=record.evolution.mutation_rate,
    )
    population.genomes[0] = record.genome
    return record.genome


def _generation_metrics(world: World, agents: list[Agent]) -> tuple[float, float, int]:
    best_end_distance = min(
        math.dist(agent.position, world.target.position)
        for agent in agents
    )
    best_close_distance = min(
        agent.closest_distance_to_target or best_end_distance
        for agent in agents
    )
    best_checkpoints = max(agent.checkpoints_reached for agent in agents)
    return best_end_distance, best_close_distance, best_checkpoints


def run_headless(generations: int, *, report_every: int = 0) -> None:
    config = AppConfig()
    world = build_world(config)
    population = Population.create(config.evolution)
    agents = spawn_agents(world, population)
    best_end_distance = 0.0
    best_close_distance = 0.0
    best_checkpoints = 0
    for _ in range(generations):
        for _tick in range(config.world.ticks_per_generation):
            for agent in agents:
                world.step_agent(agent)
            if all_agents_finished(agents):
                break
        best_end_distance, best_close_distance, best_checkpoints = _generation_metrics(
            world,
            agents,
        )
        agents, _best_index = finish_generation(world, population, agents)
        if report_every > 0 and population.last_stats is not None:
            if population.last_stats.generation % report_every == 0:
                print(
                    f"Generation {population.last_stats.generation}: "
                    f"best_cp={best_checkpoints}/{len(world.checkpoints or [])}, "
                    f"best_dist={best_end_distance:.2f}, "
                    f"stagnant={population.stagnant_generations}, "
                    f"burst={'on' if population.burst_active else 'off'}, "
                    f"curriculum={'on' if population.curriculum_active else 'off'}, "
                    f"suffix_rolls={population.suffix_randomizations}",
                    flush=True,
                )
    stats = population.last_stats
    if stats is not None:
        print(
            f"Generation {stats.generation}: best={stats.best_fitness:.4f}, "
            f"avg={stats.average_fitness:.4f}, "
            f"best_dist={best_end_distance:.2f}, "
            f"best_close={best_close_distance:.2f}, "
            f"best_cp={best_checkpoints}/{len(world.checkpoints or [])}, "
            f"burst={'on' if population.burst_active else 'off'}, "
            f"curriculum={'on' if population.curriculum_active else 'off'}, "
            f"suffix_rolls={population.suffix_randomizations}, "
            f"reached={stats.success_count}"
        )


def run_visual() -> None:
    import pygame

    config = AppConfig()
    pygame.init()
    screen = pygame.display.set_mode((config.world.width + 250, config.world.height))
    pygame.display.set_caption("EvoForge")
    clock = pygame.time.Clock()
    try:
        font = pygame.font.SysFont("Menlo", 16)
    except (ImportError, NotImplementedError):
        font = PixelFont(scale=2)
    renderer = Renderer(screen, font)

    world = build_world(config)
    population = Population.create(config.evolution)
    agents = spawn_agents(world, population)
    paused = False
    show_best_only = False
    speed_index = 0
    tick = 0
    best_agent_index = 0
    running = True
    status_message = ""

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    population = Population.create(config.evolution)
                    agents = spawn_agents(world, population)
                    best_agent_index = 0
                    tick = 0
                    status_message = "reset"
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    speed_index = min(speed_index + 1, len(SPEEDS) - 1)
                elif event.key == pygame.K_MINUS:
                    speed_index = max(speed_index - 1, 0)
                elif event.key == pygame.K_LEFTBRACKET:
                    set_mutation_rate(population, -0.005)
                    status_message = f"mutation {population.config.mutation_rate:.1%}"
                elif event.key == pygame.K_RIGHTBRACKET:
                    set_mutation_rate(population, 0.005)
                    status_message = f"mutation {population.config.mutation_rate:.1%}"
                elif event.key == pygame.K_b:
                    show_best_only = True
                elif event.key == pygame.K_a:
                    show_best_only = False
                elif event.key == pygame.K_n:
                    agents, best_agent_index = finish_generation(world, population, agents)
                    tick = 0
                elif event.key == pygame.K_s:
                    save_best_genome(
                        SAVE_PATH,
                        world=world,
                        population=population,
                        agents=agents,
                        best_agent_index=best_agent_index,
                    )
                    status_message = f"saved {SAVE_PATH}"
                elif event.key == pygame.K_l:
                    try:
                        load_saved_genome_into_population(SAVE_PATH, population=population)
                    except FileNotFoundError:
                        status_message = "no saved genome"
                    else:
                        agents = spawn_agents(world, population)
                        best_agent_index = 0
                        tick = 0
                        status_message = f"loaded {SAVE_PATH}"

        if not paused:
            for _ in range(SPEEDS[speed_index]):
                for agent in agents:
                    world.step_agent(agent)
                tick += 1
                if tick >= config.world.ticks_per_generation or all_agents_finished(agents):
                    agents, best_agent_index = finish_generation(world, population, agents)
                    tick = 0
                    break

        if not show_best_only:
            best_agent_index = max(
                range(len(agents)),
                key=lambda index: agent_fitness(world, agents[index]),
            )
        best_agent = agents[best_agent_index]
        renderer.draw(
            world,
            agents,
            best_agent,
            population,
            speed_label=f"{SPEEDS[speed_index]}x",
            paused=paused,
            show_best_only=show_best_only,
            status_message=status_message,
        )
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run EvoForge.")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--report-every", type=int, default=0)
    args = parser.parse_args()
    if args.headless:
        run_headless(args.generations, report_every=args.report_every)
    else:
        run_visual()


if __name__ == "__main__":
    main()
