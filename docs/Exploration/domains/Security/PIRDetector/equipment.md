# PIR Detector (Passive Infrared Detector)

## Identifiant
- **Code** : PIR_DETECTOR
- **Haystack** : pir-sensor
- **Brick** : brick:Motion_Sensor

## Description
Capteur de détection de mouvement basé sur la mesure des variations de rayonnement infrarouge émis par les corps chauds (humains, animaux). Utilisé pour la détection d'intrusion dans les espaces intérieurs. Peut inclure des fonctionnalités anti-masquage et compensation de température.

## Fonction
Détection de présence et de mouvement par analyse des variations de signature thermique dans sa zone de couverture. Génération d'alarmes en cas de détection pendant les périodes d'armement. Protection volumétrique des espaces.

## Variantes Courantes
- **PIR standard** : Détection mouvement standard, portée 10-15m
- **PIR longue portée** : Portée 20-30m, couloirs
- **PIR rideau** : Détection en nappe verticale, protection fenêtres/portes
- **PIR anti-animaux** : Ignore animaux jusqu'à 15-25kg
- **PIR double technologie** : Combine PIR + micro-ondes pour réduction fausses alarmes
- **PIR avec caméra** : Vérification visuelle lors détection
- **PIR extérieur** : Résistant intempéries, compensation thermique avancée

## Caractéristiques Techniques Typiques
- Portée : 10-30m selon modèle
- Angle de couverture : 90-110° horizontal, 80-90° vertical
- Sensibilité réglable : 3-5 niveaux
- Immunité animaux : jusqu'à 15-25kg
- Compensation température : automatique
- Anti-masquage : détection occultation du capteur
- Communication : Filaire (4-wire), sans fil 868MHz/433MHz, BUS RS-485
- Alimentation : 9-16V DC via centrale ou autonome
- Sorties : Contact sec, supervision
- Montage : Mural (coin ou mur), plafond

## Localisation Typique
- Bureaux et espaces de travail (hors heures)
- Couloirs et circulations
- Salles techniques
- Entrepôts et stocks
- Locaux sensibles
- Zones arrière (back-office)
- Espaces commerciaux (après fermeture)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Intrusion Alarm Panel, Power supply
- **Contrôlé par** : Intrusion Alarm Panel, Security Controller
- **Envoie à** : Alarm Panel (état alarme)
- **Interagit avec** : IP Camera (vérification visuelle), Siren, Alarm Keypad

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-50 détecteurs
- Moyen (15 étages) : 100-250 détecteurs
- Grand (30+ étages) : 300-800 détecteurs

## Sources
- EN 50131 - Alarm Systems Standard
- IEC 62642 - Alarm Systems Performance Requirements
- Brick Schema - Motion Sensor Class
