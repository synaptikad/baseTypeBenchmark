# Commutateur Automatique de Sources (ATS - Automatic Transfer Switch)

## Identifiant
- **Code** : ATS
- **Haystack** : ats, switch
- **Brick** : N/A
- **Extension** : Transfer_Switch (terme générique)

## Description
Dispositif de commutation automatique qui bascule l'alimentation électrique entre deux sources (réseau principal et source de secours comme un générateur). Détecte les défaillances de la source principale et transfère automatiquement la charge vers la source de secours.

## Fonction
Assurer la continuité d'alimentation des circuits critiques en commutant automatiquement entre le réseau normal et le groupe électrogène. Surveille en permanence la qualité et la présence de la tension sur les deux sources.

## Variantes Courantes
- **ATS 2 positions** : Source 1 OU Source 2 (commutation exclusive)
- **ATS 3 positions** : Source 1, Source 2, ou OFF (isolation)
- **ATS motorisé** : Commutation électromécanique rapide
- **ATS statique** : Commutation électronique ultra-rapide (<10ms)
- **ATS avec couplage** : Permet synchronisation et parallélisme temporaire

## Caractéristiques Techniques Typiques
- Courant nominal : 100A à 4000A
- Tension : 230V/400V triphasé
- Temps de commutation : 100ms à 10 secondes (motorisé), <10ms (statique)
- Nombre de pôles : 3P ou 4P
- Communication : Modbus RTU/TCP, contacts secs, BACnet
- Surveillance : position contacteur, tension sources, défauts
- Sélectivité programmable (priorité, hystérésis)

## Localisation Typique
- En aval du générateur et en amont du TGBT secours
- Local technique électrique principal
- Près du groupe électrogène
- Coffret dédié avec protection IP40-IP55

## Relations avec Autres Équipements
- **Alimente** : TGBT secours, circuits critiques
- **Alimenté par** : Réseau principal (TGBT) ET Générateur
- **Contrôlé par** : Automate générateur, système GTB
- **Commande** : Démarrage/arrêt générateur

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1
- Moyen (15 étages) : 1
- Grand (30+ étages) : 1-3

## Sources
- Standards Haystack (switch, ats tags)
- Documentation technique commutateurs de sources
- Standards BACnet pour dispositifs de commutation
- Normes IEC 60947-6-1 (matériel de connexion automatique)
