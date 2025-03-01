import network
import socket
import time
import ntptime

from machine import Pin, I2C
from bmp280 import BMP280I2C
import dht  # humidity
import gc
from config import ssid, password
from wlan import set_wlan

# this code is executed during import
gc.collect()

led_onboard = Pin("LED", Pin.OUT)
led_onboard.value(1)
set_wlan(led_onboard)

# Synchroniser l'heure avec un serveur NTP
ntptime.settime()

# Sensor Configuration
i2c = I2C(0, sda = Pin(0), scl = Pin(1), freq = 1000000)
bmp = BMP280I2C(0x77, i2c)
time.sleep(1)
sensor = dht.DHT22(Pin(13))
led_onboard.value(0)

def web_page():
    
    try:
        led_onboard.value(1)
        #time.sleep(1)     # le DHT22 renvoie au maximum une mesure toute les 1s      
        readout_bmp = bmp.measurements
        sensor.measure()
    except OSError as e:
        print("Reading sensors failed")
        
    temp = readout_bmp['t']
    pres = readout_bmp['p']
    hum = sensor.humidity()

    p_bar = pres/100000
    p_mmHg = pres/133.3224
    
    temp_c2f= (temp * (9/5) + 32)
    temp = "{:.1f}".format(temp)
    temp_f= "{:.1f}".format(temp_c2f)
    pres_p = "{:.1f}".format(pres)
    pres_bar = "{:.4f}".format(p_bar)
    pres_hg = "{:.1f}".format(p_mmHg)
    hum = "{:.0f}".format(hum)
    year, month, day, hour, minute, second, weekday, yearday = time.localtime()
    date_time = str(f"{month:02d}/{day:02d}/{year} {hour:02d}:{minute:02d}:{second:02d}")
        
    #HTML CODE for Webserver 
    html = """<html>
    <head>
  <title>Raspberry Pico W Web Server</title>
  <meta http-equiv="refresh" content="10">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
  <link rel="icon" href="data:,">
  <style>
    html {font-family: Arial; display: inline-block; text-align: center;}
    p {  font-size: 1.2rem;}
    body {  margin: 0;}
    .topnav { overflow: hidden; background-color: #f8af73; color: rgb(0, 0, 0); font-size: 1.7rem; }
    .content { padding: 10px; }
    .card { background-color: rgb(255, 255, 255); box-shadow: 2px 2px 12px 1px rgba(140,140,140,.5); }
    .cards { max-width: 700px; margin: 0 auto; display: grid; grid-gap: 2rem; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
    .reading { font-size: 2.8rem; }
    .card.temperature { color: #544bd6; }
    .card.humidity { color: #17bebb; }
    .card.pressure { color: #d9415f; }
  </style>
</head>
<body>
  <div class="topnav">
    <h2><u>Rpi Pico 2W Web Server using BMP280 and DHT22 sensors</u></h2>
  </div>
  <div class="content">
    <h2>""" + str(date_time) + " UTC" + """</h2>
  </div>
  <div class="content">
    <div class="cards">
      <div class="card temperature">
        <h4><i class="fas fa-thermometer-half"></i>Temp. Celsius</h4><p><span class="reading">""" + str(temp) + """ &#8451; </p>
      </div>
      <div class="card temperature">
        <h4><i class="fas fa-thermometer-half"></i> Temp. Fahrenheit</h4><p><span class="reading">""" + str(temp_f) + """ &#8457; </p>
      </div>
      <div class="card pressure">
        <h4><i class="fas fa-angle-double-down"></i> PRESSURE</h4><p><span class="reading">""" + str(pres_p) + """ Pa</p>
      </div>
      <div class="card pressure">
        <h4><i class="fas fa-angle-double-down"></i> PRESSURE</h4><p><span class="reading">""" + str(pres_bar) + """ bar</p>
      </div>
      <div class="card pressure">
        <h4><i class="fas fa-angle-double-down"></i> PRESSURE</h4><p><span class="reading">""" + str(pres_hg) + """ mmHg</p>
      </div>
      <div class="card humidity">
        <h4><i class="fas fa-angle-double-down"></i> HUMIDITY</h4><p><span class="reading">""" + str(hum) + """ %</p>
      </div>
    </div>
  </div>
</body>

</html>"""
    led_onboard.value(0)
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  try:
    if gc.mem_free() < 102000:
      gc.collect()
    conn, addr = s.accept()
    conn.settimeout(3.0)
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = str(request)
    print('Content = %s' % request)
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')