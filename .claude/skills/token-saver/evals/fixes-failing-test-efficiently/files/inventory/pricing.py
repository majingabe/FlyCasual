"""Price calculations for inventory items."""

TAX_RATE = 0.08


def discounted_price(price, discount):
    """Return price after a fractional discount (0.25 means 25% off)."""
    if not 0 <= discount < 1:
        raise ValueError("discount must be in [0, 1)")
    return round(price * discount, 2)


def with_tax(price):
    return round(price * (1 + TAX_RATE), 2)
