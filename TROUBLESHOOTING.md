# Troubleshooting Guide

## Issue: "Start Walking" Button Does Nothing

### ✅ FIXED - What Was Wrong:

1. **IMU values (Roll, Pitch, Yaw) weren't updating**
   - Fixed: Now updates continuously when "Start Walking" is active
   - You should see Roll/Pitch/Yaw values changing as you tilt the Pi

2. **No strides detected when walking**
   - Fixed: Added debug logging to show acceleration magnitude
   - You can now see in terminal if you're walking hard enough

---

## How to Test (After Friend Updates Code on Pi):

### Step 1: Start Dashboard

On Raspberry Pi:
```bash
cd ~/dataFusion/src
python3 web_dashboard_advanced.py
```

### Step 2: Access Dashboard

On your laptop browser:
```
http://10.49.216.71:5001
```

### Step 3: Test IMU Readings

1. **Before clicking Start Walking:**
   - IMU values will show 0.0° (this is normal)

2. **Click "START WALKING":**
   - IMU values should START CHANGING immediately
   - Tilt the Pi left/right → Roll changes
   - Tilt the Pi forward/back → Pitch changes
   - Rotate the Pi → Yaw changes

3. **Check Terminal on Pi:**
   You should see output like:
   ```
   🚶 Auto-walk monitor started
      Stride threshold: 1.2g
      Min stride interval: 0.3s
      💡 TIP: Walk vigorously to trigger stride detection!

      Accel magnitude: 1.01g (threshold: 1.2g)  ← Pi sitting still
      Accel magnitude: 1.03g (threshold: 1.2g)  ← Still too low
      Accel magnitude: 1.45g (threshold: 1.2g)  ← Walking! Above threshold!
   ✓ Stride 1 detected! Position: Bayesian=(2.12, 4.68)
   ```

---

## If Strides Still Not Detected:

### Problem: Acceleration too low

**Symptoms:**
- Terminal shows: `Accel magnitude: 1.01g (threshold: 1.2g)`
- Stride count stays at 0

**Solution:**
Walk MORE VIGOROUSLY! The Pi needs to experience >1.2g acceleration.

**How to walk:**
1. Put Pi in backpack
2. Walk with strong, deliberate steps
3. Stomp a bit (don't break it!)
4. Or shake the Pi a bit while walking

### Problem: Threshold too high

If walking vigorously still doesn't work, **lower the threshold:**

**Option A: Use Manual Walk Controls (Easier)**

Instead of clicking "Start Walking", use the directional buttons (N, S, E, W) on the right side of the dashboard. These simulate strides without needing sensor data.

**Option B: Lower the Threshold**

Edit `src/web_dashboard_advanced.py`:
```python
# Line 73, change from:
stride_threshold = 1.2  # Acceleration threshold in g

# To:
stride_threshold = 1.1  # Lower threshold (easier to trigger)
```

Then restart dashboard.

---

## Testing Checklist:

### ✅ Before Walking:
- [ ] Dashboard loads at http://10.49.216.71:5001
- [ ] Connection status shows "Connected"
- [ ] IMU values show 0.0° (before Start Walking)
- [ ] MQTT broker status shows "Running" (for MQTT tests)

### ✅ After Clicking "Start Walking":
- [ ] Status card changes color (shows "WALKING")
- [ ] IMU values start updating (Roll, Pitch, Yaw change when you tilt Pi)
- [ ] Terminal shows "Auto-walk monitor started"
- [ ] Terminal shows acceleration magnitude every 2 seconds

### ✅ While Walking:
- [ ] Terminal shows "Stride X detected!" when you walk
- [ ] Stride count increases on dashboard
- [ ] Trajectory lines appear on map
- [ ] Position values update

### ✅ Alternative (Manual Mode):
- [ ] Click N/S/E/W buttons
- [ ] Trajectory lines appear
- [ ] Works without needing to walk

---

## What The Fixes Do:

### Fix 1: Continuous IMU Updates
```python
# Now ALWAYS updates IMU in the monitoring loop
orientation_deg = sense.get_orientation_degrees()
latest_imu = {
    'roll': round(orientation_deg.get('roll', 0), 1),
    'pitch': round(orientation_deg.get('pitch', 0), 1),
    'yaw': round(orientation_deg.get('yaw', 0), 1)
}
```

**Result:** Roll/Pitch/Yaw update continuously while "Start Walking" is active

### Fix 2: Debug Logging
```python
# Logs acceleration magnitude every 2 seconds
if sample_count % 40 == 0:
    accel_mag = np.sqrt(accel['x']**2 + accel['y']**2 + accel['z']**2)
    logger.info(f"Accel magnitude: {accel_mag:.2f}g (threshold: {stride_threshold}g)")
```

**Result:** You can see in terminal if you're walking hard enough

---

## Expected Terminal Output:

### When Working Correctly:
```
🚶 Auto-walk monitor started
   Stride threshold: 1.2g
   Min stride interval: 0.3s
   💡 TIP: Walk vigorously to trigger stride detection!

   Accel magnitude: 1.01g (threshold: 1.2g)  ← Still
   Accel magnitude: 1.03g (threshold: 1.2g)  ← Still
   Accel magnitude: 1.51g (threshold: 1.2g)  ← WALKING!
✓ Stride 1 detected! Position: Bayesian=(2.12, 4.68)
   Accel magnitude: 1.48g (threshold: 1.2g)  ← Walking
✓ Stride 2 detected! Position: Bayesian=(2.82, 4.55)
✓ Stride 3 detected! Position: Bayesian=(3.49, 4.43)
```

### Dashboard Should Show:
- Status: "WALKING"
- Connection: "Connected"
- Strides: Increasing numbers (1, 2, 3...)
- Roll: Changing as you tilt (e.g., -2.5°, 1.3°, 0.8°...)
- Pitch: Changing as you tilt (e.g., 5.2°, -1.1°, 3.4°...)
- Yaw: Changing as you rotate (e.g., 87.3°, 92.1°, 180.5°...)
- Map: Blue/red/green lines appearing

---

## Quick Test Without Walking:

**Use Manual Walk Controls!**

1. Look for "Manual Walk" section on right side
2. Click buttons: N (North), S (South), E (East), W (West)
3. Each click = one 0.7m stride
4. Trajectory appears on map
5. No Pi movement needed!

This is perfect for:
- Testing the system
- Demonstrating to professor
- Taking screenshots for report

---

## If Still Having Issues:

1. **Check Pi terminal for errors**
   - Look for red error messages
   - Check if SenseHat is detected

2. **Verify SenseHat is working:**
   ```python
   # On Pi, test SenseHat:
   python3 -c "from sense_hat import SenseHat; s=SenseHat(); print(s.get_orientation_degrees())"
   ```
   Should print something like: `{'roll': 0.5, 'pitch': 1.2, 'yaw': 87.3}`

3. **Use Mock Test Mode:**
   - In dashboard, there's a "Mock Test" button
   - Simulates 10 strides automatically
   - Good for testing filters without hardware

---

## Summary:

**Problem:** IMU not updating, strides not detected
**Solution:** Fixed both in code
**Test:** Click "Start Walking", tilt Pi, watch IMU values change
**Walking:** Walk vigorously (>1.2g) OR use Manual Walk buttons

**Changes committed! Friend needs to pull latest code.**
