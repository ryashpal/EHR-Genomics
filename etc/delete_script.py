import json
import requests



url = 'http://10.172.235.4:8080/fhir/Encounter?_count=100'
while url:
    print('url: ', url)
    response = requests.get(url=url)
    url = None
    responseJson = json.loads(response.text)
    print('responseJson: ', responseJson)
    if('entry' in responseJson):
        entries = responseJson['entry']
        for entry in entries:
            res = requests.delete('http://10.172.235.4:8080/fhir/Encounter/' + entry['resource']['id'])
            print('res: ', res)
    links = responseJson['link']
    for link in links:
        if link['relation'] == 'next':
            url = link['url']

