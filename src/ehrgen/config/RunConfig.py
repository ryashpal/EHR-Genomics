import os


run_config_omop_to_fhir = [
    # {
    #     'entity': 'Patient',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/sql/select/Person.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/fhir/Patient.json',
    #     'json_sql_mapping': {
    #         'id': 'id',
    #         'gender': 'gender',
    #     },
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/patient',
    # },
    # {
    #     'entity': 'Encounter',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/sql/select/VisitOccurrence.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/fhir/Encounter.json',
    #     'json_sql_mapping': {
    #         'id': 'id',
    #         'class||code': 'code',
    #         'subject||reference': 'person_id',
    #         'participant||period||end': 'visit_end_datetime',
    #         'participant||period||start': 'visit_start_datetime',
    #         'location': {
    #             'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/sql/select/LocationListitem.sql',
    #             'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/fhir/LocationListitem.json',
    #             'json_sql_mapping': {
    #                 'location||reference': 'id',
    #                 'period||start': 'intime',
    #                 'period||end': 'outtime',
    #             }
    #         }
    #     },
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/encounter',
    # },
    # {
    #     'entity': 'Observation',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/sql/select/Measurement.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/fhir/Observation.json',
    #     'json_sql_mapping': {
    #         'id': 'id',
    #         'code||coding||code': 'measurement_concept_id',
    #         'code||coding||display': 'measurement_concept_name',
    #         'code||text': 'measurement_concept_name',
    #         'subject||reference': 'person_id',
    #         'encounter||reference': 'visit_occurrence_id',
    #         'effectiveDateTime': 'measurement_datetime',
    #         'valueQuantity||value': 'value_as_number',
    #         'valueQuantity||unit': 'unit_concept_id',
    #         'valueQuantity||code': 'unit_concept_code',
    #     },
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/observation',
    # },
]


run_config_fhir_to_omop = [
    # {
    #     'entity':'Patient',
    #     'type': 'migrate',
    #     'urlQueryStringPath':'migrate/urls/Patient.url',
    #     'sqlFilePath':'migrate/sql/insert/Person.sql',
    #     'sql_json_mapping': {
    #         'id': 'id',
    #         'gender': 'gender'
    #     }
    # },
    # {
    #     'entity':'Observation',
    #     'type': 'migrate',
    #     'urlQueryStringPath':'migrate/urls/Observation.url',
    #     'sqlFilePath':'migrate/sql/insert/Measurement.sql',
    #     'sql_json_mapping': {
    #         'id': 'id',
    #         'value_as_number': 'valueQuantity||value',
    #         'measurement_concept_id': 'code||coding||0||code',
    #         'unit_concept_id': 'valueQuantity||unit',
    #         'person_id': 'subject||reference',
    #         'visit_occurrence_id': 'encounter||reference',
    #         'measurement_datetime': 'effectiveDateTime',
    #     }
    # },
]


run_config_gtf_to_fhir = [
    {
        'type': 'migrate',
        'index_file': os.environ['EHR_GENOMICS_BASE'] + '/data/genome/simulated/index.csv',
        'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/fhir/Measurement.json',
        'save': True,
        'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/gtf_to_fhir/measurement',
    },
]
