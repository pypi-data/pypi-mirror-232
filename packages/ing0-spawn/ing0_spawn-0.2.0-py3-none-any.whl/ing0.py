#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import subprocess

from lxml.html import fromstring as string2html
import requests


DEBUG = os.environ.get("DEBUG")

URL = 'https://uk.lxd.images.canonical.com/images/'


def run(command, verbose=False):
    print("** subprocess.run({})".format(command))
    if verbose:
        return subprocess.run(command, shell=True, check=True, capture_output=True)
    else:
        return subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _images_index_fetch(url):
    try:
        response = requests.get(url)
        html = string2html(response.text)
        directories = html.xpath('//tr/td/a/text()')
        directories.remove('Parent Directory')
        latest = [x.rstrip('/') for x in sorted(directories, reverse=True)]
        return latest
    except Exception:
        if DEBUG:
            raise


def _images_iter_available():
    images = _images_index_fetch(URL)
    if images is None:
        print("Oops, can not query rootfs directory")
        sys.exit(42)
    for distribution in images:
        releases = _images_index_fetch(URL + distribution)
        for release in releases:
            for arch in ['amd64', 'arm64']:
                yield from _images_iter_available_version(distribution, release, arch)

def _images_iter_available_version(distribution, release, arch):
    builds = _images_index_fetch(URL + distribution + '/' + release + '/' + arch + '/default/')
    if builds is None:
        return
    url = "{URL}{distribution}/{release}/{arch}/default/{build}/"
    for build in builds:
        url = url.format(
            URL=URL,
            distribution=distribution,
            release=release,
            arch=arch,
            build=build
        )
        yield url


def cli_images_available():
    for url in _images_iter_available():
        print(url)


def usage():
    print("""Usage:

  ing0 available
  ing0 create NAME DISTRIBUTION RELEASE ARCH"
  ing0 exec NAME -- COMMAND ...
""")

def _images_latest(distribution, release, arch):
    out = list(_images_iter_available_version(distribution, release, arch))
    try:
        return out[-1]
    except IndexError:
        return None

def cli_create(name, distribution, release, arch):
    print("* ing0: making {}".format(name))
    work = Path.home() / '.local' / 'ing0' / name
    work.mkdir(parents=True, exist_ok=True)
    root = _images_latest(distribution, release, arch)
    url = root + 'rootfs.tar.xz'
    run("cd {work} && wget '{url}'".format(work=work, url=url))
    url = root + 'SHA256SUMS'
    run("cd {work} && wget '{url}'".format(work=work, url=url))
    run("cd {work} && fgrep rootfs.tar.xz SHA256SUMS | sha256sum -c -".format(work=work))
    run("cd {work} && tar xf rootfs.tar.xz".format(work=work))
    # XXX: delete machine-id because it clash with systemd-d128 later in exec
    run("cd {work} && rm etc/machine-id".format(work=work))
    # XXX: delete resolve.conf, and copy the host one when needed in exec
    run("cd {work} && rm etc/resolv.conf".format(work=work), verbose=True)
    print("* ing0: what is done is not to be done!")

def cli_exec(name, *extra):
    print("* ing0: making {}".format(name))
    work = Path.home() / '.local' / 'ing0' / name
    run("cd {work} && cp /etc/resolv.conf etc/resolv.conf".format(work=work))
    command = "systemd-nspawn --uuid=$(systemd-id128 new) -D '{work}' --bind={cwd}:/mnt"
    command = command.format(work=work, cwd=Path.cwd())
    if extra:
        command += ' ' + ' '.join(extra)
    code = subprocess.run(command, shell=True).returncode
    # foward systemd-nspawn exit code
    sys.exit(code)

def main():
    match sys.argv[1:]:
        case ['available', *args]:
            cli_images_available()
        case ['create', *args]:
            cli_create(*args)
        case ['exec', *args]:
            cli_exec(*args)
        case _:
            usage()

if __name__ == "__main__":
    main()
