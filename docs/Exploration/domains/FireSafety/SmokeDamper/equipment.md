# Smoke Damper

## Identifiant
- **Code** : SMOKE-DMP
- **Haystack** : smoke-damper
- **Brick** : brick:Smoke_Damper

## Description
Volet motorisé installé dans les conduits de ventilation pour contrôler la propagation des fumées. Contrairement au fire damper, il est conçu spécifiquement pour l'étanchéité aux fumées et gaz de combustion, avec commande active depuis le système de sécurité incendie.

## Fonction
Empêche la migration des fumées à travers les réseaux de ventilation lors d'un incendie. Permet également le contrôle actif des fumées en ouvrant ou fermant selon les scénarios de désenfumage définis.

## Variantes Courantes
- **Motorisé 24V DC** : Commande électrique depuis FACP
- **Motorisé 230V AC** : Avec alimentation secteur
- **Combiné feu/fumée** : Double certification EI + S (leakage)
- **À action rapide** : Fermeture <60 secondes
- **Modulant** : Positionnement intermédiaire possible
- **Fail-safe** : Position de sécurité en cas de perte alimentation
- **Étanche classe S** : Différents niveaux d'étanchéité (S200, S400, S1300)

## Caractéristiques Techniques Typiques
- Étanchéité fumée : Classe S200, S400, S1300 (débit de fuite à 300 Pa)
- Actionneur : Moteur 24V DC ou 230V AC
- Temps de fermeture : 30-90 secondes
- Couple moteur : Variable selon dimension
- Retour d'information : Contact fin de course + potentiomètre position
- Protocole : Contact sec, 0-10V, Modbus
- Certification : EN 12101-8 (Europe), UL 555S (USA)
- Température max : 150°C-300°C

## Localisation Typique
- Conduits de ventilation CTA
- Système de désenfumage mécanique
- Réseaux extraction fumées
- Séparation de zones de désenfumage
- Halls et atriums
- Parkings (extraction fumées)
- Escaliers pressurisés

## Relations avec Autres Équipements
- **Alimente** : N/A (dispositif de contrôle fumées)
- **Alimenté par** : Fire Alarm Panel, BMS
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI), Smoke Control System
- **Associé à** : Smoke Extraction Fan, Supply Fan, AHU
- **Déclenché par** : Smoke Detector, Fire Alarm Panel
- **Communique avec** : Building Management System (BMS)

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 15-40 unités
- Moyen (15 étages, 15000 m²) : 80-200 unités
- Grand (30+ étages, 50000 m²) : 300-800 unités

## Sources
- EN 12101-8: Smoke and heat control systems - Smoke control dampers
- EN 1366-10: Fire resistance tests for service installations - Smoke control dampers
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- UL 555S: Standard for Smoke Dampers
