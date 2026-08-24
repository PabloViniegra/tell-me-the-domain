from .models import Payout


MINIMUM_PAYOUT_CENTS = 1000


def request_payout(payout_id: int, amount_cents: int) -> Payout:
    if amount_cents < MINIMUM_PAYOUT_CENTS:
        raise ValueError("payout must be at least 1000 cents")
    return Payout(id=payout_id, amount_cents=amount_cents, status="PENDING")
