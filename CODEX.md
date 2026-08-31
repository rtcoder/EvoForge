# EvoForge

## 1. Project Overview

**EvoForge** is an educational evolutionary AI simulation project.

The main goal is to learn and implement from scratch:

- genetic algorithms,
- evolutionary optimization,
- population-based learning,
- mutation,
- crossover,
- selection,
- fitness functions,
- neural networks,
- neuroevolution,
- emergent behaviour,
- predator-prey coevolution.

The project must prioritize **understanding the algorithms** over using ready-made AI frameworks.

Do not use libraries that implement genetic algorithms, NEAT, reinforcement learning, or evolutionary strategies for us.

Core algorithms should be implemented manually.

---

# 2. Main Concept

The application simulates a population of autonomous agents.

Each generation contains multiple agents trying to solve the same task.

Example:

```text
Generation 1

50 agents
    ↓
simulation
    ↓
fitness evaluation
    ↓
selection of best agents
    ↓
mutation / crossover
    ↓
Generation 2
```

The process repeats until agents learn to solve the environment effectively.

The project should visually demonstrate how useful behaviour emerges through evolution.

---

# 3. Technology Stack

Use:

- Python 3.12+
- NumPy
- Pygame

Optional development dependencies:

- pytest
- ruff
- mypy

Do not use:

- PyTorch
- TensorFlow
- Keras
- NEAT libraries
- genetic algorithm libraries
- reinforcement learning frameworks

The neural network implementation should initially be written manually using NumPy.

---

# 4. Project Philosophy

The project is primarily educational.

Code should therefore be:

- readable,
- modular,
- strongly typed where reasonable,
- easy to debug,
- easy to visualize,
- easy to modify during experiments.

Prefer:

- simple implementations,
- explicit algorithms,
- small classes,
- deterministic behaviour when seeds are provided.

Avoid unnecessary abstractions.

Follow:

- KISS
- DRY
- YAGNI

Complex evolutionary logic should contain comments explaining **why** something is implemented that way.

---

# 5. Initial Project Structure

Use approximately:

```text
evoforge/
├── main.py
├── config.py
│
├── simulation/
│   ├── __init__.py
│   ├── world.py
│   ├── agent.py
│   ├── obstacle.py
│   ├── target.py
│   └── sensors.py
│
├── evolution/
│   ├── __init__.py
│   ├── genome.py
│   ├── population.py
│   ├── selection.py
│   ├── mutation.py
│   ├── crossover.py
│   └── fitness.py
│
├── neural/
│   ├── __init__.py
│   └── network.py
│
├── ui/
│   ├── __init__.py
│   ├── renderer.py
│   ├── dashboard.py
│   └── charts.py
│
├── persistence/
│   ├── __init__.py
│   ├── genome_storage.py
│   └── experiment_storage.py
│
├── experiments/
│   └── README.md
│
└── tests/
```

The structure may evolve when justified.

Do not over-engineer the first version.

---

# 6. Development Roadmap

Development should happen incrementally.

Do not immediately build the final ecosystem simulation.

Each phase must work independently before proceeding to the next one.

---

# Phase 1 — Basic Simulation

Create a simple 2D world.

The world contains:

- rectangular boundaries,
- one spawn area,
- one target,
- optional static obstacles.

Agents are displayed as simple circles or rectangles.

Initial movement may be random.

Required features:

- simulation tick,
- fixed timestep,
- configurable simulation speed,
- collision detection,
- reset simulation,
- agent position and velocity.

Example:

```text
┌─────────────────────────────────┐
│                                 │
│ START                           │
│ ● ● ● ●                         │
│                                 │
│            █████                │
│            █████          ★     │
│                           GOAL  │
└─────────────────────────────────┘
```

---

# Phase 2 — Genome Based Movement

Each agent receives a genome containing a predefined sequence of actions.

Example:

```text
RIGHT
RIGHT
UP
UP
LEFT
RIGHT
DOWN
...
```

Possible representation:

