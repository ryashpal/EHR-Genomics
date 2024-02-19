import json
import requests

from ehrgen.config import AppConfig


def get(url):
    response = requests.get(
        url=url
    )
    return response


def put(entity, data):
    fhirServerBaseUrl = AppConfig.fhir_server_base_url
    fhirUrlEntity = fhirServerBaseUrl + '/' + entity

    response = requests.put(
        url=fhirUrlEntity,
        json=data,
        headers={"Content-Type": "application/fhir+json"}
    )

    return response

def readFhirFromUrl(urlQueryStringPath):
    response = None
    urlQueryString = None
    with open(urlQueryStringPath) as f:
        urlQueryString = f.read()
    if urlQueryString:
        response = get(urlQueryString)
    return json.loads(response.text)