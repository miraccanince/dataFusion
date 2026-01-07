#!/usr/bin/env python3
"""
Test the filter debug logging system
Simulates a few strides and verifies the debug log is created correctly
"""

import sys
import os
sys.path.insert(0, 'src')

import numpy as np
from bayesian_filter import BayesianNavigationFilter, FloorPlanPDF, DEBUG_LOG_PATH
from particle_filter import ParticleFilter
from kalman_filter import KalmanFilter

# Initialize floor plan
floor_plan = FloorPlanPDF(width_m=3.5, height_m=6.0, resolution=0.1)

# Initialize filters
start_x, start_y = 1.75, 3.0
bayesian_filter = BayesianNavigationFilter(floor_plan)
bayesian_filter.reset(x=start_x, y=start_y)
kalman_filter = KalmanFilter(initial_x=start_x, initial_y=start_y, dt=0.5)
particle_filter = ParticleFilter(floor_plan, n_particles=200, initial_x=start_x, initial_y=start_y)

# Initialize positions
positions = {
    'naive': {'x': start_x, 'y': start_y},
    'bayesian': {'x': start_x, 'y': start_y},
    'kalman': {'x': start_x, 'y': start_y},
    'particle': {'x': start_x, 'y': start_y}
}

# Clear debug log
print(f"Debug log location: {DEBUG_LOG_PATH}\n")
with open(DEBUG_LOG_PATH, 'w') as f:
    f.write("# Filter Debug Test - Testing logging system\n")
    f.write(f"# Starting position: ({start_x}, {start_y})\n\n")

print("\n" + "="*70)
print("FILTER DEBUG LOGGING TEST")
print("="*70)
print(f"\nStarting position: ({start_x}, {start_y})")
print(f"Floor plan: 3.5m x 6.0m room\n")

# Simulate 4 strides forming a square (North, East, South, West)
test_strides = [
    (0.0, "North"),      # 0° - North
    (90.0, "East"),      # 90° - East
    (180.0, "South"),    # 180° - South
    (270.0, "West"),     # 270° - West
]

STRIDE_LENGTH = 0.7

