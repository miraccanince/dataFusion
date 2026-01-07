"""
Bayesian Filter for Pedestrian Inertial Navigation
===================================================

Implementation of the non-recursive Bayesian filter from:
"Pedestrian inertial navigation with building floor plans for indoor
environments via non-recursive Bayesian filtering" - Koroglu & Yilmaz (2017)

Core Equation (Equation 5 from paper):
p(xk|Zk) ∝ p(xk|FP) × p(xk|dk, xk-1) × p(zk|xk) × p(xk|xk-1,...,xk-n) × p(xk-1|Zk-1)

Where:
- p(xk|FP): Static floor plan PDF (high in walkable areas, low at walls)
- p(xk|dk, xk-1): Stride length circle (Gaussian circle at distance dk)
- p(zk|xk): Sensor likelihood (IMU heading prediction)
- p(xk|xk-1,...,xk-n): Extended motion model (linear/curved prediction)
- p(xk-1|Zk-1): Previous posterior estimate
"""

import numpy as np
from scipy.optimize import minimize
from scipy.stats import multivariate_normal
import matplotlib.pyplot as plt


class FloorPlanPDF:
    """
    Static floor plan probability distribution p(xk|FP)

    Creates a rasterized probability grid where walkable areas have high
    probability and walls/obstacles have low probability.
    """

    def __init__(self, width_m=3.5, height_m=6.0, resolution=0.1):
        """
        Initialize floor plan PDF

        Args:
            width_m: Width in meters (OUTER dimensions including walls, default 3.5m)
            height_m: Height in meters (OUTER dimensions including walls, default 6.0m)
            resolution: Grid resolution in meters (default 0.1m = 10cm)
        """
        self.width_m = width_m
        self.height_m = height_m
        self.resolution = resolution

        # Grid dimensions (these define the total area including walls)
        self.grid_width = int(width_m / resolution)
        self.grid_height = int(height_m / resolution)

        # Create simple L-shaped hallway floor plan
        self.grid = self._create_simple_floor_plan()

        # DON'T normalize by sum (makes values too small)
        # Grid values are already in range [0.01, 1.0] from _create_simple_floor_plan

    def _create_simple_floor_plan(self):
        """
        Create a single rectangular room (3.5m x 6m) with 4 walls

        Layout (the room dimensions INCLUDE the walls):
        ######################  <- 0.0m (top wall)
        ##                  ##
        ##                  ##
        ##   Single Room    ##
        ##   3.5m x 6m      ##
        ##   (inner space)  ##
        ##                  ##
        ######################  <- 6.0m (bottom wall)
        ^                    ^
        0.0m                3.5m
        (left wall)      (right wall)

        The OUTER dimensions are 3.5m x 6.0m.
        Walls are 0.3m thick on all sides.
        Walkable area is interior only.
        """
        # Start with all walls (low probability everywhere)
        grid = np.ones((self.grid_height, self.grid_width)) * 0.01

        # Define wall thickness (must be thick enough to be visible)
        wall_thickness = 0.3  # meters

        # Calculate walkable area INSIDE the walls
        # Leave wall_thickness space from ALL edges (0, width_m, 0, height_m)
        x_start = int(wall_thickness / self.resolution)
        x_end = int((self.width_m - wall_thickness) / self.resolution)
        y_start = int(wall_thickness / self.resolution)
        y_end = int((self.height_m - wall_thickness) / self.resolution)

        # Ensure we don't go outside grid bounds
        x_start = max(0, min(x_start, self.grid_width - 1))
        x_end = max(x_start + 1, min(x_end, self.grid_width))
        y_start = max(0, min(y_start, self.grid_height - 1))
        y_end = max(y_start + 1, min(y_end, self.grid_height))

        # Fill ONLY the walkable area (interior) with high probability
        # Everything outside this rectangle remains low probability (walls)
        grid[y_start:y_end, x_start:x_end] = 1.0

        # NO SMOOTHING - Keep sharp binary walls
        # Walls = 0.01 (1% probability)
        # Walkable = 1.0 (100% probability)
        # This creates 4 clean wall lines with no gradient zones

        return grid

    def get_probability(self, x, y):
        """
        Get probability at position (x, y) in meters

        Args:
            x: X coordinate in meters
            y: Y coordinate in meters

        Returns:
            Probability density at (x, y)
        """
        # Convert to grid coordinates
        grid_x = int(x / self.resolution)
        grid_y = int(y / self.resolution)

        # Check bounds
        if (0 <= grid_x < self.grid_width and
            0 <= grid_y < self.grid_height):
            return self.grid[grid_y, grid_x]
        else:
            return 0.01  # Low probability outside bounds

    def visualize(self, save_path=None):
        """Visualize the floor plan PDF"""
        plt.figure(figsize=(12, 6))
        plt.imshow(self.grid, origin='lower', cmap='YlOrRd',
                   extent=[0, self.width_m, 0, self.height_m])
        plt.colorbar(label='Walking Likelihood')
        plt.xlabel('X (meters)')
        plt.ylabel('Y (meters)')
        plt.title('Floor Plan Probability Distribution p(xk|FP)')
        plt.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        return plt


