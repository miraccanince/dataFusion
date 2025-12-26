# MQTT Data Stream Management System
**Part 1 - 15% of Final Grade**

Complete implementation of all required MQTT programs for the DFA assignment.

---

## 📋 Programs Implemented

### Program 1: CPU Performance Publisher
**File:** `mqtt_cpu_publisher.py`

Publishes CPU performance data using `paho-mqtt` and `psutil`.

**Metrics Published:**
- CPU usage (overall and per-core)
- CPU frequency (current, min, max)
- CPU temperature (Raspberry Pi specific)
- Memory usage (total, available, percent)
- System load average
- Process count
- Timestamps (ISO format)

**Publishing:** Every 10ms (if possible)

**Usage:**
```bash
# Default (localhost, 10ms interval)
python3 mqtt_cpu_publisher.py

# Custom broker and interval
python3 mqtt_cpu_publisher.py --broker 10.111.224.71 --interval 10

# Run for specific duration
python3 mqtt_cpu_publisher.py --duration 60  # 60 seconds
```

---

### Program 2: SenseHAT Location Publisher
**File:** `mqtt_location_publisher.py`

Publishes predicted location from Bayesian algorithm.

**Data Published:**
- Raw IMU data (accelerometer, gyroscope, magnetometer)
- Orientation (pitch, roll, yaw in degrees and radians)
- Bayesian filter position estimate (x, y)
- Naive dead reckoning position (for comparison)
- Stride count and detection
- Timestamps (ISO format)

**Publishing:** Every 10ms (if possible)

**Usage:**
```bash
# Default settings
python3 mqtt_location_publisher.py

# Custom broker and stride length
python3 mqtt_location_publisher.py --broker 10.111.224.71 --stride 0.75

# Custom interval
python3 mqtt_location_publisher.py --interval 20  # 20ms
```

---

### Program 3: Windowed Subscriber
**File:** `mqtt_subscriber_windowed.py`

Subscribes to CPU performance data with windowed averaging.

**Features:**
- Configurable time window
- Real-time statistics (mean, std, min, max)
- Automatic cleanup of old data
- Support for multiple instances

**Metrics Computed:**
- CPU usage statistics
- Memory usage statistics
- Temperature statistics (if available)
- Load average statistics

**Usage:**
```bash
# Instance 1: 1-second window
python3 mqtt_subscriber_windowed.py --window 1.0

# Instance 2: 5-second window (run in another terminal)
python3 mqtt_subscriber_windowed.py --window 5.0

# Custom broker
python3 mqtt_subscriber_windowed.py --window 2.0 --broker 10.111.224.71
```

---

### Program 4: Bernoulli Sampling Subscriber
**File:** `mqtt_subscriber_bernoulli.py`

Subscribes with naive Bernoulli sampling (uses ~1/3 of data points).

**Bernoulli Sampling:**
- Each message has probability p of being sampled
- p = 1/3 ≈ 0.33 (assignment requirement)
- Unbiased estimator: E[sample mean] = population mean
- Reduces computational load while maintaining accuracy

**Features:**
- Configurable sampling probability
- Same statistics as windowed subscriber
- Sampling efficiency tracking
- Demonstrates data reduction techniques

**Usage:**
```bash
# Default: p=1/3, 5-second window
python3 mqtt_subscriber_bernoulli.py

# Custom probability
python3 mqtt_subscriber_bernoulli.py --probability 0.25  # 25% sampling

# Custom window
python3 mqtt_subscriber_bernoulli.py --window 10.0
```

---

### Malfunction Detection
**File:** `malfunction_detection.py`

Two simple rules to detect Raspberry Pi malfunctioning.

**Rule 1: High Temperature**
- Threshold: CPU > 80°C
- Duration: Sustained for >10 seconds
- Indicates: Thermal throttling risk, potential shutdown

**Rule 2: Memory Exhaustion**
- Threshold: Memory > 90%
- Duration: Sustained for >10 seconds
- Indicates: Out-of-memory risk, potential freeze/crash

**Alerts Published to:** `dataFusion/alerts/malfunction`

**Usage:**
```bash
python3 malfunction_detection.py --broker 10.111.224.71
```

---

## 🚀 Quick Start

### 1. Install MQTT Broker (on Raspberry Pi)
```bash
# Install Mosquitto
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients

# Start broker
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Test broker
mosquitto_sub -h localhost -t test
```

### 2. Install Python Dependencies
```bash
pip3 install paho-mqtt psutil numpy
```

### 3. Run Complete Test

**Terminal 1: Start broker (if not running)**
```bash
mosquitto -v  # Verbose mode for debugging
```

**Terminal 2: Start CPU publisher**
```bash
python3 mqtt_cpu_publisher.py --broker localhost
```

**Terminal 3: Start location publisher (requires SenseHat)**
```bash
python3 mqtt_location_publisher.py --broker localhost
```

**Terminal 4: Start windowed subscriber (1s window)**
```bash
python3 mqtt_subscriber_windowed.py --broker localhost --window 1.0
```

**Terminal 5: Start windowed subscriber (5s window)**
```bash
python3 mqtt_subscriber_windowed.py --broker localhost --window 5.0
```

