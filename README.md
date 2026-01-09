# Pedestrian Navigation System
**Data Fusion Architectures - Master SSE 25/26**

Indoor pedestrian navigation using Raspberry Pi + SenseHat IMU with Bayesian filtering.

---

## Project Structure

```
dataFusion/
├── src/                        # Source code
│   ├── bayesian_filter.py       # Bayesian filter (Equation 5 from paper)
│   ├── kalman_filter.py         # Kalman filter
│   ├── particle_filter.py       # Particle filter
│   ├── web_dashboard_advanced.py # Flask dashboard
│   └── mock_sense_hat.py        # Mock SenseHat for testing
│
├── mqtt/                       # Part 1: MQTT Stream Management
│   ├── mqtt_cpu_publisher.py            # CPU metrics publisher
│   ├── mqtt_location_publisher.py       # Position publisher
│   ├── mqtt_subscriber_windowed.py      # Windowed averaging
│   ├── mqtt_subscriber_bernoulli.py     # Bernoulli sampling
│   ├── malfunction_detection.py         # Detection rules
│   └── README.md
│
├── data/experiments/           # Experimental data (CSV files)
│
├── docs/                       # Documentation
│   ├── DFA_assignment.pdf
│   ├── Pedestrian_inertial_navigation_...pdf   # Reference paper
│   └── BAYESIAN_FILTER_README.md
│
├── templates/                  # HTML templates
│   └── tracking.html
│
├── scripts/                    # Utility scripts
│   ├── transfer_to_pi.sh
│   ├── transfer_mqtt_to_pi.sh
│   └── get_data_from_pi.sh
│
├── part2_bayesian_navigation_analysis.ipynb  # Main analysis notebook
├── terminal1.png, terminal2.png              # MQTT system screenshots
├── trajectory_map_*.png                       # Real tracking visualizations
└── README.md
```

---

## Features

### Part 1: MQTT System (15%)
- CPU performance publisher using psutil
- SenseHat position publisher
- Windowed averaging subscriber (1s and 5s windows)
- Bernoulli sampling subscriber (p=1/3)
- Malfunction detection (temperature > 80°C, memory > 90%)

### Part 2: IMU Navigation (75%)
- **Bayesian Filter:** Non-recursive implementation from Koroglu & Yilmaz 2017
  - Floor plan constraints (3.5m × 6.0m room)
  - Five probability distributions (Equation 5)
  - L-BFGS-B optimization
- **Kalman Filter:** Linear state estimation
- **Particle Filter:** Sequential Monte Carlo (N=100 particles)
- **Web Dashboard:** Real-time tracking visualization
- **Naive Dead Reckoning:** Baseline comparison

---

## Quick Start

### On Raspberry Pi

1. **Transfer files:**
```bash
./scripts/transfer_to_pi.sh
```

2. **Start dashboard:**
```bash
ssh jdmc@10.192.168.71
cd ~/dataFusion
./start_dashboard_pi.sh
```

3. **Access from browser:**
```
http://10.192.168.71:5001
```

4. **Collect data:**
- Click "START WALKING"
- Press middle button on joystick for each stride
- Walk around
- Click "STOP WALKING"
- Download CSV files

### MQTT System

```bash
# On Pi
cd ~/dataFusion/mqtt
./demo_mqtt_system.sh
```

### Local Testing

```bash
cd src
python3 web_dashboard_advanced.py
# Access at http://localhost:5001
```

---

## Analysis Notebook

The main analysis is in `part2_bayesian_navigation_analysis.ipynb`:

- Mathematical foundation (Equation 5 breakdown)
- Parameter configuration
- Architecture comparison (3 categorization dimensions)
- Synthetic experiments (heading error, stride error, wall constraints)
- **Real experimental data** (13 strides from Raspberry Pi)
- Filter performance comparison

To run:
```bash
jupyter notebook part2_bayesian_navigation_analysis.ipynb
```

---

## Dependencies

```bash
pip3 install flask numpy scipy matplotlib pandas sense-hat paho-mqtt psutil jupyter --break-system-packages
```

---

## Hardware

- Raspberry Pi 4
- Sense HAT (LSM9DS1 IMU)
- WiFi connection

---

## References

1. Koroglu, M. T., & Yilmaz, A. (2017). Pedestrian inertial navigation with building floor plans for indoor environments via non-recursive Bayesian filtering.
2. Course assignment: docs/DFA_assignment.pdf

---

## Troubleshooting

**Dashboard won't start:**
```bash
sudo lsof -i :5001
sudo kill -9 <PID>
```

**MQTT issues:**
```bash
sudo systemctl status mosquitto
sudo systemctl start mosquitto
```

**Can't access dashboard from laptop:**
- Check Pi IP: `hostname -I`
- Use correct IP in browser
- Check firewall

---

Last updated: Jan 2026
