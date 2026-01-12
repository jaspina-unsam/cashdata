from app.domain.entities.bank_account import BankAccount
from app.application.dtos.bank_account_dto import BankAccountResponseDTO


class BankAccountDTOMapper:
    """Maps between BankAccount entity and DTOs"""

    @staticmethod
    def to_response_dto(bank_account: BankAccount) -> BankAccountResponseDTO:
        """Convert domain entity to response DTO"""
        return BankAccountResponseDTO(
            id=bank_account.id,
            payment_method_id=bank_account.payment_method_id,
            primary_user_id=bank_account.primary_user_id,
            secondary_user_id=bank_account.secondary_user_id,
            name=bank_account.name,
            bank=bank_account.bank,
            account_type=bank_account.account_type,
            last_four_digits=bank_account.last_four_digits,
            currency=bank_account.currency,
        )