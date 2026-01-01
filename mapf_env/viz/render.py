# mapf_env/viz/render.py

from typing import Optional
import numpy as np
import matplotlib.pyplot as plt

from core.env import MAPFState


def render_map(
    grid: np.ndarray,
    title: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
):
    if ax is None:
        fig, ax = plt.subplots()

    ax.imshow(grid, cmap="Greys")
    ax.set_xticks([])
    ax.set_yticks([])

    if title is not None:
        ax.set_title(title)

    return ax


def render_state(
    state: MAPFState,
    ax: Optional[plt.Axes] = None,
    show_goals: bool = True,
):
    if ax is None:
        fig, ax = plt.subplots()

    grid = state.grid
    pos = state.pos
    goals = state.goals

    # Base map
    ax.imshow(grid, cmap="Greys")
    ax.set_xticks([])
    ax.set_yticks([])

    # Current positions
    rows = pos[:, 0]
    cols = pos[:, 1]
    ax.scatter(
        cols,  # x = col
        rows,  # y = row
        marker="o",
        s=30,
        edgecolors="black",
        linewidths=0.5,
    )

    # Goals
    if show_goals and goals is not None:
        g_rows = goals[:, 0]
        g_cols = goals[:, 1]
        ax.scatter(
            g_cols,
            g_rows,
            marker="x",
            s=40,
        )

    ax.set_title(f"t = {state.t}")
    return ax
