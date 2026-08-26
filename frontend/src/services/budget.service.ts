import api from '@/api/axios'
import {
  BudgetCreate,
  BudgetRead,
  BudgetUpdate,
  PaginatedResponse,
} from '@/types'

export interface BudgetListParams {
  page?: number
  page_size?: number
  category?: string
  month?: number
  year?: number
}

export const budgetService = {
  async create(data: BudgetCreate): Promise<BudgetRead> {
    const response = await api.post<BudgetRead>('/budgets', data)
    return response.data
  },

  async list(params?: BudgetListParams): Promise<PaginatedResponse<BudgetRead>> {
    const response = await api.get<PaginatedResponse<BudgetRead>>('/budgets', { params })
    return response.data
  },

  async getById(id: number): Promise<BudgetRead> {
    const response = await api.get<BudgetRead>(`/budgets/${id}`)
    return response.data
  },

  async update(id: number, data: BudgetUpdate): Promise<BudgetRead> {
    const response = await api.put<BudgetRead>(`/budgets/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/budgets/${id}`)
  },
}
