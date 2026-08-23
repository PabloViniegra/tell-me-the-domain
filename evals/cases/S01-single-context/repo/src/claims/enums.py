from enum import Enum


class ClaimStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    IN_REVIEW = "IN_REVIEW"
    PAID = "PAID"
    REJECTED = "REJECTED"
