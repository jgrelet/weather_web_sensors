# Weather Web Sensors - Raspberry Pi Pico 2W

MicroPython weather station with a local web dashboard and multi-sensor comparison.
This project is based on the IoT Starters blog post [Connecting BMP280 sensor with Raspberry Pi Pico W](https://iotstarters.com/connecting-bmp280-sensor-with-raspberry-pi-pico-w/).

## Hardware

- [Raspberry Pi Pico 2W](https://www.raspberrypi.com/products/raspberry-pi-pico-2/)
- [BME680](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf) (temperature, humidity, pressure, gas)
- [DHT22](https://fr.aliexpress.com/item/32759901711.html?spm=a2g0o.order_list.order_list_main.61.1ab05e5bBsdUCw&gatewayAdapt=glo2fra): temperature and humidity
- [AHT20 + BMP280](https://fr.aliexpress.com/item/1005008139283157.html?spm=a2g0o.order_list.order_list_main.66.1ab05e5bBsdUCw&gatewayAdapt=glo2fra): temperature and atmospheric pressure
- [OLED SSD1306 display](https://fr.aliexpress.com/item/1005007706726114.html?spm=a2g0o.order_list.order_list_main.17.11c35e5bhBt9Yk&gatewayAdapt=glo2fra)
- Wind-speed sensor, wind vane and rain gauge
- [HC-12](https://www.datasheethub.com/hc12-si4463-433mhz-wireless-rf-serial-port-module/) 433 MHz serial radio module
- [AM312](https://www.alldatasheet.com/html-pdf/1179499/ETC2/AM312/109/1/AM312.html) PIR presence sensor for OLED power control
- [DS3231](https://www.analog.com/media/en/technical-documentation/data-sheets/ds3231.pdf) (RTC module)
- Breadboard and [jumper wires](https://fr.aliexpress.com/item/1005007430055417.html?spm=a2g0o.order_list.order_list_main.16.11c35e5bhBt9Yk&gatewayAdapt=glo2fra)
- [Visual Studio Code](https://code.visualstudio.com/) with [Remote SSH](https://code.visualstudio.com/docs/remote/ssh) and [MicroPico](https://github.com/paulober/MicroPico) extensions
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

- `GP13` (physical pin 17): DHT22 data
- `GP14` (physical pin 19): wind-speed pulse input
- `GP15` (physical pin 20): rain-gauge pulse input
- `GP26/ADC0` (physical pin 31): analog wind-direction input
- `GP27/ADC1` (physical pin 32): AM312 `OUT`, read with a 2.4 V ADC threshold

AM312 power wiring:

- Pico `3V3(OUT)` (physical pin 36) -> AM312 `VCC`
- Pico `GND` -> AM312 `GND`

### UART0 / HC-12 radio

- Pico `GP0` / UART0 TX (physical pin 1) -> HC-12 `RXD`
- Pico `GP1` / UART0 RX (physical pin 2) <- HC-12 `TXD`
- Pico `3V3(OUT)` (physical pin 36) -> HC-12 `VCC`, or use a stable external 3.3 V supply
- Pico `GND` -> HC-12 `GND`; an external supply must share the same ground
- HC-12 `SET` remains unconnected in normal transparent mode

The AM312 was moved from digital `GP16` to ADC `GP27` because the RP2350-E9
high-impedance input behaviour prevented a reliable digital LOW with this module.

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

- `timezone` for local display/web rendering
  - `name` display label such as `Europe/Paris`
  - `standard_offset_minutes` / `dst_offset_minutes`
  - `dst_rule = "eu" | "none"`
  - `standard_abbrev` / `dst_abbrev`
- `ntp_sync_mode = "never" | "always" | "auto" | "pin"`
- `ntp_min_year` for `auto` mode
- `ntp_trigger_pin`, `ntp_trigger_active_high`, `ntp_trigger_pull` for `pin` mode

Behavior:

- At boot, time is loaded from the DS3231.
- If NTP sync is performed, time is written back to the DS3231.

### Time strategy for HC-12 deployment

The weather node does not require garden Wi-Fi during normal HC-12 operation. At
every boot it loads the battery-backed DS3231 into the Pico RTC, then timestamps
radio payloads from that clock.

Before moving the node to its final location:

1. run it within Wi-Fi range with `TRANSPORT_MODE = "wifi"` and
   `ntp_sync_mode = "always"`;
2. confirm `NTP sync OK`, which also writes the corrected time to the DS3231;
3. restore `TRANSPORT_MODE = "hc-12"` and `ntp_sync_mode = "auto"`, upload the
   configuration and confirm `RTC valid: True` after restart;
4. install a healthy DS3231 backup battery before placing the node in the garden.

In `auto` mode, a plausible year is considered valid; this detects a lost clock but
does not correct normal RTC drift. Periodically repeat the Wi-Fi maintenance sync
until time synchronization from the Raspberry Pi over the bidirectional HC-12 link
is implemented. If the DS3231 becomes invalid while HC-12 mode has disabled Wi-Fi,
the current firmware reports that NTP was skipped and cannot correct the clock by
itself.

## Web UI

- Summary cards (weather + wind + rain)
- Sensor comparison table with deltas (`Delta T/H/P`)
- Manual NTP endpoint: `GET /sync-ntp`
- UI button: "Sync NTP now"
- The browser displays the latest measurement cached on the Pico; it no longer triggers acquisition.

## Run

1. Flash MicroPython on Pico 2W
2. Deploy the project
3. Run `main.py`
4. Open the displayed IP in a browser (example: `http://192.168.1.58`)

## Acquisition Mode

- Acquisition now starts directly on the Pico at boot.
- The default acquisition period follows `APP["web_refresh_seconds"]`.
- You can override it with `APP["acquisition_interval_seconds"]` in `config.py`.
- The remote browser is now optional and only displays the latest cached data.

## Transport Mode

`config.py` exposes `TRANSPORT_MODE`, which selects the production transmission path:

```python
TRANSPORT_MODE = "wifi"  # "wifi" or "hc-12"
```

- `wifi`: publish through Wi-Fi/MQTT using `EXPORTS["mqtt"]`.
- `hc-12`: publish through UART0 to an HC-12 module using `EXPORTS["hc12"]`.

Long JSON lines are written in paced chunks. `EXPORTS["hc12"]["chunk_size"]`
defaults to 64 bytes and `chunk_delay_ms` to 75 ms so the HC-12 radio buffer is not
overrun by a continuous 9600-baud UART write. Keep the final newline: the Raspberry
Pi bridge uses it to detect a complete payload.

Keep this value aligned with `RPI3_METEO_TRANSMISSION_MODE` in the Raspberry Pi
`rpi3-meteo` project. The Raspberry Pi application still consumes Mosquitto;
in HC-12 mode the Pi bridges UART lines back into MQTT.

HC-12 wiring for Pico2-W:

- Pico `GP0` / UART0 TX, physical pin `1` -> HC-12 `RXD`
- Pico `GP1` / UART0 RX, physical pin `2` <- HC-12 `TXD`
- Pico `GND`, for example physical pin `3` or `38` -> HC-12 `GND`
- HC-12 `VCC` -> stable `3V3(OUT)` or external 3.3V with common ground
- HC-12 `SET` can stay unconnected for transparent mode

Before enabling app integration, run `tools/hc12_pico_test.py` on the Pico and `tools/hc12_rpi_test.py` on the Raspberry Pi to validate send, receive, and echo in both directions.

### HC-12 bidirectional test

1. On the Pico, run the test script in MicroPython:

```python
import tools.hc12_pico_test as test
# or run the script after copying it to the Pico filesystem
```

2. On the Raspberry Pi, run the new helper script:

```bash
python3 tools/hc12_rpi_test.py --port /dev/serial0 --baudrate 9600
```

3. Expected behavior:
- The Pico sends `PING_PICO` every 2 seconds.
- The Raspberry Pi sends `PING_RPI` every 2 seconds.
- Each side replies with `ACK_PICO` or `ACK_RPI` to incoming ping lines.
- Both sides should print received and sent messages.

4. Verify wiring:
- Pico `GP0` -> HC-12 `RXD`
- Pico `GP1` <- HC-12 `TXD`
- Shared ground between Pico and HC-12.

5. If you only want to verify receive/transmit once, watch the `received:` lines on both sides.

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
- Export is sent on each autonomous acquisition cycle.
- Export payloads keep `timestamp` as Unix epoch.
- Local timezone rendering is now only used on the Pico display and web UI.

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

2. Start Mosquitto 'broker' with this config under msdos:

```dos
mosquitto -c .\mosquitto.conf -v
```

or under bash

```bash
mosquitto -c ./mosquitto.conf -v
```

3. Verify subscription from the PC:

```bash
mosquitto_sub -h 192.168.1.52 -p 1883 -t weather/sensors -v
```

If Mosquitto shows `Starting in local only mode`, the broker was not started with a network listener.

Pico configuration (`config.py` -> `EXPORTS["mqtt"]`):

```python
"mqtt": {
    "enabled": True,
    "broker": "192.168.1.52",  # MQTT broker IP (for example Mosquitto)
    "port": 1883,
    "topic": "weather/sensors",
    ...
}
```

PC visualization (subscriber):

```bash
mosquitto_sub -h <PC IP> -p 1883 -t weather/sensors -v
mosquitto_sub -h 192.168.1.52 -p 1883 -t weather/sensors -v
```

Quick validation memo:

```bash
# 1) Show topic + JSON payload
mosquitto_sub -h 192.168.1.52 -p 1883 -t weather/sensors -v

# 2) Show MQTT client debug exchanges (CONNECT/SUBSCRIBE/PUBLISH)
mosquitto_sub -d -h 192.168.1.52 -p 1883 -t weather/sensors -v

# 3) Validate one JSON payload decoding
mosquitto_sub -h 192.168.1.52 -p 1883 -t weather/sensors -C 1| python -m json.tool

# 4) Validate all JSON payload decoding (use with Powershell)
mosquitto_sub -h 192.168.1.52 -p 1883 -t weather/sensors |
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
- `connection refused` on `192.168.1.52:1883`: broker not started, missing network listener, or Windows firewall blocking TCP 1883
- `Unknown configuration variable '...listener'`: `mosquitto.conf` saved with UTF-8 BOM. Save without BOM (ASCII or UTF-8 without BOM)

Timestamp fields in exported JSON:
- `timestamp`: Unix epoch, preserved for machine processing and compatibility

## Serial Port and Baud Rate

`SerialExporter` in this project writes through `print()` to USB serial output (CDC/REPL).
There is no `baudrate` setting in `config.py` for this exporter, unlike a classic TTL UART setup.

`tools/serial_receiver.py` (`--baudrate`) applies to PC-side serial reading when using a system/hardware serial port.

## Hardware

<img width="1543" height="803" alt="image" src="https://github.com/user-attachments/assets/e5853433-b947-4fa2-820d-d2fb01fcb56f" />

First version of the prototype on a breadboard

<img width="3923" height="2326" alt="20260716_171411" src="https://github.com/user-attachments/assets/26634663-5037-4245-a06f-dfd89a5126ef" />

Second version of the prototype with radio transmission and IR presence detection on a breadboard

## Data visualisation

### Web interface 

<img width="1028" height="783" alt="image" src="https://github.com/user-attachments/assets/b2c7bc54-ce5f-44ac-90db-f4be6364fedb" />

### Mosquitto preview

```bash
mosquitto_sub -h 192.168.1.52 -p 1883 -t weather/sensors -C 1| python -m json.tool
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
```

## Technical appendix

### Remote configuration over HC-12

When `TRANSPORT_MODE = "hc-12"`, the Raspberry Pi can send newline-delimited
`CMD` JSON control messages. The Pico returns matching `ACK` JSON responses without
stopping weather exports. Supported operations are status retrieval, RTC and DS3231
time update, persistent Test/Production timing-profile selection, and temporary
Wi-Fi diagnostic access.

Temporary Wi-Fi does not replace HC-12 as the weather transport. Connection runs
without blocking sensor acquisition, the Pico HTTP server starts after an IP address
is assigned, and the session stops automatically after 15 minutes. The Raspberry Pi
kiosk displays the assigned IP and can stop the session early.

### Presence-controlled OLED display

For autonomous operation, an AM312 PIR sensor can keep the SSD1306 OLED powered off
when nobody is near the station. The default wiring is:

- AM312 `VCC` to Pico `3V3(OUT)`;
- AM312 `GND` to Pico `GND`;
- AM312 `OUT` to ADC input `GP27` (physical pin 32).

The settings are under `SENSORS["display"]["presence_sensor"]` in `config.py`.
With presence control enabled, sensor acquisition and HC-12 export continue while
the OLED is off. A rising PIR signal turns the display on with the latest reading;
continued motion extends the configured 20-second visibility period. The GPIO
is sampled as an ADC input with a configurable 2.4 V threshold. This avoids the
RP2350-E9 high-impedance digital-input erratum observed with this AM312 on GP16,
while OLED I2C operations remain in the main loop.
Check the `VCC`, `OUT` and `GND` markings on the actual module before applying power,
because physical pin order can vary between AM312 boards.

HC-12 transmission can couple into the AM312 supply or signal and produce a false
PIR pulse. The runtime masks presence immediately before each radio transmission and
rearms it only after the ADC input has returned LOW. For the final installation,
also keep PIR wiring away from the HC-12 antenna and add local supply decoupling near
both modules; software filtering does not replace good power and RF layout.

`SENSORS["display"]["boot_message_seconds"]` controls how long each OLED startup
message remains visible. The default is two seconds.

For autonomous startup, keep both `micropico.openOnStart` and
`micropico.autoConnect` disabled in the local VS Code workspace. An automatic REPL
connection can interrupt the already-running `main.py`. Fatal startup errors are
printed to USB serial and trigger an automatic board reset after ten seconds.

### Resetting Flash memory

For Pico-series devices, BOOTSEL mode lives in read-only memory inside the RP2040 or RP2350 chip, and can’t be overwritten accidentally. No matter what, if you hold down the BOOTSEL button when you plug in your Pico, it will appear as a drive onto which you can drag a new UF2 file. There is no way to brick the board through software. However, there are some circumstances where you might want to make sure your flash memory is empty. You can do this by dragging and dropping a special UF2 flash_nuke.uf2 binary onto your Pico when it is in mass storage mode.

### Download the UF2 files:

https://micropython.org/download/RPI_PICO2_W/
https://datasheets.raspberrypi.com/soft/flash_nuke.uf2

### RTC module DS3231

<img width="320" height="245" alt="image" src="https://github.com/user-attachments/assets/e578ffde-41ab-4811-afb2-333b8daddb3b" />

The RTC module has a potential problem. The module is designed to be used with a rechargeable lithium battery via a very simple charging circuit (a diode and a resistor powered by 5 V). If you are using a CR2032 battery, simply desolder the diode to prevent the battery from charging, which could damage or even cause it to explode.

## MicroPython over SSH (Raspberry Pi)

If you develop remotely on a Raspberry Pi (for example a RPi4 running the companion `rpi3-meteo` service), the recommended workflow is to keep your SSH private key protected by a passphrase and use an SSH agent to cache the unlocked key during your session. This avoids repeatedly entering the passphrase while preserving good security.

Recommended steps (Option B - keep passphrase and cache it):

- Start the agent and add your key (enter the passphrase once per session):

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

- Make SSH automatically add keys to the agent by adding to `~/.ssh/config` (create if missing):

```text
Host *
  AddKeysToAgent yes
  IdentityFile ~/.ssh/id_ed25519
```

- Persist the unlocked key across logins on Debian/Ubuntu using `keychain` (optional):

```bash
sudo apt install keychain
# add to ~/.profile or ~/.bash_profile:
eval "$(keychain --eval --agents ssh id_ed25519)"
```

- VS Code Remote SSH tips:
  - Ensure VS Code forwards the local SSH agent: enable `remote.SSH.enableAgentForwarding` in settings when connecting through a jump host.
  - Start `ssh-agent` and `ssh-add` on the machine where you run VS Code (your workstation) so the key is available to the Remote-SSH extension.

Note about security:
- Do not remove the passphrase from your private key unless you fully understand the security consequences. Removing it permanently makes the key usable by anyone who can access the file.

Local memo (non-versioned):
- For convenience you can keep an operational memo on the Pi at `rpi3-meteo/docs/memo-ssh.md`. This file contains step-by-step commands and reminders and is intended to remain untracked for security reasons. See the repository `.gitignore` for the ignored path.
