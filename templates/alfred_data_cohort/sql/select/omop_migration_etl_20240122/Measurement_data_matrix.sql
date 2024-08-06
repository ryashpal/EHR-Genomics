with stg1 as (
    select
    distinct
    ('M' || mmt.measurement_id) as id,
    mmt.measurement_concept_id as measurement_concept_id,
    mmt.measurement_source_value as measurement_concept_name,
    'Patient/' || ('P' || mmt.person_id) as person_id,
    'Encounter/' || ('E' || mmt.visit_occurrence_id) as visit_occurrence_id,
    to_char(mmt.measurement_datetime, 'YYYY-MM-DD') || 'T00:00:00' as measurement_datetime,
    '' as unit_concept_id,
    mmt.unit_source_value as unit_concept_code,
    mmt.value_as_number as value_as_number
    from
    omop_migration_etl_20240122.cdm_measurement mmt
    inner join omop_migration_etl_20240122.cohort_saur coh
        on mmt.person_id::text = coh.person_id
    where value_as_number <> 'NaN'
    and value_as_number is not null
    and (mmt.person_id, mmt.visit_occurrence_id) IN (SELECT person_id, visit_occurrence_id FROM omop_migration_etl_20240122.data_matrix)
    -- and measurement_concept_id in ('767002', '1022571000000108', '68615006', '1028281000000106', '50213009', '15373003', '71960002', '1022431000000105', '165418001', '56972008', '1022481000000109', '1022471000000107', '1022491000000106', '55918008', '30630007', '88480006', '14089001', '993501000000105', '39972003', '16378004', '56935002', '1028091000000102', '52454007', '79706000', '997611000000101', '304383000', '81905004', '5540006', '104866001', '38151008') -- lab measurements
    and measurement_concept_id in ('431314004', '86290005', '246508008', '271649006', '271650006', '6797001', '364075005') -- vitals
),
stg2 as (
    select DISTINCT ON (person_id, visit_occurrence_id, measurement_concept_id, measurement_datetime)
        *
    from stg1
)
select * from stg2
;
