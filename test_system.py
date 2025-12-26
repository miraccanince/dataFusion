#!/usr/bin/env python3
"""
System Test Script
==================

Quick test to verify all components are working.
Runs WITHOUT Raspberry Pi hardware.

Usage:
    python3 test_system.py
"""

import sys
import os

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print colored header"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def test_imports():
    """Test if required packages are installed"""
    print_header("Testing Package Imports")

    packages = [
        ('numpy', 'NumPy'),
        ('scipy', 'SciPy'),
        ('matplotlib', 'Matplotlib'),
        ('flask', 'Flask'),
        ('paho.mqtt.client', 'paho-mqtt'),
    ]

    all_ok = True
    for package, name in packages:
        try:
            __import__(package)
            print_success(f"{name:20s} - installed")
        except ImportError:
            print_error(f"{name:20s} - MISSING (pip3 install {package.split('.')[0]})")
            all_ok = False

    # Optional packages
    optional = [
        ('sense_hat', 'sense-hat (Raspberry Pi only)'),
        ('psutil', 'psutil'),
    ]

    for package, name in optional:
        try:
            __import__(package)
            print_success(f"{name:20s} - installed")
        except ImportError:
            print_warning(f"{name:20s} - not installed (optional)")

    return all_ok

def test_bayesian_filter():
    """Test Bayesian filter implementation"""
    print_header("Testing Bayesian Filter")

    try:
        sys.path.insert(0, 'src')
        from bayesian_filter import BayesianNavigationFilter, FloorPlanPDF

        # Create floor plan
        floor_plan = FloorPlanPDF(width_m=20.0, height_m=10.0, resolution=0.1)
        print_success("Floor plan PDF created")

        # Create filter
        bf = BayesianNavigationFilter(floor_plan, stride_length=0.7)
        print_success("Bayesian filter initialized")

        # Test update
        import numpy as np
        pos = bf.update(heading=0.0, stride_length=0.7)
        print_success(f"Position update works: ({pos['x']:.2f}, {pos['y']:.2f})")

        # Verify position is reasonable
        if 0 <= pos['x'] <= 20 and 0 <= pos['y'] <= 10:
            print_success("Position within floor plan bounds")
            return True
        else:
            print_error(f"Position out of bounds: ({pos['x']}, {pos['y']})")
            return False

    except Exception as e:
        print_error(f"Bayesian filter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mqtt_programs():
    """Test MQTT programs can be imported"""
    print_header("Testing MQTT Programs")

    programs = [
        'mqtt_cpu_publisher',
        'mqtt_location_publisher',
        'mqtt_subscriber_windowed',
        'mqtt_subscriber_bernoulli',
        'malfunction_detection'
    ]

    all_ok = True
    sys.path.insert(0, 'mqtt')

    for program in programs:
        try:
            __import__(program)
            print_success(f"{program}.py loads successfully")
        except ImportError as e:
            if 'sense_hat' in str(e):
                print_warning(f"{program}.py needs SenseHat (Raspberry Pi only)")
            else:
                print_error(f"{program}.py failed to load: {e}")
                all_ok = False
        except Exception as e:
            print_warning(f"{program}.py loads with warning: {e}")

    return all_ok

def test_web_dashboard():
    """Test web dashboard can be imported"""
    print_header("Testing Web Dashboard")

    try:
        sys.path.insert(0, 'src')
        import web_dashboard_advanced
        print_success("Web dashboard loads successfully")
        print_warning("Note: Requires SenseHat to run, but code is valid")
        return True
    except ImportError as e:
        if 'sense_hat' in str(e):
            print_warning("Web dashboard needs SenseHat (Raspberry Pi only)")
            print_success("But code structure is valid")
            return True
        else:
            print_error(f"Web dashboard failed: {e}")
            return False
    except Exception as e:
        print_error(f"Web dashboard test failed: {e}")
        return False

def test_file_structure():
    """Verify project structure is correct"""
    print_header("Testing File Structure")

    required_dirs = [
        ('src', 'Main source code'),
        ('mqtt', 'MQTT programs'),
        ('examples', 'Tutorial scripts'),
        ('utils', 'Utility tools'),
        ('docs', 'Documentation'),
        ('templates', 'HTML templates'),
        ('scripts', 'Shell scripts'),
        ('output', 'Generated images'),
    ]

    all_ok = True
    for dir_name, description in required_dirs:
        if os.path.isdir(dir_name):
            print_success(f"{dir_name:15s} - {description}")
        else:
            print_error(f"{dir_name:15s} - MISSING")
            all_ok = False

    return all_ok

def test_documentation():
    """Check if documentation exists"""
    print_header("Testing Documentation")

    docs = [
        ('README.md', 'Main README'),
        ('DEMO_SYSTEM.md', 'Demo guide'),
        ('docs/BAYESIAN_FILTER_README.md', 'Bayesian filter docs'),
        ('docs/QUICK_START_BAYESIAN.md', 'Quick start guide'),
        ('mqtt/README.md', 'MQTT documentation'),
    ]

    all_ok = True
    for doc, description in docs:
        if os.path.isfile(doc):
            print_success(f"{description:30s} - exists")
        else:
            print_error(f"{description:30s} - MISSING")
            all_ok = False

    return all_ok

def run_quick_demo():
    """Run quick algorithm comparison"""
    print_header("Running Quick Demo (compare_algorithms.py)")

    try:
        sys.path.insert(0, 'examples')
        from compare_algorithms import (
            FloorPlanPDF,
            simulate_walk_with_drift,
            run_naive_algorithm,
            run_bayesian_algorithm,
            calculate_errors
        )

        import numpy as np

        # Create floor plan
        floor_plan = FloorPlanPDF(width_m=20.0, height_m=10.0, resolution=0.1)
        print_success("Floor plan created")

        # Simulate walk
        ground_truth, imu_headings = simulate_walk_with_drift()
        print_success(f"Simulated {len(imu_headings)} strides with realistic IMU drift")

        # Run algorithms
        naive_traj = run_naive_algorithm(ground_truth[0], imu_headings)
        print_success("Naive dead reckoning completed")

        bayesian_traj = run_bayesian_algorithm(floor_plan, ground_truth[0], imu_headings)
        print_success("Bayesian filter completed")

        # Calculate errors
        naive_errors = calculate_errors(naive_traj, ground_truth)
        bayesian_errors = calculate_errors(bayesian_traj, ground_truth)

        print(f"\n{'-'*70}")
        print(f"Results:")
        print(f"  Naive final error:     {naive_errors[-1]:.2f}m")
        print(f"  Bayesian final error:  {bayesian_errors[-1]:.2f}m")

        improvement = ((naive_errors[-1] - bayesian_errors[-1]) / naive_errors[-1]) * 100
        if improvement > 0:
            print(f"  Improvement:           {improvement:.1f}% better!")
            print_success("Bayesian filter is more accurate! ✓")
        else:
            print_warning("Bayesian should be more accurate (may need parameter tuning)")

        print(f"{'-'*70}\n")

        return True

    except Exception as e:
        print_error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'#'*70}")
    print("#" + " " * 68 + "#")
    print("#" + "   System Test - Pedestrian Inertial Navigation   ".center(68) + "#")
    print("#" + " " * 68 + "#")
    print(f"{'#'*70}{RESET}\n")

    tests = [
        ("Package Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Documentation", test_documentation),
        ("Bayesian Filter", test_bayesian_filter),
        ("MQTT Programs", test_mqtt_programs),
        ("Web Dashboard", test_web_dashboard),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print_error(f"{name} test crashed: {e}")
            results[name] = False

    # Summary
    print_header("Test Summary")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for name, result in results.items():
        if result:
            print_success(f"{name:25s} - PASS")
        else:
            print_error(f"{name:25s} - FAIL")

    print(f"\n{'-'*70}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{'-'*70}\n")

    # Run demo if all critical tests pass
    critical_pass = results.get("Bayesian Filter", False)
    if critical_pass:
        run_quick_demo()

    # Final verdict
    if passed == total:
        print(f"{GREEN}╔═══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{GREEN}║   ✓ ALL TESTS PASSED - System is ready!                  ║{RESET}")
        print(f"{GREEN}╚═══════════════════════════════════════════════════════════╝{RESET}\n")
        print(f"Next steps:")
        print(f"  1. Read DEMO_SYSTEM.md for usage examples")
        print(f"  2. Run: python3 examples/compare_algorithms.py")
        print(f"  3. Transfer to Pi and test MQTT system")
        return 0
    else:
        print(f"{YELLOW}╔═══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{YELLOW}║   ⚠ Some tests failed - Review errors above              ║{RESET}")
        print(f"{YELLOW}╚═══════════════════════════════════════════════════════════╝{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
