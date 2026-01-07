#!/usr/bin/env python3
"""
Test script to verify wall detection in Bayesian filter

This script simulates walking directly toward the wall at x=5m
to verify the Bayesian filter correctly avoids crossing it.
"""

import numpy as np
from src.bayesian_filter import FloorPlanPDF, BayesianNavigationFilter

print("=" * 70)
print("WALL DETECTION TEST")
print("=" * 70)
print("\nObjective: Verify Bayesian filter prevents wall crossing at x=5m")
print("Method: Walk from x=2m toward x=8m (through wall) and check trajectory")
print()

# Create floor plan (wall at x=5m)
print("1. Creating floor plan with wall at x=5.0m...")
floor_plan = FloorPlanPDF(width_m=10.0, height_m=10.0, resolution=0.1)
print(f"   ✓ Floor plan created: {floor_plan.grid_width} × {floor_plan.grid_height} cells")
print(f"   ✓ Wall location: x=5.0m ± 0.25m")
print(f"   ✓ Wall probability: {floor_plan.get_probability(5.0, 5.0):.4f} (should be ≈0.01)")
print(f"   ✓ Walkable probability: {floor_plan.get_probability(2.0, 5.0):.4f} (should be ≈1.0)")

# Create Bayesian filter
print("\n2. Initializing Bayesian filter...")
bf = BayesianNavigationFilter(floor_plan, stride_length=0.7)
bf.reset(x=2.0, y=5.0)  # Start in Room 1 (left side)
print(f"   ✓ Start position: ({bf.current_estimate['x']:.2f}, {bf.current_estimate['y']:.2f})")
print(f"   ✓ Floor plan weight: {bf.floor_plan_weight}")
print(f"   ✓ Expected wall penalty: {bf.floor_plan_weight * np.log(0.01):.1f}")

# Simulate walking EAST (heading = 0°) toward the wall
print("\n3. Simulating walk EAST (heading=0°) toward wall...")
print("\n   Step | Heading | Stride | Position (x, y) | Status")
print("   " + "-" * 60)

heading = 0.0  # East (directly toward wall)
stride = 0.7   # meters

trajectory = [bf.current_estimate.copy()]

for step in range(1, 8):  # 7 steps should try to cross wall
    # Update filter
    pos = bf.update(heading, stride)
    trajectory.append(pos.copy())

    # Check if crossed wall
    if pos['x'] >= 5.0:
        status = "⚠️ CROSSED WALL!" if pos['x'] > 5.3 else "Near wall edge"
    elif pos['x'] >= 4.7:
        status = "Approaching wall"
    else:
        status = "Walking normally"

    print(f"   {step:4d} | {np.degrees(heading):7.0f}° | {stride:6.2f}m | "
          f"({pos['x']:4.2f}, {pos['y']:4.2f})   | {status}")

# Analyze results
print("\n" + "=" * 70)
print("RESULTS ANALYSIS")
print("=" * 70)

max_x = max(pos['x'] for pos in trajectory)
min_x = min(pos['x'] for pos in trajectory)
final_x = trajectory[-1]['x']

print(f"\n✓ Starting X: {trajectory[0]['x']:.2f}m")
print(f"✓ Maximum X reached: {max_x:.2f}m")
print(f"✓ Final X: {final_x:.2f}m")
print(f"✓ Wall location: 5.00m")

print("\n" + "-" * 70)

if max_x < 5.0:
    print("✅ SUCCESS: Filter stopped BEFORE wall (x < 5.0m)")
    print("   The Bayesian filter correctly detected and avoided the wall!")
elif max_x < 5.3:
    print("⚠️ PARTIAL: Filter reached wall edge but didn't fully cross")
    print(f"   Maximum X = {max_x:.2f}m is near the wall gradient zone.")
    print("   This is acceptable due to Gaussian smoothing of wall boundaries.")
else:
    print("❌ FAILURE: Filter CROSSED the wall (x > 5.3m)")
    print("   The floor_plan_weight may need to be increased!")

print("-" * 70)

# Check floor plan probabilities along the path
print("\n4. Floor plan probabilities along trajectory:")
print("   X (m) | Probability | Walkability")
print("   " + "-" * 40)
for x_check in [2.0, 3.0, 4.0, 4.5, 4.8, 4.9, 5.0, 5.1, 5.5, 6.0]:
    prob = floor_plan.get_probability(x_check, 5.0)
    if prob > 0.9:
        walkable = "Fully walkable ✓"
    elif prob > 0.5:
        walkable = "Edge gradient"
    elif prob > 0.1:
        walkable = "Wall gradient"
    else:
        walkable = "WALL ⚠️"
    print(f"   {x_check:5.2f} | {prob:11.4f} | {walkable}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

# Save trajectory for plotting (optional)
try:
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Trajectory with floor plan
    x_vals = [pos['x'] for pos in trajectory]
    y_vals = [pos['y'] for pos in trajectory]

    # Draw floor plan
    ax1.axvline(x=5.0, color='red', linewidth=4, label='Wall', alpha=0.7)
    ax1.axvspan(0, 5, color='blue', alpha=0.1, label='Room 1')
    ax1.axvspan(5, 10, color='green', alpha=0.1, label='Room 2')

    # Draw trajectory
    ax1.plot(x_vals, y_vals, 'o-', color='purple', linewidth=2,
             markersize=8, label='Bayesian trajectory')
    ax1.plot(x_vals[0], y_vals[0], 'go', markersize=12, label='Start')
    ax1.plot(x_vals[-1], y_vals[-1], 'rs', markersize=12, label='End')

    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.set_xlabel('X Position (meters)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Y Position (meters)', fontsize=12, fontweight='bold')
    ax1.set_title('Bayesian Filter Wall Avoidance Test', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)

    # Plot 2: X position over steps
    steps = list(range(len(trajectory)))
    ax2.plot(steps, x_vals, 'o-', color='blue', linewidth=2, markersize=8)
    ax2.axhline(y=5.0, color='red', linewidth=2, linestyle='--', label='Wall at x=5.0m')
    ax2.set_xlabel('Step Number', fontsize=12, fontweight='bold')
    ax2.set_ylabel('X Position (meters)', fontsize=12, fontweight='bold')
    ax2.set_title('X Position vs Steps (Walking East)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig('wall_detection_test.png', dpi=150, bbox_inches='tight')
    print("\n📊 Plot saved to: wall_detection_test.png")
    print("   View this image to see the trajectory visualization!")

except ImportError:
    print("\n⚠️ matplotlib not available - skipping visualization")
    print("   Install with: pip install matplotlib")