```python
genome = [
    Direction.RIGHT,
    Direction.RIGHT,
    Direction.UP,
    Direction.LEFT,
]
```

The genome determines the movement of the agent during the simulation.

No neural network yet.

The goal of this phase is to understand genetic algorithms without additional complexity.

---

# Phase 3 — Fitness Function

Implement fitness evaluation.

Initial fitness should reward getting closer to the target.

Example concept:

```python
fitness = 1 / (distance_to_goal + 1)
```

Possible bonuses:

```text
reached target
fast completion
distance travelled toward target
checkpoints reached
```

Possible penalties:

```text
collision
standing still
moving away from target
excessive simulation time
```

Fitness logic must be isolated from the Agent implementation.

It must be easy to replace fitness functions during experiments.

---

# Phase 4 — Population

Introduce configurable population size.

Default:

```text
population_size = 50
```

Each population contains agents with independent genomes.

Track:

- generation number,
- best fitness,
- average fitness,
- worst fitness,
- successful agents,
- population diversity.

---

# Phase 5 — Selection

Implement parent selection.

Start with simple elitism.

Example:

```text
Population: 50

Top 5:
    preserved

Next generation:
    5 elites
    35 mutated descendants
    5 crossover descendants
    5 random agents
```

The percentages must be configurable.

Do not hardcode selection policy into Population.

Selection should be replaceable later.

---

# Phase 6 — Mutation

Implement genome mutation.

Example:

```python
if random.random() < mutation_rate:
    gene = random_direction()
```

Configuration:

```text
mutation_rate
mutation_strength
```

Allow mutation rate to be changed while the simulation is running.

---

# Phase 7 — Crossover

Implement crossover between two parents.

Start with single-point crossover.

Example:

```text
Parent A

→ → ↑ ↑ | ← ← ↓ ↓

Parent B

↑ ↑ ← ↓ | → → ← ←

Child

→ → ↑ ↑ | → → ← ←
```

Later possible strategies:

- two-point crossover,
- uniform crossover.

---

# Phase 8 — Evolution Dashboard

Create a visible statistics panel.

Display at least:

```text
EVOLUTION

Generation:       142
Population:        50

Best fitness:    912.2
Average fitness: 447.5
Worst fitness:    12.1

Reached goal:      19

Mutation rate:      5%
```

Add fitness history chart.

Track:

- best fitness per generation,
- average fitness per generation,
- success rate.

The chart should make evolutionary progress visible.

---

# 7. Simulation Controls

Add keyboard controls.

Suggested defaults:

```text
SPACE
pause / resume

R
restart experiment

+
increase simulation speed

-
decrease simulation speed

B
display only best agent

A
display all agents

V
toggle sensors

S
save best genome

L
load saved genome

N
force next generation
```

Controls should be displayed somewhere in the UI.

---

# Phase 9 — Neural Network

Replace predefined movement sequences with a neural network.

Do not use an ML framework.

Implement a small feed-forward neural network using NumPy.

Example architecture:

```text
inputs
   ↓
hidden layer
   ↓
hidden layer
   ↓
outputs
```

Possible first architecture:

```text
8 inputs
16 hidden neurons
8 hidden neurons
2 outputs
```

Use a simple activation function such as:

```python
np.tanh()
```

No backpropagation.

The neural network is not trained using gradient descent.

Its weights are evolved.

---

# 8. Neural Genome

Once neuroevolution is introduced, the genome represents the neural network parameters.

Example:

```text
Genome

weights layer 1
biases layer 1

weights layer 2
biases layer 2

weights layer 3
biases layer 3
```

Mutation modifies these parameters.

Example:

```python
child_weights = parent_weights + random_noise
```

Gaussian mutation is recommended:

```python
noise = np.random.normal(
    loc=0,
    scale=mutation_strength,
    size=weights.shape,
)
```

---

# Phase 10 — Sensors

Agents should no longer know the entire state of the world directly.

Instead, introduce sensors.

