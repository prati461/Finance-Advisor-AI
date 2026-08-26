import { useState } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, Wallet, PiggyBank, Target } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { useWealthProjection } from '@/hooks/useAI'
import { formatCurrency } from '@/utils'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  ReferenceLine,
} from 'recharts'
import { useTheme } from '@/contexts/ThemeContext'

export function WealthProjectionPage() {
  const [monthlySIP, setMonthlySIP] = useState(10000)
  const [years, setYears] = useState(10)
  const [expectedReturn, setExpectedReturn] = useState(12)
  const [currentAmount, setCurrentAmount] = useState(0)
  const [inflationRate, setInflationRate] = useState(6)
  const projectionMutation = useWealthProjection()
  const { currentTheme } = useTheme()
  const isDark = currentTheme === 'dark'

  const handleProjectionInputChange = (
    value: number,
    setter: (val: number) => void,
    min: number,
    max: number
  ) => {
    const bounded = Math.max(min, Math.min(max, value))
    setter(bounded)
  }

  const handleProject = () => {
    projectionMutation.mutate({
      monthly_sip: Math.max(1, monthlySIP),
      years: Math.max(1, Math.min(50, years)),
      expected_return: Math.max(0, expectedReturn),
      current_amount: Math.max(0, currentAmount),
      inflation_rate: Math.max(0, inflationRate),
    })
  }

  const projection = projectionMutation.data

  return (
    <div className="space-y-6">
      <PageHeader
        title="Wealth Projection Calculator"
        subtitle="Simulate your future wealth with SIP, returns, and inflation-adjusted values"
      />

      <Card>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Monthly SIP (₹)</label>
            <Input
              type="number"
              min="1"
              max="9999999"
              value={monthlySIP}
              onChange={(e) => handleProjectionInputChange(Number(e.target.value), setMonthlySIP, 1, 9999999)}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Min: ₹1, Max: ₹9,999,999</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Years</label>
            <Input
              type="number"
              min="1"
              max="50"
              value={years}
              onChange={(e) => handleProjectionInputChange(Number(e.target.value), setYears, 1, 50)}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Min: 1, Max: 50</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Expected Return (%)</label>
            <Input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={expectedReturn}
              onChange={(e) => handleProjectionInputChange(Number(e.target.value), setExpectedReturn, 0, 100)}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Min: 0%, Max: 100%</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Current Investment (₹)</label>
            <Input
              type="number"
              min="0"
              max="9999999"
              value={currentAmount}
              onChange={(e) => handleProjectionInputChange(Number(e.target.value), setCurrentAmount, 0, 9999999)}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Min: ₹0, Max: ₹9,999,999</p>
          </div>
          <div className="flex items-end gap-2">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Inflation (%)</label>
              <Input
                type="number"
                min="0"
                max="50"
                step="0.1"
                value={inflationRate}
                onChange={(e) => handleProjectionInputChange(Number(e.target.value), setInflationRate, 0, 50)}
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Min: 0%, Max: 50%</p>
            </div>
            <Button onClick={handleProject} isLoading={projectionMutation.isPending}>
              <TrendingUp className="h-4 w-4" />
              Project
            </Button>
          </div>
        </div>
      </Card>

      {projectionMutation.isPending && <LoadingSpinner />}

      {projection && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card padding="sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg"><Wallet className="h-5 w-5 text-blue-600 dark:text-blue-400" /></div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Future Value</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{formatCurrency(projection.future_value)}</p>
                </div>
              </div>
            </Card>
            <Card padding="sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg"><PiggyBank className="h-5 w-5 text-green-600 dark:text-green-400" /></div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total Invested</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{formatCurrency(projection.total_invested)}</p>
                </div>
              </div>
            </Card>
            <Card padding="sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg"><Target className="h-5 w-5 text-purple-600 dark:text-purple-400" /></div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total Gain</p>
                  <p className="text-lg font-bold text-green-600 dark:text-green-400">{formatCurrency(projection.total_gain)}</p>
                </div>
              </div>
            </Card>
            <Card padding="sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg"><TrendingUp className="h-5 w-5 text-orange-600 dark:text-orange-400" /></div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Inflation-Adjusted Value</p>
                  <p className="text-lg font-bold text-orange-600 dark:text-orange-400">{formatCurrency(projection.inflation_adjusted_value)}</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Scenario Bands */}
          <Card>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Future Wealth Projection
            </h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={projection.chart}>
                  <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                  <XAxis dataKey="year" tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${formatCurrency(v).replace('₹', '')}`} width={80} />
                  <Tooltip contentStyle={{ backgroundColor: isDark ? '#1f2937' : '#fff', border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`, borderRadius: '8px', color: isDark ? '#f3f4f6' : '#111827' }} formatter={(value: number) => [formatCurrency(value)]} />
                  <Line type="monotone" dataKey="p90" stroke="#10b981" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="p50" stroke="#3b82f6" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="p10" stroke="#ef4444" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Monthly SIP Growth */}
          <Card>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Monthly SIP Growth</h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={projection.timeline}>
                  <defs>
                    <linearGradient id="sipGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                  <XAxis dataKey="month" tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${formatCurrency(v).replace('₹', '')}`} width={80} />
                  <Tooltip contentStyle={{ backgroundColor: isDark ? '#1f2937' : '#fff', border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`, borderRadius: '8px', color: isDark ? '#f3f4f6' : '#111827' }} formatter={(value: number) => [formatCurrency(value)]} />
                  <Area type="monotone" dataKey="value" stroke="#6366f1" fill="url(#sipGradient)" strokeWidth={2} />
                  <ReferenceLine y={projection.total_invested} stroke="#ef4444" strokeDasharray="6 3" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </>
      )}
    </div>
  )
}
