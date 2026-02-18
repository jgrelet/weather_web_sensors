# Weather Web Sensors - Raspberry Pi Pico 2W

Station meteo MicroPython avec visualisation web locale et comparaison multi-capteurs.

## Materiel

- Raspberry Pi Pico 2W
- BME680 (temperature, humidite, pression, gaz)
- BME280/BMP280 (temperature, pression)
- AHT20 (temperature, humidite)
- DHT22 (temperature, humidite)
- RTC DS3231 (+ EEPROM AT24C32)
- OLED SSD1306
- Anemometre + girouette + pluviometre

## Cartographie I2C et GPIO

### Bus I2C1 (principal)

- SDA: `GP2`, SCL: `GP3`, `id=1`
- `0x3C`: SSD1306
- `0x68`: DS3231 (RTC)
- `0x57`: AT24C32 (EEPROM du module RTC)
- `0x77`: BME680

### Bus I2C0 (auxiliaire)

- SDA: `GP4`, SCL: `GP5`, `id=0`
- `0x38`: AHT20
- `0x77`: BME280/BMP280

### GPIO direct

- `GP13`: DHT22

## Configuration

Les parametres capteurs/bus sont dans `config.py` (dict `SENSORS`).

### Wi-Fi sans exposer les credentials

`config_wifi.py` charge `wifi_secrets.py` si present.

1. Copier `wifi_secrets.example.py` en `wifi_secrets.py`
2. Renseigner:

```python
ssid = "YOUR_WIFI_SSID"
password = "YOUR_WIFI_PASSWORD"
```

`wifi_secrets.py` est ignore par Git.

## NTP et RTC DS3231

Politique de synchro dans `config.py` -> `APP`:

- `ntp_sync_mode = "never" | "always" | "auto" | "pin"`
- `ntp_min_year` pour le mode `auto`
- `ntp_trigger_pin`, `ntp_trigger_active_high`, `ntp_trigger_pull` pour le mode `pin`

Comportement:

- Au boot, l'heure est lue depuis le DS3231.
- Si une synchro NTP est executee, l'heure est aussi reecrite dans le DS3231.

## Web UI

- Cartes resume (meteo + vent + pluie)
- Tableau de comparaison par capteur avec deltas (`Delta T/H/P`)
- Endpoint manuel NTP: `GET /sync-ntp`
- Bouton dans l'UI: "Synchroniser NTP maintenant"

## Lancement

1. Flasher MicroPython sur Pico 2W
2. Deployer le projet
3. Executer `main.py`
4. Ouvrir l'IP affichee dans le navigateur (ex: `http://192.168.1.54`)

