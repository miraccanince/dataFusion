# Quick Setup Guide (For Friend Helping with Pi)

## Super Simple - Just 3 Commands!

After cloning this repo on the Raspberry Pi, run:

```bash
cd ~/dataFusion
chmod +x start_dashboard_pi.sh
./start_dashboard_pi.sh
```

That's it! Dashboard will start automatically.

---

## Full Instructions (If Needed)

### 1. SSH to Raspberry Pi
```bash
ssh jdmc@10.49.216.71
# Enter password when asked
```

### 2. Clone Repository
```bash
# Remove old version
rm -rf ~/dataFusion

# Clone fresh
git clone <REPO_URL> ~/dataFusion
cd ~/dataFusion
```

### 3. One-Time Setup (First Time Only)
```bash
# Install MQTT broker
sudo apt-get update
sudo apt-get install -y mosquitto mosquitto-clients
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Install Python dependencies
pip3 install paho-mqtt psutil --break-system-packages
```

### 4. Start Dashboard
```bash
chmod +x start_dashboard_pi.sh
./start_dashboard_pi.sh
```

### 5. Keep Terminal Open
- Dashboard is now running
- Mirac can access it from: **http://10.49.216.71:5001**
- Press **Ctrl+C** when done to stop

---

## What This Dashboard Does

- **Real-time pedestrian tracking** using IMU sensors
- **4 filter algorithms** (Naive, Bayesian, Kalman, Particle)
- **MQTT system control** (Part 1 of assignment - 15%)
- **Floor plan constraints** for indoor navigation

---

## Troubleshooting

**If dashboard won't start:**
```bash
# Check if Python 3 is installed
python3 --version

# Check if Flask is installed
pip3 list | grep Flask

# If not, install:
pip3 install flask --break-system-packages
```

**If MQTT broker not running:**
```bash
sudo systemctl status mosquitto
sudo systemctl start mosquitto
```

**If port 5001 already in use:**
```bash
# Kill existing process
sudo lsof -t -i:5001 | xargs kill -9

# Then start again
./start_dashboard_pi.sh
```

---

## For Mirac (After Friend Starts Dashboard)

On your laptop browser:
```
http://10.49.216.71:5001
```

You should see:
1. **Tracking section** - Start/stop walking, view trajectories
2. **MQTT Control Panel** (scroll down) - Control all MQTT programs

Take screenshots for your report!

---

## When Done

Tell friend to press **Ctrl+C** in the terminal to stop the dashboard.
