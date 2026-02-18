# Read the sensor values:
#    (temperature_celsius, pressure_hpa)
#    Humidity is not available on BMP280.
from machine import I2C, Pin
from time import sleep

from bmp280 import BMP280I2C
from config import SENSORS

i2c_cfg = SENSORS.get("i2c_aux", SENSORS["i2c"])
bme280_cfg = SENSORS.get("bme280", {})

bus = I2C(
    i2c_cfg["id"],
    sda=Pin(i2c_cfg["sda_pin"]),
    scl=Pin(i2c_cfg["scl_pin"]),
    freq=i2c_cfg["freq"],
)
bmp280 = BMP280I2C(bme280_cfg.get("address", 0x77), bus)

while True:
    readout = bmp280.measurements
    print(readout)
    print(f"Temperature: {readout['t']} C, pressure: {readout['p']} hPa.")
    sleep(1)

