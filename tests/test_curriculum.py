import unittest

from evoforge.evolution.curriculum import CurriculumState, select_curriculum_start


class CurriculumTest(unittest.TestCase):
    def test_select_curriculum_start_stays_at_origin_without_stagnation(self) -> None:
        state = CurriculumState(
            best_checkpoint=12,
            best_step_index=80,
            stagnant_generations=10,
            activation_generations=20,
        )

        start = select_curriculum_start(state, agent_index=0, population_size=10)

        self.assertFalse(start.enabled)
        self.assertEqual(start.checkpoint_index, -1)
        self.assertEqual(start.step_index, 0)

    def test_select_curriculum_start_uses_frontier_for_some_agents_after_stagnation(self) -> None:
        state = CurriculumState(
            best_checkpoint=12,
            best_step_index=80,
            stagnant_generations=20,
            activation_generations=20,
            fraction=0.5,
        )

        first = select_curriculum_start(state, agent_index=0, population_size=10)
        later = select_curriculum_start(state, agent_index=8, population_size=10)

        self.assertTrue(first.enabled)
        self.assertEqual(first.checkpoint_index, 11)
        self.assertEqual(first.step_index, 80)
        self.assertFalse(later.enabled)


if __name__ == "__main__":
    unittest.main()
