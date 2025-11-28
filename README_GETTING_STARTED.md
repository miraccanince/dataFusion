# Getting Started - Naive Implementation Guide

## The Learning Progression

Your teacher wants you to build this step-by-step to understand WHY we need Bayesian filtering:

```
Step 1: Collect Data         → Understand sensors
Step 2: Naive Dead Reckoning → See the problems
Step 3: Analyze Results      → Quantify errors
Step 4: Add Kalman Filter    → Smooth sensor noise
Step 5: Add Bayesian Filter  → Use floor plan
Step 6: Add Particle Filter  → Compare approaches
```

## Quick Start

### 1. Data Collection (First!)

Run on Raspberry Pi:
```bash
python 01_collect_stride_data.py
```

What this does:
- Press joystick button → records sensor data
- One button press = one stride event
- Saves to `stride_data.csv`
- **Goal**: Understand what your sensors actually output

### 2. Naive Position Tracking

Run on Raspberry Pi:
```bash
python 02_naive_dead_reckoning.py
```

What this does:
- Button press = move 0.7m in current heading direction
- Simple formula: `new_position = old_position + stride_length * direction`
- NO filtering, NO floor plan, NO intelligence
- Saves to `naive_trajectory.csv`
- **Goal**: See how quickly errors accumulate

### 3. Analyze on Your Computer

Transfer CSV files to your computer, then:
```bash
jupyter notebook 03_analyze_data.ipynb
```

What this shows:
- Plot your walked path
- See heading drift
- Measure position errors
- **Goal**: Understand WHY we need better methods

## Understanding the Data Flow

### JSON → CSV (Excel)

Yes, this makes perfect sense! Here's why:

**JSON** (from GetData.py):
```json
{
  "timestamp": "2025-11-28T10:30:00Z",
  "yaw_deg": 45.2,
  "accel_x": 0.02,
  ...
}
```

**CSV** (for Excel analysis):
```csv
stride,timestamp,x,y,yaw_deg,accel_x
1,2025-11-28T10:30:00Z,0.5,0.5,45.2,0.02
2,2025-11-28T10:30:05Z,1.0,1.0,47.1,0.01
```

Benefits of CSV:
- ✅ Open in Excel for easy viewing
- ✅ Plot in Python/Jupyter easily
- ✅ Share with team
- ✅ Understand patterns before coding filters

## Joystick as Stride Detector

Your teacher's approach (button press = stride):

```python
# Instead of complex accelerometer analysis
# Start simple:

wait_for_button_press()  # You press button
record_sensor_data()     # Capture IMU readings
update_position()        # Move 0.7m in heading direction
```

Later, you'll replace this with:
```python
detect_stride_from_accelerometer()  # Automatic detection
```

But starting with button presses lets you:
- Control timing exactly
- Focus on position estimation first
- Debug step-by-step
- Understand the algorithm before adding complexity

## What You'll Learn

### Week 1-2: Naive Approach
- ✅ Button press = stride
- ✅ Fixed stride length (0.7m)
- ✅ Heading from gyro (unreliable!)
- ✅ See: Position drifts badly

### Week 3-4: Add Intelligence
- ✅ Kalman filter for sensor smoothing
- ✅ Bayesian filter with floor plan
- ✅ Particle filter comparison

### Week 5-6: Real Implementation
- ✅ Automatic stride detection from accelerometer
- ✅ Real-time visualization
- ✅ MQTT streaming

## File Structure

```
dataFusion/
├── GetData.py                      # Raw sensor reading (you have this)
├── 01_collect_stride_data.py       # Collect with button press
├── 02_naive_dead_reckoning.py      # Simple position tracking
├── 03_analyze_data.ipynb           # Jupyter analysis
├── stride_data.csv                 # Output: sensor readings per stride
├── naive_trajectory.csv            # Output: x,y positions
└── README_GETTING_STARTED.md       # This file
```

## Common Questions

### Q: Why CSV instead of keeping JSON?
**A:** CSV is easier to analyze in Excel and plot in Python. JSON is good for transmission, CSV is good for analysis.

### Q: Why button press instead of automatic detection?
**A:** Start simple! Understand position estimation FIRST, then add automatic stride detection LATER.

### Q: What stride length should I use?
**A:** Start with 0.7m (average), then measure YOUR actual stride and update it.

### Q: How many strides should I collect?
**A:** Start with 10-20 strides in a simple path (rectangle or L-shape). You'll see the drift immediately!

## Next Session Plan

1. **Run script 01** - Collect 20 strides worth of data
2. **Run script 02** - Track position using naive method
3. **Open notebook 03** - Analyze and see the problems
4. **Discuss** - Why do we need Bayesian filtering?
5. **Then** - Implement the smart algorithms

## Tips

- Start in a hallway or simple room
- Walk in a square or rectangle (easier to measure error)
- Keep initial orientation aligned (e.g., face north)
- Press button BEFORE each step (not during)
- Take consistent stride lengths

Good luck! 🚀
