import api from '@/api/axios'
import { MonthlySummaryResponse } from '@/types'

export interface SummaryParams {
  month?: number
  year?: number
}

export interface MonthlyChartData {
  month: string
  income: number
  expense: number
  savings: number
}

export const financeService = {
  async getMonthlySummary(params?: SummaryParams): Promise<MonthlySummaryResponse> {
    const response = await api.get<MonthlySummaryResponse>('/finance/summary', { params })
    return response.data
  },

  async getHistoricalSummary(months: number = 6): Promise<MonthlyChartData[]> {
    const results: MonthlyChartData[] = []
    const today = new Date()

    for (let i = months - 1; i >= 0; i--) {
      const d = new Date(today)
      d.setMonth(d.getMonth() - i)
      const month = d.getMonth() + 1
      const year = d.getFullYear()

      try {
        const summary = await this.getMonthlySummary({ month, year })
        const monthName = d.toLocaleString('default', { month: 'short' })
        results.push({
          month: monthName,
          income: summary.income_total || 0,
          expense: summary.expense_total || 0,
          savings: summary.savings_total || 0,
        })
      } catch {
        // If API fails for a month, add zero values
        const monthName = d.toLocaleString('default', { month: 'short' })
        results.push({
          month: monthName,
          income: 0,
          expense: 0,
          savings: 0,
        })
      }
    }

    return results
  },
}
