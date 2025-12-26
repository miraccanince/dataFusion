# Bayesian Filter Implementation

## Overview

This implements the **non-recursive Bayesian filter** from the research paper:

> **"Pedestrian inertial navigation with building floor plans for indoor environments via non-recursive Bayesian filtering"**
> M. T. Koroglu and A. Yilmaz, IEEE SENSORS (2017)

The algorithm uses **floor plan constraints** to correct heading errors from the IMU, achieving better accuracy than naive dead reckoning without the computational cost of particle filters.

---

## Mathematical Foundation

### Core Equation (Equation 5 from paper)

```
p(xₖ|Zₖ) ∝ p(xₖ|FP) × p(xₖ|dₖ, xₖ₋₁) × p(zₖ|xₖ) × p(xₖ|xₖ₋₁,...,xₖ₋ₙ) × p(xₖ₋₁|Zₖ₋₁)
```

Where:
- **xₖ**: Position at time k (x, y coordinates)
- **Zₖ**: All measurements up to time k
- **FP**: Floor plan
- **dₖ**: Stride length (accurate from ZUPT)
- **n**: Number of previous positions in motion model

### The Five Probability Distributions

#### 1. **p(xₖ|FP)** - Static Floor Plan PDF

Pre-computed probability grid of your building.

- **High probability**: Hallways, walkable areas
- **Low probability**: Walls, obstacles
- **Stays constant**: Computed once, reused (efficient!)

**Implementation:**
```python
class FloorPlanPDF:
    def __init__(self, width_m, height_m, resolution=0.1):
        # Creates grid: 0.1m resolution
        # walkable areas = 1.0
        # walls = 0.01 (Gaussian smoothed)
```

**Current floor plan**: 20m × 10m L-shaped hallway

#### 2. **p(xₖ|dₖ, xₖ₋₁)** - Stride Length Circle

Circular Gaussian centered at previous position with radius = stride_length.

**Why it works**: ZUPT gives **accurate** stride lengths (even though heading is wrong!)

**Mathematical form:**
```
distance = √[(x - x_{k-1})² + (y - y_{k-1})²]
p(xₖ|dₖ, xₖ₋₁) = (1 / (σ_stride × √(2π))) × exp(-0.5 × ((distance - dₖ) / σ_stride)²)
```

**Parameters:**
- `σ_stride = 0.1m` (stride uncertainty)

#### 3. **p(zₖ|xₖ)** - Sensor Likelihood (Equation 4)

IMU prediction using unreliable heading.

**Equation 4 from paper:**
```
zₖ = x̂_{k-1} + dₖ × [sin(ψ̂_{k-1} + δψₖ)]
                    [cos(ψ̂_{k-1} + δψₖ)]
```

Where:
- ψ̂: Heading estimate
- δψₖ: Heading change (unreliable!)

**Implementation:**
```python
z_x = x_prev + stride_length × sin(heading)
z_y = y_prev + stride_length × cos(heading)
p(zₖ|xₖ) = Gaussian(mean=[z_x, z_y], σ=0.5)
```

#### 4. **p(xₖ|xₖ₋₁,...,xₖ₋ₙ)** - Extended Motion Model

Predicts next position using previous trajectory.

- **Straight segments**: Linear extrapolation
- **Corners**: Curved prediction

**Implementation:**
```python
# Use last n=3 positions
velocity = last_position - prev_position
predicted = last_position + velocity
p(xₖ|history) = Gaussian(mean=predicted, σ=0.3)
```

#### 5. **p(xₖ₋₁|Zₖ₋₁)** - Previous Posterior

Keeps estimate near previous result.

```python
p(xₖ₋₁|Zₖ₋₁) = Gaussian(mean=previous_estimate, Σ=0.3×I)
```

---

## Mode-Seeking (MAP Estimation)

Since the posterior is **non-parametric** (no closed-form solution), we use **mode-seeking** to find the maximum.

**Algorithm**: scipy.optimize.minimize with L-BFGS-B

```python
def posterior_probability(pos):
    # Multiply all 5 PDFs (use log for stability)
    log_p = (log(p(xₖ|FP)) +
             log(p(xₖ|dₖ, xₖ₋₁)) +
             log(p(zₖ|xₖ)) +
             log(p(xₖ|history)) +
             log(p(xₖ₋₁|Zₖ₋₁)))
    return log_p

# Find maximum (mode of posterior)
result = minimize(-posterior_probability, initial_guess, bounds=floor_plan_bounds)
estimated_position = result.x
```

