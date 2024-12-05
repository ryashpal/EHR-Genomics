import os
import json

import pandas as pd

from src.ehrgen.utils.FhirUtils import get
from src.ehrgen.utils.DbUtils import getConnection

import logging

log = logging.getLogger("EHRQC")


def importIndexFile(args):

    log.info('getting connection')
    con = getConnection()

    log.info('Creating table')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS omop_migration_etl_20240122.index_saur (specimen_id varchar, person_id varchar);")
    cur.close()

    log.info('Loading data from file: ' + args['cohort_file'])
    log.info('Person ID Column in the file: ' + args['person_id_column'])
    log.info('Specimen ID Column in the file: ' + args['specimen_id_column'])
    cohortDf = pd.read_csv(args['cohort_file'])
    for i, row in cohortDf.iterrows():
        personId = row[args['person_id_column']]
        specimenId = row[args['specimen_id_column']]
        cur = con.cursor()
        cur.execute('INSERT INTO omop_migration_etl_20240122.index_saur (person_id, specimen_id) VALUES (' + str(personId) + ", '" + str(specimenId) +"')")
        cur.close()

    log.info('Completed!!')
    con.commit()
    con.close()


def createDataCohort(args):

    log.info('getting connection')
    con = getConnection()

    log.info('Creating table')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS omop_migration_etl_20240122.cohort_saur (person_id varchar);")
    cur.close()

    log.info('Loading data from file: ' + args['cohort_file'])
    log.info('Person ID Column in the file: ' + args['person_id_column'])
    cohortDf = pd.read_csv(args['cohort_file'])
    for i, row in cohortDf.iterrows():
        personId = row[args['person_id_column']]
        cur = con.cursor()
        cur.execute('INSERT INTO omop_migration_etl_20240122.cohort_saur (person_id) VALUES (' + str(personId) + ')')
        cur.close()

    log.info('Completed!!')
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
        description = str(args['description'])
        cur = con.cursor()
        cur.execute(
            'INSERT INTO omop_migration_etl_20240122.risk_scores (person_id, visit_occurrence_id, risk_score, description) VALUES (%s, %s, %s, %s)',
            (personId, visitOccurrenceId, riskScore, description)
            )
        cur.close()

    log.info('Shutting down')
    con.commit()
    con.close()


