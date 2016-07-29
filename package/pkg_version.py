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

def read_copr_version(repo, package, chroot, raw = False, debug = False,
        instance = 'https://copr.fedorainfracloud.org/api_2'):
    if repo.startswith('@'):
        project_group, project_name = repo.split('@')[1].split('/')
        projects_query = {'group': project_group, 'name': project_name}
    elif repo.startswith('g/'):
        project_group, project_name = repo.split('/')[1:]
        projects_query = {'group': project_group, 'name': project_name}
    else:
        project_owner, project_name = repo.split('/')
        projects_query = {'owner': project_owner, 'name': project_name}
    projects_query_encoded = urllib.parse.urlencode(projects_query)
    projects_url = '{}/projects?{}'.format(instance, projects_query_encoded)
    data = urllib.request.urlopen(projects_url).read()
    data = json.loads(data.decode())
    project_id = data['projects'][0]['project']['id']
    build_offset = 0
    build_limit = 10
    while True:
        if build_offset % build_limit == 0:
            builds_query = {
                'project_id': project_id,
                'offset': build_offset,
                'limit': build_limit}
            builds_query_encoded = urllib.parse.urlencode(builds_query)
            builds_url = '{}/builds?{}'.format(instance, builds_query_encoded)
            builds_data = urllib.request.urlopen(builds_url).read()
            builds_data = json.loads(builds_data.decode())
        if build_offset % build_limit >= len(builds_data['builds']):
            break
        build_detail = builds_data['builds'][build_offset % build_limit]
        build_offset += 1
        build_id = build_detail['build']['id']
        build_package_name = build_detail['build']['package_name']
        build_package_version = build_detail['build']['package_version']
        if debug:
            print('{}'.format(build_offset), end = '\t')
            print('{}'.format(build_package_name), end = '\t')
            print('{}'.format(build_package_version), end = '\n')
        if build_package_name != package:
            continue
        build_tasks_query = {'build_id': build_id}
        build_tasks_query_encoded = urllib.parse.urlencode(build_tasks_query)
        build_tasks_url = '{}/build_tasks?{}'.format(
            instance, build_tasks_query_encoded)
        build_tasks_data = urllib.request.urlopen(build_tasks_url).read()
        build_tasks_data = json.loads(build_tasks_data.decode())
        for build_task in build_tasks_data['build_tasks']:
            build_task_chroot_name = build_task['build_task']['chroot_name']
            if build_task_chroot_name == chroot:
                pkg_version = build_package_version
                if not raw:
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
