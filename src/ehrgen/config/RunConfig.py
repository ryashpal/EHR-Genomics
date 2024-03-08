import os
import json

import pandas as pd

from ehrgen.utils.FhirUtils import get
from ehrgen.utils.DbUtils import getConnection

import logging

log = logging.getLogger("EHRQC")


def createDataCohort():

    log.info('getting connection')
    con = getConnection()

    log.info('Creating table')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS omop_migration_etl_20240122.cohort (person_id varchar, visit_occurrence_id varchar);")
    cur.close()

    log.info('Loading data')
    cohortDf = pd.read_csv('/home/vmadmin/workspace/EHR-Genomics/data/omop_to_fhir/cohort_saur.csv')
    for i, row in cohortDf.iterrows():
        personId = row.person_id
        visitOccurrenceId = row.visit_occurrence_id
        cur = con.cursor()
        cur.execute('INSERT INTO omop_migration_etl_20240122.cohort (person_id, visit_occurrence_id) VALUES (%s, %s)', (str(personId), str(visitOccurrenceId)))
        cur.close()

    log.info('Shutting down')
    con.commit()
    con.close()


def importRiskScores(args):

    log.info('getting connection')
    con = getConnection()

    log.info('dropping table')
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS omop_migration_etl_20240122.risk_scores;")
    cur.close()

    log.info('creating table')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS omop_migration_etl_20240122.risk_scores (person_id varchar, visit_occurrence_id varchar, risk_score varchar, description varchar);")
    cur.close()

    log.info('Loading data')
    cohortDf = pd.read_csv(args['risk_scores_file'])
    for i, row in cohortDf.iterrows():
        personId = str(row.person_id)
        visitOccurrenceId = str(row.visit_occurrence_id)
        riskScore = str(row.preds)
        description = args['description']
        cur = con.cursor()
        cur.execute(
            'INSERT INTO omop_migration_etl_20240122.risk_scores (person_id, visit_occurrence_id, risk_score, description) VALUES (%s, %s, %s, %s)',
            (personId, visitOccurrenceId, riskScore, description)
            )
        cur.close()

    log.info('Shutting down')
    con.commit()
    con.close()


def createLocationLookup():
    log.info('getting connection')
    con = getConnection()

    log.info('creating table')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS omop_migration_etl_20240122.location_id_map (id varchar, name varchar);")
    cur.close()

    log.info('fetching data')
    url = 'http://superbugai.erc.monash.edu:8082/fhir/Location?organization=T001&_count=50'
    response = get(url=url)
    responseJson = json.loads(response.text)
    entries = responseJson['entry']
    for entry in entries:
        id = entry['resource']['id']
        name = entry['resource']['name']
        cur = con.cursor()
        cur.execute('INSERT INTO omop_migration_etl_20240122.location_id_map (id, name) VALUES (%s, %s)', (id, name))
        cur.close()
    log.info('completed loading the data')
    con.commit()
    con.close()


