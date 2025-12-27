# Pedestrian Inertial Navigation System
**Data Fusion Architectures (DFA) - Master SSE 25/26**

Indoor pedestrian navigation using Raspberry Pi + SenseHat with Bayesian filtering and floor plan constraints.

---

## 📁 Project Structure

```
dataFusion/
├── launcher.py                 # 🚀 MAIN LAUNCHER (run this on laptop!)
├── test_system.py              # System tests
│
├── src/                        # Main source code ⭐
│   ├── bayesian_filter.py      # Bayesian filter (Equation 5 from paper)
│   └── web_dashboard_advanced.py # Advanced dashboard with auto-walk
│
├── mqtt/                       # MQTT Stream Management ✅ (Part 1 - 15%)
│   ├── mqtt_cpu_publisher.py           # Program 1: CPU metrics
│   ├── mqtt_location_publisher.py      # Program 2: Bayesian positions
│   ├── mqtt_subscriber_windowed.py     # Program 3: Windowed averaging
│   ├── mqtt_subscriber_bernoulli.py    # Program 4: Bernoulli sampling
│   ├── malfunction_detection.py        # 2 detection rules
│   └── README.md                        # MQTT documentation
│
├── examples/                   # Tutorial scripts
│   ├── 01_collect_stride_data.py       # Button-triggered data collection
│   ├── 02_naive_dead_reckoning.py      # Simple dead reckoning demo
│   ├── compare_algorithms.py           # Naive vs Bayesian comparison
│   └── understand_sensors.py           # Interactive sensor explorer
│
├── utils/                      # Utility tools
│   ├── GetData.py              # Simple sensor reader
│   └── test_leds_heading.py    # LED matrix test
│
├── notebooks/                  # Jupyter analysis
│   └── 03_analyze_data.ipynb   # Data analysis template
│
├── docs/                       # Documentation
│   ├── DFA_assignment.pdf                      # Assignment specification
│   ├── Pedestrian_inertial_navigation_...pdf   # Reference paper
│   ├── API Reference - Sense HAT.pdf           # Hardware reference
│   ├── BAYESIAN_FILTER_README.md               # Algorithm documentation
│   └── QUICK_START_BAYESIAN.md                 # Quick start guide
│
├── templates/                  # HTML templates for Flask
│   ├── index.html              # Basic dashboard UI
│   └── advanced.html           # Advanced comparison UI
│
├── scripts/                    # Shell utilities
│   ├── transfer_to_pi.sh       # Transfer files to Pi
│   ├── get_data_from_pi.sh     # Download data from Pi
│   └── start_dashboard.sh      # Quick launch dashboard
│
├── output/                     # Generated visualizations
│   ├── floor_plan_pdf.png
│   ├── algorithm_comparison.png
│   └── error_comparison.png
│
├── archive/                    # Old files (not needed for assignment)
│   └── old_docs/               # Redundant documentation
│
├── DEMO_SYSTEM.md              # ⭐ How to run the complete system
└── README.md                   # This file
```

---

## ✅ Implemented Features

### Part 2: IMU Assignment (Partial - ~40%)
- ✅ **Bayesian Filter** (Section II.C from paper)
  - Floor plan PDF (L-shaped hallway)
  - Five probability distributions (Equation 5)
  - Mode-seeking with scipy.optimize
  - Real-time position correction
- ✅ **Linear Kalman Filter** (yaw angle filtering)
- ✅ **Web Dashboard** (Flask-based interface)
- ✅ **Naive Dead Reckoning** (baseline comparison)
- ✅ **Data Collection Tools**

---

## ❌ Missing Components (Required for Passing)

### Part 1: MQTT Data Stream Management (15% - NOT STARTED)
- [ ] **Program 1:** CPU performance publisher (psutil + paho-mqtt)
- [ ] **Program 2:** SenseHat location publisher (Bayesian predictions)
- [ ] **Program 3:** Subscriber with windowed averaging (2 instances)
- [ ] **Program 4:** Subscriber with Bernoulli sampling (1/3 of data)
- [ ] **Finally:** Two malfunction detection rules

### Part 2: IMU Assignment (75% - 40% COMPLETE)
- [ ] **Particle Filter** implementation
- [ ] **Jupyter Notebook** with:
  - [ ] All three algorithms visualized
  - [ ] Mathematical equations (LaTeX)
  - [ ] Parameter value table
  - [ ] Impact of priors/likelihoods discussion
  - [ ] Experiments showing parameter effects
  - [ ] Error analysis plots
  - [ ] Computational cost comparison
