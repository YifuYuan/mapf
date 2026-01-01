# scripts/validate_paths.py

import argparse
from pathlib import Path

import numpy as np

from mapf_env.io.movingai_map import load_map
from mapf_env.io.movingai_scene import load_scen
from core.instance import instance_from_scen
from core.validate import validate_paths


def main():
    parser = argparse.ArgumentParser(
        description="Validate MAPF paths on a MovingAI map."
    )
    parser.add_argument(
        "paths_path",
        type=str,
        help="Path to paths.npy (shape T x N x 2, (row, col)).",
    )
    parser.add_argument(
        "--map",
        required=True,
        help="Map basename, e.g. 'den312d' (without extension).",
    )
    parser.add_argument(
        "--maps_dir",
        type=str,
        default="data/mapf-map",
        help="Directory with .map files (default: data/mapf-map).",
    )
    parser.add_argument(
        "--map_path",
        type=str,
        default=None,
        help="Explicit .map path (overrides --map & --maps_dir).",
    )
    parser.add_argument(
        "--scen_dir",
        type=str,
        default="data/scens",
        help="Directory with .scen files (default: data/scens).",
    )
    parser.add_argument(
        "--scen_path",
        type=str,
        default=None,
        help="Explicit .scen path; if not set, tries '<map>-random-1.scen'.",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=None,
        help="Number of agents (scenario rows) to use for starts/goals. "
             "If omitted, success check will be skipped.",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Scenario row offset (default: 0).",
    )
    parser.add_argument(
        "--connectivity",
        choices=["4", "8"],
        default="4",
        help="Grid connectivity for legality checks (4 or 8).",
    )

    args = parser.parse_args()

    # Load grid
    if args.map_path is not None:
        map_path = Path(args.map_path)
    else:
        map_path = Path(args.maps_dir) / f"{args.map}.map"

    print(f"Map path   : {map_path}")
    if not map_path.exists():
        raise FileNotFoundError(f"Map file not found: {map_path}")
    grid = load_map(map_path)
    H, W = grid.shape
    print(f"Grid shape : H={H}, W={W}")

    # Load paths
    paths_path = Path(args.paths_path)
    
    # Check if it's a literal example path (common mistake)
    if args.paths_path.startswith('/path/to/') or args.paths_path.startswith('/full/path/'):
        error_msg = (
            f"Error: '{args.paths_path}' appears to be an example path, not a real file.\n"
            f"Please provide the actual path to your paths.npy file.\n"
            f"\nExamples:\n"
            f"  If the file is in the current directory:\n"
            f"    python -m scripts.validate_paths ./paths.npy --map den312d --k 50\n"
            f"  If the file is in another directory:\n"
            f"    python -m scripts.validate_paths /home/user/paths.npy --map den312d --k 50\n"
            f"  Or use a relative path:\n"
            f"    python -m scripts.validate_paths ../results/paths.npy --map den312d --k 50"
        )
        raise FileNotFoundError(error_msg)
    
    # Resolve relative paths properly
    if not paths_path.is_absolute():
        # Handle ./ prefix
        if args.paths_path.startswith('./'):
            paths_path = Path.cwd() / args.paths_path[2:]
        else:
            paths_path = Path.cwd() / paths_path
    
    # Try to resolve the path
    try:
        paths_path = paths_path.resolve()
    except (OSError, RuntimeError):
        pass  # If resolve fails, use the path as-is
    
    if not paths_path.exists():
        # Try to provide helpful suggestions
        cwd = Path.cwd()
        # Check if there are any .npy files in the current directory
        npy_files = list(cwd.glob("*.npy"))
        suggestions = ""
        if npy_files:
            suggestions = f"\nFound .npy files in current directory:\n"
            for f in npy_files[:5]:  # Show up to 5 files
                suggestions += f"  - {f.name}\n"
            if len(npy_files) > 5:
                suggestions += f"  ... and {len(npy_files) - 5} more\n"
        
        error_msg = (
            f"Paths file not found: {args.paths_path}\n"
            f"  Resolved to: {paths_path}\n"
            f"  Current directory: {cwd}\n"
            f"{suggestions}"
            f"\nPlease provide a valid path to a .npy file containing paths with shape (T, N, 2)."
        )
        raise FileNotFoundError(error_msg)
    paths = np.load(str(paths_path))
    if paths.ndim != 3 or paths.shape[2] != 2:
        raise ValueError(
            f"paths.npy must have shape (T, N, 2), got {paths.shape}"
        )
    T, N, _ = paths.shape
    print(f"Paths shape: T={T}, N={N}, 2")

    # Optional starts/goals from scenario for success check
    starts = goals = None
    if args.k is not None:
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

        print(f"Scenario   : {scen_path}")
        if not scen_path.exists():
            raise FileNotFoundError(
                f"Scenario file not found: {scen_path}\n"
                f"Available scenario files in {args.scen_dir}: "
                f"{list(Path(args.scen_dir).glob('*.scen'))[:5]}"
            )
        scen_starts, scen_goals = load_scen(scen_path)

        instance = instance_from_scen(
            grid=grid,
            scen_starts=scen_starts,
            scen_goals=scen_goals,
            k=args.k,
            offset=args.offset,
        )
        starts = instance.starts
        goals = instance.goals

        if N != instance.num_agents:
            print(
                f"[WARN] paths has N={N} agents but instance uses "
                f"{instance.num_agents}; success check may not match."
            )

    # Run validation
    result = validate_paths(
        grid=grid,
        paths=paths,
        starts=starts,
        goals=goals,
        connectivity=args.connectivity,
    )

    print("\n=== Validation Report ===")
    print(f"OK (no errors + success if goals): {result['ok']}")
    print(f"  Out-of-bounds positions : {result['num_out_of_bounds']}")
    print(f"  On-obstacle positions   : {result['num_on_obstacle']}")
    print(f"  Illegal moves           : {result['num_illegal_moves']}")
    print(f"  Vertex collisions       : {result['num_vertex_collisions']}")
    print(f"  Edge collisions (swaps) : {result['num_edge_collisions']}")

    if result["success"] is not None:
        print(f"  Success (end at goals)  : {result['success']}")
    else:
        print("  Success (end at goals)  : [not checked, no goals given]")

    first_error = result["first_error"]
    if first_error is not None:
        print("\nFirst error:")
        print(f"  time   : {first_error['time']}")
        print(f"  type   : {first_error['type']}")
        print(f"  agents : {first_error['agents']}")
        if first_error.get("extra"):
            print(f"  extra  : {first_error['extra']}")
    else:
        print("\nNo errors detected in paths.")


if __name__ == "__main__":
    main()
