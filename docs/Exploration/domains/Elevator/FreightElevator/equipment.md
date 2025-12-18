# Freight Elevator

## Identifiant
- **Code** : FREIGHT_ELEV
- **Haystack** : elev + freight + equip
- **Brick** : brick:Freight_Elevator (subclass of brick:Elevator)

## Description
Monte-charge conçu pour le transport vertical de marchandises, équipements lourds et chariots. Possède une structure renforcée et des dimensions adaptées aux charges importantes. Équipement communicant permettant la supervision et l'optimisation logistique.

## Fonction
Assurer le transport vertical de marchandises, matériel, équipements et chariots entre les niveaux du bâtiment. Facilite les opérations logistiques, de maintenance et d'approvisionnement.

## Variantes Courantes
- **Monte-charge classe A** : Charge accompagnée uniquement
- **Monte-charge classe B** : Marchandises sur chariots avec accompagnateur
- **Monte-charge classe C1** : Chariots + conducteur sur chariot
- **Monte-charge classe C2** : Chariots sans accompagnateur
- **Monte-charge industriel** : Charges très lourdes (5000+ kg)

## Caractéristiques Techniques Typiques
- Capacité : 1000 kg à 10000 kg
- Vitesse : 0.25 m/s à 1 m/s
- Dimensions cabine : Plus grandes que passagers (2.5m x 2.5m typique)
- Portes renforcées : Souvent à deux vantaux, largeur 1.4-2.2m
- Revêtement résistant aux chocs
- Protocoles : BACnet, Modbus TCP, protocoles industriels

## Localisation Typique
- Zones de service et quais de chargement
- Arrière du bâtiment
- Zones logistiques et stockage
- Cuisines et offices (hôtels, hôpitaux)
- Ateliers et zones techniques

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, Emergency Generator
- **Contrôlé par** : Elevator Controller
- **Supervise par** : Elevator Monitoring System, Building Management System
- **Interagit avec** : Hall Call Station, Loading Dock Equipment, Access Control System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 monte-charge
- Moyen (15 étages) : 1-2 monte-charges
- Grand (30+ étages) : 2-4 monte-charges (selon usage industriel/commercial/hôtelier)

## Sources
- Haystack Project 4.0 - Freight elevator tagging
- Brick Schema - Freight_Elevator class
- EN 81-20:2020 - Safety rules for goods lifts
- ISO 8100 - Lifts for goods
