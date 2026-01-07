# Changes Log - 2026-01-07

## Critical Bug Fixes

### 1. ✅ Bayesian Filter Initialization Bug Fixed (CRITICAL - USER REPORTED)
**Issue**: Bayesian filter's internal state was hardcoded to (2.0, 4.0) instead of using the correct starting position (1.75, 3.0). This caused massive trajectory errors from the very first stride when users started walking without clicking "Reset Tracking" first.

**Example Problem:**
- External `positions['bayesian']` initialized to `(1.75, 3.0)` ✓
- Internal `bayesian_filter.current_estimate` hardcoded to `(2.0, 4.0)` ✗
- First stride: Bayesian moved from wrong starting point, caused 1+ meter error
- Error compounded with each stride, reaching 12+ meters by stride #21

**Root Cause:**
- `bayesian_filter.py:175` hardcoded: `self.current_estimate = {'x': 2.0, 'y': 4.0}`
- `web_dashboard_advanced.py:121` created filter without initial position parameter
- Kalman and Particle filters received `initial_x` and `initial_y`, but Bayesian didn't

**Fix**: Added `initial_x` and `initial_y` parameters to `BayesianNavigationFilter.__init__()`
```python
def __init__(self, floor_plan, stride_length=0.7, n_history=3, initial_x=1.75, initial_y=3.0):
    # ...
    self.current_estimate = {'x': initial_x, 'y': initial_y}  # Now uses parameters!
```

**Files Modified:**
- `src/bayesian_filter.py`:
  - Added `initial_x` and `initial_y` parameters to `__init__()` (line 158)
  - Changed `current_estimate` to use parameters instead of hardcoded values (line 177)
- `src/web_dashboard_advanced.py`:
  - Updated global filter initialization to pass `initial_x=1.75, initial_y=3.0` (line 121)
  - Updated set_start_position endpoint to pass initial position (line 709)
- `mqtt/mqtt_location_publisher.py`:
  - Updated filter initialization to pass `initial_x=1.75, initial_y=3.0` (lines 67-68)
  - Updated naive_position to match Bayesian start position (line 73)
- `test_filter_debug.py`:
  - Updated to use new API with `initial_x` and `initial_y` parameters (line 21)

**Impact**: Bayesian filter now starts at correct position, matches other filters from stride #1

---

### 2. ✅ IMU Calibration System Added (CRITICAL - USER REPORTED)
**Issue**: IMU returns absolute magnetic compass heading (e.g., 130° for North), but code expected 0° for starting direction. This caused completely wrong trajectory - user would face North but system thought they were facing Southeast!

**Example Problem:**
- User faces North in a room where magnetic North = 130°
- IMU reads: `yaw = 130°`
- Without calibration: `sin(130°) = 0.77`, `cos(130°) = -0.64`
- Movement: +0.77X, -0.64Y (Southeast) ✗ **COMPLETELY WRONG!**
- Expected: 0X, +1Y (North)

**Fix**: Automatic calibration on "START WALKING"
- Captures initial yaw as reference: `initial_yaw_reference = 130°`
- Calculates relative yaw: `yaw_relative = current_yaw - initial_yaw_reference`
- Now: `yaw_relative = 130° - 130° = 0°` → Moves North correctly ✓

**Files Modified:**
- `src/web_dashboard_advanced.py`:
  - Added `initial_yaw_reference` global variable (line 104)
  - Modified `start_joystick_walk()` to capture initial yaw (lines 868-873)
  - Modified `determine_walking_direction_from_imu()` to use relative yaw (lines 196-205)
  - Modified `record_stride()` API endpoint to use relative yaw (lines 489-500)
  - Modified `process_stride_all_algorithms()` to display relative yaw (lines 247-265)
  - Modified `reset()` to clear calibration (line 791)

- `templates/tracking.html`:
  - Updated start alert to show calibration info (lines 937-952)

**Verification**: See [CALIBRATION.md](CALIBRATION.md) for full details and test results

---

### 3. ✅ Coordinate System Fixed (CRITICAL)
**Issue**: Code used math convention (0°=East), but paper and real IMU use navigation convention (0°=North)

**Changed from:**
```python
x = stride_length * cos(heading)  # WRONG for IMU
y = stride_length * sin(heading)
```

**Changed to:**
```python
x = stride_length * sin(heading)  # CORRECT for IMU (0°=North)
y = stride_length * cos(heading)
```

