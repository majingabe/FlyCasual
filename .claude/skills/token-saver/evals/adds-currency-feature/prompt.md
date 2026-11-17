---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add multi-currency support to this shop project. Items in the JSON data can now carry an optional "currency" field (USD, EUR or GBP; default USD). Convert everything to USD for the report using 1 EUR = 1.08 USD and 1 GBP = 1.27 USD (keep the rates in shop/config.py). Add a --currency option to the CLI so the TOTAL line can be printed in USD, EUR or GBP (for example `TOTAL 57.04 EUR`), rounded to 2 decimals; USD stays the default. Keep the existing tests passing and add tests for the new behaviour. Tests run with `python3 -m unittest discover -s tests`.

Input files: shop/__init__.py, shop/config.py, shop/models.py, shop/storage.py, shop/pricing.py, shop/report.py, shop/cli.py, tests/test_pricing.py, tests/test_report.py, tests/test_cli.py, data/items.json
