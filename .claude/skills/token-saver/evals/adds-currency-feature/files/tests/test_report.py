import unittest

from shop.models import Item
from shop.report import format_report, summarize


class ReportTests(unittest.TestCase):
    def test_summary_total(self):
        s = summarize([Item("A", "a", 10.0, 2), Item("B", "b", 1.5, 2)])
        self.assertEqual(s["total"], 23.0)

    def test_format_has_total_line(self):
        text = format_report(summarize([Item("A", "a", 10.0, 1)]))
        self.assertTrue(text.splitlines()[-1].startswith("TOTAL 10.00 USD"))
