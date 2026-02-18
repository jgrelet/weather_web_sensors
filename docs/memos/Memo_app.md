# Memo App - Evolutions recentes

## 1) Stabilite boot/debug

- `main.py` ne force plus un reset en boucle apres exception.
- Les erreurs fatales restent visibles sur le port serie (debug plus simple).

## 2) Gestion capteurs et bus

- Separation explicite de deux bus I2C dans `config.py`:
  - `i2c` (I2C1): SSD1306, DS3231, BME680
  - `i2c_aux` (I2C0): AHT20, BME280
- Ajout capteurs applicatifs:
  - `AHT20Sensor`
  - `BME280Sensor`
  - `DHT22Sensor`
- `BME680Sensor` publie des cles dediees (`sensor_bme680_*`) pour comparaison.

## 3) UI Web

- Correction du bug `.format()` dans CSS (accolades echappees).
- Ajout tableau "Comparaison capteurs" (Temp/Hum/Press).
- Ajout deltas instantanes vs capteur de reference (`Delta T/H/P`).

## 4) NTP/RTC

- Lecture DS3231 au boot pour initialiser l'horloge systeme.
- Politique de synchro NTP configurable:
  - `never`, `always`, `auto`, `pin`
- En cas de synchro NTP, ecriture retour vers DS3231.
- Endpoint manuel web: `/sync-ntp` + bouton dans l'interface.

## 5) Configuration et securite

- `config_wifi.py` lit `wifi_secrets.py` si present.
- `wifi_secrets.py` ajoute a `.gitignore`.
- `wifi_secrets.example.py` fourni comme modele.

## 6) Clarification config RTC

- Renommage `trc` -> `eeprom` pour l'adresse `0x57` (AT24C32).

