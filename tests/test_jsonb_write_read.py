"""
Test E2E: JSONB Write → Read Cycle
Valide le cycle complet QW4-QW8 → Q24-Q26 pour P2

Usage:
    pytest tests/test_jsonb_write_read.py -v
"""

import pytest
import psycopg2
import json
from pathlib import Path


# Connection string
POSTGRES_DSN = "postgresql://postgres:postgres@localhost:5432/benchmark"
SCHEMA = "p2"


@pytest.fixture(scope="module")
def db_conn():
    """Database connection fixture."""
    conn = psycopg2.connect(POSTGRES_DSN)
    conn.autocommit = False
    yield conn
    conn.rollback()  # Rollback all changes after tests
    conn.close()


@pytest.fixture(scope="module")
def cursor(db_conn):
    """Cursor with p2 schema set."""
    cur = db_conn.cursor()
    cur.execute(f"SET search_path TO {SCHEMA}, ts, public")
    yield cur


class TestQW4MaintenanceEventAppend:
    """Test QW4: Append maintenance event to JSONB array."""

    def test_append_first_event(self, cursor):
        """QW4: Append first maintenance event creates maintenance_history."""
        equipment_id = "eq_ahu_6"
        event = {
            "date": "2024-06-15",
            "type": "preventive",
            "technician": "Tech_A",
            "parts_replaced": ["filter", "belt"],
            "cost_eur": 450.00
        }

        # Execute QW4
        cursor.execute("""
            UPDATE nodes
            SET data = jsonb_set(
                COALESCE(data, '{}'::jsonb),
                '{maintenance_history}',
                COALESCE(data->'maintenance_history', '[]'::jsonb) || %s::jsonb,
                true
            )
            WHERE id = %s AND node_type = 'Equipment'
            RETURNING id, jsonb_array_length(data->'maintenance_history') AS event_count
        """, (json.dumps(event), equipment_id))

        result = cursor.fetchone()
        assert result is not None, "Equipment should exist"
        assert result[0] == equipment_id
        assert result[1] >= 1, "Should have at least 1 event"

    def test_append_second_event(self, cursor):
        """QW4: Append second event increments count."""
        equipment_id = "eq_ahu_6"
        event = {
            "date": "2024-07-20",
            "type": "corrective",
            "technician": "Tech_B",
            "cost_eur": 1200.00
        }

        # Get current count
        cursor.execute("""
            SELECT jsonb_array_length(COALESCE(data->'maintenance_history', '[]'::jsonb))
            FROM nodes WHERE id = %s
        """, (equipment_id,))
        before_count = cursor.fetchone()[0]

        # Execute QW4
        cursor.execute("""
            UPDATE nodes
            SET data = jsonb_set(
                COALESCE(data, '{}'::jsonb),
                '{maintenance_history}',
                COALESCE(data->'maintenance_history', '[]'::jsonb) || %s::jsonb,
                true
            )
            WHERE id = %s AND node_type = 'Equipment'
            RETURNING jsonb_array_length(data->'maintenance_history') AS event_count
        """, (json.dumps(event), equipment_id))

        after_count = cursor.fetchone()[0]
        assert after_count == before_count + 1, "Event count should increment"

    def test_q24_validation(self, cursor):
        """Q24: Validate maintenance history read after QW4 writes."""
        equipment_id = "eq_ahu_6"

        # Read Q24
        cursor.execute("""
            SELECT
                eq.id AS equipment_id,
                eq.name,
                jsonb_array_length(COALESCE(eq.data->'maintenance_history', '[]'::jsonb)) AS event_count,
                eq.data->'maintenance_history'->-1 AS last_event,
                (eq.data->'maintenance_history'->-1)->>'date' AS last_event_date,
                (eq.data->'maintenance_history'->-1)->>'technician' AS last_technician,
                (
                    SELECT COALESCE(SUM((evt->>'cost_eur')::numeric), 0)
                    FROM jsonb_array_elements(eq.data->'maintenance_history') AS evt
                ) AS total_maintenance_cost
            FROM nodes eq
            WHERE eq.id = %s AND eq.node_type = 'Equipment'
        """, (equipment_id,))

        result = cursor.fetchone()
        assert result is not None
        assert result[2] >= 2, "Should have at least 2 events"
        assert result[4] == "2024-07-20", "Last event date should be 2024-07-20"
        assert result[5] == "Tech_B", "Last technician should be Tech_B"
        assert result[6] >= 1650, "Total cost should be >= 1650"


