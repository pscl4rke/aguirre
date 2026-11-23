

"""
This is an attempt to integrate Aguirre into Django's staticfiles.
It only sort-of works.  The settings.py would look something like:

    AGUIRRE_BASE_DIR = BASE_DIR / "packages"
    AGUIRRE_PREFIX = "/vendor"
    STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        "aguirre.integrations.django_staticfiles.StaticfilesFinder",
    ]

The `collectstatic` command did work, as long as you don't try to use --link.
Although it is full of bugs.

Serving up files when DEBUG=True doesn't work, and will probably never
work unless the Django devs dramatically alter their `serve(...)` functions.

Also, it's very slow because it reads the same tarball many times!

So, basically, this whole idea is a dead end.
"""


from contextlib import contextmanager
from typing import Iterable, Tuple

import datetime
from io import IOBase, BytesIO
import os
import tarfile

from aguirre.util import load_from_package, UTC

from django.conf import settings
from django.contrib.staticfiles.finders import BaseFinder


def available_packages(basedir: str) -> Iterable[Tuple[str, str, str]]:
    for filename in sorted(os.listdir(basedir)):
        if filename.endswith(".tgz"):
            package, hyphen, version = filename[:-4].partition("-")
            yield (package, version, filename)


def resources_in_package(basedir: str, package: str, version: str) -> Iterable[str]:
    srcpath = f"{basedir}/{package}-{version}.tgz"
    with tarfile.open(srcpath, "r:gz") as archive:
        for filename in archive.getnames():
            # I think I might need to filter out directories
            if filename.startswith("package/"):
                yield filename[8:]


class TarballStorage:

    def __init__(self, basedir: str, package: str, version: str, prefix: str) -> None:
        self.basedir = basedir
        self.package = package
        self.version = version
        self.prefix = prefix

    def path(self, path: str) -> str:
        return path

    def get_modified_time(self, path: str) -> datetime.datetime:
        return datetime.datetime(1970, 1, 1, tzinfo=UTC)  # meant to be immutable anyway

    @contextmanager  # type: ignore
    def open(self, urlpath: str) -> Iterable[IOBase]:
        urlprefix = f"{self.prefix}/{self.package}@{self.version}/"
        assert urlpath.startswith("urlprefix"), urlpath
        path = urlpath[len(urlprefix):]
        content = load_from_package(self.basedir, self.package, self.version, path)
        if content is None:
            raise Exception("Missing %s" % path)
        yield BytesIO(content)


class StaticfilesFinder(BaseFinder):

    # as used by "collectstatic"
    def list(self, ignore_patterns):  # type: ignore
        basedir = settings.AGUIRRE_BASE_DIR
        prefix = settings.AGUIRRE_PREFIX
        for package, version, filename in available_packages(basedir):
            storage = TarballStorage(basedir, package, version, prefix)
            for resourcepath in resources_in_package(basedir, package, version):
                urlpath = f"{prefix.strip('/')}/{package}@{version}/{resourcepath}"
                yield (urlpath, storage)

    # as used when DEBUG=True
    def find(self, path, find_all=False):  # type: ignore
        basedir = settings.AGUIRRE_BASE_DIR
        #prefix = settings.AGUIRRE_PREFIX
        matches: list = []
        for package, version, filename in available_packages(basedir):
            pass  # no... this isn't going to work is it...
        return matches
