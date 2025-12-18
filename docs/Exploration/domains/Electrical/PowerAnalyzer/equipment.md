# Analyseur de Puissance (Power Analyzer / Power Quality Analyzer)

## Identifiant
- **Code** : PA
- **Haystack** : power-meter, elec-meter
- **Brick** : Power_Meter, Electrical_Meter

## Description
Appareil de mesure avancé qui analyse en détail la qualité de l'énergie électrique. Au-delà de la simple mesure d'énergie, il enregistre les harmoniques, les déséquilibres, les creux et pointes de tension, les transitoires et autres perturbations électriques. Outil essentiel pour le diagnostic et l'optimisation énergétique.

## Fonction
Analyser finement la qualité de l'énergie électrique et identifier les anomalies, perturbations et sources de gaspillage. Aide au diagnostic des problèmes électriques, à la conformité normative et à l'optimisation du facteur de puissance. Génère des rapports détaillés et des alarmes sur événements.

## Variantes Courantes
- **Analyseur réseau fixe** : Installation permanente sur TGBT
- **Analyseur portable** : Pour campagnes de mesure temporaires
- **Analyseur embarqué** : Intégré dans disjoncteurs intelligents
- **Analyseur multicanal** : Surveillance simultanée de plusieurs circuits

## Caractéristiques Techniques Typiques
- Mesures : THD-U, THD-I jusqu'au rang 63
- Flicker (Pst, Plt)
- Creux et pointes de tension (EN 50160)
- Déséquilibre triphasé
- Puissances harmoniques
- Taux d'échantillonnage : 10-256 échantillons/période
- Communication : Modbus TCP, BACnet IP, IEC 61850, SNMP
- Mémoire événements : horodatage précis des perturbations
- Conformité : IEC 61000-4-30 classe A ou S

## Localisation Typique
- TGBT principal (surveillance globale)
- Départs critiques (datacenters, process sensibles)
- Zones avec équipements sensibles aux perturbations
- En amont d'équipements générateurs d'harmoniques (variateurs)

## Relations avec Autres Équipements
- **Mesure** : Qualité électrique de circuits en aval
- **Connecté à** : TC (Transformateurs de Courant), TT (Transformateurs de Tension)
- **Supervisé par** : Système EMS, plateforme d'analyse énergétique
- **Dialogue avec** : Compensateurs d'énergie réactive, filtres d'harmoniques

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2
- Moyen (15 étages) : 2-5
- Grand (30+ étages) : 5-15

## Sources
- Haystack v4 (power-meter, elec-meter tags)
- Brick Schema (Power_Meter class)
- Standards IEC 61000-4-30 (qualité de l'énergie)
- Standards EN 50160 (caractéristiques tension réseau)
- Documentation technique analyseurs de réseau
