from enum import StrEnum, auto


class PaymentMethodType(StrEnum):
    CREDIT_CARD = auto()
    CASH = auto()
    BANK_ACCOUNT = auto()
    DIGITAL_WALLET = auto()
