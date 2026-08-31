# EvoForge

Educational evolutionary AI simulation written from scratch. A population of
agents tries to learn a route through a generated maze to the yellow target.
Each agent is controlled only by a fixed-length genome of movement directions;
there is no NEAT, reinforcement learning, pathfinding, or ML framework.

The current version includes:

- a deterministic DFS maze generator with static wall obstacles,
- ordered checkpoints placed along turns and longer maze segments,
- agents driven by fixed-length direction genomes,
- checkpoint-first fitness with distance shaping and wall-collision penalties,
- elitism, mutation, simple crossover, and random immigrants,
- protected genome prefixes so discovered route fragments survive mutation,
- burst mutation and suffix randomization after checkpoint stagnation,
- curriculum/frontier spawning for part of the population after long stagnation,
- a Pygame visual runner with dashboard charts,
- a headless runner with progress reports for longer experiments,
- save/load support for the current best genome,
- deterministic unit tests for core evolution and simulation behavior.

## Requirements

- Python 3.12+
- Pygame for visual mode

## How It Learns

The maze is generated at startup from a seed, then converted into rectangular
walls. Agents start near the entrance and execute their genomes one action per
tick. A generation currently has `2200` ticks and genomes are `2200` actions
long, which gives agents enough lifetime to traverse deeper parts of the maze
before evolution evaluates them.

Fitness rewards several signals:

- reaching more ordered checkpoints,
- getting closer to the next checkpoint,
- making progress toward the final target,
- reaching the final target,
- avoiding wall collisions.

When an agent hits a wall it is marked as collided and its fitness is heavily
reduced. If every agent is already finished or collided, the generation ends
early and evolution starts the next one.

To avoid losing discovered route fragments, evolution preserves the genome
prefix up to the best checkpoint step. After enough generations without a new
checkpoint, burst mode raises mutation pressure and randomizes genome suffixes
after the protected prefix. During deeper stagnation, curriculum/frontier
spawning starts part of the population directly from the best known checkpoint,
using the recorded step index, so the search can focus on the unknown part of
the maze instead of repeatedly spending all time on the already learned route.

## Run

Headless smoke run:

```bash
python3 -m evoforge.main --headless --generations 5
```

Longer headless progress run:

```bash
.venv/bin/python -m evoforge.main --headless --generations 80 --report-every 10
```

Visual simulation:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m evoforge.main
```

Controls:

- `SPACE` pause/resume
- `R` reset experiment
- `+` / `-` adjust simulation speed
- `[` / `]` adjust mutation rate
- `B` show best agent only
- `A` show all agents
- `N` force next generation
- `S` save best genome to `experiments/best_genome.json`
- `L` load saved genome from `experiments/best_genome.json`

## Test

```bash
.venv/bin/python -m unittest tests/test_evolution_core.py tests/test_simulation_world.py tests/test_main_flow.py tests/test_dashboard_charts.py tests/test_genome_storage.py tests/test_runtime_controls.py tests/test_maze_generator.py tests/test_curriculum.py -v
```
