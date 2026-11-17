import contextlib
import io
import os
import unittest

from shop.cli import main

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "items.json")


class CliTests(unittest.TestCase):
    def test_total_line(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(main([DATA]), 0)
        self.assertEqual(buf.getvalue().strip().splitlines()[-1], "TOTAL 105.50 USD")
