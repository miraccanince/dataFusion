# DFA Assignment Gap Analysis

**Date:** 2026-01-06
**Purpose:** Identify what's missing and create action plan

---

## Part 1: MQTT/DSMS (15% of final grade)

### ❌ STATUS: NOT STARTED

**What's Required:**

#### Program 1: CPU Performance Publisher
```python
# Publish CPU data using paho-mqtt and psutil
# - CPU temperature
# - CPU usage %
# - Memory usage
# - Publish every 10ms (if possible)
# - Each reading timestamped
```

#### Program 2: Sense HAT Data Publisher
```python
# Publish Bayesian predicted location
# - X, Y coordinates from Bayesian filter
# - Heading
# - Publish every 10ms (if possible)
# - Each reading timestamped
```

#### Program 3: Subscriber with Averaging
```python
# Subscribe to CPU performance data
# - Implement sliding window averaging
# - Run TWO instances with different window sizes
# Example: Window 1 = 100ms, Window 2 = 500ms
```

#### Program 4: Subscriber with Bernoulli Sampling
```python
# Subscribe to CPU performance data
# - Use (naive) Bernoulli sampling: ~1/3 of data points
# - Estimate averages over same windows as Program 3
# - Compare results
```

#### Finally: Malfunction Detection Rules
```python
# Two simple rules to detect RPi malfunction
# Example rules:
# 1. If CPU temp > 80°C for 5 seconds → Warning
# 2. If CPU usage > 95% for 10 seconds → Warning
```

---

## Part 2: IMU Assignment (75% of final grade)

### ✅ CODE IMPLEMENTATION: COMPLETE

We have:
- ✅ Bayesian filter (Koroglu Section II.C)
- ✅ Particle filter
- ✅ Kalman filter
- ✅ Real-time operation
- ✅ Live dashboard
- ✅ Floor plan constraints

### ❌ JUPYTER NOTEBOOK & ANALYSIS: MISSING

**What's Required for Submission:**

#### 1. Mathematical Equations ❌
**Requirement:** "Inference equations in mathematical form"

**Need to add:**
```
Equation 5 from Koroglu paper:
p(xk|Zk) ∝ p(xk|FP) × p(xk|dk,xk-1) × p(zk|xk) × p(xk|xk-1,...) × p(xk-1|Zk-1)

Where:
- p(xk|FP): Floor plan PDF
- p(xk|dk, xk-1): Stride circle (Gaussian at distance dk)
- p(zk|xk): Sensor likelihood (IMU heading)
- p(xk|xk-1,...): Motion model
- p(xk-1|Zk-1): Previous posterior

Each term with explicit Gaussian formulas showing μ and σ
```

#### 2. Parameter Values Table ❌
**Requirement:** "Supported by a table of parameter values used"

**Need table like:**
| Parameter | Value | Units | Meaning |
|-----------|-------|-------|---------|
| stride_length | 0.7 | m | Average human stride |
| sigma_stride | 0.1 | m | Stride uncertainty |
| sigma_heading | 0.5 | rad | Heading uncertainty |
| floor_plan_weight | 50.0 | - | Wall avoidance strength |
| stride_threshold | 1.2 | g | Accel threshold for detection |
| ... | ... | ... | ... |

#### 3. Architecture Analysis (3 Categories) ❌
**Requirement (0.1 weight):** "Three different architecture categorizations"

**Need to discuss:**

**a) Centralized vs Decentralized vs Distributed**
- Our system: Centralized (all processing on RPi)
- Pros: Simple, low latency
- Cons: Single point of failure

**b) Tightly-Coupled vs Loosely-Coupled**
- Our system: Tightly-coupled (IMU sensors directly integrated)
- Pros: Fast, synchronized
- Cons: Hard to add new sensors

**c) Hierarchical vs Flat**
- Our system: Hierarchical (Raw IMU → Filters → Position Estimate → Display)
- Pros: Clear data flow
- Cons: Limited parallelism

#### 4. Common Representational Format ❌
**Requirement (0.15 weight):** "Construct a common representational format"

**Need to document:**
```json
{
  "timestamp": "ISO 8601 format",
  "stride": 42,
  "position": {
    "x": 3.45,
    "y": 5.67,
    "uncertainty": {
      "sigma_x": 0.2,
      "sigma_y": 0.2
    }
  },
  "imu": {
    "roll": 1.2,
    "pitch": -0.8,
    "yaw": 87.3,
    "accel": {"x": 0.1, "y": 0.05, "z": 9.81}
  },
  "algorithm": "bayesian"
}
```

#### 5. Temporal & Spatial Alignment ❌
**Requirement (0.1 weight):** "Quantification of alignment differences"

**Need to analyze:**
- IMU sampling rate: 100 Hz
- Dashboard update rate: 500ms
- Stride detection delay: ~50ms
- How we align: Timestamps + buffering
- Quantify: Before vs after alignment error

#### 6. Configuration System ❌
**Requirement (0.15 weight):** "Configuration files supported"

**Need to create:**
```python
# config.yaml
filters:
  bayesian:
    stride_length: 0.7
    sigma_heading: 0.5
    floor_plan_weight: 50.0

  kalman:
    dt: 0.5
    Q: 0.01
    R: 0.1

  particle:
    n_particles: 200

system:
  stride_threshold: 1.2
  min_stride_interval: 0.3
```

#### 7. Error Propagation Analysis ❌
**Requirement (0.15 weight):** "Error analysis showing how model assumptions influence final outcome"

