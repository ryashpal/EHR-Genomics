select
	specimen_id as id,
	'Patient/' || ('P' || person_id) as person_id
from
	omop_migration_etl_20240122.index_saur per
