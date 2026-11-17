import json

from .models import Item


def load_items(path):
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    return [Item(sku=r["sku"], name=r["name"], price=float(r["price"]), qty=int(r["qty"])) for r in raw]
