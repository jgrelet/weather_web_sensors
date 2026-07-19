# Configuration, horloge et acquisition

## Configuration générale

Les bus, les capteurs et leurs options se trouvent dans le dictionnaire `SENSORS` de `config.py`. Les paramètres de l'application se trouvent dans `APP` et ceux des sorties dans `EXPORTS`.

Les identifiants Wi-Fi ne doivent pas être versionnés. `config_wifi.py` charge `wifi_secrets.py` lorsqu'il existe :

```python
ssid = "YOUR_WIFI_SSID"
password = "YOUR_WIFI_PASSWORD"
```

`wifi_secrets.py` est ignoré par Git.

## Acquisition autonome

L'acquisition commence au démarrage du Pico. Sa période suit par défaut `APP["web_refresh_seconds"]` et peut être remplacée par `APP["acquisition_interval_seconds"]`. Le navigateur affiche la dernière mesure mise en cache et ne déclenche aucune lecture de capteur.

## Fuseau horaire, NTP et DS3231

Les options de `APP` comprennent :

- `timezone` : nom, décalages hiver/été, règle `eu` ou `none` et abréviations ;
- `ntp_sync_mode` : `never`, `always`, `auto` ou `pin` ;
- `ntp_min_year` : année minimale considérée comme plausible en mode `auto` ;
- `ntp_trigger_pin`, `ntp_trigger_active_high` et `ntp_trigger_pull` pour le mode `pin`.

Au démarrage, le Pico charge l'heure du DS3231 dans son horloge interne. Après une synchronisation NTP, il réécrit l'heure corrigée dans le DS3231. Une synchronisation manuelle est aussi disponible avec `GET /sync-ntp` ou le bouton **Sync NTP now**.

## Préparation d'un déploiement HC-12

Le nœud météo n'a pas besoin du Wi-Fi dans le jardin : les messages radio sont horodatés à partir du DS3231.

1. À portée du Wi-Fi, utiliser `TRANSPORT_MODE = "wifi"` et `ntp_sync_mode = "always"`.
2. Vérifier le message `NTP sync OK`, qui confirme aussi l'écriture du DS3231.
3. Restaurer `TRANSPORT_MODE = "hc-12"` et `ntp_sync_mode = "auto"`.
4. Redémarrer et vérifier `RTC valid: True`.
5. Installer une pile saine avant de placer la station dans le jardin.

Le mode `auto` détecte une horloge manifestement perdue, mais ne corrige pas sa dérive normale. Répéter périodiquement la synchronisation de maintenance. Sans Wi-Fi et avec un DS3231 invalide, le firmware peut signaler l'erreur mais ne peut pas corriger seul l'heure.

## Affichage OLED

`SENSORS["display"]["presence_sensor"]` configure le contrôle par présence. Un mouvement affiche la dernière mesure puis prolonge la durée d'affichage, de 20 secondes par défaut. `SENSORS["display"]["boot_message_seconds"]` règle la durée des messages de démarrage.
