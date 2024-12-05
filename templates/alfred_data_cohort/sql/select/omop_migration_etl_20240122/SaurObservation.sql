select
    person_id || '-' || visit_occurrence_id || '-' || replace(loci_id, '_', '-') as id,
    'Patient/' || ('P' || person_id) as person_id,
    'Encounter/' || ('E' || visit_occurrence_id) as visit_occurrence_id,
    loci_id, source, type, contig, start_loc, end_loc
from
omop_migration_etl_20240122.genome_annotations ga
;
