# ANPR/LPR Camera

## Identifiant
- **Code** : ANPR_CAMERA
- **Haystack** : N/A
- **Brick** : N/A

## Description
Caméra de reconnaissance automatique de plaques d'immatriculation (ANPR - Automatic Number Plate Recognition / LPR - License Plate Recognition). Capture et analyse les plaques véhicules pour contrôle d'accès sans barrière ou avec validation automatique.

## Fonction
Lecture optique et reconnaissance automatique des plaques d'immatriculation en temps réel. Permet l'accès automatisé (liste blanche/noire), la tarification basée sur plaque, et la traçabilité des mouvements véhicules.

## Variantes Courantes
- **ANPR entrée/sortie** : Positionnée aux accès, contrôle flux
- **ANPR contexte** : Vue large avec plaque + véhicule complet
- **ANPR infrarouge** : Éclairage IR pour vision nocturne
- **ANPR multi-voies** : Couvre 2-3 voies simultanément

## Caractéristiques Techniques Typiques
- Résolution : 2-5 MP (minimum pour OCR fiable)
- Vitesse capture : Jusqu'à 200 km/h (selon installation)
- Précision reconnaissance : 95-99% (conditions optimales)
- Éclairage : IR 850 nm ou flash LED
- Objectif : Varifocal 5-50mm (ajustable)
- Protocoles : ONVIF, RTSP, HTTP API, Modbus TCP
- Traitement : Embarqué (edge computing) ou serveur distant
- Température opération : -40°C à +60°C
- Protection : IP66/IP67

## Localisation Typique
- Entrée principale parking (avant barrière)
- Sortie parking (validation sortie)
- Rampes d'accès inter-niveaux
- Zones contrôlées (VIP, abonnés)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : PoE+ ou 12-24V DC
- **Contrôlé par** : Parking Management Server, LPR Server
- **Interagit avec** : Barrier Gate (commande ouverture), Entry/Exit Station, Parking Revenue Control System, base de données plaques autorisées

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 2-4 caméras (entrée/sortie + contexte)
- Moyen (parking 200 places) : 4-8 caméras (multiples accès)
- Grand (parking 1000+ places) : 10-20 caméras (accès multiples + zones)

## Sources
- Standards ONVIF (IP camera protocols)
- Documentation systèmes ANPR/LPR
- Spécifications traitement image OCR
- Réglementations RGPD/privacy (stockage données)
