"""Inventory value report."""
from .pricing import discounted_price, with_tax


def line_total(price, qty, discount=0.0):
    return round(with_tax(discounted_price(price, discount)) * qty, 2)


def report(items):
    """items: iterable of (sku, price, qty, discount)."""
    return {sku: line_total(price, qty, discount) for sku, price, qty, discount in items}
