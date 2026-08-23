from dataclasses import dataclass
from datetime import datetime


@dataclass
class Ticket:
    id: int
    tenant_id: int
    subject: str
    body: str
    opened_at: datetime | None = None
