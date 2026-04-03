#!/usr/bin/env python3
"""
Neumorphic fullscreen sensor dashboard for 7-inch HDMI monitor.
Reads live MPU6050 + FC-33 speed sensor data and displays it
as modern truck/lorry-style gauges with gradient arcs and dark panels.

Run:  DISPLAY=:0 python3 sensors_dashboard.py
Exit: Press ESC or close window.
"""

import math
import os

import pygame
import pygame.gfxdraw
from sensors_reader import SensorReader

# ---------------------------------------------------------------------------
# Color palette  (neumorphic dark theme matching reference image)
# ---------------------------------------------------------------------------
BG_COLOR        = (30, 30, 35)
PANEL_DARK      = (38, 38, 44)
PANEL_LIGHT     = (50, 50, 58)
BEZEL_OUTER     = (22, 22, 26)
BEZEL_INNER     = (42, 42, 48)
GAUGE_FACE      = (28, 28, 33)
GAUGE_FACE_LITE = (35, 35, 40)

WHITE           = (255, 255, 255)
TEXT_PRIMARY    = (240, 240, 245)
TEXT_MUTED      = (140, 145, 155)
TEXT_UNIT       = (180, 180, 190)

# Gradient accent:  orange -> red
ACCENT_ORANGE   = (255, 150, 50)
ACCENT_RED      = (230, 60, 60)
ACCENT_YELLOW   = (255, 200, 60)
ACCENT_BLUE     = (70, 160, 230)

# For the progress ring ticks
TICK_DIM        = (60, 60, 68)
TICK_BRIGHT     = (200, 200, 210)

# ---------------------------------------------------------------------------
# Layout constants  (designed for 1280x720, scales proportionally)
# ---------------------------------------------------------------------------
TARGET_W, TARGET_H = 1280, 720
FPS = 30
SENSOR_POLL_MS = 1000          # read sensors every 1 s
SMOOTHING      = 0.18          # needle / value smoothing factor per frame

os.environ.setdefault("DISPLAY", ":0")


