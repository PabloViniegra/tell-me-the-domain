import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config" / "fees"


def _load(insurer: str) -> dict:
    with (CONFIG_DIR / f"{insurer}.json").open() as f:
        return json.load(f)


def price(insurer: str, amount_cents: int) -> int:
    config = _load(insurer)
    rate = config["fee_percent"] / 100.0
    fee = round(amount_cents * rate)
    return amount_cents - fee
