# 🍓 Raspberry Pi Setup Guide

## Complete Installation Steps

### 1. System Packages
```bash
sudo apt-get update
sudo apt-get install -y mosquitto mosquitto-clients sense-hat python3-sense-hat
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

### 2. Python Dependencies
```bash
# Install all required packages
pip3 install numpy scipy flask matplotlib paho-mqtt psutil --break-system-packages
```

If you get errors, install one by one:
```bash
pip3 install numpy --break-system-packages
pip3 install scipy --break-system-packages
pip3 install flask --break-system-packages
pip3 install matplotlib --break-system-packages
pip3 install paho-mqtt --break-system-packages
pip3 install psutil --break-system-packages
```

### 3. Make Script Executable
```bash
chmod +x start_dashboard_pi.sh
```

### 4. Start Dashboard
```bash
./start_dashboard_pi.sh
```

### 5. Access from Your Laptop
Open browser and go to: `http://[PI_IP_ADDRESS]:5001`

Example: `http://10.49.216.71:5001`

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'scipy'"
**Solution:** Install scipy: `pip3 install scipy --break-system-packages`

### Error: "ModuleNotFoundError: No module named 'sense_hat'"
**Solution:**
```bash
sudo apt-get install -y sense-hat python3-sense-hat
pip3 install sense-hat --break-system-packages
```

### Error: Dashboard not accessible
**Check:**
1. Pi and laptop on same WiFi
2. Dashboard is running (check terminal for "Running on http://0.0.0.0:5001")
3. Use Pi's IP address (find with: `hostname -I`)

### Charts not updating / Missing trajectories
**Solution:** Click "Reset Tracking" button and start fresh

---

## How to Use the System

### Starting Position
1. **Hold Pi FLAT** (like holding a tray)
2. **Point USB ports NORTH** (0° compass heading)
3. **Stand at your start position** (default: center of room at 1.75m, 3.0m)
4. **Keep level** (roll ≈ 0°, pitch ≈ 0°)

### Walking and Recording Strides
1. Click "START WALKING (Joystick)"
2. **Point the Pi in the direction you want to walk**
3. **Press MIDDLE button** (push down joystick) to record each stride
4. Watch trajectories update in real-time
5. Click "STOP WALKING" when done

### Compass Directions
- **0° = North** (top of map)
- **90° = East** (right side of map)
- **180° = South** (bottom of map)
- **270° = West** (left side of map)

---

## Floor Plan Details

**Room Dimensions:** 3.5m (width) × 6.0m (height)
- **Walls:** 0.3m thick on all 4 sides
- **Walkable area:** 2.9m × 5.4m (interior space)
- **Start position (default):** (1.75m, 3.0m) - center of room

**Map Orientation:**
- X-axis: 0m (West) → 3.5m (East)
- Y-axis: 0m (South) → 6.0m (North)

---

## Understanding the Trajectories

**4 Algorithms Compared:**
1. **Naive (Raw IMU)** - Red - Simple dead reckoning, no corrections
2. **Bayesian Filter** - Blue - Uses floor plan constraints, avoids walls
3. **Kalman Filter** - Green - Smooth tracking, no floor plan awareness
4. **Particle Filter** - Purple - Multiple hypotheses with floor plan

**Expected Behavior:**
- **Bayesian & Particle:** Should stop at walls (constraint-aware)
- **Naive & Kalman:** Will walk through walls (no constraints)

---

## File Structure

```
dataFusion/
├── src/
│   ├── web_dashboard_advanced.py  # Main Flask application
│   ├── bayesian_filter.py         # Bayesian filter implementation
│   ├── kalman_filter.py           # Kalman filter
│   └── particle_filter.py         # Particle filter
├── templates/
│   └── tracking.html              # Web dashboard UI
├── mqtt/
│   ├── cpu_publisher.py           # MQTT data generator
│   ├── windowed_subscriber.py     # Part 1: Windowed sampling
│   └── bernoulli_subscriber.py    # Part 1: Bernoulli sampling
├── start_dashboard_pi.sh          # Startup script
└── requirements.txt               # Python dependencies
```

---

## Assignment Requirements

### Part 1 (15%): MQTT Data Stream
- ✅ CPU publisher generating system metrics
- ✅ Windowed subscriber (5-sample window)
- ✅ Bernoulli sampler (p=0.3)
- ✅ Malfunction detection rules
- ✅ Web dashboard control

### Part 2 (75%): Bayesian Navigation
- ✅ Non-recursive Bayesian filter (Koroglu & Yilmaz 2017)
- ✅ Floor plan constraints (wall detection)
- ✅ IMU-based heading estimation
- ✅ Stride detection via joystick
- ✅ Filter comparison (Naive, Bayesian, Kalman, Particle)
- ⚠️ **TODO:** Jupyter notebook with analysis

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./start_dashboard_pi.sh` | Start web dashboard |
| `python3 mqtt/cpu_publisher.py` | Start MQTT data generator |
| `python3 mqtt/windowed_subscriber.py` | Start windowed subscriber |
| `python3 mqtt/bernoulli_subscriber.py` | Start Bernoulli sampler |
| `Ctrl+C` | Stop any running program |

