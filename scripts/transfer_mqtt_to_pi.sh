#!/bin/bash
# Transfer MQTT system to Raspberry Pi

PI_USER="jdmc"
PI_HOST="10.49.216.71"
PI_ADDR="${PI_USER}@${PI_HOST}"

echo "=========================================="
echo "Transferring MQTT System to Raspberry Pi"
echo "=========================================="
echo "Raspberry Pi: ${PI_ADDR}"
echo ""

# Create MQTT directory on Pi
echo "Creating MQTT directory on Pi..."
ssh ${PI_ADDR} "mkdir -p ~/dataFusion/mqtt"

# Transfer all MQTT Python programs
echo "Transferring MQTT programs..."
scp ../mqtt/mqtt_cpu_publisher.py ${PI_ADDR}:~/dataFusion/mqtt/
scp ../mqtt/mqtt_location_publisher.py ${PI_ADDR}:~/dataFusion/mqtt/
scp ../mqtt/mqtt_subscriber_windowed.py ${PI_ADDR}:~/dataFusion/mqtt/
scp ../mqtt/mqtt_subscriber_bernoulli.py ${PI_ADDR}:~/dataFusion/mqtt/
scp ../mqtt/malfunction_detection.py ${PI_ADDR}:~/dataFusion/mqtt/

# Transfer README files
echo "Transferring documentation..."
scp ../mqtt/README.md ${PI_ADDR}:~/dataFusion/mqtt/
scp ../mqtt/GETTING_STARTED.md ${PI_ADDR}:~/dataFusion/mqtt/

echo ""
echo "✓ MQTT system transferred successfully!"
echo ""
echo "=========================================="
echo "Next steps on Raspberry Pi:"
echo "=========================================="
echo "1. SSH into Pi:"
echo "   ssh ${PI_ADDR}"
echo ""
echo "2. Install MQTT broker (first time only):"
echo "   sudo apt-get update"
echo "   sudo apt-get install -y mosquitto mosquitto-clients"
echo "   sudo systemctl start mosquitto"
echo "   sudo systemctl enable mosquitto"
echo ""
echo "3. Install Python dependencies:"
echo "   pip3 install paho-mqtt psutil --break-system-packages"
echo ""
echo "4. Test CPU publisher:"
echo "   cd ~/dataFusion/mqtt"
echo "   python3 mqtt_cpu_publisher.py --broker localhost --duration 30"
echo ""
echo "5. For full system test, see GETTING_STARTED.md"
echo "=========================================="
