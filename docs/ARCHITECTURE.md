# System Architecture

## Overview

The Sensor Dashboard is a real-time monitoring system for vehicle telemetry data acquired from MPU6050 (6-axis IMU) and FC-33 speed sensors. The system runs on a Raspberry Pi 5 and displays live data on a 7-inch HDMI monitor via a modern neumorphic GUI.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SENSOR DASHBOARD SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌──────────────────┐
│   MPU6050 IMU   │         │   FC-33 Speed    │
│  (I2C 0x68/0x69)│         │   Sensor (GPIO27)│
│                 │         │                  │
│ - Accel (xyz)   │         │ - Pulses/second  │
│ - Gyro (xyz)    │         │ - 40 pulses/rev  │
│ - Temperature   │         │                  │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         │ I2C Bus                   │ GPIO Int.
         │                           │
         └───────────┬───────────────┘
                     │
         ┌───────────▼────────────┐
         │   SensorReader Module   │  (sensors_reader.py)
         │  ─────────────────────  │
         │ • SpeedCounter class    │ - Poll sensors @ 1 Hz
         │ • RawMPU class          │ - Raw I2C register reads
         │ • RTC/DS3231 support    │ - Calculates RPM, accel, yaw
         │ • Data dict return      │
         └───────────┬────────────┘
                     │
         ┌───────────┴──────────────┬──────────────┐
         │                          │              │
    ┌────▼──────┐         ┌────────▼──┐    ┌─────▼─────────┐
    │  Logger   │         │ Dashboard  │    │ CSV Log File  │
    │(sensors_  │         │ (sensors_  │    │(sensors_log   │
    │logger.py) │         │dashboard.  │    │.csv)          │
    │           │         │py)         │    │               │
    │ • 1s loop │         │            │    │ Metrics:      │
    │ • CSV     │         │ • Pygame   │    │ - timestamp   │
    │   write   │         │   fullscreen    │ - RPM         │
    │ • Print   │         │ • 30 FPS   │    │ - accel       │
    │   live    │         │ • Neumor  │    │ - heading     │
    │           │         │   phic UI  │    │               │
    │ Shared    │         │ • HDMI0    │    │ Optional CSV  │
    │ reader    │         │   fullscreen    │ analysis      │
    └───────────┘         └────────────┘    └───────────────┘
         │                      │
         │ Uses              Uses
         │                      │
         └──────────┬───────────┘
                    │
         ┌──────────▼──────────────┐
         │  Autostart Scheduler    │
         │ ─────────────────────── │
         │ ~/.config/autostart/    │
         │   sensors-dashboard     │
         │   .desktop              │
         │                         │
         │ Executes start-         │
         │ dashboard.sh on boot    │
         └────────────────────────┘

