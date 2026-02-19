# Weather Web Sensors - Raspberry Pi Pico 2W

MicroPython weather station with a local web dashboard and multi-sensor comparison.
This project is based on the IoT Starters blog post [Connecting BMP280 sensor with Raspberry Pi Pico W](https://iotstarters.com/connecting-bmp280-sensor-with-raspberry-pi-pico-w/).

## Hardware

- [Raspberry Pi Pico 2W](https://www.raspberrypi.com/products/raspberry-pi-pico-2/)
- [BME680](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf) (temperature, humidity, pressure, gas)
- [DHT22](https://fr.aliexpress.com/item/32759901711.html?spm=a2g0o.order_list.order_list_main.61.1ab05e5bBsdUCw&gatewayAdapt=glo2fra): temperature and humidity
- [AHT20 + BMP280](https://fr.aliexpress.com/item/1005008139283157.html?spm=a2g0o.order_list.order_list_main.66.1ab05e5bBsdUCw&gatewayAdapt=glo2fra): temperature and atmospheric pressure
- [OLED SSD1306 display](https://fr.aliexpress.com/item/1005007706726114.html?spm=a2g0o.order_list.order_list_main.17.11c35e5bhBt9Yk&gatewayAdapt=glo2fra)
- Wind sensor and rain gauge (not implemented)
- [DS3231](https://www.analog.com/media/en/technical-documentation/data-sheets/ds3231.pdf) (RTC module)
- Breadboard and [jumper wires](https://fr.aliexpress.com/item/1005007430055417.html?spm=a2g0o.order_list.order_list_main.16.11c35e5bhBt9Yk&gatewayAdapt=glo2fra)
- [Thonny](https://thonny.org/) IDE or Visual Studio Code with [MicroPico](https://github.com/paulober/MicroPico)
- [MicroPython for Pico 2W](https://micropython.org/download/RPI_PICO2_W/)

## I2C and GPIO Mapping

### Diagram

![image](https://github.com/user-attachments/assets/89be49a1-b381-4cd1-b109-21f744a02b64)

### I2C1 Bus (primary)

- SDA: `GP2`, SCL: `GP3`, `id=1`
- `0x3C`: SSD1306
- `0x68`: DS3231 (RTC)
- `0x57`: AT24C32 (RTC module EEPROM)
- `0x77`: BME680

### I2C0 Bus (auxiliary)

- SDA: `GP4`, SCL: `GP5`, `id=0`
- `0x38`: AHT20
- `0x77`: BME280/BMP280

### Direct GPIO

- `GP13`: DHT22

## Configuration

Sensor and bus settings are in `config.py` (`SENSORS` dictionary).

### Wi-Fi credentials without exposing secrets

`config_wifi.py` loads `wifi_secrets.py` when present.

1. Copy `wifi_secrets.example.py` to `wifi_secrets.py`
2. Fill in:

```python
ssid = "YOUR_WIFI_SSID"
password = "YOUR_WIFI_PASSWORD"
```

`wifi_secrets.py` is gitignored.

## NTP and DS3231 RTC

Sync policy is configured in `config.py` -> `APP`:

- `ntp_sync_mode = "never" | "always" | "auto" | "pin"`
- `ntp_min_year` for `auto` mode
- `ntp_trigger_pin`, `ntp_trigger_active_high`, `ntp_trigger_pull` for `pin` mode

Behavior:

- At boot, time is loaded from the DS3231.
- If NTP sync is performed, time is written back to the DS3231.

## Web UI

- Summary cards (weather + wind + rain)
- Sensor comparison table with deltas (`Delta T/H/P`)
- Manual NTP endpoint: `GET /sync-ntp`
- UI button: "Sync NTP now"

## Run

1. Flash MicroPython on Pico 2W
2. Deploy the project
3. Run `main.py`
4. Open the displayed IP in a browser (example: `http://192.168.1.54`)

## Export Visualization (UDP and MQTT)

### UDP (direct JSON payload)

Pico configuration (`config.py` -> `EXPORTS["udp"]`):

```python
"udp": {
    "enabled": True,
    "host": "192.168.1.48",  # PC IP running the receiver
    "port": 9999,
}
```

Receive on PC:

```bash
python tools/udp_receiver.py --host 0.0.0.0 --port 9999
```

Note:
- Export is sent on each sensor read (in this app, when an HTTP request hits the web UI).

### MQTT (publish through broker)

Quick Mosquitto install on Windows with [Scoop](https://scoop.sh/) (a command-line installer for Windows):

```bash
scoop install mosquitto
```

Start broker with network listener (not local-only):

1. Create `mosquitto.conf` (without BOM, preferably ASCII) with:

```conf
listener 1883 0.0.0.0
allow_anonymous true
```

2. Start Mosquitto with this config:

```bash
mosquitto -c .\mosquitto.conf -v
```

3. Verify subscription from the PC:

```bash
mosquitto_sub -h 192.168.1.48 -p 1883 -t weather/sensors -v
```

If Mosquitto shows `Starting in local only mode`, the broker was not started with a network listener.

Pico configuration (`config.py` -> `EXPORTS["mqtt"]`):

```python
"mqtt": {
    "enabled": True,
    "broker": "192.168.1.48",  # MQTT broker IP (for example Mosquitto)
    "port": 1883,
    "topic": "weather/sensors",
    ...
}
```

PC visualization (subscriber):

```bash
mosquitto_sub -h 192.168.1.48 -p 1883 -t weather/sensors -v
```

Quick validation memo:

```bash
# 1) Show topic + JSON payload
mosquitto_sub -h 192.168.1.48 -p 1883 -t weather/sensors -v

# 2) Show MQTT client debug exchanges (CONNECT/SUBSCRIBE/PUBLISH)
mosquitto_sub -d -h 192.168.1.48 -p 1883 -t weather/sensors -v

# 3) Validate one JSON payload decoding
mosquitto_sub -h 192.168.1.48 -p 1883 -t weather/sensors -C 1| python -m json.tool

# 4) Validate all JSON payload decoding (use with Powershell)
mosquitto_sub -h 192.168.1.48 -p 1883 -t weather/sensors |
  ForEach-Object {
    if ($_ -and $_.Trim()) {
      $_ | python -m json.tool
    }
  }
```

Network analysis (optional, Wireshark):
- Display filter: `tcp.port == 1883` (or `mqtt`)
- Shows frames such as `CONNECT`, `CONNACK`, `PUBLISH`, and others

Why different ports:
- MQTT usually uses TCP/1883 (or 8883 with TLS) through a broker
- UDP export is a separate transport, here on UDP/9999 to a local receiver

Quick troubleshooting:
- `connection refused` on `192.168.1.48:1883`: broker not started, missing network listener, or Windows firewall blocking TCP 1883
- `Unknown configuration variable '...listener'`: `mosquitto.conf` saved with UTF-8 BOM. Save without BOM (ASCII or UTF-8 without BOM)

## Serial Port and Baud Rate

`SerialExporter` in this project writes through `print()` to USB serial output (CDC/REPL).
There is no `baudrate` setting in `config.py` for this exporter, unlike a classic TTL UART setup.

`tools/serial_receiver.py` (`--baudrate`) applies to PC-side serial reading when using a system/hardware serial port.

## Hardware

<img width="1543" height="803" alt="image" src="https://github.com/user-attachments/assets/e5853433-b947-4fa2-820d-d2fb01fcb56f" />

## Data visualisation

### Web interface 

<img width="1028" height="783" alt="image" src="https://github.com/user-attachments/assets/b2c7bc54-ce5f-44ac-90db-f4be6364fedb" />

### Mosquitto preview

```bash
mosquitto_sub -h 192.168.1.48 -p 1883 -t weather/sensors -C 1| python -m json.tool
```

```json
{
  "sensor_bme280_temperature_c": 21.23,
  "wind_dir_cardinal": "W",
  "sensor_bme680_gas_kohms": 553.17,
  "sensor_dht22_temperature_c": 20.6,
  "sensor_bme680_temperature_c": 20.11,
  "sensor_dht22_humidity_pct": 59.3,
  "sensor_bme680_humidity_pct": 59.54,
  "sensor_aht20_humidity_pct": 64.15,
  "pressure_hpa": 978.34,
  "temperature_c": 20.11,
  "gas_kohms": 553.17,
  "wind_dir_raw": 7905,
  "sensor_bme680_pressure_hpa": 978.34,
  "humidity_pct": 59.54,
  "rain_mm": 0.0,
  "timestamp": 1771428856,
  "rain_tips": 0,
  "wind_dir_deg": 270.0,
  "wind_speed_kmh": 0.0,
  "wind_pulses": 0,
  "sensor_bme280_pressure_hpa": 978.78,
  "rain_mm_total": 0.0,
  "sensor_aht20_temperature_c": 20.77
}

## Technical appendix

### Resetting Flash memory

For Pico-series devices, BOOTSEL mode lives in read-only memory inside the RP2040 or RP2350 chip, and can’t be overwritten accidentally. No matter what, if you hold down the BOOTSEL button when you plug in your Pico, it will appear as a drive onto which you can drag a new UF2 file. There is no way to brick the board through software. However, there are some circumstances where you might want to make sure your flash memory is empty. You can do this by dragging and dropping a special UF2 flash_nuke.uf2 binary onto your Pico when it is in mass storage mode.

### Download the UF2 files:

https://micropython.org/download/RPI_PICO2_W/
https://datasheets.raspberrypi.com/soft/flash_nuke.uf2

### RTC module DS3231

<img width="320" height="245" alt="image" src="https://github.com/user-attachments/assets/e578ffde-41ab-4811-afb2-333b8daddb3b" />

The RTC module has a potential problem. The module is designed to be used with a rechargeable lithium battery via a very simple charging circuit (a diode and a resistor powered by 5 V). If you are using a CR2032 battery, simply desolder the diode to prevent the battery from charging, which could damage or even cause it to explode.
