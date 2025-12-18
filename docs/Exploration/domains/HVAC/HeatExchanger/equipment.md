# Heat Exchanger (Échangeur de Chaleur)

## Identifiant
- **Code** : HX / ECH
- **Haystack** : `heatExchanger-equip`
- **Brick** : `brick:Heat_Exchanger`

## Description
Dispositif qui transfère la chaleur entre deux fluides sans les mélanger. Utilisé pour récupérer l'énergie, isoler des circuits hydrauliques (sous-stations), ou préchauffer/pré-refroidir des flux d'air ou d'eau.

## Fonction
Transférer l'énergie thermique d'un fluide chaud vers un fluide froid de manière efficace, soit pour récupération d'énergie, soit pour séparation hydraulique de circuits.

## Variantes Courantes
- **Échangeur à plaques** : Eau-eau, compact, haute efficacité
- **Échangeur rotatif (roue thermique)** : Air-air, récupération d'énergie sur AHU
- **Échangeur à tubes et calandre** : Eau-eau, grandes puissances
- **Échangeur air-air à plaques fixes** : Récupération sans mélange des flux
- **Échangeur caloporteur (run-around coil)** : Récupération air-air via circuit glycol
- **Échangeur de sous-station** : Interface entre réseau urbain et bâtiment

## Caractéristiques Techniques Typiques
- Puissance échangée : 10 kW - 5 MW
- Efficacité : 50-85% selon technologie
- Fluides : Eau-eau, Air-air, Eau-glycol
- Delta T : 5-20°C
- Protocoles : BACnet, Modbus (si motorisé/contrôlé)
- Points de supervision : températures entrée/sortie (4 mesures), puissance échangée, efficacité

## Localisation Typique
- AHU (échangeur rotatif ou plaques fixes intégré)
- Sous-station technique (échangeur à plaques)
- Circuit séparation hydraulique
- Système de récupération d'énergie

## Relations avec Autres Équipements
- **Alimente** : Circuit secondaire (bâtiment) en énergie
- **Alimenté par** : Circuit primaire (production ou réseau urbain), Air extrait (si air-air)
- **Contrôlé par** : Vannes de régulation, BMS
- **Interagit avec** : Pompes, Thermostats, Compteurs d'énergie

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-5 unités
- Moyen (15 étages) : 5-15 unités
- Grand (30+ étages) : 15-40 unités

## Sources
- Haystack Project - Heat Exchanger Equipment
- Brick Schema - Heat Exchanger Classes
- BACnet Standard - Heat Recovery
- ASHRAE Handbook - Heat Exchangers and Energy Recovery
