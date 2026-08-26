import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import toast from 'react-hot-toast'

const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

// Validate API URL is not empty
if (!API_URL || API_URL === '/api/v1' && !window.location.hostname.match(/localhost|127.0.0.1/)) {
  console.warn('API_URL not configured. Make sure VITE_API_URL environment variable is set.')
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for token refresh and error handling
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<{ detail: string }>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken && originalRequest.url !== '/auth/login' && originalRequest.url !== '/auth/refresh' && originalRequest.url !== '/auth/register') {
        try {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          const { access_token, refresh_token: newRefreshToken } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', newRefreshToken)

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          return api(originalRequest)
        } catch {
          // Refresh failed, clear tokens and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          toast.error('Session expired. Please log in again.')
          window.location.href = '/login'
          return Promise.reject(error)
        }
      } else if (!refreshToken && originalRequest.url !== '/auth/login' && originalRequest.url !== '/auth/register') {
        // No refresh token available, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        toast.error('Session expired. Please log in again.')
        window.location.href = '/login'
        return Promise.reject(error)
      }
    }

    // Handle other errors
    const errorMessage = error.response?.data?.detail || error.message || 'An unexpected error occurred'

    // Don't toast for 401 on auth endpoints
    if (!(error.response?.status === 401 && (originalRequest.url === '/auth/login' || originalRequest.url === '/auth/register'))) {
      if (error.response?.status === 422) {
        const validationErrors = error.response?.data as unknown as { detail: Array<{ msg: string }> }
        if (Array.isArray(validationErrors?.detail)) {
          validationErrors.detail.forEach((err) => {
            toast.error(err.msg)
          })
        } else {
          toast.error(errorMessage)
        }
      } else if (error.response?.status === 404) {
        toast.error('Resource not found')
      } else if (error.response?.status === 409) {
        toast.error(errorMessage)
      } else if (error.response?.status && error.response.status >= 500) {
        toast.error('Server error. Please try again later.')
      } else if (error.code === 'ERR_NETWORK') {
        toast.error('Network error. Please check your connection.')
      } else if (error.response?.status !== 401) {
        toast.error(errorMessage)
      }
    }

    return Promise.reject(error)
  }
)

export default api
