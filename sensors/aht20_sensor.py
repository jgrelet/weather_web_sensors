from machine import I2C, Pin
import ahtx0


class AHT20Sensor:
    def __init__(self, i2c_id=0, sda_pin=4, scl_pin=5, i2c_freq=200000):
        self.i2c = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=i2c_freq)
        self.sensor = ahtx0.AHT20(self.i2c)

    def read(self):
        return {
            "sensor_aht20_temperature_c": round(self.sensor.temperature, 2),
            "sensor_aht20_humidity_pct": round(self.sensor.relative_humidity, 2),
        }
