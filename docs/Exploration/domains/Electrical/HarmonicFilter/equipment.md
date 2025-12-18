# Filtre d'Harmoniques (Harmonic Filter / Active Harmonic Filter)

## Identifiant
- **Code** : AHF
- **Haystack** : filter, harmonic-filter
- **Brick** : N/A
- **Extension** : Harmonic_Filter

## Description
Équipement électronique qui réduit ou élimine les harmoniques de courant générées par les charges non-linéaires (variateurs de vitesse, alimentations à découpage, LED, onduleurs). Améliore la qualité de l'énergie et la conformité aux normes de compatibilité électromagnétique.

## Fonction
Filtrer les courants harmoniques polluants créés par l'électronique de puissance pour protéger les équipements sensibles, réduire les pertes, éviter les échauffements anormaux et respecter les normes de qualité d'énergie (EN 50160, IEEE 519).

## Variantes Courantes
- **Filtre passif** : Circuits LC accordés sur harmoniques ciblés (H5, H7)
- **Filtre actif parallèle** : Injection de courants harmoniques opposés
- **Filtre hybride** : Combinaison passif + actif
- **Filtre série** : Protection équipements sensibles
- **Filtre modulaire** : Capacité évolutive par modules

## Caractéristiques Techniques Typiques
- Puissance : 30A à 600A (filtres actifs)
- Harmoniques filtrés : Rang 2 à 50
- Taux de filtrage : 90-98% de réduction THD-I
- Temps de réponse : <50µs (filtres actifs)
- Communication : Modbus TCP, BACnet IP, Ethernet
- Supervision : THD-I, spectres harmoniques, courant compensé
- Montage : Armoire murale ou rack 19"

## Localisation Typique
- TGBT (filtrage global)
- Départs variateurs de vitesse
- Datacenters (nombreuses alimentations à découpage)
- Zones avec forte concentration de LED/électronique
- Tableaux alimentant charges non-linéaires

## Relations avec Autres Équipements
- **Filtre** : Harmoniques de variateurs, onduleurs, LED, alimentations
- **Alimenté par** : TGBT ou tableau divisionnaire
- **Protège** : Transformateurs, moteurs, équipements sensibles
- **Supervisé par** : Analyseur de puissance, système GTB
- **Associé à** : Batteries de condensateurs (détuning)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1
- Moyen (15 étages) : 1-3
- Grand (30+ étages) : 2-6

## Sources
- Standards IEEE 519 (limites harmoniques)
- Standards EN 50160 (qualité tension réseau)
- Documentation technique filtrage actif
- Haystack (filter tags)
