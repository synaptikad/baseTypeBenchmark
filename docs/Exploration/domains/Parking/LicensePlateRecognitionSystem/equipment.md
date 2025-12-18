# License Plate Recognition System

## Identifiant
- **Code** : LPR_SYSTEM
- **Haystack** : N/A
- **Brick** : N/A

## Description
Système complet de reconnaissance de plaques d'immatriculation combinant caméras ANPR, serveur de traitement OCR, base de données plaques, et logique métier. Système edge-to-cloud pour contrôle d'accès et tarification sans ticket.

## Fonction
Système automatisé complet de gestion parking basé sur plaques. Capture image, reconnaissance OCR temps réel, validation contre base autorisées/interdites, enregistrement entrées/sorties, calcul tarification, et intégration paiement. Alternative système à tickets.

## Variantes Courantes
- **LPR local** : Traitement edge computing dans caméras
- **LPR centralisé** : Serveur central traite flux de toutes caméras
- **LPR cloud** : Traitement et base de données hébergés cloud
- **LPR hybride** : Edge computing + synchronisation cloud

## Caractéristiques Techniques Typiques
- Caméras : 2-5 MP, objectif varifocal, IR illumination
- Serveur : CPU multi-core, GPU optionnel (deep learning)
- Base de données : SQL (PostgreSQL, MySQL), NoSQL (MongoDB)
- Algorithmes : OCR classique ou deep learning (CNN)
- Précision : 95-99% (conditions optimales)
- Vitesse traitement : < 500 ms par véhicule
- Protocoles : HTTP/HTTPS REST API, ONVIF (caméras)
- Intégrations : Système paiement, CRM, ERP, BMS

## Localisation Typique
- Serveur : Datacenter local ou cloud
- Caméras : Entrées, sorties, zones internes parking
- Base de données : Co-localisée avec serveur

## Relations avec Autres Équipements
- **Alimente** : N/A (système logiciel + caméras réseau)
- **Alimenté par** : Infrastructure IT (serveurs, réseau)
- **Contrôlé par** : Parking Management Server (intégration)
- **Interagit avec** : ANPR Camera (capture images), Barrier Gate (commande ouverture), Parking Revenue Control System (facturation), système paiement (CB, mobile)

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 1 serveur + 2-4 caméras ANPR
- Moyen (parking 200 places) : 1 serveur + 4-8 caméras ANPR
- Grand (parking 1000+ places) : Cluster serveurs + 10-30 caméras ANPR

## Sources
- Standards ONVIF (caméras IP)
- Spécifications OCR et deep learning (CNN, YOLO)
- Documentation systèmes LPR/ANPR
- RGPD et réglementations privacy (stockage données)
