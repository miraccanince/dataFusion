"""
Advanced Web Dashboard with Data Comparison
============================================
Access from browser: http://10.111.224.71:5001

NEW FEATURES:
- Compare raw vs filtered sensor data
- Multiple trajectories overlay (naive, Bayesian, particle filter)
- Real-time error metrics
- Side-by-side algorithm comparison
- Parameter tuning sliders

Usage: python3 web_dashboard_advanced.py
"""

from flask import Flask, render_template, jsonify, send_file, request
from sense_hat import SenseHat
import numpy as np
import json
import csv
import io
import time
import threading
from datetime import datetime
from collections import deque
from bayesian_filter import BayesianNavigationFilter, FloorPlanPDF

app = Flask(__name__)
sense = SenseHat()
sense.set_imu_config(True, True, True)

# Global state
stride_count = 0
STRIDE_LENGTH = 0.7

# Auto-stride detection state
auto_walk_active = False
auto_walk_thread = None
auto_walk_lock = threading.Lock()
last_stride_time = 0.0
stride_threshold = 1.2  # Acceleration threshold in g
min_stride_interval = 0.3  # Minimum 0.3s between strides

# Store multiple trajectories for comparison
trajectories = {
    'naive': [],
    'bayesian': [],
    'particle': [],
    'ground_truth': []  # Manual entry by user
}

positions = {
    'naive': {'x': 0.0, 'y': 0.0},
    'bayesian': {'x': 2.0, 'y': 4.0},  # Start at floor plan origin
    'particle': {'x': 0.0, 'y': 0.0}
}

# Sensor data buffers (last 50 readings)
sensor_buffer = {
    'raw': deque(maxlen=50),
    'filtered': deque(maxlen=50),
    'timestamps': deque(maxlen=50)
}

# Simple Kalman filter state
kalman_state = {
    'yaw': 0.0,
    'P': 1.0,  # Covariance
    'Q': 0.01,  # Process noise
    'R': 0.1    # Measurement noise
}

# Initialize Bayesian filter with floor plan
print("Initializing Bayesian Navigation Filter...")
floor_plan = FloorPlanPDF(width_m=20.0, height_m=10.0, resolution=0.1)
bayesian_filter = BayesianNavigationFilter(floor_plan, stride_length=STRIDE_LENGTH)
print("✓ Bayesian filter ready!")

def simple_kalman_filter(measurement, state):
    """Simple 1D Kalman filter for heading"""
    # Prediction
    x_pred = state['yaw']
    P_pred = state['P'] + state['Q']

    # Update
    K = P_pred / (P_pred + state['R'])  # Kalman gain
    x_est = x_pred + K * (measurement - x_pred)
    P_est = (1 - K) * P_pred

    # Update state
    state['yaw'] = x_est
    state['P'] = P_est

    return x_est

def detect_stride(accel_data):
    """
    Detect stride based on acceleration magnitude

    Args:
        accel_data: Accelerometer reading {'x', 'y', 'z'}

    Returns:
        bool: True if stride detected
    """
    global last_stride_time

    # Calculate acceleration magnitude
    accel_mag = np.sqrt(
        accel_data['x']**2 +
        accel_data['y']**2 +
        accel_data['z']**2
    )

    # Detect if magnitude exceeds threshold
    # Also check minimum time between strides (prevents false positives)
    if accel_mag > stride_threshold:
        current_time = time.time()
        if (current_time - last_stride_time) > min_stride_interval:
            last_stride_time = current_time
            return True

    return False

