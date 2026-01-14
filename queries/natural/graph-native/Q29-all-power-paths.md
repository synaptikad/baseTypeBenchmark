# Q29 - All Power Paths

## Question
> **FR:** Quels sont tous les chemins électriques entre un transformateur et les équipements critiques ?
>
> **EN:** What are all the electrical paths between a transformer and critical equipment?

## Cas d'usage / Use case
Audit résilience électrique, planification maintenance.
Electrical resilience audit, maintenance planning.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| TRANSFORMER_ID | string | ID du transformateur source | `eq_transformer_main` |

## Relations
`FEEDS` (max 10 hops)

## Filtres
- `critical = true`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ⚠️ | ⚠️ | ✅ | ✅ | ❌ |
