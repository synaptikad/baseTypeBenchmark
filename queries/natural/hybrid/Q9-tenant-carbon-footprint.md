# Q9 - Tenant Carbon Footprint

## Question
> **FR:** Quelle est l'empreinte carbone d'un locataire (énergie × facteur CO2) sur une période ?
>
> **EN:** What is the carbon footprint of a tenant (energy × CO2 factor) over a period?

## Cas d'usage / Use case
Reporting RSE, conformité réglementaire.
CSR reporting, regulatory compliance.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| TENANT_ID | string | ID d'un locataire | `tenant_acme_corp` |
| DATE_START | timestamp | Début de période | `2024-01-01T00:00:00Z` |
| DATE_END | timestamp | Fin de période | `2024-01-31T23:59:59Z` |
| CO2_FACTOR | float | Facteur kgCO2/kWh | `0.0569` |

## Relations
`METERS_TENANT`, `HAS_POINT`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
