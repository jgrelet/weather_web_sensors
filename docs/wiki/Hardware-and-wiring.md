# Matériel et câblage

## Vue des prototypes

![Version finale du prototype avec module radio HC-12 et détecteur de présence AM312](https://raw.githubusercontent.com/jgrelet/weather_web_sensors/main/docs/images/breadboard-prototype-final.jpg)

*Version finale avec transmission radio et détecteur de présence*

![Première version du prototype sur platine d'essais](https://raw.githubusercontent.com/jgrelet/weather_web_sensors/main/docs/images/breadboard-prototype.png)

*Première version du prototype*

![Plan de câblage du Raspberry Pi Pico 2 W](https://raw.githubusercontent.com/jgrelet/weather_web_sensors/main/docs/images/pico2-w-wiring.png)

## Bus I2C1 principal

- SDA : `GP2`, SCL : `GP3`, `id=1`
- `0x3C` : écran SSD1306
- `0x68` : horloge DS3231
- `0x57` : EEPROM AT24C32 du module RTC
- `0x77` : BME680

## Bus I2C0 auxiliaire

- SDA : `GP4`, SCL : `GP5`, `id=0`
- `0x38` : AHT20
- `0x77` : BME280/BMP280

## GPIO directs

- `GP13` (broche physique 17) : données DHT22
- `GP14` (broche 19) : impulsions de l'anémomètre
- `GP15` (broche 20) : impulsions du pluviomètre
- `GP26/ADC0` (broche 31) : direction analogique du vent
- `GP27/ADC1` (broche 32) : sortie du détecteur AM312

## Radio HC-12 sur UART0

- Pico `GP0/TX` (broche 1) vers HC-12 `RXD`
- Pico `GP1/RX` (broche 2) depuis HC-12 `TXD`
- HC-12 `VCC` sur une alimentation 3,3 V stable
- masse commune entre le Pico, le HC-12 et toute alimentation externe
- `SET` non connecté en mode transparent normal

## Détecteur de présence AM312

L'AM312 permet d'éteindre l'OLED lorsque personne ne se trouve devant la station, sans interrompre l'acquisition ni les exports.

- `VCC` vers `3V3(OUT)` ;
- `GND` vers la masse ;
- `OUT` vers `GP27/ADC1`.

Le signal est lu sur l'ADC avec un seuil configurable de 2,4 V. Ce choix contourne le comportement des entrées numériques à haute impédance lié à l'erratum RP2350-E9, observé avec ce module sur `GP16`.

La transmission HC-12 peut produire de faux déclenchements par couplage RF ou alimentation. Le firmware masque la présence pendant une émission, mais il faut aussi éloigner le câblage PIR de l'antenne et découpler localement l'alimentation des deux modules. Vérifier l'ordre réel des broches du module avant sa mise sous tension.

## Module RTC DS3231

Certains modules DS3231 possèdent un circuit de charge destiné à un accumulateur. Avec une pile CR2032 non rechargeable, retirer la diode de charge afin de ne pas tenter de recharger la pile.

![Module RTC DS3231](https://raw.githubusercontent.com/jgrelet/weather_web_sensors/main/docs/images/ds3231-module.png)
