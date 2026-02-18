import network
import ntptime
from machine import RTC
import utime
from config_wifi import ssid, password

# Connect to Wi-Fi.
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for Wi-Fi connection.
while not wlan.isconnected():
    utime.sleep(1)

print("Connected to Wi-Fi")

# Sync time with NTP server.
ntptime.settime()

# Create RTC instance.
rtc = RTC()

# Check and print synced RTC datetime.
print("RTC synchronized with NTP:", rtc.datetime())

# Print current RTC time every second.
while True:
    print("Current time:", rtc.datetime())
    utime.sleep(1)
