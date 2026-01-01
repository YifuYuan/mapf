#!/bin/bash
# Test script for validate_paths.py

set -e  # Exit on error

echo "=========================================="
echo "Testing validate_paths.py"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Create test paths file
echo "Creating test paths file..."
python3 << 'PYTHON_EOF'
import numpy as np
from pathlib import Path

# Create a simple valid paths file
paths = np.zeros((10, 5, 2), dtype=np.int32)
for t in range(10):
    for n in range(5):
        paths[t, n] = [t % 20, n % 10]

np.save("test_paths.npy", paths)
print(f"Created test_paths.npy with shape {paths.shape}")
PYTHON_EOF
echo ""

# Test 1: Basic validation
echo "TEST 1: Basic validation"
python -m scripts.validate_paths test_paths.npy --map den312d
echo ""

# Test 2: With goals check
echo "TEST 2: Validation with goals check (k=5)"
python -m scripts.validate_paths test_paths.npy --map den312d --k 5
echo ""

# Test 3: Different connectivity
echo "TEST 3: Testing with 4-connectivity"
python -m scripts.validate_paths test_paths.npy --map den312d --connectivity 4
echo ""

echo "TEST 4: Testing with 8-connectivity"
python -m scripts.validate_paths test_paths.npy --map den312d --connectivity 8
echo ""

# Test 4: Different maps
echo "TEST 5: Testing with empty-8-8"
python3 << 'PYTHON_EOF'
import numpy as np
paths = np.zeros((5, 3, 2), dtype=np.int32)
for t in range(5):
    for n in range(3):
        paths[t, n] = [t % 8, n % 8]
np.save("test_paths_small.npy", paths)
PYTHON_EOF
python -m scripts.validate_paths test_paths_small.npy --map empty-8-8
echo ""

# Test 5: Error cases
echo "TEST 6: Testing error - missing file"
python -m scripts.validate_paths nonexistent.npy --map den312d 2>&1 || echo "Expected error occurred"
echo ""

echo "TEST 7: Testing error - example path detection"
python -m scripts.validate_paths /path/to/your/paths.npy --map den312d 2>&1 || echo "Expected error occurred"
echo ""

# Test 6: With offset
echo "TEST 8: Testing with offset"
python -m scripts.validate_paths test_paths.npy --map den312d --k 5 --offset 5
echo ""

# Cleanup
echo "Cleaning up test files..."
rm -f test_paths.npy test_paths_small.npy
echo ""

echo "=========================================="
echo "All tests completed!"
echo "=========================================="

