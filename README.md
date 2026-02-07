# Vehicle Telemetry

> Real-time vehicle sensor monitoring system for Raspberry Pi 5 with live dashboard UI.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%205-red.svg)](https://www.raspberrypi.com/)

---

## 🚀 Features

- **Live Sensor Dashboard** — Neumorphic Pygame UI @ 1280×720 @ 30 FPS
- **Multi-Sensor Support** — MPU6050 IMU + FC-33 speed sensor + DS3231 RTC
- **Real-Time Visualization** — Animated gauges, heading compass, vehicle status panel
- **Continuous Data Logging** — CSV export with 1-second sampling
- **Autostart** — Zero-config boot integration (XDG + systemd)
- **Modular Architecture** — Reusable sensor reader, clean separation of concerns

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Hardware](#-hardware)
- [Installation](#-installation)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ⚡ Quick Start

### 60-Second Setup

```bash
# 1. Clone repository
git clone https://github.com/vishnuskandha/Vehicle-Telemetry.git
cd Vehicle-Telemetry

# 2. Install dependencies
sudo apt-get update && sudo apt-get install -y python3-pygame python3-pip
pip3 install -r requirements.txt

# 3. Wire hardware (see wiring diagrams below)

# 4. Run dashboard
DISPLAY=:0 python3 sensors_dashboard.py
```

**Autostart on boot:** Already configured. Just reboot.

---

## 🔧 Hardware

### Supported Sensors

| Sensor | Interface | Purpose | Address |
|--------|-----------|---------|---------|
| **MPU6050** | I2C | 6-axis IMU (accel, gyro) | 0x68 / 0x69 |
| **FC-33** | GPIO27 | Speed sensor (pulse counting) | — |
| **DS3231** | I2C (optional) | Real-time clock | 0x68 |

### Wiring Diagram

```
┌─────────────────────────────────────────────┐
│        Raspberry Pi 5                       │
└─────────────────────────────────────────────┘

I2C (GPIO2/SDA, GPIO3/SCL):
  ├─ MPU6050    (0x68)  ← 3.3V, GND
  └─ DS3231     (0x68)  ← 3.3V, GND (optional)

GPIO27 (pin 13):
  └─ FC-33 speed sensor → GND, 5V

Power:
  5V  ← RPi power pin
  GND ← Multiple pins available
```

**Full wiring details:** See [INSTALLATION.md](docs/INSTALLATION.md)

---

## 📦 Installation

### Prerequisites

- **Hardware:** Raspberry Pi 5 (or Pi 4B+)
- **OS:** Raspberry Pi OS (Bookworm) with desktop
- **Display:** 7-inch HDMI monitor (1280×720)
- **Python:** 3.9+

### Step-by-Step

```bash
# 1. Enable I2C & GPIO in raspi-config
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_gpio 0

# 2. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pygame python3-pip i2c-tools

# 3. Install Python packages
pip3 install -r requirements.txt

# 4. Run verification
python3 -c "from sensors_reader import SensorReader; print('✓ Imports OK')"

# 5. Scan I2C bus (verify MPU6050 detected)
i2cdetect -y 1

# 6. Reboot to enable autostart
sudo reboot
```

**Troubleshooting:** See [INSTALLATION.md](docs/INSTALLATION.md#troubleshooting)

---

## 💻 Usage

### Run Dashboard

```bash
# Manual start (foreground)
DISPLAY=:0 python3 sensors_dashboard.py

# Background start
DISPLAY=:0 nohup python3 sensors_dashboard.py &

# Via systemd service
systemctl --user start sensors-dashboard.service
```

### Run Logger (Optional)

```bash
# Start CSV data logging
python3 sensors_logger.py

# Data saved to: sensors_log.csv
tail sensors_log.csv
```

### Dashboard Controls

| Key | Action |
|-----|--------|
| **ESC / Q** | Exit fullscreen |
| **Ctrl+C** | Force quit (terminal) |

### Dashboard Display

```
┌─────────────────────────────────────────────────┐
│  RPM Gauge    Accel Gauge    Heading Ring  Status│
│  ┌────────┐   ┌────────┐    ┌────────┐   │Panel│
│  │        │   │        │    │   45°  │   │     │
│  │ 1200   │   │ 2.5m/s²│    │ (N)    │   │RPM  │
│  │ RPM    │   │ ACCEL  │    │HEADING │   │Accel│
│  └────────┘   └────────┘    └────────┘   │Head │
│                                            │└─────│
│ [●] 2026-02-07 13:50:42 | System Clock       │
└─────────────────────────────────────────────────┘
```

**Gauge Ranges:**
- RPM: 0–3000
- Acceleration: 0–20 m/s²
- Heading: 0–360°

---

## 🏗️ Architecture

### Project Structure

```
vehicle-telemetry/
├── sensors_reader.py         # Sensor abstraction layer (440 lines)
├── sensors_dashboard.py      # Pygame UI (550 lines)
├── sensors_logger.py         # CSV logger (50 lines)
├── start-dashboard.sh        # Boot wrapper
├── sensors_log.csv           # Data output (auto-generated)
├── i2c_scan.py              # Debug utility
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Dev tools (pytest, black, flake8)
├── LICENSE                   # MIT
├── .gitignore               # Git ignore rules
├── .editorconfig            # Editor settings
└── docs/
    ├── ARCHITECTURE.md      # System design
    ├── INSTALLATION.md      # Hardware setup
    ├── USAGE.md            # Operational guide
    ├── COMMANDS.md         # CLI reference
    └── GITHUB.md           # Contribution guidelines
```

### Data Flow

```
Hardware (I2C, GPIO)
    ↓
SensorReader (shared abstraction)
    ├─→ Dashboard UI (real-time visualization)
    └─→ Logger (CSV export)
```

### Key Classes

- **`SensorReader`** — Orchestrates I2C/GPIO reads, applies calibration
- **`CircularGauge`** — Pygame widget for RPM, acceleration display
- **`ProgressRing`** — Circular heading indicator
- **`Dashboard`** — Main app, event loop, rendering

**Full architecture details:** See [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, components, data flow patterns |
| [INSTALLATION.md](docs/INSTALLATION.md) | Hardware wiring, dependency installation, first-boot setup |
| [USAGE.md](docs/USAGE.md) | Dashboard operation, logger workflows, data analysis |
| [COMMANDS.md](docs/COMMANDS.md) | CLI reference, systemd control, debugging commands |
| [GITHUB.md](docs/GITHUB.md) | Repository structure, branching, PR guidelines |

Start here: **[INSTALLATION.md](docs/INSTALLATION.md)** for setup

---

## 🆘 Troubleshooting

### Common Issues

#### Dashboard Won't Start

```bash
# Check display is running
DISPLAY=:0 xrandr
# Expected: HDMI-A-1 connected 1280x720

# Manual start with output
DISPLAY=:0 python3 sensors_dashboard.py
# Look for Python errors
```

#### I2C Device Not Detected

```bash
# Verify I2C is enabled
i2cdetect -y 1
# Expected: 0x68 or 0x69 listed

# Check wiring: SDA (GPIO2), SCL (GPIO3), 3.3V, GND
# Verify pull-ups (10 kΩ recommended on SDA/SCL)
```

#### CSV Not Updating

```bash
# Verify logger is running
ps aux | grep sensors_logger

# Check file permissions
ls -la sensors_log.csv

# Start manually
python3 sensors_logger.py
```

**More troubleshooting:** See [INSTALLATION.md § Troubleshooting](docs/INSTALLATION.md#troubleshooting)

---

## 🧪 Testing

### Run Test Suite

```bash
pip3 install -r requirements-dev.txt
pytest -v
pytest --cov=sensors --cov-report=html
```

### Manual Hardware Test

```bash
# Test I2C connection
python3 << 'EOF'
import board, busio, adafruit_mpu6050
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_mpu6050.MPU6050(i2c)
print(f"Accel: {sensor.acceleration}")
print(f"Gyro: {sensor.gyro}")
EOF

# Test GPIO speed sensor
python3 << 'EOF'
import lgpio
chip = lgpio.gpiochip_open(0)
for i in range(10):
    print(lgpio.gpio_read(chip, 27))
lgpio.gpiochip_close(chip)
EOF
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Sensor polling | 1.0 Hz (1 second) |
| Display refresh | 30 FPS |
| End-to-end latency | ~1–2 seconds |
| CPU usage | 3–4% (Pi 5) |
| Memory | ~150 MB |
| CSV growth | ~100 KB/min |

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/cool-feature`)
3. **Test** on Raspberry Pi 5 with real hardware
4. **Commit** with clear messages (`git commit -m "Add feature X"`)
5. **Push** to your fork (`git push origin feature/cool-feature`)
6. **Open a Pull Request** with description + testing notes

**Guidelines:** See [GITHUB.md § Contributing](docs/GITHUB.md#contributing)

### Development Setup

```bash
git clone https://github.com/vishnuskandha/Vehicle-Telemetry.git
cd Vehicle-Telemetry

python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Code quality checks
black sensors/
flake8 sensors/
mypy sensors/
pytest
```

---

## 📝 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

Free to use, modify, and distribute with attribution.

---

## 🙋 Support

- **Issues:** [GitHub Issues](https://github.com/vishnuskandha/Vehicle-Telemetry/issues)
- **Discussions:** [GitHub Discussions](https://github.com/vishnuskandha/Vehicle-Telemetry/discussions)
- **Docs:** Start with [INSTALLATION.md](docs/INSTALLATION.md)

---

## 📌 Roadmap

- [ ] Web dashboard (Flask/Dash alternative)
- [ ] Mobile app integration (Bluetooth broadcast)
- [ ] Data export (Excel, JSON)
- [ ] Sensor calibration wizard
- [ ] Multi-vehicle support
- [ ] Cloud logging (optional)

---

## 🏆 Highlights

✨ **Modern UI** — Dark neumorphic design inspired by truck gauges  
⚡ **Real-Time** — 30 FPS fullscreen @ 1280×720  
🔧 **Modular** — Reusable sensor reader for other projects  
📊 **Data Ready** — CSV export for analysis (pandas/matplotlib)  
🚀 **Zero Config** — Autostart on boot, no manual setup on subsequent runs  

---

## 👨‍💻 Author

Built for Raspberry Pi 5 in 2026.

Suitable for:
- Vehicle telemetry (truck, RC car, lorry)
- Educational robotics
- Sensor integration projects
- Real-time data visualization

---

## 🔗 Links

- [Raspberry Pi Official Docs](https://www.raspberrypi.com/documentation/)
- [Adafruit Blinka](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [MPU6050 Datasheet](https://invensense.tdk.com/products/motion-tracking/6-axis/)

---

**Questions?** Check [INSTALLATION.md](docs/INSTALLATION.md) or open an [issue](https://github.com/vishnuskandha/Vehicle-Telemetry/issues).

