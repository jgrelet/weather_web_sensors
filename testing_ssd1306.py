# Source: Electrocredible.com, Language: MicroPython

# Import necessary modules
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
# Pin numbers for I2C communication
sda_pin=Pin(0)
scl_pin=Pin(1)
# Display dimensions
WIDTH =128 
HEIGHT= 32
# Set up I2C communication
i2c=I2C(0,scl=scl_pin,sda=sda_pin,freq=200000)
time.sleep(0.1)

print('Scan i2c bus...')
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))

  for device in devices:  
    print("Decimal address: ",device," | Hexa address: ",hex(device))

# Initialize SSD1306 display with I2C interface
oled = SSD1306_I2C(WIDTH,HEIGHT,i2c)
while True:
    # Clear the display
    oled.fill(0)
    # text, x-position, y-position
    #oled.text("Hello world ,", 0, 0) 
    oled.text("Temp: 21.3 C", 0, 0)
    oled.text("Pres: 1012.1 mb", 0, 12)
    oled.text("Hum:  63 %", 0, 24)
    # Show the updated display
    oled.show()