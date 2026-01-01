# # mapf_env/viz/animate.py

# from __future__ import annotations

# from typing import Optional
# import numpy as np
# import matplotlib.pyplot as plt
# import imageio.v2 as imageio  # pip install imageio if you don't have it


# def animate_paths(
#     grid: np.ndarray,
#     paths: np.ndarray,
#     goals: Optional[np.ndarray] = None,
#     out: str = "paths.gif",
#     fps: int = 5,
# ) -> str:
#     if paths.ndim != 3 or paths.shape[2] != 2:
#         raise ValueError(f"paths must have shape (T, N, 2); got {paths.shape}")

#     T, N, _ = paths.shape
#     H, W = grid.shape

#     frames = []
#     duration = 1.0 / fps

#     for t in range(T):
#         fig, ax = plt.subplots(figsize=(6, 6))

#         # Draw map
#         ax.imshow(grid, cmap="Greys")
#         ax.set_xticks([])
#         ax.set_yticks([])

#         pos_t = paths[t]
#         rows = pos_t[:, 0]
#         cols = pos_t[:, 1]

#         # Agents at goal vs not-at-goal
#         if goals is not None and goals.shape == (N, 2):
#             at_goal = np.all(pos_t == goals, axis=1)
#         else:
#             at_goal = np.zeros(N, dtype=bool)

#         # Not-at-goal agents: circles
#         na_idx = np.where(~at_goal)[0]
#         if len(na_idx) > 0:
#             ax.scatter(
#                 cols[na_idx],
#                 rows[na_idx],
#                 marker="o",
#                 s=30,
#                 edgecolors="black",
#                 linewidths=0.5,
#             )

#         # At-goal agents: crosses
#         ag_idx = np.where(at_goal)[0]
#         if len(ag_idx) > 0:
#             ax.scatter(
#                 cols[ag_idx],
#                 rows[ag_idx],
#                 marker="x",
#                 s=40,
#             )

#         # Draw goals themselves (faint) if provided
#         if goals is not None and goals.shape == (N, 2):
#             g_rows = goals[:, 0]
#             g_cols = goals[:, 1]
#             ax.scatter(
#                 g_cols,
#                 g_rows,
#                 marker="+",
#                 s=30,
#                 alpha=0.3,
#             )

#         ax.set_title(f"t = {t} (T={T}, N={N})")

#         # Convert figure to RGB array
#         fig.canvas.draw()
#         # Use buffer_rgba() for newer matplotlib, fallback to tostring_rgb() for older versions
#         try:
#             buf = fig.canvas.buffer_rgba()
#             frame = np.asarray(buf)
#             # Convert RGBA to RGB
#             frame = frame[:, :, :3]
#         except AttributeError:
#             # Fallback for older matplotlib versions
#             frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
#             frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
#         frames.append(frame)

#         plt.close(fig)

#     imageio.mimsave(out, frames, duration=duration)
#     return out

# mapf_env/viz/animate.py

from __future__ import annotations

from typing import Optional, Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio  # pip install imageio if you don't have it


def _compute_vertex_collisions(
    pos: np.ndarray,
) -> List[Tuple[Tuple[int, int], Tuple[int, ...]]]:
    """
    Return list of (cell, agents) for any cell with >= 2 agents.
    """
    cell_to_agents: Dict[Tuple[int, int], List[int]] = {}
    N = pos.shape[0]
    for i in range(N):
        cell = (int(pos[i, 0]), int(pos[i, 1]))
        cell_to_agents.setdefault(cell, []).append(i)

    collisions = []
    for cell, agents in cell_to_agents.items():
        if len(agents) > 1:
            collisions.append((cell, tuple(agents)))
    return collisions


def _compute_edge_collisions(
    prev_pos: np.ndarray,
    curr_pos: np.ndarray,
) -> List[Tuple[Tuple[int, int], Tuple[int, int, int, int, int, int]]]:

    collisions = []
    N = prev_pos.shape[0]
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


