from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from evoforge.config import EvolutionConfig
from evoforge.evolution.genome import Direction, Genome


@dataclass(frozen=True)
class GenomeRecord:
    generation: int
    fitness: float
    genome: Genome
    evolution: EvolutionConfig


def save_genome_record(
    path: Path,
    *,
    generation: int,
    fitness: float,
    genome: Genome,
    config: EvolutionConfig,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "generation": generation,
        "fitness": fitness,
        "genome": [direction.name for direction in genome.actions],
        "evolution": asdict(config),
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def load_genome_record(path: Path) -> GenomeRecord:
    data = json.loads(path.read_text(encoding="utf-8"))
    return GenomeRecord(
        generation=int(data["generation"]),
        fitness=float(data["fitness"]),
        genome=Genome([Direction[name] for name in data["genome"]]),
        evolution=EvolutionConfig(**data["evolution"]),
    )
