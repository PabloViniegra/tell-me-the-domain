class ClaimError(Exception):
    pass


class NoReviewerAssigned(ClaimError):
    pass


class PaymentBeforeReview(ClaimError):
    pass
