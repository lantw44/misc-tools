#!/usr/bin/env python3

import pkg_version
import sys

verbose = len(sys.argv) - 1
latest = pkg_version.read_openssl_version('1.0')
packaged = pkg_version.read_copr_version(
    'lantw44/gcoin-community', 'gcoin-compat-openssl', 'epel-7-x86_64')
exit(pkg_version.write_package_status(latest, packaged, 'openssl', verbose))
