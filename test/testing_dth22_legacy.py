"""
Legacy DHT22 test script for ambient temperature and humidity.
Reference:
https://www.upesy.fr/blogs/tutorials/pi-pico-dht22-with-micropython-humidity-temperature-sensor
"""

from machine import Pin
from time import sleep
import dht
from config import SENSORS

dht_cfg = SENSORS.get("dht22", {})
sensor = dht.DHT22(Pin(dht_cfg.get("pin", 13)))

while True:
    try:
        sleep(1)  # DHT22 supports at most one measurement per second.
        sensor.measure()  # Read sensor values.
        print(f"Temperature: {sensor.temperature():.1f} C")
        print(f"Humidity:    {sensor.humidity():.0f}%")
    except OSError:
        print("Read failed")
