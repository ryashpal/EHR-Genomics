select
(case when mmt.measurement_id::text like '-%' then 'm' || substr(mmt.measurement_id::text, 2) else 'p' || mmt.measurement_id end) as id,
mmt_con.concept_id as measurement_concept_id,
mmt_con.concept_name as measurement_concept_name,
'Patient/' || (case when mmt.person_id::text like '-%' then 'm' || substr(mmt.person_id::text, 2) else 'p' || mmt.person_id end) as person_id,
'Encounter/' || (case when mmt.visit_occurrence_id::text like '-%' then 'm' || substr(mmt.visit_occurrence_id::text, 2) else 'p' || mmt.visit_occurrence_id end) as visit_occurrence_id,
to_char(mmt.measurement_datetime, 'YYYY-MM-DD') || 'T' || to_char(mmt.measurement_datetime, 'HH24:MI:SS') as measurement_datetime,
uni_con.concept_id as unit_concept_id,
uni_con.concept_code as unit_concept_code,
mmt.value_as_number as value_as_number
from
omop_test_20220817.measurement mmt
inner join omop_test_20220817.concept mmt_con
on mmt_con.concept_id = mmt.measurement_concept_id
inner join omop_test_20220817.micro_cohort coh
on coh.visit_occurrence_id = mmt.visit_occurrence_id
inner join omop_test_20220817.concept uni_con
on uni_con.concept_id = mmt.unit_concept_id
where  mmt.measurement_source_value IN
    (
    '220045' -- heartrate
    )
and value_as_number <> 'NaN'
and value_as_number is not null