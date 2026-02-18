"""
Quick terminal test for DHT22 + BMP280 readings.
Reference:
https://www.upesy.fr/blogs/tutorials/pi-pico-dht22-with-micropython-humidity-temperature-sensor
"""

from machine import Pin, I2C
import time
import ntptime

import dht
from bmp280 import BMP280I2C
from wlan import set_wlan

led_onboard = Pin("LED", Pin.OUT)
led_onboard.value(1)
set_wlan(led_onboard)
ntptime.settime()
dt = time.localtime()
print(
    "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        dt[0], dt[1], dt[2], dt[4], dt[5], dt[6]
    )
)

sensor = dht.DHT22(Pin(13))
bus = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
bmp280 = BMP280I2C(0x77, bus)
led_onboard.value(0)

while True:
    try:
        time.sleep(1)  # DHT22 supports at most one measurement per second.
        readout = bmp280.measurements
        sensor.measure()  # Read sensor values.
        print(f"Temperature: {sensor.temperature():.1f} C")
        print(f"Humidity:    {sensor.humidity():.0f}%")
        print(f"BMP280 temperature: {readout['t']:.1f} C, pressure: {readout['p']:.1f} hPa.")
    except OSError:
        print("Read failed")
