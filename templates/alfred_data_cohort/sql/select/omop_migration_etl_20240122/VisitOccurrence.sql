with stg1 as (
    select
    distinct
    ('E' || vo.visit_occurrence_id) as id,
    (
        case when vo.admitting_source_concept_id is null then 'outpatient' else 
        (
            case when vo.admitting_source_concept_id = 0 then 'outpatient' else 'inpatient' end
        ) end
    ) as code,
    'Patient/' || ('P' || per.person_source_value) as person_id,
    to_char(vo.visit_start_datetime, 'YYYY-MM-DD') || 'T' || to_char(vo.visit_start_datetime, 'HH24:MI:SS') as visit_start_datetime,
    to_char(vo.visit_end_datetime, 'YYYY-MM-DD') || 'T' || to_char(vo.visit_end_datetime, 'HH24:MI:SS') as visit_end_datetime
    from
    omop_migration_etl_20240122.cdm_visit_occurrence vo
    inner join omop_migration_etl_20240122.cdm_person per
    on per.person_source_value = vo.person_id::text
    inner join omop_migration_etl_20240122.cohort_saur coh
    on vo.person_id::text = coh.person_id
)
select * from stg1
;
