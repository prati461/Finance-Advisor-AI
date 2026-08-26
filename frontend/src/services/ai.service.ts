import api from '@/api/axios'
import type {
  FinancialHealthResponse,
  RecommendationsResponse,
  BudgetOptimizerResponse,
  SpendingForecastResponse,
  InvestmentAdvisorResponse,
  PortfolioRecommendationResponse,
  StockPredictionResponse,
  HousePriceResponse,
  FraudDetectionResponse,
  ChatResponse,
  AnalyticsResponse,
  StockPredictionRequest,
  HousePriceRequest,
  ChatRequest,
  AnalyticsRequest,
  MarketAnalysisRequest,
  MarketAnalysisResponse,
  ComparisonRequest,
  ComparisonResponse,
  SectorPerformanceResponse,
  MarketOverviewResponse,
  MutualFundRequest,
  MutualFundResponse,
  MutualFundsListResponse,
  WealthProjectionRequest,
  WealthProjectionData,
  SymbolsResponse,
} from '@/types'

export const aiService = {
  async getFinancialHealth(): Promise<FinancialHealthResponse> {
    const response = await api.post<FinancialHealthResponse>('/ai/financial-health')
    return response.data
  },

  async getRecommendations(): Promise<RecommendationsResponse> {
    const response = await api.post<RecommendationsResponse>('/ai/recommendations')
    return response.data
  },

  async optimizeBudgets(): Promise<BudgetOptimizerResponse> {
    const response = await api.post<BudgetOptimizerResponse>('/ai/budget-optimizer')
    return response.data
  },

  async forecastSpending(): Promise<SpendingForecastResponse> {
    const response = await api.post<SpendingForecastResponse>('/ai/spending-forecast')
    return response.data
  },

  async getInvestmentAdvice(): Promise<InvestmentAdvisorResponse> {
    const response = await api.post<InvestmentAdvisorResponse>('/ai/investment-advisor')
    return response.data
  },

  async getPortfolioRecommendation(): Promise<PortfolioRecommendationResponse> {
    const response = await api.post<PortfolioRecommendationResponse>('/ai/portfolio')
    return response.data
  },

  async predictStock(data: StockPredictionRequest): Promise<StockPredictionResponse> {
    const response = await api.post<StockPredictionResponse>('/ai/stock-predict', data)
    return response.data
  },

  async predictHousePrice(data: HousePriceRequest): Promise<HousePriceResponse> {
    const response = await api.post<HousePriceResponse>('/ai/house-price-predict', data)
    return response.data
  },

  async detectFraud(): Promise<FraudDetectionResponse> {
    const response = await api.post<FraudDetectionResponse>('/ai/fraud-detection')
    return response.data
  },

  async chat(data: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/ai/chat', data)
    return response.data
  },

  async getAnalytics(data?: AnalyticsRequest): Promise<AnalyticsResponse> {
    const response = await api.post<AnalyticsResponse>('/ai/analytics', data || { period: 'monthly' })
    return response.data
  },

  // New market analysis endpoints
  async getMarketAnalysis(data: MarketAnalysisRequest): Promise<MarketAnalysisResponse> {
    const response = await api.post<MarketAnalysisResponse>('/ai/market-analysis', data)
    return response.data
  },

  async compareAssets(data: ComparisonRequest): Promise<ComparisonResponse> {
    const response = await api.post<ComparisonResponse>('/ai/compare', data)
    return response.data
  },

  async getSectorPerformance(): Promise<SectorPerformanceResponse> {
    const response = await api.post<SectorPerformanceResponse>('/ai/sector-performance')
    return response.data
  },

  async getMarketOverview(): Promise<MarketOverviewResponse> {
    const response = await api.post<MarketOverviewResponse>('/ai/market-overview')
    return response.data
  },

  async analyzeMutualFund(data: MutualFundRequest): Promise<MutualFundResponse> {
    const response = await api.post<MutualFundResponse>('/ai/mutual-fund', data)
    return response.data
  },

  async listMutualFunds(): Promise<MutualFundsListResponse> {
    const response = await api.post<MutualFundsListResponse>('/ai/mutual-funds')
    return response.data
  },

  async getWealthProjection(data: WealthProjectionRequest): Promise<WealthProjectionData> {
    const response = await api.post<WealthProjectionData>('/ai/wealth-projection', data)
    return response.data
  },

  async getSymbols(assetClass?: string): Promise<SymbolsResponse> {
    const response = await api.get<SymbolsResponse>('/ai/symbols', {
      params: assetClass ? { asset_class: assetClass } : {},
    })
    return response.data
  },
}

