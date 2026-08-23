from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Order:
    id: int
    customer_id: int
    items: list = field(default_factory=list)
    placed_at: datetime | None = None
