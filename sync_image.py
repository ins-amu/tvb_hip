import os
import argparse
import requests
import time
import datetime
import getpass

api = 'https://data-proxy.ebrains.eu/api/'

def upload(fname):
    hdr = {'Authorization': 'Bearer ' + get_token()}
    ul_url = requests.put(api + f'buckets/hip-tvb-app/{fname}', headers=hdr).json()['url']
    # file is too big to naively put
    # with open(fname, 'rb') as fd:
    #     resp = requests.put(ul_url, data=fd.read())
    cmd = f"curl '{ul_url}' --upload-file '{fname}'"
    print(repr(cmd))
    os.system(cmd)

def get_token():
    if 'EBRAINS_TOKEN' in os.environ:
        return os.environ['EBRAINS_TOKEN']
    resp = requests.post(api + 'auth/token', json={'username': input('Username: '), 'password': getpass.getpass()})
    token = resp.json()
    print(token)
    os.environ['EBRAINS_TOKEN'] = token
    return token

def put_image():
    # docker run --rm -it -v $PWD:/export hip bash -c 'apt-get install -y pigz && tar cf - /apps/tvb-hip | pigz -c > /export/tvb-hip-app.tar.gz2'
    upload('tvb-hip-app.tar.gz2')

if __name__ == '__main__':
    put_image()
