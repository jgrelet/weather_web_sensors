# Exploitation et dépannage

## Démarrage autonome

Désactiver `micropico.openOnStart` et `micropico.autoConnect` dans l'espace de travail VS Code. Une connexion automatique au REPL peut interrompre un `main.py` déjà lancé. Les erreurs fatales de démarrage sont affichées sur le port USB série et déclenchent un redémarrage après dix secondes.

## Diagnostic MQTT

- `connection refused` sur le port 1883 : broker arrêté, listener réseau absent ou pare-feu bloquant ;
- `Starting in local only mode` : Mosquitto n'a pas chargé de listener réseau ;
- `Unknown configuration variable` au début du fichier : enregistrer `mosquitto.conf` sans BOM ;
- filtre Wireshark utile : `tcp.port == 1883` ou `mqtt`.

Afficher les échanges du client :

```bash
mosquitto_sub -d -h 192.168.1.52 -p 1883 -t weather/sensors -v
```

MQTT utilise généralement TCP/1883, ou 8883 avec TLS. L'export UDP sur 9999 est un transport indépendant et direct.

## Remise à zéro de la mémoire flash

Le mode BOOTSEL réside dans la ROM du RP2040/RP2350 et ne peut pas être écrasé par le firmware. En maintenant BOOTSEL pendant le branchement, le Pico apparaît comme un volume USB. Pour effacer complètement la flash, déposer le fichier officiel `flash_nuke.uf2`, puis réinstaller MicroPython.

- [MicroPython pour Raspberry Pi Pico 2 W](https://micropython.org/download/RPI_PICO2_W/)
- [flash_nuke.uf2](https://datasheets.raspberrypi.com/soft/flash_nuke.uf2)

## Développement distant par SSH

Conserver une phrase de passe sur la clé privée et utiliser un agent SSH :

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Configuration possible dans `~/.ssh/config` :

```text
Host *
  AddKeysToAgent yes
  IdentityFile ~/.ssh/id_ed25519
```

Sur Debian/Ubuntu, `keychain` peut restaurer l'agent entre les connexions. Pour VS Code Remote SSH, activer le transfert de l'agent si une machine intermédiaire est utilisée. Ne retirer la phrase de passe d'une clé privée qu'en connaissance du risque associé.