class BayesianNavigationFilter:
    """
    Non-recursive Bayesian filter for pedestrian navigation
    Implements Equation 5 from Koroglu & Yilmaz (2017)
    """

    def __init__(self, floor_plan, stride_length=0.7, n_history=3):
        """
        Initialize Bayesian filter

        Args:
            floor_plan: FloorPlanPDF object
            stride_length: Default stride length in meters
            n_history: Number of previous positions to use in motion model
        """
        self.floor_plan = floor_plan
        self.stride_length = stride_length
        self.n_history = n_history

        # Position history for extended motion model
        self.position_history = []

        # Current posterior estimate
        self.current_estimate = {'x': 2.0, 'y': 4.0}  # Start position
        self.current_covariance = np.eye(2) * 0.5  # Initial uncertainty

        # Tunable parameters
        self.sigma_stride = 0.1  # Stride length uncertainty (meters)
        self.sigma_heading = 0.5  # Heading uncertainty (radians) - trust IMU heading
        self.sigma_motion = 0.5  # Motion model uncertainty (meters)

        # Floor plan weight (higher = stronger wall constraints)
        # CRITICAL: Must be EXTREMELY high to prevent wall crossing when IMU points through wall
        # With weight=1000: wall penalty = 1000*log(0.019) ≈ -3900 (MASSIVE)
        # This creates an impenetrable energy barrier at walls
        self.floor_plan_weight = 1000.0  # EXTREMELY strong - walls are HARD constraints!

    def p_stride_circle(self, x, y, x_prev, y_prev, stride_length):
        """
        p(xk|dk, xk-1): Stride length circle PDF

        Circular Gaussian centered at previous position with radius = stride_length.
        This exploits the fact that ZUPT gives accurate stride lengths.

        Args:
            x, y: Candidate position
            x_prev, y_prev: Previous position
            stride_length: Measured stride length from ZUPT

        Returns:
            Probability density
        """
        # Distance from previous position
        distance = np.sqrt((x - x_prev)**2 + (y - y_prev)**2)

        # Gaussian centered at stride_length
        prob = np.exp(-0.5 * ((distance - stride_length) / self.sigma_stride)**2)
        prob /= (self.sigma_stride * np.sqrt(2 * np.pi))

        return prob

    def p_sensor_likelihood(self, x, y, x_prev, y_prev, heading, stride_length):
        """
        p(zk|xk): Sensor likelihood based on IMU heading (Equation 4)

        zk = x_{k-1} + dk * [sin(heading), cos(heading)]

        Args:
            x, y: Candidate position
            x_prev, y_prev: Previous position
            heading: IMU heading in radians
            stride_length: Stride length

        Returns:
            Probability density
        """
        # IMU prediction (navigation convention: 0°=North, x = sin, y = cos)
        z_x = x_prev + stride_length * np.sin(heading)
        z_y = y_prev + stride_length * np.cos(heading)

        # Gaussian likelihood centered at IMU prediction
        mean = np.array([z_x, z_y])
        cov = np.eye(2) * self.sigma_heading**2

        try:
            prob = multivariate_normal.pdf([x, y], mean=mean, cov=cov)
        except:
            prob = 1e-10

        return prob

    def p_motion_model(self, x, y):
        """
        p(xk|xk-1, ..., xk-n): Extended motion model

        For pedestrian navigation, we use a WEAK uniform prior since
        the IMU heading is much more reliable than velocity extrapolation.
        Velocity extrapolation fights direction changes and causes errors.

        Args:
            x, y: Candidate position

        Returns:
            Probability density
        """
        # Use uniform weak prior - don't fight the IMU heading
        # The IMU sensor likelihood p(zk|xk) handles direction
        return 1.0

    def p_previous_posterior(self, x, y):
        """
        p(xk-1|Zk-1): Previous posterior estimate

        Weak Gaussian around previous estimate to provide continuity
        but not fight the floor plan constraints.

        Args:
            x, y: Candidate position

        Returns:
            Probability density
        """
        mean = np.array([self.current_estimate['x'], self.current_estimate['y']])

        # Use VERY large covariance (weak constraint) to avoid rubber-band effect
        # This just provides gentle continuity without fighting wall constraints
        weak_cov = np.eye(2) * 2.0  # Large uncertainty (2m std dev)

        try:
            prob = multivariate_normal.pdf([x, y], mean=mean, cov=weak_cov)
        except:
            prob = 1e-10

        return prob

    def posterior_probability(self, pos, x_prev, y_prev, heading, stride_length):
        """
        Compute full posterior probability (Equation 5)

        p(xk|Zk) ∝ p(xk|FP) × p(xk|dk, xk-1) × p(zk|xk) ×
                    p(xk|xk-1,...,xk-n) × p(xk-1|Zk-1)

        Args:
            pos: [x, y] position to evaluate
            x_prev, y_prev: Previous position
            heading: IMU heading in radians
            stride_length: Stride length

        Returns:
            Posterior probability (log scale for numerical stability)
        """
        x, y = pos

        # 1. Floor plan PDF p(xk|FP)
        p_fp = self.floor_plan.get_probability(x, y)

        # 2. Stride circle p(xk|dk, xk-1)
        p_stride = self.p_stride_circle(x, y, x_prev, y_prev, stride_length)

        # 3. Sensor likelihood p(zk|xk)
        p_sensor = self.p_sensor_likelihood(x, y, x_prev, y_prev, heading, stride_length)

        # 4. Motion model p(xk|xk-1,...,xk-n)
        p_motion = self.p_motion_model(x, y)

        # 5. Previous posterior p(xk-1|Zk-1)
        p_prev = self.p_previous_posterior(x, y)

        # Combine (use log probabilities for numerical stability)
        # Apply extra weight to floor plan to enforce wall constraints
        log_posterior = (self.floor_plan_weight * np.log(p_fp + 1e-10) +
                        np.log(p_stride + 1e-10) +
                        np.log(p_sensor + 1e-10) +
                        np.log(p_motion + 1e-10) +
                        np.log(p_prev + 1e-10))

        return log_posterior

    def negative_posterior(self, pos, x_prev, y_prev, heading, stride_length):
        """Negative posterior for minimization"""
        return -self.posterior_probability(pos, x_prev, y_prev, heading, stride_length)

    def update(self, heading, stride_length):
        """
        Update filter with new stride

        Args:
            heading: IMU heading in radians
            stride_length: Measured stride length

        Returns:
            Estimated position {'x': ..., 'y': ...}
        """
        x_prev = self.current_estimate['x']
        y_prev = self.current_estimate['y']

        # IMU prediction (navigation convention: 0°=North, x = sin, y = cos)
        imu_x = x_prev + stride_length * np.sin(heading)
        imu_y = y_prev + stride_length * np.cos(heading)

        # CRITICAL: Check if PATH from current to IMU prediction crosses through wall
        # Sample points along the line segment to detect wall crossing
        n_samples = 10
        path_crosses_wall = False
        for i in range(1, n_samples + 1):
            t = i / n_samples
            sample_x = x_prev + t * (imu_x - x_prev)
            sample_y = y_prev + t * (imu_y - y_prev)
            sample_prob = self.floor_plan.get_probability(sample_x, sample_y)

            # If any point along path has very low probability, it's a wall
            if sample_prob < 0.1:  # Wall threshold
                path_crosses_wall = True
                break

        if path_crosses_wall:
            # Path would cross wall - start optimization from safe current position
            x0 = [x_prev, y_prev]
        else:
            # Path is clear - start from IMU prediction (normal case)
            x0 = [imu_x, imu_y]

        # Mode-seeking: Find maximum of posterior (minimize negative posterior)
        result = minimize(
            self.negative_posterior,
            x0,
            args=(x_prev, y_prev, heading, stride_length),
            method='L-BFGS-B',
            bounds=[(0, self.floor_plan.width_m), (0, self.floor_plan.height_m)]
        )

        # Extract estimate
        x_est, y_est = result.x

        # Update current estimate
        self.current_estimate = {'x': float(x_est), 'y': float(y_est)}

        # Update covariance (simple approach: use inverse Hessian approximation)
        # For now, keep it constant
        self.current_covariance = np.eye(2) * 0.3

        # Add to history
        self.position_history.append(self.current_estimate.copy())

        # Keep only last 10 positions
        if len(self.position_history) > 10:
            self.position_history.pop(0)

        return self.current_estimate

    def reset(self, x=2.0, y=4.0):
        """Reset filter to initial state"""
        self.position_history = []
        self.current_estimate = {'x': x, 'y': y}
        self.current_covariance = np.eye(2) * 0.5


