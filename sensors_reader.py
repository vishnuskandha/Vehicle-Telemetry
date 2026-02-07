#!/usr/bin/env python3
"""Shared sensor reader for MPU6050 + FC-33 speed + RTC on Raspberry Pi."""

import math
import time
from datetime import datetime

import board
import busio

try:
    import adafruit_ds3231
    DS3231_AVAILABLE = True
except Exception:
    DS3231_AVAILABLE = False

try:
    import lgpio
except Exception:
    lgpio = None

try:
    import RPi.GPIO as GPIO
except Exception:
    GPIO = None

# --- Configuration ---
SPEED_GPIO = 27  # GPIO27 (pin 13)
PULL_UP = True  # Enable internal pull-up
PULSES_PER_REV = 40  # Measured: 40 edges per rotation
COUNT_BOTH_EDGES = True  # Count rising + falling edges

# MPU6050 address: 0x68 default, 0x69 if AD0 is pulled high
MPU_ADDRS = [0x68, 0x69]
MPU_WHOAMI_REG = 0x75
MPU_WHOAMI_EXPECTED = {0x68, 0x70}  # 0x68=MPU6050, 0x70=MPU6500/9250
MPU_REG_PWR_MGMT_1 = 0x6B
MPU_REG_ACCEL_XOUT_H = 0x3B
MPU_REG_GYRO_XOUT_H = 0x43

ACCEL_LSB_PER_G = 16384.0  # +/-2g
GYRO_LSB_PER_DPS = 131.0   # +/-250 dps
STANDARD_GRAVITY = 9.80665

# DS3231 address (the RTC is always 0x68; 0x57 is module EEPROM)
DS3231_ADDR = 0x68


class SpeedCounter:
    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin
        self.pulse_count = 0
        self.last_calc_time = time.time()
        self._chip = None
        self._callback = None
        self._backend = None

    def _pulse_callback(self, *_args):
        self.pulse_count += 1

    def setup(self):
        if lgpio is not None:
            self._chip = lgpio.gpiochip_open(0)
            pull = lgpio.SET_PULL_UP if PULL_UP else lgpio.SET_PULL_NONE
            edge = lgpio.BOTH_EDGES if COUNT_BOTH_EDGES else lgpio.FALLING_EDGE
            lgpio.gpio_claim_alert(self._chip, self.gpio_pin, edge, pull)
            self._callback = lgpio.callback(
                self._chip,
                self.gpio_pin,
                edge,
                self._pulse_callback,
            )
            self._backend = "lgpio"
            return

        if GPIO is None:
            raise SystemExit("No GPIO backend available. Install python3-lgpio or RPi.GPIO.")

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        pull = GPIO.PUD_UP if PULL_UP else GPIO.PUD_OFF
        GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=pull)
        edge = GPIO.BOTH if COUNT_BOTH_EDGES else GPIO.FALLING
        GPIO.add_event_detect(
            self.gpio_pin,
            edge,
            callback=self._pulse_callback,
            bouncetime=5,
        )
        self._backend = "rpi-gpio"

    def read_rpm(self):
        now = time.time()
        elapsed = now - self.last_calc_time
        if elapsed <= 0:
            return 0.0, 0, elapsed
        pulses = self.pulse_count
        self.pulse_count = 0
        self.last_calc_time = now
        revs = pulses / float(PULSES_PER_REV)
        rpm = (revs / elapsed) * 60.0
        return rpm, pulses, elapsed

    def cleanup(self):
        if self._callback is not None:
            self._callback.cancel()
            self._callback = None
        if self._chip is not None:
            lgpio.gpiochip_close(self._chip)
            self._chip = None
        if self._backend == "rpi-gpio" and GPIO is not None:
            GPIO.cleanup()


def read_i2c_reg(i2c, addr, reg):
    buf = bytearray(1)
    i2c.writeto_then_readfrom(addr, bytes([reg]), buf)
    return buf[0]


def read_i2c_block(i2c, addr, reg, length):
    buf = bytearray(length)
    i2c.writeto_then_readfrom(addr, bytes([reg]), buf)
    return buf


def to_int16(msb, lsb):
    value = (msb << 8) | lsb
    if value & 0x8000:
        value -= 0x10000
    return value