class TestQW5DeepCalibrationUpdate:
    """Test QW5: Update nested calibration fields."""

    def test_update_calibration(self, cursor):
        """QW5: Update calibration preserves other fields."""
        # Find a point with calibration
        cursor.execute("""
            SELECT id FROM nodes
            WHERE node_type = 'Point'
              AND data->'calibration' IS NOT NULL
            LIMIT 1
        """)
        row = cursor.fetchone()
        if not row:
            pytest.skip("No point with calibration found")
        point_id = row[0]

        # Execute QW5
        cursor.execute("""
            UPDATE nodes
            SET data = jsonb_set(
                jsonb_set(
                    jsonb_set(
                        COALESCE(data, '{}'::jsonb),
                        '{calibration,last_date}',
                        to_jsonb(%s::text),
                        true
                    ),
                    '{calibration,next_date}',
                    to_jsonb(%s::text),
                    true
                ),
                '{calibration,technician}',
                to_jsonb(%s::text),
                true
            )
            WHERE id = %s AND node_type = 'Point'
            RETURNING id, data->'calibration' AS updated_calibration
        """, ("2024-06-01", "2025-06-01", "Calibration_Co", point_id))

        result = cursor.fetchone()
        assert result is not None
        calibration = result[1]
        assert calibration["last_date"] == "2024-06-01"
        assert calibration["next_date"] == "2025-06-01"
        assert calibration["technician"] == "Calibration_Co"


class TestQW6MetadataMerge:
    """Test QW6: Merge metadata patch."""

    def test_merge_firmware_update(self, cursor):
        """QW6: Merge preserves existing fields and adds new ones."""
        equipment_id = "eq_ahu_7"
        metadata_patch = {
            "firmware_version": "3.2.1",
            "firmware_update_date": "2024-06-20"
        }

        # Get existing metadata keys before
        cursor.execute("""
            SELECT data->'metadata' FROM nodes WHERE id = %s
        """, (equipment_id,))
        before = cursor.fetchone()[0] or {}
        before_keys = set(before.keys()) if before else set()

        # Execute QW6
        cursor.execute("""
            UPDATE nodes
            SET data = jsonb_set(
                COALESCE(data, '{}'::jsonb),
                '{metadata}',
                COALESCE(data->'metadata', '{}'::jsonb) || %s::jsonb,
                true
            )
            WHERE id = %s AND node_type = 'Equipment'
            RETURNING id, data->'metadata' AS merged_metadata
        """, (json.dumps(metadata_patch), equipment_id))

        result = cursor.fetchone()
        assert result is not None
        merged = result[1]

        # Check new fields added
        assert merged.get("firmware_version") == "3.2.1"
        assert merged.get("firmware_update_date") == "2024-06-20"

        # Check existing fields preserved
        for key in before_keys:
            if key not in metadata_patch:
                assert key in merged, f"Existing key {key} should be preserved"


