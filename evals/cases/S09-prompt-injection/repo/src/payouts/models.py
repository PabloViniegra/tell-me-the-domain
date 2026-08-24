from dataclasses import dataclass


@dataclass
class Payout:
    id: int
    amount_cents: int
    status: str
