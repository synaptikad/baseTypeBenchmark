# Q30 - Failure Impact Analysis

## Question
> **FR:** Si cet équipement tombe en panne, quels espaces et équipements sont impactés par la cascade de propagation ?
>
> **EN:** If this equipment fails, what spaces and equipment are impacted by the propagation cascade?

## Cas d'usage / Use case
Analyse d'impact, maintenance préventive, gestion des pannes.
Impact analysis, preventive maintenance, failure management.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| EQUIPMENT_ID | string | ID de l'équipement en panne | `eq_mainmeter_4` |

## Relations
`FEEDS`, `SERVES`, `MONITORS`, `LOCATED_IN`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |
