# Meteorological sensor measurement with RPI Pico 2W and web visualization.

This project is based from IoT Starters blog [Connecting BMP280 sensor with Raspberry Pi Pico W](https://iotstarters.com/connecting-bmp280-sensor-with-raspberry-pi-pico-w/)

## Materials Required
  
- [Raspberry Pico 2W](https://www.raspberrypi.com/products/raspberry-pi-pico-2/) 
- [DTH22](https://fr.aliexpress.com/item/32759901711.html?spm=a2g0o.order_list.order_list_main.61.1ab05e5bBsdUCw&gatewayAdapt=glo2fra): Temperature and humidity
- [AHT20 + BMP280](https://fr.aliexpress.com/item/1005008139283157.html?spm=a2g0o.order_list.order_list_main.66.1ab05e5bBsdUCw&gatewayAdapt=glo2fra): Temperature and atmospheric pressure
- Breadboard and jumper wires
- [Thonny](https://thonny.org/) IDE
- [Micropython](https://micropython.org/download/RPI_PICO2_W/)

## Wlan configuration

Define your Wifi ssid and password in [config.py](https://github.com/jgrelet/weather_web_sensors/blob/main/config.py) file

## Connect sensors to Pico 2w

### Diagram

![image](https://github.com/user-attachments/assets/89be49a1-b381-4cd1-b109-21f744a02b64)

### AHT20 + BMP280 

- VDD -> Pin36  (3.3v)
- GND -> Pin3
- SDA -> Pin1 (GP0)
- SCL -> Pin2 (GP1)

### DHT22

- VCC -> Pin36  (3.3v)
- GND -> Pin3
- DAT -> Pin17 (GP13)

![image](https://github.com/user-attachments/assets/dd9a2923-c1ae-4107-bdb5-fe882f0aea93)


## Run scanner.py to scan I2C bus (AHT20 + BMP280 sensors)

``` bash
>>> %Run -c $EDITOR_CONTENT

MPY: soft reboot
Scan i2c bus...
i2c devices found: 2
Decimal address:  56  | Hexa address:  0x38
Decimal address:  119  | Hexa address:  0x77
```

## Testing
Edit and run main_terminal to check all sensors in text mode
``` bash
MPY: soft reboot
Temperature : 23.0°C
Humidity    : 47%
Temperature : 23.5 °C, pressure: 1008.5 hPa.
```
Run main.py 

``` bash
MPY: soft reboot
Connection successful
Connected on 192.168.1.36
```
Now copy the IP address into your web browser, in this case http://192.168.29.36. The web server will open and display the sensor data as shown below:

![image](https://github.com/user-attachments/assets/a4a947ea-ab98-41d5-9230-b89f77d2cbc8)



