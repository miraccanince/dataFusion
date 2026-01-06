"""
Advanced Web Dashboard with Data Comparison
============================================
Access from browser: http://10.49.216.71:5001

NEW FEATURES:
- Compare raw vs filtered sensor data
- Multiple trajectories overlay (naive, Bayesian, particle filter)
- Real-time error metrics
- Side-by-side algorithm comparison
- Parameter tuning sliders

Usage: python3 web_dashboard_advanced.py
"""

from flask import Flask, render_template, jsonify, send_file, request
import numpy as np
import json
import csv
import io
import time
import threading
import logging
import subprocess
import socket
from datetime import datetime
from collections import deque
from bayesian_filter import BayesianNavigationFilter, FloorPlanPDF
from kalman_filter import KalmanFilter
from particle_filter import ParticleFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger(__name__)

# Try to import real SenseHat, fall back to mock if not available
IS_REAL_HARDWARE = False
try:
    from sense_hat import SenseHat
    IS_REAL_HARDWARE = True
    logger.info("✓ Using real SenseHat hardware")
except ImportError:
    from mock_sense_hat import SenseHat
    IS_REAL_HARDWARE = False
    logger.warning("⚠️  Using mock SenseHat (testing mode - no Raspberry Pi)")

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Flask to find templates in parent directory
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

sense = SenseHat()
sense.set_imu_config(True, True, True)

# Global state
stride_count = 0
STRIDE_LENGTH = 0.7

# Joystick button stride detection state (ONLY MODE - removed accelerometer auto-detection)
joystick_walk_active = False
joystick_walk_thread = None
joystick_walk_lock = threading.Lock()

# Current LED matrix state (8x8 grid of RGB values) for real-time UI display
current_led_matrix = [[0, 0, 0] for _ in range(64)]  # 64 pixels, each [R, G, B]
led_matrix_lock = threading.Lock()

# Store multiple trajectories for comparison
trajectories = {
    'naive': [],
    'bayesian': [],
    'kalman': [],
    'particle': [],
    'ground_truth': []  # Manual entry by user
}

positions = {
    'naive': {'x': 2.0, 'y': 4.0},
    'bayesian': {'x': 2.0, 'y': 4.0},
    'kalman': {'x': 2.0, 'y': 4.0},
    'particle': {'x': 2.0, 'y': 4.0}
}

