from .config import FEATURE_FLAGS
from .discounts import apply_automatic_renewal_discount


def calculate_charge(amount_cents: int, automatic_renewal: bool) -> int:
    if automatic_renewal and FEATURE_FLAGS["automatic_renewal_discount"]:
        return apply_automatic_renewal_discount(amount_cents)
    return amount_cents
