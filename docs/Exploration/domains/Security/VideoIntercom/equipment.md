# Video Intercom

## Identifiant
- **Code** : VIDEO_INTERCOM
- **Haystack** : video-intercom
- **Brick** : brick:Video_Intercom

## Description
Système de communication bidirectionnelle combinant audio et vidéo, permettant l'identification visuelle des visiteurs avant d'autoriser l'accès. Intègre caméra, micro, haut-parleur, et souvent bouton de déverrouillage. Version moderne utilise IP pour connexion au réseau, permettant visualisation sur smartphones, tablettes, PC.

## Fonction
Communication audio-vidéo avec visiteurs, identification visuelle, enregistrement d'images et vidéo des visiteurs, déverrouillage de porte à distance, intégration avec VMS et contrôle d'accès, notifications sur appareils mobiles, historique des appels.

## Variantes Courantes
- **Video intercom IP** : Connexion réseau, streaming vidéo, SIP/VoIP
- **Video intercom analogique** : Câblage coaxial + audio dédié
- **Multi-logements** : Annuaire, sélection d'appartements
- **Avec reconnaissance faciale** : Authentification biométrique intégrée
- **Avec lecteur RFID** : Double authentification (badge + vidéo)
- **Modular** : Modules combinables (caméra, clavier, lecteur)

## Caractéristiques Techniques Typiques
- Caméra : 2MP minimum, grand angle 170-180°
- Vision nocturne : IR LEDs, Starlight
- Résolution : Full HD 1080p
- Protocoles : SIP, ONVIF, RTSP, propriétaires
- Audio : Full-duplex, suppression écho, réduction bruit
- Alimentation : PoE (802.3af/at), 12-24V DC
- Écran tactile : 7-10 pouces (modèles avec écran intégré)
- Stockage : Carte SD pour snapshots/vidéos
- Protection : IP65, IK10 (vandalisme)
- Relais : Commande serrure intégrée
- Intégrations : VMS, Access Control, SIP PBX, Mobile apps
- Matériau : Acier inox, aluminium

## Localisation Typique
- Entrées principales
- Halls d'immeubles résidentiels
- Entrées de bureaux
- Portes de service
- Zones de livraison
- Parkings souterrains
- Résidences sécurisées
- Copropriétés

## Relations avec Autres Équipements
- **Alimente** : Electric Lock, Electric Strike, Magnetic Lock, Barrier Gate (via relais)
- **Alimenté par** : PoE switch, Power supply
- **Contrôlé par** : Video Intercom Server, SIP Server, Access Control System
- **Envoie vers** : Indoor Stations, Mobile Apps, IP Phones, Security Desk, VMS
- **Enregistre sur** : NVR, VMS, Local SD card
- **Intègre** : Badge Reader, Biometric Reader, Keypad
- **Interagit avec** : Elevator Controller (appel automatique)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-3 video intercoms
- Moyen (15 étages) : 3-10 video intercoms
- Grand (30+ étages) : 10-30 video intercoms

## Sources
- ONVIF Profile T (Door Control)
- SIP Video Intercom Standards
- Brick Schema - Video Intercom Class
