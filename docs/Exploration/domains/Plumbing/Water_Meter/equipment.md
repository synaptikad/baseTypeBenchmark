# Water Meter

## Identifiant
- **Code** : WATER-MTR
- **Haystack** : `water`, `meter`, `equip`
- **Brick** : `brick:Water_Meter`

## Description
Compteur d'eau intelligent mesurant la consommation volumétrique d'eau dans le bâtiment. Équipement communicant permettant le relevé à distance, la détection de fuites et l'analyse des profils de consommation.

## Fonction
Mesurer avec précision les volumes d'eau consommés (froide et/ou chaude), transmettre les données de consommation au système de supervision, détecter les anomalies de consommation (fuites, surconsommations), et permettre la facturation et l'optimisation des usages.

## Variantes Courantes
- **Compteur mécanique communicant** : Turbine avec module de télé-relève
- **Compteur électromagnétique** : Haute précision, sans pièce mobile
- **Compteur ultrasonique** : Mesure par temps de transit, très précis
- **Compteur volumétrique** : Pistons rotatifs, faibles débits
- **Compteur divisionnaire** : Par appartement ou zone dans bâtiments multi-locataires

## Caractéristiques Techniques Typiques
- Diamètre : DN15 à DN200 (selon débit)
- Classe de précision : A, B, C (ISO 4064)
- Plage de mesure : Qmin à Qmax (ratio 1:100 à 1:400)
- Communication : M-Bus, Modbus, LoRaWAN, NB-IoT, impulsion
- Relevé : Volume cumulé, débit instantané, alarmes
- Alimentation : Batterie (10-15 ans) ou secteur

## Localisation Typique
- Point de livraison réseau urbain (entrée bâtiment)
- Comptage divisionnaire (étages, appartements)
- Départ circuits spécialisés (process, arrosage)
- Chaufferie (eau froide/chaude sanitaire)

## Relations avec Autres Équipements
- **Alimente** : N/A (instrument de mesure)
- **Alimenté par** : N/A (sur réseau hydraulique)
- **Contrôlé par** : Système de comptage, superviseur GTB
- **Associé à** : Leak Detector, système de facturation, analytics

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-5 compteurs (général + circuits principaux)
- Moyen (15 étages) : 5-20 compteurs (par zone, étage, usage)
- Grand (30+ étages) : 20-100 compteurs (divisionnaire + sous-comptage détaillé)

## Sources
- Haystack Project - Metering equipment
- Brick Schema - Meter classes
- ISO 4064 - Water meters standards
- Smart metering standards (M-Bus, LoRaWAN)
