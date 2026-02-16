import time
from machine import Pin
import dht


class DHT22Sensor:
    def __init__(self, pin=13, min_interval_ms=2000):
        self.sensor = dht.DHT22(Pin(pin))
        self.min_interval_ms = min_interval_ms
        self._last_read_ms = None
        self._last_data = {}

    def read(self):
        now = time.ticks_ms()
        if (
            self._last_read_ms is None
            or time.ticks_diff(now, self._last_read_ms) >= self.min_interval_ms
        ):
            self.sensor.measure()
            self._last_data = {
                "sensor_dht22_temperature_c": round(self.sensor.temperature(), 2),
                "sensor_dht22_humidity_pct": round(self.sensor.humidity(), 2),
            }
            self._last_read_ms = now
        return self._last_data
