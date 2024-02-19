import json
import requests


def extractPatient(id):
    url = '''http://superbugai.erc.monash.edu:8082/fhir/Patient?_id=''' + id
    response = requests.get(url=url)
    return json.loads(response.text)


def extractObservation(id):
    url = '''http://superbugai.erc.monash.edu:8082/fhir/Observation?subject=''' + id
    response = requests.get(url=url)
    return json.loads(response.text)


def extractEncounter(id):
    url = '''http://superbugai.erc.monash.edu:8082/fhir/Encounter?subject=''' + id
    response = requests.get(url=url)
    return json.loads(response.text)


def extractAllData(id):

    patientsResponse = extractPatient(id=id)
    patientsData = patientsResponse['entry']
    patientsList = [[patient['resource']['id'], patient['resource']['gender']] for patient in patientsData]

    encountersResponse = extractEncounter(id=id)
    encountersData = encountersResponse['entry']
    encountersList = [
        [
            encounter['resource']['id'],
            encounter['resource']['serviceProvider']['reference'],
            encounter['resource']['participant'][0]['period']['start'],
            encounter['resource']['participant'][0]['period']['end'],
        ] for encounter in encountersData
    ]

    observationsResponse = extractObservation(id=id)
    observationsData = observationsResponse['entry']
    observationsList = [
        [
            observation['resource']['id'],
            observation['resource']['subject']['reference'],
            observation['resource']['encounter']['reference'],
            observation['resource']['valueString'],
        ] for observation in observationsData
    ]

    print('patientsList: ', patientsList)
    print('encountersList: ', encountersList)
    print('observations: ', observationsList)

    return patientsList, encountersList, observationsList


if __name__ == '__main__':
    data = extractAllData(id='p99806512')
    print('data: ', data)
