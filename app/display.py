import time

from machine import ADC, Pin
from ssd1306 import SSD1306_I2C
from config import APP
from app.timezone_utils import get_timezone_config, localtime_from_utc


class Display:
    def __init__(
        self,
        i2c,
        width=128,
        height=64,
        addr=None,
        timezone_cfg=None,
        presence_cfg=None,
        boot_message_seconds=0,
    ):
        if addr is None:
            addr = 0x3C
            try:
                devices = i2c.scan()
                if 0x3C in devices:
                    addr = 0x3C
                elif 0x3D in devices:
                    addr = 0x3D
            except Exception:
                # Fallback to default SSD1306 address when scan is unavailable.
                pass

        self._oled = SSD1306_I2C(width, height, i2c, addr=addr)
        self._timezone_cfg = timezone_cfg or get_timezone_config(APP)
        self._boot_message_ms = max(0, int(float(boot_message_seconds) * 1000))
        self._presence_pin = None
        self._presence_adc = None
        self._presence_pin_number = None
        self._presence_last_value = None
        self._motion_pending = False
        self._presence_suppressed_until_low = False
        self._visible = True
        self._display_until_ms = None
        self._last_reading = None
        presence_cfg = presence_cfg or {}
        self._presence_enabled = bool(presence_cfg.get("enabled", False))
        self._hold_ms = max(1, int(presence_cfg.get("hold_seconds", 20))) * 1000
        if self._presence_enabled:
            input_mode = str(presence_cfg.get("input_mode", "digital")).lower()
            pull_name = str(presence_cfg.get("pull", "down")).lower()
            pull = Pin.PULL_DOWN if pull_name == "down" else Pin.PULL_UP if pull_name == "up" else None
            pin_number = int(presence_cfg.get("pin", 16))
            self._presence_pin_number = pin_number
            if input_mode == "adc":
                threshold_volts = float(presence_cfg.get("threshold_volts", 2.4))
                self._presence_threshold = int(
                    max(0.0, min(3.3, threshold_volts)) * 65535 / 3.3
                )
                self._presence_adc = ADC(pin_number)
                initial_raw = self._presence_adc.read_u16()
                self._presence_last_value = int(initial_raw >= self._presence_threshold)
                print(
                    "OLED presence sensor: GP{} ADC initial={} raw={} threshold={}".format(
                        pin_number,
                        self._presence_last_value,
                        initial_raw,
                        self._presence_threshold,
                    )
                )
            else:
                self._presence_pin = (
                    Pin(pin_number, Pin.IN, pull)
                    if pull is not None
                    else Pin(pin_number, Pin.IN)
                )
                self._presence_last_value = self._presence_pin.value()
                print(
                    "OLED presence sensor: GP{} digital initial={}".format(
                        pin_number, self._presence_last_value
                    )
                )
                self._presence_pin.irq(trigger=Pin.IRQ_RISING, handler=self._on_motion)
            self._extend_visibility()

    def _on_motion(self, _pin):
        self._motion_pending = True

    def _extend_visibility(self):
        self._display_until_ms = time.ticks_add(time.ticks_ms(), self._hold_ms)

    def _power_on(self):
        if not self._visible:
            self._oled.poweron()
            self._visible = True
            print("OLED powered on by presence")

    def _power_off(self):
        if self._visible:
            self._oled.poweroff()
            self._visible = False
            print("OLED powered off after presence timeout")

    def poll(self):
        if not self._presence_enabled:
            return
        motion = self._motion_pending
        self._motion_pending = False
        presence_value = self._read_presence()
        if presence_value is not None:
            if presence_value != self._presence_last_value:
                print(
                    "OLED presence sensor: GP{} {} -> {}".format(
                        self._presence_pin_number,
                        self._presence_last_value,
                        presence_value,
                    )
                )
                self._presence_last_value = presence_value
            if self._presence_suppressed_until_low and not presence_value:
                self._presence_suppressed_until_low = False
                print("OLED presence sensor rearmed after radio transmission")
            if presence_value and not self._presence_suppressed_until_low:
                motion = True
        if motion:
            self._extend_visibility()
            was_visible = self._visible
            self._power_on()
            if not was_visible and self._last_reading:
                self._render_reading(self._last_reading)
        if (
            self._visible
            and self._display_until_ms is not None
            and time.ticks_diff(time.ticks_ms(), self._display_until_ms) >= 0
        ):
            self._power_off()

    def suppress_presence_until_low(self):
        if not self._presence_enabled:
            return
        self._motion_pending = False
        self._presence_suppressed_until_low = True
        print("OLED presence sensor suppressed during radio transmission")

    def _read_presence(self):
        if self._presence_adc:
            return int(self._presence_adc.read_u16() >= self._presence_threshold)
        if self._presence_pin:
            return self._presence_pin.value()
        return None

    def show_boot(self, lines):
        self._power_on()
        if self._presence_enabled:
            self._extend_visibility()
        self._oled.fill(0)
        y = 0
        for line in lines:
            self._oled.text(line, 0, y)
            y += 12
        self._oled.show()
        if self._boot_message_ms:
            time.sleep_ms(self._boot_message_ms)

    def show_reading(self, data):
        self._last_reading = dict(data or {})
        if self._presence_enabled:
            motion_active = (
                not self._presence_suppressed_until_low
                and (self._motion_pending or self._read_presence())
            )
            if motion_active:
                self._motion_pending = False
                self._extend_visibility()
                self._power_on()
            elif not self._visible:
                return
        self._render_reading(self._last_reading)

    def _render_reading(self, data):
        self._oled.fill(0)
        now = localtime_from_utc(time.localtime(), self._timezone_cfg)
        self._oled.text(
            "{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
                now[1], now[2], now[3], now[4], now[5]
            ),
            0,
            0,
        )
        self._oled.hline(0, 10, 128, 1)
        self._oled.text(
            "T:{}C H:{}%".format(
                data.get("temperature_c", "-"), data.get("humidity_pct", "-")
            ),
            0,
            18,
        )
        self._oled.text("P:{}hPa".format(data.get("pressure_hpa", "-")), 0, 30)
        self._oled.text(
            "W:{}km/h {}".format(
                data.get("wind_speed_kmh", "-"), data.get("wind_dir_cardinal", "-")
            ),
            0,
            42,
        )
        self._oled.text("R:{}mm".format(data.get("rain_mm_total", "-")), 0, 54)
        self._oled.show()
