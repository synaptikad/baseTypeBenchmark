# Intercom

## Identifiant
- **Code** : INTERCOM
- **Haystack** : intercom
- **Brick** : brick:Intercom

## Description
Système de communication audio bidirectionnelle permettant la communication entre un point d'entrée et un poste intérieur (réception, sécurité, bureau). Peut intégrer fonction de déverrouillage de porte à distance. Utilisé pour identification visiteurs, livraisons, contrôle accès manuel.

## Fonction
Communication audio entre extérieur et intérieur, identification des visiteurs, commande de déverrouillage de porte à distance, appel vers postes dédiés ou téléphones IP, journalisation des appels, intégration avec contrôle d'accès.

## Variantes Courantes
- **Intercom audio simple** : Communication voix uniquement
- **Intercom mains-libres** : Sans combiné
- **Intercom IP** : Communication via réseau Ethernet/IP
- **Intercom analogique** : Câblage dédié traditionnel
- **Intercom multi-logements** : Sélection d'appartements
- **Intercom avec afficheur** : Écran pour information texte

## Caractéristiques Techniques Typiques
- Audio : Full-duplex ou half-duplex
- Technologie : IP (SIP/VoIP), analogique 2-fils
- Alimentation : PoE, 12-24V DC
- Bouton d'appel : Résistant vandalisme (IK10)
- Sortie relais : Pour commande serrure
- Protection : IP54-IP65 pour extérieur
- Matériau : Acier inox, aluminium, polycarbonate
- Communication : SIP, TCP/IP, propriétaire
- Intégration : Avec téléphonie IP, Access Control
- Audio : Suppression écho, réduction bruit
- Éclairage : LED pour signalisation et nom

## Localisation Typique
- Entrées principales bâtiments
- Portes de service
- Zones de livraison
- Parkings (bornes)
- Halls d'immeubles résidentiels
- Postes de garde
- Accès sites industriels

## Relations avec Autres Équipements
- **Alimente** : Electric Lock, Electric Strike, Magnetic Lock (via relais)
- **Alimenté par** : PoE switch, Power supply
- **Contrôlé par** : Intercom Master Station, IP PBX (si SIP)
- **Envoie vers** : Master Station, IP Phones, Security Desk
- **Intègre avec** : Access Controller, Video Intercom (upgrade)
- **Interagit avec** : Badge Reader, Barrier Gate

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-5 intercoms
- Moyen (15 étages) : 5-15 intercoms
- Grand (30+ étages) : 15-40 intercoms

## Sources
- SIP Protocol Specifications (IP Intercoms)
- Brick Schema - Intercom Class
- Building Communication Systems Standards