**Need experiments:**

**Experiment 1: Impact of floor_plan_weight**
- Test: floor_plan_weight = [10, 20, 50, 100]
- Measure: How often Bayesian crosses walls
- Result: Plot error vs weight

**Experiment 2: Impact of sigma_heading**
- Test: sigma_heading = [0.1, 0.5, 1.0, 2.0]
- Measure: Position accuracy
- Result: Show optimal value

**Experiment 3: Stride length uncertainty**
- Test: Add noise to stride length
- Measure: How it propagates to final position
- Formula: σ_position = sqrt(n) × σ_stride (for n strides)

#### 8. Discussion of Priors/Likelihoods Impact ❌
**Requirement:** "Discussion of the impact of changes in the priors and likelihoods"

**Need to explain:**
- What happens if floor plan prior is too weak? (Goes through walls)
- What happens if sensor likelihood σ is too small? (Overfits noisy IMU)
- What happens if motion model is too strong? (Fights direction changes)

#### 9. Visualized Output ⚠️
**Requirement:** "The visualized output"

**We have:** Dashboard with real-time trajectories
**Need to add to notebook:**
- Static plots from experiments
- Error bar plots
- Comparison charts
- Heat maps of floor plan PDF

---

## HOW TO APPROACH PART 1 (MQTT)

### Option 1: Separate from Part 2 (Recommended)

**Create new folder:** `mqtt_system/`

```
mqtt_system/
├── program1_cpu_publisher.py      # Publishes psutil data
├── program2_sensehat_publisher.py # Publishes Bayesian position
├── program3_subscriber_avg.py     # Averaging (run 2 instances)
├── program4_subscriber_bernoulli.py # Bernoulli sampling
├── rules_monitor.py               # Malfunction detection
└── README_MQTT.md                 # Documentation
```

**Why separate?**
- Part 1 is about MQTT/streaming (15%)
- Part 2 is about IMU/Bayesian filter (75%)
- Different evaluation criteria
- Can work in parallel

### Option 2: Integrate with Existing System

**Modify** `web_dashboard_advanced.py` to also publish via MQTT

**Pros:**
- Reuse existing Bayesian filter
- Real data from actual walking

**Cons:**
- More complex
- Mixes two assignments
- Harder to debug

### My Recommendation:

**Do Option 1 (Separate)**

1. **Install MQTT on Pi:**
```bash
sudo apt-get install mosquitto mosquitto-clients
pip3 install paho-mqtt psutil
```

2. **Start simple:**
```python
# program1_cpu_publisher.py
import paho.mqtt.client as mqtt
import psutil
import time
import json
from datetime import datetime

client = mqtt.Client()
client.connect("localhost", 1883, 60)

while True:
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": psutil.cpu_percent(),
        "cpu_temp": psutil.sensors_temperatures()['cpu_thermal'][0].current,
        "memory_percent": psutil.virtual_memory().percent
    }

    client.publish("sensor/cpu", json.dumps(data))
    time.sleep(0.01)  # 10ms = 100 Hz
```

3. **Then build the others similarly**

---

## PRIORITY ACTION PLAN

### Week 1: Complete Part 1 (MQTT)
1. Set up MQTT broker on Pi
2. Write Program 1 (CPU publisher)
3. Write Program 2 (SenseHAT publisher) - can publish mock data
4. Write Program 3 (Subscriber with averaging)
5. Write Program 4 (Bernoulli sampling)
6. Write malfunction detection rules

### Week 2: Complete Part 2 Documentation
1. Create Jupyter notebook
2. Add mathematical equations
3. Create parameter table
4. Run experiments (floor_plan_weight, sigma_heading, etc.)
5. Generate plots and analysis
6. Write architecture analysis
7. Write error propagation analysis
8. Document common representational format

### Week 3: Polish & Submit
1. Test entire system on Pi
2. Generate final report
3. Clean up code
4. Add comments
5. Create README files
6. Submit!

---

## CRITICAL MISSING ITEMS (High Priority)

1. ❌ **Part 1 MQTT system** - 0/4 programs written (15% of grade!)
2. ❌ **Jupyter notebook** - No analysis notebook exists
3. ❌ **Mathematical equations in notebook** - Required for rubric
4. ❌ **Parameter values table** - Required for rubric
5. ❌ **Architecture analysis** - 10% of Part 2 grade
6. ❌ **Error propagation experiments** - 15% of Part 2 grade

---

## WHAT WE HAVE (Already Complete)

1. ✅ Bayesian filter implementation (Koroglu Equation 5)
2. ✅ Particle filter implementation
3. ✅ Kalman filter implementation
4. ✅ Real-time dashboard
5. ✅ Floor plan constraints
6. ✅ Mock test system
7. ✅ Report generation
8. ✅ IMU sensor readings display
9. ✅ Mode-seeking optimization

---

## ESTIMATED WORK REMAINING

- **Part 1 (MQTT):** ~8-12 hours
- **Part 2 (Documentation):** ~12-16 hours
- **Testing & Polish:** ~4-6 hours

**Total:** ~24-34 hours

---

## NEXT STEPS

1. **Decide:** Do Part 1 first (easier, separate) or Part 2 documentation first?
2. **My recommendation:** Part 1 first - it's independent and worth 15%
3. **Then:** Create comprehensive Jupyter notebook for Part 2

Do you want me to:
- A) Start implementing the MQTT system (Part 1)?
- B) Create the Jupyter notebook with analysis (Part 2)?
- C) Both in parallel?
