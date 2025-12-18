# Booster Pump

## Identifiant
- **Code** : BOOSTER-PUMP
- **Haystack** : `water`, `booster`, `pump`, `equip`
- **Brick** : `brick:Booster_Pump`

## Description
Pompe de surpression qui augmente la pression de l'eau dans le réseau de distribution pour garantir une pression suffisante aux étages élevés ou aux zones éloignées. Compense les pertes de charge et l'insuffisance de pression du réseau urbain.

## Fonction
Augmenter la pression d'eau pour maintenir une pression de service adéquate (2-4 bars) aux points d'usage situés en hauteur ou éloignés. Démarre automatiquement selon la demande et maintient une pression constante via régulation à vitesse variable.

## Variantes Courantes
- **Pompe simple avec réservoir surpresseur** : Configuration traditionnelle
- **Groupe de surpression multi-pompes** : 2-4 pompes en cascade avec variateurs
- **Pompe inline à vitesse variable** : Compact, régulation pression intégrée
- **Station de relevage/surpression** : Forte HMT pour très grandes hauteurs

## Caractéristiques Techniques Typiques
- Débit nominal : 1-50 m³/h selon taille bâtiment
- Hauteur manométrique : 10-100 mCE
- Puissance : 0.5-30 kW par pompe
- Régulation : Variateur de fréquence avec capteur pression
- Pression de consigne : 3-6 bars
- Redondance : N+1 pompes en cascade

## Localisation Typique
- Sous-sol technique
- Salle des pompes
- Local technique eau
- Chaufferie

## Relations avec Autres Équipements
- **Alimente** : Réseau de distribution interne, étages élevés
- **Alimenté par** : Réseau urbain, Water Tank, Potable Water Pump
- **Contrôlé par** : Contrôleur DDC, régulation pression cascade
- **Associé à** : Pressure Sensor (refoulement), Flow Meter, Pressure Reducing Valve

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 groupe (si pression réseau insuffisante)
- Moyen (15 étages) : 1 groupe de 2-3 pompes (5-15 m³/h)
- Grand (30+ étages) : 2-3 groupes par zone (15-40 m³/h total) étagement vertical

## Sources
- Haystack Project - Pump equipment
- Brick Schema - Booster_Pump class
- ASHRAE Handbook - Plumbing applications
- Water supply and pressure codes
