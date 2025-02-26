# Scanner i2c en MicroPython | MicroPython i2c scanner
# Renvoi l'adresse en decimal et hexa de chaque device connecte sur le bus i2c
# Return decimal and hexa adress of each i2c device
# https://projetsdiy.fr - https://diyprojects.io (dec. 2017)
"""
MPY: soft reboot
Scan i2c bus...
i2c devices found: 2
Decimal address:  56  | Hexa address:  0x38
Decimal address:  119  | Hexa address:  0x77
"""

from machine import *
i2c = I2C(id=0, scl=Pin(1), sda=Pin(0))

print('Scan i2c bus...')
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))

  for device in devices:  
    print("Decimal address: ",device," | Hexa address: ",hex(device))