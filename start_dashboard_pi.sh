#!/bin/bash
# Quick Start Script for Raspberry Pi
# Run this after cloning the repo

echo "=========================================="
echo "Starting Pedestrian Navigation Dashboard"
echo "=========================================="
echo ""

# Check if mosquitto is running
if ! systemctl is-active --quiet mosquitto; then
    echo "Starting MQTT broker..."
    sudo systemctl start mosquitto
fi

echo "✓ MQTT broker running"
echo ""
echo "Starting dashboard..."
echo "Access from browser: http://10.49.216.71:5001"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Start dashboard
cd src
python3 web_dashboard_advanced.py
