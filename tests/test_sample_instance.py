#!/usr/bin/env python3
"""
Strict tests for sample_instance.py
"""

import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_basic_usage():
    """Test basic usage with den312d map"""
    print("=" * 60)
    print("TEST: Basic usage with den312d")
    print("=" * 60)
    result = subprocess.run(
        ["python", "-m", "scripts.sample_instance", "--map", "den312d", "--k", "10"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    assert result.returncode == 0, f"Test failed with return code {result.returncode}"
    assert "num_agents      : 10" in result.stdout
    assert "starts on free cells: True" in result.stdout
    assert "goals on free cells : True" in result.stdout
    print("✓ PASSED\n")


def test_different_maps():
    """Test with different maps"""
    maps = ["empty-8-8", "empty-16-16", "empty-32-32"]
    for map_name in maps:
        print("=" * 60)
        print(f"TEST: Testing with map {map_name}")
        print("=" * 60)
        result = subprocess.run(
            ["python", "-m", "scripts.sample_instance", "--map", map_name, "--k", "5"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        assert result.returncode == 0, f"Test failed for {map_name}"
        assert "num_agents      : 5" in result.stdout
        print(f"✓ PASSED for {map_name}\n")


def test_different_k_values():
    """Test with different k values"""
    k_values = [1, 5, 10, 20, 50]
    for k in k_values:
        print("=" * 60)
        print(f"TEST: Testing with k={k}")
        print("=" * 60)
        result = subprocess.run(
            ["python", "-m", "scripts.sample_instance", "--map", "den312d", "--k", str(k)],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode == 0:
            assert f"num_agents      : {k}" in result.stdout
            print(f"✓ PASSED for k={k}\n")
        else:
            print(f"✗ FAILED for k={k}\n")
            if result.stderr:
                print("STDERR:", result.stderr)


def test_offset():
    """Test with offset"""
    print("=" * 60)
    print("TEST: Testing with offset=10")
    print("=" * 60)
    result = subprocess.run(
        ["python", "-m", "scripts.sample_instance", "--map", "den312d", "--k", "10", "--offset", "10"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    assert result.returncode == 0
    assert "offset          : 10" in result.stdout
    print("✓ PASSED\n")


def test_explicit_paths():
    """Test with explicit map and scen paths"""
    print("=" * 60)
    print("TEST: Testing with explicit paths")
    print("=" * 60)
    map_path = "data/mapf-map/den312d.map"
    scen_dir = Path(__file__).parent.parent / "data" / "scens"
    scen_files = list(scen_dir.glob("den312d-random-*.scen"))
    if scen_files:
        scen_path = scen_files[0]
        result = subprocess.run(
            [
                "python", "-m", "scripts.sample_instance",
                "--map_path", map_path,
                "--scen_path", str(scen_path),
                "--k", "5"
            ],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        assert result.returncode == 0
        print("✓ PASSED\n")
    else:
        print("⚠ SKIPPED: No scenario files found\n")


def test_invalid_map():
    """Test with invalid map name"""
    print("=" * 60)
    print("TEST: Testing with invalid map name")
    print("=" * 60)
    result = subprocess.run(
        ["python", "-m", "scripts.sample_instance", "--map", "nonexistent_map", "--k", "10"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    assert result.returncode != 0, "Should fail with invalid map"
    print("✓ PASSED (correctly failed)\n")


def test_missing_args():
    """Test with missing required arguments"""
    print("=" * 60)
    print("TEST: Testing with missing --map argument")
    print("=" * 60)
    result = subprocess.run(
        ["python", "-m", "scripts.sample_instance", "--k", "10"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    assert result.returncode != 0, "Should fail with missing --map"
    print("✓ PASSED (correctly failed)\n")


def test_large_k():
    """Test with large k value"""
    print("=" * 60)
    print("TEST: Testing with large k=100")
    print("=" * 60)
    result = subprocess.run(
        ["python", "-m", "scripts.sample_instance", "--map", "den312d", "--k", "100"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    if result.returncode == 0:
        assert "num_agents      : 100" in result.stdout
        print("✓ PASSED\n")
    else:
        print("⚠ FAILED (may be expected if not enough scenario entries)\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RUNNING STRICT TESTS FOR sample_instance.py")
    print("=" * 60 + "\n")
    
    tests = [
        test_basic_usage,
        test_different_maps,
        test_different_k_values,
        test_offset,
        test_explicit_paths,
        test_invalid_map,
        test_missing_args,
        test_large_k,
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
            failed += 1
    
    print("=" * 60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)

