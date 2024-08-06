import json
import requests

from src.ehrgen.config import AppConfig


def get(url):
    response = requests.get(
        url=url,
        headers={"Content-Type": "application/fhir+json", "authentication": "mjRmoNGW6klxaClkKhEkqi7HVYwx6NTH"},
    )
    return response


def put(entity, data):
    fhirServerBaseUrl = AppConfig.fhir_server_base_url
    fhirUrlEntity = fhirServerBaseUrl + '/' + entity

    response = requests.put(
        url=fhirUrlEntity,
        json=data,
        headers={"Content-Type": "application/fhir+json", "authentication": "mjRmoNGW6klxaClkKhEkqi7HVYwx6NTH"},
    )

    return response


def readData(url):
    nextUrl = url
    data = []
    while(nextUrl):
        print('Reading URL: ', nextUrl)
        response = get(nextUrl)
        responseText = json.loads(response.text)
        data.append(responseText)
        nextUrl = None
        if 'link' in responseText:
            for link in responseText['link']:
                if link['relation'] == 'next':
                    nextUrl = link['url']
    return data


def readFhirFromUrl(urlQueryStringPath):
    response = None
    urlQueryString = None
    with open(urlQueryStringPath) as f:
        urlQueryString = f.read()
    if urlQueryString:
        response = get(urlQueryString)
    return json.loads(response.text)
