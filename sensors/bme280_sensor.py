from machine import I2C, Pin
from bmp280 import BMP280I2C


class BME280Sensor:
    def __init__(self, i2c_id=0, sda_pin=4, scl_pin=5, i2c_freq=200000, address=0x77):
        self.i2c = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=i2c_freq)
        self.sensor = BMP280I2C(address, self.i2c)

    def read(self):
        values = self.sensor.measurements
        return {
            "sensor_bme280_temperature_c": round(values["t"], 2),
            "sensor_bme280_pressure_hpa": round(values["p"], 2),
        }
