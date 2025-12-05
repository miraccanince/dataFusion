# 🌐 Web Dashboard - Quick Start Guide

## ✨ What You Get

A **beautiful web interface** to control your Raspberry Pi from any browser!

**Features:**
- 📊 Live sensor readings (refreshes every second)
- 📍 Real-time position tracking
- 🗺️ Interactive trajectory visualization
- ➕ Record strides with button click
- 💾 Download CSV files
- 🧭 Show heading direction on LED matrix
- 📱 Works on phone, tablet, or computer

---

## 🚀 How to Start

### Option 1: Start from Your Computer (Recommended)

```bash
ssh jdmc@10.111.224.71 "cd ~/dataFusion && python3 web_dashboard.py"
```

### Option 2: Start on the Pi Directly

```bash
ssh jdmc@10.111.224.71
cd ~/dataFusion
python3 web_dashboard.py
```

---

## 📱 Access the Dashboard

Once started, open your browser and go to:

```
http://10.111.224.71:5000
```

**Works from:**
- ✅ Your Mac
- ✅ Your phone (if on same WiFi)
- ✅ Any device on the same network

---

## 🎯 How to Use

### 1. Record Data
1. Open dashboard in browser
2. Click **"Record Stride"** button
3. Walk one step
4. Repeat
5. Watch trajectory update in real-time!

### 2. View Sensors
- See live accelerometer, gyroscope, magnetometer
- Watch heading angle change
- Monitor temperature, humidity, pressure

### 3. Visualize Path
- Interactive chart shows your walking path
- Click and drag to zoom
- See exact x,y coordinates

### 4. Download Data
- Click **"Download CSV"** button
- Analyze in Excel or Jupyter
- Contains: stride number, timestamp, x, y, heading

### 5. LED Control
- Click **"Show Heading"** - displays direction on LED matrix
- Click **"Clear LED"** - turns off LEDs

---

## 🛑 How to Stop

Press `Ctrl+C` in the terminal where it's running

Or run:
```bash
ssh jdmc@10.111.224.71 "pkill -f web_dashboard.py"
```

---

## 🐛 Troubleshooting

### Can't access http://10.111.224.71:5000 ?

1. Check if dashboard is running:
   ```bash
   ssh jdmc@10.111.224.71 "ps aux | grep web_dashboard"
   ```

2. Check if port 5000 is open:
   ```bash
   ssh jdmc@10.111.224.71 "sudo lsof -i :5000"
   ```

3. Try from Pi itself:
   ```bash
   curl http://localhost:5000
   ```

### Firewall blocking?

On the Pi:
```bash
sudo ufw allow 5000
```

---

## 💡 Advanced Usage

### Run in Background (keeps running when you disconnect SSH)

```bash
ssh jdmc@10.111.224.71 "cd ~/dataFusion && nohup python3 web_dashboard.py > dashboard.log 2>&1 &"
```

View logs:
```bash
ssh jdmc@10.111.224.71 "tail -f ~/dataFusion/dashboard.log"
```

Stop background process:
```bash
ssh jdmc@10.111.224.71 "pkill -f web_dashboard"
```

---

## 📸 Screenshot of Dashboard

The dashboard includes:

```
┌─────────────────────────────────────────────────────┐
│  🚶 Pedestrian Navigation Dashboard                 │
├──────────────┬──────────────┬──────────────────────┤
│ 📍 Position  │ 📊 Sensors   │ ⚙️ Controls         │
│              │              │                      │
│ X: 2.50 m    │ Yaw: 45°     │ [Record Stride]     │
│ Y: 1.20 m    │ Pitch: 2°    │ [Reset]             │
│ Strides: 5   │ Roll: 1°     │ [Download CSV]      │
│              │ |a|: 1.02g   │ [Show Heading]      │
│ [Actions]    │ Temperature  │ [Clear LED]         │
├──────────────┴──────────────┴──────────────────────┤
│  🗺️ Trajectory Map                                 │
│  [Interactive Chart showing walking path]           │
└─────────────────────────────────────────────────────┘
```

---

## 🎓 For Your Assignment

This dashboard helps with:

**Part 1 (DSMS):**
- Real-time data streaming
- Web-based monitoring
- Data export functionality

**Part 2 (IMU):**
- Live sensor visualization
- Position tracking
- Trajectory analysis
- CSV export for Jupyter analysis

---

## 🔗 Quick Links

- Dashboard: http://10.111.224.71:5000
- SSH: `ssh jdmc@10.111.224.71`
- Files: `~/dataFusion/`

**Enjoy your web-based navigation system!** 🚀