# Example usage and testing
if __name__ == '__main__':
    print("=" * 70)
    print("Bayesian Filter for Pedestrian Navigation")
    print("=" * 70)

    # Create floor plan
    print("\n1. Creating floor plan PDF...")
    floor_plan = FloorPlanPDF(width_m=20.0, height_m=10.0, resolution=0.1)
    print(f"   Grid size: {floor_plan.grid_width} × {floor_plan.grid_height}")

    # Visualize floor plan
    print("\n2. Visualizing floor plan...")
    floor_plan.visualize(save_path='floor_plan_pdf.png')
    print("   Saved to: floor_plan_pdf.png")

    # Create filter
    print("\n3. Initializing Bayesian filter...")
    bf = BayesianNavigationFilter(floor_plan, stride_length=0.7)
    print(f"   Start position: ({bf.current_estimate['x']:.2f}, {bf.current_estimate['y']:.2f})")

    # Simulate some steps
    print("\n4. Simulating walking...")
    headings = [0.0, 0.0, 0.0, np.pi/2, np.pi/2, np.pi/2]  # North, then East
    stride_lengths = [0.7, 0.7, 0.7, 0.7, 0.7, 0.7]

    trajectory = [bf.current_estimate.copy()]

    for i, (heading, stride) in enumerate(zip(headings, stride_lengths)):
        pos = bf.update(heading, stride)
        trajectory.append(pos.copy())
        print(f"   Step {i+1}: heading={np.degrees(heading):.0f}°, "
              f"position=({pos['x']:.2f}, {pos['y']:.2f})")

    print("\n" + "=" * 70)
    print("✓ Bayesian filter implementation complete!")
    print("=" * 70)
