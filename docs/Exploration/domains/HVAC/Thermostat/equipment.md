# Thermostat (Thermostat d'ambiance)

## Identifiant
- **Code** : TSTAT / TH
- **Haystack** : `thermostat-equip`
- **Brick** : `brick:Thermostat`

## Description
Dispositif de régulation de température d'ambiance qui mesure la température de la zone et commande les équipements de chauffage/climatisation pour maintenir une consigne. Interface utilisateur principale pour le confort thermique.

## Fonction
Mesurer la température ambiante, permettre à l'occupant de définir une consigne de confort, et commander les équipements terminaux (radiateurs, ventilo-convecteurs, splits) pour maintenir la température souhaitée.

## Variantes Courantes
- **Thermostat mécanique** : Bilame, sans électronique
- **Thermostat électronique** : Affichage digital, programmable
- **Thermostat connecté/intelligent** : WiFi, apprentissage, géolocalisation
- **Thermostat BMS** : Intégré au système GTB (BACnet/Modbus)
- **Thermostat multizone** : Gestion de plusieurs zones
- **Thermostat avec capteurs intégrés** : Humidité, CO2, présence

## Caractéristiques Techniques Typiques
- Plage mesure : 5-40°C
- Précision : ±0.5°C
- Plage consigne : 15-30°C
- Hystérésis : 0.5-2°C (réglable)
- Alimentation : Pile, 24V, 230V
- Protocoles : BACnet, Modbus, KNX, Zigbee, Z-Wave, WiFi
- Points de supervision : température, consigne, mode, occupation

## Localisation Typique
- Mur de zone (1.5m du sol)
- Bureaux individuels
- Salles de réunion
- Chambres d'hôtel
- Logements

## Relations avec Autres Équipements
- **Commande** : FCU, VAV, Radiateurs, Splits, Planchers chauffants
- **Alimenté par** : Réseau électrique, Pile
- **Contrôlé par** : BMS, Application mobile, Utilisateur
- **Interagit avec** : Capteurs de présence, Contacts de fenêtre, Scheduling

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-50 unités
- Moyen (15 étages) : 50-200 unités
- Grand (30+ étages) : 200-1000 unités
- Hôtel : 1 par chambre

## Sources
- ASHRAE Handbook - Fundamentals
- EN 15500 - Building Automation Controls
- Project Haystack - Thermostat Equipment
- Brick Schema - Thermostat Class
- Honeywell / Siemens / Schneider - Thermostat Documentation
