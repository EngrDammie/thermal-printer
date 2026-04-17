#!/bin/bash
# Setup script for thermal printer CLI

echo "=== Thermal Printer CLI Setup ==="
echo ""

# Check Python
echo "1. Checking Python..."
python3 --version || { echo "Python3 not found!"; exit 1; }
echo "   OK"
echo ""

# Install system dependencies
echo "2. Installing system dependencies..."
sudo apt update
sudo apt install -y bluetooth bluez libbluetooth-dev python3-bluez
echo "   OK"
echo ""

# Install Python dependencies
echo "3. Installing Python dependencies..."
pip3 install -r requirements.txt
echo "   OK"
echo ""

# Check Bluetooth service
echo "4. Checking Bluetooth service..."
systemctl status bluetooth 2>/dev/null | grep -q "active (running)" && echo "   Bluetooth is running" || sudo systemctl start bluetooth
echo ""

# Check if constants are available
echo "5. Testing Bluetooth constants..."
python3 -c "import socket; print('AF_BLUETOOTH:', socket.AF_BLUETOOTH); print('BTPROTO_RFCOMM:', socket.BTPROTO_RFCOMM)" 2>/dev/null && echo "   OK" || { echo "   FAILED - Try reinstalling: pip3 install --force-reinstall pybluez"; }
echo ""

echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Pair your printer: bluetoothctl"
echo "2. Scan: python3 -m thermal_printer scan"
echo "3. Print: python3 -m thermal_printer print-text -m 98:B2:6A:F7:AD:50 -t 'Hello'"
