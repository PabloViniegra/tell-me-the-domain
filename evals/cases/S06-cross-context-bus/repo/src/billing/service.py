import json
from datetime import datetime

INVOICE_BUS = "billing-events"

def mark_paid(invoice, now: datetime) -> dict:
    invoice.status = "PAID"
    invoice.paid_at = now
    return {
        "detail_type": "InvoicePaid",
        "payload": {
            "invoice_id": invoice.id,
            "tenant_id": invoice.tenant_id,
            "amount_cents": invoice.amount_cents,
            "paid_at": now.isoformat(),
        },
    }


def encode(event: dict) -> str:
    return json.dumps(event)
