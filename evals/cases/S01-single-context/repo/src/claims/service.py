from datetime import datetime, timedelta

from .enums import ClaimStatus
from .exceptions import NoReviewerAssigned, PaymentBeforeReview
from .models import Claim

REVIEW_SLA_HOURS = 48


def submit(claim: Claim, now: datetime) -> None:
    claim.status = ClaimStatus.SUBMITTED
    claim.submitted_at = now


def assign_reviewer(claim: Claim, reviewer_id: int) -> None:
    claim.reviewer_id = reviewer_id
    claim.status = ClaimStatus.IN_REVIEW


def review_deadline(claim: Claim) -> datetime:
    return claim.submitted_at + timedelta(hours=REVIEW_SLA_HOURS)


def pay(claim: Claim) -> None:
    if claim.reviewer_id is None:
        raise NoReviewerAssigned()
    if claim.status is not ClaimStatus.IN_REVIEW:
        raise PaymentBeforeReview()
    claim.status = ClaimStatus.PAID


def reject(claim: Claim) -> None:
    claim.status = ClaimStatus.REJECTED
