# Parking Sensor (Ultrasonic)

## Identifiant
- **Code** : PARKING_SENSOR_US
- **Haystack** : N/A
- **Brick** : N/A

## Description
Capteur de détection de présence véhicule basé sur technologie ultrasonique. Installé au plafond au-dessus de chaque place, détecte l'occupation par émission/réception d'ondes ultrasonores. Communique l'état vers système de guidage.

## Fonction
Détection en temps réel de l'occupation des places de stationnement. Remonte l'information d'état (libre/occupé) vers système central pour guidage des conducteurs et comptage des disponibilités.

## Variantes Courantes
- **Capteur simple** : Détection présence uniquement (occupé/libre)
- **Capteur avancé** : Détection + durée stationnement + classification véhicule
- **Capteur multi-places** : Un capteur couvre 2-3 places adjacentes
- **Version LoRaWAN** : Transmission longue portée, faible consommation

## Caractéristiques Techniques Typiques
- Technologie : Ultrasons 40-48 kHz
- Portée détection : 0.3-4 mètres
- Hauteur installation : 2.5-4 mètres
- Précision : > 99%
- Alimentation : PoE, batterie lithium (3-5 ans), 12-24V DC
- Communication : RS485, Zigbee, LoRaWAN, WiFi, BLE
- Température opération : -40°C à +85°C
- Protection : IP65
- Temps réponse : < 1 seconde

## Localisation Typique
- Plafond parking souterrain (au-dessus de chaque place)
- Parking couvert extérieur
- Zones de stationnement réglementé
- Places handicapés, VIP, recharge EV

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Distribution électrique PoE ou batterie autonome
- **Contrôlé par** : Parking Guidance Controller
- **Interagit avec** : Overhead Parking Indicator (LED local), Parking Guidance Display, Parking Management Server

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 50 capteurs (1 par place)
- Moyen (parking 200 places) : 200 capteurs (1 par place)
- Grand (parking 1000+ places) : 1000+ capteurs (1 par place)

## Sources
- Standards ITS (Intelligent Transportation Systems)
- Documentation systèmes de guidage parking
- Protocoles IoT (LoRaWAN, Zigbee)
