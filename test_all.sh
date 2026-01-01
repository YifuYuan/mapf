#!/bin/bash
# Run all tests

set -e

echo "=========================================="
echo "Running All Tests"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Make scripts executable
chmod +x test_sample_instance.sh
chmod +x test_validate_paths.sh
chmod +x tests/test_sample_instance.py
chmod +x tests/test_validate_paths.py

echo "1. Running shell script tests for sample_instance.py"
echo "----------------------------------------------------"
./test_sample_instance.sh
echo ""

echo "2. Running shell script tests for validate_paths.py"
echo "----------------------------------------------------"
./test_validate_paths.sh
echo ""

echo "3. Running Python strict tests for sample_instance.py"
echo "----------------------------------------------------"
python tests/test_sample_instance.py
echo ""

echo "4. Running Python strict tests for validate_paths.py"
echo "----------------------------------------------------"
python tests/test_validate_paths.py
echo ""

echo "=========================================="
echo "All tests completed!"
echo "=========================================="

