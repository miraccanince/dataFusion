#!/bin/bash
# Transfer complete dashboard system to Raspberry Pi
# Usage: ./transfer_to_pi.sh

PI_USER="jdmc"
PI_HOST="10.192.168.71"
PI_ADDR="${PI_USER}@${PI_HOST}"

echo "=========================================="
echo "Transferring Dashboard to Raspberry Pi"
echo "=========================================="
echo "Raspberry Pi: ${PI_ADDR}"
echo ""

# Create remote directories
echo "Creating remote directories..."
ssh ${PI_ADDR} "mkdir -p ~/dataFusion/src ~/dataFusion/templates ~/dataFusion/output"

# Transfer Python source files
echo "Transferring Python source files..."
scp ../src/bayesian_filter.py ${PI_ADDR}:~/dataFusion/src/
scp ../src/kalman_filter.py ${PI_ADDR}:~/dataFusion/src/
scp ../src/particle_filter.py ${PI_ADDR}:~/dataFusion/src/
scp ../src/web_dashboard_advanced.py ${PI_ADDR}:~/dataFusion/src/

# Transfer HTML templates
echo "Transferring HTML templates..."
scp ../templates/tracking.html ${PI_ADDR}:~/dataFusion/templates/
scp ../templates/advanced.html ${PI_ADDR}:~/dataFusion/templates/

# Transfer floor plan image
echo "Transferring floor plan..."
scp ../output/floor_plan_pdf.png ${PI_ADDR}:~/dataFusion/output/ 2>/dev/null || echo "  (Floor plan image not found, will be generated on RPi)"

echo ""
echo "✓ Dashboard transferred successfully!"
echo ""
echo "=========================================="
echo "Next steps:"
echo "=========================================="
echo "1. SSH into Raspberry Pi:"
echo "   ssh ${PI_ADDR}"
echo ""
echo "2. Install dependencies (first time only):"
echo "   sudo apt-get update"
echo "   sudo apt-get install -y python3-pip python3-flask python3-numpy python3-scipy"
echo "   pip3 install sense-hat --break-system-packages"
echo ""
echo "3. Navigate to folder:"
echo "   cd ~/dataFusion"
echo ""
echo "4. Start the dashboard:"
echo "   python3 src/web_dashboard_advanced.py"
echo ""
echo "5. Access dashboard from your laptop:"
echo "   http://10.192.168.71:5001"
echo ""
echo "6. Put RPi in backpack, click START WALKING, and walk around!"
echo "=========================================="
