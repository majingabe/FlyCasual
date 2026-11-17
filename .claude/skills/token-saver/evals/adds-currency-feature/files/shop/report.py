from .config import BASE_CURRENCY
from .pricing import line_total


def summarize(items):
    lines = [(it.sku, it.name, line_total(it)) for it in items]
    return {"lines": lines, "total": round(sum(t for _, _, t in lines), 2), "currency": BASE_CURRENCY}


def format_report(summary):
    out = [f"{sku:<6} {name:<20} {total:>10.2f}" for sku, name, total in summary["lines"]]
    out.append(f"TOTAL {summary['total']:.2f} {summary['currency']}")
    return "\n".join(out)