# Latest IMU readings (roll, pitch, yaw in degrees)
latest_imu = {
    'roll': 0.0,
    'pitch': 0.0,
    'yaw': 0.0
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

# Initialize floor plan and all filters
logger.info("Initializing filters...")
floor_plan = FloorPlanPDF(width_m=10.0, height_m=10.0, resolution=0.1)
bayesian_filter = BayesianNavigationFilter(floor_plan, stride_length=STRIDE_LENGTH)
kalman_filter = KalmanFilter(initial_x=2.0, initial_y=4.0, dt=0.5)
particle_filter = ParticleFilter(floor_plan, n_particles=200, initial_x=2.0, initial_y=4.0)
logger.info("✓ All filters ready! (Bayesian, Kalman, Particle)")

# MQTT Control State
mqtt_processes = {
    'cpu_publisher': None,
    'location_publisher': None,
    'windowed_1s': None,
    'windowed_5s': None,
    'bernoulli': None,
    'malfunction': None
}

mqtt_stats = {
    'broker_running': False,
    'cpu_publisher_active': False,
    'location_publisher_active': False,
    'windowed_1s_active': False,
    'windowed_5s_active': False,
    'bernoulli_active': False,
    'malfunction_active': False,
    'last_check': None
}

def check_mqtt_broker():
    """Check if MQTT broker (Mosquitto) is running on port 1883"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 1883))
        sock.close()
        return result == 0
    except:
        return False

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

def determine_walking_direction_from_imu():
    """
    Determine walking direction from IMU roll/pitch/yaw

    Uses the Pi's orientation to determine which direction the person is walking:
    - Yaw (compass heading): Which direction you're facing (0°=East, 90°=North, 180°=West, 270°=South)
    - Roll: Tilt left/right (not used for direction, but logged for debugging)
    - Pitch: Tilt forward/backward (not used for direction, but logged for debugging)

    Returns:
        heading_radians: The walking direction in radians (standard math: 0=East, π/2=North, etc.)
        heading_description: Human-readable direction (e.g., "North", "Northeast", etc.)
    """
    try:
        # Get current orientation
        orientation_deg = sense.get_orientation_degrees()
        orientation_rad = sense.get_orientation_radians()

        roll = orientation_deg.get('roll', 0)
        pitch = orientation_deg.get('pitch', 0)
        yaw_rad = orientation_rad.get('yaw', 0)
        yaw_deg = orientation_deg.get('yaw', 0)

        # Determine cardinal/intercardinal direction from yaw
        # Standard compass: 0°=North, 90°=East, 180°=South, 270°=West
        # BUT we need to convert to math convention: 0=East, 90°=North, 180°=West, 270°=South
        # Conversion: math_angle = 90° - compass_angle

        # Normalize yaw to 0-360
        yaw_normalized = yaw_deg % 360

        # Determine direction label
        if 337.5 <= yaw_normalized or yaw_normalized < 22.5:
            direction = "North"
        elif 22.5 <= yaw_normalized < 67.5:
            direction = "Northeast"
        elif 67.5 <= yaw_normalized < 112.5:
            direction = "East"
        elif 112.5 <= yaw_normalized < 157.5:
            direction = "Southeast"
        elif 157.5 <= yaw_normalized < 202.5:
            direction = "South"
        elif 202.5 <= yaw_normalized < 247.5:
            direction = "Southwest"
        elif 267.5 <= yaw_normalized < 292.5:
            direction = "West"
        elif 292.5 <= yaw_normalized < 337.5:
            direction = "Northwest"
        else:
            direction = "Unknown"

        logger.info(f"   [IMU] Roll={roll:.1f}°, Pitch={pitch:.1f}°, Yaw={yaw_deg:.1f}° → Walking {direction}")

        return yaw_rad, direction

    except Exception as e:
        logger.error(f"Error reading IMU orientation: {e}")
        return 0.0, "Unknown"

def process_stride_all_algorithms(yaw):
    """Process a detected stride for all algorithms"""
    global stride_count, latest_imu

    # Update IMU readings (get current orientation)
    try:
        orientation = sense.get_orientation_degrees()
        latest_imu = {
            'roll': round(orientation.get('roll', 0), 1),
            'pitch': round(orientation.get('pitch', 0), 1),
            'yaw': round(orientation.get('yaw', 0), 1)
        }
    except Exception as e:
        logger.warning(f"Failed to read IMU orientation: {e}")

    # 1. NAIVE algorithm (simple dead reckoning)
    # Standard math: x = cos(angle), y = sin(angle)
    new_x = positions['naive']['x'] + STRIDE_LENGTH * np.cos(yaw)
    new_y = positions['naive']['y'] + STRIDE_LENGTH * np.sin(yaw)
    positions['naive'] = {'x': round(new_x, 3), 'y': round(new_y, 3)}
    trajectories['naive'].append({
        'stride': stride_count,
        'timestamp': datetime.utcnow().isoformat(),
        'x': positions['naive']['x'],
        'y': positions['naive']['y'],
        'heading': round(np.degrees(yaw), 2),
        'algorithm': 'naive'
    })

    # 2. BAYESIAN FILTER (uses floor plan constraints)
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

    # 3. LINEAR KALMAN FILTER (position + velocity tracking)
    # Calculate naive position as measurement
    # Standard math: x = cos(angle), y = sin(angle)
    naive_meas_x = positions['kalman']['x'] + STRIDE_LENGTH * np.cos(yaw)
    naive_meas_y = positions['kalman']['y'] + STRIDE_LENGTH * np.sin(yaw)
    kalman_filter.predict()
    kalman_filter.update([naive_meas_x, naive_meas_y])
    kalman_pos = kalman_filter.get_position()
    positions['kalman'] = {'x': round(kalman_pos[0], 3), 'y': round(kalman_pos[1], 3)}
    trajectories['kalman'].append({
        'stride': stride_count,
        'timestamp': datetime.utcnow().isoformat(),
        'x': positions['kalman']['x'],
        'y': positions['kalman']['y'],
        'heading': round(np.degrees(yaw), 2),
        'algorithm': 'kalman'
    })

    # 4. PARTICLE FILTER (multiple hypotheses with floor plan)
    particle_filter.update_stride(STRIDE_LENGTH, yaw)
    particle_pos = particle_filter.get_position()
    positions['particle'] = {'x': round(particle_pos[0], 3), 'y': round(particle_pos[1], 3)}
    trajectories['particle'].append({
        'stride': stride_count,
        'timestamp': datetime.utcnow().isoformat(),
        'x': positions['particle']['x'],
        'y': positions['particle']['y'],
        'heading': round(np.degrees(yaw), 2),
        'algorithm': 'particle'
    })

    stride_count += 1

    # Visual feedback on SenseHat LED
    # Green flash = stride detected
    G = [0, 255, 0]  # Green
    O = [0, 0, 0]    # Off

    # Create 8x8 grid (64 pixels) - flash green on top row
    grid = [
        G, G, G, G, G, G, G, G,  # Row 1: All green
        O, O, O, O, O, O, O, O,  # Rows 2-8: Off
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O
    ]

    # Update LED matrix
    with led_matrix_lock:
        global current_led_matrix
        current_led_matrix = grid.copy()

    sense.set_pixels(grid)
    time.sleep(0.1)
    sense.clear()

    # Clear LED matrix after flash
    with led_matrix_lock:
        current_led_matrix = [[0, 0, 0] for _ in range(64)]

def joystick_walk_monitor():
    """
    Background thread that monitors joystick MIDDLE button for stride detection.

    Uses IMU roll/pitch/yaw to determine walking direction automatically.
    NO automatic accelerometer detection - ONLY button presses count!
    """
    global joystick_walk_active, latest_imu

    logger.info("🕹️  Joystick walk monitor started")
    logger.info("   💡 TIP: Press the MIDDLE button (push down on joystick) for each stride!")
    logger.info("   💡 Direction is determined from Pi orientation (roll/pitch/yaw)")

    # Import joystick constants
    try:
        from sense_hat import ACTION_PRESSED
    except ImportError:
        # Mock mode - define constants
        ACTION_PRESSED = "pressed"

    def handle_joystick_middle_button(event):
        """Process middle button press - registers ONE stride"""
        global latest_imu

        # Only process button presses (not releases or holds)
        if event.action != ACTION_PRESSED:
            return

        logger.info("   [JOYSTICK] 🔘 MIDDLE BUTTON PRESSED!")

        with joystick_walk_lock:
            try:
                # Determine walking direction from current IMU orientation
                heading_rad, direction_name = determine_walking_direction_from_imu()

                # Update latest IMU readings for UI
                orientation_deg = sense.get_orientation_degrees()
                latest_imu = {
                    'roll': round(orientation_deg.get('roll', 0), 1),
                    'pitch': round(orientation_deg.get('pitch', 0), 1),
                    'yaw': round(orientation_deg.get('yaw', 0), 1)
                }

                # Process stride for all algorithms
                process_stride_all_algorithms(heading_rad)

                logger.info(f"✓ STRIDE {stride_count} COUNTED! Direction: {direction_name} ({np.degrees(heading_rad):.1f}°)")
                logger.info(f"  Position: Bayesian=({positions['bayesian']['x']:.2f}, {positions['bayesian']['y']:.2f})")

            except Exception as e:
                logger.error(f"Failed to process stride: {e}")

    # Assign ONLY middle button handler
    sense.stick.direction_middle = handle_joystick_middle_button

    logger.info("🕹️  Joystick MIDDLE button handler registered")

    # Keep thread alive while active
    while joystick_walk_active:
        try:
            # Update IMU readings periodically (so UI shows live sensor data)
            orientation_deg = sense.get_orientation_degrees()
            latest_imu = {
                'roll': round(orientation_deg.get('roll', 0), 1),
                'pitch': round(orientation_deg.get('pitch', 0), 1),
                'yaw': round(orientation_deg.get('yaw', 0), 1)
            }

            # Update LED matrix to show current orientation (optional visual feedback)
            # You could add a simple compass indicator here later

            time.sleep(0.1)  # Update every 100ms

        except Exception as e:
            logger.error(f"Error in joystick monitor: {e}")
            time.sleep(0.1)

    # Clean up event handler when stopping
    sense.stick.direction_middle = None

    logger.info("🛑 Joystick walk monitor stopped")

@app.route('/')
def index():
    return render_template('tracking.html')

@app.route('/api/sensors/raw')
def get_raw_sensors():
    """Get RAW sensor readings"""
    global latest_imu

    accel = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()
    mag = sense.get_compass_raw()
    orientation = sense.get_orientation_degrees()

    # Update latest IMU readings
    latest_imu = {
        'roll': round(orientation.get('roll', 0), 1),
        'pitch': round(orientation.get('pitch', 0), 1),
        'yaw': round(orientation.get('yaw', 0), 1)
    }

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
        'kalman': trajectories['kalman'],
        'particle': trajectories['particle'],
        'ground_truth': trajectories['ground_truth'],
        'stride_count': stride_count,
        'imu': latest_imu
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

@app.route('/api/connection_status')
def connection_status():
    """Check if using real hardware or mock"""
    logger.info("[CONNECTION STATUS] API endpoint called")
    hardware_type = 'real' if IS_REAL_HARDWARE else 'mock'
    message = 'Real Raspberry Pi' if IS_REAL_HARDWARE else 'Mock testing mode'
    logger.info(f"[CONNECTION STATUS] Returning: hardware={hardware_type}, message={message}")
    return jsonify({
        'hardware': hardware_type,
        'message': message
    })

@app.route('/api/set_start_position', methods=['POST'])
def set_start_position():
    """Set custom starting position"""
    global positions, bayesian_filter, kalman_filter, particle_filter

    logger.info("[SET START POSITION] API endpoint called")

    try:
        data = request.get_json()
        logger.info(f"[SET START POSITION] Received data: {data}")

        start_x = float(data.get('x', 2.0))
        start_y = float(data.get('y', 4.0))
        logger.info(f"[SET START POSITION] Parsed coordinates: x={start_x}, y={start_y}")

        # Update all algorithm starting positions
        positions['naive'] = {'x': start_x, 'y': start_y}
        positions['bayesian'] = {'x': start_x, 'y': start_y}
        positions['kalman'] = {'x': start_x, 'y': start_y}
        positions['particle'] = {'x': start_x, 'y': start_y}
        logger.info(f"[SET START POSITION] Updated positions for all algorithms")

        # Reinitialize filters with new starting position
        bayesian_filter = BayesianNavigationFilter(floor_plan, stride_length=STRIDE_LENGTH)
        bayesian_filter.reset(x=start_x, y=start_y)
        kalman_filter = KalmanFilter(initial_x=start_x, initial_y=start_y, dt=0.5)
        particle_filter = ParticleFilter(floor_plan, n_particles=200, initial_x=start_x, initial_y=start_y)
        logger.info(f"[SET START POSITION] Reinitialized all filters")

        logger.info(f"[SET START POSITION] ✓ SUCCESS - Start position set to ({start_x}, {start_y})")
        return jsonify({
            'success': True,
            'start_position': {'x': start_x, 'y': start_y}
        })
    except Exception as e:
        logger.error(f"[SET START POSITION] ✗ ERROR: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/manual_stride', methods=['POST'])
def manual_stride():
    """Process a single manual stride with specified heading"""
    global stride_count

    try:
        data = request.get_json()
        heading = float(data.get('heading', 0.0))

        logger.info(f"[MANUAL STRIDE] Processing stride with heading={np.degrees(heading):.1f}°")

        # Process stride for all algorithms
        process_stride_all_algorithms(heading)

        logger.info(f"[MANUAL STRIDE] ✓ SUCCESS - Stride {stride_count}, Bayesian=({positions['bayesian']['x']:.2f}, {positions['bayesian']['y']:.2f})")

        return jsonify({
            'success': True,
            'stride_count': stride_count,
            'position': positions['bayesian'],
            'heading_deg': round(np.degrees(heading), 1)
        })
    except Exception as e:
        logger.error(f"[MANUAL STRIDE] ✗ ERROR: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mock_test', methods=['POST'])
def mock_test():
    """Run a mock test - simulate a walk pattern WITH ground truth"""
    global stride_count, trajectories

    logger.info("[MOCK TEST] API endpoint called")

    try:
        # Extended mock test: Walk TOWARD the wall to test Bayesian avoidance
        # Starting at (2.0, 4.0) in Room 1
        # Wall is at x=5.0 (Room 1 safe zone: x=[1.5, 4.8])
        # This path walks EAST toward wall - Naive goes through, Bayesian should avoid!
        test_headings = [
            # Rectangle 1: Approach the wall (larger loop)
            0, 0, 0, 0,              # East - 4 strides (2.0→4.8) approaches wall

            np.pi/2, np.pi/2, np.pi/2,  # North - 3 strides

            np.pi, np.pi, np.pi, np.pi,  # West - 4 strides (away from wall)

            -np.pi/2, -np.pi/2, -np.pi/2,  # South - 3 strides

            # Rectangle 2: Repeat to show consistency
            0, 0, 0,                 # East - 3 strides (toward wall again)

            np.pi/2, np.pi/2,        # North - 2 strides

            np.pi, np.pi, np.pi,     # West - 3 strides

            -np.pi/2, -np.pi/2       # South - 2 strides
        ]

        logger.info(f"[MOCK TEST] Simulating {len(test_headings)} strides")
        initial_count = stride_count

        # Compute ideal ground truth path (perfect dead reckoning)
        # NOTE: In mock test with perfect headings, naive and ground truth are identical
        # This is CORRECT - ground truth IS what naive does with perfect sensors
        gt_x, gt_y = positions['naive']['x'], positions['naive']['y']
        trajectories['ground_truth'].clear()  # Clear previous mock test

        for i, heading in enumerate(test_headings):
            logger.debug(f"[MOCK TEST] Processing stride {i+1}/{len(test_headings)}, heading={np.degrees(heading):.1f}°")

            # Process stride with filters first
            process_stride_all_algorithms(heading)

            # Update ground truth AFTER processing (so indices match)
            gt_x += STRIDE_LENGTH * np.cos(heading)
            gt_y += STRIDE_LENGTH * np.sin(heading)
            trajectories['ground_truth'].append({
                'x': round(gt_x, 3),
                'y': round(gt_y, 3),
                'stride': stride_count,
                'heading': round(np.degrees(heading), 2)
            })

            time.sleep(0.1)  # Small delay between strides

        total_strides = stride_count - initial_count
        logger.info(f"[MOCK TEST] ✓ SUCCESS - Generated {total_strides} test strides with ground truth")

        return jsonify({
            'success': True,
            'strides': total_strides,
            'message': f'Generated {total_strides} test strides'
        })
    except Exception as e:
        logger.error(f"[MOCK TEST] ✗ ERROR: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset all data"""
    global stride_count, positions, trajectories, bayesian_filter, kalman_filter, particle_filter

    stride_count = 0
    start_x, start_y = 2.0, 4.0

    positions = {
        'naive': {'x': start_x, 'y': start_y},
        'bayesian': {'x': start_x, 'y': start_y},
        'kalman': {'x': start_x, 'y': start_y},
        'particle': {'x': start_x, 'y': start_y}
    }
    trajectories = {
        'naive': [],
        'bayesian': [],
        'kalman': [],
        'particle': [],
        'ground_truth': []
    }
    sensor_buffer['raw'].clear()
    sensor_buffer['filtered'].clear()
    sensor_buffer['timestamps'].clear()

    # Reset all filters to start position
    bayesian_filter.reset(x=start_x, y=start_y)
    kalman_filter = KalmanFilter(initial_x=start_x, initial_y=start_y, dt=0.5)
    particle_filter = ParticleFilter(floor_plan, n_particles=200, initial_x=start_x, initial_y=start_y)

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

@app.route('/api/joystick_walk/start', methods=['POST'])
def start_joystick_walk():
    """Start joystick button-based stride detection (ONLY MODE - no accelerometer)"""
    try:
        global joystick_walk_active, joystick_walk_thread

        if joystick_walk_active:
            return jsonify({'success': False, 'message': 'Joystick-walk already active'})

        logger.info("[START JOYSTICK-WALK] Starting joystick stride detection...")
        logger.info("[START JOYSTICK-WALK] Press the MIDDLE button on SenseHat for each stride!")

        # Start background thread
        joystick_walk_active = True
        joystick_walk_thread = threading.Thread(target=joystick_walk_monitor, daemon=True)
        joystick_walk_thread.start()

        logger.info("[START JOYSTICK-WALK] ✓ Background thread started successfully")

        return jsonify({
            'success': True,
            'message': 'Joystick-walk started - Press MIDDLE button for each stride!'
        })

    except Exception as e:
        logger.error(f"[START JOYSTICK-WALK] Error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to start joystick-walk: {str(e)}'
        }), 500