**Why it's efficient**:
- Floor plan PDF is pre-computed (no runtime cost)
- Only optimizes over 2D position space
- Much faster than particle filters (100-1000 particles)

---

## File Structure

```
dataFusion/
├── bayesian_filter.py              # Core implementation
│   ├── FloorPlanPDF               # Floor plan probability grid
│   └── BayesianNavigationFilter   # Main filter class
│
└── web_dashboard_advanced.py       # Web interface
    └── /api/stride/bayesian        # REST endpoint
```

---

## Usage

### 1. Standalone Testing

```python
from bayesian_filter import BayesianNavigationFilter, FloorPlanPDF

# Create floor plan
floor_plan = FloorPlanPDF(width_m=20, height_m=10, resolution=0.1)

# Initialize filter
bf = BayesianNavigationFilter(floor_plan, stride_length=0.7)

# Update with IMU measurements
heading = 0.0  # radians (from IMU)
stride = 0.7   # meters (from ZUPT)

estimated_pos = bf.update(heading=heading, stride_length=stride)
print(f"Position: ({estimated_pos['x']:.2f}, {estimated_pos['y']:.2f})")
```

### 2. Web Dashboard

```bash
# On Raspberry Pi
python3 web_dashboard_advanced.py

# Access from browser
http://10.111.224.71:5001
```

**Steps:**
1. Click "Record Stride (Bayesian)" button
2. Walk one stride
3. Bayesian filter corrects position using floor plan
4. Compare trajectory with naive algorithm

---

## Tunable Parameters

### Filter Parameters

Located in `bayesian_filter.py`:

```python
class BayesianNavigationFilter:
    def __init__(self):
        self.sigma_stride = 0.1    # Stride uncertainty (m)
        self.sigma_heading = 0.5   # Heading uncertainty (rad)
        self.sigma_motion = 0.3    # Motion model uncertainty (m)
        self.n_history = 3         # Positions in motion model
```

**Tuning guide:**
- **↑ sigma_stride**: More tolerance for variable stride lengths
- **↑ sigma_heading**: Trust IMU heading less, floor plan more
- **↑ sigma_motion**: Allow more curved paths
- **↑ n_history**: Use longer trajectory history (smoother but slower to turn)

### Floor Plan Parameters

```python
floor_plan = FloorPlanPDF(
    width_m=20.0,      # Floor plan width
    height_m=10.0,     # Floor plan height
    resolution=0.1     # Grid cell size (10cm)
)
```

**Resolution trade-off:**
- **Finer** (0.05m): More accurate but larger memory
- **Coarser** (0.2m): Faster but less detailed

---

## Customizing the Floor Plan

### Option 1: Define Custom Hallways (Programmatic)

Edit `_create_simple_floor_plan()` in `bayesian_filter.py`:

```python
def _create_simple_floor_plan(self):
    grid = np.zeros((self.grid_height, self.grid_width))

    # Define your hallways
    # Hallway 1: from (x1,y1) to (x2,y2), width w
    x1, x2 = int(1.0/self.resolution), int(10.0/self.resolution)
    y1, y2 = int(2.0/self.resolution), int(4.0/self.resolution)
    grid[y1:y2, x1:x2] = 1.0  # Walkable

    # Apply smoothing
    from scipy.ndimage import gaussian_filter
    grid = gaussian_filter(grid, sigma=2.0)

    return grid
```

### Option 2: Load Image File

```python
from PIL import Image

def _create_from_image(self, image_path):
    img = Image.open(image_path).convert('L')  # Grayscale
    grid = np.array(img) / 255.0  # Normalize to [0, 1]

    # Black pixels = walls (0)
    # White pixels = walkable (1)

    return grid
```

### Option 3: Draw with Coordinates

```python
def add_room(self, x_start, y_start, width, height):
    """Add rectangular room to floor plan"""
    x1 = int(x_start / self.resolution)
    x2 = int((x_start + width) / self.resolution)
    y1 = int(y_start / self.resolution)
    y2 = int((y_start + height) / self.resolution)

    self.grid[y1:y2, x1:x2] = 1.0
```

---

## Comparison with Other Algorithms

### Naive Dead Reckoning
```
Position = Previous + Stride × [sin(heading), cos(heading)]
```

**Problems:**
- Heading drift accumulates
- No correction mechanism
- Position error grows unbounded

### Bayesian Filter (This Implementation)
```
Position = argmax[p(xₖ|FP) × p(xₖ|dₖ) × p(zₖ|xₖ) × ...]
```

**Advantages:**
- ✓ Floor plan constrains position to walkable areas
- ✓ Corrects heading errors automatically
- ✓ More accurate than naive
- ✓ Computationally efficient (vs particle filter)