def lerp_color(c1, c2, t):
    """Linear interpolate between two RGB tuples."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def gradient_color_at(frac):
    """Return gradient color from yellow -> orange -> red for 0..1."""
    if frac < 0.5:
        return lerp_color(ACCENT_YELLOW, ACCENT_ORANGE, frac * 2.0)
    return lerp_color(ACCENT_ORANGE, ACCENT_RED, (frac - 0.5) * 2.0)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_aa_circle(surface, cx, cy, radius, color):
    """Draw a filled anti-aliased circle."""
    r = int(radius)
    if r < 1:
        return
    pygame.gfxdraw.aacircle(surface, int(cx), int(cy), r, color)
    pygame.gfxdraw.filled_circle(surface, int(cx), int(cy), r, color)


def draw_thick_arc(surface, cx, cy, radius, thickness, start_deg, end_deg,
                   color_func=None, color=None, segments=120):
    """Draw a thick arc with per-segment color (gradient) support."""
    if abs(start_deg - end_deg) < 0.1:
        return
    for i in range(segments):
        t0 = i / segments
        t1 = (i + 1) / segments
        a0 = math.radians(start_deg + (end_deg - start_deg) * t0)
        a1 = math.radians(start_deg + (end_deg - start_deg) * t1)
        c = color_func(t0) if color_func else color

        inner_r = radius - thickness / 2
        outer_r = radius + thickness / 2
        points = [
            (cx + math.cos(a0) * inner_r, cy - math.sin(a0) * inner_r),
            (cx + math.cos(a0) * outer_r, cy - math.sin(a0) * outer_r),
            (cx + math.cos(a1) * outer_r, cy - math.sin(a1) * outer_r),
            (cx + math.cos(a1) * inner_r, cy - math.sin(a1) * inner_r),
        ]
        pygame.gfxdraw.filled_polygon(
            surface,
            [(int(p[0]), int(p[1])) for p in points],
            c,
        )


def draw_rounded_rect(surface, rect, color, radius=12):
    """Draw a filled rounded rectangle."""
    x, y, w, h = rect
    r = min(radius, w // 2, h // 2)
    if r < 1:
        pygame.draw.rect(surface, color, (x, y, w, h))
        return
    pygame.draw.rect(surface, color, (x + r, y, w - 2 * r, h))
    pygame.draw.rect(surface, color, (x, y + r, w, h - 2 * r))
    draw_aa_circle(surface, x + r, y + r, r, color)
    draw_aa_circle(surface, x + w - r - 1, y + r, r, color)
    draw_aa_circle(surface, x + r, y + h - r - 1, r, color)
    draw_aa_circle(surface, x + w - r - 1, y + h - r - 1, r, color)


def draw_shadow_circle(surface, cx, cy, radius, shadow_offset=6, shadow_alpha=60):
    """Draw a subtle drop shadow behind a circle."""
    size = int(radius * 2 + 40)
    shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    draw_aa_circle(shadow_surf, size // 2, size // 2 + shadow_offset,
                   int(radius), (0, 0, 0, shadow_alpha))
    surface.blit(shadow_surf, (int(cx - size // 2), int(cy - size // 2)))


# ---------------------------------------------------------------------------
# Gauge widgets
# ---------------------------------------------------------------------------

class CircularGauge:
    """Large neumorphic circular gauge (RPM-style or value display)."""

    def __init__(self, cx, cy, outer_r, value_min, value_max,
                 label="", unit="", arc_start=210, arc_span=240,
                 show_needle=True, fmt="{:.0f}"):
        self.cx = cx
        self.cy = cy
        self.outer_r = outer_r
        self.inner_r = int(outer_r * 0.78)
        self.value_min = value_min
        self.value_max = value_max
        self.label = label
        self.unit = unit
        self.arc_start = arc_start
        self.arc_span = arc_span
        self.show_needle = show_needle
        self.fmt = fmt

        self.display_value = 0.0
        self.target_value = 0.0

    def update(self, target):
        self.target_value = max(self.value_min, min(target, self.value_max))
        self.display_value += (self.target_value - self.display_value) * SMOOTHING

    def draw(self, surface, fonts):
        cx, cy = self.cx, self.cy
        outer_r = self.outer_r
        inner_r = self.inner_r

        # Outer shadow
        draw_shadow_circle(surface, cx, cy, outer_r, shadow_offset=8, shadow_alpha=70)

        # Outer bezel (dark rim)
        draw_aa_circle(surface, cx, cy, outer_r, BEZEL_OUTER)

        # Inner bezel highlight
        draw_aa_circle(surface, cx, cy, outer_r - 4, BEZEL_INNER)

        # Gauge face
        draw_aa_circle(surface, cx, cy, inner_r, GAUGE_FACE)

        # Background arc track (dim)
        track_r = (inner_r + outer_r) / 2
        track_w = outer_r - inner_r - 10
        draw_thick_arc(surface, cx, cy, track_r, track_w,
                       self.arc_start, self.arc_start - self.arc_span,
                       color=PANEL_DARK, segments=80)

        # Active gradient arc
        if self.value_max > self.value_min:
            frac = (self.display_value - self.value_min) / (self.value_max - self.value_min)
        else:
            frac = 0.0
        frac = max(0.0, min(1.0, frac))
        active_span = self.arc_span * frac
        if active_span > 0.5:
            draw_thick_arc(
                surface, cx, cy, track_r, track_w,
                self.arc_start, self.arc_start - active_span,
                color_func=gradient_color_at,
                segments=max(20, int(active_span)),
            )

        # Tick marks
        num_ticks = 30
        for i in range(num_ticks + 1):
            t = i / num_ticks
            angle_deg = self.arc_start - self.arc_span * t
            angle_rad = math.radians(angle_deg)
            is_major = i % 5 == 0
            tick_inner = inner_r - (14 if is_major else 8)
            tick_outer = inner_r - 2
            x0 = cx + math.cos(angle_rad) * tick_inner
            y0 = cy - math.sin(angle_rad) * tick_inner
            x1 = cx + math.cos(angle_rad) * tick_outer
            y1 = cy - math.sin(angle_rad) * tick_outer
            c = TICK_BRIGHT if is_major else TICK_DIM
            pygame.draw.aaline(surface, c, (x0, y0), (x1, y1))

        # Needle (if enabled)
        if self.show_needle:
            needle_angle_deg = self.arc_start - self.arc_span * frac
            needle_rad = math.radians(needle_angle_deg)
            needle_len = int(inner_r * 0.72)
            nx = cx + math.cos(needle_rad) * needle_len
            ny = cy - math.sin(needle_rad) * needle_len
            # needle shadow
            pygame.draw.aaline(surface, (0, 0, 0), (cx + 2, cy + 2), (nx + 2, ny + 2))
            # needle body
            c = lerp_color(ACCENT_ORANGE, ACCENT_RED, frac)
            pygame.draw.line(surface, c, (cx, cy), (int(nx), int(ny)), 3)
            # center cap
            draw_aa_circle(surface, cx, cy, 8, c)
            draw_aa_circle(surface, cx, cy, 4, WHITE)

        # Value text
        val_text = self.fmt.format(self.display_value)
        val_surf = fonts["big"].render(val_text, True, TEXT_PRIMARY)
        vr = val_surf.get_rect(center=(cx, cy + 2))
        surface.blit(val_surf, vr)

        # Unit label below
        unit_surf = fonts["unit"].render(self.unit, True, TEXT_UNIT)
        ur = unit_surf.get_rect(center=(cx, cy + int(inner_r * 0.38)))
        surface.blit(unit_surf, ur)

        # Top label
        if self.label:
            lbl_surf = fonts["label"].render(self.label, True, TEXT_MUTED)
            lr = lbl_surf.get_rect(center=(cx, cy - int(inner_r * 0.42)))
            surface.blit(lbl_surf, lr)


class ProgressRing:
    """Circular progress ring gauge (like the 75% ring in ref image)."""

    def __init__(self, cx, cy, outer_r, value_min, value_max,
                 label="", unit="", fmt="{:.0f}"):
        self.cx = cx
        self.cy = cy
        self.outer_r = outer_r
        self.inner_r = int(outer_r * 0.72)
        self.value_min = value_min
        self.value_max = value_max
        self.label = label
        self.unit = unit
        self.fmt = fmt
        self.display_value = 0.0
        self.target_value = 0.0

    def update(self, target):
        self.target_value = target
        self.display_value += (self.target_value - self.display_value) * SMOOTHING

    def draw(self, surface, fonts):
        cx, cy = self.cx, self.cy
        outer_r = self.outer_r
        inner_r = self.inner_r

        draw_shadow_circle(surface, cx, cy, outer_r, shadow_offset=6, shadow_alpha=50)
        draw_aa_circle(surface, cx, cy, outer_r, BEZEL_OUTER)
        draw_aa_circle(surface, cx, cy, outer_r - 3, BEZEL_INNER)
        draw_aa_circle(surface, cx, cy, inner_r + 2, GAUGE_FACE)

        ring_r = (inner_r + outer_r) / 2
        ring_w = outer_r - inner_r - 8

        # background track
        draw_thick_arc(surface, cx, cy, ring_r, ring_w, 90, -270,
                       color=PANEL_DARK, segments=80)

        # active arc
        vrange = self.value_max - self.value_min
        if vrange > 0:
            frac = max(0.0, min(1.0,
                (self.display_value - self.value_min) / vrange))
        else:
            frac = 0.0
        active_span = 270 * frac
        if active_span > 0.5:
            draw_thick_arc(surface, cx, cy, ring_r, ring_w,
                           90, 90 - active_span,
                           color_func=gradient_color_at,
                           segments=max(16, int(active_span)))

        # inner face
        draw_aa_circle(surface, cx, cy, inner_r, GAUGE_FACE)

        # value text
        val_text = self.fmt.format(self.display_value)
        val_surf = fonts["med"].render(val_text, True, TEXT_PRIMARY)
        vr = val_surf.get_rect(center=(cx, cy - 4))
        surface.blit(val_surf, vr)

        # unit
        unit_surf = fonts["unit_sm"].render(self.unit, True, TEXT_UNIT)
        ur = unit_surf.get_rect(center=(cx, cy + int(inner_r * 0.38)))
        surface.blit(unit_surf, ur)

        # label below gauge
        if self.label:
            lbl_surf = fonts["label_sm"].render(self.label, True, TEXT_MUTED)
            lr = lbl_surf.get_rect(center=(cx, cy + outer_r + 20))
            surface.blit(lbl_surf, lr)


class InfoPanel:
    """Dark rounded panel showing text info (like the weather card)."""

    def __init__(self, x, y, w, h):
        self.rect = (x, y, w, h)
        self.lines = []

    def set_lines(self, lines):
        self.lines = lines

    def draw(self, surface, fonts):
        x, y, w, h = self.rect
        draw_rounded_rect(surface, (x, y, w, h), PANEL_DARK, radius=16)
        # subtle inner highlight top edge
        draw_rounded_rect(surface, (x + 2, y + 2, w - 4, 2), PANEL_LIGHT, radius=1)

        # Small red accent dot (top-right, like the ref image)
        draw_aa_circle(surface, x + w - 28, y + 28, 10, ACCENT_RED)

        line_y = y + 22
        for text, color, font_key, align in self.lines:
            if not text:
                line_y += 8
                continue
            surf = fonts[font_key].render(text, True, color)
            if align == "center":
                r = surf.get_rect(center=(x + w // 2, line_y + surf.get_height() // 2))
            else:
                r = surf.get_rect(topleft=(x + 18, line_y))
            surface.blit(surf, r)
            line_y += surf.get_height() + 6


# ---------------------------------------------------------------------------
# Main dashboard
# ---------------------------------------------------------------------------

class Dashboard:
    def __init__(self):
        pygame.init()

        info = pygame.display.Info()
        self.width = info.current_w if info.current_w > 0 else TARGET_W
        self.height = info.current_h if info.current_h > 0 else TARGET_H

        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF,
        )
        pygame.display.set_caption("Sensor Dashboard")
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()
        self.running = True

        # Scale factor relative to 1280x720
        self.sx = self.width / TARGET_W
        self.sy = self.height / TARGET_H
        self.s = min(self.sx, self.sy)

        self._load_fonts()
        self._build_widgets()
        self._init_sensors()

        self.last_sensor_time = 0
        self.sensor_data = {
            "rpm": 0.0,
            "horiz_accel": 0.0,
            "yaw_deg": 0.0,
            "timestamp": "--",
            "rtc_active": False,
        }

    def _load_fonts(self):
        s = self.s
        font_path = None
        for p in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]:
            if os.path.exists(p):
                font_path = p
                break

        if font_path:
            def mk(sz):
                return pygame.font.Font(font_path, max(8, int(sz * s)))
        else:
            def mk(sz):
                return pygame.font.SysFont("dejavusans", max(8, int(sz * s)), bold=True)

        self.fonts = {
            "big":      mk(58),
            "med":      mk(42),
            "unit":     mk(22),
            "unit_sm":  mk(18),
            "label":    mk(16),
            "label_sm": mk(14),
            "info":     mk(20),
            "info_lg":  mk(32),
            "status":   mk(15),
        }

    def _build_widgets(self):
        s = self.s
        w, h = self.width, self.height

        # Main RPM gauge (left-center, large)
        rpm_r = int(155 * s)
        rpm_cx = int(220 * s)
        rpm_cy = int(h * 0.48)
        self.rpm_gauge = CircularGauge(
            rpm_cx, rpm_cy, rpm_r,
            value_min=0, value_max=3000,
            label="ENGINE", unit="RPM",
            show_needle=True, fmt="{:.0f}",
        )

        # Accel gauge (center, medium)
        accel_r = int(125 * s)
        accel_cx = int(530 * s)
        accel_cy = int(h * 0.48)
        self.accel_gauge = CircularGauge(
            accel_cx, accel_cy, accel_r,
            value_min=0, value_max=20.0,
            label="ACCEL", unit="m/s²",
            show_needle=False, fmt="{:.1f}",
        )

        # Heading progress ring (right-center)
        head_r = int(110 * s)
        head_cx = int(810 * s)
        head_cy = int(h * 0.46)
        self.heading_ring = ProgressRing(
            head_cx, head_cy, head_r,
            value_min=0, value_max=360,
            label="HEADING", unit="deg",
            fmt="{:.0f}°",
        )

        # Info panel (far right, dark card)
        panel_w = int(280 * s)
        panel_h = int(280 * s)
        panel_x = int(w - panel_w - int(30 * s))
        panel_y = int(h * 0.18)
        self.info_panel = InfoPanel(panel_x, panel_y, panel_w, panel_h)

        # Status bar rect (bottom strip)
        self.status_rect = (
            int(20 * s),
            int(h - 46 * s),
            int(w - 40 * s),
            int(34 * s),
        )

    def _init_sensors(self):
        try:
            self.reader = SensorReader(print_live=False)
            self.reader.setup()
            self.sensor_ok = True
            if self.reader.rtc_disabled_reason:
                print(self.reader.rtc_disabled_reason)
        except Exception as exc:
            print(f"Sensor init error: {exc}")
            self.reader = None
            self.sensor_ok = False

    def _poll_sensors(self):
        now_ms = pygame.time.get_ticks()
        if now_ms - self.last_sensor_time < SENSOR_POLL_MS:
            return
        self.last_sensor_time = now_ms

        if self.reader is None:
            return
        try:
            data = self.reader.read()
            self.sensor_data = data
            self.sensor_ok = True
        except Exception as exc:
            self.sensor_data["timestamp"] = f"ERR: {exc}"
            self.sensor_ok = False

    def _update(self):
        d = self.sensor_data
        self.rpm_gauge.update(d.get("rpm", 0.0))
        self.accel_gauge.update(d.get("horiz_accel", 0.0))
        self.heading_ring.update(d.get("yaw_deg", 0.0) % 360.0)

        # Info panel lines
        rtc_label = "RTC Active" if d.get("rtc_active") else "System Clock"
        status_color = ACCENT_BLUE if d.get("rtc_active") else ACCENT_ORANGE
        heading_val = d.get("yaw_deg", 0.0) % 360
        dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        compass = dirs[int(((heading_val + 22.5) % 360) / 45)]

        self.info_panel.set_lines([
            ("VEHICLE STATUS", TEXT_MUTED, "label", "left"),
            ("", TEXT_MUTED, "label", "left"),
            (f"{d.get('rpm', 0):.0f} RPM", TEXT_PRIMARY, "info_lg", "left"),
            ("", TEXT_MUTED, "label", "left"),
            (f"Accel  {d.get('horiz_accel', 0):.2f} m/s²", TEXT_PRIMARY, "info", "left"),
            (f"Heading  {heading_val:.0f}° {compass}", TEXT_PRIMARY, "info", "left"),
            ("", TEXT_MUTED, "label", "left"),
            (rtc_label, status_color, "label", "left"),
        ])

    def _draw(self):
        self.screen.fill(BG_COLOR)

        # subtle top gradient band
        for i in range(80):
            alpha = 1.0 - i / 80.0
            c = lerp_color((18, 18, 24), BG_COLOR, 1.0 - alpha)
            pygame.draw.line(self.screen, c, (0, i), (self.width, i))

        # Draw widgets
        self.rpm_gauge.draw(self.screen, self.fonts)
        self.accel_gauge.draw(self.screen, self.fonts)
        self.heading_ring.draw(self.screen, self.fonts)
        self.info_panel.draw(self.screen, self.fonts)

        # Bottom status bar
        sx, sy, sw, sh = self.status_rect
        draw_rounded_rect(self.screen, (sx, sy, sw, sh), PANEL_DARK, radius=8)

        ts = self.sensor_data.get("timestamp", "--")
        dot_color = (80, 220, 100) if self.sensor_ok else ACCENT_RED
        draw_aa_circle(self.screen, sx + 18, sy + sh // 2, 5, dot_color)

        status_text = f"  {ts}"
        if not self.sensor_ok:
            status_text += "   [SENSOR ERROR]"
        st_surf = self.fonts["status"].render(status_text, True, TEXT_MUTED)
        self.screen.blit(st_surf, (sx + 30, sy + (sh - st_surf.get_height()) // 2))

        # Title label top-left
        title_surf = self.fonts["info"].render("SENSOR DASHBOARD", True, TEXT_MUTED)
        self.screen.blit(title_surf, (int(24 * self.s), int(14 * self.s)))

        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_ESCAPE, pygame.K_q):
                            self.running = False

                self._poll_sensors()
                self._update()
                self._draw()
                self.clock.tick(FPS)
        finally:
            if self.reader:
                self.reader.close()
            pygame.quit()


def main():
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
