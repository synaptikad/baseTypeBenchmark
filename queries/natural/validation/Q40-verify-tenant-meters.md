# Q40 - Verify Tenant Meters

## Question
> **FR:** Quels compteurs sont associés à un locataire donné ?
>
> **EN:** Which meters are associated with a given tenant?

## Valide / Validates
**[QW9](../write/QW9-meter-assignment.md)** - Meter Assignment (Move-In with meter)

## Cas d'usage / Use case
Validation compteurs, audit facturation, vérification contrat.
Meter validation, billing audit, contract verification.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| Q40_TENANT_ID | string | ID du locataire (différent de QW10 pour idempotence) | `tenant_2` |

## Note technique
Q40 utilise un tenant différent de celui de QW10 (Move-Out) pour garantir des résultats
non-vides lors de répétitions gradient. QW10 supprime les METERS_TENANT pour son tenant.

## Support
| P1 | P2 | M1 | M2 |
|----|----|----|----|
| ✅ | ✅ | ✅ | ✅ |
