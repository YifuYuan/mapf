# scripts/preview_map.py

import argparse
import numpy as np
import matplotlib.pyplot as plt

from mapf_env.io.movingai_map import load_map
from mapf_env.viz.render import render_map


def main():
    parser = argparse.ArgumentParser(description="Preview a MovingAI MAPF map.")
    parser.add_argument(
        "map_path",
        type=str,
        help="Path to .map file (e.g., data/mapf-map/den312d.map)",
    )
    args = parser.parse_args()

    grid = load_map(args.map_path)

    h, w = grid.shape
    num_free = int(np.sum(grid == 0))
    num_obstacles = int(np.sum(grid == 1))

    print(f"Loaded map: {args.map_path}")
    print(f"  shape        : (H={h}, W={w})")
    print(f"  free cells   : {num_free}")
    print(f"  obstacles    : {num_obstacles}")

    render_map(grid, title=f"{args.map_path} (H={h}, W={w})")
    plt.show()


if __name__ == "__main__":
    main()