def process_stride_all_algorithms(yaw):
    """Process a detected stride for all algorithms"""
    global stride_count

    # Update all algorithms
    # NAIVE algorithm
    new_x = positions['naive']['x'] + STRIDE_LENGTH * np.sin(yaw)
    new_y = positions['naive']['y'] + STRIDE_LENGTH * np.cos(yaw)
    positions['naive'] = {'x': round(new_x, 3), 'y': round(new_y, 3)}

    trajectories['naive'].append({
        'stride': stride_count,
        'timestamp': datetime.utcnow().isoformat(),
        'x': positions['naive']['x'],
        'y': positions['naive']['y'],
        'heading': round(np.degrees(yaw), 2),
        'algorithm': 'naive'
    })

    # BAYESIAN algorithm
    estimated_pos = bayesian_filter.update(heading=yaw, stride_length=STRIDE_LENGTH)
    positions['bayesian'] = {
        'x': round(estimated_pos['x'], 3),
        'y': round(estimated_pos['y'], 3)
    }

    trajectories['bayesian'].append({
        'stride': stride_count,
        'timestamp': datetime.utcnow().isoformat(),
        'x': positions['bayesian']['x'],
        'y': positions['bayesian']['y'],
        'heading': round(np.degrees(yaw), 2),
        'algorithm': 'bayesian'
    })

    # PARTICLE algorithm (placeholder)
    new_x = positions['particle']['x'] + STRIDE_LENGTH * np.sin(yaw)
    new_y = positions['particle']['y'] + STRIDE_LENGTH * np.cos(yaw)
    positions['particle'] = {'x': round(new_x, 3), 'y': round(new_y, 3)}

    trajectories['particle'].append({
        'stride': stride_count,
        'timestamp': datetime.utcnow().isoformat(),
        'x': positions['particle']['x'],
        'y': positions['particle']['y'],
        'heading': round(np.degrees(yaw), 2),
        'algorithm': 'particle'
    })

    stride_count += 1

    # Visual feedback on SenseHat
    sense.show_message("!", text_colour=[0, 255, 0], scroll_speed=0.05)
    sense.clear()

def auto_walk_monitor():
    """Background thread that monitors for automatic stride detection"""
    global auto_walk_active

    print("🚶 Auto-walk monitor started")

    while auto_walk_active:
        try:
            # Read accelerometer
            accel = sense.get_accelerometer_raw()

            # Detect stride
            if detect_stride(accel):
                # Get current heading (use Kalman filtered yaw)
                orientation = sense.get_orientation_radians()
                raw_yaw = orientation.get('yaw', 0)
                filtered_yaw = simple_kalman_filter(raw_yaw, kalman_state)

                # Process stride for all algorithms
                with auto_walk_lock:
                    process_stride_all_algorithms(filtered_yaw)

                print(f"✓ Stride {stride_count} detected! Position: Bayesian=({positions['bayesian']['x']:.2f}, {positions['bayesian']['y']:.2f})")

            # Sleep to avoid excessive CPU usage
            time.sleep(0.05)  # Check every 50ms

        except Exception as e:
            print(f"Error in auto-walk monitor: {e}")
            time.sleep(0.1)

    print("🛑 Auto-walk monitor stopped")

@app.route('/')
def index():
    return render_template('advanced.html')

@app.route('/api/sensors/raw')
def get_raw_sensors():
    """Get RAW sensor readings"""
    accel = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()
    mag = sense.get_compass_raw()
    orientation = sense.get_orientation_degrees()

    timestamp = datetime.utcnow().isoformat()

    data = {
        'timestamp': timestamp,
        'accelerometer': accel,
        'gyroscope': gyro,
        'magnetometer': mag,
        'orientation': orientation,
        'temperature': round(sense.get_temperature(), 2)
    }

    # Store in buffer
    sensor_buffer['raw'].append(data)
    sensor_buffer['timestamps'].append(timestamp)

    return jsonify(data)

@app.route('/api/sensors/filtered')
def get_filtered_sensors():
    """Get FILTERED sensor readings"""
    # Get raw data
    accel = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()
    orientation = sense.get_orientation_radians()

    # Apply Kalman filter to yaw
    raw_yaw = orientation.get('yaw', 0)
    filtered_yaw = simple_kalman_filter(raw_yaw, kalman_state)

    # Simple moving average for accelerometer
    accel_filtered = {
        'x': round(accel['x'], 4),
        'y': round(accel['y'], 4),
        'z': round(accel['z'], 4)
    }

    data = {
        'timestamp': datetime.utcnow().isoformat(),
        'yaw_raw': round(np.degrees(raw_yaw), 2),
        'yaw_filtered': round(np.degrees(filtered_yaw), 2),
        'accelerometer': accel_filtered,
        'gyroscope': gyro
    }

    sensor_buffer['filtered'].append(data)

    return jsonify(data)

@app.route('/api/sensors/comparison')
def get_sensor_comparison():
    """Get comparison of raw vs filtered sensors over time"""
    return jsonify({
        'raw_buffer': list(sensor_buffer['raw']),
        'filtered_buffer': list(sensor_buffer['filtered']),
        'timestamps': list(sensor_buffer['timestamps'])
    })

