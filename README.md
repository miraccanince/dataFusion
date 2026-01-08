# Pedestrian Inertial Navigation System
**Data Fusion Architectures (DFA) - Master SSE 25/26**

Indoor pedestrian navigation using Raspberry Pi + SenseHat with Bayesian filtering and floor plan constraints.

---

## 📁 Project Structure

```
dataFusion/
├── src/                        # Main source code ⭐
│   ├── bayesian_filter.py       # Bayesian filter implementation (Equation 5)
│   ├── kalman_filter.py         # Linear Kalman filter
│   ├── particle_filter.py       # Particle filter implementation
│   ├── web_dashboard_advanced.py # Flask dashboard with real-time tracking
│   └── mock_sense_hat.py        # Mock SenseHat for local testing
│
├── mqtt/                       # MQTT Stream Management ✅ (Part 1 - 15%)
│   ├── mqtt_cpu_publisher.py            # Program 1: CPU metrics publisher
│   ├── mqtt_location_publisher.py       # Program 2: Bayesian position publisher
│   ├── mqtt_subscriber_windowed.py      # Program 3: Windowed averaging
│   ├── mqtt_subscriber_bernoulli.py     # Program 4: Bernoulli sampling
│   ├── malfunction_detection.py         # 2 detection rules
│   ├── demo_mqtt_system.sh              # Demo script to run all MQTT programs
│   ├── README.md                         # MQTT system documentation
│   ├── GETTING_STARTED.md                # Quick start guide
│   └── DASHBOARD_INTEGRATION.md          # Integration with web dashboard
│
├── notebooks/                  # Jupyter analysis notebooks
│   ├── 03_analyze_data.ipynb            # Data analysis template
│   ├── DFA_2025_Code 11.ipynb           # Course educational material
│   └── README.md                         # Notebooks guide
│
├── docs/                       # Documentation and references
│   ├── DFA_assignment.pdf                       # Assignment specification
│   ├── Pedestrian_inertial_navigation_...pdf   # Reference paper (Koroglu & Yilmaz 2017)
│   ├── API Reference - Sense HAT.pdf            # Hardware reference
│   ├── ASSIGNMENT_GAP_ANALYSIS.md               # What's missing for assignment
│   ├── BAYESIAN_FILTER_README.md                # Bayesian filter documentation
│   ├── QUICK_START_BAYESIAN.md                  # Quick start guide
│   └── SYSTEM_VERIFICATION.md                   # Implementation verification
│
├── templates/                  # HTML templates for Flask
│   └── tracking.html            # Web dashboard UI
│
├── scripts/                    # Shell utilities
│   ├── transfer_to_pi.sh        # Transfer code to Raspberry Pi
│   ├── transfer_mqtt_to_pi.sh   # Transfer MQTT programs to Pi
│   ├── get_data_from_pi.sh      # Download data from Pi
│   └── start_dashboard.sh       # Quick launch dashboard
│
├── output/                     # Generated visualizations
│   └── floor_plan_pdf.png       # Floor plan visualization
│
├── part2_bayesian_navigation_analysis.ipynb  # ⭐ Main analysis notebook (Part 2)
├── NOTEBOOK_README.md           # Description of analysis notebook
├── CALIBRATION.md               # IMU calibration system documentation
├── COORDINATE_SYSTEM.md         # Coordinate system reference
├── start_dashboard_pi.sh        # Start dashboard on Raspberry Pi
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## ✅ Implemented Features

### Part 1: MQTT Data Stream Management System (15%) - ✅ COMPLETE
- ✅ **Program 1:** CPU performance publisher (psutil + paho-mqtt)
- ✅ **Program 2:** SenseHat location publisher (Bayesian predictions)
- ✅ **Program 3:** Subscriber with windowed averaging (2 instances)
- ✅ **Program 4:** Subscriber with Bernoulli sampling (1/3 of data)
- ✅ **Malfunction Detection:** Two detection rules implemented

### Part 2: IMU Pedestrian Navigation (75%) - ⚠️ IN PROGRESS
**Implemented:**
- ✅ **Bayesian Filter** (Section II.C from Koroglu & Yilmaz 2017)
  - Floor plan PDF (3.5m × 6.0m room)
  - Five probability distributions (Equation 5)
  - Mode-seeking with scipy.optimize
  - Real-time position correction
- ✅ **Linear Kalman Filter** (yaw angle filtering)
- ✅ **Particle Filter** (basic implementation)
- ✅ **Web Dashboard** (Flask-based real-time tracking interface)
- ✅ **Naive Dead Reckoning** (baseline comparison)
- ✅ **IMU Calibration System** (automatic heading calibration)
- ✅ **Debug Logging System** (stride-by-stride analysis)

**In Progress:**
- ⚠️ **Jupyter Notebook Analysis** (part2_bayesian_navigation_analysis.ipynb)
  - Notebook structure created (20 cells)
  - Needs to be executed with real data
  - Mathematical equations section needs completion
  - Parameter experiments need to be run
  - Error analysis plots need generation
  - Architecture discussion needs completion

---

## 🚀 Quick Start

### Running on Raspberry Pi

#### 1. Transfer Files to Pi
```bash
# Transfer main code
./scripts/transfer_to_pi.sh

