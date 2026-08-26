import { motion } from 'framer-motion'
import { TrendingUp, Shield, PieChart, DollarSign, Info } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { useInvestmentAdvice, usePortfolioRecommendation } from '@/hooks/useAI'
import { formatCurrency } from '@/utils'
import { PieChart as RePieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { useTheme } from '@/contexts/ThemeContext'

const ALLOCATION_COLORS = {
  mutual_funds: '#3b82f6',
  stocks: '#10b981',
  gold: '#f59e0b',
  fixed_deposit: '#8b5cf6',
  cash: '#6b7280',
}

const RISK_COLORS: Record<string, string> = {
  Conservative: '#10b981',
  'Conservative-Moderate': '#3b82f6',
  Moderate: '#f59e0b',
  'Moderate-Aggressive': '#f97316',
  Aggressive: '#ef4444',
}

export function InvestmentAdvisorPage() {
  const { data: advice, isLoading: adviceLoading, error: adviceError, refetch: refetchAdvice } = useInvestmentAdvice()
  const { data: portfolio, isLoading: portfolioLoading } = usePortfolioRecommendation()
  const { currentTheme } = useTheme()
  const isDark = currentTheme === 'dark'

  // Validate and cap percentage display
  const getValidatedPercentage = (percentage: number): { value: number; isUnrealistic: boolean } => {
    // Cap at 0-100% for display purposes
    // Realistic portfolio returns should be 0-50%
    const isUnrealistic = percentage > 50 || percentage < 0
    const value = Math.max(0, Math.min(100, percentage))
    return { value, isUnrealistic }
  }

  if (adviceError) {
    return <ErrorMessage title="Failed to load investment advice" onRetry={refetchAdvice} />
  }

  const isLoading = adviceLoading || portfolioLoading

  const pieData = advice ? [
    { name: 'Mutual Funds', value: advice.allocation.mutual_funds },
    { name: 'Stocks', value: advice.allocation.stocks },
    { name: 'Gold', value: advice.allocation.gold },
    { name: 'Fixed Deposit', value: advice.allocation.fixed_deposit },
    { name: 'Cash', value: advice.allocation.cash },
  ].filter(item => item.value > 0) : []

  const expectedReturnData = advice ? getValidatedPercentage(advice.expected_annual_return) : { value: 0, isUnrealistic: false }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Investment Advisor"
        subtitle="Personalized investment recommendations based on your financial profile"
      />

      {isLoading ? (
        <LoadingSpinner />
      ) : advice ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <DollarSign className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Monthly Investment Capacity</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {formatCurrency(advice.monthly_investment_capacity)}
                  </p>
                </div>
              </div>
            </Card>
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <Shield className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Risk Profile</p>
                  <p className="text-lg font-bold" style={{ color: RISK_COLORS[advice.risk_profile] || '#6b7280' }}>
                    {advice.risk_profile}
                  </p>
                </div>
              </div>
            </Card>
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Expected Annual Return</p>
                  <div className="flex items-center gap-2">
                    <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {expectedReturnData.value.toFixed(2)}%
                    </p>
                    {expectedReturnData.isUnrealistic && (
                      <div className="relative group">
                        <Info className="h-4 w-4 text-yellow-600 dark:text-yellow-400 cursor-help" />
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity">
                          Return value may be outside realistic range
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </Card>
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                  <PieChart className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Portfolio Diversification</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {pieData.length} Assets
                  </p>
                </div>
              </div>
            </Card>
          </div>

          {/* Allocation Pie Chart & Details */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Asset Allocation
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <RePieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {pieData.map((entry) => (
                        <Cell
                          key={entry.name}
                          fill={ALLOCATION_COLORS[entry.name.toLowerCase().replace(' ', '_') as keyof typeof ALLOCATION_COLORS] || '#6b7280'}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: isDark ? '#1f2937' : '#ffffff',
                        border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                        borderRadius: '8px',
                        color: isDark ? '#f3f4f6' : '#111827',
                      }}
                      formatter={(value: number) => [`${value}%`]}
                    />
                    <Legend
                      formatter={(value: string) => (
                        <span className="text-sm text-gray-600 dark:text-gray-400">{value}</span>
                      )}
                    />
                  </RePieChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Allocation Details
              </h3>
              <div className="space-y-3">
                {pieData.map((item) => {
                  const key = item.name.toLowerCase().replace(' ', '_') as keyof typeof ALLOCATION_COLORS
                  return (
                    <div key={item.name} className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: ALLOCATION_COLORS[key] || '#6b7280' }} />
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.name}</span>
                      </div>
                      <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">{item.value}%</span>
                    </div>
                  )
                })}
              </div>

              <div className="mt-4 p-3 rounded-xl bg-blue-50 dark:bg-blue-900/20">
                <div className="flex items-start gap-2">
                  <Info className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-blue-700 dark:text-blue-300">{advice.advice}</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Portfolio Recommendation */}
          {portfolio && portfolio.portfolio.length > 0 && (
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Recommended Portfolio
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-3 px-4 font-medium text-gray-500 dark:text-gray-400">Asset</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-500 dark:text-gray-400">Allocation</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-500 dark:text-gray-400">Expected Return</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-500 dark:text-gray-400">Risk Level</th>
                    </tr>
                  </thead>
                  <tbody>
                    {portfolio.portfolio.map((item, index) => (
                      <motion.tr
                        key={item.name}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30"
                      >
                        <td className="py-3 px-4 font-medium text-gray-900 dark:text-gray-100">{item.name}</td>
                        <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">{item.allocation}%</td>
                        <td className="py-3 px-4 text-right text-green-600 dark:text-green-400">{item.expected_return}%</td>
                        <td className="py-3 px-4 text-right">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            item.risk_level === 'High' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
                            item.risk_level === 'Moderate' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                            'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                          }`}>
                            {item.risk_level}
                          </span>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </>
      ) : null}
    </div>
  )
}

