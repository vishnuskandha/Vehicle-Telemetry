#!/usr/bin/env python3
"""Scan I2C bus and probe common registers for MPU6050 and DS3231."""

import sys
import board
import busio

I2C_FREQ = 100_000

# MPU6050
MPU_WHOAMI_REG = 0x75
MPU_WHOAMI_EXPECTED = 0x68

# DS3231
DS3231_STATUS_REG = 0x0F
DS3231_CONTROL_REG = 0x0E


def scan_i2c(i2c):
    addrs = []
    for addr in range(0x03, 0x78):
        try:
            buf = bytearray(1)
            i2c.writeto_then_readfrom(addr, bytes([0x00]), buf)
            addrs.append(addr)
        except OSError:
            continue
        except Exception:
            continue
    return addrs


def read_reg(i2c, addr, reg):
    buf = bytearray(1)
    i2c.writeto_then_readfrom(addr, bytes([reg]), buf)
    return buf[0]


def main():
    i2c = busio.I2C(board.SCL, board.SDA, frequency=I2C_FREQ)
    print("Scanning I2C bus...")

    addrs = scan_i2c(i2c)
    if not addrs:
        print("No I2C devices found.")
        return

    print("Found I2C addresses:")
    print(" ".join(f"0x{a:02X}" for a in addrs))

    print("\nProbing MPU6050 (WHO_AM_I = 0x75)...")
    for addr in addrs:
        try:
            who = read_reg(i2c, addr, MPU_WHOAMI_REG)
            if who == MPU_WHOAMI_EXPECTED:
                print(f"  MPU6050 detected at 0x{addr:02X} (WHO_AM_I=0x{who:02X})")
        except Exception:
            continue

    print("\nProbing DS3231 (STATUS/CONTROL regs)...")
    for addr in addrs:
        try:
            status = read_reg(i2c, addr, DS3231_STATUS_REG)
            control = read_reg(i2c, addr, DS3231_CONTROL_REG)
            # DS3231 registers are readable; status bit 7 is OSF
            if 0x00 <= status <= 0xFF and 0x00 <= control <= 0xFF:
                print(f"  Possible DS3231 at 0x{addr:02X} (STATUS=0x{status:02X}, CTRL=0x{control:02X})")
        except Exception:
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
