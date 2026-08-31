import unittest

from evoforge.config import EvolutionConfig
from evoforge.evolution.controls import adjust_mutation_rate


class RuntimeControlsTest(unittest.TestCase):
    def test_adjust_mutation_rate_returns_new_config_with_clamped_value(self) -> None:
        config = EvolutionConfig(
            population_size=4,
            genome_length=3,
            elite_count=1,
            random_agent_count=0,
            mutation_rate=0.05,
        )

        increased = adjust_mutation_rate(config, 0.02)
        decreased = adjust_mutation_rate(config, -0.10)
        capped = adjust_mutation_rate(config, 2.0)

        self.assertEqual(config.mutation_rate, 0.05)
        self.assertEqual(increased.mutation_rate, 0.07)
        self.assertEqual(decreased.mutation_rate, 0.0)
        self.assertEqual(capped.mutation_rate, 1.0)


if __name__ == "__main__":
    unittest.main()
