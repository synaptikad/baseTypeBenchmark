# Fire Door

## Identifiant
- **Code** : FIRE-DOOR
- **Haystack** : fire-door
- **Brick** : brick:Fire_Door

## Description
Porte coupe-feu équipée de capteurs et/ou actionneurs permettant la supervision de son état (ouvert/fermé) et parfois sa fermeture automatique. Élément essentiel du compartimentage coupe-feu du bâtiment, supervisé par le système de sécurité incendie.

## Fonction
Maintient l'intégrité du compartimentage en position normale et assure sa fermeture en cas d'incendie. La supervision permet de vérifier que les portes coupe-feu ne sont pas bloquées ouvertes de manière inappropriée.

## Variantes Courantes
- **Avec contact de position** : Surveillance état ouvert/fermé
- **À fermeture automatique** : Ferme-porte + retenue électromagnétique
- **Motorisée** : Fermeture active par moteur sur alarme
- **Simple vantail** : Une porte
- **Double vantail** : Deux portes avec coordinateur
- **Avec verrou électrique** : Déverrouillage automatique évacuation
- **Avec anti-panique** : Barre de sécurité évacuation

## Caractéristiques Techniques Typiques
- Résistance au feu : EI1 30, EI1 60, EI1 90, EI2 120 minutes
- Contact de position : Contact magnétique ou mécanique
- Retenue électromagnétique : 24V DC, force 50-200 N
- Ferme-porte : Hydraulique calibré selon masse porte
- Supervision : Contact sec NO/NF
- Certification : EN 16034 (Europe), UL 10C (USA)
- Largeur passage : 700-2400 mm
- Coordination : Sélecteur d'ordre pour double vantail

## Localisation Typique
- Limites de compartiments coupe-feu
- Cages d'escaliers (issues de secours)
- Sas d'entrée d'escalier
- Locaux à risque (chaufferie, archives)
- Séparation zones publiques/privées
- Couloirs de circulation
- Zones de cantonnement fumées

## Relations avec Autres Équipements
- **Alimente** : N/A (élément passif supervisé)
- **Alimenté par** : Fire Alarm Panel (retenue électromagnétique)
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI)
- **Libéré par** : Fire Door Holder (relâche la retenue)
- **Déclenché par** : Smoke Detector, Heat Detector, Manual Call Point
- **Communique avec** : Building Management System (BMS) via contact position

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 40-80 unités supervisées
- Moyen (15 étages, 15000 m²) : 200-400 unités supervisées
- Grand (30+ étages, 50000 m²) : 600-1500 unités supervisées

## Sources
- EN 16034: Pedestrian doorsets, industrial, commercial, garage doors and windows - Product standard, performance characteristics - Fire resistance and/or smoke control characteristics
- EN 1634-1: Fire resistance and smoke control tests for door and shutter assemblies
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- NFPA 80: Standard for Fire Doors and Other Opening Protectives