Possible inputs:

```text
distance to goal
angle to goal
velocity
rotation
distance to wall ahead
distance to wall left
distance to wall right
```

Later introduce raycast-style sensors.

Example:

```text
          ↑

      ↖   │   ↗

←──────── ● ────────→

      ↙   │   ↘

          ↓
```

Possible configuration:

```text
8 rays
maximum sensor distance
```

The normalized ray distances become neural network inputs.

---

# 9. Neural Network Outputs

For continuous movement use:

```text
output 1:
steering

output 2:
throttle
```

Values should be normalized.

For example:

```text
steering:
-1 = rotate left
 0 = straight
 1 = rotate right

throttle:
-1 = reverse
 0 = stop
 1 = forward
```

This is preferred over discrete movement once neuroevolution is implemented.

---

# Phase 11 — Food and Energy

Extend the environment into a survival simulation.

Add food objects.

Agents have:

```text
energy
age
health
```

Movement consumes energy.

Food restores energy.

Example fitness:

```text
fitness =
    survival_time
    + food_collected * food_reward
```

The algorithm should not explicitly tell agents to look for food.

Natural selection should make food-seeking behaviour advantageous.

---

# Phase 12 — Multi-Agent Competition

Multiple agents compete for limited resources.

Example:

```text
100 agents
30 food objects
```

Possible emergent strategies may include:

- searching,
- following other agents,
- avoiding crowded areas,
- camping near food locations,
- stealing resources.

Do not explicitly program these behaviours.

The simulation should make them possible through evolution.

---

# Phase 13 — Predator and Prey

Introduce two independent populations.

## Prey

Objective:

```text
survive
find resources
avoid predators
```

Fitness example:

```python
fitness = survival_time + food_collected * 20
```

## Predator

Objective:

```text
hunt prey
```

Fitness example:

```python
fitness = kills * 100 + survival_time
```

Both populations evolve independently.

This should create a coevolutionary arms race.

---

# Phase 14 — Continuous Evolution

Eventually remove discrete generations.

Agents exist continuously in the world.

Each agent has:

```text
age
energy
genome
fitness / reproductive success
```

Agents may reproduce if they satisfy configurable requirements.

Example:

```text
energy > reproduction_threshold
```

Child genome:

```text
parent A
+
parent B
+
mutation
```

Agents die when:

```text
energy <= 0

or

age >= maximum_age
```

At this stage the simulation becomes a small artificial ecosystem.

---

# 10. Genetic Diversity

Avoid collapsing the entire population into nearly identical genomes.

Track genetic diversity.

Possible mechanisms:

- random immigrants,
- adaptive mutation rate,
- mutation strength,
- multiple parents,
- diversity bonuses.

Initial recommended population reproduction:

```text
10% elites
60% mutated descendants
20% crossover descendants
10% random genomes
```

All values must be configurable.

---

# 11. Random Seeds

Support deterministic experiments.

Configuration:

```python
random_seed = 12345
```

Both Python random and NumPy RNG should use the configured seed.

A saved experiment should contain its seed.

This allows experiments to be reproduced.

---

# 12. Configuration

Keep major parameters configurable.

Example:

```text
simulation:
    width
    height
    ticks_per_second
    generation_duration
    simulation_speed

population:
    size
    elite_count
    random_agent_count

evolution:
    mutation_rate
    mutation_strength
    crossover_rate

agent:
    speed
    rotation_speed
    radius

neural_network:
    hidden_layers
    activation

sensors:
    ray_count
    ray_distance
```

A Python config structure is acceptable initially.

Later it may be moved to YAML or JSON.

---

# 13. Saving Genomes

Allow saving the best agent.

Store:

```text
generation
fitness
genome
network architecture
mutation settings
random seed
experiment configuration
```

Suggested format:

```text
JSON
+
NumPy arrays where appropriate
```

Saved agents should be loadable into another simulation.

---

# 14. Experiment System

Eventually introduce named experiments.

Example:

