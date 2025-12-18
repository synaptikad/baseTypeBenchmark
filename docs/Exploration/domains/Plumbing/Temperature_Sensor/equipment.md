# Temperature Sensor

## Identifiant
- **Code** : TEMP-SNS-WATER
- **Haystack** : `water`, `temp`, `sensor`, `equip`
- **Brick** : `brick:Water_Temperature_Sensor`

## Description
Sonde de température mesurant la température de l'eau dans les circuits de plomberie, stockage et distribution. Élément fondamental pour la régulation thermique, le confort, la sécurité sanitaire et l'efficacité énergétique.

## Fonction
Mesurer avec précision la température de l'eau aux points stratégiques, transmettre les données au système de régulation, permettre le contrôle anti-légionelle (>55°C), assurer la protection anti-brûlure (<48°C distribution), et optimiser la production d'ECS.

## Variantes Courantes
- **Sonde PT100/PT1000** : Haute précision, linéarité excellente
- **Thermistance NTC** : Économique, bonne sensibilité
- **Thermocouple** : Hautes températures, robuste
- **Sonde sans fil** : IoT, installation simplifiée
- **Sonde d'immersion** : Plongeante dans ballon
- **Sonde à doigt de gant** : Sur canalisation avec puits thermométrique

## Caractéristiques Techniques Typiques
- Plage de mesure : -10°C à +110°C (plomberie)
- Précision : Classe A (±0.15°C), Classe B (±0.3°C)
- Sortie : 4-20mA, 0-10V, Modbus, BACnet, résistance directe
- Temps de réponse : T90 < 30s (eau en mouvement)
- Longueur doigt de gant : 50-300mm
- Indice de protection : IP65-68

## Localisation Typique
- DHW Tank (stratification multi-niveaux)
- Départ/retour circuits ECS
- Sortie Water Heater, Heat Exchanger
- Après Mixing Valve (contrôle température distribution)
- Boucle retour circulation ECS

## Relations avec Autres Équipements
- **Alimente** : N/A (capteur)
- **Alimenté par** : N/A
- **Contrôlé par** : Régulation PID, contrôleur DDC
- **Associé à** : Water Heater (régulation), DHW Tank (stratification), Mixing Valve (sécurité), DHW Circulation Pump

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-15 sondes (production, stockage, distribution)
- Moyen (15 étages) : 15-40 sondes (multi-zones, régulation fine)
- Grand (30+ étages) : 40-100 sondes (monitoring complet tous circuits)

## Sources
- Haystack Project - Temperature sensors
- Brick Schema - Temperature_Sensor class
- IEC 60751 - PT100/PT1000 standards
- ASHRAE Guideline 12 - Legionellosis prevention
