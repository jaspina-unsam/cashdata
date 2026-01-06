# backend/cashdata/domain/value_objects/percentage.py
from dataclasses import dataclass
from decimal import Decimal
from app.domain.value_objects.money import Money
from app.domain.exceptions.domain_exceptions import InvalidPercentage


@dataclass(frozen=True, order=True)
class Percentage:
    """
    Representa un porcentaje (0-100%).

    Internamente guarda el valor como porcentaje (58.5 significa 58.5%),
    no como decimal (0.585).

    Ejemplos:
        Percentage(58.5)  # 58.5%
        Percentage(100)   # 100%
        Percentage(0)     # 0%
    """

    value: Decimal

    def __post_init__(self):
        # Normalizar a Decimal si viene como int/float
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, "value", Decimal(str(self.value)))

        # Validar rango
        if not (Decimal("0") <= self.value <= Decimal("100")):
            raise InvalidPercentage(
                f"Percentage must be between 0 and 100, got {self.value}"
            )

    @classmethod
    def from_decimal(cls, decimal: Decimal) -> "Percentage":
        """
        Crea Percentage desde decimal (0-1).

        Args:
            decimal: Valor entre 0 y 1 (ej: 0.585)

        Returns:
            Percentage (ej: 58.5%)
        """
        if not (Decimal("0") <= decimal <= Decimal("1")):
            raise InvalidPercentage(
                f"Decimal value must be between 0 and 1, got {decimal}"
            )
        return cls(decimal * 100)

    def to_decimal(self) -> Decimal:
        """
        Convierte a decimal (0-1) para cálculos.

        Returns:
            Decimal entre 0 y 1 (ej: 0.585)
        """
        return self.value / 100

    def apply_to(self, money: Money) -> Money:
        """
        Aplica el porcentaje a un monto de dinero.

        Args:
            money: Monto al que aplicar el porcentaje

        Returns:
            Nuevo Money con el porcentaje aplicado

        Example:
            >>> pct = Percentage(58.5)
            >>> money = Money(Decimal("1000"), Currency.ARS)
            >>> pct.apply_to(money)
            Money(amount=Decimal('585'), currency=Currency.ARS)
        """
        return money * self.to_decimal()

    def __add__(self, other: "Percentage") -> "Percentage":
        """Suma dos porcentajes"""
        if not isinstance(other, Percentage):
            raise InvalidPercentage(
                f"Cannot add Percentage with {type(other).__name__}"
            )

        total = self.value + other.value
        if total > 100:
            raise InvalidPercentage(
                f"Sum of percentages cannot exceed 100%: {self.value}% + {other.value}% = {total}%"
            )

        return Percentage(total)

    def __sub__(self, other: "Percentage") -> "Percentage":
        """Resta dos porcentajes"""
        if not isinstance(other, Percentage):
            raise InvalidPercentage(
                f"Cannot subtract {type(other).__name__} from Percentage"
            )

        result = self.value - other.value
        if result < 0:
            raise InvalidPercentage(
                f"Result of subtraction cannot be negative: {self.value}% - {other.value}% = {result}%"
            )

        return Percentage(result)

    def __str__(self) -> str:
        return f"{self.value}%"

    def __repr__(self) -> str:
        return f"Percentage({self.value})"

    def is_close_to(
        self, other: "Percentage", tolerance: Decimal = Decimal("0.0001")
    ) -> bool:
        """
        Compara si dos percentages son aproximadamente iguales.

        Args:
            other: Otro Percentage
            tolerance: Tolerancia permitida (default: 0.01%)

        Returns:
            True si la diferencia es menor que tolerance
        """
        if not isinstance(other, Percentage):
            return False

        diff = abs(self.value - other.value)
        return diff <= tolerance
