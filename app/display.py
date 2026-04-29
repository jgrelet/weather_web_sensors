import time

from ssd1306 import SSD1306_I2C


def _days_in_month(year, month):
    if month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return 29
        return 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def _weekday(year, month, day):
    offsets = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)
    adjusted_year = year - 1 if month < 3 else year
    sunday_based = (
        adjusted_year
        + adjusted_year // 4
        - adjusted_year // 100
        + adjusted_year // 400
        + offsets[month - 1]
        + day
    ) % 7
    return (sunday_based - 1) % 7


def _last_sunday_day(year, month):
    days = _days_in_month(year, month)
    weekday = _weekday(year, month, days)
    return days - ((weekday + 1) % 7)


def _is_paris_dst(utc_dt):
    year, month, day, hour, _, _, _, _ = utc_dt
    if month < 3 or month > 10:
        return False
    if 3 < month < 10:
        return True

    march_switch_day = _last_sunday_day(year, 3)
    october_switch_day = _last_sunday_day(year, 10)
    if month == 3:
        return day > march_switch_day or (day == march_switch_day and hour >= 1)
    return day < october_switch_day or (day == october_switch_day and hour < 1)


def _paris_localtime(utc_dt=None):
    if utc_dt is None:
        utc_dt = time.localtime()

    year, month, day, hour, minute, second, weekday, yearday = utc_dt
    hour += 2 if _is_paris_dst(utc_dt) else 1

    while hour >= 24:
        hour -= 24
        day += 1
        weekday = (weekday + 1) % 7
        if day > _days_in_month(year, month):
            day = 1
            month += 1
            if month > 12:
                month = 1
                year += 1

    return (year, month, day, hour, minute, second, weekday, yearday)


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
        now = _paris_localtime(time.localtime())
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
