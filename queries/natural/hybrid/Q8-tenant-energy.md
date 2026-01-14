# Q8 - Tenant Energy

## Question
> **FR:** Quelle est la consommation totale d'énergie d'un locataire via ses sous-compteurs sur une période ?
>
> **EN:** What is the total energy consumption of a tenant via their sub-meters over a period?

## Cas d'usage / Use case
Facturation énergie, reporting RE2020.
Energy billing, RE2020 reporting.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| TENANT_ID | string | ID d'un locataire | `tenant_acme_corp` |
| DATE_START | timestamp | Début de période | `2024-01-01T00:00:00Z` |
| DATE_END | timestamp | Fin de période | `2024-01-31T23:59:59Z` |

## Relations
`METERS_TENANT`, `HAS_POINT`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
