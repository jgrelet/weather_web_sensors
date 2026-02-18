import network
import ntptime
from machine import RTC
import utime
from config_wifi import ssid, password

# Connexion au rÃ©seau Wi-Fi
#ssid = 'votre_ssid'
#password = 'votre_mot_de_passe'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Attendre la connexion au Wi-Fi
while not wlan.isconnected():
    utime.sleep(1)

print("ConnectÃ© au rÃ©seau Wi-Fi")

# Synchroniser l'heure avec un serveur NTP
ntptime.settime()

# CrÃ©er une instance de l'horloge RTC
rtc = RTC()

# VÃ©rifier et afficher la date et l'heure dÃ©finies
print("Heure RTC synchronisÃ©e avec NTP:", rtc.datetime())

# Boucle pour afficher l'heure chaque seconde
while True:
    print("Heure actuelle:", rtc.datetime())
    utime.sleep(1)
