# QW5 - Deep Calibration Update

## Question
> **FR:** Comment mettre à jour les informations de calibration d'un point de mesure (date, technicien, certificat) ?
>
> **EN:** How to update calibration information for a measurement point (date, technician, certificate)?

## Validé par / Validated by
**[Q25](../validation/Q25-equipment-audit-trail.md)** - Equipment Audit Trail

## Cas d'usage / Use case
Métrologie, conformité, traçabilité calibration.
Metrology, compliance, calibration traceability.

## Paramètres / Parameters
| Nom | Type | Description | Exemple |
|-----|------|-------------|---------|
| POINT_ID | string | ID du point de mesure | `point_temp_101` |
| CALIBRATION | json | Objet calibration | `{"last_date": "2024-06-01", "next_date": "2025-06-01", "technician": "Jane", "certificate": "CAL-2024-001"}` |

## Support
| P1 | P2 | M1 | M2 | O2 |
|----|----|----|----|----|
| ❌ | ✅ | ✅ | ✅ | ⚠️ |
