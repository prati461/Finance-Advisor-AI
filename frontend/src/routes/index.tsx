import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { ProtectedRoute } from '@/components/layout/ProtectedRoute'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'

// Lazy loaded pages
const LoginPage = lazy(() => import('@/pages/auth/LoginPage').then(m => ({ default: m.LoginPage })))
const RegisterPage = lazy(() => import('@/pages/auth/RegisterPage').then(m => ({ default: m.RegisterPage })))
const DashboardPage = lazy(() => import('@/pages/dashboard/DashboardPage').then(m => ({ default: m.DashboardPage })))
const IncomePage = lazy(() => import('@/pages/income/IncomePage').then(m => ({ default: m.IncomePage })))
const ExpensePage = lazy(() => import('@/pages/expense/ExpensePage').then(m => ({ default: m.ExpensePage })))
const BudgetPage = lazy(() => import('@/pages/budget/BudgetPage').then(m => ({ default: m.BudgetPage })))
const ProfilePage = lazy(() => import('@/pages/profile/ProfilePage').then(m => ({ default: m.ProfilePage })))
const SettingsPage = lazy(() => import('@/pages/settings/SettingsPage').then(m => ({ default: m.SettingsPage })))
const MonthlySummaryPage = lazy(() => import('@/pages/MonthlySummaryPage').then(m => ({ default: m.MonthlySummaryPage })))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage').then(m => ({ default: m.NotFoundPage })))
const FinancialHealthPage = lazy(() => import('@/pages/ai/FinancialHealthPage').then(m => ({ default: m.FinancialHealthPage })))
const InvestmentAdvisorPage = lazy(() => import('@/pages/ai/InvestmentAdvisorPage').then(m => ({ default: m.InvestmentAdvisorPage })))
const StockPredictionPage = lazy(() => import('@/pages/ai/StockPredictionPage').then(m => ({ default: m.StockPredictionPage })))
const HousePricePage = lazy(() => import('@/pages/ai/HousePricePage').then(m => ({ default: m.HousePricePage })))
const AIChatPage = lazy(() => import('@/pages/ai/AIChatPage').then(m => ({ default: m.AIChatPage })))
const ReportsPage = lazy(() => import('@/pages/ai/ReportsPage').then(m => ({ default: m.ReportsPage })))
const AnalyticsPage = lazy(() => import('@/pages/ai/AnalyticsPage').then(m => ({ default: m.AnalyticsPage })))
const MarketAnalysisPage = lazy(() => import('@/pages/ai/MarketAnalysisPage').then(m => ({ default: m.MarketAnalysisPage })))
const MutualFundPage = lazy(() => import('@/pages/ai/MutualFundPage').then(m => ({ default: m.MutualFundPage })))
const WealthProjectionPage = lazy(() => import('@/pages/ai/WealthProjectionPage').then(m => ({ default: m.WealthProjectionPage })))

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<LoadingSpinner fullPage />}>
      {children}
    </Suspense>
  )
}

function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <AppLayout />
    </ProtectedRoute>
  )
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <SuspenseWrapper>
        <LoginPage />
      </SuspenseWrapper>
    ),
  },
  {
    path: '/register',
    element: (
      <SuspenseWrapper>
        <RegisterPage />
      </SuspenseWrapper>
    ),
  },
  {
    path: '/',
    element: <ProtectedLayout />,
    children: [
      {
        index: true,
        element: (
          <SuspenseWrapper>
            <DashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'incomes',
        element: (
          <SuspenseWrapper>
            <IncomePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'expenses',
        element: (
          <SuspenseWrapper>
            <ExpensePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'budgets',
        element: (
          <SuspenseWrapper>
            <BudgetPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'monthly-summary',
        element: (
          <SuspenseWrapper>
            <MonthlySummaryPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'profile',
        element: (
          <SuspenseWrapper>
            <ProfilePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'settings',
        element: (
          <SuspenseWrapper>
            <SettingsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'financial-health',
        element: (
          <SuspenseWrapper>
            <FinancialHealthPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'investment-advisor',
        element: (
          <SuspenseWrapper>
            <InvestmentAdvisorPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'stock-prediction',
        element: (
          <SuspenseWrapper>
            <StockPredictionPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'house-price',
        element: (
          <SuspenseWrapper>
            <HousePricePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'ai-chat',
        element: (
          <SuspenseWrapper>
            <AIChatPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'reports',
        element: (
          <SuspenseWrapper>
            <ReportsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'analytics',
        element: (
          <SuspenseWrapper>
            <AnalyticsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'market-analysis',
        element: (
          <SuspenseWrapper>
            <MarketAnalysisPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'mutual-funds',
        element: (
          <SuspenseWrapper>
            <MutualFundPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: 'wealth-projection',
        element: (
          <SuspenseWrapper>
            <WealthProjectionPage />
          </SuspenseWrapper>
        ),
      },
    ],
  },
  {
    path: '/404',
    element: (
      <SuspenseWrapper>
        <NotFoundPage />
      </SuspenseWrapper>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/404" replace />,
  },
])
