import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import { authService } from '@/services/auth.service'
import { userService } from '@/services/user.service'
import { UserRead, LoginRequest, RegisterRequest } from '@/types'
import toast from 'react-hot-toast'

interface AuthContextType {
  user: UserRead | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  updateUser: (user: UserRead) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserRead | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const isAuthenticated = !!user

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setIsLoading(false)
      return
    }
    try {
      const userData = await userService.getProfile()
      setUser(userData)
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      // If profile fetch fails, clear authentication
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const login = useCallback(async (data: LoginRequest) => {
    const response = await authService.login(data)
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    try {
      const userData = await userService.getProfile()
      setUser(userData)
      toast.success('Welcome back!')
    } catch (error) {
      console.error('Failed to fetch user profile after login:', error)
      // Even if profile fetch fails, we're logged in with a token
      toast.error('Login successful but could not load profile. Please refresh.')
    }
  }, [])

  const register = useCallback(async (data: RegisterRequest) => {
    const response = await authService.register(data)
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    try {
      const userData = await userService.getProfile()
      setUser(userData)
      toast.success('Account created successfully!')
    } catch (error) {
      console.error('Failed to fetch user profile after register:', error)
      toast.error('Registration successful but could not load profile. Please refresh.')
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    toast.success('Logged out successfully')
  }, [])

  const updateUser = useCallback((userData: UserRead) => {
    setUser(userData)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
