"""
Linear Kalman Filter for Pedestrian Dead Reckoning
===================================================

Implements a linear Kalman filter for position estimation using:
- State: [x, y, vx, vy] (position and velocity)
- Measurements: stride-based position updates
- Process model: constant velocity
"""

import numpy as np


class KalmanFilter:
    """
    Linear Kalman Filter for 2D position tracking

    State vector: x = [x, y, vx, vy]
    - x, y: position in meters
    - vx, vy: velocity in m/s
    """

    def __init__(self, initial_x=0.0, initial_y=0.0, dt=1.0):
        """
        Initialize Kalman filter

        Args:
            initial_x: Initial x position (meters)
            initial_y: Initial y position (meters)
            dt: Time step (seconds)
        """
        self.dt = dt

        # State vector: [x, y, vx, vy]
        self.x = np.array([initial_x, initial_y, 0.0, 0.0])

        # State covariance matrix (uncertainty in state)
        self.P = np.eye(4) * 1.0

        # Process noise covariance
        q = 0.1  # Process noise magnitude
        self.Q = np.array([
            [q * dt**4/4, 0, q * dt**3/2, 0],
            [0, q * dt**4/4, 0, q * dt**3/2],
            [q * dt**3/2, 0, q * dt**2, 0],
            [0, q * dt**3/2, 0, q * dt**2]
        ])

        # Measurement noise covariance
        r = 0.5  # Measurement noise (meters)
        self.R = np.eye(2) * r**2

        # State transition matrix (constant velocity model)
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        # Measurement matrix (we measure position only)
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])

    def predict(self):
        """
        Prediction step: predict next state based on motion model
        """
        # Predict state: x = F * x
        self.x = self.F @ self.x

        # Predict covariance: P = F * P * F^T + Q
        self.P = self.F @ self.P @ self.F.T + self.Q

    def update(self, measurement):
        """
        Update step: incorporate measurement

        Args:
            measurement: [x, y] position measurement in meters
        """
        z = np.array(measurement)

        # Innovation (measurement residual)
        y = z - self.H @ self.x

        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R

        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # Update state: x = x + K * y
        self.x = self.x + K @ y

        # Update covariance: P = (I - K*H) * P
        I = np.eye(4)
        self.P = (I - K @ self.H) @ self.P

    def get_position(self):
        """
        Get current position estimate

        Returns:
            (x, y) tuple in meters
        """
        return (self.x[0], self.x[1])

    def get_velocity(self):
        """
        Get current velocity estimate

        Returns:
            (vx, vy) tuple in m/s
        """
        return (self.x[2], self.x[3])

    def get_state(self):
        """
        Get full state vector

        Returns:
            State vector [x, y, vx, vy]
        """
        return self.x.copy()

    def get_covariance(self):
        """
        Get state covariance matrix

        Returns:
            4x4 covariance matrix
        """
        return self.P.copy()


if __name__ == '__main__':
    """Test Kalman filter with simulated walk"""

    print("=" * 50)
    print("Testing Linear Kalman Filter")
    print("=" * 50)

    # Create filter
    kf = KalmanFilter(initial_x=0.0, initial_y=0.0, dt=0.5)

    # Simulate a straight walk with noise
    true_positions = []
    measurements = []
    estimates = []

    # Walk 10 steps in +x direction
    for i in range(10):
        # True position (0.7m stride length)
        true_x = i * 0.7
        true_y = 0.0
        true_positions.append((true_x, true_y))

        # Noisy measurement
        noise = np.random.normal(0, 0.3, 2)
        meas_x = true_x + noise[0]
        meas_y = true_y + noise[1]
        measurements.append((meas_x, meas_y))

        # Kalman filter
        kf.predict()
        kf.update([meas_x, meas_y])
        est = kf.get_position()
        estimates.append(est)

        print(f"Step {i+1}:")
        print(f"  True: ({true_x:.2f}, {true_y:.2f})")
        print(f"  Meas: ({meas_x:.2f}, {meas_y:.2f})")
        print(f"  Est:  ({est[0]:.2f}, {est[1]:.2f})")

    # Calculate errors
    meas_errors = [np.sqrt((m[0]-t[0])**2 + (m[1]-t[1])**2)
                   for m, t in zip(measurements, true_positions)]
    est_errors = [np.sqrt((e[0]-t[0])**2 + (e[1]-t[1])**2)
                  for e, t in zip(estimates, true_positions)]

    print("\n" + "=" * 50)
    print(f"Average measurement error: {np.mean(meas_errors):.3f}m")
    print(f"Average Kalman estimate error: {np.mean(est_errors):.3f}m")
    print(f"Improvement: {(1 - np.mean(est_errors)/np.mean(meas_errors)) * 100:.1f}%")
    print("=" * 50)
