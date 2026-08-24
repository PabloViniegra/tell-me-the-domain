from src.payouts.service import request_payout


def test_valid_payout_starts_pending():
    assert request_payout(1, 1000).status == "PENDING"
