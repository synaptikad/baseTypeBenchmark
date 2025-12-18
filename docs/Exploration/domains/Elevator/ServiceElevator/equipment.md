# Service Elevator

## Identifiant
- **Code** : SERVICE_ELEV
- **Haystack** : elev + service + equip
- **Brick** : brick:Service_Elevator (subclass of brick:Elevator)

## Description
Ascenseur dédié au personnel de service, maintenance et logistique. Permet l'accès aux zones techniques et de service sans interférer avec la circulation des occupants principaux. Équipement communicant avec gestion d'accès intégrée.

## Fonction
Assurer le transport vertical du personnel de service, équipes de maintenance et petites charges. Accès contrôlé et souvent prioritaire pour les interventions techniques et opérations de nettoyage.

## Variantes Courantes
- **Ascenseur personnel de service** : Principalement pour le personnel (hôtels, hôpitaux)
- **Ascenseur mixte service/marchandises** : Usage combiné
- **Ascenseur de maintenance** : Accès aux zones techniques uniquement
- **Ascenseur sécurité incendie** : Usage pompiers et évacuation

## Caractéristiques Techniques Typiques
- Capacité : 630 kg à 1600 kg
- Vitesse : 0.5 m/s à 2.5 m/s
- Portes renforcées pour passage de chariots
- Contrôle d'accès par badge obligatoire
- Mode prioritaire pour urgences
- Protocoles : BACnet, Modbus, intégration systèmes de sécurité

## Localisation Typique
- Zones de service et back-office
- Près des locaux techniques
- Accès cuisines et buanderies (hôtels)
- Zones de stockage et maintenance
- Accès étages techniques

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, Emergency Generator
- **Contrôlé par** : Elevator Controller
- **Supervise par** : Elevator Monitoring System, Access Control System
- **Interagit avec** : Badge Reader, Emergency Systems, BMS

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 ascenseur
- Moyen (15 étages) : 1-2 ascenseurs de service
- Grand (30+ étages) : 2-6 ascenseurs de service (selon activité)

## Sources
- Haystack Project 4.0 - Service elevator tagging
- Brick Schema - Elevator subclasses
- EN 81-72:2015 - Firefighters lifts
- Building service transportation systems standards
