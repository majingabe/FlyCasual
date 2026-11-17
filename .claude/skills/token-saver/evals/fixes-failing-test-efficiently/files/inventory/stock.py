"""Stock bookkeeping."""


class Stock:
    def __init__(self):
        self._qty = {}

    def add(self, sku, qty):
        if qty <= 0:
            raise ValueError("qty must be positive")
        self._qty[sku] = self._qty.get(sku, 0) + qty

    def remove(self, sku, qty):
        have = self._qty.get(sku, 0)
        if qty > have:
            raise ValueError(f"only {have} of {sku} in stock")
        self._qty[sku] = have - qty

    def quantity(self, sku):
        return self._qty.get(sku, 0)
