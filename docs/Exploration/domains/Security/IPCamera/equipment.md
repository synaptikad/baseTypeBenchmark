# IP Camera

## Identifiant
- **Code** : IP_CAMERA
- **Haystack** : camera-ip
- **Brick** : brick:Camera

## Description
Caméra de surveillance numérique connectée au réseau IP, capable de capturer, encoder et transmettre des flux vidéo via le réseau. Supporte généralement des protocoles standardisés (ONVIF, RTSP) pour intégration avec les systèmes de gestion vidéo. Peut intégrer des fonctions d'analyse vidéo embarquées (edge analytics).

## Fonction
Capture vidéo en temps réel, compression et streaming réseau, enregistrement local (carte SD), détection de mouvement, analytics vidéo embarquée (comptage, détection d'intrusion, reconnaissance), gestion d'événements, audio bidirectionnel.

## Variantes Courantes
- **Fixe** : Positionnement fixe, champ de vision déterminé
- **Dôme fixe** : Format discret, angle de vue fixe
- **PTZ (Pan-Tilt-Zoom)** : Motorisée, contrôle orientation et zoom
- **Multi-capteurs** : 2 à 4 capteurs pour couverture panoramique
- **Fisheye** : Vision 180° ou 360°, dewarping logiciel
- **Bullet** : Format cylindrique, souvent extérieur
- **Thermique** : Détection par infrarouge, surveillance périmétrique
- **ANPR (Automatic Number Plate Recognition)** : Spécialisée lecture de plaques

## Caractéristiques Techniques Typiques
- Résolution : 2MP à 12MP (Full HD à 4K et au-delà)
- Frame rate : 15-60 fps
- Compression : H.264, H.265 (HEVC), MJPEG
- Protocoles : ONVIF Profile S/T/G, RTSP, HTTP
- Alimentation : PoE (802.3af/at/bt), 12-24V DC
- Stockage : Carte SD/microSD (jusqu'à 512GB-1TB)
- Vision nocturne : IR 20-100m, Starlight, ColorVu
- Protection : IP66, IP67, IK10 (vandalisme)
- Analytics embarquée : Motion detection, line crossing, intrusion, loitering
- Audio : Microphone intégré, sortie audio, bidirectionnel

## Localisation Typique
- Entrées et sorties du bâtiment
- Halls et couloirs principaux
- Parkings (intérieurs et extérieurs)
- Périmètre extérieur
- Ascenseurs
- Espaces communs
- Zones sensibles et restreintes
- Escaliers de secours
- Quais de chargement

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : PoE switch, Power supply, UPS
- **Contrôlé par** : Video Management System, NVR
- **Envoie à** : NVR, Video Management Server, Video Analytics Server
- **Interagit avec** : Access Controller (event triggering), Alarm Panel, Lighting Controller

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-50 caméras
- Moyen (15 étages) : 100-300 caméras
- Grand (30+ étages) : 500-1500 caméras

## Sources
- ONVIF Core Specification
- ONVIF Profile S/T/G Documentation
- Brick Schema - Camera Class
- Project Haystack - Camera Equipment