- [ ] **Architecture Analysis** (3 categorizations)
- [ ] **Configuration System** (YAML/JSON files)
- [ ] **Error Propagation Analysis**

---

## 🚀 Quick Start

### ⭐ EASIEST WAY - Use Launcher (Recommended!)

```bash
# Run on your LAPTOP - opens browser automatically
python3 launcher.py

# Click "Connect to Raspberry Pi" button
# Dashboard starts automatically on Pi!
```

### Alternative Methods:

#### 1. Test Bayesian Filter Locally
```bash
cd examples
python3 compare_algorithms.py
```

#### 2. Manual Pi Setup
```bash
# Transfer files to Pi
./scripts/transfer_to_pi.sh

# SSH to Pi
ssh jdmc@10.111.224.71

# Run dashboard
cd ~/dataFusion/src
python3 web_dashboard_advanced.py

# Access: http://10.111.224.71:5001
```

---

## 📊 Current Grade Estimate: ~45-50% (FAILING)

### Breakdown:
| Component | Weight | Status | Estimated Score |
|-----------|--------|--------|----------------|
| **Part 1: MQTT DSMS** | 15% | ❌ Not started | 0-2% |
| **Part 2: IMU** | 75% | ⚠️ Partial (40%) | 40-45% |
| **Total** | 90% | | **~45%** |

### What's Missing = 45% of Grade:
- MQTT system (15%)
- Particle filter (10%)
- Jupyter analysis (15%)
- Documentation/discussion (5%)

---

## 📝 Assignment Requirements Checklist

### Part 1: MQTT (15%)
- [ ] Program 1: CPU publisher (psutil)
- [ ] Program 2: Location publisher (Bayesian)
- [ ] Program 3: Windowed subscriber (2 instances)
- [ ] Program 4: Bernoulli sampling subscriber
- [ ] Two malfunction detection rules

### Part 2: IMU (75%)
**Code (35%):**
- [x] Bayesian filter (Section II.C)
- [ ] Particle filter
- [x] Linear Kalman filter
- [x] Working Python code
- [ ] Well-commented with explanations

**Analysis (40%):**
- [ ] Jupyter notebook with visualizations
- [ ] Mathematical equations displayed
- [ ] Parameter value table
- [ ] Discussion of priors/likelihoods
- [ ] Experiments showing impact
- [ ] Error analysis
- [ ] Computational cost comparison
- [ ] Architecture categorization (3 types)
- [ ] Common representational format
- [ ] Temporal/spatial alignment
- [ ] Configuration system
- [ ] Error propagation analysis

---

## 🎯 Priority Action Plan

### Week 1: Core Implementation
1. **Day 1-2:** Implement 4 MQTT programs
2. **Day 3-4:** Implement particle filter
3. **Day 5:** Test everything on Raspberry Pi

### Week 2: Documentation & Analysis
1. **Day 1-2:** Create comprehensive Jupyter notebook
2. **Day 3:** Parameter experiments & error analysis
3. **Day 4:** Architecture discussion & documentation
4. **Day 5:** Final testing & submission prep

---

## 📚 Key References

1. **Main Paper:** Koroglu & Yilmaz (2017) - Pedestrian inertial navigation ([docs/Pedestrian_inertial_navigation_...pdf](docs/Pedestrian_inertial_navigation_with_building_floor_plans_for_indoor_environments_via_non-recursive_Bayesian_filtering.pdf))
2. **Assignment:** [docs/DFA_assignment.pdf](docs/DFA_assignment.pdf)
3. **SenseHat API:** [docs/API Reference - Sense HAT.pdf](docs/API%20Reference%20-%20Sense%20HAT.pdf)

---

## 🔧 Hardware Requirements

- Raspberry Pi (3 or 4)
- Sense HAT (LSM9DS1 IMU)
- Power supply
- WiFi connection

---

## 📦 Dependencies

```bash
pip3 install flask numpy scipy matplotlib pandas sense-hat paho-mqtt psutil
```

---

## 👥 Authors

[Your Name(s) Here]

---

## 📄 License

Educational project for Data Fusion Architectures course