```text
experiments/

maze-001/
maze-002/
food-search-001/
predator-prey-001/
```

Each experiment should preserve:

```text
configuration
random seed
fitness history
best genome
generation statistics
```

This allows comparison between fitness functions and evolutionary strategies.

---

# 15. Metrics

Collect metrics per generation.

Required:

```text
generation
best_fitness
average_fitness
median_fitness
worst_fitness
success_count
success_rate
population_diversity
```

Later:

```text
average_age
average_energy
food_collected
kills
births
deaths
```

Metrics should not depend on rendering.

The simulation should eventually be able to run headlessly.

---

# 16. Headless Mode

Rendering and simulation logic must remain separate.

Eventually support:

```bash
python main.py
```

for normal visual simulation and something similar to:

```bash
python main.py --headless
```

for accelerated training.

Headless mode should allow evolution to run significantly faster than real-time.

---

# 17. Simulation Speed

The user should be able to watch evolution at normal speed or accelerate it.

Possible speeds:

```text
1x
2x
5x
10x
50x
MAX
```

At high speeds rendering can be reduced.

For example:

```text
render every 10 simulation ticks
```

Headless mode should skip rendering entirely.

---

# 18. Visualization

The UI should clearly distinguish:

- agents,
- best agent,
- target,
- obstacles,
- food,
- predators,
- prey,
- sensors.

The best agent may have an additional outline or marker.

Do not spend excessive development time on visual polish early in the project.

Functionality and observability are more important.

---

# 19. Debug Visualization

Support optional debug overlays.

Possible visualizations:

```text
sensor rays
agent direction
velocity vector
target direction
fitness
agent ID
parent IDs
generation
```

Debug visualization should be toggleable.

---

# 20. Evolution Debugging

Evolutionary algorithms can appear to work while actually exploiting a broken fitness function.

Therefore provide tools for inspecting:

```text
best agent
worst agent
random agent
fitness components
genome
parentage
mutation amount
```

When possible, fitness should expose individual components.

Example:

```text
Fitness: 821.4

distance reward:     +432.0
goal reward:         +500.0
collision penalty:   -100.0
time penalty:         -10.6
```

---

# 21. Fitness Function Rule

Never optimize the implementation specifically for a desired behaviour unless that behaviour is part of the fitness definition.

One purpose of the project is to observe unexpected strategies.

Avoid hardcoding behaviour such as:

```python
if food_visible:
    move_toward_food()
```

Instead provide sensory information and let the evolved neural network decide what to do.

---

# 22. Important Educational Goals

While implementing the project, code and documentation should make it possible to understand:

## Genetic algorithms

- genome
- phenotype
- population
- fitness
- selection
- elitism
- crossover
- mutation

## Evolutionary problems

- local optima
- premature convergence
- loss of genetic diversity
- exploration vs exploitation
- fitness shaping
- deceptive fitness functions

## Neuroevolution

- neural network encoding
- weight mutation
- behaviour emergence
- topology limitations
- sensory inputs
- action outputs

## Artificial life

Later phases should expose concepts such as:

- competition,
- resource scarcity,
- natural selection,
- predator-prey dynamics,
- coevolution,
- reproductive success,
- emergent behaviour.

---

# 23. Testing

Unit tests should cover algorithms that can be tested deterministically.

Important tests:

```text
mutation modifies genomes correctly
mutation rate 0 produces identical genome
mutation rate 1 mutates expected genes
crossover produces correct child
selection chooses valid parents
fitness calculation is correct
network forward pass has correct dimensions
genome serialization/deserialization
random seed produces deterministic result
```

UI rendering does not require extensive automated testing initially.

---

# 24. Logging

Do not print information for every simulation tick.

Log important evolutionary events:

```text
Generation 42 completed
Best fitness: 912.53
Average fitness: 481.20
Successful agents: 17/50
Diversity: 0.61
```

Optionally log when a new all-time record is achieved.

---

# 25. Performance

Simulation performance matters because many generations may need to be evaluated.

