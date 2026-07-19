# Transports et export des mesures

## Sélection du transport

`TRANSPORT_MODE` dans `config.py` choisit le chemin de production :

```python
TRANSPORT_MODE = "wifi"  # "wifi" ou "hc-12"
```

- `wifi` publie via les sorties configurées dans `EXPORTS`, notamment MQTT et UDP ;
- `hc-12` envoie les mesures par UART0 vers la passerelle Raspberry Pi, qui les republie dans MQTT.

Aligner ce réglage avec `RPI3_METEO_TRANSMISSION_MODE` dans le projet compagnon `rpi3-meteo`.

## HC-12

Les lignes JSON sont terminées par un saut de ligne, utilisé par la passerelle pour détecter un message complet. Pour éviter de saturer le tampon radio à 9 600 bauds, elles sont écrites par fragments. Les valeurs par défaut sont `chunk_size = 64` octets et `chunk_delay_ms = 75` ms dans `EXPORTS["hc12"]`.

### Test bidirectionnel

1. Copier et lancer `tools/hc12_pico_test.py` sur le Pico.
2. Sur le Raspberry Pi :

```bash
python3 tools/hc12_rpi_test.py --port /dev/serial0 --baudrate 9600
```

Le Pico et le Pi envoient respectivement `PING_PICO` et `PING_RPI` toutes les deux secondes, puis répondent par `ACK_PICO` ou `ACK_RPI`. Contrôler les lignes `received:` des deux côtés.

### Commandes distantes

En mode HC-12, le Raspberry Pi peut envoyer des commandes JSON `CMD`, délimitées par des sauts de ligne. Le Pico retourne un `ACK` correspondant sans interrompre les relevés. Les opérations couvrent l'état, la mise à l'heure du RTC/DS3231, les profils persistants Test/Production et un accès Wi-Fi diagnostique temporaire.

Le Wi-Fi temporaire ne remplace pas HC-12 pour les mesures. La connexion est non bloquante, le serveur HTTP démarre après attribution de l'adresse IP et la session s'arrête automatiquement après 15 minutes.

## MQTT

Exemple de configuration :

```python
"mqtt": {
    "enabled": True,
    "broker": "192.168.1.52",
    "port": 1883,
    "topic": "weather/sensors",
}
```

Le broker Mosquitto doit écouter le réseau, par exemple avec :

```conf
listener 1883 0.0.0.0
allow_anonymous true
```

Puis lancer `mosquitto -c ./mosquitto.conf -v` et vérifier un message :

```bash
mosquitto_sub -h 192.168.1.52 -p 1883 -t weather/sensors -C 1 | python -m json.tool
```

## UDP

Exemple dans `EXPORTS["udp"]` :

```python
"udp": {
    "enabled": True,
    "host": "192.168.1.48",
    "port": 9999,
}
```

Réception sur le poste cible :

```bash
python tools/udp_receiver.py --host 0.0.0.0 --port 9999
```

Un message est exporté à chaque cycle d'acquisition. Le champ `timestamp` reste un epoch Unix pour le traitement machine ; le fuseau local n'est appliqué qu'à l'OLED et à l'interface web.

## Sortie série

`SerialExporter` écrit avec `print()` sur la sortie USB CDC/REPL : aucun débit n'est configuré dans `config.py`. L'option `--baudrate` de `tools/serial_receiver.py` concerne uniquement la lecture d'un port série par le poste récepteur.
