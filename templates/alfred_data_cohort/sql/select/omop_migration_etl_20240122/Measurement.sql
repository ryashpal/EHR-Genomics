with stg1 as (
    select
    distinct
    ('M' || mmt.measurement_id) as id,
    mmt.measurement_concept_id as measurement_concept_id,
    mmt.measurement_source_value as measurement_concept_name,
    'Patient/' || ('P' || mmt.person_id) as person_id,
    'Encounter/' || ('E' || mmt.visit_occurrence_id) as visit_occurrence_id,
    to_char(mmt.measurement_datetime, 'YYYY-MM-DD') || 'T' || to_char(mmt.measurement_datetime, 'HH24:MI:SS') as measurement_datetime,
    '' as unit_concept_id,
    mmt.unit_source_value as unit_concept_code,
    mmt.value_as_number as value_as_number
    from
    omop_migration_etl_20240122.cdm_measurement mmt
    inner join (select * from omop_migration_etl_20240122.cohort_saur limit 30) coh
        on mmt.person_id::text = coh.person_id
    where value_as_number <> 'NaN'
    and value_as_number is not null
    and (mmt.person_id, mmt.visit_occurrence_id) IN (SELECT person_id, visit_occurrence_id FROM omop_migration_etl_20240122.data_matrix)
)
select * from stg1
;