def animate_paths(
    grid: np.ndarray,
    paths: np.ndarray,
    starts: Optional[np.ndarray] = None,
    goals: Optional[np.ndarray] = None,
    out: str = "paths.gif",
    fps: int = 5,
    stride: int = 1,
    highlight_collisions: bool = True,
) -> str:
    if paths.ndim != 3 or paths.shape[2] != 2:
        raise ValueError(f"paths must have shape (T, N, 2); got {paths.shape}")

    T, N, _ = paths.shape
    H, W = grid.shape

    if stride < 1:
        stride = 1

    frames = []
    duration = 1.0 / fps

    # Precompute collisions per frame if highlighting is on
    vertex_per_t: Dict[int, List[Tuple[Tuple[int, int], Tuple[int, ...]]]] = {}
    edge_per_t: Dict[int, List[Tuple[Tuple[int, int], Tuple[int, int, int, int, int, int]]]] = {}
    if highlight_collisions:
        for t in range(T):
            pos_t = paths[t]
            vertex_per_t[t] = _compute_vertex_collisions(pos_t)
        for t in range(1, T):
            prev = paths[t - 1]
            curr = paths[t]
            edge_per_t[t] = _compute_edge_collisions(prev, curr)

    # Iterate over downsampled timesteps
    for t in range(0, T, stride):
        fig, ax = plt.subplots(figsize=(6, 6))

        # Draw map
        ax.imshow(grid, cmap="Greys")
        ax.set_xticks([])
        ax.set_yticks([])

        pos_t = paths[t]
        rows = pos_t[:, 0]
        cols = pos_t[:, 1]

        # Determine which agents are at goal
        if goals is not None and goals.shape == (N, 2):
            at_goal = np.all(pos_t == goals, axis=1)
        else:
            at_goal = np.zeros(N, dtype=bool)

        # Collision sets for this frame
        coll_agents = set()
        if highlight_collisions:
            # vertex collisions
            for _, agents in vertex_per_t.get(t, []):
                coll_agents.update(agents)
            # edge collisions (both endpoints count as "colliding" at time t)
            for (i, j), _ in edge_per_t.get(t, []):
                coll_agents.add(i)
                coll_agents.add(j)

        # --- draw start markers (small green triangles) ---
        if starts is not None and starts.shape == (N, 2):
            s_rows = starts[:, 0]
            s_cols = starts[:, 1]
            ax.scatter(
                s_cols,
                s_rows,
                marker="^",
                s=20,
                alpha=0.4,
            )

        # --- draw goal markers (small blue plus) ---
        if goals is not None and goals.shape == (N, 2):
            g_rows = goals[:, 0]
            g_cols = goals[:, 1]
            ax.scatter(
                g_cols,
                g_rows,
                marker="+",
                s=25,
                alpha=0.4,
            )

        # --- draw agents ---
        not_at_goal_idx = np.where(~at_goal)[0]
        at_goal_idx = np.where(at_goal)[0]

        # normal (not-at-goal) agents
        if len(not_at_goal_idx) > 0:
            # Colliding vs non-colliding among not-at-goal
            normal_non_coll = [i for i in not_at_goal_idx if i not in coll_agents]
            normal_coll = [i for i in not_at_goal_idx if i in coll_agents]

            if len(normal_non_coll) > 0:
                ax.scatter(
                    cols[normal_non_coll],
                    rows[normal_non_coll],
                    marker="o",
                    s=30,
                    edgecolors="black",
                    linewidths=0.5,
                )

            if len(normal_coll) > 0:
                ax.scatter(
                    cols[normal_coll],
                    rows[normal_coll],
                    marker="o",
                    s=45,
                    edgecolors="red",
                    linewidths=1.5,
                )

        # at-goal agents (x marker)
        if len(at_goal_idx) > 0:
            goal_non_coll = [i for i in at_goal_idx if i not in coll_agents]
            goal_coll = [i for i in at_goal_idx if i in coll_agents]

            if len(goal_non_coll) > 0:
                ax.scatter(
                    cols[goal_non_coll],
                    rows[goal_non_coll],
                    marker="x",
                    s=40,
                )

            if len(goal_coll) > 0:
                ax.scatter(
                    cols[goal_coll],
                    rows[goal_coll],
                    marker="x",
                    s=55,
                    linewidths=2.0,
                )

        # --- annotations: timestep & collision text ---
        num_vertex = len(vertex_per_t.get(t, [])) if highlight_collisions else 0
        num_edge = len(edge_per_t.get(t, [])) if highlight_collisions else 0

        ax.set_title(f"t = {t} / {T-1} (N={N})")

        # Small HUD text in bottom-left
        hud_lines = [f"t = {t}", f"N = {N}"]
        if highlight_collisions:
            hud_lines.append(f"vertex: {num_vertex}, edge: {num_edge}")
        hud_text = "\n".join(hud_lines)

        ax.text(
            0.01,
            0.99,
            hud_text,
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=9,
            bbox=dict(boxstyle="round", fc="white", ec="black", alpha=0.6),
        )

        # Convert figure to RGB array
        fig.canvas.draw()
        # Use buffer_rgba() for newer matplotlib, fallback to tostring_rgb() for older versions
        try:
            buf = fig.canvas.buffer_rgba()
            frame = np.asarray(buf)
            # Convert RGBA to RGB
            frame = frame[:, :, :3]
        except AttributeError:
            # Fallback for older matplotlib versions
            frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(frame)

        plt.close(fig)

    imageio.mimsave(out, frames, duration=duration)
    return out
