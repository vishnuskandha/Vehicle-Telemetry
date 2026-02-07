# Changelog

All notable changes to Vehicle Telemetry are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for alternative I2C addresses (0x69 for MPU6050 AD0 variant)
- Configurable sensor polling interval
- Data export functionality (CSV, Excel)

### Changed
- Improved gauge smoothing algorithm (SMOOTHING=0.18)
- Refactored sensors_reader.py for better extensibility

### Fixed
- Heading drift on long-duration trips (>30 min)

### Deprecated
- Old Tkinter UI (will be removed in v2.0)

---

## [1.0.0] - 2026-02-07

### Added
- **Initial Release**

#### Core Features
- Real-time Pygame dashboard UI (1280×720 @ 30 FPS)
- Neumorphic dark theme with circular gauges
- Live sensor monitoring (MPU6050, FC-33, DS3231)
- Continuous CSV data logging (1 Hz)
- Autostart on boot (XDG + systemd)

#### Hardware Support
- MPU6050 6-axis IMU (acceleration, gyro, temperature)
- FC-33 speed sensor (GPIO27 pulse counting)
- DS3231 Real-Time Clock (optional, I2C)

#### UI Components
- **RPM Gauge** — Animated needle, 0–3000 RPM range
- **Acceleration Gauge** — 0–20 m/s² horizontal acceleration
- **Heading Ring** — 360° compass with cardinal directions
- **Vehicle Status Panel** — Summary metrics + RTC indicator
- **Status Bar** — Connection status, timestamp, clock source

#### Infrastructure
- Shared `SensorReader` class (hardware abstraction)
- Modular architecture (hardware → reader → logger/UI)
- Hardware-specific drivers (I2C, GPIO)
- Comprehensive documentation suite
- Development tools (pytest, black, flake8, mypy)

#### Documentation
- [README.md](README.md) — Feature overview & quick start
- [INSTALLATION.md](docs/INSTALLATION.md) — Hardware setup & wiring
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — System design & components
- [USAGE.md](docs/USAGE.md) — Dashboard operation & data analysis
- [COMMANDS.md](docs/COMMANDS.md) — CLI reference & troubleshooting
- [GITHUB.md](docs/GITHUB.md) — Repository & contribution guidelines
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contributor guidelines

#### Configuration
- `.gitignore` — Git ignore rules
- `LICENSE` — MIT License
- `.editorconfig` — Cross-editor code style
- `requirements.txt` — Production dependencies
- `requirements-dev.txt` — Development tools

### Performance Metrics
- Sensor polling: 1.0 Hz
- Display refresh: 30 FPS (33 ms/frame)
- Dashboard CPU: 3–4% on Raspberry Pi 5
- Dashboard RAM: ~150 MB
- CSV growth: ~100 KB/min

### Testing
- Manual hardware tests on Raspberry Pi 5
- I2C device detection verified
- GPIO pulse counting verified
- Wayland/X11 display compatibility confirmed
- CSV logging append-mode verified

### Known Limitations
- Heading drift ~1°/min without calibration (expected)
- Single vehicle instance (not multi-vehicle)
- No web/mobile UI (desktop fullscreen only)
- No cloud logging (local CSV only)

### Hardware Requirements
- Raspberry Pi 5 (or Pi 4B+ for reduced performance)
- 7-inch HDMI display (1280×720)
- Python 3.9+
- I2C & GPIO enabled on Pi

---

## Version History

### v0.1 - Initial Development (private)
- Tkinter prototype dashboard (non-functional)
- Proof-of-concept sensor reader

### v0.2 - Pygame Rewrite (private)
- Complete dashboard rewrite using Pygame
- Hardware-accelerated fullscreen rendering
- Neumorphic design implementation

### v0.3 - Autostart Integration (private)
- XDG desktop autostart (.desktop entry)
- Systemd user service (fallback)
- Bootstrap script for display detection

### v1.0 - Public Release (2026-02-07)
- Full documentation suite
- GitHub repository ready
- Contributing guidelines
- Release management setup

---

## Future Roadmap

### v1.1.0 (Next Minor)
- [ ] Web dashboard (Flask/Dash)
- [ ] Mobile app integration (Bluetooth)
- [ ] Data export (Excel, JSON)
- [ ] Sensor calibration wizard

### v2.0.0 (Major)
- [ ] Multi-vehicle support
- [ ] Cloud logging (optional AWS/Azure)
- [ ] Advanced analytics (pandas integration)
- [ ] Remove deprecated Tkinter code

### Backlog
- [ ] Voice alerts (high RPM, high accel)
- [ ] GPS integration (optional)
- [ ] OBD-II support (car diagnostics)
- [ ] 3D vehicle visualization

---

## How to Update

Check the latest version:
```bash
git log --oneline | head -5
git describe --tags
```

Update to latest:
```bash
git fetch origin
git pull origin main
pip install -r requirements.txt
```

## Support

- Report bugs: [GitHub Issues](https://github.com/vishnuskandha/Vehicle-Telemetry/issues)
- Questions: [GitHub Discussions](https://github.com/vishnuskandha/Vehicle-Telemetry/discussions)
- Contribute: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Maintained by:** Vehicle Telemetry Contributors  
**License:** MIT  
**Repository:** https://github.com/vishnuskandha/Vehicle-Telemetry
