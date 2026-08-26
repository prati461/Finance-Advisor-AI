"""
AI-Powered Finance API Routes

New AI endpoints for financial health, recommendations, predictions, and more.
All routes use the authenticated user's data from the database.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.api.v1.dependencies import get_current_user, get_db_session
from backend.models.user import User
from backend.models.advisor import AdvisorRecord, AIConversation
from pydantic import BaseModel, Field

from backend.schemas.ai import (
    AnalyticsRequest,
    AnalyticsResponse,
    BudgetOptimizerResponse,
    ChatRequest,
    ChatResponse,
    FinancialHealthResponse,
    FraudDetectionResponse,
    HousePriceRequest,
    HousePriceResponse,
    InvestmentAdvisorResponse,
    PortfolioRecommendationResponse,
    RecommendationsResponse,
    ReportRequest,
    SpendingForecastResponse,
    StockPredictionRequest,
    StockPredictionResponse,
)
from backend.ml.services.financial_health import FinancialHealthEngine
from backend.ml.services.recommendations import RecommendationEngine

router = APIRouter(prefix="/ai", tags=["ai"])


# ---- Request models for new endpoints ----
class MarketAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Symbol or asset name (e.g., RELIANCE, NIFTY 50)")


class ComparisonRequest(BaseModel):
    symbols: list[str] = Field(..., description="List of symbols to compare")


class MutualFundRequest(BaseModel):
    fund: str = Field(..., description="Mutual fund key (e.g., NIFTY 50 INDEX FUND)")


class WealthProjectionRequest(BaseModel):
    monthly_sip: float = Field(10000, gt=0)
    years: int = Field(5, ge=1, le=50)
    expected_return: float = Field(12.0, gt=0)
    current_amount: float = Field(0, ge=0)
    inflation_rate: float = Field(6.0, ge=0)


@router.post(
    "/financial-health",
    response_model=FinancialHealthResponse,
    summary="Calculate Financial Health Score",
    description="Calculates comprehensive financial health score (0-100) using user's real financial data.",
)
def get_financial_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> FinancialHealthResponse:
    """Calculate financial health score for the current user."""
    engine = FinancialHealthEngine(db, current_user.id)
    result = engine.calculate_overall_health_score()
    db.add(AdvisorRecord(user_id=current_user.id, record_type="financial_health", payload=result))
    db.commit()
    return FinancialHealthResponse(**result)


@router.post(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="Generate AI Recommendations",
    description="Generates personalized financial recommendations based on user's financial data.",
)
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> RecommendationsResponse:
    """Generate personalized financial recommendations."""
    engine = RecommendationEngine(db, current_user.id)
    result = engine.generate_recommendations()
    db.add(AdvisorRecord(user_id=current_user.id, record_type="recommendations", payload=result))
    db.commit()
    return RecommendationsResponse(**result)


@router.post(
    "/budget-optimizer",
    response_model=BudgetOptimizerResponse,
    summary="Optimize Budgets",
    description="Analyzes spending patterns and suggests optimized budget allocations.",
)
def optimize_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """Optimize budgets based on spending analysis."""
    # Placeholder - will be implemented in Phase 5B
    from backend.ml.services.budget_optimizer import BudgetOptimizer
    optimizer = BudgetOptimizer(db, current_user.id)
    result = optimizer.optimize()
    return BudgetOptimizerResponse(**result)


@router.post(
    "/spending-forecast",
    response_model=SpendingForecastResponse,
    summary="Forecast Spending",
    description="Predicts next month's income, expenses, and savings using ML models.",
)
def forecast_spending(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """Forecast future spending patterns."""
    # Placeholder - will be implemented in Phase 5B
    from backend.ml.services.spending_forecast import SpendingForecast
    forecast = SpendingForecast(db, current_user.id)
    result = forecast.forecast()
    return SpendingForecastResponse(**result)


@router.post(
    "/investment-advisor",
    response_model=InvestmentAdvisorResponse,
    summary="Investment Advisor",
    description="Provides personalized investment plan based on income, savings, and risk profile.",
)
def get_investment_advice(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """Generate investment advice."""
    # Placeholder - will be implemented in Phase 5C
    from backend.ml.services.investment_advisor import InvestmentAdvisor
    advisor = InvestmentAdvisor(db, current_user.id)
    result = advisor.advise()
    db.add(AdvisorRecord(user_id=current_user.id, record_type="investment_advice", payload=result))
    db.commit()
    return InvestmentAdvisorResponse(**result)


@router.post(
    "/portfolio",
    response_model=PortfolioRecommendationResponse,
    summary="Portfolio Recommendation",
    description="Recommends a diversified investment portfolio with risk/return analysis.",
)
def get_portfolio_recommendation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """Generate portfolio recommendation."""
    # Placeholder - will be implemented in Phase 5C
    from backend.ml.services.portfolio import PortfolioRecommender
    recommender = PortfolioRecommender(db, current_user.id)
    result = recommender.recommend()
    db.add(AdvisorRecord(user_id=current_user.id, record_type="portfolio", payload=result))
    db.commit()
    return PortfolioRecommendationResponse(**result)


@router.post(
    "/stock-predict",
    response_model=StockPredictionResponse,
    summary="Predict Stock Prices",
    description="Predicts stock prices for tomorrow, 7 days, and 30 days using trained ML models.",
)
def predict_stock(
    request: StockPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """Predict stock prices."""
    # Placeholder - will be implemented in Phase 5D
    from backend.ml.services.stock_predictor import StockPredictor
    predictor = StockPredictor()
    try:
        result = predictor.predict(request.symbol)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Market prediction is temporarily unavailable. Please try again later.",
        ) from exc
    db.add(AdvisorRecord(user_id=current_user.id, record_type="prediction", payload=result))
    db.commit()
    return StockPredictionResponse(**result)


@router.post(
    "/house-price-predict",
    response_model=HousePriceResponse,
    summary="Predict House Prices",
    description="Predicts house prices based on area, bedrooms, bathrooms, and location.",
)
def predict_house_price(
    request: HousePriceRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict house prices."""
    # Placeholder - will be implemented in Phase 5E
    from backend.ml.services.house_price_predictor import HousePricePredictor
    predictor = HousePricePredictor()
    result = predictor.predict(request)
    return HousePriceResponse(**result)


