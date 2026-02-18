# MicroPython I2C scanner.
# Returns decimal and hexadecimal addresses for each detected I2C device.
# Source inspiration: https://projetsdiy.fr - https://diyprojects.io (Dec. 2017)
"""
MPY: soft reboot
Scan i2c bus...
i2c devices found: 2
Decimal address: 56  | Hex address: 0x38
Decimal address: 119 | Hex address: 0x77
"""

from machine import I2C, Pin

i2c = I2C(id=1, scl=Pin(3), sda=Pin(2))
# i2c = I2C(id=0, scl=Pin(5), sda=Pin(4))

print("Scan i2c bus...")
devices = i2c.scan()

if len(devices) == 0:
    print("No i2c device!")
else:
    print("i2c devices found:", len(devices))
    for device in devices:
        print("Decimal address:", device, "| Hex address:", hex(device))
