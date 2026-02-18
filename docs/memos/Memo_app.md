# App Memo - Recent Changes

## 1) Boot/debug stability

- `main.py` no longer forces a reset loop after an exception.
- Fatal errors remain visible on the serial port (easier debugging).

## 2) Sensor and bus management

- Explicit separation of two I2C buses in `config.py`:
- `i2c` (I2C1): SSD1306, DS3231, BME680
- `i2c_aux` (I2C0): AHT20, BME280
- Added application sensors:
- `AHT20Sensor`
- `BME280Sensor`
- `DHT22Sensor`
- `BME680Sensor` publishes dedicated keys (`sensor_bme680_*`) for comparison.

## 3) Web UI

- Fixed `.format()` bug in CSS (escaped braces).
- Added "Sensor comparison" table (Temp/Hum/Press).
- Added live deltas versus reference sensor (`Delta T/H/P`).

## 4) NTP/RTC

- Read DS3231 at boot to initialize system clock.
- Configurable NTP sync policy:
- `never`, `always`, `auto`, `pin`
- On NTP sync, time is written back to DS3231.
- Manual web endpoint: `/sync-ntp` + UI button.

## 5) Configuration and security

- `config_wifi.py` reads `wifi_secrets.py` when present.
- `wifi_secrets.py` added to `.gitignore`.
- `wifi_secrets.example.py` provided as template.

## 6) RTC config clarification

- Renamed `trc` -> `eeprom` for address `0x57` (AT24C32).
