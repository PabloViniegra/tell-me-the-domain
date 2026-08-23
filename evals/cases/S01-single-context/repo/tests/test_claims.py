from datetime import datetime

from src.claims.enums import ClaimStatus
from src.claims.exceptions import NoReviewerAssigned, PaymentBeforeReview
from src.claims.models import Claim
from src.claims.service import assign_reviewer, pay, review_deadline, submit


def make_claim() -> Claim:
    return Claim(id=1, hospital_id=7, insurer_ref="INS-1", amount_cents=12500, status=ClaimStatus.DRAFT)


def test_paying_without_reviewer_is_refused():
    claim = make_claim()
    submit(claim, datetime(2026, 1, 1))
    try:
        pay(claim)
    except NoReviewerAssigned:
        return
    raise AssertionError("expected NoReviewerAssigned")


def test_claim_cannot_be_paid_before_review():
    claim = make_claim()
    submit(claim, datetime(2026, 1, 1))
    try:
        pay(claim)
    except PaymentBeforeReview:
        return
    except NoReviewerAssigned:
        raise AssertionError("expected PaymentBeforeReview, got NoReviewerAssigned")
    raise AssertionError("expected PaymentBeforeReview")


def test_review_deadline_is_48_hours_after_submission():
    claim = make_claim()
    now = datetime(2026, 1, 1, 8, 0, 0)
    submit(claim, now)
    assign_reviewer(claim, reviewer_id=99)
    assert (review_deadline(claim) - now).total_seconds() == 48 * 3600
