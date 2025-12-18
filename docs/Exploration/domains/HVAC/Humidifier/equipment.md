# Humidifier (Humidificateur)

## Identifiant
- **Code** : HUM
- **Haystack** : `humidifier-equip`
- **Brick** : `brick:Humidifier`

## Description
Équipement qui ajoute de l'humidité à l'air en injectant de la vapeur d'eau ou en pulvérisant de l'eau. Installé dans les AHU ou en gaine pour maintenir un taux d'humidité relative confortable et sain (30-60% HR).

## Fonction
Maintenir le taux d'humidité relative de l'air soufflé dans la plage de confort, particulièrement en hiver lorsque l'air extérieur est sec. Éviter l'air trop sec (inconfort, électricité statique, santé).

## Variantes Courantes
- **Humidificateur à vapeur électrique** : Résistances chauffant l'eau (électrode ou résistance immergée)
- **Humidificateur à vapeur gaz** : Chaudière vapeur intégrée
- **Humidificateur à pulvérisation (atomisation)** : Fines gouttelettes d'eau
- **Humidificateur adiabatique** : Évaporation naturelle sur média humide
- **Humidificateur à ultrasons** : Brumisation par vibrations ultrasoniques
- **Humidificateur isotherme** : Vapeur chaude stérile

## Caractéristiques Techniques Typiques
- Capacité : 5 - 200 kg/h de vapeur
- Puissance : 5 - 150 kW (si électrique)
- Type : Vapeur, pulvérisation, adiabatique
- Alimentation eau : Adoucie ou déminéralisée
- Protocoles : BACnet, Modbus, 0-10V
- Points de supervision : capacité (%), consommation eau/énergie, HR zone, alarmes

## Localisation Typique
- Intégré dans AHU
- En gaine après batterie de chauffe
- Locaux nécessitant humidité contrôlée (salles blanches, musées, archives)

## Relations avec Autres Équipements
- **Alimente** : AHU (air humidifié)
- **Alimenté par** : Réseau eau (adoucie), Réseau électrique ou vapeur
- **Contrôlé par** : Hygromètre (capteur HR), DDC Controller, BMS
- **Interagit avec** : Ventilateurs AHU, Vannes, Pompes doseuses

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-3 unités
- Moyen (15 étages) : 3-10 unités
- Grand (30+ étages) : 10-30 unités

## Sources
- Haystack Project - Humidifier Equipment
- Brick Schema - Humidifier Classes
- BACnet Standard - Humidification Control
- ASHRAE Handbook - Humidifiers
