# Create

# python
import time
import argparse
import json
from datetime import datetime

# Try to import SenseHat; script will exit with a clear message if not available.
try:
    from sense_hat import SenseHat
except Exception as e:
    raise SystemExit(
        "Sense HAT library not available. Install it on the Raspberry Pi with:\n"
        "  sudo apt-get install sense-hat python3-sense-emu-sense-hat\n"
        "or use the real Sense HAT image. Original error: " + str(e)
    )

sense = SenseHat()
sense.set_imu_config(True, True, True)  # enable gyroscope, accelerometer, magnetometer

def read_sensors():
    """
    Read all available sensors from the Sense HAT and return a dict.
    """
    # Environment
    temp_c = sense.get_temperature()
    humidity = sense.get_humidity()
    pressure = sense.get_pressure()

    # Orientation (degrees)
    orientation = sense.get_orientation_degrees()
    pitch = orientation.get("pitch")
    roll = orientation.get("roll")
    yaw = orientation.get("yaw")

    # Raw vectors
    accel = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()
    mag = sense.get_compass_raw()

    # Rounded/structured output
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "temperature_c": round(temp_c, 2) if temp_c is not None else None,
        "humidity_percent": round(humidity, 2) if humidity is not None else None,
        "pressure_mbar": round(pressure, 2) if pressure is not None else None,
        "orientation_deg": {
            "pitch": round(pitch, 2) if pitch is not None else None,
            "roll": round(roll, 2) if roll is not None else None,
            "yaw": round(yaw, 2) if yaw is not None else None,
        },
        "accelerometer_g": {
            "x": round(accel.get("x", 0), 4),
            "y": round(accel.get("y", 0), 4),
            "z": round(accel.get("z", 0), 4),
        },
        "gyroscope_dps": {
            "x": round(gyro.get("x", 0), 4),
            "y": round(gyro.get("y", 0), 4),
            "z": round(gyro.get("z", 0), 4),
        },
        "magnetometer_uT": {
            "x": round(mag.get("x", 0), 4),
            "y": round(mag.get("y", 0), 4),
            "z": round(mag.get("z", 0), 4),
        },
    }
    return data

def pretty_print(data):
    """
    Print human-readable lines for the most common sensors.
    """
    print(f"{data['timestamp']}")
    print(f"Temperature: {data['temperature_c']} °C   Humidity: {data['humidity_percent']} %   Pressure: {data['pressure_mbar']} mbar")
    o = data['orientation_deg']
    print(f"Orientation (deg) - Pitch: {o['pitch']}, Roll: {o['roll']}, Yaw: {o['yaw']}")
    a = data['accelerometer_g']
    print(f"Accel (g) - x:{a['x']} y:{a['y']} z:{a['z']}")
    g = data['gyroscope_dps']
    print(f"Gyro (deg/s) - x:{g['x']} y:{g['y']} z:{g['z']}")
    m = data['magnetometer_uT']
    print(f"Mag (uT) - x:{m['x']} y:{m['y']} z:{m['z']}")
    print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description="Read sensors from Sense HAT and print readings.")
    parser.add_argument("--interval", "-i", type=float, default=1.0, help="Interval in seconds for continuous reading (default 1.0)")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of samples to take (default 1). Use 0 for infinite.")
    parser.add_argument("--json", action="store_true", help="Output JSON per reading instead of pretty text.")
    args = parser.parse_args()

    interval = max(0.01, args.interval)
    count = args.count

    taken = 0
    try:
        while True:
            data = read_sensors()
            if args.json:
                print(json.dumps(data))
            else:
                pretty_print(data)

            taken += 1
            if count > 0 and taken >= count:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")

if __name__ == "__main__":
    main()