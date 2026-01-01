# mapf_env/core/env.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple

import numpy as np

from .instance import MAPFInstance

MotionType = Literal["4", "8"]


def _allowed_deltas(motion: MotionType):
    """Return a dict: action_id -> (dr, dc)."""
    four = {
        0: (0, 0),   # WAIT
        1: (0, 1),   # RIGHT
        2: (1, 0),   # DOWN
        3: (-1, 0),  # UP
        4: (0, -1),  # LEFT
    }
    if motion == "4":
        return four

    diag = {
        5: (1, 1),
        6: (1, -1),
        7: (-1, 1),
        8: (-1, -1),
    }
    return {**four, **diag}


@dataclass
class MAPFState:

    t: int
    pos: np.ndarray
    goals: np.ndarray
    grid: np.ndarray


class MAPFEnv:

    def __init__(self, instance: MAPFInstance, motion: MotionType = "4"):
        if motion not in ("4", "8"):
            raise ValueError(f"motion must be '4' or '8', got {motion}")

        self.instance = instance
        self.motion: MotionType = motion
        self._deltas = _allowed_deltas(motion)

        self.grid = instance.grid
        self.goals = instance.goals
        self.num_agents = instance.num_agents

        self.t = 0
        self.pos = None  # will be set in reset()

    # ---------------------------------------------------------------
    # Core API
    # ---------------------------------------------------------------
    def reset(self, instance: Optional[MAPFInstance] = None) -> MAPFState:
        """
        Reset environment to the start state.

        If `instance` is given, it replaces the current one.
        """
        if instance is not None:
            self.instance = instance
            self.grid = instance.grid
            self.goals = instance.goals
            self.num_agents = instance.num_agents

        self.t = 0
        # Copy to avoid aliasing with instance.starts
        self.pos = self.instance.starts.astype(int).copy()

        return MAPFState(
            t=self.t,
            pos=self.pos.copy(),
            goals=self.goals.copy(),
            grid=self.grid,
        )

    def step(self, joint_action: np.ndarray) -> Tuple[MAPFState, Dict]:

        actions = np.asarray(joint_action).reshape(-1)
        if actions.shape[0] != self.num_agents:
            raise ValueError(
                f"Expected {self.num_agents} actions, got {actions.shape[0]}"
            )

        prev_pos = self.pos.copy()
        new_pos = prev_pos.copy()

        H, W = self.grid.shape

        invalid_moves: List[int] = []
        unknown_actions: List[int] = []

        # --- apply moves with "invalid → stay" semantics ---
        for i in range(self.num_agents):
            a = int(actions[i])

            if a not in self._deltas:
                # Treat unknown action as WAIT
                unknown_actions.append(i)
                dr, dc = 0, 0
            else:
                dr, dc = self._deltas[a]

            r, c = int(prev_pos[i, 0]), int(prev_pos[i, 1])
            r_new = r + dr
            c_new = c + dc

            # Check bounds + obstacles
            if (
                r_new < 0
                or r_new >= H
                or c_new < 0
                or c_new >= W
                or self.grid[r_new, c_new] == 1
            ):
                # invalid move → stay
                invalid_moves.append(i)
                r_new, c_new = r, c

            new_pos[i, 0] = r_new
            new_pos[i, 1] = c_new

        self.pos = new_pos
        self.t += 1

        # --- compute collisions for this step ---
        vertex_collisions = self._compute_vertex_collisions(new_pos)
        edge_collisions = self._compute_edge_collisions(prev_pos, new_pos)

        state = MAPFState(
            t=self.t,
            pos=self.pos.copy(),
            goals=self.goals.copy(),
            grid=self.grid,
        )

        info = {
            "t": self.t,
            "invalid_moves": invalid_moves,          # list of agent indices
            "unknown_actions": unknown_actions,      # agents who sent invalid action ids
            "vertex_collisions": vertex_collisions,  # list of (cell, [agents...])
            "edge_collisions": edge_collisions,      # list of ((ai, aj), (from_i, to_i, from_j, to_j))
        }

        return state, info

    # ---------------------------------------------------------------
    # Collision helpers
    # ---------------------------------------------------------------
    def _compute_vertex_collisions(
        self, pos: np.ndarray
    ) -> List[Tuple[Tuple[int, int], Tuple[int, ...]]]:
        cell_to_agents: Dict[Tuple[int, int], List[int]] = {}
        for i in range(self.num_agents):
            cell = (int(pos[i, 0]), int(pos[i, 1]))
            cell_to_agents.setdefault(cell, []).append(i)

        collisions = []
        for cell, agents in cell_to_agents.items():
            if len(agents) > 1:
                collisions.append((cell, tuple(agents)))
        return collisions

    def _compute_edge_collisions(
        self, prev_pos: np.ndarray, curr_pos: np.ndarray
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int, int, int, int, int]]]:
        collisions = []
        N = self.num_agents
        for i in range(N):
            for j in range(i + 1, N):
                if (
                    prev_pos[i, 0] == curr_pos[j, 0]
                    and prev_pos[i, 1] == curr_pos[j, 1]
                    and prev_pos[j, 0] == curr_pos[i, 0]
                    and prev_pos[j, 1] == curr_pos[i, 1]
                ):
                    collisions.append(
                        (
                            (i, j),
                            (
                                int(prev_pos[i, 0]),
                                int(prev_pos[i, 1]),
                                int(curr_pos[i, 0]),
                                int(curr_pos[i, 1]),
                                int(prev_pos[j, 0]),
                                int(prev_pos[j, 1]),
                            ),
                        )
                    )
        return collisions

    # ---------------------------------------------------------------
    # Convenience: current state + simple render hook
    # ---------------------------------------------------------------
    def get_state(self) -> MAPFState:
        return MAPFState(
            t=self.t,
            pos=self.pos.copy(),
            goals=self.goals.copy(),
            grid=self.grid,
        )

    def render(self, ax=None, show_goals: bool = True):
        from mapf_env.viz.render import render_state  # local import

        state = self.get_state()
        return render_state(state, ax=ax, show_goals=show_goals)
