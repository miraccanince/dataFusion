# Debug Logging Quick Start

## On Raspberry Pi

### Starting the Dashboard

When you start the dashboard, you'll see:

```bash
python3 src/web_dashboard_advanced.py
```

Output will show:
```
======================================================================
📝 DEBUG LOG ENABLED
   Location: /home/pi/dataFusion/filters_debug.log
   File will log each stride's detailed filter behavior
======================================================================
```

### During Walking

As you walk and press the middle button for each stride, you'll see console output:
```
[DEBUG] Stride #1 logged to: /home/pi/dataFusion/filters_debug.log
[DEBUG] Stride #2 logged to: /home/pi/dataFusion/filters_debug.log
[DEBUG] Stride #3 logged to: /home/pi/dataFusion/filters_debug.log
...
```

This confirms each stride is being logged successfully.

### Viewing the Log

After your walking session:

```bash
# View the entire log
cat /home/pi/dataFusion/filters_debug.log

# View specific strides
grep -A 50 "STRIDE #1" /home/pi/dataFusion/filters_debug.log

# Check Bayesian filter details
grep -A 30 "BAYESIAN FILTER INTERNAL" /home/pi/dataFusion/filters_debug.log

# See position comparisons
grep -A 5 "POSITION COMPARISON" /home/pi/dataFusion/filters_debug.log

# Count total strides logged
grep -c "^STRIDE #" /home/pi/dataFusion/filters_debug.log
```

### Downloading to Your Laptop

From your laptop terminal:

```bash
# Download the log file
scp pi@10.49.216.71:~/dataFusion/filters_debug.log .

# Then open it locally
cat filters_debug.log
# or
code filters_debug.log  # Opens in VS Code
```

## Log File Contents

For each stride, you'll see:

1. **Input heading** - absolute yaw, calibration, relative yaw
2. **Naive filter** - simple calculation
3. **Bayesian filter** - detailed optimization process including:
   - IMU prediction
   - Wall detection (if any)
   - Optimization iterations
   - Actual vs expected displacement
4. **Kalman filter** - measurement and update
5. **Particle filter** - weighted position
6. **Position comparison** - all filters side-by-side
7. **Deviation analysis** - how far each filter is from naive

## Troubleshooting

### Log file not being created?

Check console output when starting dashboard. You should see:
```
📝 DEBUG LOG ENABLED
   Location: /home/pi/dataFusion/filters_debug.log
```

If you see an error instead:
```
[ERROR] Failed to initialize debug log: <error message>
```

Check file permissions:
```bash
ls -l /home/pi/dataFusion/filters_debug.log
# Should show: -rw-r--r-- 1 pi pi ...

# If file doesn't exist or has wrong permissions:
touch /home/pi/dataFusion/filters_debug.log
chmod 644 /home/pi/dataFusion/filters_debug.log
```

### No stride messages appearing?

If you don't see `[DEBUG] Stride #X logged to:` messages while walking:
- Check if you're pressing the middle button on the SenseHat
- Verify "START WALKING" was clicked in the web dashboard
- Check the backend terminal for any error messages

### Log file exists but is empty?

If the file exists but has no stride data:
- Click "Reset Tracking" in the dashboard to initialize the log
- Then click "START WALKING" and press the middle button for strides

## gitignore Note

The `filters_debug.log` file is in `.gitignore`, so it won't be committed to git. This is intentional - logs are for debugging only and shouldn't be in version control.

---

**Quick Commands for Pi:**

```bash
# Start dashboard
python3 src/web_dashboard_advanced.py

# View log in real-time (in another terminal)
tail -f /home/pi/dataFusion/filters_debug.log

# View just Bayesian filter details
grep -A 15 "BAYESIAN FILTER INTERNAL" /home/pi/dataFusion/filters_debug.log | less

# Clear the log and start fresh
rm /home/pi/dataFusion/filters_debug.log
# Then click "Reset Tracking" in dashboard
```
