# Quick Start Guide

Get Vehicle-Telemetry running in 5 minutes on Raspberry Pi 5.

## Prerequisites

- Raspberry Pi 5 with Raspberry Pi OS (Bookworm)
- 7-inch HDMI monitor
- MPU6050 I2C sensor (wired to GPIO2/GPIO3)
- FC-33 speed sensor (wired to GPIO27)
- Python 3.9+

## Installation

```bash
# 1. Clone repository
git clone https://github.com/vishnuskandha/Vehicle-Telemetry.git
cd Vehicle-Telemetry

# 2. Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pygame python3-pip i2c-tools
pip3 install -r requirements.txt

# 3. Enable I2C & GPIO
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_gpio 0

# 4. Verify sensors
python3 i2c_scan.py
# Should show MPU6050 at 0x68 or 0x69

# 5. Reboot (autostart should kick in)
sudo reboot
```

## Dashboard Available

After reboot, the dashboard appears on HDMI0 automatically.

**See [README.md](README.md) for full documentation.**

---

## Manual Start

```bash
# Start dashboard
DISPLAY=:0 python3 sensors_dashboard.py

# Start logger (in another terminal)
python3 sensors_logger.py
```

## Check Logs

```bash
# Service logs
journalctl --user -u sensors-dashboard.service -n 20

# Data log
tail -20 sensors_log.csv
```

## Troubleshooting

See [docs/INSTALLATION.md](docs/INSTALLATION.md#troubleshooting)

---

Next: [INSTALLATION.md](docs/INSTALLATION.md) for detailed hardware setup.
