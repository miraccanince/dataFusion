#!/bin/bash
# Transfer scripts to Raspberry Pi
# Usage: ./transfer_to_pi.sh

PI_USER="jdmc"
PI_HOST="10.111.224.71"
PI_ADDR="${PI_USER}@${PI_HOST}"

echo "=========================================="
echo "Transferring scripts to Raspberry Pi"
echo "=========================================="
echo "Raspberry Pi: ${PI_ADDR}"
echo ""

# Create remote directory
echo "Creating remote directory..."
ssh ${PI_ADDR} "mkdir -p ~/dataFusion"

# Transfer Python scripts
echo "Transferring Python scripts..."
scp 01_collect_stride_data.py ${PI_ADDR}:~/dataFusion/
scp 02_naive_dead_reckoning.py ${PI_ADDR}:~/dataFusion/
scp understand_sensors.py ${PI_ADDR}:~/dataFusion/

echo ""
echo "✓ Scripts transferred successfully!"
echo ""
echo "=========================================="
echo "Next steps:"
echo "=========================================="
echo "1. SSH into Raspberry Pi:"
echo "   ssh ${PI_ADDR}"
echo ""
echo "2. Navigate to folder:"
echo "   cd ~/dataFusion"
echo ""
echo "3. Run scripts:"
echo "   python 01_collect_stride_data.py"
echo "   python 02_naive_dead_reckoning.py"
echo ""
echo "4. Transfer data back (run on your computer):"
echo "   ./get_data_from_pi.sh"
echo "=========================================="
