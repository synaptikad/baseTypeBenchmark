# Ticket Dispenser

## Identifiant
- **Code** : TICKET_DISPENSER
- **Haystack** : N/A
- **Brick** : N/A

## Description
Distributeur automatique de tickets de parking à l'entrée. Délivre un ticket papier ou code-barres lors de l'arrivée du véhicule, enregistre l'heure d'entrée, et initialise la transaction de stationnement.

## Fonction
Émission de justificatif d'entrée horodaté pour système de tarification au temps passé. Enregistrement des transactions d'entrée et communication avec système central pour gestion des capacités.

## Variantes Courantes
- **Ticket thermique** : Impression code-barres/QR sur ticket papier
- **Ticket RFID** : Ticket avec puce RFID réutilisable ou jetable
- **Hybride** : Ticket papier + code-barres + RFID
- **Sans ticket** : Capture plaque uniquement (ANPR full)

## Caractéristiques Techniques Typiques
- Technologie impression : Thermique direct
- Capacité rouleau : 2000-5000 tickets
- Temps distribution : < 2 secondes
- Encodage : Code-barres 1D/2D, QR code, RFID
- Protocoles : RS232/485, TCP/IP, Modbus
- Détection véhicule : Boucle inductive, capteur IR/ultrason
- Température opération : -20°C à +60°C
- Protection : IP54 (usage extérieur)

## Localisation Typique
- Entrée principale parking public
- Voie d'accès visiteurs
- Entrée parking temporaire
- Zones de stationnement courte durée

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : 230V AC
- **Contrôlé par** : Entry/Exit Station, Parking Management Server
- **Interagit avec** : Barrier Gate (commande ouverture après distribution), Induction Loop Detector (détection véhicule), Parking Revenue Control System

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 1-2 distributeurs (entrée principale)
- Moyen (parking 200 places) : 2-4 distributeurs (multiples voies)
- Grand (parking 1000+ places) : 4-10 distributeurs (entrées multiples)

## Sources
- Standards industrie parking (IPI)
- Spécifications systèmes contrôle accès parking
- Protocoles impression thermique
