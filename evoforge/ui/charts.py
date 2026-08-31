from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from evoforge.evolution.population import PopulationStats


@dataclass(frozen=True)
class ChartSeries:
    label: str
    color: tuple[int, int, int]
    points: list[tuple[int, int]]


def history_chart_series(
    history: list[PopulationStats],
    *,
    width: int,
    height: int,
    max_points: int = 80,
) -> list[ChartSeries]:
    visible = history[-max_points:]
    if not visible:
        return []

    return [
        ChartSeries(
            label="best",
            color=(80, 220, 140),
            points=_scale_points(visible, width, height, lambda stats: stats.best_fitness),
        ),
        ChartSeries(
            label="average",
            color=(86, 150, 235),
            points=_scale_points(
                visible,
                width,
                height,
                lambda stats: stats.average_fitness,
            ),
        ),
        ChartSeries(
            label="reached",
            color=(245, 196, 66),
            points=_scale_points(visible, width, height, lambda stats: stats.success_count),
        ),
    ]


def _scale_points(
    history: list[PopulationStats],
    width: int,
    height: int,
    value_of: Callable[[PopulationStats], float],
) -> list[tuple[int, int]]:
    values = [float(value_of(stats)) for stats in history]
    low = min(values)
    high = max(values)
    count = len(values)
    if count == 1:
        xs = [width]
    else:
        xs = [round(index * width / (count - 1)) for index in range(count)]

    if high == low:
        y = height // 2 if high > 0 else height
        return [(x, y) for x in xs]

    return [
        (x, round(height - ((value - low) / (high - low)) * height))
        for x, value in zip(xs, values, strict=True)
    ]
