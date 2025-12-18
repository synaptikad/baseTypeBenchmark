# Valve (Vanne motorisée)

## Identifiant
- **Code** : VLV / V
- **Haystack** : `valve-equip`
- **Brick** : `brick:Valve`

## Description
Dispositif installé sur une tuyauterie d'eau qui contrôle le débit de fluide hydraulique (eau chaude, eau glacée, eau condenseur). Peut être motorisée pour un contrôle automatique (2 voies ou 3 voies) ou manuelle.

## Fonction
Réguler le débit d'eau dans les circuits hydrauliques pour contrôler la puissance thermique fournie aux équipements terminaux (batteries AHU, FCU, radiateurs) ou la production (chiller, boiler).

## Variantes Courantes
- **Vanne 2 voies** : Régulation de débit (fermeture = arrêt débit)
- **Vanne 3 voies** : Mélange ou dérivation (débit constant)
- **Vanne tout ou rien (on/off)** : Ouverte ou fermée
- **Vanne modulante** : Position variable 0-100%
- **Vanne à siège** : Régulation précise, faible débit
- **Vanne papillon** : Grandes tailles, débit important
- **Vanne à pression différentielle** : Auto-équilibrage hydraulique

## Caractéristiques Techniques Typiques
- Diamètre : DN15 - DN300 (1/2" - 12")
- Kvs : 0.4 - 1,000 m³/h (coefficient de débit)
- Type d'actionneur : Électrique (24VAC, 230VAC), Pneumatique
- Force actionneur : 100 - 3,000 N
- Temps d'ouverture/fermeture : 60 - 240 secondes
- Signal de commande : 0-10V, 4-20mA, contact sec, BACnet/Modbus
- Points de supervision : position (%), débit, alarmes

## Localisation Typique
- Tuyauteries des circuits hydrauliques
- Batteries AHU, FCU
- Départs radiateurs, planchers chauffants
- Entrée/sortie chillers, boilers
- Sous-stations hydrauliques

## Relations avec Autres Équipements
- **Alimente** : AHU, FCU, Radiateurs, Chilled Beams (contrôle débit)
- **Alimenté par** : N/A (actionnée par signal électrique/pneumatique)
- **Contrôlé par** : DDC Controller, PID Loop, BMS
- **Interagit avec** : Pompes, Capteurs de température, Débitmètres

## Quantité Typique par Bâtiment
- Petit (5 étages) : 50-200 vannes
- Moyen (15 étages) : 200-800 vannes
- Grand (30+ étages) : 800-3,000 vannes

## Sources
- Haystack Project - Valve Equipment
- Brick Schema - Valve Classes
- BACnet Standard - Valve Control
- ASHRAE Handbook - Hydronic Systems
