from cashdata.domain.entities.user import User
from cashdata.application.dtos.user_dto import UserResponseDTO


class UserDTOMapper:
    """Maps between User entity and DTOs"""

    @staticmethod
    def to_response_dto(user: User) -> UserResponseDTO:
        """Convert domain entity to response DTO (flatten value objects)"""
        return UserResponseDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            wage_amount=user.wage.amount,
            wage_currency=user.wage.currency,
        )
