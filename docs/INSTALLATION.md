# Installation & Setup Guide

Complete step-by-step instructions for getting the Sensor Dashboard running on Raspberry Pi 5.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hardware Setup](#hardware-setup)
3. [OS & System Configuration](#os--system-configuration)
4. [Software Installation](#software-installation)
5. [First Boot & Verification](#first-boot--verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware

- **Raspberry Pi 5** (4B+ may work but untested)
- **MicroSD card** ≥32 GB, Class 10
- **7-inch HDMI monitor** (1280×720 native resolution)
- **MPU6050** I2C 6-axis IMU breakout board
- **FC-33** speed sensor or compatible encoder
- **DS3231 RTC breakout board** (optional)
- **Jumper wires** & breadboard
- **Micro USB power supply** (≥2.5A for Pi 5)

### Software

- **Raspberry Pi OS** (Bookworm, with Wayland/X11 desktop) — minimum Feb 2025
- **Python 3.9+** (pre-installed in Bookworm)
- **Internet connection** for package download

---

## Hardware Setup

### Step 1: Enable I2C & GPIO

On the Raspberry Pi:

```bash
sudo raspi-config
```

Navigate to:
```
Interface Options
  ├─ I2C
  │  └─ Would you like the ARM I2C interface to be enabled? → YES
  └─ GPIO
     └─ Would you like the GPIO server to be enabled? → YES
```

Exit and reboot:
```bash
sudo reboot
```

Verify:
```bash
i2cdetect -y 1     # Should show connected I2C devices
gpio readall       # Should list GPIO pins
```

---

### Step 2: Wire MPU6050 (I2C IMU)

**Raspberry Pi Pin Layout (focus on I2C):**
```
┌─────┬─────┐
│ 1   │ 2   │  (3.3V, 5V)
├─────┼─────┤
│ 3   │ 4   │  (GPIO2=SDA, 5V)
│ SDA │ 5V  │
├─────┼─────┤
│ 5   │ 6   │  (GPIO3=SCL, GND)
│ SCL │GND  │
├─────┼─────┤
│ ...         │
└─────┴─────┘
```

**MPU6050 → Pi 5 Wiring:**

| MPU6050 | Pi 5 | Comments |
|---------|------|----------|
| VCC | Pin 1 (3.3V) | Red wire |
| GND | Pin 6 (GND) | Black wire |
| SDA | Pin 3 (GPIO2) | White wire, I2C data |
| SCL | Pin 5 (GPIO3) | Yellow wire, I2C clock |
| AD0 | GND or 3.3V | GND = 0x68, 3.3V = 0x69 |
| INT | (optional) | Not used in this project |

**Optional I2C pull-ups:**
- If SDA/SCL are not pulled up on your breakout, add **10 kΩ resistors** from each to 3.3V

---

### Step 3: Wire FC-33 Speed Sensor

**FC-33 Pinout (typical):**
```
[OUT pin] → GPIO27 (pin 13)
[+ pin]   → 5V (pin 4 or 2)
[- /GND]  → GND (pin 6, 9, 14, ...)
```

**Optional GPIO27 pull-up:**
```
GPIO27 → 10kΩ → 3.3V
```

**Test the connection:**
```bash
gpio mode 27 in
gpio read 27    # Should show 0 or 1; toggle it with a magnet/pulse
```

---

### Step 4: Wire DS3231 RTC (Optional)

Only needed if you want accurate timestamps without internet.

**DS3231 → Pi 5 Wiring:**

| DS3231 | Pi 5 | Notes |
|--------|------|-------|
| VCC | Pin 1 (3.3V) | Red wire |
| GND | Pin 6 (GND) | Black wire |
| SDA | Pin 3 (GPIO2) | Same bus as MPU6050 |
| SCL | Pin 5 (GPIO3) | Same bus as MPU6050 |
| 32K | (ignore) | Not used here |
| SQW | (ignore) | Not used here |

**Address conflict:** If both RTC and MPU6050 use 0x68, move MPU6050 AD0 to 3.3V.

---

## OS & System Configuration

### Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Install Python & Essential Packages

```bash
sudo apt-get install -y \
  python3-dev \
  python3-pip \
  libopenjp2-7 \
  libtiff5 \
  libjasper1 \
  libharfbuzz0b \
  libwebp6 \
  libtk8.6 \
  libtkimg4 \
  python3-pil \
  python3-numpy \
  git \
  build-essential
```

---

## Software Installation

### Step 1: Clone or Download Project

```bash
# Option A: Clone from GitHub
cd ~
git clone https://github.com/vishnuskandha/Vehicle-Telemetry.git
cd Vehicle-Telemetry

# Option B: Manual setup in existing directory
cd ~/Desktop && mkdir -p sensors
# Copy sensors_*.py and start-dashboard.sh to this folder
```

### Step 2: Install Python Dependencies

```bash
pip3 install --upgrade pip
pip3 install \
  pygame \
  adafruit-blinka \
  adafruit-circuitpython-ds3231 \
  RPi.GPIO \
  python-libgpio
```

**Note:** If `python-libgpio` fails, `RPi.GPIO` will be the fallback.

---

### Step 3: Verify I2C & GPIO Permissions

```bash
# Check I2C device access
ls -l /dev/i2c-1      # Should be readable by user 'pi'

# Add pi user to i2c group
sudo usermod -aG i2c pi

# Add pi user to gpio group (if using RPi.GPIO)
sudo usermod -aG gpio pi

# Apply group changes (logout & login, or reboot)
exit
# SSH back in
```

---

### Step 4: Test Sensor Detection

```bash
cd ~/Desktop/sensors

# Scan I2C bus
python3 i2c_scan.py
# Expected output:
#   Scanning I2C bus 1...
#   Found device at 0x68 (or 0x69)

# Test speed sensor (GPIO27)
python3 << 'EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN)
for i in range(10):
    import time
    print(f"GPIO27: {GPIO.input(27)}")
    time.sleep(0.2)
GPIO.cleanup()
EOF
```

---

### Step 5: Configure Autostart

#### Option A: XDG Desktop Autostart (Recommended)

```bash
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/sensors-dashboard.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Sensor Dashboard
Exec=/home/pi/Desktop/sensors/start-dashboard.sh
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=2
NoDisplay=false
EOF

chmod +x ~/.config/autostart/sensors-dashboard.desktop
```

#### Option B: Systemd User Service (Fallback)

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/sensors-dashboard.service << 'EOF'
[Unit]
Description=Sensor Dashboard
After=graphical.target
Wants=graphical.target

[Service]
Type=simple
User=pi
Environment="HOME=/home/pi"
ExecStart=/home/pi/Desktop/sensors/start-dashboard.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable sensors-dashboard.service
```

---

## First Boot & Verification

### Step 1: Manual Test

```bash
# Test dashboard launch manually
cd ~/Desktop/sensors
DISPLAY=:0 python3 sensors_dashboard.py
```

**Expected behavior:**
- Pygame window appears on HDMI0 (may take 2–3 seconds)
- Detects MPU6050 (prints "Detected MPU-6500/9250...")
- Shows gauges with live data (if vehicle is moving/tilted)
- Press ESC to exit

### Step 2: Test Logger (Optional)

In a separate terminal:
```bash
cd ~/Desktop/sensors
python3 sensors_logger.py
```

**Expected output:**
```
Logging to /home/pi/Desktop/sensors/sensors_log.csv
Press Ctrl+C to stop
2026-02-07 13:50:01 | rpm=  0.00 | pulses=  0 | window= 1.00s
2026-02-07 13:50:02 | rpm=120.50 | pulses= 40 | window= 1.04s
```

Stop with Ctrl+C. Check CSV:
```bash
tail -5 sensors_log.csv
```

### Step 3: Reboot & Test Autostart

```bash
sudo reboot
```

After reboot:
- Watch HDMI monitor for dashboard to appear (within 5 seconds)
- Check processes:
  ```bash
  ps aux | grep sensors_dashboard
  ```

---

## Troubleshooting

### Issue: I2C Devices Not Detected

**Symptom:**
```
i2c_scan.py reports "No I2C devices found"
```

**Debug:**
```bash
# Check I2C kernel module
lsmod | grep i2c

# Check device file
ls -l /dev/i2c-*

# Manually probe I2C bus
i2cdetect -y 1
```

**Solutions:**
- Verify wiring (SDA/SCL to correct pins)
- Check pull-up resistors (10 kΩ to 3.3V)
- Reboot: `sudo reboot`
- Check power on breakout board (3.3V LED should glow)

---

### Issue: "Module not found: pygame"

**Fix:**
```bash
pip3 install pygame

# If that fails, install dependencies first
sudo apt-get install -y libsdl2-dev libsdl2-image-dev \
  libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev

pip3 install --upgrade pygame
```

---

### Issue: "$DISPLAY not set" or Dashboard Won't Start

**Check display status:**
```bash
echo $DISPLAY                           # Should show :0
ps aux | grep -E "labwc|Xvfb|Xorg"    # Check if DE is running
```

**Fix: Manual start with explicit display**
```bash
DISPLAY=:0 python3 /home/pi/Desktop/sensors/sensors_dashboard.py
```

**Fix: Update wrapper script**
```bash
# Edit start-dashboard.sh
nano ~/Desktop/sensors/start-dashboard.sh

# Ensure this line exists:
# export DISPLAY=:0
# export XAUTHORITY=/home/pi/.Xauthority
```

---

### Issue: "Sensor init error" or Blank Gauges

**For MPU6050:**
- Verify `i2c_scan.py` shows device at 0x68 or 0x69
- Check I2C address (AD0 wired correctly)
- Re-seat breakout board connections

**For speed sensor:**
- Check GPIO27 is accessible: `gpio read 27` should return 0 or 1
- Verify pull-up wiring (10 kΩ to 3.3V)
- Simulate pulse: Hold magnet near sensor, watch GPIO toggle

---

### Issue: Autostart Not Working

**Check desktop entry:**
```bash
cat ~/.config/autostart/sensors-dashboard.desktop
# Should have: Type=Application, Exec=...start-dashboard.sh
```

**Check script is executable:**
```bash
ls -la ~/Desktop/sensors/start-dashboard.sh
# Should show:  -rwxr-xr-x
chmod +x ~/Desktop/sensors/start-dashboard.sh  # If not
```

**Manual test:**
```bash
/home/pi/Desktop/sensors/start-dashboard.sh
# Should launch dashboard within 5 seconds
```

**Check systemd logs (if using systemd service):**
```bash
journalctl --user -u sensors-dashboard.service -n 20
```

---

### Issue: High CPU Usage or Laggy Display

**Reduce refresh rate:**
```bash
# Edit sensors_dashboard.py, line ~56
nano ./sensors_dashboard.py
# Change: FPS = 30 → FPS = 20
```

**Lower sensor polling frequency:**
```bash
# Edit sensors_reader.py, line ~32
# Change: SENSOR_POLL_MS = 1000 → 2000  (2 second updates)
```

---

### Issue: "No GPIO backend available"

**Install GPIO library:**
```bash
pip3 install RPi.GPIO
# or
pip3 install python-libgpio
```

---

## Post-Installation Checklist

- [ ] I2C detected: `i2cdetect -y 1` shows 0x68
- [ ] GPIO27 usable: `gpio read 27` returns 0 or 1
- [ ] Sensor reader test: manual run prints values
- [ ] Dashboard launches: `DISPLAY=:0 python3 sensors_dashboard.py`
- [ ] Logger works: CSV appends rows every second
- [ ] Autostart enabled: `~/.config/autostart/sensors-dashboard.desktop` exists
- [ ] Reboot test: `sudo reboot` → dashboard auto-starts
- [ ] No error messages in status bar after 10 seconds

---

## Next Steps

1. **First run:** Let the system capture data for 1–2 minutes
2. **Analyze logs:** Open `sensors_log.csv` in Excel or Python
3. **Customize:** Adjust gauge ranges, colors, polling intervals (see README.md)
4. **Deploy:** Use `systemctl` or add to cron for background logging

See [USAGE.md](USAGE.md) for operating instructions and [COMMANDS.md](COMMANDS.md) for CLI reference.

