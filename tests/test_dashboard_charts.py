import unittest

from evoforge.evolution.population import PopulationStats
from evoforge.ui.charts import ChartSeries, history_chart_series


class DashboardChartsTest(unittest.TestCase):
    def test_history_chart_series_keeps_recent_generations_and_scales_values(self) -> None:
        history = [
            PopulationStats(
                generation=index,
                best_fitness=float(index * 10),
                average_fitness=float(index * 5),
                median_fitness=0.0,
                worst_fitness=0.0,
                success_count=index,
            )
            for index in range(1, 8)
        ]

        series = history_chart_series(history, width=60, height=40, max_points=5)

        self.assertEqual(
            series,
            [
                ChartSeries(
                    label="best",
                    color=(80, 220, 140),
                    points=[(0, 40), (15, 30), (30, 20), (45, 10), (60, 0)],
                ),
                ChartSeries(
                    label="average",
                    color=(86, 150, 235),
                    points=[(0, 40), (15, 30), (30, 20), (45, 10), (60, 0)],
                ),
                ChartSeries(
                    label="reached",
                    color=(245, 196, 66),
                    points=[(0, 40), (15, 30), (30, 20), (45, 10), (60, 0)],
                ),
            ],
        )

    def test_history_chart_series_handles_empty_history(self) -> None:
        self.assertEqual(history_chart_series([], width=60, height=40), [])

    def test_history_chart_series_handles_flat_values(self) -> None:
        history = [
            PopulationStats(
                generation=1,
                best_fitness=5.0,
                average_fitness=5.0,
                median_fitness=5.0,
                worst_fitness=5.0,
                success_count=0,
            ),
            PopulationStats(
                generation=2,
                best_fitness=5.0,
                average_fitness=5.0,
                median_fitness=5.0,
                worst_fitness=5.0,
                success_count=0,
            ),
        ]

        series = history_chart_series(history, width=10, height=10)

        self.assertEqual(series[0].points, [(0, 5), (10, 5)])
        self.assertEqual(series[1].points, [(0, 5), (10, 5)])
        self.assertEqual(series[2].points, [(0, 10), (10, 10)])


if __name__ == "__main__":
    unittest.main()
