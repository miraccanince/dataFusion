"""
STEP 2: Naive Dead Reckoning (No Bayesian, No Floor Plan)
==========================================================
Goal: Simple position tracking using button press + orientation
Output: CSV file with position estimates

This is the SIMPLEST possible approach:
- Button press = 1 stride happened
- Assume fixed stride length (e.g., 0.7m)
- Use heading from gyroscope
- Calculate new position: x_new = x_old + stride_length * cos(heading)
                          y_new = y_old + stride_length * sin(heading)

Usage: python 02_naive_dead_reckoning.py
"""

import time
import csv
import numpy as np
from datetime import datetime
from sense_hat import SenseHat

sense = SenseHat()
sense.set_imu_config(True, True, True)

# NAIVE PARAMETERS (to be tuned later)
STRIDE_LENGTH = 0.7  # meters (average human stride)

# Position tracking
position_history = []
current_position = {'x': 0.0, 'y': 0.0}  # Start at origin
stride_count = 0

def wait_for_stride():
    """Wait for button press indicating a stride"""
    print("Ready for next stride (press button)...")

    button_pressed = False
    while not button_pressed:
        for event in sense.stick.get_events():
            if event.direction == 'middle' and event.action == 'pressed':
                button_pressed = True
                sense.set_pixel(0, 0, (0, 255, 0))  # Green dot
                time.sleep(0.1)
                sense.clear()
                break
        time.sleep(0.01)

    return time.time()

def get_heading():
    """Get current heading from IMU in radians"""
    orientation = sense.get_orientation_radians()
    yaw = orientation.get('yaw', 0)
    return yaw

def update_position_naive(x, y, heading, stride_length):
    """
    Naive dead reckoning update

    Args:
        x, y: current position
        heading: direction in radians
        stride_length: distance traveled

    Returns:
        new_x, new_y
    """
    # Simple 2D movement
    new_x = x + stride_length * np.sin(heading)
    new_y = y + stride_length * np.cos(heading)

    return new_x, new_y

def visualize_heading(yaw):
    """Show heading direction on LED matrix"""
    # Convert yaw to 8 directions (0-7)
    direction_idx = int((yaw / (np.pi / 4)) % 8)

    # LED positions for 8 directions (N, NE, E, SE, S, SW, W, NW)
    arrow_positions = {
        0: [(3, 0), (4, 0)],  # North
        1: [(6, 0), (7, 1)],  # NE
        2: [(7, 3), (7, 4)],  # East
        3: [(6, 7), (7, 6)],  # SE
        4: [(3, 7), (4, 7)],  # South
        5: [(0, 6), (1, 7)],  # SW
        6: [(0, 3), (0, 4)],  # West
        7: [(0, 1), (1, 0)],  # NW
    }

    sense.clear()
    for pos in arrow_positions.get(direction_idx, []):
        sense.set_pixel(pos[0], pos[1], (255, 255, 0))

def save_trajectory(filename='naive_trajectory.csv'):
    """Save position history to CSV"""
    if not position_history:
        print("No trajectory data to save!")
        return

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['stride', 'timestamp', 'x', 'y', 'heading_rad', 'heading_deg']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(position_history)

    print(f"\n✓ Trajectory saved to {filename}")

def main():
    global stride_count, current_position

    print("=" * 60)
    print("NAIVE DEAD RECKONING TRACKER")
    print("=" * 60)
    print(f"\nSettings:")
    print(f"  Stride length: {STRIDE_LENGTH}m")
    print(f"\nInstructions:")
    print("1. Start at origin (0, 0)")
    print("2. Press button BEFORE each stride")
    print("3. Walk one step")
    print("4. Watch LED show your heading")
    print("5. Ctrl+C when done")
    print("=" * 60)

    input("\nPress ENTER to start...")

    # Record initial position
    position_history.append({
        'stride': 0,
        'timestamp': datetime.utcnow().isoformat(),
        'x': 0.0,
        'y': 0.0,
        'heading_rad': 0.0,
        'heading_deg': 0.0
    })

    try:
        while True:
            # Wait for stride
            timestamp = wait_for_stride()

            # Get heading
            heading_rad = get_heading()
            heading_deg = np.degrees(heading_rad)

            # Show heading on LED
            visualize_heading(heading_rad)

            # Update position (NAIVE - just dead reckoning)
            new_x, new_y = update_position_naive(
                current_position['x'],
                current_position['y'],
                heading_rad,
                STRIDE_LENGTH
            )

            # Update state
            stride_count += 1
            current_position['x'] = new_x
            current_position['y'] = new_y

            # Record
            position_history.append({
                'stride': stride_count,
                'timestamp': datetime.utcnow().isoformat(),
                'x': round(new_x, 3),
                'y': round(new_y, 3),
                'heading_rad': round(heading_rad, 4),
                'heading_deg': round(heading_deg, 2)
            })

            # Print status
            print(f"\n--- Stride #{stride_count} ---")
            print(f"Position: ({new_x:.2f}, {new_y:.2f}) m")
            print(f"Heading: {heading_deg:.1f}°")
            print(f"Distance from start: {np.sqrt(new_x**2 + new_y**2):.2f}m")

    except KeyboardInterrupt:
        print("\n\nStopping tracker...")
        save_trajectory()
        sense.clear()

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total strides: {stride_count}")
        print(f"Final position: ({current_position['x']:.2f}, {current_position['y']:.2f})")
        print(f"Total distance traveled: {stride_count * STRIDE_LENGTH:.2f}m")

if __name__ == "__main__":
    main()
