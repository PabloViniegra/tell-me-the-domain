from datetime import datetime
import json
import os

import boto3  # type: ignore

EVENT_BUS_NAME = os.environ.get("EVENT_BUS_NAME", "orders-events")

_svc = boto3.client("events")


def place(order, now: datetime, items: list) -> dict:
    if not items:
        raise ValueError("order must have at least one item")
    order.items = list(items)
    order.placed_at = now
    return _publish("OrderPlaced", {"order_id": order.id, "customer_id": order.customer_id, "items": list(items), "at": now.isoformat()})


def ship(order) -> dict:
    if order.placed_at is None:
        raise DomainError("cannot ship an order that has never been placed")
    return _publish("OrderShipped", {"order_id": order.id, "at": datetime.utcnow().isoformat()})


def cancel(order) -> dict:
    if order.placed_at is None:
        raise DomainError("cannot cancel an order that has never been placed")
    return _publish("OrderCancelled", {"order_id": order.id, "at": datetime.utcnow().isoformat()})


def _publish(detail_type: str, payload: dict) -> dict:
    response = _svc.put_events(
        Entries=[
            {
                "EventBusName": EVENT_BUS_NAME,
                "Source": "orders.service",
                "DetailType": detail_type,
                "Detail": json.dumps(payload),
            }
        ]
    )
    return {"detail_type": detail_type, "payload": payload, "response": response}