for stride_num, (heading_deg, direction) in enumerate(test_strides, 1):
    heading_rad = np.radians(heading_deg)

    print(f"\n{'='*70}")
    print(f"STRIDE #{stride_num} - Heading: {heading_deg}° ({direction})")
    print(f"{'='*70}")

    # Write to debug log
    with open(DEBUG_LOG_PATH, 'a') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"STRIDE #{stride_num} - Test stride\n")
        f.write(f"{'='*80}\n")
        f.write(f"\n[INPUT HEADING]\n")
        f.write(f"  Heading: {heading_deg:.2f}° ({heading_rad:.4f} rad) - {direction}\n")
        f.write(f"  Stride length: {STRIDE_LENGTH:.2f}m\n")
        f.write(f"  Coordinate system: Navigation (0°=North, x=sin, y=cos)\n")

    # 1. NAIVE
    with open('filters_debug.log', 'a') as f:
        f.write(f"\n[1. NAIVE FILTER]\n")
        f.write(f"  Previous position: ({positions['naive']['x']:.3f}, {positions['naive']['y']:.3f})\n")

    new_x = positions['naive']['x'] + STRIDE_LENGTH * np.sin(heading_rad)
    new_y = positions['naive']['y'] + STRIDE_LENGTH * np.cos(heading_rad)
    positions['naive'] = {'x': round(new_x, 3), 'y': round(new_y, 3)}

    with open('filters_debug.log', 'a') as f:
        f.write(f"  New position: ({positions['naive']['x']:.3f}, {positions['naive']['y']:.3f})\n")

    print(f"Naive:    ({positions['naive']['x']:6.3f}, {positions['naive']['y']:6.3f})")

    # 2. BAYESIAN (with internal logging)
    with open('filters_debug.log', 'a') as f:
        f.write(f"\n[2. BAYESIAN FILTER]\n")
        f.write(f"  Previous position: ({positions['bayesian']['x']:.3f}, {positions['bayesian']['y']:.3f})\n")
        f.write(f"  Input heading: {heading_deg:.2f}° ({heading_rad:.4f} rad)\n")
        f.write(f"  Input stride length: {STRIDE_LENGTH:.2f}m\n")

    bayesian_prev_x = positions['bayesian']['x']
    bayesian_prev_y = positions['bayesian']['y']
    estimated_pos = bayesian_filter.update(heading=heading_rad, stride_length=STRIDE_LENGTH)
    positions['bayesian'] = {'x': round(estimated_pos['x'], 3), 'y': round(estimated_pos['y'], 3)}

    with open('filters_debug.log', 'a') as f:
        f.write(f"  New position (after optimization): ({positions['bayesian']['x']:.3f}, {positions['bayesian']['y']:.3f})\n")
        f.write(f"  Displacement: Δx={positions['bayesian']['x'] - bayesian_prev_x:.3f}, Δy={positions['bayesian']['y'] - bayesian_prev_y:.3f}\n")

    print(f"Bayesian: ({positions['bayesian']['x']:6.3f}, {positions['bayesian']['y']:6.3f})")

    # 3. KALMAN
    with open('filters_debug.log', 'a') as f:
        f.write(f"\n[3. KALMAN FILTER]\n")
        f.write(f"  Previous position: ({positions['kalman']['x']:.3f}, {positions['kalman']['y']:.3f})\n")

    naive_meas_x = positions['kalman']['x'] + STRIDE_LENGTH * np.sin(heading_rad)
    naive_meas_y = positions['kalman']['y'] + STRIDE_LENGTH * np.cos(heading_rad)

    with open('filters_debug.log', 'a') as f:
        f.write(f"  Measurement (naive): ({naive_meas_x:.3f}, {naive_meas_y:.3f})\n")

    kalman_filter.predict()
    kalman_filter.update([naive_meas_x, naive_meas_y])
    kalman_pos = kalman_filter.get_position()
    positions['kalman'] = {'x': round(kalman_pos[0], 3), 'y': round(kalman_pos[1], 3)}

    with open('filters_debug.log', 'a') as f:
        f.write(f"  New position (after Kalman update): ({positions['kalman']['x']:.3f}, {positions['kalman']['y']:.3f})\n")

    print(f"Kalman:   ({positions['kalman']['x']:6.3f}, {positions['kalman']['y']:6.3f})")

    # 4. PARTICLE
    with open('filters_debug.log', 'a') as f:
        f.write(f"\n[4. PARTICLE FILTER]\n")
        f.write(f"  Previous position: ({positions['particle']['x']:.3f}, {positions['particle']['y']:.3f})\n")
        f.write(f"  Input heading: {heading_deg:.2f}° ({heading_rad:.4f} rad)\n")
        f.write(f"  Input stride length: {STRIDE_LENGTH:.2f}m\n")

    particle_filter.update_stride(STRIDE_LENGTH, heading_rad)
    particle_pos = particle_filter.get_position()
    positions['particle'] = {'x': round(particle_pos[0], 3), 'y': round(particle_pos[1], 3)}

    with open('filters_debug.log', 'a') as f:
        f.write(f"  New position (weighted average): ({positions['particle']['x']:.3f}, {positions['particle']['y']:.3f})\n")

    print(f"Particle: ({positions['particle']['x']:6.3f}, {positions['particle']['y']:6.3f})")

    # Comparison summary
    with open('filters_debug.log', 'a') as f:
        f.write(f"\n[POSITION COMPARISON]\n")
        f.write(f"  Naive:    ({positions['naive']['x']:6.3f}, {positions['naive']['y']:6.3f})\n")
        f.write(f"  Bayesian: ({positions['bayesian']['x']:6.3f}, {positions['bayesian']['y']:6.3f})\n")
        f.write(f"  Kalman:   ({positions['kalman']['x']:6.3f}, {positions['kalman']['y']:6.3f})\n")
        f.write(f"  Particle: ({positions['particle']['x']:6.3f}, {positions['particle']['y']:6.3f})\n")

        f.write(f"\n[DEVIATION FROM NAIVE]\n")
        for alg in ['bayesian', 'kalman', 'particle']:
            dx = positions[alg]['x'] - positions['naive']['x']
            dy = positions[alg]['y'] - positions['naive']['y']
            dist = np.sqrt(dx**2 + dy**2)
            f.write(f"  {alg.capitalize():9s}: Δx={dx:+.3f}, Δy={dy:+.3f}, distance={dist:.3f}m\n")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print(f"\nFinal positions after 4 strides (square path):")
print(f"  Naive:    ({positions['naive']['x']:6.3f}, {positions['naive']['y']:6.3f})")
print(f"  Bayesian: ({positions['bayesian']['x']:6.3f}, {positions['bayesian']['y']:6.3f})")
print(f"  Kalman:   ({positions['kalman']['x']:6.3f}, {positions['kalman']['y']:6.3f})")
print(f"  Particle: ({positions['particle']['x']:6.3f}, {positions['particle']['y']:6.3f})")

print(f"\n✓ Debug log written to: {DEBUG_LOG_PATH}")
print(f"  File size: {os.path.getsize(DEBUG_LOG_PATH)} bytes\n")