run_config_omop_to_fhir = [
    # {
    #     'type': 'execute',
    #     'function': createDataCohort
    # },
    # {
    #     'entity': 'Organization',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_full/sql/select/omop_migration_etl_20240122/Organization.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_full/fhir/Organization.json',
    #     'json_sql_mapping': {
    #         'id': 'id',
    #         'name': 'organization_name',
    #     },
    #     'readFromDb': True,
    #     'loadToFHIR': True,
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/organization',
    # },
    # {
    #     'entity': 'Patient',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/sql/select/omop_migration_etl_20240122/Person.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/fhir/Patient.json',
    #     'json_sql_mapping': {
    #         'id': 'id',
    #         'gender': 'gender',
    #     },
    #     'readFromDb': True,
    #     'loadToFHIR': True,
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/patient',
    # },
    # {
    #     'entity': 'Encounter',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/sql/select/omop_migration_etl_20240122/VisitOccurrence.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/fhir/Encounter.json',
    #     'json_sql_mapping': {
    #         'id': 'id',
    #         'class||code': 'code',
    #         'subject||reference': 'person_id',
    #         'participant||period||end': 'visit_end_datetime',
    #         'participant||period||start': 'visit_start_datetime',
    #     },
    #     'readFromDb': True,
    #     'loadToFHIR': True,
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/encounter',
    # },
    {
        'entity': 'Observation',
        'type': 'migrate',
        'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/sql/select/omop_migration_etl_20240122/Measurement.sql',
        'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/fhir/Observation.json',
        'json_sql_mapping': {
            'id': 'id',
            'code||coding||code': 'measurement_concept_id',
            'code||coding||display': 'measurement_concept_name',
            'code||text': 'measurement_concept_name',
            'subject||reference': 'person_id',
            'encounter||reference': 'visit_occurrence_id',
            'effectiveDateTime': 'measurement_datetime',
            'valueQuantity||value': 'value_as_number',
            'valueQuantity||unit': 'unit_concept_id',
            'valueQuantity||code': 'unit_concept_code',
        },
        'readFromDb': False,
        'loadToFHIR': True,
        'save': True,
        'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/observation',
    },
    # {
    #     'type': 'execute',
    #     'function': importRiskScores,
    #     'args': {
    #         'risk_scores_file': '/home/vmadmin/workspace/ehr_data/blood_pos_cohort_20240119/predictions/death_7_day/wb_30_wa_1.csv',
    #         'description': "Model: XGBoost Ensemble, Window Before: 30 days, Window After: 1 day, Target: 7 day mortality",
    #         }
    # },
    # {
    #     'entity': 'RiskAssessment',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/sql/select/omop_migration_etl_20240122/RiskAssessment.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/fhir/RiskAssessment.json',
    #     'json_sql_mapping': {
    #         'id': 'id',
    #         'subject||reference': 'person_id',
    #         'occurrenceDateTime': 'occurrence_datetime',
    #         'prediction||probabilityDecimal': 'risk_score',
    #         'note||text': 'description',
    #     },
    #     'readFromDb': True,
    #     'loadToFHIR': True,
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/risk_assessment',
    # },
    # {
    #     'type': 'execute',
    #     'function': importRiskScores,
    #     'args': {
    #         'risk_scores_file': '/home/vmadmin/workspace/ehr_data/blood_pos_cohort_20240119/predictions/death_14_day/wb_30_wa_1.csv',
    #         'description': "Model: XGBoost Ensemble, Window Before: 30 days, Window After: 1 day, Target: 14 day mortality",
    #         }
    # },
    # {
    #     'entity': 'RiskAssessment',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/sql/select/omop_migration_etl_20240122/RiskAssessment.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/fhir/RiskAssessment.json',
    #     'json_sql_mapping': {
    #         'id': 'id',
    #         'subject||reference': 'person_id',
    #         'occurrenceDateTime': 'occurrence_datetime',
    #         'prediction||probabilityDecimal': 'risk_score',
    #         'note||text': 'description',
    #     },
    #     'readFromDb': True,
    #     'loadToFHIR': False,
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/risk_assessment',
    # },
    # {
    #     'type': 'execute',
    #     'function': importRiskScores,
    #     'args': {
    #         'risk_scores_file': '/home/vmadmin/workspace/ehr_data/blood_pos_cohort_20240119/predictions/death_30_day/wb_30_wa_1.csv',
    #         'description': "Model: XGBoost Ensemble, Window Before: 30 days, Window After: 1 day, Target: 30 day mortality",
    #         }
    # },
    # {
    #     'entity': 'RiskAssessment',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/sql/select/omop_migration_etl_20240122/RiskAssessment.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/fhir/RiskAssessment.json',
    #     'json_sql_mapping': {
    #         'id': 'id',
    #         'subject||reference': 'person_id',
    #         'occurrenceDateTime': 'occurrence_datetime',
    #         'prediction||probabilityDecimal': 'risk_score',
    #         'note||text': 'description',
    #     },
    #     'readFromDb': True,
    #     'loadToFHIR': True,
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/risk_assessment',
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
    # {
    #     'type': 'migrate',
    #     'index_file': os.environ['EHR_GENOMICS_BASE'] + '/data/genome/simulated/index.csv',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_full/fhir/Measurement.json',
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/gtf_to_fhir/measurement',
    # },
]


run_config_remap_to_fhir = [
    # {
    #     'type': 'migrate',
    #     'index_file': os.environ['EHR_GENOMICS_BASE'] + '/data/genome/simulated/index.csv',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_full/fhir/MolecularSequence.json',
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/remap_to_fhir/molecular_sequence',
    # },
]
