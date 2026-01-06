from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, exists

from app.domain.entities import User
from app.domain.repositories import IUserRepository
from app.infrastructure.persistence.mappers import UserMapper
from app.infrastructure.persistence.models import UserModel


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID (only active users)"""
        user = self.session.scalars(
            select(UserModel).where(
                UserModel.id == user_id,
                UserModel.is_deleted == False,
            )
        ).first()
        return UserMapper.to_entity(user) if user else None

    def find_all(self) -> List[User]:
        """Retrieve all active users"""
        users = self.session.scalars(
            select(UserModel).where(UserModel.is_deleted == False)
        ).all()
        return [UserMapper.to_entity(u) for u in users]

    def save(self, user: User) -> User:
        """Insert or update user"""
        if user.id is not None:
            # Update existing
            existing = self.session.get(UserModel, user.id)
            if existing:
                existing.name = user.name
                existing.email = user.email
                existing.wage_amount = float(user.wage.amount)
                existing.wage_currency = user.wage.currency.value
                existing.is_deleted = user.is_deleted
                existing.deleted_at = user.deleted_at
                self.session.flush()
                self.session.refresh(existing)
                return UserMapper.to_entity(existing)

        # Insert new
        model = UserMapper.to_model(user)
        merged_model = self.session.merge(model)
        self.session.flush()
        self.session.refresh(merged_model)
        return UserMapper.to_entity(merged_model)

    def delete(self, user_id: int) -> bool:
        """Hard delete user by ID (use mark_as_deleted for soft delete)"""
        user = self.session.get(UserModel, user_id)
        if not user:
            return False

        self.session.delete(user)
        self.session.flush()
        return True

    def exists_by_email(self, email: str) -> bool:
        """Checks if a given email is registered and active (not deleted)"""
        exists_stmt = select(
            exists(
                select(UserModel).where(
                    UserModel.email.ilike(email),
                    UserModel.is_deleted == False,
                )
            )
        )
        result = self.session.scalar(exists_stmt)
        return result
