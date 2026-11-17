from .config import TAX_RATE


def line_total(item):
    return round(item.price * item.qty * (1 + TAX_RATE), 2)