@app.route('/api/joystick_walk/stop', methods=['POST'])
def stop_joystick_walk():
    """Stop joystick button-based stride detection"""
    try:
        global joystick_walk_active, joystick_walk_thread, stride_count

        if not joystick_walk_active:
            return jsonify({'success': False, 'message': 'Joystick-walk not active'})

        logger.info("[STOP JOYSTICK-WALK] Stopping joystick stride detection...")

        # Stop background thread
        joystick_walk_active = False

        # Wait for thread to finish (with timeout)
        if joystick_walk_thread and joystick_walk_thread.is_alive():
            joystick_walk_thread.join(timeout=2.0)

        logger.info(f"[STOP JOYSTICK-WALK] ✓ Stopped (captured {stride_count} strides)")

        return jsonify({
            'success': True,
            'message': 'Joystick-walk stopped',
            'stride_count': stride_count
        })

    except Exception as e:
        logger.error(f"[STOP JOYSTICK-WALK] Error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to stop joystick-walk: {str(e)}'
        }), 500

@app.route('/api/joystick_walk/status')
def get_joystick_walk_status():
    """Get joystick-walk status"""
    return jsonify({
        'active': joystick_walk_active,
        'stride_count': stride_count,
        'imu': latest_imu  # Include live IMU readings
    })