@app.route('/api/stride/<algorithm>', methods=['POST'])
def record_stride(algorithm):
    """Record a stride using specified algorithm"""
    global stride_count

    data = request.json or {}
    use_filtered = data.get('use_filtered', False)

    # Get heading
    if use_filtered:
        yaw = kalman_state['yaw']
    else:
        orientation = sense.get_orientation_radians()
        yaw = orientation.get('yaw', 0)

    # Update position based on algorithm
    if algorithm == 'naive':
        # Simple dead reckoning
        new_x = positions['naive']['x'] + STRIDE_LENGTH * np.sin(yaw)
        new_y = positions['naive']['y'] + STRIDE_LENGTH * np.cos(yaw)
        positions['naive'] = {'x': round(new_x, 3), 'y': round(new_y, 3)}

        trajectories['naive'].append({
            'stride': stride_count,
            'timestamp': datetime.utcnow().isoformat(),
            'x': positions['naive']['x'],
            'y': positions['naive']['y'],
            'heading': round(np.degrees(yaw), 2),
            'algorithm': 'naive'
        })

    elif algorithm == 'bayesian':
        # BAYESIAN FILTER: Implement non-recursive Bayesian filter (Equation 5)
        # Uses floor plan constraints to correct heading errors

        # Update Bayesian filter with IMU measurements
        estimated_pos = bayesian_filter.update(heading=yaw, stride_length=STRIDE_LENGTH)

        positions['bayesian'] = {
            'x': round(estimated_pos['x'], 3),
            'y': round(estimated_pos['y'], 3)
        }

        trajectories['bayesian'].append({
            'stride': stride_count,
            'timestamp': datetime.utcnow().isoformat(),
            'x': positions['bayesian']['x'],
            'y': positions['bayesian']['y'],
            'heading': round(np.degrees(yaw), 2),
            'algorithm': 'bayesian'
        })

    elif algorithm == 'particle':
        # TODO: Implement particle filter (placeholder)
        new_x = positions['particle']['x'] + STRIDE_LENGTH * np.sin(yaw)
        new_y = positions['particle']['y'] + STRIDE_LENGTH * np.cos(yaw)
        positions['particle'] = {'x': round(new_x, 3), 'y': round(new_y, 3)}

        trajectories['particle'].append({
            'stride': stride_count,
            'timestamp': datetime.utcnow().isoformat(),
            'x': positions['particle']['x'],
            'y': positions['particle']['y'],
            'heading': round(np.degrees(yaw), 2),
            'algorithm': 'particle'
        })

    stride_count += 1

    # Visual feedback
    sense.show_message("!", text_colour=[0, 255, 0], scroll_speed=0.05)
    sense.clear()

    return jsonify({
        'success': True,
        'stride': stride_count,
        'position': positions[algorithm],
        'algorithm': algorithm
    })

@app.route('/api/trajectories')
def get_all_trajectories():
    """Get all trajectories for comparison"""
    return jsonify({
        'naive': trajectories['naive'],
        'bayesian': trajectories['bayesian'],
        'particle': trajectories['particle'],
        'ground_truth': trajectories['ground_truth'],
        'stride_count': stride_count
    })

@app.route('/api/ground_truth', methods=['POST'])
def set_ground_truth():
    """Manually set ground truth position"""
    data = request.json
    trajectories['ground_truth'].append({
        'stride': stride_count,
        'timestamp': datetime.utcnow().isoformat(),
        'x': data.get('x', 0),
        'y': data.get('y', 0),
        'note': data.get('note', '')
    })
    return jsonify({'success': True})

