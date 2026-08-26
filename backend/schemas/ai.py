"""
AI Module Schemas

Pydantic models for AI-powered financial features.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---- Financial Health ----
class HealthComponent(BaseModel):
    score: float
    note: str


class FinancialHealthResponse(BaseModel):
    overall_score: float
    category: str
    color: str
    summary: str
    components: Dict[str, HealthComponent]
    suggestions: List[str]

    model_config = ConfigDict(extra="forbid")


# ---- Recommendations ----
class PriorityGoal(BaseModel):
    priority: str
    goal: str
    action: str
    timeline: str


class SpendingTip(BaseModel):
    category: str
    current_spend: float
    tip: str
    potential_savings: float


class SavingsTip(BaseModel):
    tip: str
    impact: str


class InvestmentAdvice(BaseModel):
    advice: str
    type: str
    action: str


class BudgetTip(BaseModel):
    category: str
    budget: float
    spent: float
    tip: str
    over_budget: bool


class EmergencyFund(BaseModel):
    monthly_expense: float
    recommended_fund: float
    current_estimate: float
    months_covered: float
    status: str
    advice: str


class RecommendationsResponse(BaseModel):
    priority_goals: List[PriorityGoal]
    spending_tips: List[SpendingTip]
    savings_tips: List[SavingsTip]
    investment_advice: List[InvestmentAdvice]
    budget_tips: List[BudgetTip]
    emergency_fund: EmergencyFund

    model_config = ConfigDict(extra="forbid")


# ---- Budget Optimizer ----
class BudgetOptimizationItem(BaseModel):
    category: str
    current_amount: float
    recommended_amount: float
    difference: float
    reason: str


class BudgetOptimizerResponse(BaseModel):
    optimizations: List[BudgetOptimizationItem]
    total_current: float
    total_recommended: float
    potential_savings: float

    model_config = ConfigDict(extra="forbid")


# ---- Spending Forecast ----
class ForecastPoint(BaseModel):
    month: str
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None


class SpendingForecastResponse(BaseModel):
    next_month_income: float
    next_month_expense: float
    expected_savings: float
    confidence_score: float
    income_forecast: List[ForecastPoint]
    expense_forecast: List[ForecastPoint]

    model_config = ConfigDict(extra="forbid")


# ---- Investment Advisor ----
class InvestmentAllocation(BaseModel):
    mutual_funds: float = 0
    stocks: float = 0
    gold: float = 0
    fixed_deposit: float = 0
    cash: float = 0
    debt_funds: float = 0


class MarketReturn(BaseModel):
    mutual_funds: float = 0
    stocks: float = 0
    gold: float = 0
    fixed_deposit: float = 0
    debt_funds: float = 0
    cash: float = 0


class SectorPerformanceItem(BaseModel):
    sector: str
    avg_return: float
    avg_volatility: float
    stocks: List[str]


class ProjectionPoint(BaseModel):
    month: int
    year: float
    value: float
    invested: float


class BandPoint(BaseModel):
    year: float
    p10: float
    p50: float
    p90: float


class WealthProjectionData(BaseModel):
    monthly_sip: float
    years: int
    expected_return: float
    current_amount: float
    future_value: float
    total_invested: float
    total_gain: float
    inflation_adjusted_value: float
    inflation_rate: float
    p10: float
    p50: float
    p90: float
    timeline: List[ProjectionPoint]
    chart: List[BandPoint]


class InvestmentAdvisorResponse(BaseModel):
    monthly_investment_capacity: float
    risk_profile: str
    risk_score: float
    allocation: InvestmentAllocation
    expected_annual_return: float
    expected_cagr: float
    expected_wealth_5y: float
    inflation_adjusted_wealth: float
    confidence_score: float
    advice: str
    market_returns: MarketReturn
    sector_performance: List[SectorPerformanceItem] = []
    projection: Optional[WealthProjectionData] = None

    model_config = ConfigDict(extra="forbid")


# ---- Portfolio Recommendation ----
class PortfolioItem(BaseModel):
    name: str
    allocation: float
    expected_return: float
    risk_level: str


class PortfolioRecommendationResponse(BaseModel):
    total_investment: float
    risk_level: str
    expected_annual_return: float
    portfolio: List[PortfolioItem]

    model_config = ConfigDict(extra="forbid")


# ---- Stock Prediction ----
class StockPredictionRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to predict")

    model_config = ConfigDict(extra="forbid")


class StockPredictionPoint(BaseModel):
    date: str
    price: float


class StockPredictionResponse(BaseModel):
    symbol: str
    ticker: Optional[str] = None
    current_price: float
    tomorrow_price: float
    next_7_days_avg: float
    next_30_days_avg: float
    trend: str
    signal: Optional[str] = None
    rsi: Optional[float] = None
    macd: Dict[str, float] = {}
    moving_averages: Dict[str, float] = {}
    support: Optional[float] = None
    resistance: Optional[float] = None
    confidence_score: float
    predictions: List[StockPredictionPoint]
    explanation: Optional[str] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None

    model_config = ConfigDict(extra="forbid")


# ---- House Price Prediction ----
class HousePriceRequest(BaseModel):
    area: float = Field(..., gt=0, description="Area in sq ft")
    bedrooms: int = Field(..., ge=1, le=10)
    bathrooms: int = Field(..., ge=1, le=10)
    location: str = Field(..., description="Location/City")

    model_config = ConfigDict(extra="forbid")


class HousePriceResponse(BaseModel):
    predicted_price: float
    price_range_low: float
    price_range_high: float
    investment_rating: str
    confidence_score: float

    model_config = ConfigDict(extra="forbid")


# ---- Fraud Detection ----
class FraudAlert(BaseModel):
    expense_id: int
    category: str
    amount: float
    date: str
    merchant: Optional[str] = None
    risk_level: str
    reason: str


class FraudDetectionResponse(BaseModel):
    alerts: List[FraudAlert]
    total_analyzed: int
    suspicious_count: int

    model_config = ConfigDict(extra="forbid")


# ---- Chatbot ----
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)

    model_config = ConfigDict(extra="forbid")


class ChatResponse(BaseModel):
    response: str
    confidence: float
    source: Optional[str] = "analytics"

    model_config = ConfigDict(extra="forbid")


# ---- Reports ----
class ReportRequest(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    format: str = Field("pdf", pattern="^(pdf|csv)$")

    model_config = ConfigDict(extra="forbid")


# ---- Analytics ----
class AnalyticsRequest(BaseModel):
    period: str = Field("monthly", pattern="^(weekly|monthly|yearly)$")

    model_config = ConfigDict(extra="forbid")


class TrendPoint(BaseModel):
    label: str
    value: float


class CategoryAnalysis(BaseModel):
    category: str
    total: float
    percentage: float
    trend: str


class AnalyticsResponse(BaseModel):
    period: str
    total_income: float
    total_expense: float
    total_savings: float
    savings_rate: float
    income_trend: List[TrendPoint]
    expense_trend: List[TrendPoint]
    savings_trend: List[TrendPoint]
    category_analysis: List[CategoryAnalysis]

    model_config = ConfigDict(extra="forbid")
