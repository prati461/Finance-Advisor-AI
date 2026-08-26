//// Enums
export enum IncomeCategory {
  SALARY = 'Salary',
  BUSINESS = 'Business',
  FREELANCE = 'Freelance',
  INVESTMENT = 'Investment',
  OTHER = 'Other',
}

export enum ExpenseCategory {
  FOOD = 'Food',
  UTILITIES = 'Utilities',
  RENT = 'Rent',
  TRANSPORTATION = 'Transportation',
  ENTERTAINMENT = 'Entertainment',
  HEALTH = 'Health',
  SHOPPING = 'Shopping',
  EDUCATION = 'Education',
  OTHER = 'Other',
}

export enum IncomeFrequency {
  ONE_TIME = 'One-time',
  WEEKLY = 'Weekly',
  BIWEEKLY = 'Biweekly',
  MONTHLY = 'Monthly',
  ANNUAL = 'Annual',
}

// Auth
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  full_name: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RefreshRequest {
  refresh_token: string
}

// User
export interface UserRead {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  risk_profile?: string | null
  investment_horizon_years?: number | null
}

export interface UserUpdate {
  full_name?: string
  email?: string
  risk_profile?: string
  investment_horizon_years?: number
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

// Income
export interface IncomeBase {
  source: string
  category: IncomeCategory
  amount: number
  frequency: IncomeFrequency
  received_date: string
  description?: string | null
}

export interface IncomeCreate extends IncomeBase {}

export interface IncomeUpdate {
  source?: string
  category?: IncomeCategory
  amount?: number
  frequency?: IncomeFrequency
  received_date?: string
  description?: string | null
}

export interface IncomeRead extends IncomeBase {
  id: number
  user_id: number
}

// Expense
export interface ExpenseBase {
  category: ExpenseCategory
  amount: number
  spent_at: string
  description?: string | null
  merchant?: string | null
  payment_method?: string | null
}

export interface ExpenseCreate extends ExpenseBase {}

export interface ExpenseUpdate {
  category?: ExpenseCategory
  amount?: number
  spent_at?: string
  description?: string | null
  merchant?: string | null
  payment_method?: string | null
}

export interface ExpenseRead extends ExpenseBase {
  id: number
  user_id: number
}

// Budget
export interface BudgetBase {
  month: number
  year: number
  category: ExpenseCategory
  budget_amount: number
  alert_threshold_pct: number
}

export interface BudgetCreate extends BudgetBase {}

export interface BudgetUpdate {
  month?: number
  year?: number
  category?: ExpenseCategory
  budget_amount?: number
  alert_threshold_pct?: number
}

export interface BudgetRead extends BudgetBase {
  id: number
  user_id: number
}

// Finance
export interface MonthlySummaryResponse {
  income_total: number
  expense_total: number
  savings_total: number
}

// Pagination
export interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

// API Error
export interface ApiError {
  detail: string
}

// Theme
export type Theme = 'light' | 'dark' | 'system'

// Navigation
export interface NavItem {
  label: string
  path: string
  icon: string
  roles?: string[]
}

// Chart Data
export interface ChartDataPoint {
  name: string
  value: number
  color?: string
}

export interface MonthlyChartData {
  month: string
  income: number
  expense: number
}

// ============ AI Types ============

// Financial Health
export interface HealthComponent {
  score: number
  note: string
}

export interface FinancialHealthResponse {
  overall_score: number
  category: string
  color: string
  summary: string
  components: {
    income_stability: HealthComponent
    expense_ratio: HealthComponent
    savings_ratio: HealthComponent
    budget_utilization: HealthComponent
    investment_readiness: HealthComponent
  }
  suggestions: string[]
}

// Recommendations
export interface PriorityGoal {
  priority: string
  goal: string
  action: string
  timeline: string
}

export interface SpendingTip {
  category: string
  current_spend: number
  tip: string
  potential_savings: number
}

export interface SavingsTip {
  tip: string
  impact: string
}

export interface InvestmentAdvice {
  advice: string
  type: string
  action: string
}

export interface BudgetTip {
  category: string
  budget: number
  spent: number
  tip: string
  over_budget: boolean
}

export interface EmergencyFund {
  monthly_expense: number
  recommended_fund: number
  current_estimate: number
  months_covered: number
  status: string
  advice: string
}

export interface RecommendationsResponse {
  priority_goals: PriorityGoal[]
  spending_tips: SpendingTip[]
  savings_tips: SavingsTip[]
  investment_advice: InvestmentAdvice[]
  budget_tips: BudgetTip[]
  emergency_fund: EmergencyFund
}

// Budget Optimizer
export interface BudgetOptimizationItem {
  category: string
  current_amount: number
  recommended_amount: number
  difference: number
  reason: string
}

export interface BudgetOptimizerResponse {
  optimizations: BudgetOptimizationItem[]
  total_current: number
  total_recommended: number
  potential_savings: number
}

// Spending Forecast
export interface ForecastPoint {
  month: string
  predicted_value: number
  lower_bound?: number
  upper_bound?: number
}

export interface SpendingForecastResponse {
  next_month_income: number
  next_month_expense: number
  expected_savings: number
  confidence_score: number
  income_forecast: ForecastPoint[]
  expense_forecast: ForecastPoint[]
}

// Investment Advisor
export interface InvestmentAllocation {
  mutual_funds: number
  stocks: number
  gold: number
  fixed_deposit: number
  cash: number
}

export interface InvestmentAdvisorResponse {
  monthly_investment_capacity: number
  risk_profile: string
  allocation: InvestmentAllocation
  expected_annual_return: number
  advice: string
}

// Portfolio
export interface PortfolioItem {
  name: string
  allocation: number
  expected_return: number
  risk_level: string
}

export interface PortfolioRecommendationResponse {
  total_investment: number
  risk_level: string
  expected_annual_return: number
  portfolio: PortfolioItem[]
}

// Stock Prediction
export interface StockPredictionRequest {
  symbol: string
}

export interface StockPredictionPoint {
  date: string
  price: number
}

export interface StockPredictionResponse {
  symbol: string
  current_price: number
  tomorrow_price: number
  next_7_days_avg: number
  next_30_days_avg: number
  trend: string
  confidence_score: number
  predictions: StockPredictionPoint[]
}

// House Price
export interface HousePriceRequest {
  area: number
  bedrooms: number
  bathrooms: number
  location: string
}

export interface HousePriceResponse {
  predicted_price: number
  price_range_low: number
  price_range_high: number
  investment_rating: string
  confidence_score: number
}

// Fraud Detection
export interface FraudAlert {
  expense_id: number
  category: string
  amount: number
  date: string
  merchant?: string
  risk_level: string
  reason: string
}

export interface FraudDetectionResponse {
  alerts: FraudAlert[]
  total_analyzed: number
  suspicious_count: number
}

// Chatbot
export interface ChatRequest {
  message: string
}

export interface ChatResponse {
  response: string
  confidence: number
}

// Analytics
export interface AnalyticsRequest {
  period: 'weekly' | 'monthly' | 'yearly'
}

export interface TrendPoint {
  label: string
  value: number
}

export interface CategoryAnalysis {
  category: string
  total: number
  percentage: number
  trend: string
}

export interface AnalyticsResponse {
  period: string
  total_income: number
  total_expense: number
  total_savings: number
  savings_rate: number
  income_trend: TrendPoint[]
  expense_trend: TrendPoint[]
  savings_trend: TrendPoint[]
  category_analysis: CategoryAnalysis[]
}

// === New AI Feature Types ===

// Expanded Investment Advisor
export interface InvestmentAllocationExtended extends InvestmentAllocation {
  debt_funds?: number
}

export interface MarketReturnData {
  mutual_funds: number
  stocks: number
  gold: number
  fixed_deposit: number
  debt_funds: number
  cash: number
}

export interface SectorPerformanceItem {
  sector: string
  avg_return: number
  avg_volatility: number
  stocks: string[]
}

export interface ProjectionPoint {
  month: number
  year: number
  value: number
  invested: number
}

export interface BandPoint {
  year: number
  p10: number
  p50: number
  p90: number
}

export interface WealthProjectionData {
  monthly_sip: number
  years: number
  expected_return: number
  current_amount: number
  future_value: number
  total_invested: number
  total_gain: number
  inflation_adjusted_value: number
  inflation_rate: number
  p10: number
  p50: number
  p90: number
  timeline: ProjectionPoint[]
  chart: BandPoint[]
}

// Extended InvestmentAdvisorResponse
export interface InvestmentAdvisorResponseExtended {
  monthly_investment_capacity: number
  risk_profile: string
  risk_score: number
  allocation: InvestmentAllocationExtended
  expected_annual_return: number
  expected_cagr: number
  expected_wealth_5y: number
  inflation_adjusted_wealth: number
  confidence_score: number
  advice: string
  market_returns: MarketReturnData
  sector_performance: SectorPerformanceItem[]
  projection?: WealthProjectionData
}

// Extended Stock Pred Response
export interface StockPredictionResponseExtended extends StockPredictionResponse {
  ticker?: string
  signal?: string
  rsi?: number
  macd?: Record<string, number>
  moving_averages?: Record<string, number>
  support?: number
  resistance?: number
  explanation?: string
  fifty_two_week_high?: number | null
  fifty_two_week_low?: number | null
  market_cap?: number | null
  pe_ratio?: number | null
  dividend_yield?: number | null
}

// Market Analysis
export interface MarketAnalysisRequest {
  symbol: string
}

export interface YearlyReturnPoint {
  year: number
  return: number
}

export interface TechnicalAnalysisData {
  rsi?: number
  macd?: Record<string, number>
  moving_averages?: Record<string, number>
  support?: number
  resistance?: number
  trend?: string
  signal?: string
  available?: boolean
}

export interface MarketAnalysisResponse {
  symbol: string
  name: string
  asset_class: string
  available: boolean
  current_price: number
  cagr: number
  annual_return: number
  max_drawdown: number
  volatility: number
  sharpe_ratio: number
  beta: number
  pe_ratio?: number | null
  dividend_yield?: number | null
  market_cap?: number | null
  fifty_two_week_high?: number | null
  fifty_two_week_low?: number | null
  confidence_score: number
  yearly_returns: YearlyReturnPoint[]
  data_points: number
  start_date?: string
  end_date?: string
  technical?: TechnicalAnalysisData | null
  message?: string
}

// Comparison
export interface ComparisonRequest {
  symbols: string[]
}

export interface ComparisonResponse {
  dates: string[]
  assets: Record<string, {
    key: string
    values: Record<string, number>
  }>
  normalized: boolean
}

// Sector Performance
export interface SectorPerformanceResponse {
  sectors: SectorPerformanceItem[]
}

// Market Overview
export interface MarketOverviewResponse {
  assets: Array<{
    name: string
    key: string
    asset_class: string
    current_price: number
    cagr: number
    volatility: number
    max_drawdown: number
  }>
  top_performing: Array<{
    name: string
    cagr: number
  }>
}

// Mutual Fund
export interface MutualFundRequest {
  fund: string
}

export interface MutualFundResponse {
  key: string
  name: string
  category: string
  proxy_symbol: string
  available: boolean
  returns_1y: number
  returns_3y: number
  returns_5y: number
  cagr_5y: number
  expense_ratio: number
  risk_level: string
  aum_estimate: number
  volatility: number
  sharpe_ratio: number
  benchmark_cagr: number
  recommendation: string
  reason: string
  pros: string[]
  cons: string[]
  fund_manager: string
  technical_signal: string
  message?: string
}

export interface MutualFundsListResponse {
  funds: Array<{
    key: string
    name: string
    category: string
  }>
}

// Wealth Projection
export interface WealthProjectionRequest {
  monthly_sip: number
  years: number
  expected_return: number
  current_amount: number
  inflation_rate: number
}

// Symbols
export interface SymbolItem {
  key: string
  symbol: string
  name: string
  asset_class: string
  currency: string
}

export interface SymbolsResponse {
  symbols: SymbolItem[]
}

// Extended Chat
export interface ChatResponseExtended extends ChatResponse {
  source?: string
}
