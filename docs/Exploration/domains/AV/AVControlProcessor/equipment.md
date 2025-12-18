# AV Control Processor

## Identifiant
- **Code** : AV_CTRL
- **Haystack** : N/A
- **Brick** : N/A

## Description
Automate de contrôle centralisé pour systèmes audiovisuels. Équipement hautement communicant via IP, série pour orchestration de tous les équipements AV et intégration avec Building Management Systems.

## Fonction
Cerveau du système AV : orchestre displays, projecteurs, matrix switchers, DSP, caméras, éclairage, stores. Exécute des macros automatisées, gère la logique de salle, expose des APIs pour intégration BMS/IoT et permet le contrôle unifié via interfaces utilisateur.

## Variantes Courantes
- **Room Control Processor** : Contrôleur salle unique, 1-2 salles
- **Enterprise Control Processor** : Contrôleur multi-salles, scalable
- **Appliance Controller** : Serveur dédié pour large deployment (10-100+ salles)
- **Cloud-Managed Controller** : Contrôle hybride local/cloud avec remote management
- **Open-Platform Controller** : Linux-based avec développement custom (Python, Node.js)

## Caractéristiques Techniques Typiques
- Ports série : 4-16 ports RS-232/RS-422/RS-485
- Ports réseau : 2-4 GbE Ethernet
- Relais : 8-16 relais pour contrôle électrique (écrans motorisés, éclairage)
- IR : 4-8 sorties infra-rouge
- GPIO : Digital I/O pour capteurs et boutons
- Contrôle : API REST, WebSocket, HTTPS, SSH
- Protocoles : TCP/IP, UDP, Telnet, HTTP, SNMP, BACnet (certains), Modbus
- Intégrations : Calendar (Exchange, Google), Room booking, BMS
- Programmation : Proprietary IDE ou scripting (Python, JavaScript)
- Alimentation : PoE+ ou AC adapter

## Localisation Typique
- Salles de réunion et visioconférence (rack)
- Auditoriums (régie technique)
- Locaux techniques AV centraux
- Faux-plafonds (modèles compacts)

## Relations avec Autres Équipements
- **Contrôle** : Display, Projector, AV Matrix Switcher, Video Conference Codec, DSP, PTZ Camera, Motorized Screen, Lighting Controller
- **Contrôlé par** : Touch Panel Controller, Room Scheduling Display, BMS/BOS
- **Intégré avec** : Calendar systems, Room booking platforms, Occupancy sensors

## Quantité Typique par Bâtiment
- Petit (5 étages) : 3-8 processors
- Moyen (15 étages) : 15-40 processors
- Grand (30+ étages) : 60-150 processors

## Sources
- AV control system architecture documentation
- BACnet and Modbus integration for AV systems
- Commercial building automation protocols
