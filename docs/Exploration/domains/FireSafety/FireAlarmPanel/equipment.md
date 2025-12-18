# Fire Alarm Panel

## Identifiant
- **Code** : FACP
- **Haystack** : fire-alarm-panel
- **Brick** : brick:Fire_Alarm_Control_Panel

## Description
Centrale de contrôle et de gestion du système de sécurité incendie (SSI). Surveille tous les détecteurs, gère les alarmes, active les dispositifs d'alerte et pilote les équipements de sécurité incendie. Aussi appelé CMSI (Centralisateur de Mise en Sécurité Incendie) en France.

## Fonction
Assure la supervision complète du système de détection incendie, traite les signaux des détecteurs, déclenche les alarmes sonores et visuelles, active les scénarios de mise en sécurité (désenfumage, compartimentage, évacuation) et communique avec les systèmes de supervision du bâtiment.

## Variantes Courantes
- **Conventionnel** : Gestion par zones (4-32 zones typiques)
- **Adressable** : Identification individuelle de chaque détecteur (250-4000 points)
- **Analogique adressable** : Transmission des valeurs mesurées
- **FACP simple** : Détection et alarme uniquement
- **CMSI (France)** : Inclut les fonctions de mise en sécurité
- **Networked** : Plusieurs panneaux reliés en réseau
- **Avec serveur de gestion** : Interface graphique et historisation

## Caractéristiques Techniques Typiques
- Alimentation : 230V AC + batterie de secours 24-48V DC
- Autonomie batterie : 24-72 heures en veille, 30 min en alarme
- Capacité : 2-4000 points adressables
- Boucles de détection : 1-32 boucles
- Protocoles : Propriétaire, BACnet, Modbus, OPC UA
- Interface : Écran LCD/tactile, clavier, LED de statut
- Journalisation : 10000+ événements
- Certification : EN 54-2, EN 54-4 (Europe), UL 864 (USA)
- Connexions BMS : Contact sec, RS-485, Ethernet

## Localisation Typique
- Local de sécurité incendie (PC sécurité)
- Loge de gardien
- Local technique accessible 24/7
- Salle de contrôle centralisée
- Proximité accès pompiers

## Relations avec Autres Équipements
- **Alimente** : Tous les détecteurs et dispositifs d'alarme (via boucles)
- **Alimenté par** : Alimentation électrique + batterie secours
- **Contrôlé par** : N/A (équipement maître du système incendie)
- **Contrôle** : Smoke Detector, Heat Detector, Manual Call Point, Sounder, Beacon, Fire Damper, Smoke Extraction Fan, Fire Door Holder
- **Communique avec** : Building Management System (BMS), Fire Control Panel Repeater, Emergency Response System

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 1 panneau
- Moyen (15 étages, 15000 m²) : 1-3 panneaux en réseau
- Grand (30+ étages, 50000 m²) : 3-10 panneaux en réseau

## Sources
- EN 54-2: Fire detection and fire alarm systems - Control and indicating equipment
- EN 54-4: Fire detection and fire alarm systems - Power supply equipment
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- NFPA 72: National Fire Alarm and Signaling Code
- Règle APSAD R7: Détection automatique d'incendie
