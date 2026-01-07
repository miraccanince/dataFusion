"""
Particle Filter for Pedestrian Dead Reckoning
==============================================

Implements a particle filter for position estimation using:
- Multiple particles representing possible positions
- Floor plan constraints
- Resampling based on likelihood
"""

import numpy as np


class ParticleFilter:
    """
    Particle Filter for 2D position tracking with floor plan constraints
    """

    def __init__(self, floor_plan, n_particles=100, initial_x=2.0, initial_y=4.0):
        """
        Initialize particle filter

        Args:
            floor_plan: FloorPlanPDF object
            n_particles: Number of particles
            initial_x: Initial x position (meters)
            initial_y: Initial y position (meters)
        """
        self.floor_plan = floor_plan
        self.n_particles = n_particles

        # Initialize particles around starting position
        self.particles = np.zeros((n_particles, 2))
        self.particles[:, 0] = initial_x + np.random.normal(0, 0.5, n_particles)
        self.particles[:, 1] = initial_y + np.random.normal(0, 0.5, n_particles)

        # Initialize weights (uniform)
        self.weights = np.ones(n_particles) / n_particles

        # Process noise parameters
        self.position_noise = 0.3  # meters
        self.heading_noise = 0.1  # radians

    def predict(self, stride_length, heading):
        """
        Prediction step: move particles based on motion model

        Args:
            stride_length: Length of stride in meters
            heading: Heading angle in radians
        """
        for i in range(self.n_particles):
            # Add noise to heading for each particle
            noisy_heading = heading + np.random.normal(0, self.heading_noise)

            # Calculate displacement (navigation convention: 0°=North)
            dx = stride_length * np.sin(noisy_heading)
            dy = stride_length * np.cos(noisy_heading)

            # Add position noise
            dx += np.random.normal(0, self.position_noise)
            dy += np.random.normal(0, self.position_noise)

            # Update particle position
            self.particles[i, 0] += dx
            self.particles[i, 1] += dy

    def update(self):
        """
        Update step: reweight particles based on floor plan likelihood
        """
        for i in range(self.n_particles):
            x, y = self.particles[i]

            # Get floor plan probability at this position
            p_fp = self.floor_plan.get_probability(x, y)

            # Update weight (likelihood of being in walkable area)
            self.weights[i] *= p_fp

        # Normalize weights
        weight_sum = np.sum(self.weights)
        if weight_sum > 0:
            self.weights /= weight_sum
        else:
            # If all weights are zero, reset to uniform
            self.weights = np.ones(self.n_particles) / self.n_particles

    def resample(self):
        """
        Resample particles based on weights (systematic resampling)
        """
        # Check effective sample size
        n_eff = 1.0 / np.sum(self.weights ** 2)

        # Only resample if effective sample size is low
        if n_eff < self.n_particles / 2:
            # Systematic resampling
            positions = (np.arange(self.n_particles) + np.random.random()) / self.n_particles
            cumsum = np.cumsum(self.weights)
            i, j = 0, 0
            new_particles = np.zeros_like(self.particles)

            while i < self.n_particles:
                if positions[i] < cumsum[j]:
                    new_particles[i] = self.particles[j]
                    i += 1
                else:
                    j += 1

            self.particles = new_particles
            self.weights = np.ones(self.n_particles) / self.n_particles

    def get_position(self):
        """
        Get current position estimate (weighted mean)

        Returns:
            (x, y) tuple in meters
        """
        x = np.sum(self.weights * self.particles[:, 0])
        y = np.sum(self.weights * self.particles[:, 1])
        return (x, y)

    def get_particles(self):
        """
        Get all particles and weights

        Returns:
            (particles, weights) tuple
        """
        return self.particles.copy(), self.weights.copy()

    def update_stride(self, stride_length, heading):
        """
        Process one stride update

        Args:
            stride_length: Length of stride in meters
            heading: Heading angle in radians
        """
        self.predict(stride_length, heading)
        self.update()
        self.resample()


if __name__ == '__main__':
    """Test particle filter with simulated walk"""
    from bayesian_filter import FloorPlanPDF

    print("=" * 50)
    print("Testing Particle Filter")
    print("=" * 50)

    # Create floor plan
    floor_plan = FloorPlanPDF(width_m=10.0, height_m=10.0, resolution=0.1)

    # Create particle filter
    pf = ParticleFilter(floor_plan, n_particles=200, initial_x=2.0, initial_y=4.0)

    print(f"\nInitial position: {pf.get_position()}")

    # Simulate walking straight in +x direction
    stride_length = 0.7
    heading = 0.0  # East

    print("\nSimulating 10 strides...")
    for i in range(10):
        # Add some noise to heading
        noisy_heading = heading + np.random.normal(0, 0.05)

        # Update filter
        pf.update_stride(stride_length, noisy_heading)

        pos = pf.get_position()
        print(f"Step {i+1}: Position = ({pos[0]:.2f}, {pos[1]:.2f})")

    print("\n" + "=" * 50)
    print("✓ Particle filter test complete!")
    print("=" * 50)
