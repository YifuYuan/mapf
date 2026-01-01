# mapf_env/io/movingai_scen.py

from pathlib import Path
from typing import Tuple, Union

import numpy as np

PathLike = Union[str, Path]


def load_scen(path: PathLike) -> Tuple[np.ndarray, np.ndarray]:
    path = Path(path)

    start_locations = []
    goal_locations = []

    with path.open("r") as f:
        for line in f:
            line = line.rstrip()
            if not line or line.startswith("version"):
                continue

            tokens = line.split("\t")
            # Expected format: 9 fields per MovingAI scen line
            assert len(tokens) == 9, f"Unexpected scen format in line: {line}"

            # tokens[4:] are: start_col, start_row, goal_col, goal_row, distance
            start_col = int(tokens[4])
            start_row = int(tokens[5])
            goal_col = int(tokens[6])
            goal_row = int(tokens[7])

            start_locations.append((start_row, start_col))
            goal_locations.append((goal_row, goal_col))

    starts = np.array(start_locations, dtype=int)
    goals = np.array(goal_locations, dtype=int)

    return starts, goals
