# Air Compressor (Compresseur d'air)

## Identifiant
- **Code** : COMP / AC
- **Haystack** : `airCompressor-equip`
- **Brick** : `brick:Air_Compressor`

## Description
Équipement qui comprime l'air atmosphérique pour produire de l'air comprimé utilisé dans les systèmes pneumatiques du bâtiment : actionneurs de registres et vannes pneumatiques, outils, processus industriels, ou systèmes de contrôle HVAC.

## Fonction
Produire et maintenir une pression d'air comprimé constante pour alimenter les équipements pneumatiques du bâtiment. Assurer la qualité de l'air (filtration, séchage) selon les applications.

## Variantes Courantes
- **Compresseur à piston** : Petites puissances, intermittent
- **Compresseur à vis** : Moyennes/grandes puissances, continu
- **Compresseur scroll** : Silencieux, air propre
- **Compresseur centrifuge** : Très grandes puissances
- **Compresseur oil-free** : Applications médicales, alimentaires
- **Compresseur avec sécheur intégré** : Air sec directement

## Caractéristiques Techniques Typiques
- Débit : 10 - 5,000 l/min (FAD)
- Pression : 6 - 13 bar
- Puissance : 1 - 500 kW
- Type : Piston, vis, scroll, centrifuge
- Protocoles : BACnet, Modbus, Profibus
- Points de supervision : pression, débit, température, heures fonctionnement, alarmes

## Localisation Typique
- Local technique dédié (compresseur)
- Sous-sol ou toiture
- Proximité des utilisateurs pneumatiques

## Relations avec Autres Équipements
- **Alimente** : Réseau air comprimé, Actionneurs pneumatiques, Dampers, Vannes
- **Alimenté par** : Réseau électrique
- **Contrôlé par** : Contrôleur intégré, BMS, API
- **Interagit avec** : Sécheur d'air, Réservoir tampon, Filtres, Purgeurs

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 unité (si pneumatique)
- Moyen (15 étages) : 1-2 unités
- Grand (30+ étages) : 2-5 unités (redondance)

## Sources
- Atlas Copco - Air Compressor Systems
- Kaeser - Compressed Air Technology
- Project Haystack - Compressor Equipment
- ISO 8573 - Compressed Air Quality
