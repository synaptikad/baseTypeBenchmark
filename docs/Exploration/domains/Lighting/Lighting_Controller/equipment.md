# Lighting Controller

## Identifiant
- **Code** : LIGHT_CTRL
- **Haystack** : controller, lighting
- **Brick** : brick:Lighting_System_Controller, brick:Controller

## Description
Dispositif électronique centralisé ou distribué assurant la supervision et le contrôle intelligent d'un ou plusieurs circuits d'éclairage. Ce contrôleur fait le lien entre les capteurs (présence, lumière), les commandes utilisateur, et les actuateurs (luminaires, dimmers), en appliquant des logiques de contrôle programmées.

## Fonction
Coordonner et automatiser le fonctionnement du système d'éclairage selon des scénarios programmés, des horaires, des données de capteurs, et des commandes utilisateur. Assure l'optimisation énergétique, le confort visuel, et l'intégration avec le système de gestion technique du bâtiment (GTB/BMS).

## Variantes Courantes
- **Standalone Lighting Controller** : Contrôleur autonome pour zone unique
- **Networked Lighting Controller** : Contrôleur connecté pour système distribué
- **DALI Master Controller** : Contrôleur maître pour bus DALI (jusqu'à 64 adresses)
- **Multi-Protocol Controller** : Gestion simultanée DALI, 0-10V, DMX, relais
- **Zone Controller** : Gestion d'une zone géographique (étage, département)
- **Building Controller** : Supervision de l'ensemble du bâtiment
- **Wireless Lighting Controller** : Contrôle sans fil (Zigbee, Bluetooth Mesh)
- **PoE Lighting Controller** : Alimenté par Power over Ethernet
- **Panel-Mount Controller** : Format compact pour montage en tableau
- **Cloud-Connected Controller** : Supervision distante via IoT

## Caractéristiques Techniques Typiques
- Processeur: ARM Cortex ou équivalent
- Mémoire: 256MB à 2GB RAM
- Capacité: 64 à 10,000+ points de contrôle
- Zones gérées: 1 à 1,000+ zones
- Protocoles supportés: DALI, DALI-2, DMX512, KNX, BACnet, Modbus, MQTT, Zigbee, Bluetooth
- Interface réseau: Ethernet 10/100/1000, Wi-Fi, LoRaWAN
- Entrées: 4-32 entrées digitales/analogiques (capteurs, boutons)
- Sorties: 4-64 sorties relais/0-10V/PWM
- Alimentation: 24V DC, 48V PoE, ou 120-240V AC
- Stockage: SD card ou mémoire flash (logging, configurations)
- Interface utilisateur: LCD, LED, ou web/app
- Programmation: Logique ladder, scripts, interface graphique
- Temps réel: Horloge RTC avec batterie de sauvegarde
- Sécurité: Authentification, SSL/TLS, isolation réseau

## Localisation Typique
- Locaux techniques et salles serveur
- Tableaux électriques
- Faux-plafond technique
- Salles de contrôle et supervision
- Montage DIN rail dans armoires
- Peut être distribué dans toutes les zones du bâtiment

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, PoE Switch, UPS
- **Contrôlé par** : Building Automation System, SCADA, Cloud Platform
- **Contrôle** : LED Luminaire, Fluorescent Luminaire, Dimmer, Lighting Relay, Scene Controller, Emergency Lighting
- **Reçoit données de** : Occupancy Sensor, Photocell, Connected Switch, Time Schedule
- **Communique avec** : DALI Gateway, Wireless Gateway, BACnet Router, autres contrôleurs

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-5
- Moyen (15 étages) : 5-20
- Grand (30+ étages) : 20-100

## Sources
- Haystack Project - Controller and lighting equipment definitions
- Brick Schema - Lighting System Controller class
- DALI Alliance - DALI control system architecture
- IEC 62386 - DALI standard series
- BACnet standard - ASHRAE 135
- KNX standard - ISO/IEC 14543
