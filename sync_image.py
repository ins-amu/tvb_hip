import argparse
import requests
import time
import datetime

def upload(tok, fname):
    api = 'https://data-proxy.ebrains.eu/api/'
    hdr = {'Authorization': 'Bearer ' + tok}
    ul_url = requests.put(api + f'buckets/hip-tvb-app/{fname}', headers=hdr).json()['url']
    with open(fname, 'rb') as fd:
        resp = requests.put(ul_url, data=fd.read())
    print(resp.text)

resp = requests.post(api + 'auth/token', json={'username': 'woodman', 'password': "oawGQe!N4!%Rwnc*"})
tok = resp.json()
upload(tok, 'Dockerfile')
