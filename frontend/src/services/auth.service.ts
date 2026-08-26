import api from '@/api/axios'
import {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  RefreshRequest,
} from '@/types'

export const authService = {
  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/login', data)
    return response.data
  },

  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/register', data)
    return response.data
  },

  async refresh(data: RefreshRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/refresh', data)
    return response.data
  },
}
