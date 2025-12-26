from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from cashdata.domain.entities import User
from cashdata.domain.repositories import IUserRepository
from cashdata.infrastructure.persistence.mappers import UserMapper
from cashdata.infrastructure.persistence.models import UserModel


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID"""
        user = self.session.get(UserModel, user_id)
        return UserMapper.to_entity(user) if user else None

    def find_all(self) -> List[User]:
        """Retrieve all users"""
        users = self.session.scalars(select(UserModel)).all()
        return [UserMapper.to_entity(u) for u in users]

    def save(self, user: User) -> User:
        """Insert or update user"""
        model = UserMapper.to_model(user)
        merged_model = self.session.merge(model)
        self.session.commit()
        self.session.refresh(merged_model)
        return UserMapper.to_entity(merged_model)

    def delete(self, user_id: int) -> bool:
        """Delete user by ID"""
        user = self.session.get(UserModel, user_id)
        if not user:
            return False

        self.session.delete(user)
        self.session.commit()
        return True
