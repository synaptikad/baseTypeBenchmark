# Power Distribution Unit (PDU)

## Identifiant
- **Code** : PDU
- **Haystack** : `pdu-equip`
- **Brick** : `brick:Power_Distribution_Unit`

## Description
Unité de distribution électrique qui reçoit l'alimentation d'une source unique et la distribue vers plusieurs sorties (prises). Utilisé principalement dans les centres de données et locaux techniques pour alimenter les équipements informatiques avec monitoring et contrôle avancés.

## Fonction
Distribuer l'alimentation électrique de manière sécurisée et contrôlée aux équipements IT (serveurs, switches, stockage). Fournir des mesures de consommation par prise ou groupe, permettre le contrôle à distance et l'intégration DCIM/BMS.

## Variantes Courantes
- **PDU Basic** : Distribution simple sans monitoring (multiprise)
- **PDU Metered** : Avec affichage local de la consommation
- **PDU Monitored** : Monitoring à distance par SNMP/Modbus/BACnet
- **PDU Switched** : Contrôle on/off à distance par prise
- **PDU Intelligent** : Monitoring par prise + contrôle + alertes
- **PDU Hot-Swap** : Remplacement à chaud sans coupure
- **PDU In-Rack** : Montage vertical dans baie 19"
- **PDU Floor-Standing** : Armoire autonome de distribution

## Caractéristiques Techniques Typiques
- Tension entrée : 230V mono, 400V tri, 480V (US)
- Tension sortie : 230V (EU), 120V/208V (US)
- Puissance : 3 kVA - 60 kVA
- Nombre de sorties : 6 - 48 prises
- Types prises : C13, C19, Schuko, NEMA
- Protocoles : SNMP, Modbus TCP/RTU, BACnet IP, HTTP/REST
- Points de supervision : tension, courant, puissance par prise/phase, énergie, température

## Localisation Typique
- Baies informatiques (montage vertical 0U)
- Salles serveurs
- Centres de données
- Locaux techniques IT

## Relations avec Autres Équipements
- **Alimente** : Serveurs, Switches, Stockage, UPS secondaires
- **Alimenté par** : TGBT, UPS, ATS
- **Contrôlé par** : DCIM, BMS, NMS
- **Interagit avec** : Capteurs environnementaux, Systèmes de refroidissement

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-50 PDU (si salle serveur)
- Moyen (15 étages) : 50-200 PDU
- Grand (30+ étages) : 200-1000+ PDU (si datacenter)

## Sources
- Server Technology - Intelligent PDU Documentation
- Legrand / Raritan - PDU Integration Guides
- Schneider Electric - Data Center PDU
- ASHRAE TC 9.9 - Data Center Guidelines
