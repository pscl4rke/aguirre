

import unittest

from aguirre.util import guess_mime_type


class TestUtil(unittest.TestCase):

    def test_guessing_the_mimetype(self):
        self.assertEqual(guess_mime_type("/foo/thing.js"), "text/javascript")
        self.assertEqual(guess_mime_type("/foo/thing.css"), "text/css")
        self.assertEqual(guess_mime_type("/foo/thing.xyz"), "text/html")
