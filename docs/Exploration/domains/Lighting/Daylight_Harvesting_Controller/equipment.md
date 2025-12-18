# Daylight Harvesting Controller

## Identifiant
- **Code** : DAYLIGHT_CTRL
- **Haystack** : daylight, harvesting, controller, lighting
- **Brick** : brick:Daylight_Harvesting_Controller, brick:Controller

## Description
Système de contrôle intelligent optimisant l'utilisation de la lumière naturelle en ajustant automatiquement l'éclairage artificiel en fonction de l'apport de lumière du jour. Le contrôleur mesure continuellement l'éclairement ambiant via des photocellules et module l'intensité des luminaires pour maintenir un niveau d'éclairement cible constant tout en maximisant les économies d'énergie.

## Fonction
Réduire la consommation énergétique d'éclairage en exploitant au maximum la lumière naturelle disponible. Le système maintient un niveau d'éclairement constant au plan de travail en diminuant progressivement l'éclairage artificiel lorsque la lumière naturelle augmente, et vice-versa. Assure le confort visuel tout en optimisant l'efficacité énergétique.

## Variantes Courantes
- **Open-Loop Daylight Controller** : Mesure de la lumière extérieure, contrôle prédictif
- **Closed-Loop Daylight Controller** : Mesure de la lumière intérieure, contrôle asservi
- **Hybrid Daylight Controller** : Combinaison open-loop et closed-loop
- **Zone-Based Daylight Controller** : Contrôle différencié par zone de profondeur (fenêtre, milieu, fond)
- **Continuous Dimming Controller** : Gradation fluide et continue
- **Stepped Dimming Controller** : Gradation par paliers (économie simple)
- **Perimeter Daylight Controller** : Spécialisé pour zones périmétriques vitrées
- **Skylight Controller** : Contrôle sous verrières et puits de lumière
- **Integrated Blind Controller** : Coordonné avec gestion des stores

## Caractéristiques Techniques Typiques
- Nombre de photocellules: 1 à 10+ par contrôleur
- Zones de contrôle: 1 à 20 zones indépendantes
- Canaux de sortie: 1 à 50+ canaux
- Niveau d'éclairement cible: 200-1,000 lux (configurable)
- Précision de régulation: ±5% à ±10%
- Temps de réponse: 10 secondes à 5 minutes (avec filtrage anti-oscillation)
- Dead band: 20-100 lux (évite les variations continuelles)
- Taux de gradation: 1-10% par seconde (imperceptible)
- Protocoles: DALI, 0-10V, DMX, BACnet, Modbus, KNX
- Algorithme: PID, fuzzy logic, ou adaptatif auto-calibrant
- Compensation temporelle: Filtrage des variations rapides (nuages)
- Mode override: Manuel temporaire ou permanent
- Calibration: Automatique ou assistée
- Alimentation: 24V DC, PoE, ou secteur
- Interface: Web, application mobile, ou intégré au BMS

## Localisation Typique
- Bureaux périmétriques avec fenêtres
- Open-spaces à proximité des façades
- Salles de classe avec fenestration importante
- Espaces commerciaux avec vitrines
- Atriums et halls avec verrières
- Bibliothèques et espaces de lecture
- Couloirs avec apport de lumière naturelle
- Espaces sous skylights ou puits de lumière
- Zones de travail orientées sud/est/ouest

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, PoE Switch
- **Contrôlé par** : Building Automation System (supervision et paramétrage)
- **Contrôle** : LED Luminaire, Fluorescent Luminaire, Dimmer
- **Reçoit données de** : Photocell, Light Sensor, parfois Weather Station
- **Peut coordonner avec** : Blind/Shade Controller, HVAC Controller (charge thermique)
- **Communique avec** : Lighting Controller, Energy Management System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-20
- Moyen (15 étages) : 20-80
- Grand (30+ étages) : 80-400

## Sources
- ASHRAE 90.1 - Energy Standard for Buildings (daylight control requirements)
- California Title 24 - Daylighting control requirements
- IES (Illuminating Engineering Society) - Daylight harvesting design guides
- LEED - Daylighting and views credits
- IEC 62386-304 - DALI light sensor control interface
- Haystack Project - Daylight control definitions
- Brick Schema - Daylight Harvesting Controller class
