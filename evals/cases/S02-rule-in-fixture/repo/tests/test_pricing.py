import json
from pathlib import Path

from src.pricing.engine import price

GOLDEN = Path(__file__).resolve().parent / "fixtures" / "golden" / "acme.json"


def test_pricing_matches_golden_fixtures():
    cases = json.loads(GOLDEN.read_text())["cases"]
    for case in cases:
        assert price("insurer-acme", case["amount_cents"]) == case["expected_price_cents"]
