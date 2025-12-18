# Occupancy Sensor

## Identifiant
- **Code** : OCC_SENSOR
- **Haystack** : occupancy, sensor, motion
- **Brick** : brick:Occupancy_Sensor, brick:Motion_Sensor

## Description
Capteur intelligent détectant la présence ou l'absence de personnes dans un espace. Utilise des technologies infrarouges passives (PIR), ultrasoniques, ou combinées pour identifier les mouvements et l'occupation. Ces capteurs sont essentiels pour l'optimisation énergétique des systèmes d'éclairage.

## Fonction
Détecter automatiquement la présence humaine dans une zone et transmettre cette information au système de contrôle d'éclairage pour allumer, éteindre ou ajuster l'intensité lumineuse. Permet des économies d'énergie importantes en évitant l'éclairage des espaces inoccupés.

## Variantes Courantes
- **PIR Occupancy Sensor** : Détection infrarouge passive des mouvements
- **Ultrasonic Occupancy Sensor** : Détection par ondes ultrasoniques, plus sensible aux petits mouvements
- **Dual-Technology Sensor** : Combine PIR et ultrasonique pour réduire les faux positifs
- **Ceiling-Mounted Sensor** : Montage plafond, couverture 360 degrés
- **Wall-Mounted Sensor** : Montage mural, couverture directionnelle
- **Corner-Mounted Sensor** : Montage en angle pour couverture optimale
- **High-Bay Sensor** : Pour espaces à hauts plafonds (entrepôts, gymnases)
- **Wireless Occupancy Sensor** : Communication sans fil (Zigbee, Bluetooth, EnOcean)
- **Multi-Level Sensor** : Détection fine/moyenne/grossière de l'occupation

## Caractéristiques Techniques Typiques
- Technologie de détection: PIR, Ultrasonic, ou Dual-Technology
- Zone de couverture: 100 à 2,000 sq.ft selon modèle
- Portée de détection: 5 à 30 mètres
- Angle de détection: 90° à 360°
- Sensibilité ajustable: 10-100%
- Délai avant extinction (timeout): 30 secondes à 30 minutes (configurable)
- Seuil de luminosité: 10 à 2,000 lux (optionnel)
- Alimentation: 24V DC, PoE, ou batterie (wireless)
- Communication: DALI, BACnet, KNX, Modbus, Zigbee, Bluetooth Mesh, EnOcean
- Sortie: Relais, 0-10V, signal digital
- Montage: Plafond, mural, encastré

## Localisation Typique
- Bureaux individuels et open-space
- Salles de réunion
- Toilettes et vestiaires
- Couloirs et cages d'escalier
- Salles de classe
- Entrepôts et zones de stockage
- Parkings intérieurs
- Espaces communs
- Salles de serveur
- Espaces techniques

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Lighting Panel, PoE Switch, Batterie
- **Contrôlé par** : Lighting Controller, Building Automation System
- **Contrôle** : LED Luminaire, Fluorescent Luminaire, Dimmer, Lighting Relay, HVAC System (intégration multi-domaine)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 50-200
- Moyen (15 étages) : 200-800
- Grand (30+ étages) : 1,000-5,000

## Sources
- Haystack Project - Occupancy sensor definitions
- Brick Schema - Occupancy Sensor class
- ASHRAE 90.1 - Energy standard for buildings (occupancy sensing requirements)
- California Title 24 - Lighting control requirements
- IEC 62386-303 - DALI Part 303: Occupancy sensor control interface
