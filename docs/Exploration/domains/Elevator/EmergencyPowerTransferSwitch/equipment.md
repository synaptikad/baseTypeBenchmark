# Emergency Power Transfer Switch

## Identifiant
- **Code** : EMERG_PWR_SW
- **Haystack** : elev + emergency + power + transfer + switch + equip
- **Brick** : brick:Emergency_Power_Transfer_Switch (subclass of brick:Electrical_Equipment)

## Description
Commutateur automatique basculant l'alimentation électrique des ascenseurs du réseau normal vers le générateur de secours en cas de panne. Assure la continuité de service pour ascenseurs prioritaires (pompiers, service).

## Fonction
Détecter les coupures d'alimentation principale et basculer automatiquement vers le générateur de secours. Prioriser certains ascenseurs (pompiers, évacuation). Rétablir l'alimentation normale une fois le réseau rétabli.

## Variantes Courantes
- **ATS standard** : Basculement automatique simple
- **ATS avec délestage** : Gestion séquentielle de plusieurs ascenseurs
- **ATS prioritaire pompiers** : Ascenseur incendie en priorité absolue
- **ATS avec bypass manuel** : Intervention manuelle possible
- **ATS redondant** : Double système pour criticité maximale

## Caractéristiques Techniques Typiques
- Puissance : 10 kVA à 100 kVA selon nombre d'ascenseurs
- Temps de transfert : <100 ms (sans coupure) à 10s
- Contrôle tension/fréquence réseau
- Contacteurs électromécaniques ou statiques
- Logique de priorité programmable
- Communication : Contact sec, Modbus RTU/TCP
- Supervision état réseau/secours
- Conformité NF C 15-100, NEC

## Localisation Typique
- Local électrique principal
- Tableau général basse tension (TGBT)
- Salle des machines ascenseurs
- Près du groupe électrogène

## Relations avec Autres Équipements
- **Alimente** : Elevator Controllers, Elevator Drives
- **Alimenté par** : Main Electrical Panel (normal), Emergency Generator (secours)
- **Contrôlé par** : Emergency Power System
- **Supervise par** : Building Management System, Power Monitoring System
- **Interagit avec** : Fire Alarm System, UPS

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 commutateur (si générateur présent)
- Moyen (15 étages) : 1-2 commutateurs (secours partiel)
- Grand (30+ étages) : 2-4 commutateurs (par zone + redondance)

## Sources
- NFPA 70 - National Electrical Code (NEC)
- IEC 60947-6-1 - Automatic transfer switching equipment
- EN 81-72:2015 - Firefighters lifts (emergency power)
- Building emergency power systems standards
