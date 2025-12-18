# Magnetic Lock (Electromagnetic Lock)

## Identifiant
- **Code** : MAG_LOCK
- **Haystack** : mag-lock
- **Brick** : brick:Magnetic_Lock

## Description
Dispositif de verrouillage électromagnétique basé sur l'attraction entre un électro-aimant fixé sur le dormant et une plaque d'armature métallique fixée sur la porte. Maintient la porte fermée par force magnétique (250-600 kg de force). Intrinsèquement fail-safe (déverrouille en cas de coupure électrique). Simple, fiable, sans pièces mobiles.

## Fonction
Verrouillage magnétique de porte, maintien force élevée (anti-effraction), déverrouillage instantané sur commande ou coupure, conformité sécurité incendie (fail-safe), surveillance état (bond sensor), pas de clé mécanique.

## Variantes Courantes
- **Maglock standard** : Montage en applique, 300kg
- **Maglock haute tenue** : 600-1200kg pour portes lourdes
- **Maglock encastré** : Discret, intégré dans dormant
- **Maglock double** : Pour portes doubles battantes
- **Maglock extérieur** : Protection IP65
- **Shear lock** : Force de cisaillement (portes coulissantes)

## Caractéristiques Techniques Typiques
- Force de maintien : 250-1200 kg (550-2600 lbs)
- Tension : 12-24V DC
- Consommation : 300-600mA selon force
- Type : Toujours fail-safe (sécurité incendie)
- Temps réponse : Instantané (<10ms)
- Bond sensor : Détection armature présente (porte fermée)
- Résiduel magnétisme : <2% après coupure
- Protection : IP20-IP68 selon modèle
- Certification : EN 1155, UL Listed
- Montage : En applique (surface mount)
- Matériau : Aluminium anodisé, inox

## Localisation Typique
- Issues de secours
- Portes coupe-feu
- Portes vitrées
- Portes d'accès général
- Sas de sécurité
- Zones contrôlées
- Halls et circulations
- Portes double battants

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Door Controller, Access Controller, Power supply (avec backup batterie)
- **Contrôlé par** : Door Controller, Access Controller
- **Reçoit commande de** : Badge Reader (via contrôleur), Request-to-Exit, Emergency Release, Fire Alarm
- **Retour état** : Bond Sensor (armature contact)
- **Supervision** : Door Contact
- **Requis avec** : Request-to-Exit Sensor (sortie), Emergency Break Glass

## Quantité Typique par Bâtiment
- Petit (5 étages) : 15-40 maglocks
- Moyen (15 étages) : 60-180 maglocks
- Grand (30+ étages) : 200-600 maglocks

## Sources
- EN 1155 - Electrically Powered Hold-Open Devices
- UL 1034 - Burglary-Resistant Electric Locking Mechanisms
- Brick Schema - Magnetic Lock Class
- Fire Safety Codes (Fail-Safe Requirements)
