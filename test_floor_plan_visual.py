#!/usr/bin/env python3
"""
Test script to visualize the 3.5m × 6.0m floor plan
Shows the probability distribution with walls
"""

import numpy as np
import matplotlib.pyplot as plt
from src.bayesian_filter import FloorPlanPDF

print("=" * 70)
print("3.5m × 6.0m Floor Plan Visualization Test")
print("=" * 70)

# Create floor plan matching the web dashboard
print("\n1. Creating floor plan (3.5m × 6.0m)...")
floor_plan = FloorPlanPDF(width_m=3.5, height_m=6.0, resolution=0.1)

print(f"   Grid size: {floor_plan.grid_width} × {floor_plan.grid_height} cells")
print(f"   Resolution: {floor_plan.resolution}m per cell")
print(f"   Dimensions: {floor_plan.width_m}m × {floor_plan.height_m}m")

# Check probability values at key locations
print("\n2. Checking probability values...")
locations = [
    (0.0, 0.0, "Bottom-left corner (wall)"),
    (0.15, 0.15, "Near bottom-left wall"),
    (0.5, 0.5, "Wall edge"),
    (1.0, 1.0, "Inside walkable area"),
    (1.75, 3.0, "Center of room (start position)"),
    (3.0, 5.0, "Inside walkable area"),
    (3.3, 5.8, "Near top-right wall"),
    (3.5, 6.0, "Top-right corner (wall)")
]

for x, y, desc in locations:
    prob = floor_plan.get_probability(x, y)
    print(f"   ({x:.2f}, {y:.2f}) {desc:30s}: {prob:.4f}")

# Create visualization
print("\n3. Creating visualization...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Plot 1: Probability heatmap
im = ax1.imshow(floor_plan.grid, origin='lower', cmap='RdYlGn',
                extent=[0, floor_plan.width_m, 0, floor_plan.height_m],
                vmin=0, vmax=1.0)
ax1.set_xlabel('X Position (meters)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Y Position (meters)', fontsize=12, fontweight='bold')
ax1.set_title('Floor Plan Probability Distribution\n(Green=Walkable, Red=Wall)',
              fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Add colorbar
cbar = plt.colorbar(im, ax=ax1)
cbar.set_label('Walking Probability', rotation=270, labelpad=20)

# Mark key positions
ax1.plot(1.75, 3.0, 'b*', markersize=20, label='Start (1.75, 3.0)')
ax1.plot(0.5, 0.5, 'rx', markersize=15, label='Wall edge')
ax1.plot(3.0, 5.5, 'ro', markersize=15, label='Wall edge')

# Draw room boundaries
from matplotlib.patches import Rectangle
wall_thickness = 0.3
room_rect = Rectangle((wall_thickness, wall_thickness),
                      floor_plan.width_m - 2*wall_thickness,
                      floor_plan.height_m - 2*wall_thickness,
                      linewidth=3, edgecolor='blue', facecolor='none',
                      label='Walkable area')
ax1.add_patch(room_rect)

ax1.legend(fontsize=10, loc='upper right')

# Plot 2: Cross-section view (horizontal slice at y=3.0)
print("\n4. Creating cross-section view...")
y_slice = 3.0
y_idx = int(y_slice / floor_plan.resolution)
x_values = np.linspace(0, floor_plan.width_m, floor_plan.grid_width)
prob_slice = floor_plan.grid[y_idx, :]

ax2.plot(x_values, prob_slice, 'b-', linewidth=2)
ax2.axhline(y=0.5, color='orange', linestyle='--', label='50% threshold')
ax2.axhline(y=0.15, color='red', linestyle='--', label='Wall threshold (15%)')
ax2.axvline(x=0.3, color='gray', linestyle=':', alpha=0.5, label='Wall edges')
ax2.axvline(x=3.2, color='gray', linestyle=':', alpha=0.5)

# Shade wall regions
ax2.axvspan(0, 0.3, alpha=0.2, color='red', label='Wall region')
ax2.axvspan(3.2, 3.5, alpha=0.2, color='red')

# Shade walkable region
ax2.axvspan(0.3, 3.2, alpha=0.1, color='green', label='Walkable region')

ax2.set_xlabel('X Position (meters)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Walking Probability', fontsize=12, fontweight='bold')
ax2.set_title(f'Cross-Section at Y = {y_slice}m (Center Line)',
              fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 1.05)
ax2.legend(fontsize=9, loc='upper right')

plt.tight_layout()
plt.savefig('floor_plan_3.5x6.0_visualization.png', dpi=150, bbox_inches='tight')
print("\n✓ Visualization saved to: floor_plan_3.5x6.0_visualization.png")

# Analyze the gradient zones
print("\n5. Analyzing wall gradient zones...")
gradient_analysis = []
for x in np.linspace(0, 3.5, 36):
    prob = floor_plan.get_probability(x, 3.0)
    if 0.15 < prob < 0.85:
        gradient_analysis.append((x, prob))

if gradient_analysis:
    print("\n   Gradient zones (15% < prob < 85%):")
    for x, prob in gradient_analysis[:5]:  # Show first 5
        print(f"   x={x:.2f}m: probability={prob:.3f}")
    if len(gradient_analysis) > 5:
        print(f"   ... ({len(gradient_analysis)} total gradient points)")
else:
    print("   ✓ No significant gradient zones (sharp walls)")

# Calculate statistics
walkable_count = np.sum(floor_plan.grid > 0.5)
wall_count = np.sum(floor_plan.grid < 0.15)
gradient_count = np.sum((floor_plan.grid >= 0.15) & (floor_plan.grid <= 0.5))
total_cells = floor_plan.grid.size

print(f"\n6. Floor plan statistics:")
print(f"   Total cells: {total_cells}")
print(f"   Walkable area (prob > 50%): {walkable_count} cells ({100*walkable_count/total_cells:.1f}%)")
print(f"   Wall area (prob < 15%): {wall_count} cells ({100*wall_count/total_cells:.1f}%)")
print(f"   Gradient zone (15-50%): {gradient_count} cells ({100*gradient_count/total_cells:.1f}%)")

print("\n" + "=" * 70)
print("✓ Floor plan test complete!")
print("=" * 70)
print("\nView the generated image: floor_plan_3.5x6.0_visualization.png")
