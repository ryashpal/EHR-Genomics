select
distinct
    'T' || '-' || dm.person_id || '-' || dm.visit_occurrence_id || '-WB-' || split_part(replace(description, '''', '"')::json->'windowBefore'::text#>>'{}', ' ', 1) || '-WA-' || split_part(replace(description, '''', '"')::json->'windowAfter'::text#>>'{}', ' ', 1) || '-TT-' || split_part(replace(description, '''', '"')::json->'targetTime'::text#>>'{}', ' ', 1) as id,
    'Patient/' || ('P' || dm.person_id::text) as person_id,
    risk_score as risk_score,
    to_char((to_timestamp(dm.admittime_adm,'DD/MM/YYYY') + (split_part(replace(description, '''', '"')::json->'windowAfter'::text#>>'{}', ' ', 1) || ' day')::interval), 'YYYY-MM-DD') || 'T' || '00:00:00' as occurrence_datetime,
    description as description
from
omop_migration_etl_20240122.risk_scores rs
inner join omop_migration_etl_20240122.data_matrix dm
on left(rs.person_id::text, -2) = dm.person_id::text and left(rs.visit_occurrence_id::text, -2) = dm.visit_occurrence_id::text
;
