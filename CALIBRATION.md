# IMU Calibration System

## Problem Solved

**Issue**: The SenseHat IMU returns **absolute magnetic compass heading**, not relative to a starting position.

Example:
- You face North and start the app
- Your location has North at magnetic bearing **130°**
- IMU reads: `yaw = 130°`
- Code expects: `yaw = 0°` (North)
- **Result**: Wrong direction calculations!

## Solution: Automatic Calibration

The system now **automatically calibrates** when you press "START WALKING":

### How It Works

1. **Before calibration** (app just opened):
   - IMU reads absolute compass: `yaw_absolute = 130°`
   - System shows: "Not calibrated"

2. **Press "START WALKING"**:
   - System captures: `initial_yaw_reference = 130°`
   - This becomes your **0° reference** (North)

3. **After calibration**:
   - IMU reads: `yaw_absolute = 220°`
   - System calculates: `yaw_relative = 220° - 130° = 90°`
   - Display shows: `yaw = 90°` (East, turned right 90°)
   - ✅ **CORRECT!**

### Usage

```
1. Hold Pi facing desired "North" direction
2. Click "START WALKING"
3. System calibrates automatically
4. Walk and turn - yaw shows RELATIVE heading
```

### What You'll See

**Alert on Start:**
```
✓ CALIBRATED!
Absolute yaw: 130.0°
Your current direction is now 0° (North)

HOW TO USE:
📱 Point Pi in the direction you want to walk
🔘 Press MIDDLE button to count each stride

Yaw display shows RELATIVE heading (0° = starting direction)
```

**During Walking:**
```
[IMU] Absolute yaw=130.0°, Relative yaw=0.0° → Walking North
[IMU] Absolute yaw=220.0°, Relative yaw=90.0° → Walking East
[IMU] Absolute yaw=40.0°, Relative yaw=-90.0° → Walking West
```

### Reset

Click **"Reset Tracking"** to:
- Clear calibration (`initial_yaw_reference = None`)
- Reset all positions
- Ready to recalibrate on next "START WALKING"

### Implementation

**Files Modified:**
- `src/web_dashboard_advanced.py`:
  - Added `initial_yaw_reference` global variable
  - Modified `start_joystick_walk()` to capture initial yaw
  - Modified `determine_walking_direction_from_imu()` to use relative yaw
  - Modified `record_stride()` to use relative yaw
  - Modified `process_stride_all_algorithms()` to display relative yaw
  - Modified `reset()` to clear calibration

- `templates/tracking.html`:
  - Updated alert message to show calibration info

### Example Scenario

**Your setup:**
- Location: Room where magnetic North = 130°
- You face North and place Pi

**Without calibration (OLD - BROKEN):**
```
yaw = 130° → sin(130°) = 0.77, cos(130°) = -0.64
Moves: +0.77X (East), -0.64Y (South) ✗ WRONG!
Should move: 0X, +1Y (North)
```

**With calibration (NEW - FIXED):**
```
yaw_absolute = 130°
yaw_relative = 130° - 130° = 0°
sin(0°) = 0, cos(0°) = 1
Moves: 0X, +1Y (North) ✓ CORRECT!
```

---

**Status**: ✅ Implemented and working
**Date**: 2026-01-07
