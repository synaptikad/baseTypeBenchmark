-- QW1: Space Reservation
-- Creates OCCUPIES edge between tenant and space with period
-- Parameters: %(qw1_tenant_id)s, %(qw1_space_id)s, %(qw1_start_date)s, %(qw1_end_date)s

INSERT INTO p1.edges (source_id, target_id, rel_type, start_date, end_date)
VALUES (
    %(qw1_tenant_id)s,
    %(qw1_space_id)s,
    'OCCUPIES',
    %(qw1_start_date)s::date,
    %(qw1_end_date)s::date
);
