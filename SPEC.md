# MAPF Environment SPEC

Version: 0.1  
Status: DRAFT (frozen for this project)

This document fixes the conventions for our minimal MAPF environment built on
MovingAI-style grid maps. All planners / learners / visualizers **must**
follow these conventions.

---

## 1. Scope

- We use **only grid maps** from the MovingAI MapF benchmarks.
- Environment is purely discrete-time, grid-based.
- No external simulator (no physics); this is a logical MAPF world.
- The env:
  - loads a `.map` file (MovingAI format),
  - tracks `N` agents on the grid,
  - applies joint actions each timestep,
  - can visualize maps + paths,
  - can run collision checks.

Planners / learners / reward functions will be built separately on top of this.

---

## 2. Coordinate System & Map Representation

- Grid cells are indexed as **(row, col)**.
- Both `row` and `col` are **0-based integers**.
- Origin `(0, 0)` = **top-left** cell of the map.
- Increasing `row` → moves **down** on the screen.
- Increasing `col` → moves **right** on the screen.

### 2.1. Map storage

- `map[row, col]` or `grid[row][col]` is the canonical access pattern.
- Obstacles:
  - A cell is **blocked** if the underlying MovingAI map has a wall/obstacle
    (e.g., `'@'`, `'T'`, etc.).
  - A cell is **free** if it is traversable (`'.'` or `'G'` / start/goal cells,
    depending on the map format we parse).
- The environment exposes:
  - `height` = number of rows
  - `width`  = number of cols

No alternative coordinate convention is allowed inside the env core.

---

## 3. Agents, State, and Time

- Number of agents: `N` (fixed per episode).
- Time is **discrete**: `t = 0, 1, 2, ...`.

### 3.1. Agent positions

- At any step `t`, each agent `i` has a **single cell position**:
  - `pos[t, i] = (row, col)`.

- A full joint state can be represented as:
  - `state[t] = [(r_0, c_0), (r_1, c_1), ..., (r_{N-1}, c_{N-1})]`.

---

## 4. Path Format

We standardize one canonical path tensor format; all planners / learners must
produce paths in this format.

- `paths` has shape: **(T, N, 2)**

Where:

- `T` = total number of time steps in the plan.
- `N` = number of agents.
- `paths[t, i] = (row, col)` = position of agent `i` at time `t`.

Conventions:

- `t = 0` row contains **start positions**.
- `t = T-1` row contains **final positions** (usually goals, but not enforced at env-level).
- If an agent reaches its goal early and waits, its future positions must
  keep repeating the goal cell (no padding / sentinel values).

The visualizer and collision checker will assume this `paths[t, i]` layout.

---

## 5. Action Space

We use **4-connected grid moves + WAIT** as the core action space.

### 5.1. Action IDs

Define the action set and their deltas in **(row, col)** coordinates:

- `0: WAIT   → ( 0,  0)`
- `1: RIGHT  → ( 0, +1)`
- `2: DOWN   → (+1,  0)`
- `3: UP     → (-1,  0)`
- `4: LEFT   → ( 0, -1)`

(These IDs are fixed and must match across env, planner, and learner.)

Internally we will have:

```python
ACTION_DELTAS = {
    0: (0, 0),   # WAIT
    1: (0, 1),   # RIGHT
    2: (1, 0),   # DOWN
    3: (-1, 0),  # UP
    4: (0, -1),  # LEFT
}
