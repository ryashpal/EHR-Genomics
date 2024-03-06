select
distinct
('O' || '_' || mmt.person_id || '_' || mmt.visit_occurrence_id) as id,
mmt.measurement_concept_id as measurement_concept_id,
mmt.measurement_source_value as measurement_concept_name,
'Patient/' || ('P' || mmt.person_id) as person_id,
'Encounter/' || ('E' || mmt.visit_occurrence_id) as visit_occurrence_id,
to_char(NOW(), 'YYYY-MM-DD') || 'T' || to_char(NOW(), 'HH24:MI:SS') as effective_dateTime
from
omop_migration_etl_20240122.cdm_measurement mmt
where value_as_number <> 'NaN'
and value_as_number is not null
and (mmt.person_id, mmt.visit_occurrence_id) IN (SELECT person_id, visit_occurrence_id FROM omop_migration_etl_20240122.data_matrix)
limit 2
;
