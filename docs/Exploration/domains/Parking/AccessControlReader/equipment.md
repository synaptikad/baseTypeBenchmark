# Access Control Reader

## Identifiant
- **Code** : ACCESS_READER
- **Haystack** : N/A
- **Brick** : N/A

## Description
Lecteur d'authentification pour contrôle d'accès parking. Lit badges RFID, cartes magnétiques, QR codes, ou NFC pour identifier véhicules autorisés (abonnés, employés, résidents). Déclenche ouverture barrière/bollard après validation.

## Fonction
Authentification automatisée des usagers autorisés. Validation identité basée sur supports physiques ou virtuels, vérification droits d'accès en base de données, et commande ouverture équipements (barrière, bollard) pour accès sans ticket.

## Variantes Courantes
- **RFID longue portée** : Lecture mains-libres 5-15 mètres (UHF)
- **RFID courte portée** : Proximité 5-20 cm (13.56 MHz)
- **Lecteur multi-technologies** : RFID + NFC + QR code + Bluetooth
- **Lecteur biométrique** : Empreinte digitale, reconnaissance faciale (haute sécurité)

## Caractéristiques Techniques Typiques
- Technologies : RFID 125 kHz/13.56 MHz/UHF, NFC, code-barres/QR, Bluetooth Low Energy
- Portée lecture : 5 cm à 15 mètres (selon technologie)
- Temps réponse : < 0.5 seconde
- Protocoles : Wiegand, RS232/485, TCP/IP, OSDP
- Alimentation : 12-24V DC, PoE
- Température opération : -30°C à +60°C
- Protection : IP54-IP67, IK10
- LED/buzzer : Retour visuel/sonore validation

## Localisation Typique
- Entrée parking (station d'accès abonnés)
- Accès zones réservées (VIP, employés, handicapés)
- Portillons piétons parking
- Ascenseurs (restriction étages)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : 12-24V DC ou PoE
- **Contrôlé par** : Parking Management Server, système de contrôle d'accès (PACS)
- **Interagit avec** : Barrier Gate (commande ouverture), Bollard (commande escamotage), Entry/Exit Station (intégré), base de données badges autorisés

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 2-4 lecteurs (entrée/sortie + zones réservées)
- Moyen (parking 200 places) : 4-10 lecteurs (multiples accès/zones)
- Grand (parking 1000+ places) : 10-30 lecteurs (nombreuses zones contrôlées)

## Sources
- Standards RFID (ISO 14443, ISO 15693, ISO 18000-6C)
- Protocole OSDP (Open Supervised Device Protocol)
- Spécifications systèmes contrôle d'accès (PACS)
