"""
Mock SenseHat for testing on laptop without Raspberry Pi

This allows you to test the dashboard and algorithms locally
without needing the actual SenseHat hardware.
"""
import numpy as np
import time

class MockJoystick:
    """Mock joystick for testing"""
    def __init__(self):
        self.direction_up = None
        self.direction_down = None
        self.direction_left = None
        self.direction_right = None
        self.direction_middle = None
        self.direction_any = None

class SenseHat:
    """Mock SenseHat that simulates realistic sensor readings"""

    def __init__(self):
        self.current_heading = 0.0  # Current heading in radians
        self.time_offset = time.time()
        self.walking = False
        self.stick = MockJoystick()  # Add joystick support
        print("⚠️  Using MOCK SenseHat (for testing without Raspberry Pi)")

    def set_imu_config(self, compass, gyro, accel):
        """Mock IMU configuration"""
        pass

    def get_accelerometer_raw(self):
        """Return mock accelerometer data with walking simulation"""
        # Simulate walking: periodic acceleration spikes
        t = time.time() - self.time_offset

        # Walking creates periodic vertical acceleration
        walking_signal = np.sin(t * 2 * np.pi * 0.8)  # ~0.8 Hz walking frequency

        if walking_signal > 0.5:  # Simulate stride
            walking_accel = 1.5 + np.random.normal(0, 0.2)
        else:
            walking_accel = 0.0

        return {
            'x': np.random.normal(0, 0.05),
            'y': np.random.normal(0, 0.05),
            'z': 1.0 + walking_accel  # 1g gravity + walking acceleration
        }

    def get_gyroscope_raw(self):
        """Return mock gyroscope data"""
        return {
            'x': np.random.normal(0, 0.01),
            'y': np.random.normal(0, 0.01),
            'z': np.random.normal(0, 0.005)  # Heading drift
        }

    def get_compass_raw(self):
        """Return mock magnetometer data"""
        # Simulate magnetic field
        return {
            'x': np.cos(self.current_heading) + np.random.normal(0, 0.05),
            'y': np.sin(self.current_heading) + np.random.normal(0, 0.05),
            'z': np.random.normal(0, 0.05)
        }

    def get_orientation_degrees(self):
        """Return mock orientation in degrees"""
        yaw_deg = np.degrees(self.current_heading) % 360

        return {
            'pitch': np.random.normal(0, 2),
            'roll': np.random.normal(0, 2),
            'yaw': yaw_deg + np.random.normal(0, 3)  # Add sensor noise
        }

    def get_orientation_radians(self):
        """Return mock orientation in radians"""
        # Simulate slow heading drift (like real IMU)
        self.current_heading += np.random.normal(0, 0.01)

        # Keep heading in [0, 2π)
        self.current_heading = self.current_heading % (2 * np.pi)

        return {
            'pitch': np.random.normal(0, 0.02),
            'roll': np.random.normal(0, 0.02),
            'yaw': self.current_heading + np.random.normal(0, 0.05)
        }

    def get_temperature(self):
        """Return mock temperature (°C)"""
        return np.random.normal(24, 1)

    def get_pressure(self):
        """Return mock pressure (millibars)"""
        return np.random.normal(1013, 5)

    def get_humidity(self):
        """Return mock humidity (%)"""
        return np.random.normal(45, 5)

    def show_message(self, message, text_colour=None, scroll_speed=0.1):
        """Mock LED message display"""
        print(f"[Mock SenseHat LED] {message}")

    def clear(self):
        """Mock LED clear"""
        pass

    def set_pixels(self, pixels):
        """Mock LED matrix"""
        pass

    def get_pixels(self):
        """Mock get LED matrix"""
        return [[0, 0, 0] for _ in range(64)]
