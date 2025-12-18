# Machine Room Equipment

## Identifiant
- **Code** : MACH_ROOM
- **Haystack** : elev + machineRoom + equip
- **Brick** : brick:Machine_Room_Equipment (subclass of brick:Equipment)

## Description
Ensemble des équipements mécaniques et électriques situés dans la salle des machines d'ascenseur : moteur de traction, poulies, limiteur de vitesse, armoires électriques. Coeur mécanique du système de levage.

## Fonction
Héberger et protéger tous les équipements de traction, contrôle et sécurité nécessaires au fonctionnement de l'ascenseur. Assurer les conditions environnementales appropriées (température, ventilation).

## Variantes Courantes
- **Machinerie en haut de gaine** : Position classique au-dessus de la gaine
- **Machinerie en bas de gaine** : Pour ascenseurs hydrauliques
- **Machinerie déportée** : Locale technique séparé
- **Machinerie compacte** : Version réduite pour petits espaces
- **Sans local machine (MRL)** : Équipements intégrés dans gaine

## Caractéristiques Techniques Typiques
- Moteur de traction ou groupe hydraulique
- Poulie de traction et poulie de renvoi
- Limiteur de vitesse mécanique
- Armoire de contrôle et puissance
- Ventilation et climatisation
- Éclairage de service
- Monitoring température et vibrations
- Accès sécurisé contrôlé
- Surface : 6-15 m² selon capacité

## Localisation Typique
- Sommet de la gaine d'ascenseur (traction)
- Sous-sol ou rez-de-chaussée (hydraulique)
- Local technique dédié adjacent
- Intégré dans gaine (MRL)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, Emergency Power
- **Contrôlé par** : Elevator Controller
- **Supervise par** : Elevator Monitoring System, BMS
- **Contient** : Elevator Drive, Speed Governor, Control Cabinet
- **Interagit avec** : HVAC (ventilation locale), Access Control

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 locaux machines (1 par ascenseur ou commun)
- Moyen (15 étages) : 2-4 locaux machines (groupés ou séparés)
- Grand (30+ étages) : 4-12 locaux machines (par zones d'ascenseurs)

## Sources
- EN 81-20:2020 - Machine room requirements
- ASME A17.1 - Machinery spaces specifications
- Haystack Project 4.0 - Space and equipment relationship
- Building services mechanical rooms standards
