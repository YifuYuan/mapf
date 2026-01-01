#!/bin/bash
# Test error cases and edge cases

set +e  # Don't exit on error - we expect some to fail

echo "=========================================="
echo "Testing Error Cases"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Test 1: Missing required arguments
echo "TEST 1: Missing --map argument (sample_instance)"
python -m scripts.sample_instance --k 10 2>&1 | head -5
echo ""

echo "TEST 2: Missing --k argument (sample_instance)"
python -m scripts.sample_instance --map den312d 2>&1 | head -5
echo ""

# Test 2: Invalid map names
echo "TEST 3: Invalid map name (sample_instance)"
python -m scripts.sample_instance --map invalid_map_name --k 10 2>&1 | head -10
echo ""

# Test 3: Missing paths file
echo "TEST 4: Missing paths file (validate_paths)"
python -m scripts.validate_paths nonexistent_file.npy --map den312d 2>&1 | head -10
echo ""

# Test 4: Example path detection
echo "TEST 5: Example path detection (validate_paths)"
python -m scripts.validate_paths /path/to/your/paths.npy --map den312d 2>&1 | head -15
echo ""

# Test 5: Missing --map in validate_paths
echo "TEST 6: Missing --map argument (validate_paths)"
python -m scripts.validate_paths paths.npy 2>&1 | head -5
echo ""

# Test 6: Invalid k value (too large)
echo "TEST 7: k value larger than available scenarios"
python -m scripts.sample_instance --map den312d --k 10000 2>&1 | head -10
echo ""

# Test 7: Invalid offset
echo "TEST 8: Invalid offset (too large)"
python -m scripts.sample_instance --map den312d --k 10 --offset 10000 2>&1 | head -10
echo ""

# Test 8: Wrong file format
echo "TEST 9: Wrong file format (not .npy)"
echo "test" > test.txt
python -m scripts.validate_paths test.txt --map den312d 2>&1 | head -10
rm -f test.txt
echo ""

# Test 9: Invalid connectivity
echo "TEST 10: Invalid connectivity value"
python -m scripts.validate_paths paths.npy --map den312d --connectivity 6 2>&1 | head -10
echo ""

echo "=========================================="
echo "Error case tests completed!"
echo "=========================================="