**Files Modified:**
- `src/bayesian_filter.py` (lines 224, 344)
- `src/particle_filter.py` (line 57)
- `src/web_dashboard_advanced.py` (lines 239, 269, 479, 740)
- `src/web_dashboard_advanced.py` (lines 308-355: LED arrows)
- `mqtt/mqtt_location_publisher.py` (line 225)

**Impact**: System now works correctly with real Raspberry Pi SenseHat

---

### 4. ✅ Particle Filter API Endpoint Fixed
**Issue**: Line 594-607 had TODO placeholder using naive dead reckoning

**Fix**: Replaced with actual particle filter call:
```python
particle_filter.update_stride(STRIDE_LENGTH, yaw)
particle_pos = particle_filter.get_position()
```

**File**: `src/web_dashboard_advanced.py:594-607`

---

### 5. ✅ MQTT Floor Plan Dimensions Fixed
**Issue**: Used wrong dimensions (20.0m × 10.0m instead of 3.5m × 6.0m)

**Fix**: Changed to correct dimensions
```python
FloorPlanPDF(width_m=3.5, height_m=6.0, resolution=0.1)
```

**File**: `mqtt/mqtt_location_publisher.py:63`

---

## Code Cleanup

### 6. ✅ Removed Unused API Endpoints
**Removed:**
- `/api/sensors/raw` (~33 lines)
- `/api/sensors/filtered` (~30 lines)
- `/api/sensors/comparison` (~8 lines)
- `/api/errors` (~21 lines)
- `sensor_buffer` data structure

**File**: `src/web_dashboard_advanced.py`

---

### 7. ✅ Removed Dead Code
**Removed:**
- `imuDirection` element reference (non-existent element)

**File**: `templates/tracking.html:1038`

---

### 8. ✅ Cleaned Cache and Old Files
**Removed:**
- `src/__pycache__/` (old bytecode with wrong convention)
- `dashboard.log` (old logs)
- `wall_detection_test.png` (old test image)
- `floor_plan_3.5x6.0_visualization.png` (old visualization)

---

## New Features

### 9. ✅ Stride Length Control Added
**Added UI input** to customize stride length (0.3m - 1.5m)

**Files:**
- `templates/tracking.html` (lines 216-234: UI)
- `src/web_dashboard_advanced.py` (lines 649-690: API endpoint)

---

## Verification Tests Passed

```
✓ Bayesian Filter: heading=0° (North) → Δy=+1.00
✓ Particle Filter: heading=0° (North) → Δy=+1.00
✓ LED Arrows: 0°=North (UP), 90°=East (RIGHT), etc.
```

---

## Debug Tools Added

### 10. ✅ Comprehensive Filter Debug Logging
**Added detailed logging system** to diagnose filter behavior differences

**Logs for each stride:**
- Input heading (absolute, relative, calibration info)
- Naive filter calculations
- **Bayesian filter internal debug:**
  - IMU prediction calculation
  - Wall detection status
  - Optimization process (iterations, convergence)
  - Actual vs expected displacement
  - Floor plan probability
- Kalman filter measurements and updates
- Particle filter position estimates
- Side-by-side position comparison
- Deviation analysis from naive baseline

**Features:**
- **Absolute file path**: `/home/pi/dataFusion/filters_debug.log` (always in project root)
- **Console output**: Shows `[DEBUG] Stride #X logged to: <path>` for each stride
- **Startup message**: Displays full log file path when dashboard starts
- **Error visibility**: Prints errors to console if log file can't be created

**Files:**
- `src/web_dashboard_advanced.py` (process_stride_all_algorithms: lines 241-396)
- `src/bayesian_filter.py` (update method: lines 329-438)
- `filters_debug.log` (output file, auto-cleared on reset)
- `test_filter_debug.py` (test script)
- `FILTER_DEBUG_GUIDE.md` (full usage documentation)
- `DEBUG_QUICK_START.md` (quick reference for Pi)

**Usage:**
```bash
# On Raspberry Pi - you'll see console output confirming logging
python3 src/web_dashboard_advanced.py
# Output shows: 📝 DEBUG LOG ENABLED
#                Location: /home/pi/dataFusion/filters_debug.log

# View log after walking
cat /home/pi/dataFusion/filters_debug.log

# Test locally
python3 test_filter_debug.py
```

---

## Documentation Added

- `COORDINATE_SYSTEM.md` - Reference for navigation convention
- `CALIBRATION.md` - IMU calibration system documentation
- `FILTER_DEBUG_GUIDE.md` - How to use filter debug logging
- `CHANGES.md` - This file

---

**Status**: ✅ All critical bugs fixed, code cleaned, debug tools added
