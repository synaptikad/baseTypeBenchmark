# Parking Sensor (Magnetic)

## Identifiant
- **Code** : PARKING_SENSOR_MAG
- **Haystack** : N/A
- **Brick** : N/A

## Description
Capteur de détection de présence véhicule basé sur technologie magnétique. Installé dans le sol de chaque place, détecte les variations du champ magnétique terrestre causées par la masse métallique du véhicule.

## Fonction
Détection fiable de l'occupation des places de stationnement en extérieur ou souterrain. Remonte l'état (libre/occupé) et durée d'occupation vers système central. Robuste aux conditions climatiques.

## Variantes Courantes
- **Capteur encastré** : Installation par carottage dans béton/asphalte
- **Capteur de surface** : Fixation par résine, installation rapide
- **Version LoRaWAN** : Transmission longue portée, batterie 5-10 ans
- **Version NB-IoT** : Connectivité cellulaire, couverture nationale

## Caractéristiques Techniques Typiques
- Technologie : Magnétomètre 3 axes (détection champ magnétique)
- Précision détection : > 98%
- Alimentation : Batterie lithium 3.6V (5-10 ans autonomie)
- Communication : LoRaWAN, NB-IoT, Sigfox, Zigbee
- Fréquence transmission : 1-5 minutes (configurable)
- Température opération : -40°C à +85°C
- Protection : IP68 (immersion temporaire)
- Résistance charge : 40 tonnes

## Localisation Typique
- Parking extérieur en surface
- Voirie urbaine (stationnement sur rue)
- Parking souterrain (alternative ultrason)
- Zones de livraison réglementées

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Batterie autonome (pas d'alimentation externe)
- **Contrôlé par** : Parking Guidance Controller, Parking Management Server
- **Interagit avec** : Gateway LoRaWAN/NB-IoT, Parking Guidance Display, système de tarification dynamique

## Quantité Typique par Bâtiment
- Petit (parking 50 places extérieur) : 50 capteurs (1 par place)
- Moyen (parking 200 places) : 200 capteurs (1 par place)
- Grand (voirie urbaine 1000+ places) : 1000+ capteurs (1 par place)

## Sources
- Standards ITS (Intelligent Transportation Systems)
- Spécifications LoRaWAN Alliance
- 3GPP NB-IoT standards
- Documentation systèmes smart parking
