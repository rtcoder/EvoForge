# Initial Evolution Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first playable EvoForge slice: a 2D world, genome-driven movement, fitness scoring, and simple generational evolution.

**Architecture:** Keep simulation, evolution, rendering, and configuration separate. Core algorithms are plain Python and NumPy-friendly, while Pygame stays at the application edge.

**Tech Stack:** Python 3.12+, Pygame for rendering, pytest for deterministic tests.

**Spec:** `CODEX.md`

## Global Constraints

- Do not use libraries that implement genetic algorithms, NEAT, reinforcement learning, or evolutionary strategies.
- Core algorithms must be implemented manually.
- Prioritize readable, modular, deterministic code.
- Rendering and simulation logic remain separate.

---

### Task 1: Deterministic Evolution Core

**Files:**
- Create: `evoforge/config.py`
- Create: `evoforge/evolution/genome.py`
- Create: `evoforge/evolution/mutation.py`
- Create: `evoforge/evolution/crossover.py`
- Create: `evoforge/evolution/fitness.py`
- Create: `evoforge/evolution/population.py`
- Test: `tests/test_evolution_core.py`

**Interfaces:**
- Produces: `Direction`, `Genome`, `mutate_genome`, `single_point_crossover`, `distance_to_target_fitness`, `Population`.

- [ ] Write failing tests for mutation rate 0, mutation rate 1, crossover, fitness, and deterministic population advancement.
- [ ] Run `python3 -m pytest tests/test_evolution_core.py -v` and verify the expected import failures.
- [ ] Implement the minimal evolution core.
- [ ] Run `python3 -m pytest tests/test_evolution_core.py -v` and verify the tests pass.

### Task 2: Simulation World

**Files:**
- Create: `evoforge/simulation/agent.py`
- Create: `evoforge/simulation/world.py`
- Create: `evoforge/simulation/obstacle.py`
- Create: `evoforge/simulation/target.py`
- Test: `tests/test_simulation_world.py`

**Interfaces:**
- Consumes: `Genome`, `Direction`, `WorldConfig`, `AgentConfig`.
- Produces: `Agent`, `World`, `Obstacle`, `Target`.

- [ ] Write failing tests for agent movement, boundary collision, target reaching, and reset.
- [ ] Run `python3 -m pytest tests/test_simulation_world.py -v` and verify the expected failures.
- [ ] Implement the minimal simulation model.
- [ ] Run `python3 -m pytest tests/test_simulation_world.py -v` and verify the tests pass.

### Task 3: Pygame Runner And UI

**Files:**
- Create: `evoforge/main.py`
- Create: `evoforge/ui/renderer.py`
- Create: `evoforge/ui/dashboard.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `Population`, `World`, configuration dataclasses.
- Produces: `python3 -m evoforge.main` visual runner.

- [ ] Add a Pygame app loop with fixed timestep, pause/reset/speed controls, and next-generation control.
- [ ] Render agents, best agent, target, obstacles, and concise stats.
- [ ] Document install and run commands in `README.md`.
- [ ] Run unit tests and a short import/smoke check for `evoforge.main`.
