from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass

from evoforge.config import MazeConfig
from evoforge.simulation.obstacle import Obstacle

Cell = tuple[int, int]


@dataclass(frozen=True)
class Maze:
    columns: int
    rows: int
    cell_size: int
    open_cells: frozenset[Cell]
    start_cell: Cell
    goal_cell: Cell

    def cell_center(self, cell: Cell) -> tuple[float, float]:
        column, row = cell
        return (
            column * self.cell_size + self.cell_size / 2,
            row * self.cell_size + self.cell_size / 2,
        )

    def has_path(self, start: Cell, goal: Cell) -> bool:
        return bool(self.solution_path(start=start, goal=goal))

    def solution_path(self, start: Cell | None = None, goal: Cell | None = None) -> list[Cell]:
        start = self.start_cell if start is None else start
        goal = self.goal_cell if goal is None else goal
        frontier: deque[Cell] = deque([start])
        visited = {start}
        previous: dict[Cell, Cell | None] = {start: None}
        while frontier:
            cell = frontier.popleft()
            if cell == goal:
                return _reconstruct_path(previous, goal)
            for neighbor in _grid_neighbors(cell):
                if neighbor in self.open_cells and neighbor not in visited:
                    visited.add(neighbor)
                    previous[neighbor] = cell
                    frontier.append(neighbor)
        return []


def generate_maze(config: MazeConfig) -> Maze:
    rng = random.Random(config.seed)
    start = (1, 1)
    goal = (config.columns - 2, config.rows - 2)
    open_cells: set[Cell] = {start}
    visited: set[Cell] = {start}
    stack = [start]

    while stack:
        current = stack[-1]
        neighbors = [
            neighbor
            for neighbor in _logical_neighbors(current)
            if _inside_inner_grid(neighbor, config.columns, config.rows)
            and neighbor not in visited
        ]
        if not neighbors:
            stack.pop()
            continue

        chosen = rng.choice(neighbors)
        wall_between = (
            (current[0] + chosen[0]) // 2,
            (current[1] + chosen[1]) // 2,
        )
        open_cells.add(wall_between)
        open_cells.add(chosen)
        visited.add(chosen)
        stack.append(chosen)

    open_cells.add(goal)
    return Maze(
        columns=config.columns,
        rows=config.rows,
        cell_size=config.cell_size,
        open_cells=frozenset(open_cells),
        start_cell=start,
        goal_cell=goal,
    )


def maze_to_obstacles(maze: Maze) -> list[Obstacle]:
    obstacles: list[Obstacle] = []
    for row in range(maze.rows):
        column = 0
        while column < maze.columns:
            if (column, row) in maze.open_cells:
                column += 1
                continue
            start_column = column
            while column < maze.columns and (column, row) not in maze.open_cells:
                column += 1
            obstacles.append(
                Obstacle(
                    x=start_column * maze.cell_size,
                    y=row * maze.cell_size,
                    width=(column - start_column) * maze.cell_size,
                    height=maze.cell_size,
                )
            )
    return obstacles


def checkpoints_from_path(
    maze: Maze,
    path: list[Cell],
    *,
    spacing: int = 1,
) -> list[tuple[float, float]]:
    if len(path) < 2:
        return []

    checkpoints: list[Cell] = []
    steps_since_checkpoint = 0
    last_direction: Cell | None = None

    for index in range(1, len(path)):
        previous = path[index - 1]
        current = path[index]
        direction = (current[0] - previous[0], current[1] - previous[1])
        is_turn = last_direction is not None and direction != last_direction
        is_goal = current == path[-1]
        steps_since_checkpoint += 1

        if is_turn or is_goal or steps_since_checkpoint >= spacing:
            checkpoints.append(current)
            steps_since_checkpoint = 0

        last_direction = direction

    if checkpoints[-1] != path[-1]:
        checkpoints.append(path[-1])

    return [maze.cell_center(cell) for cell in checkpoints]


def _reconstruct_path(previous: dict[Cell, Cell | None], goal: Cell) -> list[Cell]:
    path: list[Cell] = []
    current: Cell | None = goal
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    return path


def _logical_neighbors(cell: Cell) -> list[Cell]:
    column, row = cell
    return [
        (column + 2, row),
        (column - 2, row),
        (column, row + 2),
        (column, row - 2),
    ]


def _grid_neighbors(cell: Cell) -> list[Cell]:
    column, row = cell
    return [
        (column + 1, row),
        (column - 1, row),
        (column, row + 1),
        (column, row - 1),
    ]


def _inside_inner_grid(cell: Cell, columns: int, rows: int) -> bool:
    column, row = cell
    return 1 <= column < columns - 1 and 1 <= row < rows - 1