class RawMPU:
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        # Wake device
        self.i2c.writeto(self.addr, bytes([MPU_REG_PWR_MGMT_1, 0x00]))

    def read_accel(self):
        data = read_i2c_block(self.i2c, self.addr, MPU_REG_ACCEL_XOUT_H, 6)
        ax = to_int16(data[0], data[1])
        ay = to_int16(data[2], data[3])
        az = to_int16(data[4], data[5])
        return (
            (ax / ACCEL_LSB_PER_G) * STANDARD_GRAVITY,
            (ay / ACCEL_LSB_PER_G) * STANDARD_GRAVITY,
            (az / ACCEL_LSB_PER_G) * STANDARD_GRAVITY,
        )

    def read_gyro(self):
        data = read_i2c_block(self.i2c, self.addr, MPU_REG_GYRO_XOUT_H, 6)
        gx = to_int16(data[0], data[1])
        gy = to_int16(data[2], data[3])
        gz = to_int16(data[4], data[5])
        # Convert to rad/s
        return (
            math.radians(gx / GYRO_LSB_PER_DPS),
            math.radians(gy / GYRO_LSB_PER_DPS),
            math.radians(gz / GYRO_LSB_PER_DPS),
        )


def init_mpu(i2c):
    last_error = None
    for addr in MPU_ADDRS:
        try:
            who = read_i2c_reg(i2c, addr, MPU_WHOAMI_REG)
            if who in MPU_WHOAMI_EXPECTED:
                if who == 0x70:
                    print("Detected MPU-6500/9250 (WHO_AM_I=0x70). Using raw register reads.")
                return RawMPU(i2c, addr), addr
        except Exception as exc:
            last_error = exc
    raise SystemExit(
        "MPU6050 not found at 0x68 or 0x69. Check wiring and AD0. "
        f"Last error: {last_error}"
    )


def init_rtc(i2c):
    if not DS3231_AVAILABLE:
        return None
    try:
        return adafruit_ds3231.DS3231(i2c, address=DS3231_ADDR)
    except Exception:
        return None


def get_timestamp(rtc):
    if rtc:
        try:
            t = rtc.datetime
            return (
                f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d} "
                f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}"
            )
        except Exception:
            pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SensorReader:
    def __init__(self, speed_gpio=SPEED_GPIO, print_live=False):
        self.speed_gpio = speed_gpio
        self.print_live = print_live
        self.i2c = None
        self.mpu = None
        self.mpu_addr = None
        self.rtc = None
        self.speed = None
        self.yaw_deg = 0.0
        self.last_time = None
        self.rtc_disabled_reason = None

    def setup(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.mpu, self.mpu_addr = init_mpu(self.i2c)
        if self.mpu_addr != DS3231_ADDR:
            self.rtc = init_rtc(self.i2c)
        else:
            self.rtc_disabled_reason = (
                "DS3231 not enabled (MPU6050 is using 0x68). "
                "Use AD0=3.3V to move MPU6050 to 0x69."
            )
        self.speed = SpeedCounter(self.speed_gpio)
        self.speed.setup()
        self.yaw_deg = 0.0
        self.last_time = time.time()

    def read(self):
        if self.speed is None or self.mpu is None:
            raise RuntimeError("SensorReader.setup() must be called first.")

        now = time.time()
        dt = now - self.last_time if self.last_time else 0.0
        self.last_time = now

        rpm, pulses, elapsed = self.speed.read_rpm()
        ax, ay, _az = self.mpu.read_accel()
        horiz_accel = math.sqrt(ax * ax + ay * ay)

        _gx, _gy, gz = self.mpu.read_gyro()
        self.yaw_deg += math.degrees(gz) * dt

        timestamp = get_timestamp(self.rtc)
        rtc_active = self.rtc is not None and self.mpu_addr != DS3231_ADDR

        if self.print_live:
            print(
                f"{timestamp} | rpm={rpm:7.2f} | pulses={pulses:4d} | window={elapsed:4.2f}s"
            )

        return {
            "timestamp": timestamp,
            "rpm": rpm,
            "pulses": pulses,
            "elapsed": elapsed,
            "horiz_accel": horiz_accel,
            "yaw_deg": self.yaw_deg,
            "rtc_active": rtc_active,
        }

    def close(self):
        if self.speed is not None:
            self.speed.cleanup()
            self.speed = None
