# Transformateur MT/BT (Medium to Low Voltage Transformer)

## Identifiant
- **Code** : TRANSFO
- **Haystack** : transformer, elec-input
- **Brick** : Transformer

## Description
Équipement qui transforme l'électricité moyenne tension (généralement 20kV) en basse tension (400V) pour alimenter le bâtiment. Les transformateurs modernes intègrent des capteurs de température, de charge et de diagnostic pour supervision à distance.

## Fonction
Convertir l'énergie électrique moyenne tension du réseau public en basse tension utilisable par les équipements du bâtiment. Assure également l'isolation galvanique entre le réseau MT et l'installation BT.

## Variantes Courantes
- **Transformateur sec** : Isolation résine, sans huile (usage intérieur)
- **Transformateur immergé** : Refroidissement par huile diélectrique
- **Transformateur de secours** : Redondance N+1 pour continuité de service
- **Transformateur variable** : Avec changeur de prise en charge

## Caractéristiques Techniques Typiques
- Tension primaire : 10kV, 15kV ou 20kV
- Tension secondaire : 230V/400V
- Puissance : 100 kVA à 2500 kVA (bâtiments tertiaires)
- Rendement : 96-99%
- Communication : Relais de protection Modbus/IEC 61850
- Sondes de température (huile/enroulements)
- Détection gaz dissous (transformateurs immergés)

## Localisation Typique
- Poste de transformation dédié (local MT)
- Sous-sol technique avec ventilation
- À proximité du point de livraison énergétique
- Zone sécurisée avec accès restreint

## Relations avec Autres Équipements
- **Alimente** : TGBT principal
- **Alimenté par** : Réseau moyenne tension public
- **Contrôlé par** : Relais de protection, système SCADA, automate GTB
- **Associé à** : Cellules MT, disjoncteur MT, compteur énergie

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1
- Moyen (15 étages) : 1-2
- Grand (30+ étages) : 2-4

## Sources
- Brick Schema (Transformer class)
- Haystack v4 (transformer, elec tags)
- Standards IEC 61850 pour communication transformateurs
- Documentation technique postes de transformation
