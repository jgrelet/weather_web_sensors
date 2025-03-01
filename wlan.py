import network
import socket
import time
from machine import Pin

from config import ssid, password


def set_wlan(led_onboard):
    #Connect to WLAN
   
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        led_onboard.value(1)
        print('Connecting...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print('Connection successful')
    print(f'Connected on {ip}')
