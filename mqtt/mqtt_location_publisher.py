"""
MQTT Program 2: SenseHAT Location Publisher
============================================

Publishes predicted location from Bayesian algorithm via MQTT.
Publishes Sense HAT data and position estimates every 10ms (if possible).

Assignment: Part 1 - Data Stream Management System (15%)

Usage:
    python3 mqtt_location_publisher.py [--broker BROKER_IP] [--interval MS]
"""

import paho.mqtt.client as mqtt
from sense_hat import SenseHat
import sys
import os
import json
import time
import argparse
from datetime import datetime
import numpy as np

# Add src directory to path to import bayesian_filter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from bayesian_filter import BayesianNavigationFilter, FloorPlanPDF


class LocationPublisher:
    """
    Publishes Sense HAT IMU data and Bayesian filter position estimates via MQTT

    Data Published:
    - Raw IMU data (accelerometer, gyroscope, magnetometer)
    - Orientation (pitch, roll, yaw)
    - Bayesian filter position estimate (x, y)
    - Naive dead reckoning position (for comparison)
    - Timestamp (ISO format)
    """

    def __init__(self, broker='localhost', port=1883, interval_ms=10, stride_length=0.7):
        """
        Initialize location publisher

        Args:
            broker: MQTT broker IP address
            port: MQTT broker port
            interval_ms: Publishing interval in milliseconds
            stride_length: Stride length in meters
        """
        self.broker = broker
        self.port = port
        self.interval = interval_ms / 1000.0

        # Initialize Sense HAT
        print("Initializing Sense HAT...")
        self.sense = SenseHat()
        self.sense.set_imu_config(True, True, True)
        print("✓ Sense HAT ready")

        # Initialize Bayesian filter
        print("Initializing Bayesian filter...")
        self.floor_plan = FloorPlanPDF(width_m=20.0, height_m=10.0, resolution=0.1)
        self.bayesian_filter = BayesianNavigationFilter(
            self.floor_plan,
            stride_length=stride_length
        )
        print("✓ Bayesian filter ready")

        # State tracking
        self.naive_position = {'x': 0.0, 'y': 0.0}
        self.stride_count = 0
        self.stride_length = stride_length

        # Previous heading for stride detection
        self.prev_heading = None
        self.last_stride_time = time.time()

        # MQTT topics
        self.topic_base = "dataFusion/location"
        self.topic_imu = f"{self.topic_base}/imu"
        self.topic_position = f"{self.topic_base}/position"
        self.topic_status = f"{self.topic_base}/status"

        # MQTT client
        self.client = mqtt.Client(client_id="location_publisher")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        self.connected = False
        self.message_count = 0

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            print(f"✓ Connected to MQTT broker at {self.broker}:{self.port}")

            # Publish status
            status_msg = {
                'status': 'online',
                'timestamp': datetime.utcnow().isoformat(),
                'interval_ms': self.interval * 1000,
                'publisher': 'location',
                'stride_length': self.stride_length
            }
            client.publish(self.topic_status, json.dumps(status_msg), qos=1, retain=True)
        else:
            print(f"✗ Connection failed with code {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected"""
        self.connected = False
        if rc != 0:
            print(f"⚠ Unexpected disconnection. Code: {rc}")

    def get_imu_data(self):
        """
        Get IMU sensor data from Sense HAT

        Returns:
            dict: IMU readings with timestamp
        """
        # Raw sensor data
        accel = self.sense.get_accelerometer_raw()
        gyro = self.sense.get_gyroscope_raw()
        mag = self.sense.get_magnetometer_raw()

        # Orientation (fused from sensors)
        orientation_deg = self.sense.get_orientation_degrees()
        orientation_rad = self.sense.get_orientation_radians()

        # Environmental (bonus)
        temperature = self.sense.get_temperature()
        pressure = self.sense.get_pressure()
        humidity = self.sense.get_humidity()

        imu_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': self.message_count,
            'accelerometer': {
                'x': round(accel['x'], 4),
                'y': round(accel['y'], 4),
                'z': round(accel['z'], 4)
            },
            'gyroscope': {
                'x': round(gyro['x'], 4),
                'y': round(gyro['y'], 4),
                'z': round(gyro['z'], 4)
            },
            'magnetometer': {
                'x': round(mag['x'], 4),
                'y': round(mag['y'], 4),
                'z': round(mag['z'], 4)
            },
            'orientation_degrees': {
                'pitch': round(orientation_deg['pitch'], 2),
                'roll': round(orientation_deg['roll'], 2),
                'yaw': round(orientation_deg['yaw'], 2)
            },
            'orientation_radians': {
                'pitch': round(orientation_rad['pitch'], 4),
                'roll': round(orientation_rad['roll'], 4),
                'yaw': round(orientation_rad['yaw'], 4)
            },
            'environment': {
                'temperature_c': round(temperature, 2),
                'pressure_mb': round(pressure, 2),
                'humidity_percent': round(humidity, 2)
            }
        }

        return imu_data

    def detect_stride(self, current_accel, threshold=1.2):
        """
        Simple stride detection based on acceleration magnitude

        Args:
            current_accel: Current accelerometer reading
            threshold: Acceleration threshold for step detection (g)

        Returns:
            bool: True if stride detected
        """
        # Calculate acceleration magnitude
        accel_mag = np.sqrt(
            current_accel['x']**2 +
            current_accel['y']**2 +
            current_accel['z']**2
        )

        # Detect if magnitude exceeds threshold (indicates step)
        # Also check minimum time between strides (0.3s typical)
        if accel_mag > threshold:
            current_time = time.time()
            if (current_time - self.last_stride_time) > 0.3:
                self.last_stride_time = current_time
                return True

        return False

    def update_positions(self, heading_rad, stride_detected=False):
        """
        Update position estimates (Bayesian and naive)

        Args:
            heading_rad: Current heading in radians
            stride_detected: Whether a stride was detected

        Returns:
            dict: Position data
        """
        if stride_detected:
            self.stride_count += 1

            # Update Bayesian filter
            bayesian_pos = self.bayesian_filter.update(
                heading=heading_rad,
                stride_length=self.stride_length
            )

            # Update naive dead reckoning
            self.naive_position['x'] += self.stride_length * np.sin(heading_rad)
            self.naive_position['y'] += self.stride_length * np.cos(heading_rad)

        else:
            bayesian_pos = self.bayesian_filter.current_estimate

        position_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': self.message_count,
            'stride_count': self.stride_count,
            'stride_detected': stride_detected,
            'bayesian': {
                'x': round(bayesian_pos['x'], 3),
                'y': round(bayesian_pos['y'], 3)
            },
            'naive': {
                'x': round(self.naive_position['x'], 3),
                'y': round(self.naive_position['y'], 3)
            },
            'heading_rad': round(heading_rad, 4),
            'heading_deg': round(np.degrees(heading_rad), 2)
        }

        return position_data

    def publish_data(self):
        """Collect and publish IMU and position data"""
        # Get IMU data
        imu_data = self.get_imu_data()

        # Publish IMU data
        self.client.publish(
            self.topic_imu,
            json.dumps(imu_data),
            qos=0
        )

        # Detect stride (simple acceleration-based)
        stride_detected = self.detect_stride(imu_data['accelerometer'])

        # Update and publish position
        heading_rad = imu_data['orientation_radians']['yaw']
        position_data = self.update_positions(heading_rad, stride_detected)

        self.client.publish(
            self.topic_position,
            json.dumps(position_data),
            qos=0
        )

        self.message_count += 1

        # Print status every 100 messages
        if self.message_count % 100 == 0:
            print(f"Messages: {self.message_count} | "
                  f"Strides: {self.stride_count} | "
                  f"Bayesian: ({position_data['bayesian']['x']:.2f}, {position_data['bayesian']['y']:.2f}) | "
                  f"Naive: ({position_data['naive']['x']:.2f}, {position_data['naive']['y']:.2f})")

    def run(self, duration_seconds=None):
        """
        Start publishing location data

        Args:
            duration_seconds: How long to run (None = infinite)
        """
        print("=" * 70)
        print("MQTT SenseHAT Location Publisher")
        print("=" * 70)
        print(f"Broker: {self.broker}:{self.port}")
        print(f"Topics:")
        print(f"  - IMU data: {self.topic_imu}")
        print(f"  - Position: {self.topic_position}")
        print(f"Interval: {self.interval * 1000:.1f}ms")
        print(f"Stride length: {self.stride_length}m")
        print(f"Duration: {'Infinite' if duration_seconds is None else f'{duration_seconds}s'}")
        print("=" * 70)

        # Connect to MQTT broker
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"✗ Failed to connect to broker: {e}")
            return

        # Wait for connection
        timeout = 10
        start = time.time()
        while not self.connected and (time.time() - start) < timeout:
            time.sleep(0.1)

        if not self.connected:
            print("✗ Connection timeout")
            return

        print("\n✓ Publishing location data (Ctrl+C to stop)...\n")

        # Publishing loop
        start_time = time.time()
        try:
            while True:
                if duration_seconds is not None:
                    if (time.time() - start_time) >= duration_seconds:
                        print(f"\n✓ Duration limit reached ({duration_seconds}s)")
                        break

                self.publish_data()
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n\n✓ Stopped by user")

        # Cleanup
        print(f"\nTotal messages: {self.message_count}")
        print(f"Total strides: {self.stride_count}")

        # Publish offline status
        status_msg = {
            'status': 'offline',
            'timestamp': datetime.utcnow().isoformat(),
            'total_messages': self.message_count,
            'total_strides': self.stride_count
        }
        self.client.publish(self.topic_status, json.dumps(status_msg), qos=1, retain=True)

        self.client.loop_stop()
        self.client.disconnect()
        print("✓ Disconnected from broker")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Publish SenseHAT location data via MQTT'
    )
    parser.add_argument(
        '--broker', '-b',
        default='localhost',
        help='MQTT broker IP address (default: localhost)'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=1883,
        help='MQTT broker port (default: 1883)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=10,
        help='Publishing interval in milliseconds (default: 10ms)'
    )
    parser.add_argument(
        '--stride', '-s',
        type=float,
        default=0.7,
        help='Stride length in meters (default: 0.7m)'
    )
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=None,
        help='Duration in seconds (default: infinite)'
    )

    args = parser.parse_args()

    # Create and run publisher
    publisher = LocationPublisher(
        broker=args.broker,
        port=args.port,
        interval_ms=args.interval,
        stride_length=args.stride
    )

    publisher.run(duration_seconds=args.duration)


if __name__ == '__main__':
    main()
