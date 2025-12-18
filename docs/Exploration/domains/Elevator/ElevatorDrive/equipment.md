# Elevator Drive

## Identifiant
- **Code** : ELEV_DRIVE
- **Haystack** : elev + drive + vfd + equip
- **Brick** : brick:Elevator_Drive (subclass of brick:Variable_Frequency_Drive)

## Description
Variateur de fréquence contrôlant le moteur de traction de l'ascenseur. Gère vitesse, accélération, décélération et positionnement précis. Équipement électronique de puissance communicant avec supervision énergétique.

## Fonction
Convertir l'alimentation électrique pour contrôler précisément la vitesse et le couple du moteur de traction. Assurer démarrages et arrêts progressifs, positionnement précis au palier, optimisation énergétique avec récupération possible.

## Variantes Courantes
- **Variateur VVVF standard** : Tension et fréquence variables
- **Variateur régénératif** : Récupération énergie à la descente
- **Variateur gearless** : Pour moteurs sans réducteur
- **Variateur haute performance** : Très haute précision (gratte-ciels)
- **Variateur hydraulique** : Pour ascenseurs à vérin

## Caractéristiques Techniques Typiques
- Puissance : 5 kW à 100 kW selon capacité
- Contrôle vectoriel ou DTC
- Fréquence sortie : 0-400 Hz
- Régulation vitesse : ±0.01 m/s
- Rendement : 95-98%
- Récupération énergie : jusqu'à 40%
- Protocoles : Modbus TCP, BACnet/IP, CANopen
- Monitoring : Courant, tension, température, alarmes
- Filtres CEM et harmoniques

## Localisation Typique
- Salle des machines
- Armoire électrique dans gaine (MRL)
- Local technique ascenseurs

## Relations avec Autres Équipements
- **Alimente** : Traction Motor
- **Alimenté par** : Electrical Panel, Emergency Power Transfer Switch
- **Contrôlé par** : Elevator Controller
- **Supervise par** : Elevator Monitoring System, Energy Management System
- **Interagit avec** : Position Encoder, Speed Governor, Brake System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 variateurs (1 par ascenseur)
- Moyen (15 étages) : 4-8 variateurs (1 par ascenseur)
- Grand (30+ étages) : 12-32 variateurs (1 par ascenseur)

## Sources
- IEC 61800-2 - Adjustable speed electrical power drive systems
- Haystack Project 4.0 - VFD equipment tagging
- Brick Schema - Variable_Frequency_Drive class
- Elevator drive systems and energy efficiency standards
