#!/bin/bash
# Test with different maps

set -e

echo "=========================================="
echo "Testing with Different Maps"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

MAPS=(
    "empty-8-8"
    "empty-16-16"
    "empty-32-32"
    "den312d"
    "room-32-32-4"
    "maze-32-32-2"
)

echo "Testing sample_instance.py with different maps:"
echo "-----------------------------------------------"
for map in "${MAPS[@]}"; do
    echo ""
    echo "Testing map: $map"
    echo "---"
    python -m scripts.sample_instance --map "$map" --k 5 2>&1 | head -15
    echo ""
done

echo ""
echo "Testing validate_paths.py with different maps:"
echo "-----------------------------------------------"

# Create test paths for each map
for map in "${MAPS[@]}"; do
    echo ""
    echo "Testing map: $map"
    echo "---"
    
    # Get map dimensions
    python3 << PYTHON_EOF
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from mapf_env.io.movingai_map import load_map

try:
    grid = load_map(f"data/mapf-map/{map}.map")
    H, W = grid.shape
    print(f"Map dimensions: {H}x{W}")
    
    # Create appropriate test paths
    import numpy as np
    T, N = 10, 5
    paths = np.zeros((T, N, 2), dtype=np.int32)
    for t in range(T):
        for n in range(N):
            paths[t, n] = [t % H, n % W]
    
    np.save("test_paths_${map}.npy", paths)
    print(f"Created test_paths_${map}.npy")
except Exception as e:
    print(f"Error: {e}")
PYTHON_EOF
    
    if [ -f "test_paths_${map}.npy" ]; then
        python -m scripts.validate_paths "test_paths_${map}.npy" --map "$map" 2>&1 | head -10
        rm -f "test_paths_${map}.npy"
    fi
    echo ""
done

echo "=========================================="
echo "Different maps tests completed!"
echo "=========================================="

