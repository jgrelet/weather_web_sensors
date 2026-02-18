# Source: Electrocredible.com, Language: MicroPython
import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

from config import SENSORS

WIDTH = 128
HEIGHT = 64

i2c1_cfg = SENSORS["i2c"]
i2c1 = I2C(
    i2c1_cfg["id"],
    scl=Pin(i2c1_cfg["scl_pin"]),
    sda=Pin(i2c1_cfg["sda_pin"]),
    freq=i2c1_cfg["freq"],
)
time.sleep(0.1)

print(f"Scan I2C{i2c1_cfg['id']} bus...")
i2c1_devices = i2c1.scan()
if len(i2c1_devices) == 0:
    print(f"No I2C{i2c1_cfg['id']} device !")
else:
    print(f"I2C{i2c1_cfg['id']} devices found:", len(i2c1_devices))

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c1, addr=SENSORS["display"].get("addr", 0x3C))
oled.fill(0)
oled.text(f"Devices: {len(i2c1_devices)} I2C{i2c1_cfg['id']}", 0, 0)
y = 12
for device in i2c1_devices:
    print("address: ", device, " | Hexa address: ", hex(device))
    oled.text(f"Addr: {hex(device)}", 0, y)
    y += 12
oled.show()

i2c0_cfg = SENSORS.get("i2c_aux")
if i2c0_cfg:
    i2c0 = I2C(
        i2c0_cfg["id"],
        scl=Pin(i2c0_cfg["scl_pin"]),
        sda=Pin(i2c0_cfg["sda_pin"]),
        freq=i2c0_cfg["freq"],
    )
    time.sleep(0.1)
    print(f"Scan I2C{i2c0_cfg['id']} bus...")
    i2c0_devices = i2c0.scan()
    if len(i2c0_devices) == 0:
        print(f"No I2C{i2c0_cfg['id']} device !")
    else:
        print(f"I2C{i2c0_cfg['id']} devices found:", len(i2c0_devices))
    for device in i2c0_devices:
        print("address: ", device, " | Hexa address: ", hex(device))

