#!/bin/bash
# Quick start script for web dashboard

echo "🚀 Starting Web Dashboard on Raspberry Pi..."
echo ""

ssh jdmc@10.111.224.71 "cd ~/dataFusion && python3 web_dashboard.py"
