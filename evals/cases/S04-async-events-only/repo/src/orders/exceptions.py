class DomainError(Exception):
    pass


class OrderNotCancellable(DomainError):
    pass