@app.route('/api/errors')
def get_errors():
    """Calculate errors compared to ground truth"""
    if not trajectories['ground_truth']:
        return jsonify({'error': 'No ground truth data'})

    # Get latest ground truth
    gt = trajectories['ground_truth'][-1]

    errors = {}
    for algo in ['naive', 'bayesian', 'particle']:
        if trajectories[algo]:
            latest = trajectories[algo][-1]
            error = np.sqrt((latest['x'] - gt['x'])**2 + (latest['y'] - gt['y'])**2)
            errors[algo] = {
                'distance_error': round(error, 3),
                'x_error': round(abs(latest['x'] - gt['x']), 3),
                'y_error': round(abs(latest['y'] - gt['y']), 3)
            }

    return jsonify(errors)

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset all data"""
    global stride_count, positions, trajectories, bayesian_filter

    stride_count = 0
    positions = {
        'naive': {'x': 0.0, 'y': 0.0},
        'bayesian': {'x': 0.0, 'y': 0.0},
        'particle': {'x': 0.0, 'y': 0.0}
    }
    trajectories = {
        'naive': [],
        'bayesian': [],
        'particle': [],
        'ground_truth': []
    }
    sensor_buffer['raw'].clear()
    sensor_buffer['filtered'].clear()
    sensor_buffer['timestamps'].clear()

    # Reset Bayesian filter to start position
    bayesian_filter.reset(x=2.0, y=4.0)

    sense.clear()
    return jsonify({'success': True})

@app.route('/api/download/<algorithm>')
def download_trajectory(algorithm):
    """Download specific algorithm trajectory"""
    if algorithm not in trajectories or not trajectories[algorithm]:
        return jsonify({'error': 'No data'}), 404

    output = io.StringIO()
    fieldnames = trajectories[algorithm][0].keys()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(trajectories[algorithm])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode())
    mem.seek(0)

    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{algorithm}_trajectory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/parameters', methods=['POST'])
def update_parameters():
    """Update algorithm parameters"""
    global STRIDE_LENGTH, kalman_state, bayesian_filter

    data = request.json

    if 'stride_length' in data:
        STRIDE_LENGTH = float(data['stride_length'])
        # Update Bayesian filter stride length
        bayesian_filter.stride_length = STRIDE_LENGTH

    if 'kalman_Q' in data:
        kalman_state['Q'] = float(data['kalman_Q'])

    if 'kalman_R' in data:
        kalman_state['R'] = float(data['kalman_R'])

    return jsonify({
        'success': True,
        'stride_length': STRIDE_LENGTH,
        'kalman_Q': kalman_state['Q'],
        'kalman_R': kalman_state['R']
    })

@app.route('/api/floor_plan')
def get_floor_plan():
    """Get floor plan data for visualization"""
    return jsonify({
        'width_m': floor_plan.width_m,
        'height_m': floor_plan.height_m,
        'resolution': floor_plan.resolution,
        'grid': floor_plan.grid.tolist()  # Convert numpy array to list for JSON
    })

@app.route('/api/auto_walk/start', methods=['POST'])
def start_auto_walk():
    """Start automatic stride detection"""
    global auto_walk_active, auto_walk_thread

    if auto_walk_active:
        return jsonify({'success': False, 'message': 'Auto-walk already active'})

    # Parse optional parameters
    data = request.json or {}
    if 'threshold' in data:
        global stride_threshold
        stride_threshold = float(data['threshold'])

    # Start background thread
    auto_walk_active = True
    auto_walk_thread = threading.Thread(target=auto_walk_monitor, daemon=True)
    auto_walk_thread.start()

    return jsonify({
        'success': True,
        'message': 'Auto-walk started',
        'threshold': stride_threshold,
        'min_interval': min_stride_interval
    })

@app.route('/api/auto_walk/stop', methods=['POST'])
def stop_auto_walk():
    """Stop automatic stride detection"""
    global auto_walk_active, auto_walk_thread

    if not auto_walk_active:
        return jsonify({'success': False, 'message': 'Auto-walk not active'})

    # Stop background thread
    auto_walk_active = False

    # Wait for thread to finish (with timeout)
    if auto_walk_thread and auto_walk_thread.is_alive():
        auto_walk_thread.join(timeout=2.0)

    return jsonify({
        'success': True,
        'message': 'Auto-walk stopped'
    })

@app.route('/api/auto_walk/status')
def get_auto_walk_status():
    """Get auto-walk status"""
    return jsonify({
        'active': auto_walk_active,
        'stride_count': stride_count,
        'threshold': stride_threshold,
        'min_interval': min_stride_interval,
        'last_stride_time': last_stride_time
    })

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 ADVANCED Dashboard with Auto-Stride Detection")
    print("=" * 70)
    print(f"\n📱 Access: http://10.111.224.71:5001")
    print(f"\n✨ Features:")
    print(f"   - 🚶 AUTO-WALK MODE: Real-time stride detection while walking!")
    print(f"   - Raw vs Filtered sensor comparison")
    print(f"   - Multiple algorithm trajectories:")
    print(f"     • Naive Dead Reckoning")
    print(f"     • ✓ Bayesian Filter (Equation 5 - Koroglu & Yilmaz 2017)")
    print(f"     • Particle Filter (TODO)")
    print(f"   - Real-time error metrics")
    print(f"   - Parameter tuning")
    print(f"   - Ground truth comparison")
    print(f"   - Floor plan constraints (20m × 10m L-shaped hallway)")
    print(f"\n🎒 Usage:")
    print(f"   1. Put Raspberry Pi in backpack")
    print(f"   2. Access dashboard from laptop browser")
    print(f"   3. Click 'Start Walking' button")
    print(f"   4. Walk naturally - strides detected automatically!")
    print(f"   5. Watch real-time trajectory on dashboard")
    print("\n" + "=" * 70)

    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
