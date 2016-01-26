#!/usr/bin/env python3

from pkg_resources import parse_version
import json, re
import urllib.request


def get_upstream_version():
    url = 'https://omahaproxy.appspot.com/all?os=linux&channel=stable'
    data = urllib.request.urlopen(url).readall()
    return data.split(b'\n')[1].split(b',')[2].decode()

def get_package_version_cgit():
    cgit_plain_url = 'http://phantom.tfcis.org/~lantw44/cgit/copr-rpm-spec/plain/chromium/chromium/chromium.spec'
    spec = urllib.request.urlopen(cgit_plain_url).readall().decode()
    return spec.split('\nVersion:')[1].split()[0]

def get_package_version_copr():
    copr_api_url = 'https://copr.fedorainfracloud.org/api'
    url = copr_api_url + '/coprs/lantw44/chromium/monitor/'
    data = json.loads(urllib.request.urlopen(url).readall().decode())
    for pkg in data['packages']:
        if pkg['pkg_name'] == 'chromium':
            pkg_version = pkg['results']['fedora-23-x86_64']['pkg_version']
            return re.sub('\.fc[0-9]*$', '', pkg_version)

get_package_version = get_package_version_copr
latest = get_upstream_version()
current = get_package_version()

import sys
if len(sys.argv) >= 2:
    print('>>> latest = {}, packaged = {}'.format(latest, current))

if parse_version(current) < parse_version(latest):
    print('Please update the chromium package!')
    print('>>> latest = {}, packaged = {}'.format(latest, current))
