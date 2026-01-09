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