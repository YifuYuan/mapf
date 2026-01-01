# scripts/sample_instance.py

import argparse
from pathlib import Path

import numpy as np

from mapf_env.io.movingai_map import load_map
from mapf_env.io.movingai_scene import load_scen
from core.instance import MAPFInstance, instance_from_scen


def default_paths(map_name: str, maps_dir: str, scen_dir: str):
    map_path = Path(maps_dir) / f"{map_name}.map"
    # Try to find any available random scenario file for this map
    scen_dir_path = Path(scen_dir)
    scen_files = list(scen_dir_path.glob(f"{map_name}-random-*.scen"))
    if scen_files:
        scen_path = scen_files[0]  # Use the first available one
    else:
        scen_path = scen_dir_path / f"{map_name}-random-1.scen"  # Fallback
    return map_path, scen_path


def main():
    parser = argparse.ArgumentParser(
        description="Sample a MAPF instance (starts/goals) from a MovingAI scenario."
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
        help="Number of agents (rows of scen) to sample.",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Starting scen row index (default: 0).",
    )
    parser.add_argument(
        "--maps_dir",
        type=str,
        default="data/mapf-map",
        help="Directory containing .map files (default: data/mapf-map).",
    )
    parser.add_argument(
        "--scen_dir",
        type=str,
        default="data/scens",
        help="Directory containing .scen files (default: data/scens).",
    )
    # Optional explicit overrides if your layout differs
    parser.add_argument(
        "--map_path",
        type=str,
        default=None,
        help="Explicit path to .map file (overrides maps_dir/map).",
    )
    parser.add_argument(
        "--scen_path",
        type=str,
        default=None,
        help="Explicit path to .scen file (overrides scen_dir/map-random-1.scen).",
    )

    args = parser.parse_args()

    if args.map_path is not None and args.scen_path is not None:
        map_path = Path(args.map_path)
        scen_path = Path(args.scen_path)
    else:
        map_path, scen_path = default_paths(args.map, args.maps_dir, args.scen_dir)

    print(f"Map path : {map_path}")
    print(f"Scen path: {scen_path}")

    grid = load_map(map_path)
    scen_starts, scen_goals = load_scen(scen_path)

    print(f"Loaded grid with shape HxW = {grid.shape}")
    print(f"Scenario entries available: {scen_starts.shape[0]}")

    instance = instance_from_scen(
        grid=grid,
        scen_starts=scen_starts,
        scen_goals=scen_goals,
        k=args.k,
        offset=args.offset,
    )

    print("\n=== Instance summary ===")
    print(f"num_agents      : {instance.num_agents}")
    print(f"grid shape (H,W): {instance.grid.shape}")
    print(f"offset          : {instance.scen_index_or_seed['offset']}")
    print(f"k               : {instance.scen_index_or_seed['k']}")

    # Sanity: check that all starts/goals are on free cells
    H, W = instance.grid.shape
    starts_ok = np.all(instance.grid[instance.starts[:, 0], instance.starts[:, 1]] == 0)
    goals_ok = np.all(instance.grid[instance.goals[:, 0], instance.goals[:, 1]] == 0)

    print(f"starts on free cells: {starts_ok}")
    print(f"goals on free cells : {goals_ok}")

    # Print first few agents as a quick check
    max_print = min(10, instance.num_agents)
    print(f"\nFirst {max_print} agents (row, col):")
    for i in range(max_print):
        s = instance.starts[i]
        g = instance.goals[i]
        print(f"  agent {i:3d}: start={tuple(s)}, goal={tuple(g)}")


if __name__ == "__main__":
    main()
