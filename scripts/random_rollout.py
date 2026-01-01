# scripts/random_rollout.py

import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from mapf_env.io.movingai_map import load_map
from mapf_env.io.movingai_scene import load_scen
from core.instance import instance_from_scen
from core.env import MAPFEnv


def main():
    parser = argparse.ArgumentParser(
        description="Run random actions in MAPFEnv for a few steps and visualize."
    )
    parser.add_argument(
        "--map",
        required=True,
        help="Map basename, e.g. 'den312d' (without extension).",
    )
    parser.add_argument(
        "--k",
        type=int,
        required=True,
        help="Number of agents (scenario rows).",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=20,
        help="Number of random steps to run (default: 20).",
    )
    parser.add_argument(
        "--motion",
        choices=["4", "8"],
        default="4",
        help="Motion model: 4-connected or 8-connected.",
    )
    parser.add_argument(
        "--maps_dir",
        type=str,
        default="data/mapf-map",
        help="Directory containing .map files.",
    )
    parser.add_argument(
        "--scen_dir",
        type=str,
        default="data/scens",
        help="Directory containing .scen files.",
    )
    parser.add_argument(
        "--scen_path",
        type=str,
        default=None,
        help="Explicit .scen path; if not set, uses '<map>-random-1.scen'.",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Scenario row offset (default: 0).",
    )

    args = parser.parse_args()

    # Resolve map & scen
    map_path = Path(args.maps_dir) / f"{args.map}.map"
    if not map_path.exists():
        raise FileNotFoundError(f"Map file not found: {map_path}")

    if args.scen_path is not None:
        scen_path = Path(args.scen_path)
    else:
        # Try to find any available random scenario file for this map
        scen_dir_path = Path(args.scen_dir)
        scen_files = list(scen_dir_path.glob(f"{args.map}-random-*.scen"))
        if scen_files:
            scen_path = scen_files[0]  # Use the first available one
        else:
            scen_path = scen_dir_path / f"{args.map}-random-1.scen"  # Fallback
    if not scen_path.exists():
        raise FileNotFoundError(f"Scenario file not found: {scen_path}")

    print(f"Using map : {map_path}")
    print(f"Using scen: {scen_path}")

    grid = load_map(map_path)
    scen_starts, scen_goals = load_scen(scen_path)

    instance = instance_from_scen(
        grid=grid,
        scen_starts=scen_starts,
        scen_goals=scen_goals,
        k=args.k,
        offset=args.offset,
    )

    env = MAPFEnv(instance, motion=args.motion)
    state = env.reset()

    # For random actions
    num_actions = 9 if args.motion == "8" else 5

    plt.ion()
    fig, ax = plt.subplots()

    for step_idx in range(args.steps):
        ax.clear()

        # random joint action
        actions = np.random.randint(0, num_actions, size=env.num_agents)
        state, info = env.step(actions)

        env.render(ax=ax, show_goals=True)
        ax.set_title(f"Random rollout: t={state.t}")

        # Print a tiny summary to terminal
        print(
            f"t={state.t} | invalid={len(info['invalid_moves'])}, "
            f"vertex_collisions={len(info['vertex_collisions'])}, "
            f"edge_collisions={len(info['edge_collisions'])}"
        )

        plt.pause(0.2)

    print("Rollout finished.")
    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
