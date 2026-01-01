from pathlib import Path
from typing import Union
import numpy as np

PathLike = Union[str, Path]

def load_map(path: PathLike) -> np.ndarray:
    path = Path(path)

    with path.open("r") as f:
        first = f.readline().strip()

        if first.startswith("type"):
            height_line = f.readline().strip()
            width_line = f.readline().strip()
            map_line = f.readline().strip()
            assert map_line.lower().startswith("map")

            height = int(height_line.split()[1])
            width = int(width_line.split()[1])

            rows = []
            for _ in range(height):
                line = f.readline()
                if not line:
                    break
                # Strip newline and ensure consistent width
                line_stripped = line.rstrip('\n\r')
                # Pad or truncate to expected width
                if len(line_stripped) < width:
                    line_stripped = line_stripped.ljust(width, '@')  # Pad with obstacles
                elif len(line_stripped) > width:
                    line_stripped = line_stripped[:width]  # Truncate
                rows.append(list(line_stripped))
            
            # If we read fewer rows than expected, pad with obstacles
            while len(rows) < height:
                rows.append(['@'] * width)
        else:
            rows = [list(first)]
            for line in f:
                rows.append(list(line.rstrip()))
            height = len(rows)
            width = len(rows[0]) if height > 0 else 0

    grid_chars = np.array(rows, dtype="U1")
    assert grid_chars.shape == (height, width)

    grid = np.zeros(grid_chars.shape, dtype=np.int8)

    free_mask = (grid_chars == ".")
    obstacle_mask = (grid_chars == "@") | (grid_chars == "T")

    unknown_mask = ~(free_mask | obstacle_mask)

    grid[free_mask] = 0
    grid[obstacle_mask | unknown_mask] = 1

    return grid