@router.post(
    "/fraud-detection",
    response_model=FraudDetectionResponse,
    summary="Detect Fraudulent Transactions",
    description="Analyzes expenses for anomalies and potential fraudulent transactions.",
)
def detect_fraud(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """Detect fraudulent transactions."""
    # Placeholder - will be implemented later
    return FraudDetectionResponse(
        alerts=[],
        total_analyzed=0,
        suspicious_count=0,
    )


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="AI Chat Assistant",
    description="AI-powered financial assistant that answers questions using user's financial data.",
)
def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """Chat with AI financial assistant."""
    # Placeholder - will be implemented later
    from backend.ml.services.chatbot import FinancialChatbot
    chatbot = FinancialChatbot(db, current_user.id)
    result = chatbot.respond(request.message)
    db.add(
        AIConversation(
            user_id=current_user.id,
            message=request.message,
            response=result["response"],
            source=result.get("source") or "analytics",
        )
    )
    db.commit()
    return ChatResponse(**result)


@router.post(
    "/reports",
    summary="Generate Financial Report",
    description="Generates monthly financial reports in PDF or CSV format.",
)
def generate_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """Generate financial reports."""
    # Placeholder - will be implemented later
    return {
        "message": f"Report generation for {request.month}/{request.year} in {request.format} format - coming soon",
        "status": "pending",
    }


@router.post(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Get Financial Analytics",
    description="Provides advanced analytics including trends, category analysis, and period comparisons.",
)
def get_analytics(
    request: AnalyticsRequest = AnalyticsRequest(period="monthly"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """Get financial analytics."""
    # Placeholder - will be implemented later
    return AnalyticsResponse(
        period=request.period,
        total_income=0,
        total_expense=0,
        total_savings=0,
        savings_rate=0,
        income_trend=[],
        expense_trend=[],
        savings_trend=[],
        category_analysis=[],
    )


@router.post(
    "/market-analysis",
    summary="Market Analysis",
    description="Runs full 5-year + technical analysis for a symbol using real market data.",
)
def market_analysis(
    request: MarketAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """Full market analysis for a symbol."""
    from backend.ml.analytics.analysis import market_analysis_service

    result = market_analysis_service.full_analysis(request.symbol)
    return result


@router.post(
    "/compare",
    summary="Compare Assets",
    description="Compares multiple assets using real historical data.",
)
def compare_assets(
    request: ComparisonRequest,
    current_user: User = Depends(get_current_user),
):
    """Compare multiple assets."""
    from backend.ml.analytics.analysis import market_analysis_service

    result = market_analysis_service.comparison(request.symbols)
    return result


@router.post(
    "/sector-performance",
    summary="Sector Performance",
    description="Returns sector performance based on real stock data.",
)
def get_sector_performance(
    current_user: User = Depends(get_current_user),
):
    """Get sector performance."""
    from backend.ml.analytics.analysis import market_analysis_service

    result = market_analysis_service.sector_performance()
    return {"sectors": result}


@router.post(
    "/market-overview",
    summary="Market Overview",
    description="Returns a market overview for the dashboard.",
)
def get_market_overview(
    current_user: User = Depends(get_current_user),
):
    """Get market overview."""
    from backend.ml.analytics.analysis import market_analysis_service

    result = market_analysis_service.market_overview()
    return result


@router.post(
    "/mutual-fund",
    summary="Mutual Fund Analysis",
    description="Analyzes a mutual fund using real market data.",
)
def analyze_mutual_fund(
    request: MutualFundRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze a mutual fund."""
    from backend.ml.services.mutual_fund_service import mutual_fund_service

    result = mutual_fund_service.analyze(request.fund)
    return result


@router.post(
    "/mutual-funds",
    summary="List Mutual Funds",
    description="Lists supported mutual funds.",
)
def list_mutual_funds(
    current_user: User = Depends(get_current_user),
):
    """List supported mutual funds."""
    from backend.ml.services.mutual_fund_service import mutual_fund_service

    result = mutual_fund_service.list_funds()
    return {"funds": result}


@router.post(
    "/wealth-projection",
    summary="Wealth Projection",
    description="Projects future wealth from a monthly SIP with Monte Carlo simulation.",
)
def get_wealth_projection(
    request: WealthProjectionRequest,
    current_user: User = Depends(get_current_user),
):
    """Project wealth from SIP."""
    from backend.ml.services.wealth_projection import WealthProjector

    projector = WealthProjector()
    result = projector.project(
        monthly_sip=request.monthly_sip,
        years=request.years,
        expected_return=request.expected_return,
        current_amount=request.current_amount,
        inflation_rate=request.inflation_rate,
    )
    return result


@router.get(
    "/symbols",
    summary="List Supported Symbols",
    description="Lists all supported market symbols.",
)
def list_symbols(
    current_user: User = Depends(get_current_user),
    asset_class: str = "",
):
    """List supported market symbols."""
    from backend.market.manager import market_data_manager

    result = market_data_manager.get_symbols(asset_class if asset_class else None)
    return {"symbols": result}
