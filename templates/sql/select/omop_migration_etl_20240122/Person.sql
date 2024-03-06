with stg1 as(
	select
	('P' || per.person_source_value) as id,
	lower(per.gender_source_value) as gender
	from
	omop_migration_etl_20240122.cdm_person per
	inner join omop_migration_etl_20240122.data_matrix dm
	on dm.person_id::text = per.person_source_value
)
select
distinct id as id,
first_value(gender) over () as gender
from stg1
;
