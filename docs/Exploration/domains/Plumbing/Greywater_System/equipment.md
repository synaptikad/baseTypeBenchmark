# Greywater System

## Identifiant
- **Code** : GREYWATER-SYS
- **Haystack** : `greywater`, `reuse`, `system`, `equip`
- **Brick** : `brick:Greywater_System`

## Description
Système de récupération, traitement et réutilisation des eaux grises (lavabos, douches, machines à laver) pour des usages non potables comme les chasses d'eau, l'arrosage ou le nettoyage. Contribue aux économies d'eau et à la durabilité du bâtiment.

## Fonction
Collecter les eaux grises faiblement polluées, les traiter par filtration et désinfection, les stocker dans un réservoir dédié, et les redistribuer vers des usages non potables pour réduire la consommation d'eau potable du bâtiment.

## Variantes Courantes
- **Système simple filtration** : Filtre mécanique + désinfection UV
- **Système avec traitement biologique** : Bioréacteur à membranes (MBR)
- **Système décentralisé** : Par appartement ou étage
- **Système centralisé bâtiment** : Collecte et distribution centralisées

## Caractéristiques Techniques Typiques
- Capacité de traitement : 0.5-50 m³/jour
- Étapes de traitement : Filtration grossière, fine, désinfection UV/chlore
- Stockage tampon : 0.5-10 m³ selon taille bâtiment
- Qualité eau traitée : Conforme réglementations usages non potables
- Pompe de distribution réseau séparé
- Communication : Modbus, BACnet pour monitoring

## Localisation Typique
- Sous-sol technique
- Local technique dédié
- Toiture (stockage après traitement)
- Extérieur bâtiment (enterré)

## Relations avec Autres Équipements
- **Alimente** : WC (chasses), système d'arrosage, nettoyage
- **Alimenté par** : Collecte eaux grises (douches, lavabos), appoint réseau potable
- **Contrôlé par** : Automate dédié, supervision GTB
- **Associé à** : Water Filtration System, UV Disinfection System, Level Sensor, Water Quality Sensor

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 système (si projet HQE/LEED)
- Moyen (15 étages) : 0-1 système centralisé (2-10 m³/jour)
- Grand (30+ étages) : 1-2 systèmes (10-50 m³/jour) ou décentralisés par tours

## Sources
- Haystack Project - Water reuse systems
- Brick Schema - Greywater and water reuse classes
- Green building standards (LEED, BREEAM, HQE)
- Local greywater reuse regulations
