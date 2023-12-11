import requests, json


def getPage(title):
        response = requests.get(f'https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles={title}'
                            '&rvslots=*&rvprop=content&formatversion=2&format=json')
        data = json.loads(response.text)['query']['pages'][0]['revisions'][0]['slots']['main']['content']
        return data