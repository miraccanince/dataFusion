#!/bin/bash
# Get CSV data from Raspberry Pi back to your computer
# Usage: ./get_data_from_pi.sh

PI_USER="jdmc"
PI_HOST="10.111.224.71"
PI_ADDR="${PI_USER}@${PI_HOST}"

echo "=========================================="
echo "Retrieving data from Raspberry Pi"
echo "=========================================="
echo "Raspberry Pi: ${PI_ADDR}"
echo ""

# Create local data directory
mkdir -p ./data

# Transfer CSV files
echo "Downloading CSV files..."
scp ${PI_ADDR}:~/dataFusion/*.csv ./data/ 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Data retrieved successfully!"
    echo ""
    echo "Files in ./data/:"
    ls -lh ./data/*.csv
    echo ""
    echo "=========================================="
    echo "Next steps:"
    echo "=========================================="
    echo "1. Analyze data in Jupyter:"
    echo "   jupyter notebook 03_analyze_data.ipynb"
    echo "=========================================="
else
    echo ""
    echo "✗ No CSV files found or connection failed"
    echo ""
    echo "Make sure you've run the data collection scripts on the Pi first!"
fi
