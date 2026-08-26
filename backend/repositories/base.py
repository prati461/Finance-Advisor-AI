from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type[ModelType]) -> None:
        self.db = db
        self.model = model

    def add(self, instance: ModelType) -> ModelType:
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelType) -> None:
        self.db.delete(instance)
        self.db.commit()

    def update(self, instance: ModelType, changes: dict) -> ModelType:
        for field, value in changes.items():
            if value is not None:
                setattr(instance, field, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance
