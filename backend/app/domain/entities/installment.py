from dataclasses import dataclass
from datetime import date
from typing import Union
import re

from app.domain.value_objects.dual_money import DualMoney
from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class Installment:
    """
    Domain entity representing a single installment payment of a purchase or credit.

    Invariants:
    - installment_number must be >= 1
    - installment_number must be <= total_installments
    - total_installments must be >= 1
    - amount must be != 0 (negative for credits/bonifications)
    - billing_period must match YYYYMM format with valid month (01-12)
    - id can be None (before persistence)
    """

    id: int | None
    purchase_id: int
    installment_number: int
    total_installments: int
    amount: Union[DualMoney, Money]  # Accept both for backward compatibility
    billing_period: str
    manually_assigned_statement_id: int | None


    def __post_init__(self):
        """Validate invariants after initialization"""
        # Convert Money to DualMoney if needed for backward compatibility
        if isinstance(self.amount, Money):
            object.__setattr__(
                self,
                "amount",
                DualMoney(
                    primary_amount=self.amount.amount,
                    primary_currency=self.amount.currency,
                ),
            )
        # Validate total_installments
        if self.total_installments < 1:
            raise ValueError(
                f"total_installments must be >= 1, got {self.total_installments}"
            )

        # Validate installment_number
        if self.installment_number < 1:
            raise ValueError(
                f"installment_number must be >= 1, got {self.installment_number}"
            )

        if self.installment_number > self.total_installments:
            raise ValueError(
                f"installment_number ({self.installment_number}) cannot exceed "
                f"total_installments ({self.total_installments})"
            )

        # Validate billing_period format (YYYYMM)
        if not re.match(r"^\d{6}$", self.billing_period):
            raise ValueError(
                f"billing_period must be in YYYYMM format, got {self.billing_period}"
            )

        # Validate month is valid (01-12)
        month = int(self.billing_period[4:6])
        if not (1 <= month <= 12):
            raise ValueError(
                f"billing_period month must be between 01-12, got {month:02d}"
            )

    def __eq__(self, other):
        """Installments are equal if they have the same ID"""
        if not isinstance(other, Installment):
            return False
        if self.id is None and other.id is None:
            return self is other
        return self.id == other.id

    def __hash__(self):
        """Allow Installment to be used in sets/dicts"""
        return hash(self.id) if self.id is not None else id(self)
