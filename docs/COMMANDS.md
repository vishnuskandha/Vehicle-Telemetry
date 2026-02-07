# Commands Reference

Complete command-line reference for operating and maintaining the Sensor Dashboard & Logger system.

---

## Table of Contents

1. [Start/Stop Commands](#startstop-commands)
2. [Systemd Service Commands](#systemd-service-commands)
3. [Diagnostic & Hardware Commands](#diagnostic--hardware-commands)
4. [File Management](#file-management)
5. [Python One-Liners](#python-one-liners)
6. [Troubleshooting Commands](#troubleshooting-commands)
7. [Cron & Automation](#cron--automation)

---

## Start/Stop Commands

### Dashboard

| Command | Purpose |
|---------|---------|
| `DISPLAY=:0 python3 sensors_dashboard.py` | Start dashboard (foreground; blocking) |
| `DISPLAY=:0 nohup python3 sensors_dashboard.py &` | Start dashboard (background; non-blocking) |
| `/home/pi/Desktop/sensors/start-dashboard.sh` | Start via wrapper (waits for display) |
| `pkill -f sensors_dashboard` | Stop all running dashboard processes |
| `kill 12345` | Kill dashboard by PID (replace 12345) |
| `pgrep -f sensors_dashboard` | Find dashboard PID |

### Logger

| Command | Purpose |
|---------|---------|
| `python3 sensors_logger.py` | Start logger (foreground; shows output) |
| `nohup python3 sensors_logger.py > /tmp/logger.log 2>&1 &` | Start logger (background; log to file) |
| `python3 sensors_logger.py &` | Start logger (background; output mixed with shell) |
| `pkill -f sensors_logger` | Stop all running logger processes |
| `kill 12345` | Kill logger by PID |
| `pgrep -f sensors_logger` | Find logger PID |

### Both (Dashboard + Logger)

| Command | Purpose |
|---------|---------|
| `screen -S sensors` | Create a named tmux/screen session |
| `cd ~/Desktop/sensors && python3 sensors_logger.py &` | Start logger in background |
| `DISPLAY=:0 python3 sensors_dashboard.py` | Start dashboard (takes foreground) |
| `pkill -a sensors_` | Kill all sensor processes at once |

---

## Systemd Service Commands

### Service Control

| Command | Purpose |
|---------|---------|
| `systemctl --user start sensors-dashboard.service` | Start service now |
| `systemctl --user stop sensors-dashboard.service` | Stop service now |
| `systemctl --user restart sensors-dashboard.service` | Restart service |
| `systemctl --user status sensors-dashboard.service` | Check current status |
| `systemctl --user enable sensors-dashboard.service` | Enable autostart on login |
| `systemctl --user disable sensors-dashboard.service` | Disable autostart |
| `systemctl --user daemon-reload` | Reload systemd config (after editing .service file) |

### Service Logs

| Command | Purpose |
|---------|---------|
| `journalctl --user -u sensors-dashboard.service` | View entire service log |
| `journalctl --user -u sensors-dashboard.service -n 50` | View last 50 lines |
| `journalctl --user -u sensors-dashboard.service -f` | Follow log in real-time |
| `journalctl --user -u sensors-dashboard.service --since "1 hour ago"` | View logs from last hour |
| `journalctl --user -u sensors-dashboard.service --until "2 hours ago" -n 5` | View logs from 2–3 hours ago |

### Service Info

| Command | Purpose |
|---------|---------|
| `systemctl --user list-units --type=service` | List all user services |
| `systemctl --user cat sensors-dashboard.service` | View service file content |
| `systemctl --user show sensors-dashboard.service` | Show service properties (env, paths, etc.) |
| `systemctl --user show -p Environment sensors-dashboard.service` | View service environment variables |

---

## Diagnostic & Hardware Commands

### I2C Bus Diagnostics

| Command | Purpose |
|---------|---------|
| `i2cdetect -y 1` | List all I2C devices on bus 1 |
| `i2cdump -y 1 0x68` | Dump all registers of MPU6050 at 0x68 |
| `i2cget -y 1 0x68 0x75` | Read WHO_AM_I register (should be 0x68 or 0x70) |
| `i2cset -y 1 0x68 0x6b 0x00` | Wake up MPU6050 (reset SLEEP bit) |

### GPIO Diagnostics

| Command | Purpose |
|---------|---------|
| `gpioinfo` | List all GPIO pins and their state (lgpio) |
| `gpioget gpiochip0 27` | Read GPIO pin 27 value (0 or 1) |
| `gpioinfo gpiochip0 27` | Show GPIO pin 27 details |

### System Info

| Command | Purpose |
|---------|---------|
| `uname -a` | Show system kernel & version |
| `lsb_release -a` | Show OS release info |
| `vcgencmd measure_temp` | Show CPU temperature |
| `vcgencmd measure_clock arm` | Show ARM clock speed |
| `free -h` | Show RAM usage |
| `df -h` | Show disk space |

### Display Diagnostics

| Command | Purpose |
|---------|---------|
| `DISPLAY=:0 xrandr` | List connected displays |
| `DISPLAY=:0 xrandr --current` | Show active display & resolution |
| `ps aux \| grep -E "Xvfb\|labwc\|Xwayland"` | Check display server (X11 vs Wayland) |
| `cat /proc/device-tree/model` | Identify Pi model |

### Process Monitoring

| Command | Purpose |
|---------|---------|
| `ps aux \| grep sensors` | List all sensor processes |
| `ps aux \| grep sensors_dashboard` | List dashboard processes only |
| `top -p $(pgrep -d, -f sensors_dashboard)` | Monitor dashboard resource usage |
| `watch -n 1 'ps aux \| grep sensors_dashboard'` | Continuously monitor dashboard |

---

## File Management

### CSV Data

| Command | Purpose |
|---------|---------|
| `tail sensors_log.csv` | View last 10 lines of CSV |
| `wc -l sensors_log.csv` | Count rows in CSV |
| `head -1 sensors_log.csv` | View CSV header |
| `tail -100 sensors_log.csv > trip_excerpt.csv` | Extract last 100 rows |
| `grep "14:3[0-9]" sensors_log.csv > trip_2pm.csv` | Extract rows from specific time range |
| `rm sensors_log.csv` | Delete CSV (start fresh logging) |
| `cp sensors_log.csv sensors_log.csv.backup` | Backup CSV |

### Project Files

| Command | Purpose |
|---------|---------|
| `ls -la ~/Desktop/sensors/` | List all project files with details |
| `cd ~/Desktop/sensors && ls -1` | List filenames only |
| `find ~/Desktop/sensors -name "*.md"` | Find all documentation files |
| `find ~/Desktop/sensors -name "*.py" -exec head -1 {} \;` | Show first line of all Python files |

### Logs

| Command | Purpose |
|---------|---------|
| `journalctl --user -u sensors-dashboard.service -o short -n 100 > ~/sensors_debug.log` | Export service logs to file |
| `tail /tmp/logger.log` | View background logger log file |
| `dmesg \| tail -20` | View system kernel messages (GPIO/I2C errors) |

---

## Python One-Liners

### Quick Sensor Test

```bash
# Test I2C connection to MPU6050
python3 << 'EOF'
import board, busio, adafruit_mpu6050
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_mpu6050.MPU6050(i2c)
print(f"Accel: {sensor.acceleration}")
print(f"Gyro: {sensor.gyro}")
EOF
```

### Check RTC (DS3231)

```bash
python3 << 'EOF'
import board, busio, adafruit_ds3231
i2c = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_ds3231.DS3231(i2c)
print(f"RTC time: {rtc.datetime}")
print(f"Temperature: {rtc.temperature}°C")
EOF
```

### Test GPIO Speed Sensor

```bash
python3 << 'EOF'
import lgpio
chip = lgpio.gpiochip_open(0)
pin = 27
for i in range(100):
    val = lgpio.gpio_read(chip, pin)
    print(f"GPIO27: {val}")
lgpio.gpiochip_close(chip)
EOF
```

### Quick CSV Analysis

```bash
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('sensors_log.csv')
print(df.describe())
EOF
```

### Check Imports

```bash
python3 -c "import pygame; print(f'Pygame {pygame.ver}')"
python3 -c "import board; print('Blinka OK')"
python3 -c "import adafruit_mpu6050; print('MPU6050 OK')"
```

---

## Troubleshooting Commands

### Dashboard Troubleshooting

| Command | Purpose |
|---------|---------|
| `DISPLAY=:0 xset q` | Check if X11 is responding |
| `DISPLAY=:0 python3 -c "import pygame; pygame.init()"` | Test pygame on display :0 |
| `echo $DISPLAY` | Check current DISPLAY variable |
| `ps aux \| grep -E "Xvfb\|Xwayland\|labwc"` | Identify active display server |
| `systemctl --user status pulseaudio` | Check audio server (can affect display) |

### I2C Troubleshooting

| Command | Purpose |
|---------|---------|
| `i2cdetect -y 1` | Scan for I2C devices (should show 0x68 or 0x69) |
| `sudo raspi-config nonint get_i2c` | Check if I2C is enabled (returns 0 if enabled) |
| `grep -i i2c /boot/config.txt` | View I2C boot config |
| `dmesg \| grep -i i2c` | Check kernel messages for I2C |
| `ls -la /dev/i2c*` | List I2C device files |

### GPIO Troubleshooting

| Command | Purpose |
|---------|---------|
| `gpioinfo gpiochip0 27` | Check GPIO27 status |
| `cat /sys/class/gpio/gpio27/value` | Read GPIO27 directly (requires root) |
| `dmesg \| grep -i gpio` | Check kernel messages for GPIO |
| `grep -i gpio /boot/config.txt` | View GPIO boot config |

### Logger Troubleshooting

| Command | Purpose |
|---------|---------|
| `python3 sensors_logger.py 2>&1 \| head -50` | Run logger & show first 50 error lines |
| `file sensors_log.csv` | Verify CSV file type |
| `head -3 sensors_log.csv && echo "..." && tail -3 sensors_log.csv` | Show CSV start & end |

### Permission Issues

| Command | Purpose |
|---------|---------|
| `ls -l /dev/i2c-1` | Check I2C device permissions |
| `groups pi` | Show user groups (should include i2c, gpio, etc.) |
| `sudo usermod -aG i2c,gpio pi` | Add user to required groups (if needed) |
| `sudo reboot` | Required after group changes |

---

## Cron & Automation

### Run Logger on Boot

```bash
# Option 1: Edit crontab
crontab -e

# Add line:
@reboot cd /home/pi/Desktop/sensors && python3 sensors_logger.py >> /tmp/logger.log 2>&1
```

### Stop All Sensor Services on Shutdown

```bash
# Option 1: Via systemd timer (stops logger before poweroff)
# Create /etc/systemd/system-sleep/sensors-stop

#!/bin/bash
case $1 in
    pre)
        systemctl --user stop sensors-dashboard.service
        pkill -f sensors_logger
        ;;
esac
```

### Rotate CSV Logs Daily

```bash
# Create /usr/local/bin/rotate_sensor_logs.sh
#!/bin/bash
CSV="/home/pi/Desktop/sensors/sensors_log.csv"
BACKUP="/home/pi/Desktop/sensors/sensors_log_$(date +%Y%m%d).csv"
if [ -f "$CSV" ]; then
    cp "$CSV" "$BACKUP"
    > "$CSV"  # Truncate original
    echo "CSV rotated to $BACKUP"
fi

# Add to crontab:
0 0 * * * /usr/local/bin/rotate_sensor_logs.sh
```

### Monitor CSV Size & Archive

```bash
# Create /usr/local/bin/archive_sensors.sh
#!/bin/bash
CSV="/home/pi/Desktop/sensors/sensors_log.csv"
SIZE=$(stat -f%z "$CSV" 2>/dev/null || stat -c%s "$CSV")

if [ $SIZE -gt 10485760 ]; then  # 10 MB threshold
    tar czf "/home/pi/Desktop/sensors/logs_$(date +%s).tar.gz" "$CSV"
    > "$CSV"
    echo "CSV archived"
fi

# Add to crontab (run hourly):
0 * * * * /usr/local/bin/archive_sensors.sh
```

### View Cron Jobs

| Command | Purpose |
|---------|---------|
| `crontab -l` | List user's cron jobs |
| `crontab -e` | Edit user's cron jobs (opens $EDITOR) |
| `sudo crontab -l` | List root's cron jobs |
| `sudo crontab -e` | Edit root's cron jobs |

---

## Quick Reference Cheatsheet

### Most-Used Commands

```bash
# Start dashboard
DISPLAY=:0 python3 sensors_dashboard.py

# Start logger
python3 sensors_logger.py &

# Stop all
pkill -a sensors_

# Check I2C
i2cdetect -y 1

# Monitor resources
top -p $(pgrep -d, -f sensors_dashboard)

# View CSV
tail -20 sensors_log.csv

# Service status
systemctl --user status sensors-dashboard.service

# Service logs
journalctl --user -u sensors-dashboard.service -f

# Quick analysis
python3 -c "import pandas as pd; print(pd.read_csv('sensors_log.csv').describe())"
```

### File Location Quick Links

```
Dashboard:      ~/Desktop/sensors/sensors_dashboard.py
Logger:         ~/Desktop/sensors/sensors_logger.py
Sensor Reader:  ~/Desktop/sensors/sensors_reader.py
CSV Log:        ~/Desktop/sensors/sensors_log.csv

Config Files:
  Autostart:    ~/.config/autostart/sensors-dashboard.desktop
  Systemd:      ~/.config/systemd/user/sensors-dashboard.service
  Boot Script:  ~/Desktop/sensors/start-dashboard.sh

Documentation:
  ARCHITECTURE: ~/Desktop/sensors/ARCHITECTURE.md
  README:       ~/Desktop/sensors/README.md
  INSTALLATION: ~/Desktop/sensors/INSTALLATION.md
  USAGE:        ~/Desktop/sensors/USAGE.md
  COMMANDS:     ~/Desktop/sensors/COMMANDS.md
```

---

For more details, see:
- [USAGE.md](USAGE.md) — Operational guide with workflows
- [ARCHITECTURE.md](ARCHITECTURE.md) — System design & components
- [INSTALLATION.md](INSTALLATION.md) — Hardware setup & wiring

