# Connected Switch (Interrupteur connecté)

## Identifiant
- **Code** : CSW / SW
- **Haystack** : `switch-equip`
- **Brick** : `brick:Lighting_Switch`

## Description
Interrupteur mural intelligent permettant le contrôle de l'éclairage avec communication vers le système de gestion du bâtiment. Peut intégrer des capteurs de présence, luminosité et température. Interface utilisateur locale et distante.

## Fonction
Permettre le contrôle manuel de l'éclairage par les occupants tout en remontant l'état et la consommation au BMS. Peut servir de point de commande local pour les scénarios d'éclairage ou de dérogation des automatismes.

## Variantes Courantes
- **Interrupteur simple connecté** : On/Off avec retour d'état
- **Interrupteur variateur** : Dimming intégré
- **Interrupteur scène** : Plusieurs touches pour scénarios
- **Interrupteur avec présence** : Capteur PIR intégré
- **Interrupteur avec luminosité** : Capteur lux intégré
- **Interrupteur multifonction** : Éclairage + stores + CVC

## Caractéristiques Techniques Typiques
- Charge commutée : 6A-16A (1500W-3600W)
- Tension : 230V AC
- Type de charge : LED, incandescent, fluorescent, moteur
- Protocoles : DALI, KNX, Zigbee, Z-Wave, WiFi, Bluetooth
- Alimentation : Fil neutre ou sans neutre
- Points de supervision : état, consommation, présence, luminosité

## Localisation Typique
- Entrée de pièces
- À côté des portes
- Têtes de lit (hôtel)
- Postes de travail
- Salles de réunion

## Relations avec Autres Équipements
- **Commande** : Luminaires, Circuits d'éclairage, Scènes
- **Alimenté par** : Réseau électrique 230V
- **Contrôlé par** : BMS, Utilisateur, Automatismes horaires
- **Interagit avec** : Capteurs de présence, Capteurs de lumière, DALI bus

## Quantité Typique par Bâtiment
- Petit (5 étages) : 50-150 unités
- Moyen (15 étages) : 150-500 unités
- Grand (30+ étages) : 500-2000 unités

## Sources
- IEC 60669 - Switches for Household Installations
- EN 15193 - Energy Performance of Buildings - Lighting
- Project Haystack - Lighting Switch Tags
- Brick Schema - Lighting_Switch Class
- Schneider / Legrand / Hager - Connected Switch Documentation
