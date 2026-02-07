#!/bin/bash
# Wrapper script to ensure display is ready before launching dashboard
set -e

# Wait for display to be ready
for i in {1..30}; do
    if [ -S /run/user/1000/wayland-0 ] || [ -e /tmp/.X11-unix/X0 ]; then
        break
    fi
    sleep 1
done

# Set up environment
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority

# Change to sensors directory
cd /home/pi/Desktop/sensors

# Run the dashboard
exec python3 /home/pi/Desktop/sensors/sensors_dashboard.py
