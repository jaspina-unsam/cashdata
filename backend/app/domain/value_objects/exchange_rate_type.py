from enum import StrEnum, auto


class ExchangeRateType(StrEnum):
    OFFICIAL = auto()
    BLUE = auto()
    MEP = auto()
    CCL = auto()
    CUSTOM = auto()
    INFERRED = auto()