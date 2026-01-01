#!/bin/bash
# Test script for sample_instance.py

set -e  # Exit on error

echo "=========================================="
echo "Testing sample_instance.py"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Test 1: Basic usage
echo "TEST 1: Basic usage with den312d, k=10"
python -m scripts.sample_instance --map den312d --k 10
echo ""

# Test 2: Different k values
echo "TEST 2: Testing with k=5"
python -m scripts.sample_instance --map den312d --k 5
echo ""

echo "TEST 3: Testing with k=20"
python -m scripts.sample_instance --map den312d --k 20
echo ""

# Test 3: Different maps
echo "TEST 4: Testing with empty-8-8"
python -m scripts.sample_instance --map empty-8-8 --k 5
echo ""

echo "TEST 5: Testing with empty-16-16"
python -m scripts.sample_instance --map empty-16-16 --k 5
echo ""

# Test 4: With offset
echo "TEST 6: Testing with offset=10"
python -m scripts.sample_instance --map den312d --k 10 --offset 10
echo ""

# Test 5: Large k
echo "TEST 7: Testing with k=50"
python -m scripts.sample_instance --map den312d --k 50
echo ""

# Test 6: Explicit paths
echo "TEST 8: Testing with explicit paths"
SCEN_FILE=$(find data/scens -name "den312d-random-*.scen" | head -1)
if [ -n "$SCEN_FILE" ]; then
    python -m scripts.sample_instance \
        --map_path data/mapf-map/den312d.map \
        --scen_path "$SCEN_FILE" \
        --k 5
    echo ""
fi

# Test 7: Error cases
echo "TEST 9: Testing error - missing map"
python -m scripts.sample_instance --map nonexistent_map --k 10 2>&1 || echo "Expected error occurred"
echo ""

echo "TEST 10: Testing error - missing --map"
python -m scripts.sample_instance --k 10 2>&1 || echo "Expected error occurred"
echo ""

echo "=========================================="
echo "All tests completed!"
echo "=========================================="

