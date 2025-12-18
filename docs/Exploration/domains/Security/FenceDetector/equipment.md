# Fence Detector

## Identifiant
- **Code** : FENCE_DETECTOR
- **Haystack** : fence-detector
- **Brick** : brick:Fence_Intrusion_Sensor

## Description
Système de détection d'intrusion périmétrique installé sur ou à proximité des clôtures. Détecte les tentatives d'escalade, de coupe, de soulèvement ou de vibration de la clôture. Technologies variées : câbles piézo-électriques, fibres optiques, capteurs de vibration, détection électromagnétique.

## Fonction
Détection précoce d'intrusion au périmètre extérieur, analyse des vibrations et déformations de clôture, discrimination des fausses alarmes (vent, animaux), zonage précis du point d'intrusion, intégration avec système d'alarme et vidéo.

## Variantes Courantes
- **Câble piézo-électrique** : Détection vibrations, fixé sur clôture
- **Fibre optique** : Détection déformation par analyse lumière
- **Micro-ondes** : Barrière invisible au-dessus clôture
- **Capteur électronique** : Analyse patterns vibratoires
- **Câble enterré** : Détection tunnel/approche périmètre

## Caractéristiques Techniques Typiques
- Portée : 100-300m par zone selon technologie
- Sensibilité : Réglable 1-10 niveaux
- Zonage : 2-16 zones par processeur
- Discrimination : Filtrage vent, animaux, pluie
- Alimentation : 12-24V DC
- Communication : RS-485, TCP/IP, 4-wire
- Résistance : IP65-IP68, -40°C à +70°C
- Installation : Clôture rigide, grillage, barreaux

## Localisation Typique
- Périmètres de sécurité
- Clôtures sites industriels
- Enceintes critiques (datacenters, prisons)
- Zones restreintes
- Frontières de sites sensibles

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Intrusion Panel, Power supply
- **Contrôlé par** : Intrusion Panel, Perimeter Controller
- **Envoie à** : Alarm Panel (événements alarme)
- **Interagit avec** : IP Camera (vérification vidéo), Lighting (éclairage zone)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0 (rare)
- Moyen (15 étages) : 0-2 zones périmètre
- Grand (30+ étages) : 2-8 zones (sites sensibles)

## Sources
- IEC 60839-11-1 - Perimeter Protection Systems
- Fence Detection Technologies Standards
- Brick Schema - Intrusion Sensor Class
