# Meteorological sensor measurement with RPI Pico 2W and web visualization.

This project is based from IoT Starters blog [Connecting BMP280 sensor with Raspberry Pi Pico W](https://iotstarters.com/connecting-bmp280-sensor-with-raspberry-pi-pico-w/)

## Materials Required
  
- [Raspberry Pico 2W](https://www.raspberrypi.com/products/raspberry-pi-pico-2/) 
- [DTH22](https://fr.aliexpress.com/item/32759901711.html?spm=a2g0o.order_list.order_list_main.61.1ab05e5bBsdUCw&gatewayAdapt=glo2fra): Temperature and humidity
- [AHT20 + BMP280](https://fr.aliexpress.com/item/1005008139283157.html?spm=a2g0o.order_list.order_list_main.66.1ab05e5bBsdUCw&gatewayAdapt=glo2fra): Temperature and atmospheric pressure
- Breadboard and jumper wires
- [Thonny](https://thonny.org/) IDE
- [Micropython](https://micropython.org/download/RPI_PICO2_W/)

## Wifi configuration
Define your wifi ssid and password in config.py file

## AHT20 + BMP280 
Connect the sensor to Pico 2w
- VDD -> Pin36  (3.3v)
- GND -> Pin3
- SDA -> Pin1 (GPIO0)
- SCL -> Pin2 (GPIO1)

## DHT22
- VCC -> Pin36  (3.3v)
- GND -> Pin3
- DAT -> Pin17 (GPIO13)

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
Edit and run main_terminal to check all sensors
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
Open web page on the adress given below:

![image](https://github.com/user-attachments/assets/a4a947ea-ab98-41d5-9230-b89f77d2cbc8)



