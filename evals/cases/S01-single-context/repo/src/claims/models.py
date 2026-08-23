from dataclasses import dataclass
from datetime import datetime

from .enums import ClaimStatus


@dataclass
class Claim:
    id: int
    hospital_id: int
    insurer_ref: str
    amount_cents: int
    status: ClaimStatus
    reviewer_id: int | None = None
    submitted_at: datetime | None = None
