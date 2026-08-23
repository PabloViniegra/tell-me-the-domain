from datetime import datetime, timedelta

REFUND_WINDOW_DAYS = 30


class RefundWindowExpired(Exception):
    pass


def can_refund(created_at: datetime, refund_requested_at: datetime) -> bool:
    delta = refund_requested_at - created_at
    if delta > timedelta(days=REFUND_WINDOW_DAYS):
        raise RefundWindowExpired()
    return True