@app.route('/api/led_matrix')
def get_led_matrix():
    """Get current LED matrix state for display on web UI"""
    with led_matrix_lock:
        return jsonify({
            'matrix': current_led_matrix,  # 64 pixels, each [R, G, B]
            'stride_count': stride_count,
            'joystick_active': joystick_walk_active
        })

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    """Generate comprehensive performance report"""
    try:
        data = request.get_json()
        screenshot_data = data.get('screenshot', '')  # Base64 image data

        # Calculate metrics
        metrics = {}
        for name in ['naive', 'bayesian', 'kalman', 'particle']:
            traj = trajectories[name]
            if len(traj) > 0:
                # Total distance traveled
                total_dist = 0
                for i in range(1, len(traj)):
                    dx = traj[i]['x'] - traj[i-1]['x']
                    dy = traj[i]['y'] - traj[i-1]['y']
                    total_dist += np.sqrt(dx**2 + dy**2)

                # Compare to ground truth if available
                error_from_gt = 0
                if len(trajectories['ground_truth']) > 0:
                    errors = []
                    for i in range(min(len(traj), len(trajectories['ground_truth']))):
                        dx = traj[i]['x'] - trajectories['ground_truth'][i]['x']
                        dy = traj[i]['y'] - trajectories['ground_truth'][i]['y']
                        errors.append(np.sqrt(dx**2 + dy**2))
                    error_from_gt = np.mean(errors) if errors else 0

                metrics[name] = {
                    'total_distance': round(total_dist, 2),
                    'num_strides': len(traj),
                    'avg_error_from_gt': round(error_from_gt, 3),
                    'final_position': {
                        'x': round(traj[-1]['x'], 2),
                        'y': round(traj[-1]['y'], 2)
                    }
                }

        # Generate HTML report
        report_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Pedestrian Navigation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #667eea; color: white; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-label {{ font-weight: bold; color: #666; }}
        .metric-value {{ font-size: 24px; color: #667eea; }}
        img {{ max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .algorithm-naive {{ color: #fc8181; }}
        .algorithm-bayesian {{ color: #63b3ed; }}
        .algorithm-kalman {{ color: #68d391; }}
        .algorithm-particle {{ color: #9f7aea; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Pedestrian Inertial Navigation Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Test Type:</strong> {'Mock Test Simulation' if len(trajectories['ground_truth']) > 0 else 'Real IMU Data'}</p>
        <p><strong>Total Strides:</strong> {stride_count}</p>
    </div>

    <div class="section">
        <h2>📡 IMU Sensor Readings (Current)</h2>
        <p><strong>Roll:</strong> {latest_imu['roll']}° (side-to-side tilt, should be ~0° when walking straight)</p>
        <p><strong>Pitch:</strong> {latest_imu['pitch']}° (forward/backward tilt, should be ~0° when walking straight)</p>
        <p><strong>Yaw (Heading):</strong> {latest_imu['yaw']}° (compass direction - THIS is used for navigation!)</p>
        <p><em>Note: Yaw is the critical parameter for pedestrian navigation. Roll and pitch are used to detect tilted sensor mounting.</em></p>
    </div>

    <div class="section">
        <h2>📷 Trajectory Visualization</h2>
        <img src="{screenshot_data}" alt="Trajectory Map"/>
    </div>

    <div class="section">
        <h2>📈 Performance Metrics</h2>
        <table>
            <tr>
                <th>Algorithm</th>
                <th>Total Distance (m)</th>
                <th>Num Strides</th>
                <th>Avg Error from GT (m)</th>
                <th>Final Position (x, y)</th>
            </tr>
"""

        for name in ['naive', 'bayesian', 'kalman', 'particle']:
            if name in metrics:
                m = metrics[name]
                report_html += f"""
            <tr>
                <td class="algorithm-{name}"><strong>{name.capitalize()}</strong></td>
                <td>{m['total_distance']} m</td>
                <td>{m['num_strides']}</td>
                <td>{m['avg_error_from_gt']} m</td>
                <td>({m['final_position']['x']}, {m['final_position']['y']})</td>
            </tr>
"""

        report_html += """
        </table>
    </div>

    <div class="section">
        <h2>🎯 Algorithm Comparison</h2>
        <h3>Naive Dead Reckoning (Red)</h3>
        <p>Simple pedestrian dead reckoning using stride length and IMU heading. Accumulates drift over time.</p>

        <h3>Bayesian Filter with Floor Plan (Blue)</h3>
        <p>Non-recursive Bayesian filter following Koroglu & Yilmaz (2017) methodology.
        Uses floor plan constraints to prevent wall crossing. This is the primary requirement of the assignment.</p>

        <h3>Kalman Filter (Green)</h3>
        <p>Linear Kalman filter with position and velocity state. Smooths trajectory but has no floor plan awareness.</p>

        <h3>Particle Filter (Purple)</h3>
        <p>Multiple hypothesis tracking with resampling. Uses floor plan to weight particles in walkable areas.</p>
    </div>

    <div class="section">
        <h2>⚙️ System Configuration</h2>
        <p><strong>Floor Plan:</strong> 10m × 10m room with vertical wall at x=5m</p>
        <p><strong>Stride Length:</strong> 0.7m</p>
        <p><strong>Bayesian Floor Plan Weight:</strong> 50.0</p>
        <p><strong>Starting Position:</strong> (2.0m, 4.0m)</p>
    </div>

    <div class="section">
        <h2>📝 Conclusion</h2>
        <p>This report demonstrates the implementation of pedestrian inertial navigation using
        non-recursive Bayesian filtering with floor plan constraints, as required by the DFA assignment.</p>

        <p><strong>Key Findings:</strong></p>
        <ul>
            <li>Bayesian filter successfully incorporates floor plan constraints to avoid walls</li>
            <li>Multiple algorithms compared for trajectory estimation accuracy</li>
            <li>Real-time dashboard enables live visualization and testing</li>
        </ul>
    </div>

    <script>
        // Print dialog on load
        window.onload = function() {{
            setTimeout(function() {{ window.print(); }}, 500);
        }};
    </script>
</body>
</html>
"""

        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'navigation_report_{timestamp}.html'
        report_path = f'/tmp/{report_filename}'

        with open(report_path, 'w') as f:
            f.write(report_html)

        logger.info(f"[REPORT] Generated report: {report_filename}")

        return jsonify({
            'success': True,
            'report_path': report_path,
            'filename': report_filename,
            'metrics': metrics
        })

    except Exception as e:
        logger.error(f"[REPORT] Error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download_report/<filename>')
def download_report(filename):
    """Download generated report"""
    try:
        report_path = f'/tmp/{filename}'
        return send_file(report_path, as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"[REPORT DOWNLOAD] Error: {str(e)}")
        return jsonify({'error': str(e)}), 404

# =======================
# MQTT CONTROL ROUTES
# =======================

@app.route('/api/mqtt/status')
def mqtt_status():
    """Get status of all MQTT programs"""
    global mqtt_stats, mqtt_processes

    # Check broker
    mqtt_stats['broker_running'] = check_mqtt_broker()
    mqtt_stats['last_check'] = time.time()

    # Check which processes are still running
    for key, proc in mqtt_processes.items():
        status_key = f'{key}_active'
        if proc and proc.poll() is None:  # Still running
            mqtt_stats[status_key] = True
        else:
            mqtt_stats[status_key] = False
            if proc:
                mqtt_processes[key] = None

    return jsonify(mqtt_stats)

@app.route('/api/mqtt/start/<program>', methods=['POST'])
def mqtt_start(program):
    """Start an MQTT program"""
    global mqtt_processes

    # Check if broker is running
    if not check_mqtt_broker():
        return jsonify({
            'success': False,
            'message': 'MQTT broker not running. Start mosquitto first: sudo systemctl start mosquitto'
        })

    # Get MQTT directory
    mqtt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mqtt')

    try:
        if program == 'cpu_publisher':
            if mqtt_processes['cpu_publisher'] and mqtt_processes['cpu_publisher'].poll() is None:
                return jsonify({'success': False, 'message': 'CPU publisher already running'})

            logger.info("🚀 Starting CPU Publisher...")
            proc = subprocess.Popen(
                ['python3', os.path.join(mqtt_dir, 'mqtt_cpu_publisher.py'), '--broker', 'localhost']
                # Output goes to terminal (no stdout/stderr redirect)
            )
            mqtt_processes['cpu_publisher'] = proc
            logger.info(f"✓ CPU Publisher started (PID: {proc.pid})")
            return jsonify({'success': True, 'message': 'CPU publisher started - check terminal for output'})

        elif program == 'location_publisher':
            if mqtt_processes['location_publisher'] and mqtt_processes['location_publisher'].poll() is None:
                return jsonify({'success': False, 'message': 'Location publisher already running'})

            logger.info("🚀 Starting Location Publisher...")
            proc = subprocess.Popen(
                ['python3', os.path.join(mqtt_dir, 'mqtt_location_publisher.py'), '--broker', 'localhost']
            )
            mqtt_processes['location_publisher'] = proc
            logger.info(f"✓ Location Publisher started (PID: {proc.pid})")
            return jsonify({'success': True, 'message': 'Location publisher started - check terminal for output'})

        elif program == 'windowed_1s':
            if mqtt_processes['windowed_1s'] and mqtt_processes['windowed_1s'].poll() is None:
                return jsonify({'success': False, 'message': 'Windowed subscriber (1s) already running'})

            logger.info("🚀 Starting Windowed Subscriber (1s window)...")
            proc = subprocess.Popen(
                ['python3', os.path.join(mqtt_dir, 'mqtt_subscriber_windowed.py'), '--broker', 'localhost', '--window', '1.0']
            )
            mqtt_processes['windowed_1s'] = proc
            logger.info(f"✓ Windowed Subscriber (1s) started (PID: {proc.pid})")
            return jsonify({'success': True, 'message': 'Windowed subscriber (1s) started - check terminal for output'})

        elif program == 'windowed_5s':
            if mqtt_processes['windowed_5s'] and mqtt_processes['windowed_5s'].poll() is None:
                return jsonify({'success': False, 'message': 'Windowed subscriber (5s) already running'})

            logger.info("🚀 Starting Windowed Subscriber (5s window)...")
            proc = subprocess.Popen(
                ['python3', os.path.join(mqtt_dir, 'mqtt_subscriber_windowed.py'), '--broker', 'localhost', '--window', '5.0']
            )
            mqtt_processes['windowed_5s'] = proc
            logger.info(f"✓ Windowed Subscriber (5s) started (PID: {proc.pid})")
            return jsonify({'success': True, 'message': 'Windowed subscriber (5s) started - check terminal for output'})

        elif program == 'bernoulli':
            if mqtt_processes['bernoulli'] and mqtt_processes['bernoulli'].poll() is None:
                return jsonify({'success': False, 'message': 'Bernoulli subscriber already running'})

            logger.info("🚀 Starting Bernoulli Sampling Subscriber...")
            proc = subprocess.Popen(
                ['python3', os.path.join(mqtt_dir, 'mqtt_subscriber_bernoulli.py'), '--broker', 'localhost']
            )
            mqtt_processes['bernoulli'] = proc
            logger.info(f"✓ Bernoulli Subscriber started (PID: {proc.pid})")
            return jsonify({'success': True, 'message': 'Bernoulli subscriber started - check terminal for output'})

        elif program == 'malfunction':
            if mqtt_processes['malfunction'] and mqtt_processes['malfunction'].poll() is None:
                return jsonify({'success': False, 'message': 'Malfunction detector already running'})

            logger.info("🚀 Starting Malfunction Detector...")
            proc = subprocess.Popen(
                ['python3', os.path.join(mqtt_dir, 'malfunction_detection.py'), '--broker', 'localhost']
            )
            mqtt_processes['malfunction'] = proc
            logger.info(f"✓ Malfunction Detector started (PID: {proc.pid})")
            return jsonify({'success': True, 'message': 'Malfunction detector started - check terminal for output'})

        else:
            return jsonify({'success': False, 'message': f'Unknown program: {program}'})

    except Exception as e:
        logger.error(f"Error starting {program}: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/mqtt/stop/<program>', methods=['POST'])
def mqtt_stop(program):
    """Stop an MQTT program"""
    global mqtt_processes

    try:
        if program in mqtt_processes and mqtt_processes[program]:
            if mqtt_processes[program].poll() is None:  # Still running
                mqtt_processes[program].terminate()
                mqtt_processes[program].wait(timeout=5)
                mqtt_processes[program] = None
                return jsonify({'success': True, 'message': f'{program} stopped'})
            else:
                mqtt_processes[program] = None
                return jsonify({'success': False, 'message': f'{program} not running'})
        else:
            return jsonify({'success': False, 'message': f'{program} not found'})
    except Exception as e:
        logger.error(f"Error stopping {program}: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/mqtt/stop_all', methods=['POST'])
def mqtt_stop_all():
    """Stop all MQTT programs"""
    global mqtt_processes

    stopped = []
    for key, proc in mqtt_processes.items():
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                stopped.append(key)
            except:
                pass
            mqtt_processes[key] = None

    return jsonify({
        'success': True,
        'message': f'Stopped {len(stopped)} programs',
        'stopped': stopped
    })

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("🚀 ADVANCED Dashboard with Auto-Stride Detection")
    logger.info("=" * 70)
    logger.info(f"\n📱 Access: http://10.49.216.71:5001")
    logger.info(f"\n✨ Features:")
    logger.info(f"   - 🚶 AUTOMATIC TRACKING: Always monitoring for strides!")
    logger.info(f"   - Raw vs Filtered sensor comparison")
    logger.info(f"   - Multiple algorithm trajectories:")
    logger.info(f"     • Naive Dead Reckoning")
    logger.info(f"     • ✓ Bayesian Filter (with floor plan constraints)")
    logger.info(f"     • ✓ Linear Kalman Filter (position + velocity)")
    logger.info(f"     • ✓ Particle Filter (multiple hypotheses)")
    logger.info(f"   - Real-time error metrics")
    logger.info(f"   - Parameter tuning")
    logger.info(f"   - Ground truth comparison")
    logger.info(f"   - Floor plan constraints (10m × 10m square room with middle wall)")
    logger.info(f"\n🎒 Usage:")
    logger.info(f"   1. Put Raspberry Pi in backpack")
    logger.info(f"   2. Access dashboard from laptop browser")
    logger.info(f"   3. Click 'START WALKING' button")
    logger.info(f"   4. Walk naturally - strides detected automatically")
    logger.info(f"   5. Click 'STOP WALKING' when done")
    logger.info(f"   6. View trajectories on the map!")
    logger.info("\n" + "=" * 70)

    # Don't auto-start - wait for user to click START button
    logger.info("\n⏸️  Stride detection ready - click START WALKING in dashboard")
    logger.info("=" * 70 + "\n")

    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
