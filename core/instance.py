# mapf_env/core/instance.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple

import numpy as np


@dataclass
class MAPFInstance:
    grid: np.ndarray
    starts: np.ndarray
    goals: np.ndarray
    num_agents: int
    scen_index_or_seed: Any = None

    def sanity_check(self, strict: bool = True) -> bool:
        try:
            if self.grid.ndim != 2:
                raise ValueError(f"grid must be 2D, got shape {self.grid.shape}")

            if self.starts.shape != self.goals.shape:
                raise ValueError(
                    f"starts and goals must have same shape, "
                    f"got {self.starts.shape} vs {self.goals.shape}"
                )

            if self.starts.shape[1] != 2:
                raise ValueError(
                    f"starts/goals must be (N, 2), got {self.starts.shape}"
                )

            n = self.starts.shape[0]
            if self.num_agents != n:
                raise ValueError(
                    f"num_agents={self.num_agents} but starts has N={n}"
                )

            H, W = self.grid.shape

            # bounds check
            for name, arr in [("starts", self.starts), ("goals", self.goals)]:
                if not np.all((arr[:, 0] >= 0) & (arr[:, 0] < H)):
                    raise ValueError(f"{name} has rows out of bounds (0..{H-1}).")
                if not np.all((arr[:, 1] >= 0) & (arr[:, 1] < W)):
                    raise ValueError(f"{name} has cols out of bounds (0..{W-1}).")

            # check free cells
            starts_blocked = self.grid[self.starts[:, 0], self.starts[:, 1]] == 1
            goals_blocked = self.grid[self.goals[:, 0], self.goals[:, 1]] == 1

            if np.any(starts_blocked):
                bad_idx = np.where(starts_blocked)[0][:5]
                raise ValueError(
                    f"{len(bad_idx)} start positions are on obstacles, "
                    f"examples: {self.starts[bad_idx]}"
                )

            if np.any(goals_blocked):
                bad_idx = np.where(goals_blocked)[0][:5]
                raise ValueError(
                    f"{len(bad_idx)} goal positions are on obstacles, "
                    f"examples: {self.goals[bad_idx]}"
                )

            return True

        except ValueError:
            if strict:
                raise
            return False


def instance_from_scen(
    grid: np.ndarray,
    scen_starts: np.ndarray,
    scen_goals: np.ndarray,
    k: int,
    offset: int = 0,
) -> MAPFInstance:
    M = scen_starts.shape[0]
    if scen_goals.shape[0] != M:
        raise ValueError("scen_starts and scen_goals must have same length.")

    if offset < 0 or offset + k > M:
        raise ValueError(
            f"Requested scen rows [{offset}:{offset + k}] "
            f"but scenario only has M={M} entries."
        )

    starts = scen_starts[offset : offset + k].copy()
    goals = scen_goals[offset : offset + k].copy()

    instance = MAPFInstance(
        grid=grid,
        starts=starts,
        goals=goals,
        num_agents=k,
        scen_index_or_seed={"offset": offset, "k": k},
    )

    instance.sanity_check(strict=True)
    return instance
