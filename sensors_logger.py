#!/usr/bin/env python3
"""Log MPU6050 + FC-33 speed + RTC time to CSV on Raspberry Pi 5."""

import csv
import time

from sensors_reader import SensorReader

# --- Configuration ---
CSV_PATH = "/home/pi/Desktop/sensors/sensors_log.csv"
CSV_HEADER = "timestamp,speed(rpm),horizontal acceleration,gyro heading"
SAMPLE_INTERVAL_S = 1.0

PRINT_LIVE = True  # Print live RPM/pulse info
def main():
    reader = SensorReader(print_live=PRINT_LIVE)
    reader.setup()
    if reader.rtc_disabled_reason:
        print(reader.rtc_disabled_reason)

    # Prepare CSV
    with open(CSV_PATH, "a+", newline="") as f:
        f.seek(0)
        first_line = f.readline().strip()
        if first_line != CSV_HEADER:
            f.seek(0)
            f.truncate()
            f.write(CSV_HEADER + "\n")
            f.flush()
        writer = csv.writer(f)

        print(f"Logging to {CSV_PATH}")
        print("Press Ctrl+C to stop")

        try:
            while True:
                data = reader.read()
                writer.writerow(
                    [
                        data["timestamp"],
                        f"{data['rpm']:.2f}",
                        f"{data['horiz_accel']:.3f}",
                        f"{data['yaw_deg']:.2f}",
                    ]
                )
                f.flush()

                time.sleep(SAMPLE_INTERVAL_S)

        except KeyboardInterrupt:
            print("\nStopped.")
        finally:
            reader.close()


if __name__ == "__main__":
    main()
