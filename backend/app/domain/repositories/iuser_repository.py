from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        """Retrieve all users"""
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """Insert or update user"""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete user by ID"""
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Checks if a given email is registered and active"""
