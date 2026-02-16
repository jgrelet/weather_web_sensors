# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details: https://RandomNerdTutorials.com/raspberry-pi-pico-bme680-micropython/

from machine import Pin, I2C
from time import sleep
from bme680 import *
from config_sensors import SENSORS

i2c_cfg = SENSORS["i2c"]
bme_cfg = SENSORS.get("bme680", {})
i2c = I2C(
    id=i2c_cfg["id"],
    scl=Pin(i2c_cfg["scl_pin"]),
    sda=Pin(i2c_cfg["sda_pin"]),
    freq=i2c_cfg["freq"],
)

bme = BME680_I2C(i2c=i2c, address=bme_cfg.get("address", 0x77))

while True:
  try:
    temp = str(round(bme.temperature, 2)) + ' C'
    #temp = (bme.temperature) * (9/5) + 32
    #temp = str(round(temp, 2)) + 'F'
    
    hum = str(round(bme.humidity, 2)) + ' %'
    
    pres = str(round(bme.pressure, 2)) + ' hPa'
    
    gas = str(round(bme.gas/1000, 2)) + ' KOhms'

    print('Temperature:', temp)
    print('Humidity:', hum)
    print('Pressure:', pres)
    print('Gas:', gas)
    print('-------')
  except OSError as e:
    print('Failed to read sensor.')
 
  sleep(5)
