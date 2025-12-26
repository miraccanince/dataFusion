"""
Algorithm Comparison Visualization
===================================

Compare Naive Dead Reckoning vs Bayesian Filter

This script simulates walking through the floor plan with simulated
heading errors to demonstrate how the Bayesian filter corrects them.
"""

import numpy as np
import matplotlib.pyplot as plt
from bayesian_filter import BayesianNavigationFilter, FloorPlanPDF


def simulate_walk_with_drift():
    """
    Simulate a walk through the hallway with realistic heading drift

    Returns:
        list: Ground truth positions
        list: IMU measurements (with drift)
        list: Stride lengths
    """
    # Ground truth path: Walk north, then turn east
    ground_truth = [
        {'x': 2.0, 'y': 4.0},  # Start
    ]

    # True headings (ground truth)
    true_headings = [0.0] * 5 + [np.pi/2] * 5  # North × 5, then East × 5

    # Simulate IMU with heading drift
    imu_measurements = []
    heading_drift = 0.0
    drift_rate = 0.15  # radians per step (realistic IMU drift)

    for true_heading in true_headings:
        # Add random drift
        heading_drift += np.random.normal(0, drift_rate)

        # IMU measures true heading + accumulated drift + noise
        measured_heading = true_heading + heading_drift + np.random.normal(0, 0.1)

        imu_measurements.append(measured_heading)

        # Update ground truth position (for comparison)
        last = ground_truth[-1]
        stride = 0.7 + np.random.normal(0, 0.05)  # Realistic stride variation

        new_pos = {
            'x': last['x'] + stride * np.sin(true_heading),
            'y': last['y'] + stride * np.cos(true_heading)
        }
        ground_truth.append(new_pos)

    return ground_truth, imu_measurements


def run_naive_algorithm(start_pos, imu_headings, stride_length=0.7):
    """
    Naive dead reckoning: Just integrate IMU measurements

    Args:
        start_pos: Starting position dict
        imu_headings: List of IMU heading measurements
        stride_length: Stride length

    Returns:
        List of positions
    """
    trajectory = [start_pos.copy()]

    for heading in imu_headings:
        last = trajectory[-1]
        new_pos = {
            'x': last['x'] + stride_length * np.sin(heading),
            'y': last['y'] + stride_length * np.cos(heading)
        }
        trajectory.append(new_pos)

    return trajectory


def run_bayesian_algorithm(floor_plan, start_pos, imu_headings, stride_length=0.7):
    """
    Bayesian filter: Use floor plan constraints

    Args:
        floor_plan: FloorPlanPDF object
        start_pos: Starting position dict
        imu_headings: List of IMU heading measurements
        stride_length: Stride length

    Returns:
        List of positions
    """
    bf = BayesianNavigationFilter(floor_plan, stride_length=stride_length)
    bf.current_estimate = start_pos.copy()

    trajectory = [start_pos.copy()]

    for heading in imu_headings:
        estimated = bf.update(heading=heading, stride_length=stride_length)
        trajectory.append(estimated.copy())

    return trajectory


