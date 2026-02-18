# Weather Web Sensors - Raspberry Pi Pico 2W

Station meteo MicroPython avec visualisation web locale et comparaison multi-capteurs.
This project is based from IoT Starters blog [Connecting BMP280 sensor with Raspberry Pi Pico W](https://iotstarters.com/connecting-bmp280-sensor-with-raspberry-pi-pico-w/)

## Materiel

- [Raspberry Pico 2W](https://www.raspberrypi.com/products/raspberry-pi-pico-2/)
- BME680 (temperature, humidity, pressure, gas)
- [DTH22](https://fr.aliexpress.com/item/32759901711.html?spm=a2g0o.order_list.order_list_main.61.1ab05e5bBsdUCw&gatewayAdapt=glo2fra): Temperature and humidity
- [AHT20 + BMP280](https://fr.aliexpress.com/item/1005008139283157.html?spm=a2g0o.order_list.order_list_main.66.1ab05e5bBsdUCw&gatewayAdapt=glo2fra): Temperature and atmospheric pressure
- [OLED display SSD1306](https://fr.aliexpress.com/item/1005007706726114.html?spm=a2g0o.order_list.order_list_main.17.11c35e5bhBt9Yk&gatewayAdapt=glo2fra)
- Wind sensor + raingage
- Breadboard and [jumper wires](https://fr.aliexpress.com/item/1005007430055417.html?spm=a2g0o.order_list.order_list_main.16.11c35e5bhBt9Yk&gatewayAdapt=glo2fra)
- [Thonny](https://thonny.org/) IDE or Visual Studio Code (VSC) with [MicroPico](https://github.com/paulober/MicroPico) extension
- [Micropython](https://micropython.org/download/RPI_PICO2_W/)

## Cartographie I2C et GPIO

### Diagram

![image](https://github.com/user-attachments/assets/89be49a1-b381-4cd1-b109-21f744a02b64)

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

## Visualisation des exports (UDP et MQTT)

### UDP (payload JSON direct)

Configuration Pico (`config.py` -> `EXPORTS["udp"]`):

```python
"udp": {
    "enabled": True,
    "host": "192.168.1.48",  # IP du PC qui recoit
    "port": 9999,
}
```

Reception sur le PC:

```bash
python tools/udp_receiver.py --host 0.0.0.0 --port 9999
```

Note:
- L'export est emis a chaque lecture capteurs (dans cette app, lors d'une requete HTTP sur l'UI web).

### MQTT (publication via broker)

Installation rapide de Mosquitto sous Windows (Scoop):

```bash
scoop install mosquitto
```

Demarrer le broker en ecoute reseau (pas en mode local-only):

1. Creer `mosquitto.conf` (encodage sans BOM, idealement ASCII) avec:

```conf
listener 1883 0.0.0.0
allow_anonymous true
```

2. Lancer Mosquitto avec ce fichier:

```bash
mosquitto -c .\mosquitto.conf -v
```

3. Verifier l'abonnement depuis le PC:

```bash
mosquitto_sub -h 192.168.1.48 -p 1883 -t weather/sensors -v
```

Si Mosquitto affiche `Starting in local only mode`, c'est que le broker n'a pas ete lance avec un listener reseau.

Configuration Pico (`config.py` -> `EXPORTS["mqtt"]`):

```python
"mqtt": {
    "enabled": True,
    "broker": "192.168.1.48",  # IP du broker MQTT (ex: Mosquitto)
    "port": 1883,
    "topic": "weather/sensors",
    ...
}
```

Visualisation sur le PC (abonnement):

```bash
mosquitto_sub -h 192.168.1.48 -p 1883 -t weather/sensors -v
```

Validation rapide (memo):

```bash
# 1) Voir topic + payload JSON publie
mosquitto_sub -h 192.168.1.48 -p 1883 -t weather/sensors -v

# 2) Voir les echanges MQTT cote client (CONNECT/SUBSCRIBE/PUBLISH)
mosquitto_sub -d -h 192.168.1.48 -p 1883 -t weather/sensors -v

# 3) Valider que le payload est un JSON decode correctement
mosquitto_sub -h 192.168.1.48 -p 1883 -t weather/sensors | python -m json.tool
```

Analyse reseau (optionnel, Wireshark):
- Filtre d'affichage: `tcp.port == 1883` (ou `mqtt`)
- Permet de voir les trames `CONNECT`, `CONNACK`, `PUBLISH`, etc.

Pourquoi des ports differents:
- MQTT utilise en general TCP/1883 (ou 8883 en TLS) via un broker.
- UDP est un transport distinct, ici en UDP/9999 vers un receiver local.

Depannage rapide:
- Erreur `connexion refusee` sur `192.168.1.48:1883`: broker non demarre, listener reseau absent, ou pare-feu Windows bloque TCP 1883.
- Erreur `Unknown configuration variable '...listener'`: fichier `mosquitto.conf` en UTF-8 avec BOM. Reenregistrer sans BOM (ASCII ou UTF-8 sans BOM).

## Port serie et vitesse (baudrate)

Le `SerialExporter` de ce projet ecrit avec `print()` sur la sortie serie USB (CDC/REPL).
Il n'y a donc pas de `baudrate` dans `config.py` pour cet export: la vitesse n'est pas geree ici comme un UART TTL classique.

Le script `tools/serial_receiver.py` (option `--baudrate`) concerne une lecture serie cote PC quand on passe par un port serie configure par le systeme/hardware.

