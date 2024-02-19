
select
(
    case when vo.visit_occurrence_id::text like '-%' then 'm' || substr(vo.visit_occurrence_id::text, 2) else 'p' || vo.visit_occurrence_id end
) as id,
(
    case when vo.admitting_source_concept_id is null then 'outpatient' else 
    (
        case when vo.admitting_source_concept_id = 0 then 'outpatient' else 'inpatient' end
    ) end
) as code,
'Patient/' || (case when vo.person_id::text like '-%' then 'm' || substr(vo.person_id::text, 2) else 'p' || vo.person_id end) as person_id,
to_char(vo.visit_start_datetime, 'YYYY-MM-DD') || 'T' || to_char(vo.visit_start_datetime, 'HH24:MI:SS') as visit_start_datetime,
to_char(vo.visit_end_datetime, 'YYYY-MM-DD') || 'T' || to_char(vo.visit_end_datetime, 'HH24:MI:SS') as visit_end_datetime
from
omop_test_20220817.visit_occurrence vo
inner join omop_test_20220817.person per
on per.person_id = vo.person_id
inner join omop_test_20220817.data_matrix dm
on dm.person_id = per.person_id
where
(
	(vo.visit_start_datetime between (dm.anchor_time::timestamp - interval '1 month') and (dm.anchor_time::timestamp + interval '1 month'))
	or
	(vo.visit_end_datetime between (dm.anchor_time::timestamp - interval '1 month') and (dm.anchor_time::timestamp + interval '1 month'))
	or
	(dm.anchor_time::timestamp between vo.visit_start_datetime and vo.visit_end_datetime)
)
;