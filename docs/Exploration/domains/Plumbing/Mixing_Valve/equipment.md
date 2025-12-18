# Mixing Valve

## Identifiant
- **Code** : MIX-VALVE
- **Haystack** : `water`, `mixing`, `valve`, `equip`
- **Brick** : `brick:Mixing_Valve`

## Description
Vanne mélangeuse thermostatique qui mélange automatiquement l'eau chaude et l'eau froide pour délivrer une température d'eau stabilisée à la consigne. Protection contre les brûlures et optimisation du confort.

## Fonction
Mélanger l'eau chaude sanitaire du ballon (55-60°C) avec de l'eau froide pour obtenir une température de distribution sécurisée (38-45°C) aux points d'usage. Compense les variations de pression et température pour stabilité parfaite.

## Variantes Courantes
- **Mitigeur thermostatique centralisé** : Mélange en tête de distribution
- **Mitigeur thermostatique de sécurité** : Anti-brûlure (classe AA selon EN1287)
- **Vanne 3 voies motorisée mélangeuse** : Contrôle DDC avec sonde température
- **Mitigeur point d'usage** : Local douche/baignoire, robinetterie

## Caractéristiques Techniques Typiques
- Diamètre : DN15 à DN50
- Température d'entrée chaude : 50-80°C
- Température sortie réglable : 30-60°C
- Précision régulation : ±2°C (thermostatique), ±0.5°C (motorisé)
- Protection anti-brûlure : Coupure si absence eau froide
- Débit : Fonction diamètre et Kv

## Localisation Typique
- Départ réseau ECS (mélange centralisé)
- Chaufferie à proximité DHW Tank
- Gaine technique étage (distribution locale)
- Salles de bains (point d'usage)

## Relations avec Autres Équipements
- **Alimente** : Réseau de distribution ECS, points d'usage
- **Alimenté par** : DHW Tank (eau chaude), réseau eau froide
- **Contrôlé par** : Thermostat intégré ou régulation DDC
- **Associé à** : Temperature Sensor (sortie), clapet anti-retour

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-3 valves (mélange centralisé + circuits)
- Moyen (15 étages) : 3-10 valves (par zone de distribution)
- Grand (30+ étages) : 10-30 valves (distribution multi-zones + points critiques)

## Sources
- Haystack Project - Mixing valve equipment
- Brick Schema - Mixing_Valve class
- EN 1287 - Thermostatic mixing valves standard
- Anti-scald and plumbing safety codes
