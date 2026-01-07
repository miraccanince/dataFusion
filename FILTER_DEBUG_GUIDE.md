# Filter Debug Logging Guide

## Overview

The system now includes comprehensive debug logging to help diagnose why filters behave differently. The debug log captures detailed information about what each filter receives, how it processes the data, and its output.

## Debug Log Location

**File**: `filters_debug.log` (in the project root directory)

**Absolute Path**: The log file is created using an absolute path, so it will always be in:
```
/home/pi/dataFusion/filters_debug.log  (on Raspberry Pi)
```
or
```
/Users/your-username/path/to/dataFusion/filters_debug.log  (on your laptop)
```

**Console Output**: Every time a stride is logged, you'll see a console message:
```
[DEBUG] Stride #1 logged to: /home/pi/dataFusion/filters_debug.log
```

This confirms the log file is being created and written to successfully.

## What Gets Logged

### For Each Stride:

#### 1. **Input Data**
- Absolute yaw from IMU (before calibration)
- Initial yaw reference (calibration offset)
- Relative yaw (after calibration)
- Stride length
- Coordinate system verification

**Example:**
```
[INPUT HEADING]
  Absolute yaw: 130.00° (2.2689 rad)
  Initial reference: 130.00°
  Relative yaw (used): 0.00° (0.0000 rad) [CALIBRATED]
  Stride length: 0.70m
  Coordinate system: Navigation (0°=North, x=sin, y=cos)
```

#### 2. **Naive Filter**
- Previous position
- Calculation details (x += stride * sin(heading), y += stride * cos(heading))
- New position

**Example:**
```
[1. NAIVE FILTER]
  Previous position: (1.750, 3.000)
  Calculation: x += 0.70 * sin(0.00°) = 0.0000
  Calculation: y += 0.70 * cos(0.00°) = 0.7000
  New position: (1.750, 3.700)
```

#### 3. **Bayesian Filter (DETAILED)**
- Previous estimate
- IMU prediction calculation (expected position before optimization)
- Wall detection (if path crosses a wall)
- Initial guess for optimization (IMU prediction or safe position)
- Optimization process:
  - Success status
  - Number of iterations
  - Optimized position
  - Negative posterior value
- Displacement analysis:
  - Actual displacement (Δx, Δy, distance)
  - Expected displacement (stride length)
  - Difference between actual and expected
- Floor plan probability at result

**Example:**
```
[2. BAYESIAN FILTER]
  Previous position: (1.750, 3.000)
  Input heading: 0.00° (0.0000 rad)
  Input stride length: 0.70m
  === BAYESIAN FILTER INTERNAL DEBUG ===
  Previous estimate: (1.750, 3.000)
  IMU prediction: (1.750, 3.700)
    Calculation: x = 1.750 + 0.70 * sin(0.00°) = 1.750
    Calculation: y = 3.000 + 0.70 * cos(0.00°) = 3.700
  Initial guess: (1.750, 3.700) [IMU prediction - path clear]
  Running L-BFGS-B optimization...
  Optimization result:
    Success: True
    Iterations: 1
    Optimized position: (1.750, 3.697)
    Negative posterior: 1.720874
    Actual displacement: Δx=-0.000, Δy=0.697, distance=0.697m
    Expected displacement: 0.700m
    Difference: -0.003m
    Floor plan probability at result: 1.0000
  New position (after optimization): (1.750, 3.697)
  Displacement: Δx=0.000, Δy=0.697
```

#### 4. **Kalman Filter**
- Previous position
- Naive measurement (dead reckoning used as measurement input)
- New position after Kalman update

**Example:**
```
[3. KALMAN FILTER]
  Previous position: (1.750, 3.000)
  Measurement (naive): (1.750, 3.700)
  New position (after Kalman update): (1.750, 3.583)
```

#### 5. **Particle Filter**
- Previous position
- Input heading and stride length
- New position (weighted average of particles)

**Example:**
```
[4. PARTICLE FILTER]
  Previous position: (1.750, 3.000)
  Input heading: 0.00° (0.0000 rad)
  Input stride length: 0.70m
  New position (weighted average): (1.700, 3.716)
```

#### 6. **Position Comparison**
- Side-by-side comparison of all filter positions
- Deviation from naive filter (baseline)
  - Δx, Δy offsets
  - Euclidean distance from naive

**Example:**
```
[POSITION COMPARISON]
  Naive:    ( 1.750,  3.700)
  Bayesian: ( 1.750,  3.697)
  Kalman:   ( 1.750,  3.583)
  Particle: ( 1.700,  3.716)

[DEVIATION FROM NAIVE]
  Bayesian : Δx=+0.000, Δy=-0.003, distance=0.003m
  Kalman   : Δx=+0.000, Δy=-0.117, distance=0.117m
  Particle : Δx=-0.050, Δy=+0.016, distance=0.052m
```

