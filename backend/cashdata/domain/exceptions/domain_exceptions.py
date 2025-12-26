class DomainException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidMoneyOperation(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidPeriodFormat(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidPercentage(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidEntity(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)

class InvalidCalculation(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