```

---

## Component Breakdown

### 1. **Sensor Reader** (`sensors_reader.py`)

**Purpose:** Abstracts hardware I2C/GPIO communication and performs real-time sensor math.

**Key Classes:**

- **`SpeedCounter`** — GPIO edge-counting for speed pulses
  - Supports `lgpio` (preferred) and fallback to `RPi.GPIO`
  - Counts both rising and falling edges for 40-pulse-per-revolution wheel
  - Calculates RPM from elapsed time and pulse count per window

- **`RawMPU`** — Raw I2C register reads for MPU6050/6500/9250
  - WHO_AM_I detection at 0x68 or 0x69
  - 6-byte accel reads → (ax, ay, az) in m/s²
  - 6-byte gyro reads → (gx, gy, gz) in rad/s
  - LSB-to-physical conversions (±2g accel, ±250°/s gyro)

- **`SensorReader`** — Main orchestrator
  - `.setup()` initializes I2C, MPU, RTC, GPIO
  - `.read()` returns dict: `{rpm, horiz_accel, yaw_deg, timestamp, rtc_active, ...}`
  - Maintains internal yaw integration state
  - Shared by both logger and dashboard

**I2C Addresses:**
- MPU6050: **0x68** (default) or **0x69** (AD0 high)
- DS3231 RTC: **0x68** (optional; conflicts with MPU if both at 0x68)

---

### 2. **Data Logger** (`sensors_logger.py`)

**Purpose:** Continuous data acquisition to CSV for post-analysis.

**Flow:**
1. Instantiate `SensorReader` with `print_live=True`
2. Poll at 1-second interval (configurable via `SAMPLE_INTERVAL_S`)
3. Write to CSV with header: `timestamp, speed(rpm), horizontal acceleration, gyro heading`
4. Flush each row for reliability

**Output:** `/home/pi/Desktop/sensors/sensors_log.csv`

**Use Cases:**
- Long-duration vehicle telemetry logging
- Data export for analysis in Python/Excel/MATLAB
- Post-trip playback and debugging

---

### 3. **Dashboard UI** (`sensors_dashboard.py`)

**Purpose:** Real-time fullscreen visual display on 7-inch HDMI monitor.

**Technology Stack:**
- **Pygame 2.6+** — Hardware-accelerated rendering, low-level drawing
- **Native fullscreen (1280×720)** — No desktop environment needed
- **30 FPS refresh rate** — Smooth animations

**Widget Architecture:**

1. **`CircularGauge`** (RPM & Acceleration)
   - Neumorphic dark bezel design (inspired by truck dashboards)
   - Orange-to-red gradient arc indicating fill level
   - Animated needle (for RPM) or arc (for accel)
   - Tick marks and numeric labels
   - Layout: left (RPM), center (accel)

2. **`ProgressRing`** (Heading/Compass)
   - 360° circular progress ring
   - Gradient fill showing heading angle
   - Compass direction (N, NE, E, ..., NW)
   - Right-center layout

3. **`InfoPanel`** (Vehicle Status Card)
   - Dark rounded panel (neumorphic style)
   - Summary of RPM, accel, heading, RTC status
   - Red accent dot (design element)
   - Far-right layout

4. **Status Bar** (Bottom)
   - Timestamp + RTC/system clock indicator
   - Green/red connection LED
   - Low-overhead monitoring

**Color Palette:**
- **Background:** Dark gray (30, 30, 35)
- **Panels:** Slightly lighter gray (38–50, 38–50, 44–58)
- **Accents:** Orange→Red gradient (255,150,50 → 230,60,60)
- **Text:** Light gray/white (240–255, 240–255, 245–255)

**Update Cycle:**
```
┌──────────────────────────────────┐
│ 1. Poll sensors (every 1.0 sec)  │
│    └→ read() returns data dict   │
├──────────────────────────────────┤
│ 2. Smooth values (exponential)   │
│    └→ display = display + k·Δ    │
├──────────────────────────────────┤
│ 3. Render at 30 FPS              │
│    └→ pygame.display.flip()      │
└──────────────────────────────────┘
```

---

### 4. **Autostart Mechanism**

**Primary:** XDG Desktop Autostart
- File: `~/.config/autostart/sensors-dashboard.desktop`
- Launched by `labwc` (Wayland compositor) on session start
- Delay: 2 seconds (allows desktop stabilization)

**Bootstrap Script:** `start-dashboard.sh`
- Waits up to 30 seconds for display socket to appear
- Sets `DISPLAY=:0` and `XAUTHORITY`
- Executes Python dashboard process

**Fallback:** Systemd user service (optional)
- File: `~/.config/systemd/user/sensors-dashboard.service`
- Auto-restarts on crash
- Less reliable on Wayland but provides journalctl logging

---

## Data Flow Diagram

```
Hardware Events
     │
     ├──→ [I2C Bus] → MPU6050 (6-axis data)
     │
     └──→ [GPIO27] → FC-33 (speed pulses)
          │
          ▼
     [SensorReader.read()]
          │
          ├─→ RPM calculation (pulses/elapsed time)
          ├─→ Horizontal accel magnitude √(ax² + ay²)
          ├─→ Yaw integration ∫ gz · dt
          └─→ Timestamp (RTC or system)
                  │
          ┌───────┴─────────┐
          │                 │
          ▼                 ▼
    [Sensors_Logger]   [Dashboard UI]
          │                 │
          └─→ CSV File      └─→ HDMI0 Display
                                   │
                        ┌──────────┴──────────┐
                        │                     │
                   [Gauge]            [Status Panel]
                   - Needle           - Vehicle info
                   - Arc fill         - RTC indicator
                   - Ticks            - Connection LED
                   - Numbers
