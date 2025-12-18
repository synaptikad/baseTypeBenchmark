# Rack Power Panel (RPP)

## Identifiant
- **Code** : PWR-RPP
- **Haystack** : N/A
- **Brick** : N/A

## Description
Panneau de distribution électrique monté en rack fournissant alimentation depuis source principale (UPS/secteur) vers multiples PDU. Intègre protection par disjoncteurs et parfois monitoring de la distribution par rack ou rangée.

## Fonction
Centralise la distribution électrique pour un rack ou groupe de racks avec protection individuelle par circuit. Point de jonction entre distribution électrique datacenter et PDU des racks. Peut intégrer monitoring de courant, tension et énergie par branche.

## Variantes Courantes
- **Basic RPP** : Distribution passive avec disjoncteurs uniquement
- **Monitored RPP** : Avec mesure de courant/puissance par circuit
- **Busway Tap-off** : Connexion directe depuis busbar overhead
- **Remote Power Panel (RPP)** : Panneau déporté desservant rangée de racks
- **Floor PDU** : Grande capacité alimentant multiple racks (50-400A)

## Caractéristiques Techniques Typiques
- Formats : 2U-6U rack-mount ou armoire murale/floor standalone
- Entrée : triphasé 400V 32A-125A (distribution principale)
- Sorties : 4 à 24+ circuits protégés par disjoncteurs
- Protection : disjoncteurs magnéto-thermiques 16A-32A par circuit
- Monitoring optionnel : ampérage par phase, déséquilibre de charge
- Interface (si intelligent) : SNMP, Modbus TCP, contacts secs
- Capacité typique : 10-50 kW distribution totale

## Localisation Typique
- En bas ou milieu des racks serveurs
- En fin de rangée (hot aisle/cold aisle)
- Sous plancher technique (below raised floor)
- Salle électrique adjacente au datacenter

## Relations avec Autres Équipements
- **Alimente** : PDU des racks
- **Alimenté par** : UPS, STS (Static Transfer Switch), distribution électrique bâtiment
- **Contrôlé par** : DCIM, BMS, monitoring électrique
- **Protège** : Circuits individuels contre surcharge
- **Mesure pour** : Équilibrage de charge triphasée, capacity planning

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-5 RPP (alimentation redondée petite salle serveur)
- Moyen (15 étages) : 10-30 RPP (1 par rangée de racks ou plus)
- Grand (30+ étages) : 30-100+ RPP (datacenter haute densité)

## Sources
- Datacenter power distribution architecture
- IEC 61439 (Low-voltage switchgear assemblies)
- Rack power distribution best practices
- Three-phase power monitoring
