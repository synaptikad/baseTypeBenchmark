# Parafoudre / Parasurtenseur (Surge Protective Device - SPD)

## Identifiant
- **Code** : SPD
- **Haystack** : surge-protector
- **Brick** : N/A
- **Extension** : Surge_Protector

## Description
Dispositif de protection installé dans les tableaux électriques qui limite les surtensions transitoires d'origine atmosphérique (foudre) ou de manoeuvre. Protège les équipements sensibles contre les destructions et dysfonctionnements causés par les pics de tension.

## Fonction
Écouler à la terre les courants de surtension et limiter l'amplitude des surtensions à un niveau supportable par les équipements. Protection indispensable pour les installations électroniques sensibles (informatique, automatismes, télécommunications).

## Variantes Courantes
- **SPD Type 1** : Protection tête d'installation (foudre direct)
- **SPD Type 2** : Protection tableaux divisionnaires (foudre indirect)
- **SPD Type 3** : Protection terminale équipements sensibles
- **SPD avec contact de défaut** : Signalisation défaut à distance
- **SPD débrochable** : Remplacement sans coupure

## Caractéristiques Techniques Typiques
- Tension maximale : Un = 230/400V
- Courant de décharge : Imax 40-100kA (Type 1), 20-40kA (Type 2)
- Niveau de protection : Up < 1.5kV (Type 2), < 2.5kV (Type 1)
- Technologie : Varistances (MOV), éclateurs à gaz, diodes
- Signalisation : Contact NO/NF (défaut), voyant visuel
- Communication : Contact sec vers GTB
- Montage : Rail DIN modulaire (1 à 4 modules)

## Localisation Typique
- TGBT (Type 1 en tête)
- Tableaux divisionnaires (Type 2)
- Coffrets terminaux (Type 3)
- Armoires informatiques et télécoms
- Tableaux alimentant équipements sensibles

## Relations avec Autres Équipements
- **Protège** : Tous équipements électroniques en aval
- **Installé dans** : Tableaux électriques à tous niveaux
- **Signale vers** : GTB (défaut parafoudre)
- **Coordonné avec** : Autres SPD (cascade Type 1-2-3)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-15
- Moyen (15 étages) : 15-40
- Grand (30+ étages) : 40-100

## Sources
- Standards IEC 61643-11 (parafoudres BT)
- Guide UTE C 15-443 (choix et installation SPD)
- Norme NF C 15-100 (installations BT)
- Documentation technique protection foudre