However:

**correctness and clarity come before premature optimization.**

Initial implementation may use normal Python objects.

Later optimizations may include:

- NumPy vectorization,
- batched neural network evaluation,
- spatial indexing,
- reduced rendering frequency,
- headless execution,
- multiprocessing.

Do not introduce these until profiling shows they are required.

---

# 26. Git Workflow

Implement the project in small logical commits.

Example:

```text
feat: add basic simulation world

feat: implement genome movement

feat: add fitness evaluation

feat: add population evolution

feat: implement mutation

feat: implement crossover

feat: add evolution dashboard

feat: add neural network

feat: introduce agent sensors
```

Avoid large commits containing several unrelated phases.

---

# 27. Documentation

Maintain:

```text
README.md
CODEX.md
docs/
```

README should eventually explain:

- what EvoForge is,
- installation,
- how to run,
- controls,
- screenshots,
- basic evolutionary algorithm.

Additional documentation can explain experiments and algorithms.

---

# 28. First Milestone

Do not begin with neural networks.

The first milestone is complete when:

- a 2D map exists,
- 50 agents spawn,
- every agent contains a sequence genome,
- agents execute genome instructions,
- fitness is calculated,
- best agents are selected,
- mutation exists,
- crossover exists,
- generations automatically repeat,
- fitness improves across generations,
- statistics are visible.

The first version should demonstrate something approximately like:

```text
Generation 1
agents move almost randomly

Generation 10
agents begin moving toward the target

Generation 30
some agents reach the target

Generation 100
many agents reach the target efficiently
```

Only after this milestone is working should neural networks be introduced.

---

# 29. Second Milestone

Replace sequence genomes with evolved neural networks.

Complete when:

- agents have sensors,
- neural network receives sensor values,
- neural network controls movement,
- neural weights are encoded as genomes,
- mutation modifies weights,
- crossover can combine neural genomes,
- agents evolve navigation behaviour.

---

# 30. Long-Term Goal

The final project should become an evolutionary simulation laboratory rather than one hardcoded demo.

Desired architecture:

```text
                EvoForge

                    │

        ┌───────────┴───────────┐
        │                       │

     Engine                 Experiments

        │                       │

   evolution                 maze
   neural                    navigation
   simulation                food
   metrics                   predators
   renderer                  ecosystem
```

The same evolutionary engine should eventually be usable for different environments.

Possible experiments:

```text
Maze Solver

Obstacle Course

Food Search

Resource Competition

Predator vs Prey

Continuous Ecosystem

Cooperative Agents

Evolution of Swarming

Evolution of Communication
```

---

# 31. Codex Instructions

When implementing this repository:

1. Implement only the requested phase unless a dependency requires additional work.
2. Do not jump ahead to later roadmap phases.
3. Preserve separation between simulation, evolution, neural networks and rendering.
4. Prefer explicit educational implementations over clever abstractions.
5. Do not introduce external AI/evolution libraries.
6. Add tests for evolutionary algorithms where practical.
7. Keep configuration centralized.
8. Keep algorithms deterministic when a seed is supplied.
9. Explain non-obvious evolutionary logic with concise comments.
10. Do not hardcode behaviour that should emerge through evolution.
11. Do not optimize before profiling.
12. Keep the simulation capable of eventually running without the UI.
13. When introducing a new evolutionary mechanism, document what problem it solves.
14. Do not change existing evolutionary behaviour silently.
15. If an algorithmic decision has multiple reasonable approaches, prefer the simplest implementation and document the trade-off.

---

# 32. Initial Task

Start by implementing **Phase 1 — Basic Simulation**.

Create:

- project structure,
- dependency configuration,
- application entry point,
- Pygame window,
- simulation loop,
- world,
- agent,
- target,
- static obstacle support,
- collision handling,
- configurable timestep,
- pause/resume,
- restart.

Do **not** implement genetic algorithms yet.

The result should provide a clean foundation for implementing genome-based agents in the next step.