**Trade-offs:**
- Requires pre-defined floor plan
- Mode-seeking can get stuck in local maxima
- Assumes Gaussian uncertainties

### Particle Filter (TODO)
```
Position = weighted average of N particles
```

**Advantages:**
- Most accurate (non-parametric)
- Handles multi-modal distributions

**Disadvantages:**
- Requires 100-1000 particles
- Too slow for Raspberry Pi (8MHz)

---

## Expected Performance

Based on paper results:

| Algorithm | Position Error | Computation Time |
|-----------|---------------|------------------|
| Naive DR  | 5-10% of distance | < 1ms |
| Bayesian  | < 1% of distance  | 10-50ms |
| Particle  | < 0.5% of distance | 200-500ms |

**On 20m trajectory:**
- Naive: ~2m error
- Bayesian: ~0.2m error (10× better!)

---

## Troubleshooting

### Issue: Filter estimates don't move

**Cause**: Floor plan PDF dominates (too strong constraint)

**Solution**: Reduce floor plan influence
```python
# In posterior_probability()
log_posterior = (0.5 * log(p_fp) +  # Reduce weight
                 log(p_stride) + ...)
```

### Issue: Estimates jump around

**Cause**: Optimization finds different local maxima

**Solution 1**: Increase previous posterior weight
```python
self.current_covariance = np.eye(2) * 0.1  # Tighter (was 0.3)
```

**Solution 2**: Use better initial guess
```python
# In update()
x0 = [self.current_estimate['x'] + ...,  # Start from previous
      self.current_estimate['y'] + ...]
```

### Issue: Too slow on Raspberry Pi

**Solution 1**: Reduce floor plan resolution
```python
floor_plan = FloorPlanPDF(resolution=0.2)  # Coarser grid
```

**Solution 2**: Reduce optimization iterations
```python
minimize(..., options={'maxiter': 10})  # Limit iterations
```

---

## Implementation Checklist for Assignment

Based on DFA_assignment.pdf requirements:

### Part 2: IMU Assignment (75% of grade)

- [x] **Reproduce Section II.C algorithm** from paper
  - [x] Equation 5 implemented (`posterior_probability()`)
  - [x] Floor plan PDF created
  - [x] Mode-seeking with scipy.optimize

- [x] **Linear Kalman filter** for sensor data
  - [x] 1D Kalman for yaw angle (already in dashboard)

- [ ] **Particle filter implementation** (TODO)
  - [ ] Compare with Bayesian filter

- [ ] **Jupyter notebook with**:
  - [ ] Visualization of trajectories
  - [ ] Mathematical equations shown
  - [ ] Parameter table
  - [ ] Error analysis
  - [ ] Discussion of priors/likelihoods impact

### What to Add to Jupyter Notebook

```python
# 1. Load trajectory data
bayesian_traj = pd.read_csv('bayesian_trajectory.csv')
naive_traj = pd.read_csv('naive_trajectory.csv')

# 2. Plot comparison
plt.plot(naive_traj['x'], naive_traj['y'], label='Naive')
plt.plot(bayesian_traj['x'], bayesian_traj['y'], label='Bayesian')
plt.plot(ground_truth['x'], ground_truth['y'], 'k--', label='Ground Truth')

# 3. Error analysis
errors = calculate_errors(bayesian_traj, ground_truth)
print(f"Mean error: {errors.mean():.3f}m")

# 4. Show equations (Markdown)
# Display Equation 5, parameter values, etc.
```

---

## References

1. **Main Paper**: Koroglu & Yilmaz (2017) - Pedestrian inertial navigation with building floor plans
2. **Mode-Seeking**: scipy.optimize.minimize documentation
3. **Bayesian Inference**: D.S. Sivia - Data Analysis: A Bayesian Tutorial (2006)
4. **Floor Plan Matching**: Krach & Robertson (2008) - Integration of foot-mounted inertial sensors

---

## Next Steps

1. **Test on real floor plan**: Replace L-shaped hallway with your building layout
2. **Implement particle filter**: For comparison (assignment requirement)
3. **Create Jupyter analysis**: Show results, equations, error analysis
4. **Optimize parameters**: Tune sigmas for your specific IMU
5. **Add MQTT streaming**: Part 1 of assignment (15% grade)

---

## Questions?

**Common improvements**:
- Multi-floor support (add floor number to state)
- Automatic floor plan extraction from image
- Adaptive parameter tuning
- WiFi fingerprinting integration

**Contact**: Check your assignment instructions for office hours/email