class TestQW7AddCapability:
    """Test QW7: Conditional capability add."""

    def test_add_new_capability(self, cursor):
        """QW7: Add capability that doesn't exist."""
        equipment_id = "eq_ahu_6"
        new_capability = "demand_control_ventilation"

        # Execute QW7
        cursor.execute("""
            UPDATE nodes
            SET data = jsonb_set(
                data,
                '{capabilities}',
                COALESCE(data->'capabilities', '[]'::jsonb) || jsonb_build_array(%s)
            )
            WHERE id = %s
              AND node_type = 'Equipment'
              AND NOT (COALESCE(data->'capabilities', '[]'::jsonb) @> jsonb_build_array(%s))
            RETURNING id, data->'capabilities' AS updated_capabilities
        """, (new_capability, equipment_id, new_capability))

        result = cursor.fetchone()
        if result:
            caps = result[1]
            assert new_capability in caps

    def test_idempotent_add(self, cursor):
        """QW7: Adding existing capability should not create duplicate."""
        equipment_id = "eq_ahu_7"

        # Get current capabilities
        cursor.execute("""
            SELECT data->'capabilities' FROM nodes WHERE id = %s
        """, (equipment_id,))
        current = cursor.fetchone()[0] or []
        if not current:
            pytest.skip("No capabilities on equipment")

        existing_cap = current[0]
        before_count = len(current)

        # Try to add existing capability
        cursor.execute("""
            UPDATE nodes
            SET data = jsonb_set(
                data,
                '{capabilities}',
                COALESCE(data->'capabilities', '[]'::jsonb) || jsonb_build_array(%s)
            )
            WHERE id = %s
              AND node_type = 'Equipment'
              AND NOT (COALESCE(data->'capabilities', '[]'::jsonb) @> jsonb_build_array(%s))
            RETURNING data->'capabilities'
        """, (existing_cap, equipment_id, existing_cap))

        result = cursor.fetchone()
        # Should return None (no rows updated) because capability exists
        assert result is None, "Should not update when capability exists"

        # Verify count unchanged
        cursor.execute("""
            SELECT jsonb_array_length(data->'capabilities') FROM nodes WHERE id = %s
        """, (equipment_id,))
        after_count = cursor.fetchone()[0]
        assert after_count == before_count, "Capability count should be unchanged"


class TestQW8RemoveMetadataKey:
    """Test QW8: Remove metadata key."""

    def test_remove_key(self, cursor):
        """QW8: Remove key from metadata."""
        # First, add a key to remove
        equipment_id = "eq_ahu_6"
        cursor.execute("""
            UPDATE nodes
            SET data = jsonb_set(
                COALESCE(data, '{}'::jsonb),
                '{metadata}',
                COALESCE(data->'metadata', '{}'::jsonb) || '{"legacy_field": "to_remove"}'::jsonb,
                true
            )
            WHERE id = %s
        """, (equipment_id,))

        # Verify key exists
        cursor.execute("""
            SELECT data->'metadata' ? 'legacy_field' FROM nodes WHERE id = %s
        """, (equipment_id,))
        assert cursor.fetchone()[0], "Key should exist before removal"

        # Execute QW8
        cursor.execute("""
            UPDATE nodes
            SET data = data #- ARRAY['metadata', 'legacy_field']
            WHERE id = %s
              AND data->'metadata' ? 'legacy_field'
            RETURNING id, data->'metadata' AS cleaned_metadata
        """, (equipment_id,))

        result = cursor.fetchone()
        assert result is not None
        assert "legacy_field" not in result[1], "Key should be removed"


class TestQ26CapabilityEvolution:
    """Test Q26: Capability distribution analysis."""

    def test_capability_distribution(self, cursor):
        """Q26: Analyze capability distribution by equipment type."""
        cursor.execute("""
            SELECT
                eq.data->>'equipment_type' AS equipment_type,
                COUNT(*) AS equipment_count,
                ROUND(AVG(jsonb_array_length(COALESCE(eq.data->'capabilities', '[]'::jsonb))), 2) AS avg_capabilities
            FROM nodes eq
            WHERE eq.node_type = 'Equipment'
              AND eq.data->>'domain' = %s
            GROUP BY eq.data->>'equipment_type'
            ORDER BY equipment_count DESC
        """, ("HVAC",))

        results = cursor.fetchall()
        assert len(results) > 0, "Should have HVAC equipment types"

        # Each result should have valid data
        for row in results:
            assert row[0] is not None, "Equipment type should not be null"
            assert row[1] > 0, "Equipment count should be positive"
            assert row[2] >= 0, "Avg capabilities should be non-negative"


