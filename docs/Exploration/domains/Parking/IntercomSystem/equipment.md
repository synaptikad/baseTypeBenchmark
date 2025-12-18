# Intercom System

## Identifiant
- **Code** : INTERCOM_PARKING
- **Haystack** : N/A
- **Brick** : N/A

## Description
Système d'interphonie permettant communication audio/vidéo bidirectionnelle entre usagers du parking (entrée/sortie, zones internes) et personnel d'assistance (poste central, sécurité). Assistance temps réel pour incidents ou questions.

## Fonction
Communication d'assistance usagers. Permet aux conducteurs de contacter personnel pour aide technique (ticket perdu, paiement refusé), urgence, ou information. Améliore service client et résolution incidents.

## Variantes Courantes
- **Interphone audio** : Communication vocale uniquement
- **Interphone vidéo** : Audio + caméra vers poste central
- **SIP/VoIP** : Basé IP, intégration téléphonie d'entreprise
- **Multi-points** : Système distribué (entrée, sortie, étages, ascenseurs)

## Caractéristiques Techniques Typiques
- Technologie : Audio full-duplex, caméra vidéo optionnelle
- Protocoles : Analogique, SIP/VoIP, protocoles propriétaires
- Bouton d'appel : Illuminé, tactile ou mécanique
- Haut-parleur/micro : Anti-bruit, acoustique optimisée véhicules
- Caméra : 2-5 MP, vision nocturne IR
- Alimentation : 12-24V DC, PoE (version IP)
- Température opération : -30°C à +60°C
- Protection : IP54-IP66, IK10 (anti-vandalisme)

## Localisation Typique
- Entrée parking (station d'accès)
- Sortie parking (station paiement)
- Cages d'ascenseurs parking
- Zones isolées ou étages profonds
- Bornes paiement

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : PoE ou 12-24V DC
- **Contrôlé par** : Parking Management Server, système téléphonie (PABX)
- **Interagit avec** : Entry/Exit Station (intégré), ANPR Camera (contexte visuel), poste central sécurité/accueil

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 2-4 postes (entrée/sortie + ascenseur)
- Moyen (parking 200 places) : 4-8 postes (multiples accès + étages)
- Grand (parking 1000+ places) : 10-20 postes (couverture étendue)

## Sources
- Standards SIP/VoIP (RFC 3261)
- Spécifications interphonie bâtiment
- Documentation systèmes communication parking
