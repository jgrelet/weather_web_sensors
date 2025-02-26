# Read the sensor values:
#    (temperature_celcius, pressure_hpa, humidity_percent)
#    Humidity only applies to BME280 only, not BMP280. 
#
from machine import I2C, Pin
# BME280 aslo work for BMP280
#from bmp280 import BMP280
from bmp280 import BMP280I2C
from time import sleep

bus = I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
bmp280 = BMP280I2C(0x77, bus)
while True:
    # returns a tuple with (temperature, pressure_hPa, humidity)
    #print( bmp280.raw_values )
    readout= bmp280.measurements
    print(readout)
    print(f"Temperature : {readout['t']} °C, pressure: {readout['p']} hPa.")
    sleep(1)