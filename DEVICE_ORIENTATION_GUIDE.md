# Device Orientation Guide - How to Use the Raspberry Pi for Pedestrian Tracking

## ⚠️ CRITICAL: Device Orientation Matters!

The SenseHat IMU (Inertial Measurement Unit) tracks the **actual physical orientation** of the Raspberry Pi. If you rotate the Pi, the system will detect that rotation and your trajectory will change direction.

## The Problem You're Experiencing

**What's happening:**
- You press the middle button for each stride
- Between button presses, you're accidentally rotating the Pi
- The IMU detects these rotations (126° → 52° → 77° → 288°)
- The system correctly calculates movement in those different directions
- Result: Chaotic, random-looking trajectory

**What you expect:**
- Walk in a straight line or controlled pattern
- Trajectory matches your intended path

**The mismatch:**
- The IMU tracks **device orientation**, not your "intended" direction
- You must keep the Pi oriented consistently!

## How to Hold the Raspberry Pi Correctly

### Step 1: Choose a "Forward Edge"

Pick one edge of the Raspberry Pi to be your "forward" direction:

```
Recommended: USB ports edge as "forward"

        ┌─────────────────┐
        │   SenseHat LED  │
        │     (facing up) │
        │                 │
        │    Raspberry    │
        │       Pi        │
        │                 │
 FORWARD│  [USB] [USB]    │ FORWARD
      →└─────────────────┘←

Keep this edge pointing where you want to walk!
```

### Step 2: Hold the Pi Level and Steady

**Correct holding method:**
```
✓ Hold the Pi flat (SenseHat LEDs facing UP)
✓ Keep the "forward edge" pointing in your walking direction
✓ DON'T let it rotate in your hands
✓ Keep it level (not tilted)
```

**Wrong holding method:**
```
✗ Letting the Pi rotate between strides
✗ Tilting the Pi at an angle
✗ Flipping the Pi over (LEDs facing down)
✗ Holding it vertically
```

### Step 3: Maintain Orientation While Walking

**When walking North:**
```
You:  👤 (facing North)
Pi:   Keep USB edge pointing North
      ↑
```

**When walking East:**
```
You:  👤 (facing East)
Pi:   Keep USB edge pointing East
      →
```

**When walking South:**
```
You:  👤 (facing South)
Pi:   Keep USB edge pointing South
      ↓
```

**When walking West:**
```
You:  👤 (facing West)
Pi:   Keep USB edge pointing West
      ←
```

## Testing Device Orientation

### Quick Test: Walking a Square

1. **Reset Tracking** in the web dashboard
2. **Click "START WALKING"**
3. **Face North** and orient the Pi with USB edge pointing North
4. **Walk 1 stride** forward (North), press middle button
5. **Turn right 90°** to face East, rotate Pi 90° right (USB edge now pointing East)
6. **Walk 1 stride** forward (East), press middle button
7. **Turn right 90°** to face South, rotate Pi 90° right (USB edge now pointing South)
8. **Walk 1 stride** forward (South), press middle button
9. **Turn right 90°** to face West, rotate Pi 90° right (USB edge now pointing West)
10. **Walk 1 stride** forward (West), press middle button

**Expected result on dashboard:**
- Should show a square path
- Naive and Bayesian filters should track closely
- Each side should be ~0.7m (one stride length)

### Calibration System

The system has automatic calibration:
- When you click "START WALKING", it captures your initial orientation
- That becomes "0° North" for your session
- You don't need to align with true magnetic North
- **BUT you must maintain consistent Pi orientation from that point!**

## Common Mistakes

### Mistake 1: Random Pi Rotation
```
❌ WRONG:
Stride 1: Pi pointing 45° (Northeast)
Stride 2: Pi pointing 120° (Southeast)  ← Accidentally rotated!
Stride 3: Pi pointing 210° (Southwest)  ← Rotated again!
Result: Random trajectory
```

```
✅ CORRECT:
Stride 1: Pi pointing 0° (North)
Stride 2: Pi pointing 0° (North)    ← Kept same orientation
Stride 3: Pi pointing 0° (North)    ← Kept same orientation
Result: Straight line North
```

### Mistake 2: Pi Not Level
```
❌ WRONG: Tilting the Pi
   ╱─────╲
  │  Pi   │  ← Tilted, compass reading wrong
   ╲─────╱

✅ CORRECT: Pi flat and level
  ┌─────┐
  │  Pi │  ← Flat, compass reading accurate
  └─────┘
```

### Mistake 3: Mixing Up "You Face" vs "Pi Points"
```
❌ WRONG:
You face East, but Pi points North  ← Mismatch!
System tracks where Pi points (North)
You walk East
Result: Trajectory doesn't match your path

✅ CORRECT:
You face East, Pi points East  ← Match!
System tracks where Pi points (East)
You walk East
Result: Trajectory matches your path
```

## Debug Log Analysis

You can verify proper orientation by checking `filters_debug.log`:

**Good orientation (consistent heading):**
```
STRIDE #1: Absolute yaw: 130.49°
STRIDE #2: Absolute yaw: 131.12°  ← Only 0.63° difference ✓
STRIDE #3: Absolute yaw: 129.87°  ← Only 1.62° difference ✓
```

**Bad orientation (you're rotating the Pi):**
```
STRIDE #1: Absolute yaw: 126.91°
STRIDE #2: Absolute yaw: 52.72°   ← 74° rotation! ✗
STRIDE #3: Absolute yaw: 288.91°  ← 236° rotation! ✗
```

## Advanced: Understanding IMU vs Intended Path

**The IMU doesn't know your intentions!** It only knows:
1. Which way the Pi is physically pointing (yaw/heading)
2. How the Pi is accelerating

**This means:**
- If you want to walk North → Point the Pi North
- If you want to walk East → Point the Pi East
- The system has NO way to know "I want to walk North" if the Pi is pointing Southeast

**Physical analogy:**
- The Pi is like a compass
- It always shows where it's pointing
- If you want to track "walking North", you must keep the compass needle pointing North
- If the compass spins randomly, the tracking will be random

## Troubleshooting

### "My trajectory is random/chaotic"
→ **Cause:** You're rotating the Pi between strides
→ **Fix:** Keep the Pi oriented in a fixed direction, or rotate it deliberately when changing direction

### "Straight line shows curve"
→ **Cause 1:** You're letting the Pi rotate slightly in your hands
→ **Fix:** Hold it more firmly, or use both hands

→ **Cause 2:** Your walking path actually curves (you're not walking perfectly straight)
→ **Note:** This is normal human behavior - we don't walk perfectly straight

### "Square path shows random polygon"
→ **Cause:** Not rotating the Pi 90° at each corner
→ **Fix:** When turning, consciously rotate the Pi to point in new direction

### "LED arrows point wrong direction"
→ **Cause:** Pi is mounted at wrong angle
→ **Fix:** Check which edge is "forward" (see LED arrow direction guide)

## Summary

**Key Rules:**
1. ✓ Keep Pi flat (SenseHat LEDs facing up)
2. ✓ Choose a "forward edge" (e.g., USB ports)
3. ✓ Always keep that edge pointing in your walking direction
4. ✓ DON'T let the Pi rotate accidentally
5. ✓ DO rotate the Pi deliberately when changing direction

**Remember:** The system tracks where the Pi points, NOT where you intend to go!

---

**Created:** 2026-01-07
**Purpose:** Fix trajectory issues caused by improper device orientation
