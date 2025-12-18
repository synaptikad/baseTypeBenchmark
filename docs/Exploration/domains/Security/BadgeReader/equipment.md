# Badge Reader

## Identifiant
- **Code** : BADGE_READER
- **Haystack** : badge-reader
- **Brick** : brick:Card_Reader

## Description
Dispositif de lecture de badges d'accès utilisant diverses technologies (RFID, NFC, magnétique, code-barres). Permet l'authentification des utilisateurs pour le contrôle d'accès physique. Communique avec le contrôleur d'accès pour valider les identifiants et déclencher l'ouverture des portes.

## Fonction
Lecture et transmission des identifiants de badges pour authentification et autorisation d'accès. Interface utilisateur pour le système de contrôle d'accès (feedback visuel et sonore).

## Variantes Courantes
- **RFID basse fréquence (125 kHz)** : Technologie standard, portée courte (5-10 cm)
- **RFID haute fréquence (13.56 MHz)** : Technologie plus sécurisée, support NFC
- **Multi-technologie** : Combine plusieurs technologies de lecture (RFID + NFC + QR Code)
- **Biométrique intégré** : Combine lecture de badge et biométrie (empreinte, facial)
- **Mobile credentials** : Lecture via smartphone (BLE, NFC)

## Caractéristiques Techniques Typiques
- Protocole de communication : Wiegand, OSDP, RS-485, TCP/IP
- LED multicolore pour feedback utilisateur
- Buzzer pour signalisation sonore
- Lecture sans contact ou contact
- Portée de lecture : 2-15 cm selon technologie
- Protection IP65 pour usage extérieur
- Alimentation : 12-24V DC, PoE pour versions IP
- Anti-passback, anti-tailgating (selon modèle)

## Localisation Typique
- Entrées principales du bâtiment
- Portes de bureaux sécurisés
- Salles serveurs et locaux techniques
- Parkings (entrées/sorties)
- Ascenseurs (contrôle par étage)
- Tourniquets et sas d'accès
- Zones sensibles (laboratoires, coffres)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Power supply, PoE switch
- **Contrôlé par** : Access Controller, Door Controller
- **Interagit avec** : Electric Lock, Door Contact, Request-to-Exit Sensor

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-30 lecteurs
- Moyen (15 étages) : 50-150 lecteurs
- Grand (30+ étages) : 200-500 lecteurs

## Sources
- OSDP v2 Specification (SIA)
- Wiegand Protocol Documentation
- Brick Schema - Card Reader Class
- Project Haystack v4 - Security Tags
