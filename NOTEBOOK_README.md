# Part 2 Analysis Notebook

## Overview

The **part2_bayesian_navigation_analysis.ipynb** notebook provides a comprehensive analysis of the pedestrian inertial navigation system, focusing on the non-recursive Bayesian filter implementation based on Koroglu & Yilmaz (2017).

## Contents

### 1. Mathematical Foundation (Section 1)
- **Equation 5 breakdown**: Detailed explanation of all five probability components
- **Log-space computation**: Numerical stability techniques
- **Mode-seeking optimization**: L-BFGS-B implementation details
- **Path collision detection**: Wall avoidance mechanism

### 2. System Parameters (Section 2)
- **Floor plan configuration**: 3.5m × 6.0m room with 0.3m walls
- **Bayesian filter parameters**: σ_stride, σ_heading, floor plan weight
- **Kalman filter parameters**: State vector, process/measurement noise
- **Particle filter parameters**: Number of particles, resampling threshold
- **Critical parameter analysis**: Floor plan weight impact

### 3. Architecture Analysis (Section 3)

Three categorization dimensions:

#### 3.1 Information Processing Pattern
- **Naive**: Open-loop dead reckoning
- **Kalman**: Closed-loop recursive
- **Bayesian**: Non-recursive mode-seeking
- **Particle**: Sequential Monte Carlo

#### 3.2 Constraint Handling
- **Naive/Kalman**: No constraints (walks through walls)
- **Bayesian**: Hard constraints (deterministic avoidance)
- **Particle**: Soft constraints (probabilistic avoidance)

#### 3.3 Uncertainty Representation
- **Naive**: None
- **Kalman**: Unimodal Gaussian
- **Bayesian**: Full posterior (implicit)
- **Particle**: Discrete samples

### 4. Implementation Verification (Section 4)
- **Equation 5 component evaluation**: Verify all probability terms
- **Wall vs walkable comparison**: Energy barrier calculation
- **Path collision detection test**: Wall crossing prevention

### 5. Error Propagation Experiments (Section 5)

Three comprehensive experiments:

#### 5.1 Heading Error Impact
- Test 0° to 30° heading errors
- 10 strides × 0.7m each
- Compare all 4 algorithms
- **Result**: Bayesian most robust, Naive/Kalman degrade linearly

#### 5.2 Stride Length Error Impact
- Test 0cm to 30cm stride errors
- True stride: 0.7m
- **Result**: All filters similarly affected (direct measurement error)

#### 5.3 Wall Constraint Effectiveness
- Walk into west wall (5 steps)
- **Results**:
  - Bayesian: 100% effective (stops at wall)
  - Particle: ~95% effective (mostly stops)
  - Naive/Kalman: 0% effective (walk through)

### 6. Filter Comparison (Section 6)
- **Performance metrics table**: Accuracy, robustness, computational cost
- **Use case recommendations**: When to use each filter
- **Key findings**: Floor plan weight critical, binary walls necessary

### 7. Conclusions (Section 7)
- Implementation summary
- Experimental findings
- Critical parameters
- Limitations and future work

## How to Use

### Prerequisites
```bash
pip3 install numpy scipy matplotlib pandas jupyter --break-system-packages
```

### Run the Notebook
```bash
cd /Users/mirac/Desktop/master_sse_25_26-main/dataFusion
jupyter notebook part2_bayesian_navigation_analysis.ipynb
```

Or use VS Code with Jupyter extension.

### Execute All Cells
1. Open the notebook
2. Click "Run All" or execute cells sequentially
3. Visualizations will be generated inline

### Generated Outputs

The notebook generates the following images:
- `analysis_floor_plan.png` - Floor plan visualization with cross-section
- `analysis_architectures.png` - Information flow diagrams for all 4 filters
- `analysis_heading_error.png` - Heading error sensitivity plot
- `analysis_stride_error.png` - Stride length error sensitivity plot
- `analysis_wall_test.png` - Wall avoidance trajectory comparison

## Key Findings

### 1. Floor Plan Weight is Critical
```
Wall penalty = w_fp × log(0.01) = 1000 × (-4.6) = -4600
```
This creates an impenetrable energy barrier at walls.

### 2. Binary Walls are Necessary
- No gradient zones (removed Gaussian smoothing)
- Clean 0.01 (wall) vs 1.0 (walkable) boundaries
- Deterministic constraint enforcement

### 3. Path Collision Detection Works
- Samples 10 points along trajectory
- Detects wall crossing before optimization
- Starts optimizer from safe position

### 4. Non-Recursive Advantage
- Re-computes full posterior each step
- Incorporates static constraints globally
- Avoids recursive error accumulation

## Mathematical Highlights

### Equation 5 (Koroglu & Yilmaz, 2017)
```
p(x_k | Z_k) ∝ p(x_k|FP) × p(x_k|d_k, x_{k-1}) × p(z_k|x_k) ×
               p(x_k|x_{k-1},...,x_{k-n}) × p(x_{k-1}|Z_{k-1})
```

Where:
- `p(x_k|FP)`: Floor plan PDF (binary grid)
- `p(x_k|d_k, x_{k-1})`: Stride circle (Gaussian at radius d_k)
- `p(z_k|x_k)`: IMU heading likelihood
- `p(x_k|x_{k-1},...,x_{k-n})`: Motion model (uniform)
- `p(x_{k-1}|Z_{k-1})`: Previous posterior (weak Gaussian)

## Performance Summary

| Algorithm | Wall Avoidance | Heading Robustness | Computation | Real-time |
|-----------|---------------|-------------------|-------------|-----------|
| Naive     | ✗ No          | ★☆☆☆☆             | Very Low    | ✓ Yes     |
| Kalman    | ✗ No          | ★★☆☆☆             | Low         | ✓ Yes     |
| Bayesian  | ✓ Yes (Hard)  | ★★★★☆             | High        | ⚠ Marginal |
| Particle  | ⚠ Mostly      | ★★★☆☆             | Medium      | ✓ Yes     |

## References

1. Koroglu, M. T., & Yilmaz, A. (2017). Pedestrian inertial navigation with building floor plans for indoor environments via non-recursive Bayesian filtering. *Proc. ION GNSS+*.

2. Thrun, S., Burgard, W., & Fox, D. (2005). *Probabilistic Robotics*. MIT Press.

3. Foxlin, E. (2005). Pedestrian tracking with shoe-mounted inertial sensors. *IEEE Computer Graphics and Applications*, 25(6), 38-46.

## Troubleshooting

### Import Error
If you get `ModuleNotFoundError: No module named 'bayesian_filter'`:
```python
import sys
sys.path.append('src')
```

### Visualization Not Showing
If plots don't appear:
```python
%matplotlib inline  # Add to first cell
```

### Scipy Import Error
```bash
pip3 install scipy --break-system-packages
```

## Assignment Deliverable

This notebook fulfills the **Part 2 (75%)** analysis requirement:
- ✅ Mathematical equations explained
- ✅ Parameter values documented
- ✅ Architecture analysis (3 categorizations)
- ✅ Error propagation experiments
- ✅ Implementation verification
- ✅ Filter comparison with metrics
- ✅ Visualizations and plots

---

**For questions or issues, refer to SETUP_PI.md or contact course staff.**
