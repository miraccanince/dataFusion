"""
Understanding the 3 IMU Sensors
================================
Run this on Raspberry Pi to see what each sensor outputs

Usage: python understand_sensors.py
       Move the Raspberry Pi around and watch the values
"""

from sense_hat import SenseHat
import time
import numpy as np

sense = SenseHat()
sense.set_imu_config(True, True, True)

print("=" * 80)
print("IMU SENSOR EXPLORER")
print("=" * 80)
print("\nYour Sense HAT has 3 sensors × 3 axes = 9 degrees of freedom\n")
print("Move the Raspberry Pi around and observe:")
print("  - Tilt it → Accelerometer changes")
print("  - Rotate it → Gyroscope shows rotation rate")
print("  - Spin it → Magnetometer shows compass direction")
print("\nPress Ctrl+C to stop\n")
print("=" * 80)

def classify_motion(accel, gyro):
    """Simple motion classification"""
    accel_mag = np.sqrt(accel['x']**2 + accel['y']**2 + accel['z']**2)
    gyro_mag = np.sqrt(gyro['x']**2 + gyro['y']**2 + gyro['z']**2)

    if accel_mag > 1.2:
        motion = "MOVING/SHAKING"
    elif gyro_mag > 10:
        motion = "ROTATING"
    else:
        motion = "STILL"

    return motion

try:
    while True:
        # Get raw sensor data
        accel = sense.get_accelerometer_raw()
        gyro = sense.get_gyroscope_raw()
        mag = sense.get_compass_raw()

        # Get orientation (fused from all sensors)
        orientation = sense.get_orientation_degrees()

        # Calculate magnitudes
        accel_mag = np.sqrt(accel['x']**2 + accel['y']**2 + accel['z']**2)
        gyro_mag = np.sqrt(gyro['x']**2 + gyro['y']**2 + gyro['z']**2)
        mag_mag = np.sqrt(mag['x']**2 + mag['y']**2 + mag['z']**2)

        # Classify motion
        motion = classify_motion(accel, gyro)

        # Display
        print("\n" + "─" * 80)
        print(f"Motion State: {motion}")
        print("─" * 80)

        print("\n1️⃣  ACCELEROMETER (measures: linear acceleration + gravity)")
        print(f"   Raw: X={accel['x']:+.3f}g  Y={accel['y']:+.3f}g  Z={accel['z']:+.3f}g")
        print(f"   Magnitude: {accel_mag:.3f}g  (1g = stationary, >1g = moving)")
        print(f"   💡 Use for: Step detection, tilt sensing")

        print("\n2️⃣  GYROSCOPE (measures: rotation rate)")
        print(f"   Raw: X={gyro['x']:+.3f}°/s  Y={gyro['y']:+.3f}°/s  Z={gyro['z']:+.3f}°/s")
        print(f"   Magnitude: {gyro_mag:.1f}°/s  (0 = no rotation)")
        print(f"   💡 Use for: Heading changes (yaw), turn detection")

        print("\n3️⃣  MAGNETOMETER (measures: magnetic field)")
        print(f"   Raw: X={mag['x']:+.1f}µT  Y={mag['y']:+.1f}µT  Z={mag['z']:+.1f}µT")
        print(f"   Magnitude: {mag_mag:.1f}µT  (Earth's field ~25-65µT)")
        print(f"   💡 Use for: Compass heading (unreliable indoors!)")

        print("\n🔄 FUSED ORIENTATION (combined from all 3 sensors)")
        print(f"   Pitch: {orientation['pitch']:>6.1f}°  (nose up/down)")
        print(f"   Roll:  {orientation['roll']:>6.1f}°  (wing up/down)")
        print(f"   Yaw:   {orientation['yaw']:>6.1f}°  (heading direction) ← IMPORTANT!")

        time.sleep(0.5)

except KeyboardInterrupt:
    sense.clear()
    print("\n\n" + "=" * 80)
    print("SUMMARY: What Each Sensor Does for Pedestrian Navigation")
    print("=" * 80)
    print("""
┌─────────────────┬──────────────────────┬─────────────────────────┐
│ Sensor          │ Primary Use          │ Key Challenge           │
├─────────────────┼──────────────────────┼─────────────────────────┤
│ Accelerometer   │ Detect strides       │ Very noisy              │
│                 │ (peaks in |a|)       │ Affected by vibrations  │
├─────────────────┼──────────────────────┼─────────────────────────┤
│ Gyroscope       │ Heading direction    │ Drifts over time        │
│                 │ (integrate yaw rate) │ Needs correction        │
├─────────────────┼──────────────────────┼─────────────────────────┤
│ Magnetometer    │ Absolute heading     │ Disturbed by metal      │
│                 │ (compass)            │ Unreliable indoors      │
└─────────────────┴──────────────────────┴─────────────────────────┘

This is why we need BAYESIAN FILTERING with FLOOR PLAN:
- Accelerometer too noisy → Kalman filter helps
- Gyroscope drifts → Floor plan constrains heading
- Magnetometer unreliable → Use building structure instead
""")
    print("=" * 80)
