#!/usr/bin/env python3
"""
Pedestrian Navigation System Launcher
======================================

This launcher runs on your LAPTOP and provides:
- Web interface to connect to Raspberry Pi
- Automatic browser opening
- Connection status checking
- Easy start/stop of Pi dashboard

Usage:
    python3 launcher.py
"""

from flask import Flask, render_template, jsonify, request
import webbrowser
import subprocess
import threading
import time
import socket

app = Flask(__name__)

# Configuration
PI_IP = "10.111.224.71"
PI_PORT = 5001
PI_USERNAME = "jdmc"
LAUNCHER_PORT = 8080

# State
pi_status = {
    'connected': False,
    'dashboard_running': False,
    'last_check': None
}

def check_pi_connection():
    """Check if Raspberry Pi is reachable"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((PI_IP, 22))  # Check SSH port
        sock.close()
        return result == 0
    except:
        return False

def check_dashboard_running():
    """Check if dashboard is running on Pi"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((PI_IP, PI_PORT))
        sock.close()
        return result == 0
    except:
        return False

def start_pi_dashboard():
    """Start dashboard on Raspberry Pi via SSH"""
    try:
        # SSH command to start dashboard in background
        cmd = [
            'ssh', f'{PI_USERNAME}@{PI_IP}',
            'cd ~/dataFusion/src && nohup python3 web_dashboard_advanced.py > /tmp/dashboard.log 2>&1 &'
        ]
        subprocess.Popen(cmd)
        time.sleep(3)  # Wait for startup
        return True
    except Exception as e:
        print(f"Error starting Pi dashboard: {e}")
        return False

def stop_pi_dashboard():
    """Stop dashboard on Raspberry Pi"""
    try:
        cmd = [
            'ssh', f'{PI_USERNAME}@{PI_IP}',
            'pkill -f web_dashboard_advanced.py'
        ]
        subprocess.run(cmd)
        return True
    except Exception as e:
        print(f"Error stopping Pi dashboard: {e}")
        return False

@app.route('/')
def index():
    """Main launcher page"""
    return render_template('launcher.html')

@app.route('/api/status')
def get_status():
    """Get connection status"""
    pi_status['connected'] = check_pi_connection()
    pi_status['dashboard_running'] = check_dashboard_running()
    pi_status['last_check'] = time.time()

    return jsonify(pi_status)

@app.route('/api/connect', methods=['POST'])
def connect_to_pi():
    """Connect to Raspberry Pi dashboard"""
    # Check if Pi is reachable
    if not check_pi_connection():
        return jsonify({
            'success': False,
            'message': 'Raspberry Pi not reachable. Check network connection.'
        })

    # Check if dashboard is already running
    if check_dashboard_running():
        return jsonify({
            'success': True,
            'message': 'Dashboard already running',
            'url': f'http://{PI_IP}:{PI_PORT}'
        })

    # Try to start dashboard
    if start_pi_dashboard():
        # Verify it started
        time.sleep(2)
        if check_dashboard_running():
            return jsonify({
                'success': True,
                'message': 'Dashboard started successfully',
                'url': f'http://{PI_IP}:{PI_PORT}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Dashboard failed to start. Check Pi logs.'
            })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to start dashboard on Pi'
        })

@app.route('/api/disconnect', methods=['POST'])
def disconnect_from_pi():
    """Stop Pi dashboard"""
    if stop_pi_dashboard():
        return jsonify({
            'success': True,
            'message': 'Dashboard stopped'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to stop dashboard'
        })

@app.route('/api/transfer', methods=['POST'])
def transfer_files():
    """Transfer latest files to Raspberry Pi"""
    try:
        # Use rsync to transfer files
        cmd = [
            'rsync', '-avz', '--exclude', '__pycache__',
            '--exclude', '.git', '--exclude', 'venv',
            '/Users/mirac/Desktop/master_sse_25_26-main/dataFusion/',
            f'{PI_USERNAME}@{PI_IP}:~/dataFusion/'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Files transferred successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Transfer failed: {result.stderr}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

if __name__ == '__main__':
    print("=" * 70)
    print(" Pedestrian Navigation System Launcher")
    print("=" * 70)
    print(f"\n📱 Opening launcher in browser...")
    print(f"   URL: http://localhost:{LAUNCHER_PORT}")
    print(f"\n Raspberry Pi Configuration:")
    print(f"   IP: {PI_IP}")
    print(f"   Port: {PI_PORT}")
    print(f"   Username: {PI_USERNAME}")
    print("\n" + "=" * 70)

    # Open browser after short delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f'http://localhost:{LAUNCHER_PORT}')

    threading.Thread(target=open_browser, daemon=True).start()

    # Run launcher
    app.run(host='localhost', port=LAUNCHER_PORT, debug=False)
