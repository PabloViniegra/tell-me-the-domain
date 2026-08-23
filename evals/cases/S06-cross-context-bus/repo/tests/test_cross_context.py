from src.billing.models import Invoice
from src.billing.service import encode, mark_paid
from src.notifications.handler import handle


def test_invoice_paid_event_triggers_notification():
    invoice = Invoice(id=1, tenant_id=7, amount_cents=12500, status="PENDING")
    event = mark_paid(invoice, now=__import__("datetime").datetime(2026, 1, 1, 12))
    out = handle(encode(event))
    assert out["status"] == "queued"


def test_wrong_event_type_is_ignored():
    event = {"detail_type": "SomethingElse", "payload": {}}
    out = handle(encode(event))
    assert out["status"] == "ignored"


def test_missing_payload_field_is_rejected():
    event = {"detail_type": "InvoicePaid", "payload": {"invoice_id": 1, "tenant_id": 7, "amount_cents": 100}}
    out = handle(encode(event))
    assert out["status"] == "rejected"
