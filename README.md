# Vehicle Telemetry

Real-time vehicle sensor monitoring system for Raspberry Pi 5 with a live dashboard UI.

[![CI](https://github.com/vishnuskandha/Vehicle-Telemetry/actions/workflows/ci.yml/badge.svg)](https://github.com/vishnuskandha/Vehicle-Telemetry/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%205-red.svg)](https://www.raspberrypi.com/)

## Overview

Vehicle Telemetry turns a Raspberry Pi 5 into a live vehicle monitoring dashboard.
A neumorphic, fullscreen Pygame UI (1280 x 720 @ 30 FPS) renders RPM, horizontal
acceleration, and heading from an MPU6050 IMU and an FC-33 speed sensor, while a
logger writes one-second samples to CSV. The system autostarts on boot with no
manual setup on subsequent runs.

The detailed documentation is maintained separately:

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](QUICKSTART.md) | Get running in about five minutes |
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | Hardware wiring, dependencies, first-boot setup |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, components, data flow |
| [docs/USAGE.md](docs/USAGE.md) | Dashboard operation, logger workflows, data analysis |
| [docs/COMMANDS.md](docs/COMMANDS.md) | CLI reference, systemd control, debugging |
| [docs/GITHUB.md](docs/GITHUB.md) | Repository structure, branching, PR guidelines |
| [CHANGELOG.md](CHANGELOG.md) | Version history and roadmap |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |

## Features

- Live sensor dashboard: neumorphic Pygame UI at 1280 x 720, 30 FPS
- Multi-sensor support: MPU6050 IMU, FC-33 speed sensor, DS3231 RTC
- Real-time visualization: animated gauges, heading compass, vehicle status panel
- Continuous data logging: CSV export with one-second sampling
- Autostart on boot: zero-config XDG + systemd integration
- Modular architecture: shared sensor reader, clean separation of concerns

## Quick start

Follow [QUICKSTART.md](QUICKSTART.md) for the guided setup. In short:

```bash
git clone https://github.com/vishnuskandha/Vehicle-Telemetry.git
cd Vehicle-Telemetry

# Install system and Python dependencies
sudo apt-get update && sudo apt-get install -y python3-pygame python3-pip i2c-tools
pip3 install -r requirements.txt

# Run the dashboard (from the Pi desktop session)
DISPLAY=:0 python3 sensors_dashboard.py
```

Autostart on boot is already configured; a reboot starts the dashboard automatically.

## Hardware

| Sensor | Interface | Purpose | Address |
|--------|-----------|---------|---------|
| MPU6050 | I2C | 6-axis IMU (accel, gyro) | 0x68 / 0x69 |
| FC-33 | GPIO27 | Speed sensor (pulse counting) | - |
| DS3231 | I2C (optional) | Real-time clock | 0x68 |

Full wiring details and a diagram are in [docs/INSTALLATION.md](docs/INSTALLATION.md).

## Usage

```bash
# Dashboard (foreground)
DISPLAY=:0 python3 sensors_dashboard.py

# CSV logger
python3 sensors_logger.py

# Debug: scan the I2C bus for attached devices
python3 i2c_scan.py
```

Dashboard controls: ESC / Q exits fullscreen; Ctrl+C force-quits from a terminal.
See [docs/USAGE.md](docs/USAGE.md) and [docs/COMMANDS.md](docs/COMMANDS.md) for full details.

## Testing

Tests run on any host (no Raspberry Pi hardware required). Hardware modules are
stubbed and the pure logic is verified with pytest:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q tests/
```

The suite covers two's-complement conversion, the speed/RPM math, gauge value
clamping, and the color helpers used by the dashboard. A byte-compile check
(`python3 -m py_compile sensors_*.py i2c_scan.py`) verifies syntax everywhere.
CI runs the same checks on every push and pull request.

## Project layout

```
sensors_reader.py         # Sensor abstraction layer (MPU6050, FC-33, DS3231)
sensors_dashboard.py      # Pygame dashboard UI
sensors_logger.py         # CSV data logger
i2c_scan.py               # I2C bus debug utility
start-dashboard.sh        # Boot wrapper script
tests/test_smoke.py       # Host-agnostic smoke tests
docs/                     # Architecture, installation, usage, commands, GitHub guide
requirements.txt          # Runtime dependencies
requirements-dev.txt      # Development tools (pytest, black, flake8, mypy)
QUICKSTART.md             # Five-minute setup guide
CHANGELOG.md              # Version history and roadmap
CONTRIBUTING.md           # Contribution guidelines
```

`sensors_log.csv` is generated at runtime and ignored by git.

## Performance

| Metric | Value |
|--------|-------|
| Sensor polling | 1.0 Hz (1 second) |
| Display refresh | 30 FPS |
| End-to-end latency | ~1-2 seconds |
| CPU usage | 3-4% (Pi 5) |
| Memory | ~150 MB |
| CSV growth | ~100 KB/min |

## Troubleshooting

Common issues (dashboard won't start, I2C device not detected, CSV not updating)
are covered in [docs/INSTALLATION.md](docs/INSTALLATION.md#troubleshooting).

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full
guidelines, the [Security Policy](SECURITY.md), and [docs/GITHUB.md](docs/GITHUB.md)
for repository and PR guidelines.

## License

MIT — see [LICENSE](LICENSE).
