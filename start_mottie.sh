#!/bin/bash
# Launcher used by the systemd unit (mottie.service).
exec 2>/tmp/mottie.log
set -x
echo "Starting MOTTIE"

export PYTHONPATH=/home/moth/.local/lib/python3.9/site-packages/
cd /home/moth/mothcam/
sudo PYTHONPATH=$PYTHONPATH python3 main.py
