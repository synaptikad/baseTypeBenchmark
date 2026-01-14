# Q28 - Tenant Impact Chain

## Question
> **FR:** Si un sous-compteur est coupé, quels locataires sont impactés via la chaîne SubMeter → Equipment → Space → Tenant ?
>
> **EN:** If a sub-meter is cut off, which tenants are impacted via the chain SubMeter → Equipment → Space → Tenant?

## Cas d'usage / Use case
Impact coupure électrique sur locataires, facturation, SLA.
Power outage impact on tenants, billing, SLA.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| METER_ID | string | ID du sous-compteur | `eq_submeter_floor2` |

## Relations
`FEEDS`, `SERVES`, `OCCUPIES`

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |
