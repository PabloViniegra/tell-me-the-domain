from datetime import datetime, timedelta

from src.refunds.service import can_refund


def test_refund_within_30_days_is_allowed():
    now = datetime(2026, 1, 1)
    assert can_refund(now, now + timedelta(days=15))


def test_refund_after_30_days_is_refused():
    now = datetime(2026, 1, 1)
    try:
        can_refund(now, now + timedelta(days=31))
    except Exception:
        return
    raise AssertionError("expected RefundWindowExpired")
