# Door Contact (Magnetic Contact)

## Identifiant
- **Code** : DOOR_CONTACT
- **Haystack** : door-sensor
- **Brick** : brick:Magnetic_Contact_Sensor

## Description
Capteur magnétique de position détectant l'ouverture ou la fermeture d'une porte, fenêtre ou autre ouvrant. Composé de deux parties : un aimant fixé sur la partie mobile et un contact reed (ILS - Interrupteur à Lame Souple) sur le dormant. Utilisé pour la détection d'intrusion et le monitoring d'état.

## Fonction
Surveillance permanente de l'état (ouvert/fermé) des ouvrants, génération d'alarme en cas d'ouverture non autorisée en mode armé, monitoring d'état pour systèmes de contrôle d'accès et BMS, détection sabotage (arrachement).

## Variantes Courantes
- **Contact apparent** : Montage en surface, visible
- **Contact encastré** : Intégré dans le dormant/ouvrant
- **Contact renforcé** : Pour portes métalliques, blindées
- **Contact grand écart** : Écartement aimant-contact jusqu'à 50-100mm
- **Contact avec autoprotection** : Détection d'arrachement
- **Contact codé** : Aimant spécifique pour éviter leurrage
- **Contact sans fil** : Transmission radio

## Caractéristiques Techniques Typiques
- Écartement standard : 10-20mm
- Écartement max : 50-100mm (modèles grand écart)
- Type sortie : Contact sec NO/NC (Normally Open/Normally Closed)
- Supervision : Résistance de fin de ligne (EOL)
- Autoprotection : Contact additionnel anti-arrachement
- Communication : Filaire (2-4 fils), sans fil 868MHz/433MHz
- Matériau : Plastique ABS, métal (environnements industriels)
- Protection : IP20 (intérieur) à IP67 (extérieur)
- Température : -20°C à +60°C

## Localisation Typique
- Toutes portes d'accès
- Fenêtres
- Portes techniques
- Trappes d'accès
- Armoires sensibles
- Grilles et volets
- Portes de secours
- Baies de serveurs

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Intrusion Alarm Panel, Access Controller (supervision)
- **Contrôlé par** : Alarm Panel, Door Controller, Access Controller
- **Envoie à** : Alarm Panel, Access Controller, BMS
- **Interagit avec** : Electric Lock, Request-to-Exit Sensor, PIR Detector

## Quantité Typique par Bâtiment
- Petit (5 étages) : 30-100 contacts
- Moyen (15 étages) : 150-400 contacts
- Grand (30+ étages) : 500-1500 contacts

## Sources
- EN 50131-2-6 - Opening Contacts Requirements
- Brick Schema - Magnetic Contact Sensor
- OSDP Input Specifications
