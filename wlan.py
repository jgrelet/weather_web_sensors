import network
import socket
import time
from machine import Pin

from config_wifi import ssid, password


def start_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
    return wlan


def stop_wlan(wlan=None):
    wlan = wlan or network.WLAN(network.STA_IF)
    try:
        wlan.disconnect()
    except Exception:
        pass
    wlan.active(False)


def wlan_ip(wlan):
    if wlan and wlan.isconnected():
        return wlan.ifconfig()[0]
    return None


def set_wlan(led_onboard):
    #Connect to WLAN
   
    wlan = start_wlan()
    while wlan.isconnected() == False:
        led_onboard.value(1)
        print('Connecting...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print('Connection successful')
    print(f'Connected on {ip}')
    return wlan, ip
