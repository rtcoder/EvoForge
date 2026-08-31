from __future__ import annotations

from evoforge.evolution.population import Population


def dashboard_lines(
    population: Population,
    *,
    speed_label: str,
    paused: bool,
    show_best_only: bool,
    checkpoints_label: str = "",
    status_message: str = "",
) -> list[str]:
    stats = population.last_stats
    lines = [
        "EVOLUTION",
        f"Generation: {population.generation}",
        f"Population: {len(population.genomes)}",
        f"Speed: {speed_label}",
        f"Mutation: {population.config.mutation_rate:.1%}",
        f"Burst: {'on' if population.burst_active else 'off'}",
        f"Stagnant: {population.stagnant_generations}",
        f"Suffix rolls: {population.suffix_randomizations}",
        f"Curriculum: {'on' if population.curriculum_active else 'off'}",
        f"Frontier CP: {population.best_progress_score}",
        f"Mode: {'paused' if paused else 'running'}",
        f"View: {'best' if show_best_only else 'all'}",
    ]
    if checkpoints_label:
        lines.append(f"Checkpoints: {checkpoints_label}")
    if stats is not None:
        lines.extend(
            [
                f"Best fitness: {stats.best_fitness:.4f}",
                f"Average: {stats.average_fitness:.4f}",
                f"Worst: {stats.worst_fitness:.4f}",
                f"Reached: {stats.success_count}",
            ]
        )
    lines.extend(
        [
            "",
            "SPACE pause",
            "R reset",
            "+/- speed",
            "[/] mutation",
            "B best only",
            "A all agents",
            "N next gen",
            "S save best",
            "L load best",
        ]
    )
    if status_message:
        lines.extend(["", status_message])
    return lines
