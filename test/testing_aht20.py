import utime
from machine import Pin, I2C

import ahtx0
from config import SENSORS

i2c_cfg = SENSORS.get("i2c_aux", SENSORS["i2c"])
i2c = I2C(
    id=i2c_cfg["id"],
    scl=Pin(i2c_cfg["scl_pin"]),
    sda=Pin(i2c_cfg["sda_pin"]),
    freq=i2c_cfg["freq"],
)

# Create the sensor object using I2C
sensor = ahtx0.AHT20(i2c)

while True:
    print("\nTemperature: %0.2f C" % sensor.temperature)
    print("Humidity: %0.2f %%" % sensor.relative_humidity)
    utime.sleep(5)

