#!/usr/bin/env python3

import pkg_version
import sys

verbose = len(sys.argv) - 1
latest = pkg_version.read_chrome_version('linux', 'stable')
packaged = pkg_version.read_copr_version(
    'lantw44/chromium', 'chromium', 'fedora-26-x86_64')
exit(pkg_version.write_package_status(latest, packaged, 'chromium', verbose))
