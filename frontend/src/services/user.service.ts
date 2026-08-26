import api from '@/api/axios'
import { UserRead, UserUpdate, ChangePasswordRequest } from '@/types'

export const userService = {
  async getProfile(): Promise<UserRead> {
    const response = await api.get<UserRead>('/users/me')
    return response.data
  },

  async updateProfile(data: UserUpdate): Promise<UserRead> {
    const response = await api.patch<UserRead>('/users/me', data)
    return response.data
  },

  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await api.post('/users/me/change-password', data)
  },

  async deleteAccount(): Promise<void> {
    await api.delete('/users/me')
  },
}
