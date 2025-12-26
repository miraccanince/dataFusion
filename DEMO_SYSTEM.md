# System Demo Guide
**How to See the Complete System in Action**

---

## 🎯 System Overview

Your pedestrian navigation system has **3 main components**:

```
┌─────────────────────────────────────────────────────────────┐
│                    PEDESTRIAN NAVIGATION SYSTEM              │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │   MQTT   │        │ Bayesian │        │   Web    │
    │ Streaming│◄──────►│  Filter  │◄──────►│Dashboard │
    │(Part 1)  │        │(Part 2)  │        │(Part 2)  │
    └──────────┘        └──────────┘        └──────────┘
         │                     │                    │
         ▼                     ▼                    ▼
    4 Programs          Floor Plan           Real-time
    + 2 Rules          Constraints           Comparison
```

---

## 🚀 Quick Demo (Without Raspberry Pi)

### Demo 1: Bayesian Filter Comparison
**Shows:** How Bayesian filter corrects heading errors using floor plan

```bash
cd examples
python3 compare_algorithms.py
```

**What you'll see:**
- ✅ Floor plan visualization
- ✅ Simulated walk with realistic IMU drift
- ✅ Naive vs Bayesian trajectory comparison
- ✅ Error plots showing improvement
- ✅ Generated images in `output/`

**Output files:**
- `output/algorithm_comparison.png` - Side-by-side trajectories
- `output/error_comparison.png` - Error metrics over time
- `output/floor_plan_pdf.png` - Floor plan visualization

**Expected result:** Bayesian filter should be **5-10× more accurate** than naive!

---

### Demo 2: MQTT System (Local Testing)

**Terminal 1: Start MQTT Broker**
```bash
# Install if needed
pip3 install paho-mqtt

# Start local broker (or use mosquitto if installed)
# For testing, you can skip this and use test.mosquitto.org
```

**Terminal 2: CPU Publisher (Simulated)**
```bash
cd mqtt
python3 mqtt_cpu_publisher.py --broker test.mosquitto.org --duration 30
```

**Terminal 3: Windowed Subscriber (1s window)**
```bash
cd mqtt
python3 mqtt_subscriber_windowed.py --broker test.mosquitto.org --window 1.0
```

**Terminal 4: Bernoulli Subscriber**
```bash
cd mqtt
python3 mqtt_subscriber_bernoulli.py --broker test.mosquitto.org
```

**What you'll see:**
- Publisher sends CPU metrics every 10ms
- Windowed subscriber shows statistics every 1s
- Bernoulli subscriber samples ~33% of data
- Both show similar averages (unbiased sampling!)

---

## 🔧 Full Demo (With Raspberry Pi)

### Step 1: Setup Raspberry Pi

**Install dependencies:**
```bash
ssh jdmc@10.111.224.71

# Install MQTT broker
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients

# Install Python packages
pip3 install paho-mqtt psutil sense-hat numpy scipy matplotlib flask
```

**Transfer files:**
```bash
# From your laptop
cd /Users/mirac/Desktop/master_sse_25_26-main/dataFusion
./scripts/transfer_to_pi.sh
```

---

### Step 2: Start MQTT System (Part 1 - 15%)

**On Raspberry Pi - Terminal 1:**
```bash
cd ~/dataFusion/mqtt
python3 mqtt_cpu_publisher.py --broker localhost --interval 10
```

**On Raspberry Pi - Terminal 2:**
```bash
cd ~/dataFusion/mqtt
python3 mqtt_location_publisher.py --broker localhost --interval 10
```

**On Raspberry Pi - Terminal 3:**
```bash
cd ~/dataFusion/mqtt
python3 mqtt_subscriber_windowed.py --broker localhost --window 1.0
```

**On Raspberry Pi - Terminal 4:**
```bash
cd ~/dataFusion/mqtt
python3 mqtt_subscriber_windowed.py --broker localhost --window 5.0
```

**On Raspberry Pi - Terminal 5:**
```bash
cd ~/dataFusion/mqtt
python3 mqtt_subscriber_bernoulli.py --broker localhost
```

**On Raspberry Pi - Terminal 6:**
```bash
cd ~/dataFusion/mqtt
python3 malfunction_detection.py --broker localhost
```

