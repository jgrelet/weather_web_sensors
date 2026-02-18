"""
Testing DTH22: tempÃ©rature et lâ€™humiditÃ© ambiante du DHT22
https://www.upesy.fr/blogs/tutorials/pi-pico-dht22-with-micropython-humidity-temperature-sensor?srsltid=AfmBOoohPuB-2CDeTRwpk60TF0ISvYbHoqhk5zOZo6Xh-EGBbHDdPpT4&shpxid=029aea03-fb7b-4d0a-b835-923917c3fa59
Fortunately, such a library is included in the latest versions of MicroPython, so you don't need
to download an additional one. You can directly import the module with import dht .
"""

from machine import Pin
from time import sleep
import dht
from config import SENSORS

dht_cfg = SENSORS.get("dht22", {})
sensor = dht.DHT22(Pin(dht_cfg.get("pin", 13)))

while True:
  try:
    sleep(1)     # le DHT22 renvoie au maximum une mesure toute les 1s
    sensor.measure()     # RecuperÃ¨re les mesures du sensor
    print(f"Temperature : {sensor.temperature():.1f}Â°C")
    print(f"Humidity    : {sensor.humidity():.0f}%")
  except OSError as e:
    print("Echec reception")

