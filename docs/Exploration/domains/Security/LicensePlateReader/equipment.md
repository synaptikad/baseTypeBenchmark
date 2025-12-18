# License Plate Reader (LPR/ANPR)

## Identifiant
- **Code** : LICENSE_PLATE_READER
- **Haystack** : license-plate-reader
- **Brick** : brick:License_Plate_Recognition_Camera

## Description
Caméra spécialisée avec logiciel de reconnaissance automatique des plaques d'immatriculation (ANPR - Automatic Number Plate Recognition ou LPR - License Plate Reader). Capture, analyse et extrait le numéro de plaque en temps réel pour contrôle d'accès parking, facturation, surveillance, application de règlements.

## Fonction
Capture haute résolution des plaques, reconnaissance optique de caractères (OCR), comparaison avec listes (whitelist/blacklist), commande de barrières automatiques, horodatage et enregistrement des passages, intégration avec systèmes de stationnement et contrôle d'accès.

## Variantes Courantes
- **LPR fixe** : Installation permanente entrée/sortie parking
- **LPR mobile** : Patrouille véhicules (police, contrôle)
- **LPR multi-voies** : Couverture 2-4 voies simultanées
- **LPR avec contexte** : Caméra overview + caméra plaque
- **LPR infrarouge** : Vision nocturne, capture 24/7

## Caractéristiques Techniques Typiques
- Résolution : 2-5 MP (caméra plaque)
- Vitesse capture : Jusqu'à 160 km/h
- Précision : 95-99% jour, 90-95% nuit
- Portée : 1-30m selon installation
- IR illumination : 850nm LEDs
- Déclenchement : Boucle magnétique, radar, vidéo
- Formats plaques : Multiples pays configurables
- Connexion : Ethernet PoE, WiFi
- Stockage : Local SD + serveur centralisé
- API : REST, ONVIF

## Localisation Typique
- Entrées/sorties parkings
- Barrières accès véhicules
- Zones de livraison
- Parkings visiteurs
- Postes de garde
- Contrôle périmètre véhiculé

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : PoE switch, Power supply
- **Contrôlé par** : LPR Server, Parking Management System
- **Commande** : Barrier Gate, Bollard
- **Envoie à** : LPR Server, Access Control, Parking System
- **Intègre avec** : Parking Guidance, Payment System, VMS

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 LPR (parking entrée/sortie)
- Moyen (15 étages) : 2-6 LPR (parkings multiples)
- Grand (30+ étages) : 6-20 LPR (parkings, livraisons, VIP)

## Sources
- ONVIF Profile M (Analytics)
- ISO 14816 - Road Transport ANPR
- Brick Schema - Camera Class
