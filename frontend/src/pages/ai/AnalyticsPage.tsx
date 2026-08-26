import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, TrendingDown, PiggyBank, Calendar } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { Select } from '@/components/common/Select'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { useAnalytics } from '@/hooks/useAI'
import { formatCurrency } from '@/utils'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
} from 'recharts'
import { useTheme } from '@/contexts/ThemeContext'

export function AnalyticsPage() {
  const [period, setPeriod] = useState<'weekly' | 'monthly' | 'yearly'>('monthly')
  const { data: analytics, isLoading, error, refetch } = useAnalytics(period)
  const { currentTheme } = useTheme()
  const isDark = currentTheme === 'dark'

  const chartTooltipStyle = {
    backgroundColor: isDark ? '#1f2937' : '#ffffff',
    border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
    borderRadius: '8px',
    color: isDark ? '#f3f4f6' : '#111827',
  }

  if (error) {
    return <ErrorMessage title="Failed to load analytics" onRetry={refetch} />
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analytics"
        subtitle="Advanced financial analytics and trend analysis"
      />

      {/* Period Selector */}
      <div className="flex justify-end">
        <Select
          value={period}
          onChange={(e) => setPeriod(e.target.value as typeof period)}
          options={[
            { value: 'weekly', label: 'Weekly' },
            { value: 'monthly', label: 'Monthly' },
            { value: 'yearly', label: 'Yearly' },
          ]}
          className="w-40"
        />
      </div>

      {isLoading ? (
        <LoadingSpinner />
      ) : analytics ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total Income</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {formatCurrency(analytics.total_income)}
                  </p>
                </div>
              </div>
            </Card>
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                  <TrendingDown className="h-5 w-5 text-red-600 dark:text-red-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total Expense</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {formatCurrency(analytics.total_expense)}
                  </p>
                </div>
              </div>
            </Card>
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <PiggyBank className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total Savings</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {formatCurrency(analytics.total_savings)}
                  </p>
                </div>
              </div>
            </Card>
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <BarChart3 className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Savings Rate</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {analytics.savings_rate.toFixed(1)}%
                  </p>
                </div>
              </div>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Income Trend */}
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Income Trend
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analytics.income_trend}>
                    <defs>
                      <linearGradient id="incomeGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                    <XAxis dataKey="label" tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={chartTooltipStyle} formatter={(value: number) => [formatCurrency(value)]} />
                    <Area type="monotone" dataKey="value" stroke="#10b981" fill="url(#incomeGradient)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Expense Trend */}
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Expense Trend
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analytics.expense_trend}>
                    <defs>
                      <linearGradient id="expenseGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                    <XAxis dataKey="label" tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={chartTooltipStyle} formatter={(value: number) => [formatCurrency(value)]} />
                    <Area type="monotone" dataKey="value" stroke="#ef4444" fill="url(#expenseGradient)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Savings Trend */}
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Savings Trend
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analytics.savings_trend}>
                    <defs>
                      <linearGradient id="savingsGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                    <XAxis dataKey="label" tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={chartTooltipStyle} formatter={(value: number) => [formatCurrency(value)]} />
                    <Area type="monotone" dataKey="value" stroke="#8b5cf6" fill="url(#savingsGradient)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Category Analysis */}
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Category Analysis
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analytics.category_analysis} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                    <XAxis type="number" tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis dataKey="category" type="category" tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} width={100} />
                    <Tooltip contentStyle={chartTooltipStyle} formatter={(value: number) => [formatCurrency(value)]} />
                    <Bar dataKey="total" fill="#3b82f6" radius={[0, 4, 4, 0]} maxBarSize={20} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>
        </>
      ) : null}
    </div>
  )
}