def plot_comparison(floor_plan, ground_truth, naive_traj, bayesian_traj):
    """
    Create visualization comparing all three trajectories

    Args:
        floor_plan: FloorPlanPDF object
        ground_truth: Ground truth trajectory
        naive_traj: Naive algorithm trajectory
        bayesian_traj: Bayesian filter trajectory
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Extract coordinates
    gt_x = [p['x'] for p in ground_truth]
    gt_y = [p['y'] for p in ground_truth]
    naive_x = [p['x'] for p in naive_traj]
    naive_y = [p['y'] for p in naive_traj]
    bay_x = [p['x'] for p in bayesian_traj]
    bay_y = [p['y'] for p in bayesian_traj]

    # Plot 1: Naive vs Ground Truth
    ax1 = axes[0]
    ax1.imshow(floor_plan.grid, origin='lower', cmap='gray_r', alpha=0.3,
               extent=[0, floor_plan.width_m, 0, floor_plan.height_m])
    ax1.plot(gt_x, gt_y, 'g-o', linewidth=2, markersize=6, label='Ground Truth')
    ax1.plot(naive_x, naive_y, 'r-s', linewidth=2, markersize=6, label='Naive DR')
    ax1.plot(gt_x[0], gt_y[0], 'go', markersize=15, label='Start')
    ax1.plot(gt_x[-1], gt_y[-1], 'r*', markersize=20, label='End')
    ax1.set_xlabel('X (meters)', fontsize=12)
    ax1.set_ylabel('Y (meters)', fontsize=12)
    ax1.set_title('Naive Dead Reckoning\n(Heading drift causes error)', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')

    # Plot 2: Bayesian vs Ground Truth
    ax2 = axes[1]
    ax2.imshow(floor_plan.grid, origin='lower', cmap='gray_r', alpha=0.3,
               extent=[0, floor_plan.width_m, 0, floor_plan.height_m])
    ax2.plot(gt_x, gt_y, 'g-o', linewidth=2, markersize=6, label='Ground Truth')
    ax2.plot(bay_x, bay_y, 'b-^', linewidth=2, markersize=6, label='Bayesian Filter')
    ax2.plot(gt_x[0], gt_y[0], 'go', markersize=15, label='Start')
    ax2.plot(gt_x[-1], gt_y[-1], 'r*', markersize=20, label='End')
    ax2.set_xlabel('X (meters)', fontsize=12)
    ax2.set_ylabel('Y (meters)', fontsize=12)
    ax2.set_title('Bayesian Filter\n(Floor plan corrects heading)', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')

    # Plot 3: Error comparison
    ax3 = axes[2]
    ax3.imshow(floor_plan.grid, origin='lower', cmap='YlOrRd', alpha=0.5,
               extent=[0, floor_plan.width_m, 0, floor_plan.height_m])
    ax3.plot(gt_x, gt_y, 'k-o', linewidth=3, markersize=8, label='Ground Truth')
    ax3.plot(naive_x, naive_y, 'r--s', linewidth=2, markersize=6, label='Naive DR', alpha=0.7)
    ax3.plot(bay_x, bay_y, 'b-^', linewidth=2, markersize=6, label='Bayesian', alpha=0.7)
    ax3.plot(gt_x[0], gt_y[0], 'go', markersize=15, label='Start')
    ax3.plot(gt_x[-1], gt_y[-1], 'r*', markersize=20, label='End')
    ax3.set_xlabel('X (meters)', fontsize=12)
    ax3.set_ylabel('Y (meters)', fontsize=12)
    ax3.set_title('All Trajectories\n(Bayesian stays in hallway)', fontsize=14, fontweight='bold')
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    ax3.set_aspect('equal')

    plt.tight_layout()
    return fig


def calculate_errors(trajectory, ground_truth):
    """Calculate position errors at each step"""
    errors = []
    for traj_pos, gt_pos in zip(trajectory, ground_truth):
        error = np.sqrt((traj_pos['x'] - gt_pos['x'])**2 +
                       (traj_pos['y'] - gt_pos['y'])**2)
        errors.append(error)
    return np.array(errors)


def main():
    print("=" * 70)
    print("Algorithm Comparison: Naive vs Bayesian Filter")
    print("=" * 70)

    # 1. Create floor plan
    print("\n1. Creating floor plan...")
    floor_plan = FloorPlanPDF(width_m=20.0, height_m=10.0, resolution=0.1)
    print(f"   ✓ Floor plan: {floor_plan.width_m}m × {floor_plan.height_m}m")

    # 2. Simulate walk with realistic IMU drift
    print("\n2. Simulating walk with IMU heading drift...")
    ground_truth, imu_headings = simulate_walk_with_drift()
    print(f"   ✓ Simulated {len(imu_headings)} steps")
    print(f"   ✓ Path: North (5 steps) → East (5 steps)")
    print(f"   ✓ IMU drift: {np.degrees(np.mean(np.diff(imu_headings))):.1f}°/step")

    # 3. Run naive algorithm
    print("\n3. Running Naive Dead Reckoning...")
    naive_traj = run_naive_algorithm(ground_truth[0], imu_headings)
    naive_errors = calculate_errors(naive_traj, ground_truth)
    print(f"   ✓ Final position error: {naive_errors[-1]:.2f}m")
    print(f"   ✓ Mean error: {naive_errors.mean():.2f}m")

    # 4. Run Bayesian filter
    print("\n4. Running Bayesian Filter...")
    bayesian_traj = run_bayesian_algorithm(floor_plan, ground_truth[0], imu_headings)
    bayesian_errors = calculate_errors(bayesian_traj, ground_truth)
    print(f"   ✓ Final position error: {bayesian_errors[-1]:.2f}m")
    print(f"   ✓ Mean error: {bayesian_errors.mean():.2f}m")

    # 5. Calculate improvement
    improvement = ((naive_errors[-1] - bayesian_errors[-1]) / naive_errors[-1]) * 100
    print(f"\n5. Improvement:")
    print(f"   ✓ Bayesian is {improvement:.1f}% more accurate!")
    print(f"   ✓ Error reduction: {naive_errors[-1] - bayesian_errors[-1]:.2f}m")

    # 6. Visualize
    print("\n6. Creating visualization...")
    fig = plot_comparison(floor_plan, ground_truth, naive_traj, bayesian_traj)
    output_file = 'algorithm_comparison.png'
    fig.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"   ✓ Saved to: {output_file}")

    # 7. Error plot
    print("\n7. Creating error plot...")
    fig2, ax = plt.subplots(figsize=(10, 6))
    steps = range(len(naive_errors))
    ax.plot(steps, naive_errors, 'r-o', linewidth=2, markersize=6, label='Naive DR')
    ax.plot(steps, bayesian_errors, 'b-^', linewidth=2, markersize=6, label='Bayesian Filter')
    ax.set_xlabel('Step Number', fontsize=12)
    ax.set_ylabel('Position Error (meters)', fontsize=12)
    ax.set_title('Position Error Accumulation Over Time', fontsize=14, fontweight='bold')
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.fill_between(steps, naive_errors, bayesian_errors, alpha=0.2, color='green',
                     label=f'Improvement: {improvement:.1f}%')
    fig2.savefig('error_comparison.png', dpi=150, bbox_inches='tight')
    print(f"   ✓ Saved to: error_comparison.png")

    print("\n" + "=" * 70)
    print("✓ Comparison complete!")
    print("=" * 70)
    print("\nKey Findings:")
    print(f"  • Naive DR final error:     {naive_errors[-1]:.2f}m")
    print(f"  • Bayesian filter error:    {bayesian_errors[-1]:.2f}m")
    print(f"  • Improvement:              {improvement:.1f}%")
    print(f"\n  The Bayesian filter uses floor plan constraints to correct")
    print(f"  heading errors, keeping the estimate inside walkable areas.")
    print("=" * 70)

    plt.show()


if __name__ == '__main__':
    main()
