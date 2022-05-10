#!/usr/bin/env python3

import os
import argparse
import requests
import time
import datetime
import getpass

from yaml import parse

api = 'https://data-proxy.ebrains.eu/api/'

def upload(fname):
    hdr = {'Authorization': 'Bearer ' + get_token()}
    ul_url = requests.put(api + f'buckets/hip-tvb-app/{fname}', params={'redirect':'false'}, headers=hdr).json()['url']
    # file is too big to naively put
    # with open(fname, 'rb') as fd:
    #     resp = requests.put(ul_url, data=fd.read())
    cmd = f"curl --progress-bar '{ul_url}' --upload-file '{fname}'"
    print(repr(cmd))
    os.system(cmd)

def download(fname):
    hdr = {'Authorization': 'Bearer ' + get_token()}
    dl_url_resp = requests.get(api + f'buckets/hip-tvb-app/{fname}', params={'redirect':'false'}, headers=hdr)
    ul_url = None
    try:
        ul_url = dl_url_resp.json()['url']
    except KeyError as e:
        raise Exception(f'could not get temp url for app image via EBRAINS data proxy: "{dl_url_resp.text}". '
                         'Please check your EBRAINS_TOKEN.')
    print(repr(ul_url))
    # file is too big to naively put
    # with open(fname, 'rb') as fd:
    #     resp = requests.put(ul_url, data=fd.read())
    cmd = f"curl --progress-bar -LO '{ul_url}'"
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
    # 
    upload('tvb-hip-app.tar.gz2')

actions = ''

def parse_args():
    parser = argparse.ArgumentParser()
    # for action in 'build-image export-image download'
    parser.add_argument('--export-image', action='store_true', default=False)
    parser.add_argument('--download', action='store_true', default=False)
    parser.add_argument('--app-tar-name', default='tvb-hip-app.tar.gz2')
    return parser.parse_args()

def create_tar_parts():
    os.system('split -a 2 -b 1G tvb-hip-app.tar.gz2 tvb-hip-app.tar.gz2.')

def push_github_release():
    raise NotImplementedError

def test_github():
    from github import Github
    import glob
    import os
    token = os.environ['HIP_TVB_TOKEN']
    g = Github(token)
    repo = g.get_repo('ins-amu/hip-tvb-app')
    rls = repo.get_latest_release()
    print(rls)
    for fname in glob.glob('./tvb-hip-app.tar.gz2.*'):
        print(fname)
        rls.upload_asset(fname)

if __name__ == '__main__':
    import fire
    fire.Fire()
    # # put_image()
    # args = parse_args()
    # if args.export_image:
    #     cmd = "docker run --rm -it -v $PWD:/export hip bash -c 'apt-get install -y pigz && tar cf - /apps/tvb-hip | pigz -c > /export/tvb-hip-app.tar.gz2'"
    #     os.system(cmd)
    # if args.download:
    #     download(args.app_tar_name)
