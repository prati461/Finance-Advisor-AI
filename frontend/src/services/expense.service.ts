import api from '@/api/axios'
import {
  ExpenseCreate,
  ExpenseRead,
  ExpenseUpdate,
  PaginatedResponse,
} from '@/types'

export interface ExpenseListParams {
  page?: number
  page_size?: number
  category?: string
  start_date?: string
  end_date?: string
  search?: string
}

export const expenseService = {
  async create(data: ExpenseCreate): Promise<ExpenseRead> {
    const response = await api.post<ExpenseRead>('/expenses', data)
    return response.data
  },

  async list(params?: ExpenseListParams): Promise<PaginatedResponse<ExpenseRead>> {
    const response = await api.get<PaginatedResponse<ExpenseRead>>('/expenses', { params })
    return response.data
  },

  async getById(id: number): Promise<ExpenseRead> {
    const response = await api.get<ExpenseRead>(`/expenses/${id}`)
    return response.data
  },

  async update(id: number, data: ExpenseUpdate): Promise<ExpenseRead> {
    const response = await api.put<ExpenseRead>(`/expenses/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/expenses/${id}`)
  },
}
