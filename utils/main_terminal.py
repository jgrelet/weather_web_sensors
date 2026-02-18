"""
Testing DTH22: tempÃ©rature et lâ€™humiditÃ© ambiante du DHT22
https://www.upesy.fr/blogs/tutorials/pi-pico-dht22-with-micropython-humidity-temperature-sensor?srsltid=AfmBOoohPuB-2CDeTRwpk60TF0ISvYbHoqhk5zOZo6Xh-EGBbHDdPpT4&shpxid=029aea03-fb7b-4d0a-b835-923917c3fa59
Fortunately, such a library is included in the latest versions of MicroPython, so you don't need
to download an additional one. You can directly import the module with import dht .
"""

from machine import Pin, I2C
import time
import ntptime

import dht
from bmp280 import BMP280I2C
from config_wifi import ssid, password
from wlan import set_wlan

led_onboard = Pin("LED", Pin.OUT)
led_onboard.value(1)
set_wlan(led_onboard)
ntptime.settime()
dt = time.localtime()
print("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(dt[0], dt[1], dt[2], dt[4], dt[5], dt[6]))

sensor = dht.DHT22(Pin(13))
bus = I2C(1,sda=Pin(2), scl=Pin(3), freq=400000)
bmp280 = BMP280I2C(0x77, bus)
led_onboard.value(0)

while True:
  try:
    time.sleep(1)     # le DHT22 renvoie au maximum une mesure toute les 1s
    readout= bmp280.measurements
    sensor.measure()     # RecuperÃ¨re les mesures du sensor
    print(f"Temperature : {sensor.temperature():.1f}Â°C")
    print(f"Humidity    : {sensor.humidity():.0f}%")
    print(f"Temperature : {readout['t']:.1f} Â°C, pressure: {readout['p']:.1f} hPa.")
  except OSError as e:
    print("Echec reception")
