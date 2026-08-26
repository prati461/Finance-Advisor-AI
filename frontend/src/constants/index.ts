import {
  IncomeCategory,
  ExpenseCategory,
  IncomeFrequency,
} from '@/types'

export const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const INCOME_CATEGORIES = Object.values(IncomeCategory)
export const EXPENSE_CATEGORIES = Object.values(ExpenseCategory)
export const INCOME_FREQUENCIES = Object.values(IncomeFrequency)

export const EXPENSE_CATEGORY_COLORS: Record<string, string> = {
  Food: '#ef4444',
  Utilities: '#f59e0b',
  Rent: '#8b5cf6',
  Transportation: '#3b82f6',
  Entertainment: '#ec4899',
  Health: '#10b981',
  Shopping: '#f97316',
  Education: '#6366f1',
  Other: '#6b7280',
}

export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]
export const DEFAULT_PAGE_SIZE = 20

export const CURRENCY_SYMBOL = '₹'
export const CURRENCY_CODE = 'INR'

export const TOAST_DURATION = 4000

export const QUERY_KEYS = {
  user: ['user'],
  incomes: ['incomes'],
  expenses: ['expenses'],
  budgets: ['budgets'],
  summary: ['summary'],
} as const

export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/',
  INCOMES: '/incomes',
  EXPENSES: '/expenses',
  BUDGETS: '/budgets',
  PROFILE: '/profile',
  SETTINGS: '/settings',
  MONTHLY_SUMMARY: '/monthly-summary',
  FINANCIAL_HEALTH: '/financial-health',
  INVESTMENT_ADVISOR: '/investment-advisor',
  STOCK_PREDICTION: '/stock-prediction',
  MARKET_ANALYSIS: '/market-analysis',
  MUTUAL_FUNDS: '/mutual-funds',
  WEALTH_PROJECTION: '/wealth-projection',
  HOUSE_PRICE: '/house-price',
  AI_CHAT: '/ai-chat',
  REPORTS: '/reports',
  ANALYTICS: '/analytics',
} as const

export const SIDEBAR_ITEMS = [
  { label: 'Dashboard', path: ROUTES.DASHBOARD, icon: 'LayoutDashboard' },
  { label: 'Incomes', path: ROUTES.INCOMES, icon: 'TrendingUp' },
  { label: 'Expenses', path: ROUTES.EXPENSES, icon: 'TrendingDown' },
  { label: 'Budgets', path: ROUTES.BUDGETS, icon: 'PiggyBank' },
  { label: 'Monthly Summary', path: ROUTES.MONTHLY_SUMMARY, icon: 'BarChart3' },
  { label: 'Financial Health', path: ROUTES.FINANCIAL_HEALTH, icon: 'Heart' },
  { label: 'Investment Advisor', path: ROUTES.INVESTMENT_ADVISOR, icon: 'TrendingUp' },
  { label: 'Stock Prediction', path: ROUTES.STOCK_PREDICTION, icon: 'LineChart' },
  { label: 'House Price', path: ROUTES.HOUSE_PRICE, icon: 'Home' },
  { label: 'AI Assistant', path: ROUTES.AI_CHAT, icon: 'MessageSquare' },
  { label: 'Reports', path: ROUTES.REPORTS, icon: 'FileText' },
  { label: 'Analytics', path: ROUTES.ANALYTICS, icon: 'BarChart3' },
  { label: 'Profile', path: ROUTES.PROFILE, icon: 'User' },
  { label: 'Settings', path: ROUTES.SETTINGS, icon: 'Settings' },
] as const