**What happens:**
1. CPU publisher sends metrics every 10ms
2. Location publisher sends Bayesian positions every 10ms
3. Two windowed subscribers compute statistics (1s and 5s windows)
4. Bernoulli subscriber uses only 33% of data
5. Malfunction detector monitors for issues

**Test malfunction detection:**
```bash
# In a new terminal, stress the CPU
stress --cpu 4 --timeout 30s

# Watch terminal 6 for temperature/memory alerts
```

---

### Step 3: Start Web Dashboard (Part 2 - 75%)

**On Raspberry Pi - Terminal 7:**
```bash
cd ~/dataFusion/src
python3 web_dashboard_advanced.py
```

**On your laptop - Browser:**
```
http://10.111.224.71:5001
```

**What you can do:**
1. **View real-time sensors** - IMU data, orientation, environment
2. **Record strides** - Click buttons to compare algorithms:
   - Naive Dead Reckoning
   - Bayesian Filter (uses floor plan!)
   - Particle Filter (TODO)
3. **Set ground truth** - Enter your actual position
4. **Compare trajectories** - See all algorithms overlaid
5. **Calculate errors** - Get distance errors vs ground truth
6. **Tune parameters** - Adjust stride length, Kalman filter params
7. **Download data** - Export CSV for each algorithm

---

## 📊 What to Observe

### MQTT System Performance

**Expected values (Raspberry Pi 4):**

| Metric | Expected | Indicates |
|--------|----------|-----------|
| CPU Usage | 20-40% | Normal operation |
| Memory Usage | 40-60% | Normal operation |
| Temperature | 40-60°C | Normal operation |
| Publish Rate | ~100 msg/s | 10ms interval |
| Sampling Rate | ~33% | Bernoulli working |

**If you see:**
- 🔥 **Temp > 80°C**: Malfunction detector should alert!
- 💾 **Memory > 90%**: Malfunction detector should alert!
- ⚡ **CPU > 80%**: System may be overloaded

---

### Bayesian Filter Performance

**Walk a simple path:**
1. Start at (2m, 4m) in hallway
2. Walk north 5 steps (stay in hallway)
3. Turn east 90°
4. Walk east 5 steps

**Expected results:**

| Algorithm | Final Error | Stays in Hallway? |
|-----------|-------------|-------------------|
| **Naive** | 2-5m | ❌ Drifts through walls |
| **Bayesian** | 0.2-1m | ✅ Constrained to hallway |

**Why Bayesian is better:**
- Floor plan prevents position from going through walls
- Stride circle PDF keeps position at correct distance
- Motion model predicts straight/curved paths
- Combined: **10× more accurate!**

---

## 🧪 Experiments to Try

### Experiment 1: Parameter Sensitivity
**Question:** How does stride length affect accuracy?

```python
# In web dashboard, try different stride lengths:
# 0.5m, 0.7m (default), 0.9m

# Walk same path with each
# Compare errors
```

**Expected:** Bayesian should be robust to stride length variations.

---

### Experiment 2: Window Size Effect
**Question:** Does window size affect subscriber accuracy?

```bash
# Run 3 windowed subscribers:
python3 mqtt_subscriber_windowed.py --window 0.5
python3 mqtt_subscriber_windowed.py --window 1.0
python3 mqtt_subscriber_windowed.py --window 5.0

# Compare statistics
```

**Expected:**
- Smaller window → More noise, faster response
- Larger window → Smoother, slower response

---

### Experiment 3: Sampling Efficiency
**Question:** Does Bernoulli sampling give unbiased estimates?

```bash
# Compare windowed vs Bernoulli averages
# Same window size (5s)

# Windowed uses 100% of data
# Bernoulli uses 33% of data

# CPU averages should match within ±2%
```

**Expected:** Bernoulli mean ≈ Full data mean (unbiased!)

---

### Experiment 4: Floor Plan Effect
**Question:** What happens without floor plan constraints?

```python
# In src/bayesian_filter.py, modify posterior_probability():
# Comment out floor plan term

# log_posterior = (
#     # log(p_fp) +  # DISABLED
#     log(p_stride) + ...
# )

# Run compare_algorithms.py again
# Bayesian should perform worse (closer to naive)
```

---

## 📈 Data Collection

### For Jupyter Analysis

**Collect data from all algorithms:**

