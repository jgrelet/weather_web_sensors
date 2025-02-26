"""
Testing DTH22: température et l’humidité ambiante du DHT22
https://www.upesy.fr/blogs/tutorials/pi-pico-dht22-with-micropython-humidity-temperature-sensor?srsltid=AfmBOoohPuB-2CDeTRwpk60TF0ISvYbHoqhk5zOZo6Xh-EGBbHDdPpT4&shpxid=029aea03-fb7b-4d0a-b835-923917c3fa59
"""

from machine import Pin
from time import sleep
import dht

capteur = dht.DHT22(Pin(13))

while True:
  try:
    sleep(1)     # le DHT22 renvoie au maximum une mesure toute les 1s
    capteur.measure()     # Recuperère les mesures du capteur
    print(f"Temperature : {capteur.temperature():.1f}°C")
    print(f"Humidite    : {capteur.humidity():.1f}%")
  except OSError as e:
    print("Echec reception")