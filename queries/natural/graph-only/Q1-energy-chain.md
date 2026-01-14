# Q1 - Energy Chain

## Question
> **FR:** Depuis un compteur principal (MainMeter), quels sont tous les équipements alimentés dans la chaîne électrique, jusqu'à 10 niveaux de profondeur ?
>
> **EN:** From a main meter, what are all the equipment powered in the electrical chain, up to 10 levels deep?

## Cas d'usage / Use case
Analyse d'impact en cas de coupure électrique.
Impact analysis in case of power outage.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| METER_ID | string | ID d'un MainMeter existant | `meter_main_1` |

## Relations
`FEEDS` (downstream, max 10 hops)

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ | ✅ |
