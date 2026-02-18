from machine import Pin, I2C
from time import sleep
import time
import ntptime
from bme680 import BME680_I2C
from ssd1306 import SSD1306_I2C

from wlan import set_wlan
from config import SENSORS

WIDTH = 128
HEIGHT = 64

i2c_cfg = SENSORS["i2c"]
bme_cfg = SENSORS.get("bme680", {})
display_cfg = SENSORS.get("display", {})
i2c = I2C(
    id=i2c_cfg["id"],
    scl=Pin(i2c_cfg["scl_pin"]),
    sda=Pin(i2c_cfg["sda_pin"]),
    freq=i2c_cfg["freq"],
)

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=display_cfg.get("addr", 0x3C))
bme = BME680_I2C(i2c=i2c, address=bme_cfg.get("address", 0x77))
led_onboard = Pin("LED", Pin.OUT)

oled.fill(0)
oled.text("Initializing...", 0, 0)
oled.show()

led_onboard.value(1)
set_wlan(led_onboard)
oled.text("Wifi OK", 0, 12)
oled.show()

ntptime.settime()
oled.text("NTP OK", 0, 24)
oled.show()
led_onboard.value(0)

while True:
    try:
        oled.fill(0)
        year, month, day, hour, minute, second, _, _ = time.localtime()
        date_time = f"{hour:02d}:{minute:02d}:{second:02d} {month}/{day}/{year-2000:02d}"

        temp = str(round(bme.temperature, 2)) + " C"
        hum = str(round(bme.humidity, 2)) + " %"
        pres = str(round(bme.pressure, 2)) + " hPa"
        gas = str(round(bme.gas / 1000, 2)) + " KOhms"

        print(date_time)
        print("Temperature:", temp)
        print("Humidity:", hum)
        print("Pressure:", pres)
        print("Gas:", gas)
        print("-------")

        oled.text(date_time, 0, 0)
        oled.text(f"Temp: {temp}", 0, 12)
        oled.text(f"Pres: {pres}", 0, 24)
        oled.text(f"Humi: {hum}", 0, 36)
        oled.text(f"Gas:  {gas}", 0, 48)
        oled.show()
        led_onboard.value(1)
    except OSError:
        print("Failed to read sensor.")

    sleep(1)

