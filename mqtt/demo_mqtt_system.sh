#!/bin/bash
# Quick MQTT System Demo
# This script runs all MQTT programs for testing

echo "=========================================="
echo "MQTT System Demo"
echo "=========================================="
echo "This will run:"
echo "  1. CPU Publisher (30 seconds)"
echo "  2. Windowed Subscriber (1s window)"
echo "  3. Bernoulli Sampling Subscriber"
echo "  4. Malfunction Detector"
echo ""
echo "Press Ctrl+C to stop early"
echo "=========================================="
echo ""

# Check if mosquitto is running
if ! systemctl is-active --quiet mosquitto; then
    echo "⚠ Mosquitto broker is not running!"
    echo "Starting mosquitto..."
    sudo systemctl start mosquitto
    sleep 2
fi

echo "✓ Mosquitto broker is running"
echo ""
echo "Starting programs..."
echo ""

# Start CPU publisher in background (30 second test)
echo "[1/4] Starting CPU Publisher (30s duration)..."
python3 mqtt_cpu_publisher.py --broker localhost --duration 30 &
PID_CPU=$!
sleep 3

# Start windowed subscriber (1s window)
echo "[2/4] Starting Windowed Subscriber (1s window)..."
python3 mqtt_subscriber_windowed.py --broker localhost --window 1.0 &
PID_WINDOWED=$!
sleep 1

# Start Bernoulli subscriber
echo "[3/4] Starting Bernoulli Sampling Subscriber..."
python3 mqtt_subscriber_bernoulli.py --broker localhost &
PID_BERNOULLI=$!
sleep 1

# Start malfunction detector
echo "[4/4] Starting Malfunction Detector..."
python3 malfunction_detection.py --broker localhost &
PID_MALFUNCTION=$!

echo ""
echo "=========================================="
echo "✓ All programs started!"
echo "=========================================="
echo "Running for 30 seconds..."
echo ""
echo "You should see:"
echo "  - CPU publisher: Messages every ~100 published"
echo "  - Windowed subscriber: Statistics every second"
echo "  - Bernoulli subscriber: Sampling stats every second"
echo "  - Malfunction detector: Status every 100 messages"
echo ""
echo "Press Ctrl+C to stop all programs"
echo "=========================================="
echo ""

# Function to cleanup on Ctrl+C
cleanup() {
    echo ""
    echo ""
    echo "=========================================="
    echo "Stopping all programs..."
    echo "=========================================="
    kill $PID_CPU 2>/dev/null
    kill $PID_WINDOWED 2>/dev/null
    kill $PID_BERNOULLI 2>/dev/null
    kill $PID_MALFUNCTION 2>/dev/null
    sleep 1
    echo "✓ All programs stopped"
    echo "=========================================="
    exit 0
}

# Register cleanup function
trap cleanup SIGINT SIGTERM

# Wait for CPU publisher to finish (30 seconds)
wait $PID_CPU

# Stop subscribers
echo ""
echo ""
echo "=========================================="
echo "30 seconds complete! Stopping programs..."
echo "=========================================="
kill $PID_WINDOWED $PID_BERNOULLI $PID_MALFUNCTION 2>/dev/null
sleep 1

echo ""
echo "✓ Demo complete!"
echo ""
echo "=========================================="
echo "What just happened:"
echo "=========================================="
echo "1. CPU Publisher sent ~3000 messages (10ms interval)"
echo "2. Windowed Subscriber computed 30 statistics snapshots"
echo "3. Bernoulli Subscriber sampled ~1000 messages (33%)"
echo "4. Malfunction Detector monitored for issues"
echo ""
echo "For your report:"
echo "  - Take screenshots of this output"
echo "  - Compare windowed vs Bernoulli results"
echo "  - Explain how Bernoulli sampling reduces load"
echo "=========================================="
