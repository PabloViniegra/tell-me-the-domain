from datetime import datetime, timedelta

from src.orders.models import Order
from src.orders.service import place, ship, cancel


def make_order() -> Order:
    return Order(id=1, customer_id=42)


def test_order_with_no_items_is_refused():
    order = make_order()
    try:
        place(order, datetime(2026, 1, 1), items=[])
    except ValueError:
        return
    raise AssertionError("expected ValueError for empty items")


def test_shipping_a_placed_order_publishes_an_event():
    order = make_order()
    place(order, datetime(2026, 1, 1), items=["x"])
    event = ship(order)
    assert event["detail_type"] == "OrderShipped"
    assert event["payload"]["order_id"] == 1


def test_cancellation_after_placement_publishes_an_event():
    order = make_order()
    place(order, datetime(2026, 1, 1), items=["x"])
    event = cancel(order)
    assert event["detail_type"] == "OrderCancelled"
