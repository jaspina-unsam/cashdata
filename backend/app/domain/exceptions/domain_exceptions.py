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


class InvalidStatementDateRange(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class PaymentMethodNameError(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class PaymentMethodInstallmentsError(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class BankAccountNameError(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class BankAccountUserError(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidProviderError(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ExchangeRateNotFound(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
