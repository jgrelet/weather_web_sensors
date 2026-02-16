import network
import ntptime
from machine import RTC
import utime
from config import ssid, password

# Connexion au réseau Wi-Fi
#ssid = 'votre_ssid'
#password = 'votre_mot_de_passe'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Attendre la connexion au Wi-Fi
while not wlan.isconnected():
    utime.sleep(1)

print("Connecté au réseau Wi-Fi")

# Synchroniser l'heure avec un serveur NTP
ntptime.settime()

# Créer une instance de l'horloge RTC
rtc = RTC()

# Vérifier et afficher la date et l'heure définies
print("Heure RTC synchronisée avec NTP:", rtc.datetime())

# Boucle pour afficher l'heure chaque seconde
while True:
    print("Heure actuelle:", rtc.datetime())
    utime.sleep(1)