```

---

## Computing Model

### Real-Time Constraints

| Metric | Value | Notes |
|--------|-------|-------|
| Sensor poll interval | 1.0 s | Python `time.sleep(1.0)` |
| Display refresh | 30 FPS | ~33 ms per frame |
| Dashboard update latency | 100 ms | Can exhibit up to 1 frame lag |
| RPM glitch-free window | 1.0 s | Pulse counting window |
| Heading integration drift | ~1°/min | Gyro bias accumulation (uncalibrated) |

### CPU & Memory Usage

- **Pygame Dashboard:** ~3–4% CPU, ~150 MB RAM
- **Logger Script:** ~0.5% CPU, ~30 MB RAM
- **Idle system:** Both can run concurrently without throttling on Pi 5

---

## Fault Tolerance

### Sensor Failures

| Failure Mode | Behavior |
|---|---|
| **MPU6050 not found** | Dashboard displays error; exits gracefully |
| **GPIO not available** | Speed reads as 0; system continues |
| **I2C bus hang** | Timeout after ~1 sec; next read retried |
| **RTC unavailable** | Falls back to system clock; displays "System Clock" |

### Display Loss

| Scenario | Behavior |
|---|---|
| **HDMI cable disconnected** | Dashboard crashes; systemd restarts in 10 sec |
| **Display turned off** | Pygame fills buffer; no visible crash |
| **Wayland compositor crash** | Autostart doesn't retrigger; manual restart needed |

---

## Configuration & Tuning

### MPU6050 Address Conflict

If both MPU6050 and DS3231 use 0x68:
1. Move MPU6050 AD0 pin to 3.3V (addresses it to 0x69)
2. Or disable RTC in `sensors_reader.py`

### Speed Sensor Calibration

- **`PULSES_PER_REV`** = 40 (FC-33 typical)
- Adjust for different wheel encoders or gear ratios
- RPM = (pulses / PULSES_PER_REV) / elapsed_time × 60

### Display Resolution

- **Designed for:** 1280×720 (7-inch 16:9)
- **Scales to:** Any resolution (proportional scaling via `self.s` factor)
- For 1920×1080, layouts may overlap; adjust widget positions in `_build_widgets()`

### Smoothing Factor

- **`SMOOTHING = 0.18`** in `sensors_dashboard.py`
- Higher → more responsive (0.3–0.5)
- Lower → smoother (0.05–0.1)

---

## Extension Points

### Adding a New Sensor

1. Add read logic to `SensorReader` (or subclass)
2. Update `read()` dict return with new key
3. Add widget in `Dashboard._build_widgets()`
4. Draw widget in `Dashboard._draw()`
5. Update `_update()` to smooth new values

### Adding Custom Logging

1. Extend CSV columns in `sensors_logger.py` header
2. Append values in `writer.writerow()` call
3. Post-process CSV in analysis script

### Custom Dashboard Theme

1. Edit color constants in `sensors_dashboard.py`
2. Adjust widget positions in `_build_widgets()`
3. Redraw logic in widget `.draw()` methods (Pygame `gfxdraw` calls)

---

## Dependency Graph

```
sensors_dashboard.py
    ├─ pygame 2.6+
    ├─ board (Adafruit Blinka)
    ├─ busio (Adafruit Blinka)
    ├─ sensors_reader.py
    │   ├─ board
    │   ├─ busio
    │   ├─ adafruit_ds3231 (optional)
    │   ├─ lgpio (preferred) or RPi.GPIO
    │   └─ math, time, datetime
    └─ math (stdlib)

sensors_logger.py
    ├─ csv (stdlib)
    ├─ time (stdlib)
    └─ sensors_reader.py [as above]

start-dashboard.sh
    └─ /usr/bin/python3
        └─ sensors_dashboard.py

Autostart:
    ~/.config/autostart/sensors-dashboard.desktop
        └─ start-dashboard.sh
            └─ Dashboard @ DISPLAY=:0
```

---

## Performance Profiling

### Expected Latency Chain

```
Hardware event (MPU accel change)
    ↓ (0–1 ms I2C)
Sensor register
    ↓ (0–2 ms SPI/I2C read)
sensors_reader.read() dict
    ↓ (1000 ms wait for next poll)
Dashboard _poll_sensors()
    ↓ (2 ms smoothing/update)
Gauge.update()
    ↓ (33 ms until next frame)
Pygame render + flip
    ↓ (0–16 ms display scanout)
7-inch HDMI monitor physical update
────────────────────────────────
Total end-to-end: ~1050–1150 ms (worst case)
```

This is acceptable for telemetry; not suitable for real-time control.

---

## Troubleshooting Reference

| Symptom | Check |
|---|---|
| Dashboard won't start | `DISPLAY=:0 python3 sensors_dashboard.py` (manual test) |
| Sensor not detected | `python3 /home/pi/Desktop/sensors/i2c_scan.py` |
| Autostart fails | `~/.config/autostart/sensors-dashboard.desktop` exists & executable |
| CSV not updating | Check file permissions on `/home/pi/Desktop/sensors/` |
| Display shows error | Check sensor wiring; run hardware check script |
| High CPU usage | Reduce FPS or optimize Pygame rendering |

---

## Summary Table

| Component | Language | Type | I/O | Lifecycle |
|---|---|---|---|---|
| `sensors_reader.py` | Python 3 | Module | I2C, GPIO | Imported |
| `sensors_dashboard.py` | Python 3 | App | Hardware, HDMI | PIDs 4774+ (autostart) |
| `sensors_logger.py` | Python 3 | App | Hardware, CSV | Manual or systemd |
| `start-dashboard.sh` | Bash | Script | Spawns Python | Called by autostart |

