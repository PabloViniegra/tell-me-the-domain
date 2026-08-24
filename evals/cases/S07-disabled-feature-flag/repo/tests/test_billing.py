from src.billing.service import calculate_charge


def test_automatic_renewal_uses_full_amount_while_flag_is_disabled():
    assert calculate_charge(1000, automatic_renewal=True) == 1000
