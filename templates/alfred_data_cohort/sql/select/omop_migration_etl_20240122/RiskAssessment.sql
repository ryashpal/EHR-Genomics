select
distinct
    'T' || '-' || dm.person_id || '-' || TRIM(SUBSTRING(description, 79, 2)) as id,
    'Patient/' || ('P' || dm.person_id::text) as person_id,
    risk_score as risk_score,
    to_char((to_timestamp(dm.admittime_adm,'DD/MM/YYYY') + interval '1' day), 'YYYY-MM-DD') || 'T' || '00:00:00' as occurrence_datetime,
    description as description
from
omop_migration_etl_20240122.risk_scores rs
inner join omop_migration_etl_20240122.data_matrix dm
on left(rs.person_id::text, -2) = dm.person_id::text and left(rs.visit_occurrence_id::text, -2) = dm.visit_occurrence_id::text
;
