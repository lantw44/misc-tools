#!/usr/bin/env python3

import pkg_version
import sys

verbose = len(sys.argv) - 1
latest = pkg_version.read_vim_version()
packaged = pkg_version.read_copr_version(
    'lantw44/vim-latest', 'vim', 'fedora-33-x86_64')
exit(pkg_version.write_package_status(latest, packaged, 'vim', verbose))
