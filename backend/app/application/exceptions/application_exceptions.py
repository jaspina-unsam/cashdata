class ApplicationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class UserAlreadyExistsError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class UserNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class CreditCardNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class CreditCardOwnerMismatchError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class PurchaseNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class CategoryNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class InstallmentNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class MonthlyStatementNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class BusinessRuleViolationError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class PaymentMethodNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class PaymentMethodOwnershipError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class PaymentMethodInstallmentError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class CreditCardNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class BudgetNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)


class BudgetExpenseNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)
