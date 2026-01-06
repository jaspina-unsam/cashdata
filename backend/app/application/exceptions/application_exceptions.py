class ApplicationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class UserAlreadyExistsError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)

class UserNotFoundError(ApplicationError):
    def __init__(self, *args):
        super().__init__(*args)