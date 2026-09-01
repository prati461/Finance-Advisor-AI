from typing import Optional

from sqlalchemy.orm import Session

from backend.core.logging import logger
from backend.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
        logger.debug("UserRepository: Initialized")

    def get_by_email(self, email: str) -> Optional[User]:
        logger.info("UserRepository.get_by_email: Starting for email=%s", email)
        try:
            result = self.db.query(User).filter(User.email == email).first()
            logger.info("UserRepository.get_by_email: Complete, found=%s", result is not None)
            return result
        except Exception as e:
            logger.exception("UserRepository.get_by_email: Error - %s", e)
            raise

    def get_by_id(self, user_id: int) -> Optional[User]:
        logger.info("UserRepository.get_by_id: Starting for user_id=%s", user_id)
        try:
            result = self.db.query(User).filter(User.id == user_id).first()
            logger.info("UserRepository.get_by_id: Complete")
            return result
        except Exception as e:
            logger.exception("UserRepository.get_by_id: Error - %s", e)
            raise

    def create(self, user: User) -> User:
        logger.info("UserRepository.create: Starting for email=%s", user.email)
        try:
            logger.info("UserRepository.create: Adding user to session")
            self.db.add(user)
            logger.info("UserRepository.create: Committing transaction")
            self.db.commit()
            logger.info("UserRepository.create: Commit successful, refreshing user")
            self.db.refresh(user)
            logger.info("UserRepository.create: Complete, user_id=%s", user.id)
            return user
        except Exception as e:
            logger.exception("UserRepository.create: Error during create - %s", e)
            self.db.rollback()
            raise

    def update(self, user: User, changes: dict) -> User:
        logger.info("UserRepository.update: Starting for user_id=%s", user.id)
        try:
            for field, value in changes.items():
                if value is not None:
                    setattr(user, field, value)
            logger.info("UserRepository.update: Committing")
            self.db.commit()
            self.db.refresh(user)
            logger.info("UserRepository.update: Complete")
            return user
        except Exception as e:
            logger.exception("UserRepository.update: Error - %s", e)
            raise

    def delete(self, user: User) -> None:
        logger.info("UserRepository.delete: Starting for user_id=%s", user.id)
        try:
            self.db.delete(user)
            logger.info("UserRepository.delete: Committing")
            self.db.commit()
            logger.info("UserRepository.delete: Complete")
        except Exception as e:
            logger.exception("UserRepository.delete: Error - %s", e)
            raise
