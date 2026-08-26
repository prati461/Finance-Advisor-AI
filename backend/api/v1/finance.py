from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.api.v1.dependencies import get_current_user, get_db_session
from backend.schemas.finance import MonthlySummaryResponse
from backend.services.finance_service import FinanceService

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/summary", response_model=MonthlySummaryResponse)
def monthly_summary(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> MonthlySummaryResponse:
    service = FinanceService(db)
    start_date = None
    end_date = None
    if month is not None and year is not None:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
    summary = service.get_monthly_summary(current_user.id, start_date=start_date, end_date=end_date)
    return MonthlySummaryResponse(**summary)
