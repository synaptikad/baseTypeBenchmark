# Transformateur de Tension (VT - Voltage Transformer / PT - Potential Transformer)

## Identifiant
- **Code** : TT / VT / PT
- **Haystack** : sensor, voltage-sensor
- **Brick** : Voltage_Sensor

## Description
Capteur de mesure qui transforme une tension élevée (primaire) en une tension proportionnelle faible et normalisée (secondaire 100V ou 110V) utilisable par les appareils de mesure et de protection. Permet la mesure sécurisée de tensions importantes.

## Fonction
Adapter la tension du réseau à un niveau compatible avec les compteurs d'énergie, relais de protection et analyseurs. Assure l'isolation galvanique entre le circuit haute tension et les circuits de mesure/protection basse tension.

## Variantes Courantes
- **TT inductif** : Transformateur classique (MT/BT)
- **TT capacitif** : Diviseur capacitif pour très haute tension
- **TT combiné** : Intègre TC et TT dans un même appareil
- **TT pour comptage** : Classe 0.2 à 0.5
- **TT pour protection** : Classe 3P, 6P

## Caractéristiques Techniques Typiques
- Rapports de transformation : 20000/100V, 15000/100V, 400/100V
- Tension secondaire normalisée : 100V ou 110V
- Classe de précision : 0.2, 0.5, 1 (comptage), 3P, 6P (protection)
- Puissance de précision : 10 à 200 VA
- Isolement : selon tension primaire (BT à HT)
- Montage : Traversant, sur isolateur, encastré

## Localisation Typique
- Cellules MT (poste de transformation)
- TGBT (mesure BT précise)
- Tableaux de comptage
- Zones avec mesure de tension sur réseaux HT/MT

## Relations avec Autres Équipements
- **Mesure** : Tension du réseau électrique
- **Alimente** : Compteurs d'énergie, analyseurs de puissance, relais de protection
- **Associé à** : Jeu de barres, disjoncteurs MT/BT
- **Supervisé via** : Compteurs/analyseurs raccordés

## Quantité Typique par Bâtiment
- Petit (5 étages) : 3-10
- Moyen (15 étages) : 10-30
- Grand (30+ étages) : 30-100

## Sources
- Brick Schema (Voltage_Sensor class)
- Haystack v4 (sensor, voltage tags)
- Standards IEC 61869-3 (transformateurs de tension)
- Documentation technique mesure électrique