**Terminal 6: Start Bernoulli subscriber**
```bash
python3 mqtt_subscriber_bernoulli.py --broker localhost
```

**Terminal 7: Start malfunction detector**
```bash
python3 malfunction_detection.py --broker localhost
```

---

## 📡 MQTT Topics

| Topic | Publisher | Subscribers | Description |
|-------|-----------|-------------|-------------|
| `dataFusion/cpu/performance` | Program 1 | Program 3, 4, Malfunction | CPU metrics |
| `dataFusion/cpu/status` | Program 1 | - | Publisher status |
| `dataFusion/location/imu` | Program 2 | - | Raw IMU data |
| `dataFusion/location/position` | Program 2 | - | Position estimates |
| `dataFusion/location/status` | Program 2 | - | Publisher status |
| `dataFusion/alerts/malfunction` | Malfunction | - | Critical alerts |

---

## 🧪 Testing Scenarios

### Scenario 1: Normal Operation
1. Start all publishers and subscribers
2. Observe data flow
3. Verify windowed averaging works correctly
4. Confirm Bernoulli sampling rate ≈33%

### Scenario 2: High Load Test
1. Run CPU-intensive task on Raspberry Pi
```bash
# Stress test
stress --cpu 4 --timeout 60s
```
2. Observe CPU usage spikes in subscribers
3. Check if malfunction detection triggers

### Scenario 3: Memory Test
1. Allocate large memory
```bash
# Allocate 1GB
stress --vm 1 --vm-bytes 1G --timeout 30s
```
2. Observe memory usage
3. Verify memory exhaustion detection

---

## 📊 Expected Output

### CPU Publisher
```
======================================================================
MQTT CPU Performance Publisher
======================================================================
Broker: localhost:1883
Topic: dataFusion/cpu/performance
Interval: 10.0ms
Duration: Infinite
======================================================================

✓ Connected to MQTT broker at localhost:1883
✓ Publishing CPU metrics (Ctrl+C to stop)...

Published 100 messages | CPU: 45.2% | Memory: 62.3%
Published 200 messages | CPU: 47.1% | Memory: 62.5%
...
```

### Windowed Subscriber
```
======================================================================
Windowed Statistics (Window: 1.0s)
======================================================================
Messages received: 1234
Timestamp: 2025-12-27 00:15:32
----------------------------------------------------------------------

CPU Usage (%):
  Samples:    100
  Mean:      45.32%  ±3.45
  Range:     38.20% - 52.10%

Memory Usage (%):
  Samples:    100
  Mean:      62.45%  ±0.82
  Range:     61.10% - 64.20%
```

### Bernoulli Subscriber
```
======================================================================
Bernoulli Sampling Statistics (p=0.333, Window: 5.0s)
======================================================================
Total messages:    3000
Sampled:           1005 (33.5%)
Rejected:          1995
Expected rate:     33.3%
```

### Malfunction Detector
```
🔍 Malfunction Detection Rules:
   1. High Temperature: CPU > 80°C for 10s
   2. Memory Exhaustion: Memory > 90% for 10s

✓ Monitoring started...

⚠ WARNING: High temperature detected (82.3°C)
🚨 ALERT PUBLISHED: TEMPERATURE
   {
     "current_temperature": 82.3,
     "threshold": 80.0,
     "recommendation": "Check cooling system..."
   }
```

---

## 🎯 Assignment Requirements Met

- ✅ **Program 1:** CPU performance publisher with psutil (every 10ms, timestamped)
- ✅ **Program 2:** SenseHAT location publisher (Bayesian predictions, every 10ms)
- ✅ **Program 3:** Windowed subscriber (2 instances with different windows)
- ✅ **Program 4:** Bernoulli sampling subscriber (1/3 of data, same windows)
- ✅ **Finally:** Two malfunction detection rules (temperature + memory)

**All requirements for Part 1 (15%) are complete!**

---

## 💡 Tips

1. **Broker not running?**
   ```bash
   sudo systemctl status mosquitto
   sudo systemctl start mosquitto
   ```

2. **Connection refused?**
   - Check firewall: `sudo ufw allow 1883`
   - Check broker config: `/etc/mosquitto/mosquitto.conf`

3. **Too much console output?**
   - Increase stats interval in code
   - Redirect output: `python3 program.py > output.log`

4. **Testing without SenseHat?**
   - Use mock data in `mqtt_location_publisher.py`
   - Or only test Programs 1, 3, 4, and malfunction detection

---

## 📁 File Structure

```
mqtt/
├── mqtt_cpu_publisher.py          # Program 1
├── mqtt_location_publisher.py     # Program 2
├── mqtt_subscriber_windowed.py    # Program 3
├── mqtt_subscriber_bernoulli.py   # Program 4
├── malfunction_detection.py       # Malfunction rules
└── README.md                       # This file
```

---

## 🔗 References

- paho-mqtt: https://pypi.org/project/paho-mqtt/
- psutil: https://pypi.org/project/psutil/
- Mosquitto: https://mosquitto.org/
- MQTT Protocol: https://mqtt.org/

---

**Assignment: Part 1 - Data Stream Management System (15%)**
**Status: ✅ COMPLETE**
