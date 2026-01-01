#!/usr/bin/env python3
"""
Strict tests for validate_paths.py
"""

import sys
import subprocess
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_test_paths_file(filename, shape, valid=True, map_shape=(81, 65)):
    """Create a test paths file"""
    T, N, _ = shape
    H, W = map_shape
    
    paths = np.zeros(shape, dtype=np.int32)
    
    if valid:
        # Create valid paths: agents stay at start positions
        for n in range(N):
            # Use valid positions within map bounds
            r = (n * 7) % H
            c = (n * 11) % W
            for t in range(T):
                paths[t, n] = [r, c]
    else:
        # Create invalid paths: some out of bounds, some on obstacles
        for t in range(T):
            for n in range(N):
                if t % 3 == 0:
                    paths[t, n] = [H + 10, W + 10]  # Out of bounds
                elif t % 3 == 1:
                    paths[t, n] = [0, 0]  # Might be on obstacle
                else:
                    paths[t, n] = [t % H, n % W]  # Valid
    
    np.save(filename, paths)
    return filename


def test_basic_validation():
    """Test basic validation with valid paths"""
    print("=" * 60)
    print("TEST: Basic validation with valid paths")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "test_paths_valid.npy"
    create_test_paths_file(test_file, (10, 5, 2), valid=True)
    
    result = subprocess.run(
        ["python", "-m", "scripts.validate_paths", str(test_file), "--map", "den312d"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    test_file.unlink()  # Cleanup
    
    assert result.returncode == 0
    assert "Paths shape:" in result.stdout
    print("✓ PASSED\n")


def test_validation_with_goals():
    """Test validation with goals check"""
    print("=" * 60)
    print("TEST: Validation with goals check")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "test_paths_goals.npy"
    create_test_paths_file(test_file, (10, 5, 2), valid=True)
    
    result = subprocess.run(
        ["python", "-m", "scripts.validate_paths", str(test_file), "--map", "den312d", "--k", "5"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    test_file.unlink()  # Cleanup
    
    assert result.returncode == 0
    assert "Success (end at goals)" in result.stdout
    print("✓ PASSED\n")


def test_invalid_paths():
    """Test with invalid paths (out of bounds)"""
    print("=" * 60)
    print("TEST: Validation with invalid paths")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "test_paths_invalid.npy"
    create_test_paths_file(test_file, (10, 5, 2), valid=False)
    
    result = subprocess.run(
        ["python", "-m", "scripts.validate_paths", str(test_file), "--map", "den312d"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    test_file.unlink()  # Cleanup
    
    assert result.returncode == 0  # Validation should complete, just report errors
    assert "Out-of-bounds positions" in result.stdout or "On-obstacle positions" in result.stdout
    print("✓ PASSED\n")


def test_missing_file():
    """Test with missing file"""
    print("=" * 60)
    print("TEST: Missing file error handling")
    print("=" * 60)
    
    result = subprocess.run(
        ["python", "-m", "scripts.validate_paths", "nonexistent.npy", "--map", "den312d"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    assert result.returncode != 0
    assert "not found" in result.stdout or "not found" in result.stderr
    print("✓ PASSED (correctly failed)\n")


def test_example_path_detection():
    """Test detection of example paths"""
    print("=" * 60)
    print("TEST: Example path detection")
    print("=" * 60)
    
    result = subprocess.run(
        ["python", "-m", "scripts.validate_paths", "/path/to/your/paths.npy", "--map", "den312d"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    assert result.returncode != 0
    assert "example path" in result.stdout.lower() or "example path" in result.stderr.lower()
    print("✓ PASSED (correctly detected example path)\n")


def test_different_connectivity():
    """Test with different connectivity options"""
    print("=" * 60)
    print("TEST: Different connectivity (4 vs 8)")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "test_paths_conn.npy"
    create_test_paths_file(test_file, (10, 5, 2), valid=True)
    
    for connectivity in ["4", "8"]:
        result = subprocess.run(
            ["python", "-m", "scripts.validate_paths", str(test_file), "--map", "den312d", "--connectivity", connectivity],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        print(f"Connectivity {connectivity}:")
        print(result.stdout)
        assert result.returncode == 0
    
    test_file.unlink()  # Cleanup
    print("✓ PASSED\n")


def test_wrong_shape():
    """Test with wrong array shape"""
    print("=" * 60)
    print("TEST: Wrong array shape")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "test_paths_wrong_shape.npy"
    # Create wrong shape (2D instead of 3D)
    wrong_paths = np.zeros((10, 5), dtype=np.int32)
    np.save(test_file, wrong_paths)
    
    result = subprocess.run(
        ["python", "-m", "scripts.validate_paths", str(test_file), "--map", "den312d"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    test_file.unlink()  # Cleanup
    
    assert result.returncode != 0
    assert "shape" in result.stdout.lower() or "shape" in result.stderr.lower()
    print("✓ PASSED (correctly detected wrong shape)\n")


def test_different_maps():
    """Test with different maps"""
    print("=" * 60)
    print("TEST: Different maps")
    print("=" * 60)
    
    maps = ["empty-8-8", "empty-16-16"]
    test_file = Path(__file__).parent / "test_paths_maps.npy"
    
    for map_name in maps:
        # Adjust shape for smaller maps
        if "8-8" in map_name:
            create_test_paths_file(test_file, (5, 3, 2), valid=True, map_shape=(8, 8))
        else:
            create_test_paths_file(test_file, (5, 3, 2), valid=True, map_shape=(16, 16))
        
        result = subprocess.run(
            ["python", "-m", "scripts.validate_paths", str(test_file), "--map", map_name],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        print(f"Map {map_name}:")
        print(result.stdout)
        assert result.returncode == 0
    
    test_file.unlink()  # Cleanup
    print("✓ PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RUNNING STRICT TESTS FOR validate_paths.py")
    print("=" * 60 + "\n")
    
    tests = [
        test_basic_validation,
        test_validation_with_goals,
        test_invalid_paths,
        test_missing_file,
        test_example_path_detection,
        test_different_connectivity,
        test_wrong_shape,
        test_different_maps,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)

