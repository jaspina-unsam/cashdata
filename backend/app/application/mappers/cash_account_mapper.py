from app.domain.entities.cash_account import CashAccount
from app.application.dtos.cash_account_dto import CashAccountResponseDTO


class CashAccountDTOMapper:
    """Maps between CashAccount entity and DTOs"""

    @staticmethod
    def to_response_dto(cash_account: CashAccount) -> CashAccountResponseDTO:
        """Convert domain entity to response DTO"""
        return CashAccountResponseDTO(
            id=cash_account.id,
            payment_method_id=cash_account.payment_method_id,
            user_id=cash_account.user_id,
            name=cash_account.name,
            currency=cash_account.currency,
        )