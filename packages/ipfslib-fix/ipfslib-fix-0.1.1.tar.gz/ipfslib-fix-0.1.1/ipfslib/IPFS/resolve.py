import json
import requests

# Resolve IPNS name
def resolve(api, ipns_name):
    response = requests.post('http://{endpoint}/api/v0/name/resolve/{ipns_name}'.format(endpoint=api.endpoint, ipns_name=ipns_name))
    raw_json = response.text
    try:
        data = json.loads(raw_json)
        return data['Path'].replace('/ipfs/', '')
    except KeyError:
        raise Exception('IPNS resolution failed: {}'.format(response.text))