from dataclasses import dataclass
from datetime import datetime


@dataclass
class Invoice:
    id: int
    tenant_id: int
    amount_cents: int
    status: str
    paid_at: datetime | None = None
