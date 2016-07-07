#!/usr/bin/env python3

import ftplib
import json
import re
import urllib.parse
import urllib.request
from distutils.version import LooseVersion


def read_chrome_version(os, channel,
        instance = 'https://omahaproxy.appspot.com/all'):
    url = '{}?os={}&channel={}'.format(instance, os, channel)
    data = urllib.request.urlopen(url).read()
    return data.split(b'\n')[1].split(b',')[2].decode()

def read_vim_version(
        instance = 'ftp://ftp.vim.org/mirror/vim'):
    url_parse_result = urllib.parse.urlparse(instance)
    host = url_parse_result.netloc
    root = url_parse_result.path
    with ftplib.FTP(host) as ftp:
        ftp.login()
        # Find the latest major release
        ftp.cwd('{}/unix'.format(root))
        tars = ftp.nlst()
        tar_iter = filter(
            lambda x: re.match(r'vim-[0-9]+.[0-9]+\.tar\.[a-z]z2?', x), tars)
        ver_iter = map(
            lambda x: re.sub(r'vim-(.+)\.tar\.[a-z]z2?$', r'\1', x), tar_iter)
        max_ver = '0'
        for ver in ver_iter:
            if LooseVersion(ver) > LooseVersion(max_ver):
                max_ver = ver
        # Find the latest patch release
        ftp.cwd('{}/patches/{}'.format(root, max_ver))
        patches = ftp.nlst()
        patch_pattern = '{}.[0-9]+'.format(max_ver).replace('.', r'\.')
        patch_iter = filter(lambda x: re.match(patch_pattern, x), patches)
        max_patch = '0'
        for patch in patch_iter:
            if LooseVersion(patch) > LooseVersion(max_patch):
                max_patch = patch
    return max_patch

def read_rpm_spec_version(url):
    spec = urllib.request.urlopen(url).read()
    return spec.split(b'\nVersion:')[1].split()[0].decode()

def read_anitya_version(project_id,
        instance = 'https://release-monitoring.org/api'):
    url = '{}/project/{}'.format(instance, project_id)
    data = urllib.request.urlopen(url).read()
    data = json.loads(data.decode())
    return data['version']

def read_copr_version(repo, package, chroot, raw = False,
        instance = 'https://copr.fedorainfracloud.org/api'):
    url = '{}/coprs/{}/monitor/'.format(instance, repo)
    data = urllib.request.urlopen(url).read()
    data = json.loads(data.decode())
    for pkg in data['packages']:
        if pkg['pkg_name'] == package:
            pkg_version = pkg['results'][chroot]['pkg_version']
            if raw:
                return pkg_version
            pkg_version = re.sub('\.centos', '', pkg_version)
            pkg_version = re.sub('\.el[0-9]+$', '', pkg_version)
            pkg_version = re.sub('\.fc[0-9]+$', '', pkg_version)
            pkg_version = re.sub('-.*$', '', pkg_version)
            pkg_version = re.sub('^.*:', '', pkg_version)
            return pkg_version

def write_package_status(latest, packaged, name, verbose = False):
    out_of_date = LooseVersion(packaged) < LooseVersion(latest)
    if out_of_date:
        print('Please update {} package!'.format(name))
    if out_of_date or verbose:
        print('>>> latest = {}, packaged = {}'.format(latest, packaged))
    return out_of_date
