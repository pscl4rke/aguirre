

from os.path import dirname, join
import unittest

from aguirre import util


def example_dir():
    return join(dirname(__file__), "examples")


class TestTarballLowLevelAccess(unittest.TestCase):

    def setUp(self):
        self.tarpath = join(example_dir(), "vanjs-core-1.5.0.tgz")
        self.badpath = join(example_dir(), "not-an-archive.txt")

    def test_loading_a_good_file(self):
        result = util.load_from_tarball(self.tarpath, "package/src/van.js")
        self.assertEqual(len(result), 4917)

    def test_failing_on_a_bad_file(self):
        with self.assertRaises(KeyError):
            util.load_from_tarball(self.tarpath, "src/van.js")

    def test_failing_on_a_bad_archive(self):
        with self.assertRaises(Exception):
            util.load_from_tarball(self.badpath, "package/src/van.js")


class TestMimeTypes(unittest.TestCase):

    def test_guessing_the_mimetype(self):
        self.assertEqual(util.guess_mime_type("/foo/thing.js"), "text/javascript")
        self.assertEqual(util.guess_mime_type("/foo/thing.css"), "text/css")
        self.assertEqual(util.guess_mime_type("/foo/thing.xyz"), "text/html")
