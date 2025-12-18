# EV Charger Level 2

## Identifiant
- **Code** : EV_CHARGER_L2
- **Haystack** : N/A
- **Brick** : N/A

## Description
Borne de recharge pour véhicules électriques de niveau 2 (AC), fournissant une puissance de 7 à 22 kW. Permet une recharge complète en 4-8 heures. Équipement connecté via protocole OCPP pour supervision et paiement.

## Fonction
Recharge des véhicules électriques en courant alternatif avec puissance moyenne. Gestion de sessions de charge, authentification utilisateurs, facturation et reporting énergétique vers système central.

## Variantes Courantes
- **Monophasé 7 kW** : Usage résidentiel et parkings publics standard
- **Triphasé 11 kW** : Usage commercial, charge accélérée
- **Triphasé 22 kW** : Charge rapide AC, flottes professionnelles
- **Double connecteur** : Deux points de charge sur une même borne

## Caractéristiques Techniques Typiques
- Puissance : 7-22 kW AC
- Connecteurs : Type 2 (Europe), J1772 (US)
- Protocoles : OCPP 1.6/2.0.1, Modbus TCP, ISO 15118
- Authentification : RFID, NFC, QR code, application mobile
- Alimentation : 230V monophasé ou 400V triphasé
- Protection : IP54 ou IP65 (usage extérieur)
- Température opération : -25°C à +50°C
- Communication : Ethernet, WiFi, 4G/5G, Zigbee

## Localisation Typique
- Parking souterrain
- Parking extérieur
- Parking réservé employés
- Zones de stationnement longue durée
- Emplacements dédiés EV

## Relations avec Autres Équipements
- **Alimente** : Véhicule électrique
- **Alimenté par** : Distribution électrique BT, tableau de protection
- **Contrôlé par** : Parking Management Server, EV Charging Management System (OCPP backend)
- **Interagit avec** : Payment Terminal, Access Control Reader, EV Charging Station Display, système de gestion énergétique du bâtiment

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 2-5 bornes (4-10% des places)
- Moyen (parking 200 places) : 10-20 bornes (5-10% des places)
- Grand (parking 1000+ places) : 50-150 bornes (5-15% des places)

## Sources
- Standard OCPP 1.6 et 2.0.1 (Open Charge Point Protocol)
- ISO 15118 (Vehicle-to-Grid Communication)
- IEC 61851 (Electric vehicle conductive charging systems)
- Directives européennes infrastructure recharge
