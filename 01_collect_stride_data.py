"""
STEP 1: Naive Data Collection with Joystick
============================================
Goal: Collect sensor data on each stride (button press)
Output: CSV file for analysis

Usage: python 01_collect_stride_data.py
       Press joystick middle button for each stride
       Ctrl+C to stop and save
"""

import time
import csv
from datetime import datetime
from sense_hat import SenseHat

sense = SenseHat()
sense.set_imu_config(True, True, True)  # gyro, accel, mag ON

# Storage for our stride data
stride_data = []
stride_count = 0

def wait_for_button_press():
    """Wait for middle joystick button press"""
    print("Waiting for button press...")
    button_pressed = False

    while not button_pressed:
        for event in sense.stick.get_events():
            if event.direction == 'middle' and event.action == 'pressed':
                button_pressed = True
                # Visual feedback
                sense.show_message("!", text_colour=[0, 255, 0], scroll_speed=0.05)
                sense.clear()
                break
        time.sleep(0.01)  # Small delay to prevent CPU overload

def read_stride_data():
    """Read all sensor data for this stride"""
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Orientation
    orientation = sense.get_orientation_degrees()

    # Raw IMU data
    accel = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()
    mag = sense.get_compass_raw()

    # Also get radians for later use
    orientation_rad = sense.get_orientation_radians()

    data = {
        'timestamp': timestamp,
        'stride_number': stride_count,
        # Orientation in degrees
        'pitch_deg': round(orientation.get('pitch', 0), 2),
        'roll_deg': round(orientation.get('roll', 0), 2),
        'yaw_deg': round(orientation.get('yaw', 0), 2),
        # Orientation in radians
        'pitch_rad': round(orientation_rad.get('pitch', 0), 4),
        'roll_rad': round(orientation_rad.get('roll', 0), 4),
        'yaw_rad': round(orientation_rad.get('yaw', 0), 4),
        # Accelerometer
        'accel_x': round(accel.get('x', 0), 4),
        'accel_y': round(accel.get('y', 0), 4),
        'accel_z': round(accel.get('z', 0), 4),
        # Gyroscope
        'gyro_x': round(gyro.get('x', 0), 4),
        'gyro_y': round(gyro.get('y', 0), 4),
        'gyro_z': round(gyro.get('z', 0), 4),
        # Magnetometer
        'mag_x': round(mag.get('x', 0), 4),
        'mag_y': round(mag.get('y', 0), 4),
        'mag_z': round(mag.get('z', 0), 4),
    }

    return data

def save_to_csv(filename='stride_data.csv'):
    """Save collected data to CSV file"""
    if not stride_data:
        print("No data to save!")
        return

    fieldnames = stride_data[0].keys()

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stride_data)

    print(f"\n✓ Data saved to {filename}")
    print(f"✓ Total strides collected: {len(stride_data)}")

def main():
    global stride_count

    print("=" * 60)
    print("NAIVE STRIDE DATA COLLECTOR")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Start at a known position")
    print("2. Press joystick button BEFORE each stride")
    print("3. Take one step")
    print("4. Repeat")
    print("5. Press Ctrl+C when done\n")
    print("=" * 60)

    try:
        while True:
            # Wait for button press
            wait_for_button_press()

            # Record data
            stride_count += 1
            data = read_stride_data()
            stride_data.append(data)

            # Print feedback
            print(f"\nStride #{stride_count} recorded")
            print(f"  Yaw: {data['yaw_deg']:.1f}°")
            print(f"  Accel: ({data['accel_x']:.2f}, {data['accel_y']:.2f}, {data['accel_z']:.2f})")
            print("  → Press button for next stride...")

    except KeyboardInterrupt:
        print("\n\nStopping collection...")
        save_to_csv('stride_data.csv')
        print("\nDone!")

if __name__ == "__main__":
    main()
