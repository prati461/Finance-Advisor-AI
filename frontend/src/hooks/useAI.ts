import { useQuery, useMutation } from '@tanstack/react-query'
import { aiService } from '@/services/ai.service'
import type {
  ChatRequest,
  HousePriceRequest,
  StockPredictionRequest,
  MarketAnalysisRequest,
  ComparisonRequest,
  MutualFundRequest,
  WealthProjectionRequest,
} from '@/types'

export function useFinancialHealth() {
  return useQuery({
    queryKey: ['ai', 'financial-health'],
    queryFn: () => aiService.getFinancialHealth(),
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  })
}

export function useRecommendations() {
  return useQuery({
    queryKey: ['ai', 'recommendations'],
    queryFn: () => aiService.getRecommendations(),
    staleTime: 1000 * 60 * 5,
    retry: 1,
  })
}

export function useBudgetOptimizer() {
  return useQuery({
    queryKey: ['ai', 'budget-optimizer'],
    queryFn: () => aiService.optimizeBudgets(),
    staleTime: 1000 * 60 * 5,
    retry: 1,
  })
}

export function useSpendingForecast() {
  return useQuery({
    queryKey: ['ai', 'spending-forecast'],
    queryFn: () => aiService.forecastSpending(),
    staleTime: 1000 * 60 * 5,
    retry: 1,
  })
}

export function useInvestmentAdvice() {
  return useQuery({
    queryKey: ['ai', 'investment-advisor'],
    queryFn: () => aiService.getInvestmentAdvice(),
    staleTime: 1000 * 60 * 5,
    retry: 1,
  })
}

export function usePortfolioRecommendation() {
  return useQuery({
    queryKey: ['ai', 'portfolio'],
    queryFn: () => aiService.getPortfolioRecommendation(),
    staleTime: 1000 * 60 * 5,
    retry: 1,
  })
}

export function useStockPrediction() {
  return useMutation({
    mutationFn: (data: StockPredictionRequest) => aiService.predictStock(data),
  })
}

export function useHousePricePrediction() {
  return useMutation({
    mutationFn: (data: HousePriceRequest) => aiService.predictHousePrice(data),
  })
}

export function useFraudDetection() {
  return useQuery({
    queryKey: ['ai', 'fraud-detection'],
    queryFn: () => aiService.detectFraud(),
    staleTime: 1000 * 60 * 2,
    retry: 1,
  })
}

export function useChat() {
  return useMutation({
    mutationFn: (data: ChatRequest) => aiService.chat(data),
  })
}

export function useAnalytics(period: 'weekly' | 'monthly' | 'yearly' = 'monthly') {
  return useQuery({
    queryKey: ['ai', 'analytics', period],
    queryFn: () => aiService.getAnalytics({ period }),
    staleTime: 1000 * 60 * 2,
    retry: 1,
  })
}

// New market analysis hooks
export function useMarketAnalysis() {
  return useMutation({
    mutationFn: (data: MarketAnalysisRequest) => aiService.getMarketAnalysis(data),
  })
}

export function useCompareAssets() {
  return useMutation({
    mutationFn: (data: ComparisonRequest) => aiService.compareAssets(data),
  })
}

export function useSectorPerformance() {
  return useQuery({
    queryKey: ['ai', 'sector-performance'],
    queryFn: () => aiService.getSectorPerformance(),
    staleTime: 1000 * 60 * 15,
    retry: 1,
  })
}

export function useMarketOverview() {
  return useQuery({
    queryKey: ['ai', 'market-overview'],
    queryFn: () => aiService.getMarketOverview(),
    staleTime: 1000 * 60 * 15,
    retry: 1,
  })
}

export function useMutualFundAnalysis() {
  return useMutation({
    mutationFn: (data: MutualFundRequest) => aiService.analyzeMutualFund(data),
  })
}

export function useMutualFundsList() {
  return useQuery({
    queryKey: ['ai', 'mutual-funds'],
    queryFn: () => aiService.listMutualFunds(),
    staleTime: 1000 * 60 * 60,
    retry: 1,
  })
}

export function useWealthProjection() {
  return useMutation({
    mutationFn: (data: WealthProjectionRequest) => aiService.getWealthProjection(data),
  })
}

export function useSymbols(assetClass?: string) {
  return useQuery({
    queryKey: ['ai', 'symbols', assetClass],
    queryFn: () => aiService.getSymbols(assetClass),
    staleTime: 1000 * 60 * 60,
    retry: 1,
  })
}

