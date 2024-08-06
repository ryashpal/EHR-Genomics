import json
from src.ehrgen.utils import FhirUtils


def extractPatient(id):
    url = '''http://10.172.235.4:8080/fhir/Patient?_id=''' + id
    response = FhirUtils.get(url=url)
    return json.loads(response.text)


def extractObservation(id):
    url = '''http://10.172.235.4:8080/fhir/Observation?subject=''' + id
    response = FhirUtils.get(url=url)
    return json.loads(response.text)


def extractEncounter(id):
    url = '''http://10.172.235.4:8080/fhir/Encounter?subject=''' + id
    response = FhirUtils.get(url=url)
    return json.loads(response.text)


def extractRiskAssessment(id):
    url = '''http://10.172.235.4:8080/fhir/RiskAssessment?subject=''' + id
    response = FhirUtils.get(url=url)
    return json.loads(response.text)


def extractMolecularSequence(id):
    url = '''http://10.172.235.4:8080/fhir/MolecularSequence?subject=''' + id
    response = FhirUtils.get(url=url)
    return json.loads(response.text)


def extractAllData(id):

    patientsResponse = extractPatient(id=id)
    patientsData = patientsResponse['entry'] if 'entry' in patientsResponse else []
    patientsList = [[patient['resource']['id'], patient['resource']['gender']] for patient in patientsData]
    print('patientsList: ', patientsList)

    encountersResponse = extractEncounter(id=id)
    print('encountersResponse: ', encountersResponse)
    encountersData = encountersResponse['entry'] if 'entry' in encountersResponse else []
    encountersList = [
        [
            encounter['resource']['id'],
            encounter['resource']['serviceProvider']['reference'],
            encounter['resource']['participant'][0]['period']['start'],
            encounter['resource']['participant'][0]['period']['end'],
        ] for encounter in encountersData
    ]
    print('encountersList: ', encountersList)

    observationsResponse = extractObservation(id=id)
    observationsData = observationsResponse['entry'] if 'entry' in observationsResponse else []
    observationsList = [
        [
            observation['resource']['id'],
            observation['resource']['subject']['reference'],
            observation['resource']['encounter']['reference'],
            observation['resource']['code']['coding'][0]['code'],
            observation['resource']['code']['coding'][0]['display'],
            observation['resource']['valueQuantity']['value'],
        ] for observation in observationsData
    ]
    print('observations: ', observationsList)

    riskAssessmentResponse = extractRiskAssessment(id=id)
    riskAssessmentData = riskAssessmentResponse['entry'] if 'entry' in riskAssessmentResponse else []
    riskAssessmentList = [
        [
            riskAssessment['resource']['id'],
            riskAssessment['resource']['subject']['reference'],
            riskAssessment['resource']['occurrenceDateTime'],
            riskAssessment['resource']['prediction'][0]['probabilityDecimal'],
            riskAssessment['resource']['note'][0]['text'],
        ] for riskAssessment in riskAssessmentData
    ]
    print('riskAssessment: ', riskAssessmentList)

    molecularSequenceResponse = extractMolecularSequence(id=id)
    molecularSequenceData = molecularSequenceResponse['entry'] if 'entry' in molecularSequenceResponse else []
    molecularSequenceList = [
        [
            molecularSequence['resource']['id'],
            molecularSequence['resource']['subject']['reference'],
            molecularSequence['resource']['formatted'][0]['title'],
            molecularSequence['resource']['formatted'][0]['url'] if 'url' in molecularSequence['resource']['formatted'][0] else '',
            molecularSequence['resource']['formatted'][1]['title'],
            molecularSequence['resource']['formatted'][1]['url'] if 'url' in molecularSequence['resource']['formatted'][0] else '',
            molecularSequence['resource']['extension'][0]['valueString'],
        ] for molecularSequence in molecularSequenceData
    ]
    print('molecularSequence: ', molecularSequenceList)

    return patientsList, encountersList, observationsList, riskAssessmentList, molecularSequenceList


if __name__ == '__main__':
    data = extractAllData(id='P2221447')
    print('data: ', data)
