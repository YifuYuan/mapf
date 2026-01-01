#!/bin/bash
# Quick test script - runs essential tests only

set -e

echo "=========================================="
echo "Quick Tests"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

echo "1. Testing sample_instance.py - basic usage"
python -m scripts.sample_instance --map den312d --k 10
echo ""

echo "2. Testing validate_paths.py - basic validation"
if [ -f "paths.npy" ]; then
    python -m scripts.validate_paths paths.npy --map den312d
else
    echo "Creating test paths file..."
    python3 << 'PYTHON_EOF'
import numpy as np
# Create paths with appropriate dimensions for den312d (81x65)
paths = np.zeros((10, 10, 2), dtype=np.int32)
for t in range(10):
    for n in range(10):
        # Use valid positions within map bounds
        paths[t, n] = [t % 81, n % 65]
np.save("paths.npy", paths)
print("Created paths.npy with shape", paths.shape)
PYTHON_EOF
    python -m scripts.validate_paths paths.npy --map den312d
fi
echo ""

echo "=========================================="
echo "Quick tests completed!"
echo "=========================================="

