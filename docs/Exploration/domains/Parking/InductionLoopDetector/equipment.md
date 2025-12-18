# Induction Loop Detector

## Identifiant
- **Code** : INDUCTION_LOOP
- **Haystack** : N/A
- **Brick** : N/A

## Description
Boucle de détection inductive encastrée dans la chaussée. Détecte présence véhicule par variation d'inductance magnétique causée par masse métallique. Utilisé pour déclencher ouverture barrière, comptage, et sécurité anti-écrasement.

## Fonction
Détection de présence véhicule fiable et robuste. Déclenche actions automatiques (ouverture barrière, validation passage, comptage véhicules) et assure sécurité (empêche fermeture barrière sur véhicule présent).

## Variantes Courantes
- **Boucle simple** : Détection présence uniquement
- **Boucle double** : Détection + sens de circulation + vitesse
- **Boucle de sécurité** : Protection anti-écrasement barrière
- **Boucle de comptage** : Décompte véhicules entrants/sortants

## Caractéristiques Techniques Typiques
- Technologie : Boucle inductive enfouie (câble 2-4 spires)
- Dimensions boucle : 1x2 m à 2x3 m (selon voie)
- Profondeur encastrement : 3-5 cm dans béton/asphalte
- Fréquence opération : 20-200 kHz
- Détecteur : Contrôleur inductif séparé (armoire technique)
- Sortie : Relais contact sec, signal 0-10V, RS485
- Alimentation détecteur : 12-24V DC ou 230V AC
- Sensibilité : Ajustable (moto à poids lourd)
- Température opération : -40°C à +85°C

## Localisation Typique
- Avant barrière entrée (déclenchement distribution ticket)
- Après barrière entrée (comptage entrée, sécurité)
- Avant barrière sortie (sécurité anti-écrasement)
- Après barrière sortie (comptage sortie)
- Zones de pesage (optionnel)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : 12-24V DC (contrôleur boucle)
- **Contrôlé par** : Entry/Exit Station, contrôleur barrière
- **Interagit avec** : Barrier Gate (commande ouverture/sécurité), Ticket Dispenser (déclenchement), Parking Management Server (comptage)

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 4-8 boucles (2-4 par voie entrée/sortie)
- Moyen (parking 200 places) : 8-16 boucles (multiples voies)
- Grand (parking 1000+ places) : 20-40 boucles (nombreux accès)

## Sources
- Standards détection véhicules (ASTM E2563)
- Documentation systèmes contrôle accès parking
- Spécifications boucles inductives industrielles
