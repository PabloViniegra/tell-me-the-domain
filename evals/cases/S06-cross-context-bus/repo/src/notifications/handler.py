import json

PAYLOAD_KEYS = {"invoice_id", "tenant_id", "amount_cents", "paid_at"}


def handle(event_json: str) -> dict:
    event = json.loads(event_json)
    if event["detail_type"] != "InvoicePaid":
        return {"status": "ignored"}
    payload = event["payload"]
    missing = PAYLOAD_KEYS - payload.keys()
    if missing:
        return {"status": "rejected", "missing": sorted(missing)}
    body = (
        f"Your invoice {payload['invoice_id']} for tenant {payload['tenant_id']} "
        f"was paid ({payload['amount_cents']} cents)."
    )
    return {
        "status": "queued",
        "to": "tenant@customers",
        "subject": "Receipt",
        "body": body,
    }
