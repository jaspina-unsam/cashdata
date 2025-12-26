# backend/cashdata/domain/value_objects/period.py
from dataclasses import dataclass
from datetime import date
from cashdata.domain.exceptions.domain_exceptions import InvalidPeriodFormat


@dataclass(frozen=True, order=True)
class Period:
    """
    Representa un periodo mensual (año/mes).

    Formato interno: año (int) y mes (int)
    Formato string: YYYYMM (ej: "202512")

    Ejemplos:
        Period(2025, 12)
        Period.from_string("202512")
        Period.from_date(date(2025, 12, 15))
    """

    year: int
    month: int

    def __post_init__(self):
        if not (1 <= self.month <= 12):
            raise InvalidPeriodFormat(
                f"Month must be between 1 and 12, got {self.month}"
            )
        if self.year < 2000:
            raise InvalidPeriodFormat(f"Year must be >= 2000, got {self.year}")

    @classmethod
    def from_string(cls, period_str: str) -> "Period":
        """Crea Period desde string YYYYMM"""
        if len(period_str) != 6 or not period_str.isdigit():
            raise InvalidPeriodFormat(
                f"Period string must be YYYYMM format, got '{period_str}'"
            )

        year = int(period_str[:4])
        month = int(period_str[4:])
        return cls(year, month)

    @classmethod
    def from_date(cls, dt: date) -> "Period":
        """Crea Period desde date object"""
        return cls(dt.year, dt.month)

    @classmethod
    def current(cls) -> "Period":
        """Retorna el periodo actual"""
        return cls.from_date(date.today())

    def to_string(self) -> str:
        """Convierte a formato YYYYMM"""
        return f"{self.year}{self.month:02d}"

    def next(self) -> "Period":
        """Retorna el periodo siguiente"""
        if self.month == 12:
            return Period(self.year + 1, 1)
        return Period(self.year, self.month + 1)

    def previous(self) -> "Period":
        """Retorna el periodo anterior"""
        if self.month == 1:
            return Period(self.year - 1, 12)
        return Period(self.year, self.month - 1)

    def add_months(self, months: int) -> "Period":
        """Suma N meses al periodo"""
        total_months = (self.year * 12 + self.month - 1) + months
        year = total_months // 12
        month = (total_months % 12) + 1
        return Period(year, month)

    def __str__(self) -> str:
        return self.to_string()
