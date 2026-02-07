# Usage Guide

How to operate the Sensor Dashboard, logger, and data analysis tools.

---

## Table of Contents

1. [Dashboard Operation](#dashboard-operation)
2. [Data Logger](#data-logger)
3. [Common Workflows](#common-workflows)
4. [Data Analysis](#data-analysis)
5. [Tips & Tricks](#tips--tricks)

---

## Dashboard Operation

### Starting the Dashboard

#### Automatic (Autostart on Boot)

The dashboard launches automatically 2 seconds after the Wayland desktop starts:

```bash
sudo reboot
# Wait 5–10 seconds for HDMI monitor to show gauges
```

#### Manual Launch

```bash
# From terminal on Pi or SSH
DISPLAY=:0 python3 /home/pi/Desktop/sensors/sensors_dashboard.py

# Or via wrapper script
/home/pi/Desktop/sensors/start-dashboard.sh
```

### Dashboard Controls

| Input | Action |
|-------|--------|
| **ESC key** | Exit fullscreen, return to desktop |
| **Q key** | Exit fullscreen (same as ESC) |
| **Ctrl+C** (in terminal) | Force quit if unresponsive |
| **Click anywhere** | No effect (fullscreen; mouse hidden) |

### Understanding the Display

#### Layout Overview

The dashboard displays four main elements:

1. **RPM Gauge** (left, large)
   - Circular needle gauge, 0–3000 RPM
   - Orange-to-red gradient arc indicates fill
   - Animated needle follows throttle/rotation speed
   - Label: "ENGINE RPM"

2. **Acceleration Gauge** (center-left, medium)
   - Circular gauge, 0–20 m/s² horizontal
   - Shows lateral+longitudinal movement magnitude
   - Label: "ACCEL m/s²"

3. **Heading Ring** (center-right)
   - 360° circular progress ring
   - Compass with N, NE, E, SE, S, SW, W, NW
   - Shows gyro-integrated heading angle
   - Label: "HEADING deg"

4. **Vehicle Status Panel** (far right, dark card)
   - Summary of all key metrics
   - Real-time RTC or system clock status
   - Green/red connection indicator

#### Color Meanings

| Color | Meaning |
|-------|---------|
| **Orange-Red gradient** | Active gauge fill (RPM, accel) |
| **Green** | Sensor connected & working |
| **Red** | Sensor error / disconnected |
| **Muted gray** | Labels & status text |
| **Bright white** | Numeric values |

### Interpreting the Gauges

#### RPM Gauge Behavior

- **0 RPM:** Vehicle stationary (or very slow)
- **1000–3000 RPM:** Normal driving speeds
- **Needle bounces:** Pulsing motion (acceleration/braking)

**Example:**
```
Stationary      Gentle accel     Heavy accel
    ↓               ↓                ↓
   0 RPM         ~500 RPM         ~2000 RPM
  (needle down) (needle mid)     (needle high)
```

#### Acceleration Gauge

- **0.0 m/s²:** Stationary or constant velocity (level road)
- **0.5–5.0 m/s²:** Moderate acceleration/turning
- **> 10 m/s²:** Hard acceleration or sharp cornering

**Example on level road:**
```
Stationary → Accelerate quickly → Braking
  0.1 m/s²       ~15 m/s²        ~5 m/s²
```

#### Heading Ring

- **0°:** North (magnetic or gyro-integrated)
- **90°:** East
- **180°:** South
- **270°:** West

**Note:** Heading is integrated from gyro Z-axis. It will drift ~1°/min without calibration (expected IMU behavior).

### Status Bar (Bottom)

```
[●] 2026-02-07 13:50:42  |  RTC: System Clock
│ color  timestamp        │  clock source
```

- **Green dot (●)** = Sensors connected & updating
- **Red dot (●)** = Sensor error / disconnected
- **Timestamp** = Last update time
- **RTC / System Clock** = Which time source is active

---

## Data Logger

### Starting the Logger

```bash
cd ~/Desktop/sensors

# Manual start (blocks; shows live output)
python3 sensors_logger.py

# Background start (non-blocking)
nohup python3 sensors_logger.py > logger.log 2>&1 &
```

### Logger Output

Console output (if running interactively):
```
Logging to /home/pi/Desktop/sensors/sensors_log.csv
Press Ctrl+C to stop
Detected MPU-6500/9250 (WHO_AM_I=0x70). Using raw register reads.
2026-02-07 13:50:01 | rpm=  0.00 | pulses=  0 | window= 1.01s
2026-02-07 13:50:02 | rpm=120.50 | pulses= 40 | window= 1.02s
2026-02-07 13:50:03 | rpm=  0.00 | pulses=  0 | window= 1.00s
2026-02-07 13:50:04 | rpm=240.75 | pulses= 80 | window= 1.01s
```

### CSV Output Format

File: `/home/pi/Desktop/sensors/sensors_log.csv`

```
timestamp,speed(rpm),horizontal acceleration,gyro heading
2026-02-07 13:50:01,0.00,0.098,0.00
2026-02-07 13:50:02,120.50,1.234,15.23
2026-02-07 13:50:03,0.00,0.156,15.45
2026-02-07 13:50:04,240.75,2.456,31.67
2026-02-07 13:50:05,360.25,3.123,48.90
```

### Stopping the Logger

```bash
# If running in foreground
Ctrl+C

# If running in background
pkill -f "python3 sensors_logger.py"

# Kill by PID
kill 12345  # Replace 12345 with PID from ps aux
```

### Logger Management

**Run logger + dashboard simultaneously:**
```bash
# Terminal 1: Dashboard (interactive)
DISPLAY=:0 python3 sensors_dashboard.py

# Terminal 2: Logger (background)
python3 sensors_logger.py &
```

**Append to existing CSV:**
```bash
# Logger automatically appends if CSV exists
# To start fresh, delete and re-run:
rm sensors_log.csv
python3 sensors_logger.py
```

**Extract subset of data:**
```bash
# Get last 100 lines
tail -100 sensors_log.csv > trip_excerpt.csv

# Get lines only for 13:50–13:55
grep "13:5[0-5]" sensors_log.csv > trip_filtered.csv
```

---

## Common Workflows

### Workflow 1: Long Trip Monitoring

1. **Start logger in background:**
   ```bash
   nohup python3 sensors_logger.py > /tmp/logger.log 2>&1 &
   ```

2. **Dashboard auto-starts on boot** (or manual):
   ```bash
   DISPLAY=:0 python3 sensors_dashboard.py &
   ```

3. **Drive for desired duration** (30 minutes, 1 hour, etc.)

4. **Stop logger:**
   ```bash
   pkill -f sensors_logger
   ```

5. **Analyze data:**
   ```bash
   python3 << 'EOF'
   import pandas as pd
   df = pd.read_csv('sensors_log.csv')
   print(f"Trip duration: {len(df)} seconds = {len(df)/60:.1f} min")
   print(f"Max RPM: {df['speed(rpm)'].max():.1f}")
   print(f"Max accel: {df['horizontal acceleration'].max():.2f} m/s²")
   print(f"Heading range: {df['gyro heading'].min():.0f}° to {df['gyro heading'].max():.0f}°")
   EOF
   ```

### Workflow 2: Real-Time Monitoring Only (No Logging)

1. **Start dashboard:**
   ```bash
   DISPLAY=:0 python3 sensors_dashboard.py
   ```

2. **Watch gauges**

3. **Exit with ESC** when done

Data is NOT saved to CSV (logger not running).

### Workflow 3: Headless Service (No Monitor, Just CSV)

1. **Stop autostart (if you don't need dashboard):**
   ```bash
   rm ~/.config/autostart/sensors-dashboard.desktop
   ```

2. **Run logger as a background daemon:**
   ```bash
   nohup python3 sensors_logger.py > /tmp/logger.log 2>&1 &
   echo $! > /tmp/logger.pid  # Save PID for later
   ```

3. **Check status:**
   ```bash
   tail /tmp/logger.log
   tail sensors_log.csv
   ```

4. **Stop when done:**
   ```bash
   kill $(cat /tmp/logger.pid)
   ```

---

## Data Analysis

### Quick Stats (Python)

```python
import pandas as pd
import numpy as np

# Load CSV
df = pd.read_csv('sensors_log.csv')

# Convert to numeric (in case of formatting issues)
df['speed(rpm)'] = pd.to_numeric(df['speed(rpm)'], errors='coerce')
df['horizontal acceleration'] = pd.to_numeric(df['horizontal acceleration'], errors='coerce')
df['gyro heading'] = pd.to_numeric(df['gyro heading'], errors='coerce')

# Statistics
print("=== Trip Summary ===")
print(f"Duration: {len(df)} rows ({len(df)/60:.1f} minutes)")
print(f"\n=== Speed (RPM) ===")
print(f"  Min: {df['speed(rpm)'].min():.1f} RPM")
print(f"  Max: {df['speed(rpm)'].max():.1f} RPM")
print(f"  Mean: {df['speed(rpm)'].mean():.1f} RPM")
print(f"  Std Dev: {df['speed(rpm)'].std():.1f}")

print(f"\n=== Acceleration (m/s²) ===")
print(f"  Min: {df['horizontal acceleration'].min():.2f}")
print(f"  Max: {df['horizontal acceleration'].max():.2f}")
print(f"  Mean: {df['horizontal acceleration'].mean():.2f}")

print(f"\n=== Heading (degrees) ===")
print(f"  Min: {df['gyro heading'].min():.0f}°")
print(f"  Max: {df['gyro heading'].max():.0f}°")
print(f"  Change: {df['gyro heading'].iloc[-1] - df['gyro heading'].iloc[0]:.0f}°")
```

### Plotting (Matplotlib)

```python
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('sensors_log.csv')

fig, axes = plt.subplots(3, 1, figsize=(12, 8))

# RPM over time
axes[0].plot(range(len(df)), df['speed(rpm)'], label='RPM', color='orange')
axes[0].set_ylabel('RPM')
axes[0].set_title('Vehicle Speed Over Time')
axes[0].grid()
axes[0].legend()

# Acceleration
axes[1].plot(range(len(df)), df['horizontal acceleration'], label='Accel', color='blue')
axes[1].set_ylabel('m/s²')
axes[1].set_title('Horizontal Acceleration Over Time')
axes[1].grid()
axes[1].legend()

# Heading
axes[2].plot(range(len(df)), df['gyro heading'], label='Heading', color='green')
axes[2].set_ylabel('Degrees')
axes[2].set_xlabel('Time (seconds)')
axes[2].set_title('Gyro Heading Over Time')
axes[2].grid()
axes[2].legend()

plt.tight_layout()
plt.savefig('trip_analysis.png', dpi=100)
print("Saved to trip_analysis.png")
plt.show()
```

### Export to Excel

```python
import pandas as pd

df = pd.read_csv('sensors_log.csv')

# Add time column (0, 1, 2, ... , N seconds)
df['elapsed_seconds'] = range(len(df))

# Add computed columns
df['speed(rpm)_smooth'] = df['speed(rpm)'].rolling(window=3, center=True).mean()
df['accel_magnitude'] = df['horizontal acceleration'].abs()

# Export
df.to_excel('trip_data.xlsx', sheet_name='Telemetry', index=False)
print("Exported to trip_data.xlsx")
```

---

## Tips & Tricks

### Tip 1: Monitor Live CSV in Separate Terminal

```bash
watch -n 1 'tail -5 sensors_log.csv'
# Updates every 1 second, shows last 5 rows
```

### Tip 2: Redirect Dashboard to Different Display

If you have multiple HDMI outputs:

```bash
DISPLAY=:1 python3 sensors_dashboard.py
```

### Tip 3: Reduce Smoothing for Responsive Gauges

Edit `sensors_dashboard.py`:

```python
# Line ~56, change SMOOTHING factor
SMOOTHING = 0.3  # Higher = more responsive, less smooth
```

Then restart dashboard.

### Tip 4: Capture Screenshots

```bash
# Requires 'scrot' or 'gnome-screenshot'
scrot /tmp/dashboard_$(date +%s).png

# Or via Pygame (Python)
pygame.image.save(screen, 'screenshot.png')
```

### Tip 5: Rotate Heading Display for Different Orientations

If your vehicle's "forward" is not 0°, add offset:

Edit `sensors_dashboard.py`, in `_update()`:

```python
heading_offset = 90  # Change to match your setup
heading_val = (d.get("yaw_deg", 0.0) + heading_offset) % 360
```

### Tip 6: Disable RTC, Use Only System Clock

Edit `sensors_reader.py`:

```python
# Line ~230 (in init_sensors or init_rtc)
rtc = None  # Force None, disable RTC search
```

### Tip 7: Change Sensor Poll Interval for Faster Updates

Edit `sensors_dashboard.py`:

```python
# Line ~54
SENSOR_POLL_MS = 500  # 500 ms instead of 1000 ms
```

**Trade-off:** Faster updates but higher I2C/GPIO latency.

### Tip 8: Run Both Logger & Dashboard from Single Process

```python
# Custom wrapper script
import os
import subprocess
import time

os.environ['DISPLAY'] = ':0'

# Start logger in background
logger_proc = subprocess.Popen(
    ['python3', 'sensors_logger.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Start dashboard (blocks until exit)
dashboard_proc = subprocess.Popen(['python3', 'sensors_dashboard.py'])

try:
    dashboard_proc.wait()
finally:
    logger_proc.terminate()
    print("Cleanup complete")
```

---

## Keyboard Shortcuts Reference

| Key/Action | Function | Context |
|---|---|---|
| **ESC** | Exit fullscreen | Dashboard active |
| **Q** | Exit fullscreen | Dashboard active |
| **Ctrl+C** | Interrupt (stop) | Any terminal process |
| **Ctrl+D** | EOF / exit shell | Terminal |
| **Alt+Tab** | Switch windows | Desktop |

---

## Exit & Cleanup

### Stop All Sensor Processes

```bash
pkill -f sensors_dashboard
pkill -f sensors_logger
```

### Check Running Processes

```bash
ps aux | grep -E "sensors_dashboard|sensors_logger" | grep -v grep
```

### View Systemd Service Status

```bash
systemctl --user status sensors-dashboard.service

# View recent logs
journalctl --user -u sensors-dashboard.service -n 20
```

### Disable Autostart Temporarily

```bash
# Rename desktop file (doesn't delete it)
mv ~/.config/autostart/sensors-dashboard.desktop \
   ~/.config/autostart/sensors-dashboard.desktop.disabled

# Re-enable later:
mv ~/.config/autostart/sensors-dashboard.desktop.disabled \
   ~/.config/autostart/sensors-dashboard.desktop
```

---

For more details, see:
- [COMMANDS.md](COMMANDS.md) — Command-line reference
- [ARCHITECTURE.md](ARCHITECTURE.md) — System design details
- [README.md](README.md) — Project overview

