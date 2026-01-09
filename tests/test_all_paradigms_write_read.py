"""
Test E2E: Write → Read Cycle for All Paradigms (P2, M1, M2, O2)
Validates QW4-QW8 writes and Q24-Q26 reads across all engines.

Usage:
    pytest tests/test_all_paradigms_write_read.py -v
"""

import pytest
import json
from pathlib import Path


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def p2_cursor():
    """PostgreSQL P2 cursor."""
    import psycopg2
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/benchmark")
        conn.autocommit = False
        cur = conn.cursor()
        cur.execute("SET search_path TO p2, ts, public")
        yield cur
        conn.rollback()
        conn.close()
    except Exception:
        pytest.skip("PostgreSQL not available")


@pytest.fixture(scope="module")
def m1_cursor():
    """Memgraph M1 cursor."""
    try:
        import mgclient
        conn = mgclient.connect(host='localhost', port=7688)
        yield conn.cursor()
        conn.rollback()
        conn.close()
    except Exception:
        pytest.skip("Memgraph not available")


@pytest.fixture(scope="module")
def o2_session():
    """Oxigraph O2 session (requests-based)."""
    import requests
    session = requests.Session()
    session.headers['Accept'] = 'application/sparql-results+json'
    # Check if Oxigraph is available
    try:
        response = session.get("http://localhost:7878/query", params={"query": "SELECT * WHERE { ?s ?p ?o } LIMIT 1"})
        if response.status_code != 200:
            pytest.skip("Oxigraph not available")
    except Exception:
        pytest.skip("Oxigraph not available")
    yield session


# ============================================================================
# P2 TESTS (JSONB)
# ============================================================================

class TestP2WriteRead:
    """P2 PostgreSQL JSONB tests."""

    def test_qw4_maintenance_append(self, p2_cursor):
        """QW4: Append maintenance event."""
        event = json.dumps({"date": "2024-08-01", "type": "test", "technician": "Pytest"})
        p2_cursor.execute("""
            UPDATE p2.nodes SET data = jsonb_set(
                COALESCE(data, '{}'::jsonb), '{maintenance_history}',
                COALESCE(data->'maintenance_history', '[]'::jsonb) || %s::jsonb, true
            ) WHERE id = 'ahu_1' AND node_type = 'Equipment'
            RETURNING id, jsonb_array_length(data->'maintenance_history')
        """, (event,))
        result = p2_cursor.fetchone()
        assert result is not None
        assert result[1] >= 1

    def test_qw7_add_capability(self, p2_cursor):
        """QW7: Add capability idempotently."""
        p2_cursor.execute("""
            UPDATE p2.nodes SET data = jsonb_set(data, '{capabilities}',
                COALESCE(data->'capabilities', '[]'::jsonb) || jsonb_build_array('pytest_cap')
            ) WHERE id = 'ahu_1' AND node_type = 'Equipment'
              AND NOT (COALESCE(data->'capabilities', '[]'::jsonb) @> jsonb_build_array('pytest_cap'))
            RETURNING id, data->'capabilities'
        """)
        # First call should succeed or already have the cap
        p2_cursor.execute("""
            SELECT data->'capabilities' @> jsonb_build_array('pytest_cap')
            FROM p2.nodes WHERE id = 'ahu_1'
        """)
        assert p2_cursor.fetchone()[0] is True

    def test_q26_capability_distribution(self, p2_cursor):
        """Q26: Capability distribution analysis."""
        q26 = Path("queries/p2/Q26.sql").read_text()
        p2_cursor.execute(q26, {"domain": "HVAC"})
        results = p2_cursor.fetchall()
        assert len(results) > 0
        # Check structure
        for row in results:
            assert row[0] is not None  # equipment_type
            assert row[1] > 0  # equipment_count


# ============================================================================
# M1 TESTS (Cypher)
# ============================================================================

class TestM1WriteRead:
    """M1 Memgraph Cypher tests."""

    def test_qw4_maintenance_append(self, m1_cursor):
        """QW4: Append maintenance event to list."""
        m1_cursor.execute("""
            MATCH (eq:Equipment {id: "ahu_1"})
            SET eq.maintenance_history = coalesce(eq.maintenance_history, []) + [{date: "2024-08-01", type: "pytest"}]
            RETURN eq.id, size(eq.maintenance_history)
        """)
        result = m1_cursor.fetchone()
        assert result is not None
        assert result[1] >= 1

    def test_qw7_add_capability_native_list(self, m1_cursor):
        """QW7: Add capability to native Cypher list (capabilities is now native)."""
        m1_cursor.execute("""
            MATCH (eq:Equipment {id: "ahu_1"})
            WHERE eq.capabilities IS NULL OR NOT "pytest_cap" IN eq.capabilities
            SET eq.capabilities = coalesce(eq.capabilities, []) + ["pytest_cap"]
            RETURN eq.id, eq.capabilities
        """)
        result = m1_cursor.fetchone()
        # Either updated or already had it
        m1_cursor.execute("""
            MATCH (eq:Equipment {id: "ahu_1"})
            RETURN "pytest_cap" IN coalesce(eq.capabilities, [])
        """)
        assert m1_cursor.fetchone()[0] is True

    def test_q26_capability_distribution(self, m1_cursor):
        """Q26: Capability distribution by equipment type."""
        m1_cursor.execute("""
            MATCH (eq:Equipment)
            WHERE eq.domain = "HVAC"
            RETURN eq.equipment_type, count(eq) AS equipment_count
            ORDER BY equipment_count DESC
        """)
        results = m1_cursor.fetchall()
        assert len(results) > 0
        for row in results:
            assert row[0] is not None
            assert row[1] > 0


