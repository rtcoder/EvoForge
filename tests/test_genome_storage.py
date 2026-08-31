import json
import tempfile
import unittest
from pathlib import Path

from evoforge.config import EvolutionConfig
from evoforge.evolution.genome import Direction, Genome
from evoforge.persistence.genome_storage import load_genome_record, save_genome_record


class GenomeStorageTest(unittest.TestCase):
    def test_save_genome_record_writes_reproducible_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "best_genome.json"

            save_genome_record(
                path,
                generation=42,
                fitness=123.5,
                genome=Genome([Direction.RIGHT, Direction.UP, Direction.LEFT]),
                config=EvolutionConfig(
                    population_size=4,
                    genome_length=3,
                    elite_count=1,
                    random_agent_count=0,
                    mutation_rate=0.07,
                    random_seed=99,
                ),
            )

            data = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(data["generation"], 42)
        self.assertEqual(data["fitness"], 123.5)
        self.assertEqual(data["genome"], ["RIGHT", "UP", "LEFT"])
        self.assertEqual(data["evolution"]["mutation_rate"], 0.07)
        self.assertEqual(data["evolution"]["random_seed"], 99)

    def test_load_genome_record_restores_genome_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "best_genome.json"
            path.write_text(
                json.dumps(
                    {
                        "generation": 5,
                        "fitness": 88.0,
                        "genome": ["DOWN", "RIGHT"],
                        "evolution": {
                            "population_size": 4,
                            "genome_length": 2,
                            "elite_count": 1,
                            "random_agent_count": 0,
                            "mutation_rate": 0.03,
                            "random_seed": 12,
                        },
                    }
                ),
                encoding="utf-8",
            )

            record = load_genome_record(path)

        self.assertEqual(record.generation, 5)
        self.assertEqual(record.fitness, 88.0)
        self.assertEqual(record.genome, Genome([Direction.DOWN, Direction.RIGHT]))
        self.assertEqual(record.evolution.mutation_rate, 0.03)


if __name__ == "__main__":
    unittest.main()
