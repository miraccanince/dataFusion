"""
Test LED Matrix - Show Heading Direction
=========================================
This script continuously shows your heading direction on the 8x8 LED matrix

The LEDs will light up to show which direction you're facing:
- Top = North
- Right = East
- Bottom = South
- Left = West

Move the Raspberry Pi around and watch the LEDs change!

Usage: python3 test_leds_heading.py
Press Ctrl+C to stop
"""

from sense_hat import SenseHat
import time
import numpy as np

sense = SenseHat()
sense.set_imu_config(True, True, True)

print("=" * 60)
print("LED HEADING DISPLAY TEST")
print("=" * 60)
print("\nMove the Raspberry Pi around and watch the LEDs!")
print("The lit LEDs show which direction you're facing:")
print("  - Top edge = North")
print("  - Right edge = East")
print("  - Bottom edge = South")
print("  - Left edge = West")
print("\nPress Ctrl+C to stop\n")
print("=" * 60)

# Define LED positions for 8 directions (clockwise from North)
# Each direction lights up 2-3 pixels on the edge
arrow_positions = {
    0: [(3, 0), (4, 0), (3, 1), (4, 1)],  # North (top)
    1: [(6, 0), (7, 0), (7, 1), (6, 1)],  # NE (top-right)
    2: [(7, 3), (7, 4), (6, 3), (6, 4)],  # East (right)
    3: [(7, 6), (7, 7), (6, 6), (6, 7)],  # SE (bottom-right)
    4: [(3, 7), (4, 7), (3, 6), (4, 6)],  # South (bottom)
    5: [(0, 7), (1, 7), (0, 6), (1, 6)],  # SW (bottom-left)
    6: [(0, 3), (0, 4), (1, 3), (1, 4)],  # West (left)
    7: [(0, 0), (1, 0), (0, 1), (1, 1)],  # NW (top-left)
}

# Direction names
direction_names = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

try:
    previous_direction_idx = -1

    while True:
        # Get orientation
        orientation = sense.get_orientation_radians()
        yaw = orientation.get('yaw', 0)

        # Convert yaw to 8 directions (0-7)
        # Add offset to align with compass (0 = North)
        direction_idx = int((yaw / (np.pi / 4) + 0.5) % 8)

        # Only update if direction changed
        if direction_idx != previous_direction_idx:
            # Clear previous
            sense.clear()

            # Light up new direction
            for pos in arrow_positions.get(direction_idx, []):
                sense.set_pixel(pos[0], pos[1], (255, 255, 0))  # Yellow

            # Print to console
            yaw_deg = np.degrees(yaw)
            print(f"Heading: {yaw_deg:6.1f}° - Direction: {direction_names[direction_idx]:2s} - LEDs updated!", end='\r')

            previous_direction_idx = direction_idx

        time.sleep(0.1)  # Update 10 times per second

except KeyboardInterrupt:
    sense.clear()
    print("\n\n✓ LED test stopped")
    print("LEDs cleared")
