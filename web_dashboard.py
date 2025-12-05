"""
Web Dashboard for Raspberry Pi Pedestrian Navigation
=====================================================
Access from browser: http://10.111.224.71:5000

Features:
- Live sensor readings
- Start/Stop data collection
- Visualize trajectory in real-time
- Download CSV files
- Control LED matrix

Usage on Raspberry Pi:
    python3 web_dashboard.py

Then open browser on any device: http://10.111.224.71:5000
"""

from flask import Flask, render_template, jsonify, send_file, request
from sense_hat import SenseHat
import numpy as np
import json
import csv
import io
from datetime import datetime
import threading
import time

app = Flask(__name__)
sense = SenseHat()
sense.set_imu_config(True, True, True)

# Global state
collecting_data = False
stride_count = 0
position = {'x': 0.0, 'y': 0.0}
trajectory = []
sensor_history = []
STRIDE_LENGTH = 0.7

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sensors')
def get_sensors():
    """Get current sensor readings"""
    accel = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()
    mag = sense.get_compass_raw()
    orientation = sense.get_orientation_degrees()

    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'accelerometer': accel,
        'gyroscope': gyro,
        'magnetometer': mag,
        'orientation': orientation,
        'temperature': round(sense.get_temperature(), 2),
        'humidity': round(sense.get_humidity(), 2),
        'pressure': round(sense.get_pressure(), 2)
    })

@app.route('/api/position')
def get_position():
    """Get current position and trajectory"""
    return jsonify({
        'current': position,
        'trajectory': trajectory,
        'stride_count': stride_count
    })

@app.route('/api/stride', methods=['POST'])
def record_stride():
    """Record a stride (button press)"""
    global stride_count, position, trajectory

    # Get heading
    orientation = sense.get_orientation_radians()
    yaw = orientation.get('yaw', 0)

    # Update position (naive dead reckoning)
    new_x = position['x'] + STRIDE_LENGTH * np.sin(yaw)
    new_y = position['y'] + STRIDE_LENGTH * np.cos(yaw)

    stride_count += 1
    position = {'x': round(new_x, 3), 'y': round(new_y, 3)}

    trajectory.append({
        'stride': stride_count,
        'timestamp': datetime.utcnow().isoformat(),
        'x': position['x'],
        'y': position['y'],
        'heading': round(np.degrees(yaw), 2)
    })

    # Visual feedback
    sense.show_message("!", text_colour=[0, 255, 0], scroll_speed=0.05)
    sense.clear()

    return jsonify({'success': True, 'position': position, 'stride': stride_count})

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset position and data"""
    global stride_count, position, trajectory, sensor_history
    stride_count = 0
    position = {'x': 0.0, 'y': 0.0}
    trajectory = []
    sensor_history = []
    sense.clear()
    return jsonify({'success': True})

@app.route('/api/download/trajectory')
def download_trajectory():
    """Download trajectory as CSV"""
    if not trajectory:
        return jsonify({'error': 'No data to download'}), 404

    output = io.StringIO()
    fieldnames = ['stride', 'timestamp', 'x', 'y', 'heading']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(trajectory)

    mem = io.BytesIO()
    mem.write(output.getvalue().encode())
    mem.seek(0)

    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'trajectory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/led/pattern', methods=['POST'])
def set_led_pattern():
    """Set LED pattern"""
    data = request.json
    pattern = data.get('pattern', 'clear')

    if pattern == 'clear':
        sense.clear()
    elif pattern == 'heading':
        # Show heading direction
        orientation = sense.get_orientation_radians()
        yaw = orientation.get('yaw', 0)
        direction_idx = int((yaw / (np.pi / 4)) % 8)

        arrow_positions = {
            0: [(3, 0), (4, 0)],  # North
            1: [(6, 0), (7, 1)],  # NE
            2: [(7, 3), (7, 4)],  # East
            3: [(6, 7), (7, 6)],  # SE
            4: [(3, 7), (4, 7)],  # South
            5: [(0, 6), (1, 7)],  # SW
            6: [(0, 3), (0, 4)],  # West
            7: [(0, 1), (1, 0)],  # NW
        }

        sense.clear()
        for pos in arrow_positions.get(direction_idx, []):
            sense.set_pixel(pos[0], pos[1], (255, 255, 0))

    return jsonify({'success': True})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Web Dashboard")
    print("=" * 60)
    print(f"\n📱 Access from browser:")
    print(f"   http://10.111.224.71:5000")
    print(f"   http://localhost:5000 (on Pi)")
    print(f"\n⚙️  Features:")
    print(f"   - Live sensor readings")
    print(f"   - Position tracking")
    print(f"   - Trajectory visualization")
    print(f"   - CSV download")
    print(f"   - LED control")
    print("\n" + "=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
