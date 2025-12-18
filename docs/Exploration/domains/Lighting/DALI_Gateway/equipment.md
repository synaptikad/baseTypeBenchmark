# DALI Gateway

## Identifiant
- **Code** : DALI_GW
- **Haystack** : gateway, dali, lighting
- **Brick** : brick:DALI_Gateway, brick:Gateway

## Description
Passerelle de communication convertissant les protocoles de réseau bâtiment (BACnet, Modbus, KNX, Ethernet/IP) vers le protocole DALI (Digital Addressable Lighting Interface) et vice-versa. Permet l'intégration du système d'éclairage DALI dans l'infrastructure de gestion technique du bâtiment et assure l'interopérabilité entre différents systèmes.

## Fonction
Traduire les commandes provenant du système de gestion du bâtiment (BMS/BAS) en instructions DALI pour contrôler les luminaires, ballasts, capteurs et autres dispositifs DALI. Remonter les informations de statut, consommation, et alarmes des équipements DALI vers le système de supervision.

## Variantes Courantes
- **BACnet to DALI Gateway** : Traduction BACnet/IP vers DALI
- **Modbus to DALI Gateway** : Traduction Modbus TCP/RTU vers DALI
- **KNX to DALI Gateway** : Traduction KNX vers DALI
- **Ethernet to DALI Gateway** : Interface IP directe vers DALI
- **Multi-Protocol Gateway** : Support de plusieurs protocoles simultanément
- **Single-Line DALI Gateway** : Gestion d'une ligne DALI (64 adresses max)
- **Multi-Line DALI Gateway** : Gestion de 2 à 16 lignes DALI indépendantes
- **Cloud-Connected DALI Gateway** : Accès distant via cloud/IoT
- **Wireless DALI Gateway** : Interface sans fil (Wi-Fi, Zigbee) vers DALI

## Caractéristiques Techniques Typiques
- Protocoles superviseur: BACnet/IP, BACnet MS/TP, Modbus TCP, Modbus RTU, KNX, MQTT, HTTP/REST
- Protocole terrain: DALI, DALI-2 (IEC 62386)
- Lignes DALI: 1 à 16 lignes indépendantes
- Adresses par ligne: 64 adresses DALI maximum
- Groupes DALI: 16 groupes par ligne
- Scènes DALI: 16 scènes par ligne
- Alimentation: 24V DC, 48V PoE, ou 120-240V AC
- Interface réseau: Ethernet 10/100, Wi-Fi optionnel
- Interface DALI: Sortie isolée galvaniquement
- Tension ligne DALI: 16V DC (±6.5V)
- Courant ligne DALI: 250mA max
- Mémoire: Configuration persistante (flash)
- Interface utilisateur: Web, Modbus registers, BACnet objects
- Mise à jour firmware: OTA (Over-The-Air)
- Montage: Rail DIN, mural, ou rack
- Protection: Court-circuit, polarité inversée

## Localisation Typique
- Locaux techniques et salles serveur
- Tableaux électriques
- Armoires de communication
- Faux-plafond technique
- Salles de contrôle
- Montage DIN rail dans armoires

## Relations avec Autres Équipements
- **Alimente** : Dispositifs DALI (fournit tension ligne DALI 16V)
- **Alimenté par** : Electrical Panel, PoE Switch, Power Supply
- **Contrôlé par** : Building Automation System, Lighting Controller, SCADA
- **Contrôle** : LED Luminaire (DALI), Fluorescent Luminaire (DALI), DALI Ballast, DALI Dimmer, DALI Sensor
- **Communique avec** : BACnet Network, Modbus Network, KNX Bus, Ethernet Network

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-5
- Moyen (15 étages) : 5-20
- Grand (30+ étages) : 20-100

## Sources
- IEC 62386 - Digital addressable lighting interface (DALI) standard series
- DALI Alliance - Gateway and integration specifications
- BACnet standard - ASHRAE 135
- Modbus specification
- KNX standard - ISO/IEC 14543
- Building automation integration best practices
