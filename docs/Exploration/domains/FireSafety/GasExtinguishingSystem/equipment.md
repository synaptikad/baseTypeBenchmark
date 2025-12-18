# Gas Extinguishing System

## Identifiant
- **Code** : GAS-EXT
- **Haystack** : gas-extinguishing-system
- **Brick** : brick:Gas_System

## Description
Système d'extinction automatique utilisant un agent gazeux (inerte ou chimique) pour éteindre un incendie par abaissement de la concentration en oxygène ou inhibition de la réaction de combustion. Utilisé dans les zones où l'eau est proscrite (électronique, archives, data centers).

## Fonction
Détecte et supprime rapidement un incendie dans des locaux sensibles sans endommager les équipements par eau. Le gaz inonde le local protégé et éteint le feu en quelques secondes. Système supervisé avec temporisation d'évacuation avant déclenchement.

## Variantes Courantes
- **IG-541 (Inergen)** : Mélange gaz inertes (N2, Ar, CO2), sans danger pour l'homme
- **IG-55 (Argonite)** : Azote + Argon, totalement inerte
- **FM-200 (HFC-227ea)** : Agent chimique, extinction rapide
- **Novec 1230** : Agent chimique propre, faible impact environnemental
- **CO2** : Dioxyde de carbone, dangereux pour l'homme (évacuation obligatoire)
- **À détection double** : Confirmation par deux détecteurs
- **Avec pré-alarme** : Temporisation évacuation 30-60 secondes

## Caractéristiques Techniques Typiques
- Volume protégé : 10-1000 m³ par zone
- Pression stockage : 200-300 bar (selon agent)
- Temps de décharge : 10-60 secondes
- Concentration : 30-50% selon agent et risque
- Temporisation : 30-60 secondes avant libération
- Supervision : Pression bouteilles, déclenchement, verrouillage
- Certification : EN 15004 (Europe), NFPA 2001 (USA)
- Déclenchement : Automatique (détection) ou manuel

## Localisation Typique
- Data centers et salles serveurs
- Locaux informatiques
- Salles électriques TGBT
- Archives et réserves de musées
- Salles de contrôle
- Laboratoires sensibles
- Zones de stockage batteries

## Relations avec Autres Équipements
- **Alimente** : N/A (système d'extinction)
- **Alimenté par** : Bouteilles haute pression
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI), panneau dédié extinction
- **Déclenché par** : Smoke Detector, Heat Detector (détection croisée)
- **Déclenche** : Arrêt ventilation, fermeture dampers, coupure électrique (option)
- **Communique avec** : Building Management System (BMS)
- **Alarme** : Pré-alarme sonore et visuelle (évacuation)

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 0-2 systèmes (zones critiques)
- Moyen (15 étages, 15000 m²) : 2-8 systèmes
- Grand (30+ étages, 50000 m²) : 10-30 systèmes

## Sources
- EN 15004: Fixed firefighting systems - Gas extinguishing systems
- NFPA 2001: Standard on Clean Agent Fire Extinguishing Systems
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- Règle APSAD R13: Extinction automatique à gaz
