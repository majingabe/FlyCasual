import unittest

from inventory.pricing import discounted_price, with_tax
from inventory.report import line_total, report
from inventory.stock import Stock


class PricingTests(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(discounted_price(20.0, 0), 20.0)

    def test_quarter_off(self):
        self.assertEqual(discounted_price(20.0, 0.25), 15.0)

    def test_tax(self):
        self.assertEqual(with_tax(10.0), 10.8)


class ReportTests(unittest.TestCase):
    def test_line_total(self):
        self.assertEqual(line_total(10.0, 3, 0.5), 16.2)

    def test_report(self):
        self.assertEqual(report([("a", 10.0, 1, 0.0)]), {"a": 10.8})


class StockTests(unittest.TestCase):
    def test_add_remove(self):
        s = Stock()
        s.add("x", 5)
        s.remove("x", 2)
        self.assertEqual(s.quantity("x"), 3)

    def test_overdraw(self):
        s = Stock()
        with self.assertRaises(ValueError):
            s.remove("x", 1)


if __name__ == "__main__":
    unittest.main()
