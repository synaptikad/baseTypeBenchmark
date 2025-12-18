# Fire Door Holder

## Identifiant
- **Code** : DOOR-HOLD
- **Haystack** : fire-door-holder
- **Brick** : brick:Magnetic_Door_Holder

## Description
Dispositif électromagnétique maintenant une porte coupe-feu en position ouverte en fonctionnement normal et la libérant automatiquement en cas d'alarme incendie. Permet le confort d'usage tout en garantissant le compartimentage en situation d'urgence.

## Fonction
Maintient les portes coupe-feu ouvertes pour faciliter la circulation normale, puis les libère instantanément sur ordre du système incendie pour rétablir le compartimentage. La porte se ferme alors par son ferme-porte.

## Variantes Courantes
- **Mural** : Fixé au mur, aimant visible
- **Encastré au sol** : Aimant dans le sol, discret
- **Haute force** : 50-200 N selon masse de la porte
- **Avec LED de statut** : Indication visuelle état alimenté
- **Sur batterie locale** : Autonomie en cas de coupure
- **Dual voltage** : 24V DC ou 230V AC

## Caractéristiques Techniques Typiques
- Alimentation : 24V DC (via Fire Alarm Panel)
- Force de retenue : 50-200 N
- Consommation : 0.2-1W en maintien
- Signal de libération : Coupure tension
- Position sécurité : Libéré (sans tension)
- Temps de libération : <1 seconde
- Certification : EN 1155 (Europe), UL 228 (USA)
- Indice de protection : IP40-IP54
- Câblage : 2 fils, supervision possible

## Localisation Typique
- Portes coupe-feu dans circulations
- Sas d'escaliers (maintien temporaire)
- Portes de séparation zones
- Accès locaux techniques
- Portes de cantonnement fumées
- Issues de secours à usage quotidien

## Relations avec Autres Équipements
- **Alimente** : N/A (dispositif de retenue)
- **Alimenté par** : Fire Alarm Panel (alimentation 24V DC)
- **Contrôlé par** : Fire Alarm Panel (FACP/CMSI)
- **Déclenché par** : Smoke Detector, Heat Detector, Manual Call Point, Fire Alarm Panel
- **Agit sur** : Fire Door (libération)
- **Communique avec** : Building Management System (via FACP)

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 15-30 unités
- Moyen (15 étages, 15000 m²) : 60-150 unités
- Grand (30+ étages, 50000 m²) : 200-500 unités

## Sources
- EN 1155: Building hardware - Electrically powered hold-open devices for swing doors
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- NFPA 80: Standard for Fire Doors and Other Opening Protectives
- Règlement de sécurité contre l'incendie
