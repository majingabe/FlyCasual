import argparse
import sys

from .report import format_report, summarize
from .storage import load_items


def main(argv=None):
    parser = argparse.ArgumentParser(description="Print an inventory value report.")
    parser.add_argument("path", help="JSON file with items")
    args = parser.parse_args(argv)
    print(format_report(summarize(load_items(args.path))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
