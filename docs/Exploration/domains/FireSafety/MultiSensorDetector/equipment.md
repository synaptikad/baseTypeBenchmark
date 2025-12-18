# Multi-Sensor Detector

## Identifiant
- **Code** : MULTI-DET
- **Haystack** : multisensor-detector
- **Brick** : brick:Multi_Sensor_Detector

## Description
Dispositif de détection combinant plusieurs technologies (fumée optique, température, et parfois CO) pour améliorer la fiabilité de détection et réduire les fausses alarmes. Utilise des algorithmes pour analyser plusieurs paramètres simultanément.

## Fonction
Offre une détection incendie plus robuste en croisant les données de plusieurs capteurs. Réduit significativement les fausses alarmes tout en maintenant une sensibilité élevée aux vrais départs de feu.

## Variantes Courantes
- **Fumée + Chaleur** : Combine détection optique et thermique
- **Fumée + Chaleur + CO** : Ajoute la détection de monoxyde de carbone
- **Avec intelligence embarquée** : Algorithmes adaptatifs selon l'environnement
- **Version adressable** : Communique valeurs détaillées au panneau
- **Version analogique** : Transmet les valeurs des capteurs pour analyse centralisée

## Caractéristiques Techniques Typiques
- Alimentation : 15-30V DC (via boucle d'alarme)
- Capteurs : Optique + Thermique + CO (option)
- Protocole : Analogique adressable
- Zone de couverture : 50-80 m²
- Algorithmes : Détection multi-critères avec apprentissage
- Température de fonctionnement : -10°C à +55°C
- Certification : EN 54-7, EN 54-5, EN 54-26
- Interface : LED multi-couleur pour diagnostic

## Localisation Typique
- Espaces critiques nécessitant fiabilité maximale
- Zones à risque de fausses alarmes
- Hôpitaux et établissements de santé
- Data centers et salles serveurs
- Musées et archives
- Laboratoires
- Hôtels et résidences

## Relations avec Autres Équipements
- **Alimente** : N/A (dispositif de détection)
- **Alimenté par** : Fire Alarm Panel (via boucle de détection)
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI)
- **Déclenche** : Sounder, Beacon, Smoke Extraction Fan, Fire Door Holder
- **Communique avec** : Building Management System (BMS)

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 30-50 unités
- Moyen (15 étages, 15000 m²) : 150-300 unités
- Grand (30+ étages, 50000 m²) : 500-1000 unités

## Sources
- EN 54-29: Fire detection and fire alarm systems - Multi-sensor fire detectors
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- NFPA 72: National Fire Alarm and Signaling Code
