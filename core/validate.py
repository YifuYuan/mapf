# mapf_env/core/validate.py

from __future__ import annotations

from typing import Dict, Optional, Literal, Any, Tuple
import numpy as np


Connectivity = Literal["4", "8"]


def _allowed_deltas(connectivity: Connectivity):
    """Return a set of allowed (dr, dc) moves."""
    four = {
        (0, 0),   # wait
        (0, 1),   # right
        (0, -1),  # left
        (1, 0),   # down
        (-1, 0),  # up
    }
    if connectivity == "4":
        return four

    # 8-connected = 4-connected + diagonals
    diag = {
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    }
    return four | diag


def validate_paths(
    grid: np.ndarray,
    paths: np.ndarray,
    *,
    starts: Optional[np.ndarray] = None,
    goals: Optional[np.ndarray] = None,
    connectivity: Connectivity = "4",
) -> Dict[str, Any]:
    if paths.ndim != 3 or paths.shape[2] != 2:
        raise ValueError(f"paths must have shape (T, N, 2); got {paths.shape}")

    H, W = grid.shape
    T, N, _ = paths.shape

    allowed = _allowed_deltas(connectivity)

    num_vertex_collisions = 0
    num_edge_collisions = 0
    num_illegal_moves = 0
    num_out_of_bounds = 0
    num_on_obstacle = 0

    first_error: Optional[Dict[str, Any]] = None

    # --- per-timestep position validity ---
    for t in range(T):
        pos_t = paths[t]  # shape (N, 2)
        rows = pos_t[:, 0]
        cols = pos_t[:, 1]

        # bounds
        oob_mask = (rows < 0) | (rows >= H) | (cols < 0) | (cols >= W)
        if np.any(oob_mask):
            idxs = np.where(oob_mask)[0]
            num_out_of_bounds += int(len(idxs))
            if first_error is None:
                first_error = {
                    "time": t,
                    "type": "bounds",
                    "agents": tuple(int(i) for i in idxs[:4]),
                    "extra": {
                        "positions": [tuple(map(int, pos_t[i])) for i in idxs[:4]]
                    },
                }

        # obstacle
        in_bounds_idxs = np.where(~oob_mask)[0]
        if len(in_bounds_idxs) > 0:
            r_in = rows[in_bounds_idxs]
            c_in = cols[in_bounds_idxs]
            blocked_mask = grid[r_in, c_in] == 1
            if np.any(blocked_mask):
                bad_local = np.where(blocked_mask)[0]
                bad_idxs = in_bounds_idxs[bad_local]
                num_on_obstacle += int(len(bad_idxs))
                if first_error is None:
                    first_error = {
                        "time": t,
                        "type": "obstacle",
                        "agents": tuple(int(i) for i in bad_idxs[:4]),
                        "extra": {
                            "positions": [tuple(map(int, pos_t[i])) for i in bad_idxs[:4]]
                        },
                    }

    # --- move legality (neighbor or wait) ---
    for t in range(1, T):
        prev = paths[t - 1]
        curr = paths[t]
        deltas = curr - prev  # (N, 2)
        for i in range(N):
            dr, dc = int(deltas[i, 0]), int(deltas[i, 1])
            if (dr, dc) not in allowed:
                num_illegal_moves += 1
                if first_error is None:
                    first_error = {
                        "time": t,
                        "type": "illegal_move",
                        "agents": (int(i),),
                        "extra": {"delta": (dr, dc)},
                    }

    # --- vertex collisions ---
    for t in range(T):
        pos_t = paths[t]
        # map cell -> list of agents
        cell_to_agents: Dict[Tuple[int, int], list] = {}
        for i in range(N):
            cell = (int(pos_t[i, 0]), int(pos_t[i, 1]))
            cell_to_agents.setdefault(cell, []).append(i)

        for cell, agents in cell_to_agents.items():
            if len(agents) > 1:
                # count number of unordered pairs
                k = len(agents)
                num_vertex_collisions += k * (k - 1) // 2
                if first_error is None:
                    first_error = {
                        "time": t,
                        "type": "vertex_collision",
                        "agents": tuple(int(a) for a in agents),
                        "extra": {"cell": cell},
                    }

    # --- edge collisions (swaps) ---
    for t in range(1, T):
        prev = paths[t - 1]
        curr = paths[t]
        for i in range(N):
            for j in range(i + 1, N):
                if (
                    prev[i, 0] == curr[j, 0]
                    and prev[i, 1] == curr[j, 1]
                    and prev[j, 0] == curr[i, 0]
                    and prev[j, 1] == curr[i, 1]
                ):
                    num_edge_collisions += 1
                    if first_error is None:
                        first_error = {
                            "time": t,
                            "type": "edge_collision",
                            "agents": (int(i), int(j)),
                            "extra": {
                                "from_to_i": (
                                    int(prev[i, 0]),
                                    int(prev[i, 1]),
                                    int(curr[i, 0]),
                                    int(curr[i, 1]),
                                ),
                                "from_to_j": (
                                    int(prev[j, 0]),
                                    int(prev[j, 1]),
                                    int(curr[j, 0]),
                                    int(curr[j, 1]),
                                ),
                            },
                        }

    # --- success flag (if goals provided) ---
    if goals is not None:
        if goals.shape != (paths.shape[1], 2):
            raise ValueError(
                f"goals must have shape (N, 2); got {goals.shape}, N={paths.shape[1]}"
            )
        final_pos = paths[-1]
        success = bool(np.all(final_pos == goals))
    else:
        success = None

    ok = (
        num_out_of_bounds == 0
        and num_on_obstacle == 0
        and num_illegal_moves == 0
        and num_vertex_collisions == 0
        and num_edge_collisions == 0
        and (success is not False)
    )

    return {
        "ok": ok,
        "first_error": first_error,
        "num_vertex_collisions": int(num_vertex_collisions),
        "num_edge_collisions": int(num_edge_collisions),
        "num_illegal_moves": int(num_illegal_moves),
        "num_out_of_bounds": int(num_out_of_bounds),
        "num_on_obstacle": int(num_on_obstacle),
        "success": success,
    }
