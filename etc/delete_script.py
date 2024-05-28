import json
import requests


url = 'http://10.172.235.4:8080/fhir/Observation?_count=100'
while url:
    print('url: ', url)
    response = requests.get(
                            url=url,
                            headers={"authentication": "mjRmoNGW6klxaClkKhEkqi7HVYwx6NTH"},
                            )
    url = None
    responseJson = json.loads(response.text)
    print('responseJson: ', responseJson)
    if('entry' in responseJson):
        entries = responseJson['entry']
        for entry in entries:
            res = requests.delete(
                url='http://10.172.235.4:8080/fhir/Observation/' + entry['resource']['id'],
                headers={"authentication": "mjRmoNGW6klxaClkKhEkqi7HVYwx6NTH"},
                )
            print('res: ', res)
    links = responseJson['link']
    for link in links:
        if link['relation'] == 'next':
            url = link['url']