def importAnnotations(args):

    log.info('getting connection')
    con = getConnection()

    log.info('dropping table')
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS omop_migration_etl_20240122.genome_annotations;")
    cur.close()

    log.info('creating table')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS omop_migration_etl_20240122.genome_annotations (person_id varchar, visit_occurrence_id varchar, loci_id varchar, source varchar, type varchar, contig varchar, start_loc varchar, end_loc varchar);")
    cur.close()

    log.info('Loading Lookup Information')
    lookupDf = pd.read_csv(os.environ['GENOMICS_DATA_BASE'] + '/patient_tube_id_mapping_full.tsv', sep='\t')

    log.info('Loading data')
    genomeAnnotationsDir = args['genome_annotations_dir']
    for file in os.listdir(genomeAnnotationsDir):
        if file.endswith('.gff3'):
            print('file: ', file)
            lookupRow = lookupDf[lookupDf.tube_code == file.split('.')[0]]
            gffFile = pd.read_csv(
                genomeAnnotationsDir + '/' + file, 
                comment='#', 
                sep='\t',
                names=['contig', 'source', 'type', 'start_loc', 'end_loc', 'score', 'strand', 'phase', 'attributes']
            ).dropna()
            # annotationsDf = gffFile[gffFile.source != 'Prodigal']
            annotationsDf = gffFile

            for i, row in annotationsDf.iterrows():
                if pd.isna(lookupRow.PATIENT_ID.values[0]):
                    break
                personId = str(int(lookupRow.PATIENT_ID.values[0]))
                if pd.isna(lookupRow.EPISODE_ID.values[0]):
                    break
                visitOccurrenceId = str(int(lookupRow.EPISODE_ID.values[0]))
                attributes = str(row.attributes)
                geneNames = [attribute.split('=')[1] for attribute in attributes.split(';') if attribute.split('=')[0] == 'gene']
                lociId = [attribute.split('=')[1] for attribute in attributes.split(';') if attribute.split('=')[0] == 'ID'][0]
                lociId = geneNames[0] if (len(geneNames) > 0) else lociId
                source = str(row.source)
                seq_type = str(row.type)
                contig = str(int(row.contig))
                start_loc = str(int(row.start_loc))
                end_loc = str(int(row.end_loc))
                cur = con.cursor()
                cur.execute(
                    'INSERT INTO omop_migration_etl_20240122.genome_annotations (person_id, visit_occurrence_id, loci_id, source, type, contig, start_loc, end_loc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (personId, visitOccurrenceId, lociId, source, seq_type, contig, start_loc, end_loc)
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
    #     'function': createDataCohort,
    #     'args': {
    #         'cohort_file': os.environ['GENOMICS_DATA_BASE'] + '/cohort_saur.csv',
    #         'person_id_column': 'PATIENT_ID',
    #         }
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
    #         'name||given||0': 'id',
    #         'birthDate': 'birth_date',
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
    #         'actualPeriod||end': 'visit_end_datetime',
    #         'actualPeriod||start': 'visit_start_datetime',
    #     },
    #     'readFromDb': True,
    #     'loadToFHIR': True,
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/encounter',
    # },
    # {
    #     'entity': 'Observation',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/sql/select/omop_migration_etl_20240122/Measurement_data_matrix.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/fhir/Observation.json',
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
    #     'readFromDb': True,
    #     'loadToFHIR': True,
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/observation',
    # },
    # {
    #     'type': 'execute',
    #     'function': importRiskScores,
    #     'args': {
    #         'risk_scores_file': os.environ['EHR_DATA_BASE'] + '/blood_pos_cohort_20240119/predictions/death_7_day/wb_30_wa_0.csv',
    #         'description': {
    #             "model": "XGBoost Ensemble",
    #             "windowBefore": "30 days",
    #             "windowAfter": "0 day",
    #             "target": "Mortality",
    #             "targetTime": "7 day",
    #             }
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
    #         'risk_scores_file': os.environ['EHR_DATA_BASE'] + '/blood_pos_cohort_20240119/predictions/death_14_day/wb_30_wa_0.csv',
    #         'description': {
    #             "model": "XGBoost Ensemble",
    #             "windowBefore": "30 days",
    #             "windowAfter": "0 day",
    #             "target": "Mortality",
    #             "targetTime": "14 day",
    #             }
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
    #         'risk_scores_file': os.environ['EHR_DATA_BASE'] + '/blood_pos_cohort_20240119/predictions/death_30_day/wb_30_wa_0.csv',
    #         'description': {
    #             "model": "XGBoost Ensemble",
    #             "windowBefore": "30 days",
    #             "windowAfter": "0 day",
    #             "target": "Mortality",
    #             "targetTime": "30 day",
    #             }
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
    #     'function': importIndexFile,
    #     'args': {
    #         'cohort_file': os.environ['GENOMICS_DATA_BASE'] + '/index_saur.csv',
    #         'person_id_column': 'patient_id',
    #         'specimen_id_column': 'specimen_id',
    #         }
    # },
    # {
    #     'entity': 'Observation',
    #     'type': 'migrate',
    #     'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/sql/select/omop_migration_etl_20240122/Index.sql',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/fhir/BacteriaObservation.json',
    #     'json_sql_mapping': {
    #         'id': 'id',
    #         'subject||reference': 'person_id',
    #     },
    #     'readFromDb': True,
    #     'loadToFHIR': True,
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/Observation',
    # },
    # {
    #     'type': 'execute',
    #     'function': importAnnotations,
    #     'args': {
    #         'genome_annotations_dir': os.environ['GENOMICS_DATA_BASE'] + '/annotations/s_aureus/',
    #         }
    # },
    {
        'entity': 'Observation',
        'type': 'migrate',
        'sqlFilePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/sql/select/omop_migration_etl_20240122/SaurObservation.sql',
        'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/fhir/SaurObservation.json',
        'json_sql_mapping': {
            'id': 'id',
            'subject||reference': 'person_id',
            'encounter||reference': 'visit_occurrence_id',
            'text||div': 'loci_id',
            'component||0||valueRange||low||value': 'start_loc',
            'component||0||valueRange||high||value': 'end_loc',
            'component||1||valueInteger': 'contig',
            'component||2||valueString': 'type',
            'component||3||valueString': 'source',
        },
        'readFromDb': True,
        'loadToFHIR': True,
        'save': True,
        'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/SaurObservation/',
    },
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


run_config_genome_to_fhir = [
    # {
    #     'type': 'migrate',
    #     'index_file': os.environ['GENOMICS_DATA_BASE'] + '/index_saur.csv',
    #     'jsonTemplatePath': os.environ['EHR_GENOMICS_BASE'] + '/templates/alfred_data_cohort/fhir/MolecularSequence.json',
    #     'save': True,
    #     'savePath': os.environ['EHR_GENOMICS_BASE'] + '/data/omop_to_fhir/alfred_data_saur/molecular_sequence',
    # },
]
