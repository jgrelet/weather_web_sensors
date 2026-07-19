# Documentation technique

Cette documentation complète le README, volontairement centré sur la présentation du projet.

- [[Matériel et câblage|Hardware-and-wiring]]
- [[Configuration, horloge et acquisition|Configuration-and-time]]
- [[Transports et export des mesures|Transports-and-exports]]
- [[Exploitation et dépannage|Operations-and-troubleshooting]]

## Organisation du firmware

- `main.py` construit et lance l'application ;
- `app/runtime.py` orchestre l'acquisition et les services ;
- `app/display.py` pilote l'affichage OLED ;
- `app/web.py` expose le tableau de bord HTTP ;
- `app/exporters.py` implémente les sorties série, UDP, MQTT et HC-12 ;
- `app/stats_buffer.py` conserve la fenêtre de mesures et calcule les statistiques ;
- `sensors/` contient les adaptateurs propres à chaque capteur ;
- `lib/` contient les pilotes MicroPython tiers ;
- `tools/` rassemble les récepteurs et les tests de transmission.