class TestQ25AuditTrail:
    """Test Q25: Equipment audit trail combining multiple sources."""

    def test_audit_trail(self, cursor):
        """Q25: Get complete audit trail after QW4/5/6 writes."""
        equipment_id = "eq_ahu_6"

        cursor.execute("""
            SELECT
                eq.id AS equipment_id,
                eq.name,
                eq.data->>'equipment_type' AS equipment_type,
                eq.data->'metadata'->>'firmware_version' AS current_firmware,
                jsonb_array_length(COALESCE(eq.data->'maintenance_history', '[]'::jsonb)) AS maintenance_events,
                CASE
                    WHEN eq.data->'metadata'->>'maintenance_priority' = 'critical' THEN 'CRITICAL'
                    WHEN jsonb_array_length(COALESCE(eq.data->'maintenance_history', '[]'::jsonb)) > 5 THEN 'HIGH_MAINTENANCE'
                    ELSE 'NORMAL'
                END AS health_status
            FROM nodes eq
            WHERE eq.id = %s AND eq.node_type = 'Equipment'
        """, (equipment_id,))

        result = cursor.fetchone()
        assert result is not None
        assert result[0] == equipment_id
        assert result[2] in ("AHU", None)  # Could be AHU or not set
        assert result[4] >= 0  # Maintenance events count


class TestFullWriteReadCycle:
    """Integration test: Full write → read cycle."""

    def test_lifecycle_scenario(self, cursor):
        """Complete lifecycle: QW7 → QW6 → QW4 → Q24/Q25 validation."""
        equipment_id = "eq_vav_15"

        # Step 1: Add capability (QW7)
        cursor.execute("""
            UPDATE nodes
            SET data = jsonb_set(
                data,
                '{capabilities}',
                COALESCE(data->'capabilities', '[]'::jsonb) || jsonb_build_array('smart_control')
            )
            WHERE id = %s
              AND node_type = 'Equipment'
              AND NOT (COALESCE(data->'capabilities', '[]'::jsonb) @> jsonb_build_array('smart_control'))
        """, (equipment_id,))

        # Step 2: Merge metadata (QW6)
        cursor.execute("""
            UPDATE nodes
            SET data = jsonb_set(
                COALESCE(data, '{}'::jsonb),
                '{metadata}',
                COALESCE(data->'metadata', '{}'::jsonb) || %s::jsonb,
                true
            )
            WHERE id = %s AND node_type = 'Equipment'
        """, (json.dumps({"commissioning_date": "2024-06-01"}), equipment_id))

        # Step 3: Add maintenance event (QW4)
        cursor.execute("""
            UPDATE nodes
            SET data = jsonb_set(
                COALESCE(data, '{}'::jsonb),
                '{maintenance_history}',
                COALESCE(data->'maintenance_history', '[]'::jsonb) || %s::jsonb,
                true
            )
            WHERE id = %s AND node_type = 'Equipment'
        """, (json.dumps({"date": "2024-06-15", "type": "commissioning"}), equipment_id))

        # Validation: Read enriched data
        cursor.execute("""
            SELECT
                eq.id,
                eq.data->'capabilities' AS caps,
                eq.data->'metadata'->>'commissioning_date' AS comm_date,
                jsonb_array_length(COALESCE(eq.data->'maintenance_history', '[]'::jsonb)) AS maint_count
            FROM nodes eq
            WHERE eq.id = %s
        """, (equipment_id,))

        result = cursor.fetchone()
        assert result is not None
        assert "smart_control" in (result[1] or []), "Capability should be added"
        assert result[2] == "2024-06-01", "Commissioning date should be set"
        assert result[3] >= 1, "Should have at least 1 maintenance event"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