# Transfer MQTT programs (if needed)
./scripts/transfer_mqtt_to_pi.sh
```

#### 2. Start Web Dashboard on Pi
```bash
# SSH to Pi
ssh jdmc@10.111.224.71

# Run dashboard
cd ~/dataFusion
./start_dashboard_pi.sh

# Or manually:
cd ~/dataFusion/src
python3 web_dashboard_advanced.py
```

#### 3. Access Dashboard
Open browser and navigate to:
```
http://10.111.224.71:5001
```

#### 4. Start Tracking
1. Click "START WALKING" button
2. IMU automatically calibrates
3. Press middle button on SenseHat joystick for each stride
4. System tracks position in real-time
5. Click "STOP WALKING" when done

### Running MQTT System

```bash
# On Raspberry Pi, run demo script
cd ~/dataFusion/mqtt
./demo_mqtt_system.sh

# Or start programs individually (see mqtt/README.md)
```

### Local Testing (Without Raspberry Pi)

```bash
# Uses mock SenseHat for local development
cd src
python3 web_dashboard_advanced.py

# Access at: http://localhost:5001
```

---

## 📊 Assignment Status

### Current Completion Estimate: ~85%

| Component | Weight | Status | Completion |
|-----------|--------|--------|-----------|
| **Part 1: MQTT DSMS** | 15% | ✅ Complete | 100% |
| **Part 2: IMU - Code** | 35% | ✅ Complete | 100% |
| **Part 2: IMU - Analysis** | 40% | ⚠️ In Progress | ~60% |
| **Total** | 90% | | **~85%** |

### What's Left (~15%):

#### Jupyter Notebook Analysis (Complete 40% remaining = ~15% of total grade)
- [ ] Execute notebook with real experimental data
- [ ] Complete mathematical equations section (LaTeX)
- [ ] Run parameter sensitivity experiments
- [ ] Generate error analysis plots
- [ ] Complete architecture categorization discussion
- [ ] Add computational cost comparison
- [ ] Write conclusions section

---

## 📝 Assignment Requirements Checklist

### Part 1: MQTT (15%)
- [x] Program 1: CPU publisher (psutil)
- [x] Program 2: Location publisher (Bayesian)
- [x] Program 3: Windowed subscriber (2 instances)
- [x] Program 4: Bernoulli sampling subscriber
- [x] Two malfunction detection rules
- [x] Documentation and usage guides

### Part 2: IMU (75%)

**Code Implementation (35%):**
- [x] Bayesian filter (Section II.C from paper)
- [x] Particle filter
- [x] Linear Kalman filter
- [x] Working Python code
- [x] Well-commented with explanations
- [x] Real-time web dashboard

**Analysis & Documentation (40%):**
- [ ] Jupyter notebook with complete analysis
- [ ] Mathematical equations displayed (LaTeX)
- [ ] Parameter value table
- [ ] Discussion of priors/likelihoods impact
- [ ] Experiments showing parameter effects
- [ ] Error analysis plots
- [ ] Computational cost comparison
- [ ] Architecture categorization (3 types)
- [ ] Common representational format discussion
- [ ] Temporal/spatial alignment explanation
- [ ] Configuration system description
- [ ] Error propagation analysis

---

## 🎯 Next Steps to Complete Assignment

### Priority 1: Run Experiments (2-3 hours)
1. **Collect walking data on Raspberry Pi:**
   - Walk predefined paths (straight line, square, L-shape)
   - Record trajectories with all 4 algorithms
   - Save CSV files from dashboard

2. **Test parameter sensitivity:**
   - Vary heading error (0° to 30°)
   - Vary stride length error (0cm to 30cm)
   - Test floor plan weight values
   - Test wall avoidance effectiveness

### Priority 2: Complete Jupyter Notebook (3-4 hours)
1. **Load experimental data** into notebook
2. **Generate visualizations:**
   - Trajectory plots for all algorithms
   - Error vs parameter plots
   - Computational cost comparisons
   - Architecture diagrams

3. **Write analysis sections:**
   - Mathematical foundation explanation
   - Parameter impact discussion
   - Architecture categorization
   - Error propagation analysis
   - Conclusions and future work

### Priority 3: Final Review (1 hour)
1. Execute all notebook cells
2. Verify all plots are generated
3. Check mathematical equations render correctly
4. Proofread text and explanations
5. Export to PDF for submission

---

## 📚 Key Documentation

- **[NOTEBOOK_README.md](NOTEBOOK_README.md)** - Guide to main analysis notebook
- **[mqtt/README.md](mqtt/README.md)** - MQTT system documentation
- **[mqtt/GETTING_STARTED.md](mqtt/GETTING_STARTED.md)** - MQTT quick start
- **[docs/ASSIGNMENT_GAP_ANALYSIS.md](docs/ASSIGNMENT_GAP_ANALYSIS.md)** - Detailed gap analysis
- **[docs/BAYESIAN_FILTER_README.md](docs/BAYESIAN_FILTER_README.md)** - Algorithm documentation
- **[CALIBRATION.md](CALIBRATION.md)** - IMU calibration system
- **[COORDINATE_SYSTEM.md](COORDINATE_SYSTEM.md)** - Coordinate conventions

---

## 📚 References

1. **Main Paper:** Koroglu, M. T., & Yilmaz, A. (2017). Pedestrian inertial navigation with building floor plans for indoor environments via non-recursive Bayesian filtering. *Proceedings of the ION GNSS+*.
2. **Assignment:** [docs/DFA_assignment.pdf](docs/DFA_assignment.pdf)
3. **SenseHat API:** [docs/API Reference - Sense HAT.pdf](docs/API%20Reference%20-%20Sense%20HAT.pdf)

---

## 🔧 Hardware Requirements

- Raspberry Pi (3 or 4)
- Sense HAT with LSM9DS1 IMU
- Power supply
- WiFi connection
- (Optional) MQTT broker for Part 1

---

## 📦 Dependencies

```bash
pip3 install flask numpy scipy matplotlib pandas sense-hat paho-mqtt psutil jupyter --break-system-packages
```

Or use requirements.txt:
```bash
pip3 install -r requirements.txt --break-system-packages
```

---

## 👥 Team

[Your Name(s) Here]

---

## 📄 License

Educational project for Data Fusion Architectures course, Master SSE 25/26

---

## 🆘 Troubleshooting

### "Module 'sense_hat' not found" (on laptop)
This is normal - SenseHat only works on Raspberry Pi. The code will use mock_sense_hat.py for local testing.

### Dashboard won't start on Pi
```bash
# Check if port 5001 is in use
sudo lsof -i :5001

# Kill existing process if needed
sudo kill -9 <PID>

# Restart dashboard
cd ~/dataFusion/src
python3 web_dashboard_advanced.py
```

### MQTT connection issues
```bash
# Check if mosquitto broker is running
sudo systemctl status mosquitto

# Start broker if needed
sudo systemctl start mosquitto
```

### Can't access dashboard from laptop
1. Ensure Pi and laptop are on same network
2. Check Pi's IP address: `hostname -I`
3. Use Pi's IP in browser: `http://<PI_IP>:5001`
4. Check firewall settings if still can't connect

---

**Last Updated:** 2026-01-08
