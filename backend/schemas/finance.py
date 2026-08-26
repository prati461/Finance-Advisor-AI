from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.utils.constants import ExpenseCategory, IncomeCategory, IncomeFrequency


class IncomeBase(BaseModel):
    source: str = Field(..., max_length=128)
    category: IncomeCategory
    amount: float = Field(..., gt=0)
    frequency: IncomeFrequency
    received_date: date
    description: Optional[str] = Field(None, max_length=512)

    model_config = ConfigDict(extra="forbid")


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    source: Optional[str] = Field(None, max_length=128)
    category: Optional[IncomeCategory] = None
    amount: Optional[float] = Field(None, gt=0)
    frequency: Optional[IncomeFrequency] = None
    received_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=512)

    model_config = ConfigDict(extra="forbid")


class IncomeRead(IncomeBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class ExpenseBase(BaseModel):
    category: ExpenseCategory
    amount: float = Field(..., gt=0)
    spent_at: date
    description: Optional[str] = Field(None, max_length=512)
    merchant: Optional[str] = Field(None, max_length=128)
    payment_method: Optional[str] = Field(None, max_length=64)

    model_config = ConfigDict(extra="forbid")


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    category: Optional[ExpenseCategory] = None
    amount: Optional[float] = Field(None, gt=0)
    spent_at: Optional[date] = None
    description: Optional[str] = Field(None, max_length=512)
    merchant: Optional[str] = Field(None, max_length=128)
    payment_method: Optional[str] = Field(None, max_length=64)

    model_config = ConfigDict(extra="forbid")


class ExpenseRead(ExpenseBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class BudgetBase(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    category: ExpenseCategory
    budget_amount: float = Field(..., ge=0)
    alert_threshold_pct: float = Field(80.0, ge=0, le=100)

    model_config = ConfigDict(extra="forbid")


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = Field(None, ge=2000, le=2100)
    category: Optional[ExpenseCategory] = None
    budget_amount: Optional[float] = Field(None, ge=0)
    alert_threshold_pct: Optional[float] = Field(None, ge=0, le=100)

    model_config = ConfigDict(extra="forbid")


class BudgetRead(BudgetBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class MonthlySummaryResponse(BaseModel):
    income_total: float
    expense_total: float
    savings_total: float

    model_config = ConfigDict(extra="forbid")
