import api from '@/api/axios'
import {
  IncomeCreate,
  IncomeRead,
  IncomeUpdate,
  PaginatedResponse,
} from '@/types'

export interface IncomeListParams {
  page?: number
  page_size?: number
  category?: string
  start_date?: string
  end_date?: string
  search?: string
}

export const incomeService = {
  async create(data: IncomeCreate): Promise<IncomeRead> {
    const response = await api.post<IncomeRead>('/incomes', data)
    return response.data
  },

  async list(params?: IncomeListParams): Promise<PaginatedResponse<IncomeRead>> {
    const response = await api.get<PaginatedResponse<IncomeRead>>('/incomes', { params })
    return response.data
  },

  async getById(id: number): Promise<IncomeRead> {
    const response = await api.get<IncomeRead>(`/incomes/${id}`)
    return response.data
  },

  async update(id: number, data: IncomeUpdate): Promise<IncomeRead> {
    const response = await api.put<IncomeRead>(`/incomes/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/incomes/${id}`)
  },
}
