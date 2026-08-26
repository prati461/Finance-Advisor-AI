from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.generics import GenericModel


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    model_config = ConfigDict(extra="forbid")


T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: list[T]
