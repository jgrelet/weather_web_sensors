from ssd1306 import SSD1306_I2C


class Display:
    def __init__(self, i2c, width=128, height=64, addr=None):
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

    def show_boot(self, lines):
        self._oled.fill(0)
        y = 0
        for line in lines:
            self._oled.text(line, 0, y)
            y += 12
        self._oled.show()

    def show_reading(self, data):
        self._oled.fill(0)
        self._oled.text("Weather debug", 0, 0)
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
