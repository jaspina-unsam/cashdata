from dataclasses import dataclass

from app.application.exceptions.application_exceptions import (
    InstallmentNotFoundError,
    PurchaseNotFoundError,
    BusinessRuleViolationError,
)
from app.domain.repositories.iunit_of_work import IUnitOfWork


@dataclass(frozen=True)
class DeleteInstallmentCommand:
    """Command to delete an installment"""

    installment_id: int
    user_id: int


class DeleteInstallmentUseCase:
    """
    Use case to delete an existing installment.

    Business Rules:
    - Installment must exist and belong to user's purchase
    - Cannot delete the last remaining installment of a purchase
    - Deletion is permanent (hard delete)
    """

    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    def execute(self, command: DeleteInstallmentCommand) -> None:
        """
        Deletes an existing installment

        Args:
            command: Delete command with installment ID and user ID

        Raises:
            InstallmentNotFoundError: If installment doesn't exist
            PurchaseNotFoundError: If purchase doesn't belong to user
            BusinessRuleViolationError: If trying to delete the last installment
        """
        with self._uow:
            # Find existing installment
            installment = self._uow.installments.find_by_id(command.installment_id)
            if not installment:
                raise InstallmentNotFoundError(f"Installment with ID {command.installment_id} not found")

            # Verify ownership through purchase
            purchase = self._uow.purchases.find_by_id(installment.purchase_id)
            if not purchase or purchase.user_id != command.user_id:
                raise PurchaseNotFoundError(f"Installment {command.installment_id} does not belong to user {command.user_id}")

            # Check business rule: cannot delete last installment
            all_installments = self._uow.installments.find_by_purchase_id(purchase.id)
            if len(all_installments) <= 1:
                raise BusinessRuleViolationError("Cannot delete the last remaining installment of a purchase")

            # Delete associated budget expenses first (FK constraint)
            budget_expenses = self._uow.budget_expenses.find_by_installment_id(command.installment_id)
            for expense in budget_expenses:
                self._uow.budget_expenses.delete(expense.id)

            # Delete the installment
            deleted = self._uow.installments.delete(command.installment_id)
            if not deleted:
                raise InstallmentNotFoundError(f"Installment with ID {command.installment_id} not found during deletion")

            self._uow.commit()