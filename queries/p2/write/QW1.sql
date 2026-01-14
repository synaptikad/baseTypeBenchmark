-- QW1: Space Reservation
-- Creates OCCUPIES edge with period in properties JSONB
-- Parameters: %(qw1_tenant_id)s, %(qw1_space_id)s, %(qw1_start_date)s, %(qw1_end_date)s

INSERT INTO p2.edges (source_id, target_id, rel_type, properties)
VALUES (
    %(qw1_tenant_id)s,
    %(qw1_space_id)s,
    'OCCUPIES',
    jsonb_build_object(
        'start_date', %(qw1_start_date)s::text,
        'end_date', %(qw1_end_date)s::text
    )
);
