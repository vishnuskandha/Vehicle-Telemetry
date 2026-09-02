"""Smoke tests that run on any host without Raspberry Pi hardware.

The hardware modules (board, busio, lgpio, RPi.GPIO, adafruit_ds3231) are
stubbed before importing the modules under test so the pure logic can be
verified in CI and on development machines.
"""

import sys
import types

import pytest


@pytest.fixture(scope="module", autouse=True)
def _stub_hardware_modules():
    board = types.ModuleType("board")
    board.SCL = object()
    board.SDA = object()
    busio = types.ModuleType("busio")
    sys.modules.setdefault("board", board)
    sys.modules.setdefault("busio", busio)
    sys.modules.setdefault("lgpio", None)
    sys.modules.setdefault("RPi", types.ModuleType("RPi"))
    sys.modules.setdefault("RPi.GPIO", None)
    sys.modules.setdefault("adafruit_ds3231", None)


def test_to_int16_positive():
    from sensors_reader import to_int16

    assert to_int16(0x00, 0xFF) == 0xFF
    assert to_int16(0x01, 0x00) == 0x100


def test_to_int16_negative():
    from sensors_reader import to_int16

    assert to_int16(0xFF, 0xFF) == -1
    assert to_int16(0x80, 0x00) == -32768


def test_speed_counter_reads_rpm_with_fake_pulses():
    from sensors_reader import SpeedCounter

    counter = SpeedCounter(gpio_pin=27)
    counter.pulse_count = 40
    rpm, pulses, elapsed = counter.read_rpm()
    assert pulses == 40
    assert elapsed >= 0
    assert rpm == pytest.approx(60.0 / elapsed)


def test_lerp_color_endpoints():
    from sensors_dashboard import lerp_color

    assert lerp_color((0, 0, 0), (255, 255, 255), 0.0) == (0, 0, 0)
    assert lerp_color((0, 0, 0), (255, 255, 255), 1.0) == (255, 255, 255)
    assert lerp_color((0, 0, 0), (255, 255, 255), -1.0) == (0, 0, 0)


def test_gradient_color_at_bounds():
    from sensors_dashboard import gradient_color_at

    assert gradient_color_at(0.0) == (255, 200, 60)
    assert gradient_color_at(1.0) == (230, 60, 60)


def test_circular_gauge_clamps_value():
    from sensors_dashboard import CircularGauge

    gauge = CircularGauge(100, 100, 50, value_min=0, value_max=3000)
    gauge.update(99999)
    assert gauge.target_value == 3000
    gauge.update(-5)
    assert gauge.target_value == 0


def test_progress_ring_clamps_value():
    from sensors_dashboard import ProgressRing

    ring = ProgressRing(100, 100, 50, value_min=0, value_max=360)
    ring.update(720)
    assert ring.target_value == 720
    ring.update(-10)
    assert ring.target_value == -10


def test_write_sample_formats_telemetry_row():
    from sensors_logger import write_sample

    rows = []
    data = {
        "timestamp": "2026-09-02 14:00:00",
        "rpm": 123.456,
        "horiz_accel": 9.8765,
        "yaw_deg": 12.3456,
    }

    class Writer:
        def writerow(self, row):
            rows.append(row)

    write_sample(Writer(), data)
    assert rows == [["2026-09-02 14:00:00", "123.46", "9.877", "12.35"]]


def test_i2c_scan_functions_exist():
    import i2c_scan

    assert callable(i2c_scan.scan_i2c)
    assert callable(i2c_scan.read_reg)
