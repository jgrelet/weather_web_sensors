# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details: https://RandomNerdTutorials.com/raspberry-pi-pico-bme680-micropython/

from machine import Pin, I2C
from time import sleep
import ntptime
from bme680 import *
from ssd1306 import SSD1306_I2C
from config import ssid, password
from wlan import set_wlan

# Display dimensions
WIDTH =128 
HEIGHT= 64

# RPi Pico - Pin assignment
i2c = I2C(id=0, scl=Pin(1), sda=Pin(0))

# Initialize SSD1306 display with I2C interface
oled = SSD1306_I2C(WIDTH,HEIGHT,i2c)

# Initialize BME680 sensor with I2C interface
# BME680 I2C address is 0x76 or 0x77
bme = BME680_I2C(i2c=i2c)
led_onboard = Pin("LED", Pin.OUT)

# Clear the display
oled.fill(0)
print("Initializing...,")
oled.text("Initializing...,", 0, 0) 
oled.show()

led_onboard.value(1)
set_wlan(led_onboard)
oled.text("Wifi Ok...,", 0, 12) 
oled.show()

# Synchroniser l'heure avec un serveur NTP
ntptime.settime()
oled.text("NTP Ok...", 0, 24) 
oled.show()

led_onboard.value(0)


while True:
  try:

    led_onboard.value(0)
    # Clear the display
    oled.fill(0)

    year, month, day, hour, minute, second, weekday, yearday = time.localtime()
    date_time = f"{hour:02d}:{minute:02d}:{second:02d} {month}/{day}/{year-2000:02d} "

    temp = str(round(bme.temperature, 2)) + ' C'
    #temp = (bme.temperature) * (9/5) + 32
    #temp = str(round(temp, 2)) + 'F'
    
    hum = str(round(bme.humidity, 2)) + ' %'
    pres = str(round(bme.pressure, 2)) + ' hPa'
    gas = str(round(bme.gas/1000, 2)) + ' KOhms'

    print(f"{date_time}")
    print('Temperature:', temp)
    print('Humidity:', hum)
    print('Pressure:', pres)
    print('Gas:', gas)
    print('-------')
    oled.text(f"{date_time}", 0, 0)
    oled.text(f"Temp: {temp}", 0, 12)
    oled.text(f"Pres: {pres}", 0, 24)
    oled.text(f"Humi: {hum}", 0, 36)
    oled.text(f"Gas: {gas}", 0, 48)
    # Show the updated display
    oled.show()
    led_onboard.value(1)
  except OSError as e:
    print('Failed to read sensor.')
 
  sleep(1)