```bash
# 1. Walk a known path on Raspberry Pi
# 2. Record strides in web dashboard
# 3. Set ground truth at each checkpoint
# 4. Download CSV files:
#    - naive_trajectory_YYYYMMDD_HHMMSS.csv
#    - bayesian_trajectory_YYYYMMDD_HHMMSS.csv
#    - particle_trajectory_YYYYMMDD_HHMMSS.csv (TODO)
#    - ground_truth data

# 5. Transfer to laptop
./scripts/get_data_from_pi.sh

# 6. Analyze in Jupyter notebook
jupyter notebook notebooks/03_analyze_data.ipynb
```

---

## 🎓 Understanding the System

### Data Flow

```
SenseHat IMU
    │
    ├──► Accelerometer ──┐
    ├──► Gyroscope ─────┼──► Kalman Filter ──► Filtered Heading
    └──► Magnetometer ──┘
         │
         ▼
    Button Press = Stride Event
         │
         ▼
    ┌────────────────────────────────────┐
    │   Bayesian Filter (Equation 5)     │
    │                                    │
    │   p(xₖ|Zₖ) ∝                       │
    │     × p(xₖ|FP)      [Floor plan]   │
    │     × p(xₖ|dₖ,xₖ₋₁)  [Stride]      │
    │     × p(zₖ|xₖ)      [IMU]          │
    │     × p(xₖ|history) [Motion]       │
    │     × p(xₖ₋₁|Zₖ₋₁)   [Previous]     │
    │                                    │
    │   ▼ Mode-seeking (scipy.optimize)  │
    └────────────────────────────────────┘
         │
         ├──► Web Dashboard (visualization)
         │
         └──► MQTT Publisher (streaming)
                │
                ├──► Windowed Subscribers (statistics)
                ├──► Bernoulli Subscriber (sampling)
                └──► Malfunction Detector (monitoring)
```

---

## 🐛 Troubleshooting

### "Connection refused" (MQTT)
```bash
# Check if broker is running
sudo systemctl status mosquitto

# Start broker
sudo systemctl start mosquitto

# Check if port is open
netstat -an | grep 1883
```

### "ModuleNotFoundError: No module named 'sense_hat'"
```bash
# On Raspberry Pi only!
pip3 install sense-hat

# Not available on laptop (hardware-specific)
```

### "Web dashboard not accessible"
```bash
# Check if Flask is running
ps aux | grep python

# Check firewall
sudo ufw allow 5001

# Access from laptop browser:
http://10.111.224.71:5001
```

### Floor plan PDF not visualizing
```bash
# Install dependencies
pip3 install matplotlib scipy pillow

# Run test
cd src
python3 bayesian_filter.py
```

---

## 📁 File Reference

**Quick access to important files:**

| What | Where |
|------|-------|
| **MQTT Programs** | `mqtt/*.py` |
| **Bayesian Filter** | `src/bayesian_filter.py` |
| **Web Dashboard** | `src/web_dashboard_advanced.py` |
| **Algorithm Comparison** | `examples/compare_algorithms.py` |
| **Floor Plan Config** | `src/bayesian_filter.py:92-132` |
| **Assignment PDF** | `docs/DFA_assignment.pdf` |
| **Research Paper** | `docs/Pedestrian_inertial_navigation_...pdf` |
| **Main README** | `README.md` |

---

## 🎯 Next Steps

After running the demos:

1. ✅ **Understand the system** - You've seen it work!
2. ⚠️ **Implement particle filter** - Compare with Bayesian
3. ⚠️ **Create Jupyter notebook** - Analyze all data
4. ⚠️ **Write discussion** - Impact of parameters
5. ⚠️ **Test on real floor plan** - Your building layout

---

## 📞 Questions?

**Common questions:**

**Q: Why is Bayesian better than naive?**
A: Floor plan constrains position to walkable areas. Naive just integrates heading errors.

**Q: Why use MQTT for streaming?**
A: Assignment requires data stream management. MQTT is industry standard for IoT.

**Q: Why 10ms interval?**
A: Assignment specifies "every 10ms if possible". Shows real-time capability.

**Q: What's the point of Bernoulli sampling?**
A: Reduces computational load while maintaining unbiased estimates. Important for edge devices.

**Q: Do I need to run all terminals?**
A: No! You can test MQTT separately, or just use the web dashboard, or just run the comparison script.

---

**Ready to see it in action? Start with Demo 1 (no hardware needed)!**

```bash
cd examples
python3 compare_algorithms.py
```
