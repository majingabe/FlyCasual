import unittest

from shop.models import Item
from shop.pricing import line_total


class LineTotalTests(unittest.TestCase):
    def test_line_total(self):
        self.assertEqual(line_total(Item("A", "a", 2.5, 4)), 10.0)

    def test_rounding(self):
        self.assertEqual(line_total(Item("A", "a", 0.333, 3)), 1.0)
