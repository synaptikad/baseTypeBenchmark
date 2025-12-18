# Sprinkler Flow Switch

## Identifiant
- **Code** : FLOW-SW
- **Haystack** : flow-sensor avec tag sprinkler
- **Brick** : brick:Water_Flow_Sensor

## Description
Détecteur de débit d'eau installé sur les canalisations du réseau sprinkler. Signale au Fire Alarm Panel qu'un ou plusieurs sprinklers se sont déclenchés et que l'eau s'écoule dans le réseau. Élément clé de la supervision du système sprinkler.

## Fonction
Détecte l'écoulement d'eau dans le réseau sprinkler et transmet une alarme au système de sécurité incendie. Permet de localiser la zone où le sprinkler s'est activé et déclenche les actions associées (alarme, arrêt ventilation, appel pompiers).

## Variantes Courantes
- **À palette** : Palette mécanique déplacée par le flux
- **Vane type** : Détection mécanique robuste
- **Électronique** : Détection par ultrasons ou turbine
- **Avec temporisation** : Évite alarmes intempestives (10-90 secondes)
- **Adressable** : Communication protocole avec localisation précise
- **Contact sec** : Signal binaire simple

## Caractéristiques Techniques Typiques
- Diamètre canalisation : DN 25 à DN 300
- Débit de déclenchement : 40-150 L/min selon diamètre
- Temporisation réglable : 0-90 secondes
- Contact de sortie : Contact sec NO/NF, isolé
- Alimentation : Passive (contact mécanique) ou 24V DC
- Pression max : 12-16 bar
- Certification : UL, FM, VdS
- Indice de protection : IP54-IP65
- Installation : Horizontale ou verticale selon modèle

## Localisation Typique
- Salle des vannes sprinkler
- Collecteur de distribution par zone
- Départ de chaque zone sprinkler
- Colonne montante sprinkler
- Local technique sprinkler

## Relations avec Autres Équipements
- **Alimente** : N/A (capteur)
- **Alimenté par** : Fire Alarm Panel (24V) ou passif
- **Contrôlé par** : N/A (détecteur autonome)
- **Surveille** : Sprinkler System (débit d'eau)
- **Communique avec** : Fire Alarm Panel (FACP/CMSI)
- **Déclenche** : Alarme sprinkler, arrêt CTA, appel pompiers

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 1-3 unités
- Moyen (15 étages, 15000 m²) : 5-15 unités
- Grand (30+ étages, 50000 m²) : 15-50 unités

## Sources
- EN 12845: Fixed firefighting systems - Automatic sprinkler systems
- NFPA 13: Standard for the Installation of Sprinkler Systems
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- UL 346: Standard for Waterflow Indicators for Fire Protective Signaling Systems
