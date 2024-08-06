with stg1 as(
	select
	('P' || per.person_source_value) as id,
	lower(per.gender_source_value) as gender,
    to_char(per.birth_datetime, 'YYYY-MM-DD') as birth_date
	from
	omop_migration_etl_20240122.cdm_person per
	inner join omop_migration_etl_20240122.cohort_saur coh
	on coh.person_id = per.person_source_value
), stg2 as (
	select
	distinct id as id,
	first_value(gender) over () as gender,
	first_value(birth_date) over () as birth_date
	from stg1
)
select * from stg2
;