## How to Use Debug Logging

### 1. Testing with Real Raspberry Pi

```bash
# SSH into your Raspberry Pi
ssh pi@10.49.216.71

# Navigate to project
cd dataFusion

# Start the dashboard (this will initialize the debug log)
python3 src/web_dashboard_advanced.py

# Access dashboard from your laptop: http://10.49.216.71:5001
# Click "START WALKING" and take strides
# The debug log will be populated in real-time

# After walking, view the debug log
cat filters_debug.log

# Or download it to your laptop
# (From your laptop terminal)
scp pi@10.49.216.71:~/dataFusion/filters_debug.log .
```

### 2. Testing with Mock Test

```bash
# In the web dashboard UI:
# 1. Click "Reset Tracking" to clear the log
# 2. Click "Run Mock Test" to generate test strides
# 3. View filters_debug.log file

cat filters_debug.log
```

### 3. Testing Locally

```bash
# Run the debug test script
python3 test_filter_debug.py

# View the generated log
cat filters_debug.log
```

## Analyzing Bayesian Filter Issues

When the Bayesian filter behaves differently from other filters, check:

### 1. **Is it receiving the same heading as other filters?**
Look at the `[INPUT HEADING]` section - all filters receive this same input.

### 2. **Is the IMU prediction correct?**
In the Bayesian internal debug, check:
```
IMU prediction: (x, y)
  Calculation: x = prev_x + stride * sin(heading)
  Calculation: y = prev_y + stride * cos(heading)
```
This should match the Naive filter's calculation.

### 3. **Is wall detection triggering unexpectedly?**
If you see:
```
Wall detected at (x, y) - probability: 0.xxx
Initial guess: (x, y) [SAFE - staying at current position]
```
The Bayesian filter detected a wall and stayed at the current position instead of moving.

### 4. **Is the optimizer converging correctly?**
Check:
```
Optimization result:
  Success: True/False
  Iterations: N
  Actual displacement: distance=X.XXXm
  Expected displacement: Y.YYYm
  Difference: Z.ZZZm
```
If the difference is large, the optimizer is correcting the position significantly.

### 5. **Is the floor plan probability low?**
```
Floor plan probability at result: 0.XXXX
```
Values < 1.0 indicate the filter is near walls or in constrained areas.

## Common Patterns

### Normal Behavior:
```
- Bayesian displacement ≈ expected displacement (within 0.01m)
- Floor plan probability = 1.0000 (in open space)
- Initial guess = IMU prediction (path clear)
- All filters show similar directions (not necessarily same positions)
```

### Wall Constraint Behavior:
```
- Wall detected message appears
- Initial guess = current position (SAFE mode)
- Bayesian displacement < expected (blocked by wall)
- Floor plan probability < 1.0
```

### Divergence Problem (Bug):
```
- Bayesian IMU prediction matches Naive calculation ✓
- But Bayesian goes in different direction than all others ✗
- Check if calibration is being applied inconsistently
- Check if heading units (rad vs deg) are mixed up
```

## Resetting the Debug Log

The debug log is automatically cleared when you:
1. Start the dashboard application (`python3 src/web_dashboard_advanced.py`)
2. Click "Reset Tracking" in the web UI

Manual reset:
```bash
rm filters_debug.log
```

## Example Analysis Session

```bash
# 1. Reset and start fresh
Click "Reset Tracking" in UI

# 2. Run mock test or walk with Pi
Click "Run Mock Test" or "START WALKING"

# 3. View the log
cat filters_debug.log | grep -A 20 "STRIDE #1"

# 4. Compare Bayesian vs Naive IMU predictions
cat filters_debug.log | grep "IMU prediction:"

# 5. Check for wall detections
cat filters_debug.log | grep "Wall detected"

# 6. See position comparisons
cat filters_debug.log | grep -A 5 "POSITION COMPARISON"
```

## Tips

1. **Start with a simple test**: Use the mock test to generate a square path. All filters should follow similar trajectories.

2. **Compare stride-by-stride**: Look at each stride individually to identify where divergence begins.

3. **Check calibration**: Verify that "Relative yaw (used)" is being calculated correctly from absolute yaw.

4. **Verify coordinate system**: All calculations should show `x = sin(heading), y = cos(heading)` for navigation convention.

5. **Monitor optimization**: If Bayesian shows many iterations or large displacement differences, it's fighting the floor plan constraints.

## Status

✅ Debug logging implemented
✅ Tested with mock strides
✅ Captures all filter inputs and outputs
✅ Shows Bayesian internal optimization process
✅ Automatic reset on tracking reset

---

**Created**: 2026-01-07
**Purpose**: Diagnose Bayesian filter divergence issue
