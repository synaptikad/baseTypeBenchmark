# Photocell (Light Sensor)

## Identifiant
- **Code** : PHOTOCELL
- **Haystack** : photocell, lightLevel, sensor, light
- **Brick** : brick:Photocell, brick:Illuminance_Sensor, brick:Light_Level_Sensor

## Description
Capteur mesurant l'intensité lumineuse ambiante (illuminance) dans un espace. Les photocellules convertissent la lumière en signal électrique proportionnel, permettant au système de contrôle d'ajuster automatiquement l'éclairage artificiel en fonction de la lumière naturelle disponible.

## Fonction
Mesurer en temps réel le niveau d'éclairement (en lux) d'une zone et transmettre cette information au système de contrôle pour optimiser l'éclairage artificiel. Essentiel pour les stratégies de daylight harvesting (exploitation de la lumière naturelle) et le respect des normes d'éclairement.

## Variantes Courantes
- **Indoor Photocell** : Mesure de la lumière intérieure (0-2,000 lux typique)
- **Outdoor Photocell** : Mesure de la lumière extérieure (0-100,000 lux)
- **Window-Mounted Photocell** : Positionnement près des fenêtres pour mesure de l'apport naturel
- **Ceiling-Mounted Photocell** : Mesure de l'éclairement global au plan de travail
- **Desk-Mounted Photocell** : Mesure locale au niveau du poste de travail
- **Wireless Photocell** : Sans fil pour installation flexible
- **Multi-Point Photocell** : Mesure sur plusieurs angles/directions
- **Twilight Switch** : Simple détection jour/nuit avec seuil fixe ou ajustable

## Caractéristiques Techniques Typiques
- Plage de mesure: 0-2,000 lux (intérieur) ou 0-100,000 lux (extérieur)
- Précision: ±5% à ±10%
- Résolution: 1-10 lux
- Temps de réponse: <1 seconde à 10 secondes (avec filtrage)
- Seuil configurable: 50-1,000 lux (pour automatisation on/off)
- Dead band: 10-50 lux (pour éviter l'oscillation)
- Alimentation: 12-24V DC, PoE, ou batterie
- Communication: DALI, BACnet, KNX, Modbus, 0-10V analogique, Zigbee
- Correction cosinus: Oui (pour mesure précise selon angle d'incidence)
- Compensation température: Oui (capteurs de qualité)
- Type de capteur: Photodiode, phototransistor, ou cellule photovoltaïque
- Protection: IP20 à IP65 selon application

## Localisation Typique
- Près des fenêtres et façades vitrées
- Bureaux avec apport de lumière naturelle
- Salles de classe
- Espaces commerciaux avec verrières
- Atriums et halls vitrés
- Toiture et façade extérieure (pilotage éclairage extérieur)
- Parkings avec ouvertures naturelles
- Espaces de circulation avec puits de lumière

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Lighting Panel, PoE Switch, Batterie
- **Contrôlé par** : Lighting Controller, Daylight Harvesting Controller, Building Automation System
- **Contrôle** : LED Luminaire, Fluorescent Luminaire, Dimmer, Blind Controller (intégration avec gestion des stores)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-80
- Moyen (15 étages) : 80-300
- Grand (30+ étages) : 300-1,500

## Sources
- Haystack Project - Photocell and light level sensor definitions
- Brick Schema - Illuminance Sensor class
- DALI Alliance - Light sensor specifications
- IEC 62386-304 - DALI Part 304: Light sensor control interface
- ASHRAE 90.1 - Automatic daylight control requirements
- EN 12464 - Light and lighting standard