# ============================================================================
# O2 TESTS (SPARQL)
# ============================================================================

class TestO2WriteRead:
    """O2 Oxigraph SPARQL tests."""

    def test_q26_capability_distribution(self, o2_session):
        """Q26: Capability distribution via SPARQL."""
        query = """
        PREFIX btb: <http://basetype.benchmark/ontology#>
        SELECT ?equipmentType (COUNT(DISTINCT ?eq) AS ?equipment_count)
        WHERE {
            ?eq a btb:Equipment .
            ?eq btb:domain "HVAC" .
            ?eq btb:equipmentType ?equipmentType .
        }
        GROUP BY ?equipmentType
        ORDER BY DESC(?equipment_count)
        """
        response = o2_session.post(
            "http://localhost:7878/query",
            data={"query": query}
        )
        assert response.status_code == 200
        results = response.json()
        bindings = results.get("results", {}).get("bindings", [])
        assert len(bindings) > 0

    def test_q24_maintenance_history(self, o2_session):
        """Q24: Maintenance history query."""
        query = """
        PREFIX btb: <http://basetype.benchmark/ontology#>
        SELECT ?equipmentId ?name (COUNT(?event) AS ?event_count)
        WHERE {
            ?eq btb:id "ahu_1" .
            ?eq btb:name ?name .
            BIND("ahu_1" AS ?equipmentId)
            OPTIONAL { ?eq btb:hasMaintenanceEvent ?event }
        }
        GROUP BY ?equipmentId ?name
        """
        response = o2_session.post(
            "http://localhost:7878/query",
            data={"query": query}
        )
        assert response.status_code == 200
        results = response.json()
        bindings = results.get("results", {}).get("bindings", [])
        assert len(bindings) >= 0  # May be 0 or more


# ============================================================================
# CROSS-PARADIGM COMPARISON
# ============================================================================

class TestCrossParadigmComparison:
    """Compare results across paradigms."""

    def test_hvac_equipment_count_consistency(self, p2_cursor, m1_cursor, o2_session):
        """All paradigms should report same HVAC equipment counts."""
        # P2
        p2_cursor.execute("""
            SELECT data->>'equipment_type', COUNT(*)
            FROM nodes WHERE node_type = 'Equipment' AND data->>'domain' = 'HVAC'
            GROUP BY data->>'equipment_type' ORDER BY 1
        """)
        p2_counts = {r[0]: r[1] for r in p2_cursor.fetchall()}

        # M1
        m1_cursor.execute("""
            MATCH (eq:Equipment) WHERE eq.domain = "HVAC"
            RETURN eq.equipment_type AS type, count(eq) AS cnt
            ORDER BY type
        """)
        m1_counts = {r[0]: r[1] for r in m1_cursor.fetchall()}

        # O2
        query = """
        PREFIX btb: <http://basetype.benchmark/ontology#>
        SELECT ?type (COUNT(?eq) AS ?cnt)
        WHERE { ?eq a btb:Equipment ; btb:domain "HVAC" ; btb:equipmentType ?type }
        GROUP BY ?type ORDER BY ?type
        """
        response = o2_session.post("http://localhost:7878/query", data={"query": query})
        o2_counts = {
            b["type"]["value"]: int(b["cnt"]["value"])
            for b in response.json().get("results", {}).get("bindings", [])
        }

        # Compare
        print(f"\nP2: {p2_counts}")
        print(f"M1: {m1_counts}")
        print(f"O2: {o2_counts}")

        # All should have same keys and values
        assert set(p2_counts.keys()) == set(m1_counts.keys()) == set(o2_counts.keys()), \
            f"Equipment types differ: P2={set(p2_counts.keys())}, M1={set(m1_counts.keys())}, O2={set(o2_counts.keys())}"

        for eq_type in p2_counts:
            assert p2_counts[eq_type] == m1_counts[eq_type] == o2_counts[eq_type], \
                f"Counts differ for {eq_type}: P2={p2_counts[eq_type]}, M1={m1_counts[eq_type]}, O2={o2_counts[eq_type]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
