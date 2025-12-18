# Dimmer

## Identifiant
- **Code** : DIMMER
- **Haystack** : dimmer, actuator, lighting
- **Brick** : brick:Dimmer, brick:Lighting_Dimmer

## Description
Dispositif de contrôle permettant de faire varier l'intensité lumineuse d'un ou plusieurs luminaires. Les dimmers modernes utilisent des techniques de modulation électronique (PWM, phase-cut, 0-10V) et peuvent être intégrés dans des systèmes de gestion du bâtiment via protocoles de communication standardisés.

## Fonction
Ajuster progressivement le niveau d'éclairement de 0% à 100% en réponse aux commandes manuelles (interrupteur), automatiques (capteurs, programmation horaire) ou via le système de supervision. Permet des économies d'énergie et l'adaptation du confort visuel aux besoins des occupants.

## Variantes Courantes
- **Leading-Edge Dimmer** : Coupe de phase en début de cycle (pour charges résistives et inductives)
- **Trailing-Edge Dimmer** : Coupe de phase en fin de cycle (pour charges capacitives, LED)
- **0-10V Dimmer** : Contrôle analogique standard (compatible DALI)
- **DALI Dimmer** : Contrôle digital bidirectionnel adressable
- **PWM Dimmer** : Modulation de largeur d'impulsion (pour LED DC)
- **DMX Dimmer** : Contrôle professionnel pour éclairage architectural
- **Wireless Dimmer** : Sans fil (Zigbee, Bluetooth, EnOcean)
- **Multi-Channel Dimmer** : 4 à 12 canaux indépendants
- **Rack-Mount Dimmer** : Format rack 19" pour salles techniques
- **DIN-Rail Dimmer** : Montage sur rail DIN dans tableau électrique

## Caractéristiques Techniques Typiques
- Tension d'alimentation: 120-277V AC ou 12-48V DC
- Puissance par canal: 100W à 3,000W
- Nombre de canaux: 1 à 12 (ou plus pour racks)
- Plage de variation: 0-100% ou 1-100% (selon technologie)
- Résolution: 8-bit (256 niveaux) à 16-bit (65,536 niveaux)
- Fréquence PWM: 200Hz à 20kHz (sans scintillement visible)
- Courbe de dimming: Linéaire, logarithmique, ou personnalisée
- Communication: DALI, DALI-2, DMX512, KNX, BACnet, Modbus, 0-10V
- Protection: Court-circuit, surcharge thermique
- Compatibilité charges: LED, halogène, incandescent, fluorescent (selon modèle)
- Montage: Mural, encastré, rail DIN, rack 19"
- Dissipation thermique: Passive ou active (ventilateur)

## Localisation Typique
- Salles de réunion et de conférence
- Auditoriums et amphithéâtres
- Restaurants et espaces de restauration
- Espaces de vente et showrooms
- Bureaux open-space
- Couloirs et circulations
- Salles de classe
- Espaces de réception et lobbies
- Tableaux électriques et locaux techniques

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Lighting Panel, Electrical Panel
- **Contrôlé par** : Lighting Controller, Occupancy Sensor, Photocell, Connected Switch, Scene Controller, Building Automation System
- **Contrôle** : LED Luminaire, Fluorescent Luminaire (avec ballast dimmable), Halogen Luminaire

## Quantité Typique par Bâtiment
- Petit (5 étages) : 30-150
- Moyen (15 étages) : 150-600
- Grand (30+ étages) : 600-3,000

## Sources
- Haystack Project - Dimmer equipment definitions
- Brick Schema - Dimmer class
- DALI Alliance - Dimming control specifications
- IEC 62386 - DALI standard series
- ANSI E1.3 - Entertainment Technology (DMX512-A)
- NEMA SSL 7A - Phase-cut dimming for LED lamps
