# backend/cashdata/domain/value_objects/money.py
from enum import StrEnum
from dataclasses import dataclass
from decimal import Decimal
from app.domain.exceptions.domain_exceptions import InvalidMoneyOperation
from typing import Optional


class Currency(StrEnum):
    """Monedas soportadas por el sistema"""

    ARS = "ARS"
    USD = "USD"


@dataclass(frozen=True)
class Money:
    """
    Representa un valor monetario con su moneda.

    Value Object inmutable que garantiza precisión en cálculos monetarios
    usando Decimal en lugar de float.

    Attributes:
        amount: Cantidad de dinero (siempre Decimal)
        currency: Moneda del valor (default: ARS)

    Examples:
        >>> dinero = Money(Decimal("100"), Currency.ARS)
        >>> dinero + Money(Decimal("50"), Currency.ARS)
        Money(amount=Decimal('150'), currency=Currency.ARS)

        >>> dinero * 2
        Money(amount=Decimal('200'), currency=Currency.ARS)
    """

    amount: Decimal
    currency: Optional[Currency] = Currency.ARS

    def __post_init__(self):
        """Normaliza el amount a Decimal si viene en otro tipo"""
        if not isinstance(self.amount, Decimal):
            try:
                normalized_amount = Decimal(str(self.amount))
                object.__setattr__(self, "amount", normalized_amount)
            except Exception as e:
                raise InvalidMoneyOperation(f"Invalid type for Decimal: {e}")

    def __add__(self, other) -> "Money":
        """
        Suma dos montos de dinero.

        Args:
            other: Otro objeto Money

        Returns:
            Money con la suma de ambos montos

        Raises:
            InvalidMoneyOperation: Si other no es Money o las monedas no coinciden
        """
        if not isinstance(other, Money):
            raise InvalidMoneyOperation(
                f"Invalid operation between {self.__class__} and {other.__class__}"
            )

        if other.currency != self.currency:
            raise InvalidMoneyOperation(
                f"Currency mismatch: cannot add {self.currency} with {other.currency}"
            )

        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other) -> "Money":
        """
        Resta dos montos de dinero.

        Args:
            other: Otro objeto Money

        Returns:
            Money con la resta de ambos montos

        Raises:
            InvalidMoneyOperation: Si other no es Money o las monedas no coinciden
        """
        if not isinstance(other, Money):
            raise InvalidMoneyOperation(
                f"Invalid operation between {self.__class__} and {other.__class__}"
            )

        if other.currency != self.currency:
            raise InvalidMoneyOperation(
                f"Currency mismatch: cannot subtract {other.currency} from {self.currency}"
            )

        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, other) -> "Money":
        """
        Multiplica el monto por un número.

        Args:
            other: Número (int, float o Decimal)

        Returns:
            Money con el monto multiplicado

        Raises:
            InvalidMoneyOperation: Si other no es un número
        """
        if not isinstance(other, (int, float, Decimal)):
            raise InvalidMoneyOperation(
                f"Money can only be multiplied by numbers, not {type(other).__name__}"
            )

        return Money(self.amount * Decimal(str(other)), self.currency)

    def __truediv__(self, other) -> "Money":
        """
        Divide el monto por un número.

        Args:
            other: Número (int, float o Decimal)

        Returns:
            Money con el monto dividido

        Raises:
            InvalidMoneyOperation: Si other no es un número
            ZeroDivisionError: Si other es cero
        """
        if not isinstance(other, (int, float, Decimal)):
            raise InvalidMoneyOperation(
                f"Money can only be divided by numbers, not {type(other).__name__}"
            )

        return Money(self.amount / Decimal(str(other)), self.currency)

    def __eq__(self, other) -> bool:
        """
        Compara igualdad con otro Money.

        Dos Money son iguales si tienen el mismo monto Y la misma moneda.
        """
        if not isinstance(other, Money):
            return False

        return (self.amount == other.amount) and (self.currency == other.currency)

    def __ne__(self, other) -> bool:
        """Compara desigualdad con otro Money"""
        if not isinstance(other, Money):
            return True

        return (self.amount != other.amount) or (self.currency != other.currency)

    def __lt__(self, other) -> bool:
        """
        Compara si este Money es menor que otro.

        Raises:
            InvalidMoneyOperation: Si las monedas no coinciden
        """
        if not isinstance(other, Money):
            return NotImplemented

        if self.currency != other.currency:
            raise InvalidMoneyOperation(
                f"Cannot compare {self.currency} with {other.currency}"
            )

        return self.amount < other.amount

    def __gt__(self, other) -> bool:
        """
        Compara si este Money es mayor que otro.

        Raises:
            InvalidMoneyOperation: Si las monedas no coinciden
        """
        if not isinstance(other, Money):
            return NotImplemented

        if self.currency != other.currency:
            raise InvalidMoneyOperation(
                f"Cannot compare {self.currency} with {other.currency}"
            )

        return self.amount > other.amount

    def __le__(self, other) -> bool:
        """
        Compara si este Money es menor o igual que otro.

        Raises:
            InvalidMoneyOperation: Si las monedas no coinciden
        """
        if not isinstance(other, Money):
            return NotImplemented

        if self.currency != other.currency:
            raise InvalidMoneyOperation(
                f"Cannot compare {self.currency} with {other.currency}"
            )

        return self.amount <= other.amount

    def __ge__(self, other) -> bool:
        """
        Compara si este Money es mayor o igual que otro.

        Raises:
            InvalidMoneyOperation: Si las monedas no coinciden
        """
        if not isinstance(other, Money):
            return NotImplemented

        if self.currency != other.currency:
            raise InvalidMoneyOperation(
                f"Cannot compare {self.currency} with {other.currency}"
            )

        return self.amount >= other.amount

    def __str__(self) -> str:
        """
        Representación en string.

        Returns:
            String en formato "amount CURRENCY" (ej: "100.50 ARS")
        """
        return f"{self.amount} {self.currency}"

    def __repr__(self) -> str:
        """Representación para debugging"""
        return f"Money(amount={self.amount}, currency={self.currency})"

    def __round__(self, n: int = 0) -> "Money":
        """
        Redondea el monto a n decimales.

        Args:
            n: Número de decimales (default: 0)

        Returns:
            Nuevo Money con el monto redondeado

        Raises:
            TypeError: Si n no es int
            ValueError: Si n es negativo
        """
        if not isinstance(n, int):
            raise TypeError("Can only round with integer values")
        if n < 0:
            raise ValueError("Can only round with non-negative integers")

        return Money(round(self.amount, n), self.currency)

    def __abs__(self) -> "Money":
        """
        Retorna el valor absoluto del monto.

        Returns:
            Money con el monto en valor absoluto
        """
        return Money(abs(self.amount), self.currency)

    def __neg__(self) -> "Money":
        """
        Niega el monto (cambia el signo).

        Returns:
            Money con el monto negado

        Examples:
            >>> -Money(Decimal("100"), Currency.ARS)
            Money(amount=Decimal('-100'), currency=Currency.ARS)

            >>> -Money(Decimal("-100"), Currency.ARS)
            Money(amount=Decimal('100'), currency=Currency.ARS)
        """
        return Money(-self.amount, self.currency)

    def __pos__(self) -> "Money":
        """
        Operador unario + (identidad).

        Returns:
            El mismo Money sin cambios
        """
        return Money(self.amount, self.currency)

    def convert_to(self, target_currency: Currency, exchange_rate: Decimal) -> "Money":
        """
        Convierte este Money a otra moneda.

        Args:
            target_currency: Moneda destino
            exchange_rate: Cuántas unidades de target_currency vale 1 unidad de self.currency
                          Ej: Si self es USD y target es ARS, exchange_rate=1000 significa
                              1 USD = 1000 ARS

        Returns:
            Money en la nueva moneda

        Examples:
            >>> usd = Money(Decimal("100"), Currency.USD)
            >>> usd.convert_to(Currency.ARS, Decimal("1000"))
            Money(amount=Decimal('100000'), currency=Currency.ARS)
        """
        if self.currency == target_currency:
            return self

        if not isinstance(exchange_rate, Decimal):
            exchange_rate = Decimal(str(exchange_rate))

        converted_amount = self.amount * exchange_rate
        return Money(converted_amount, target_currency)
