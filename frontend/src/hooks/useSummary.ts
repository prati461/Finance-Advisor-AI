import { useQuery } from '@tanstack/react-query'
import { financeService, SummaryParams } from '@/services/finance.service'
import { QUERY_KEYS } from '@/constants'

export function useMonthlySummary(params?: SummaryParams) {
  return useQuery({
    queryKey: [...QUERY_KEYS.summary, params],
    queryFn: () => financeService.getMonthlySummary(params),
    placeholderData: (prev) => prev,
  })
}

export function useHistoricalSummary(months: number = 6) {
  return useQuery({
    queryKey: [...QUERY_KEYS.summary, 'historical', months],
    queryFn: () => financeService.getHistoricalSummary(months),
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 2,
  })
}
