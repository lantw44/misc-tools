#!/usr/bin/env python3

from pkg_resources import parse_version
import json, re
import urllib.request


def get_upstream_version():
    url = 'http://ftp.vim.org/pub/vim/patches/7.4/README'
    data = urllib.request.urlopen(url).read()
    return data.split(b'\n')[-2].strip().split(b'  ')[1].decode()

def get_package_version_copr():
    copr_api_url = 'https://copr.fedorainfracloud.org/api'
    url = copr_api_url + '/coprs/lantw44/vim-latest/monitor/'
    data = json.loads(urllib.request.urlopen(url).read().decode())
    for pkg in data['packages']:
        if pkg['pkg_name'] == 'vim':
            pkg_version = pkg['results']['fedora-23-x86_64']['pkg_version']
            return re.sub('^[0-9]*:', '', re.sub('\.fc[0-9]*$', '', pkg_version))

get_package_version = get_package_version_copr
latest = get_upstream_version()
current = get_package_version()

import sys
if len(sys.argv) >= 2:
    print('>>> latest = {}, packaged = {}'.format(latest, current))

if parse_version(current) < parse_version(latest):
    print('Please update the vim package!')
    print('>>> latest = {}, packaged = {}'.format(latest, current))
    exit(1)
