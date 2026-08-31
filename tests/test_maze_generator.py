import unittest

from evoforge.config import AgentConfig, MazeConfig, WorldConfig
from evoforge.main import build_world
from evoforge.simulation.maze import (
    Maze,
    checkpoints_from_path,
    generate_maze,
    maze_to_obstacles,
)


class MazeGeneratorTest(unittest.TestCase):
    def test_generate_maze_is_deterministic_for_seed(self) -> None:
        config = MazeConfig(columns=9, rows=7, cell_size=40, seed=123)

        first = generate_maze(config)
        second = generate_maze(config)

        self.assertEqual(first.open_cells, second.open_cells)

    def test_generate_maze_keeps_path_between_start_and_goal(self) -> None:
        maze = generate_maze(MazeConfig(columns=11, rows=9, cell_size=40, seed=77))

        self.assertTrue(maze.has_path(maze.start_cell, maze.goal_cell))

    def test_solution_path_starts_at_start_and_ends_at_goal(self) -> None:
        maze = generate_maze(MazeConfig(columns=11, rows=9, cell_size=40, seed=77))

        path = maze.solution_path()

        self.assertEqual(path[0], maze.start_cell)
        self.assertEqual(path[-1], maze.goal_cell)
        self.assertGreater(len(path), 8)

    def test_maze_to_obstacles_keeps_start_and_goal_clear(self) -> None:
        config = MazeConfig(columns=9, rows=7, cell_size=40, seed=9)
        maze = generate_maze(config)

        obstacles = maze_to_obstacles(maze)

        start_center = maze.cell_center(maze.start_cell)
        goal_center = maze.cell_center(maze.goal_cell)
        self.assertFalse(any(obstacle.contains_circle(start_center, 5.0) for obstacle in obstacles))
        self.assertFalse(any(obstacle.contains_circle(goal_center, 5.0) for obstacle in obstacles))

    def test_checkpoints_from_path_include_turns_and_goal(self) -> None:
        maze = Maze(
            columns=5,
            rows=5,
            cell_size=40,
            open_cells=frozenset({(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)}),
            start_cell=(1, 1),
            goal_cell=(3, 3),
        )
        path = [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)]

        checkpoints = checkpoints_from_path(maze, path, spacing=3)

        self.assertEqual(checkpoints, [(140.0, 100.0), (140.0, 140.0)])

    def test_build_world_uses_deterministic_maze_layout(self) -> None:
        world = build_world(
            world_config=WorldConfig(width=640, height=480),
            agent_config=AgentConfig(radius=5.0),
            maze_config=MazeConfig(columns=13, rows=9, cell_size=40, seed=11),
        )

        self.assertGreater(len(world.obstacles), 20)
        self.assertEqual(world.config.spawn_position, (60.0, 60.0))
        self.assertEqual(world.target.position, (460.0, 300.0))
        self.assertGreater(len(world.checkpoints), 3)

    def test_world_with_maze_allows_simple_corridor_path_when_maze_is_open(self) -> None:
        maze = Maze(
            columns=4,
            rows=1,
            cell_size=40,
            open_cells=frozenset({(0, 0), (1, 0), (2, 0), (3, 0)}),
            start_cell=(0, 0),
            goal_cell=(3, 0),
        )
        obstacles = maze_to_obstacles(maze)

        self.assertEqual(obstacles, [])

    def test_maze_to_obstacles_merges_horizontal_wall_runs(self) -> None:
        maze = Maze(
            columns=5,
            rows=1,
            cell_size=40,
            open_cells=frozenset({(4, 0)}),
            start_cell=(4, 0),
            goal_cell=(4, 0),
        )

        obstacles = maze_to_obstacles(maze)

        self.assertEqual(len(obstacles), 1)
        self.assertEqual(obstacles[0].x, 0)
        self.assertEqual(obstacles[0].width, 160)


if __name__ == "__main__":
    unittest.main()
