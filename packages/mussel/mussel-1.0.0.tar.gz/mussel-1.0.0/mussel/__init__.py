#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import getpass
import sys
import os
import shutil
import subprocess
import json
import argparse
import urllib.request

try:
    import argcomplete
    __ARGCOMPLETE__ = True
except ImportError:
    __ARGCOMPLETE__ = False

sys.tracebacklimit = 0


def mussel():
    dockerhub_tags = urllib.request.urlopen("https://hub.docker.com/v2/namespaces/8env/repositories/mussel-python/tags")
    tags = sorted([tag.get('name') for tag in json.load(dockerhub_tags).get('results')])

    parser = argparse.ArgumentParser("mussel")
    parser.add_argument('--python', choices=tags, required=True, dest="python_version")
    parser.add_argument('--source', default=os.path.abspath(os.curdir), dest="source_path")

    if __ARGCOMPLETE__:
        argcomplete.autocomplete(parser)

    args, extra_args = parser.parse_known_args()

    if shutil.which("docker") is None:
        raise SystemError('Docker not installed on system. Aborted.')

    subprocess.call(
        f'{shutil.which("docker")} run --rm -v "{args.source_path}:/src" 8env/mussel-python:{args.python_version} ' +
        f'{getpass.getuser()} ' + ' '.join(extra_args),
        shell=True,
    )

# docker run --rm -v "${PWD}:/src" 8env/mussel-python:3.6 --noconfirm --onefile --clean tes.py --distpath termkit/binary
